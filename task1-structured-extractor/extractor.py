"""
Structured Extraction Engine with Bounded Corrective Retries.
Intercepts Pydantic validation errors and triggers structured self-repair cycles.
"""

import re
import json
import time
import logging
from typing import Type, TypeVar, Optional, List, Dict, Any, Generic
from pydantic import BaseModel, ValidationError

try:
    from .models import InvoiceExtraction, ResumeExtraction
    from .prompt_templates import build_extraction_prompt, CORRECTIVE_REPAIR_PROMPT
    from .provider import LLMProvider, get_provider
except ImportError:
    from models import InvoiceExtraction, ResumeExtraction
    from prompt_templates import build_extraction_prompt, CORRECTIVE_REPAIR_PROMPT
    from provider import LLMProvider, get_provider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class ExtractionAttempt(BaseModel):
    """Telemetry record for each extraction attempt."""
    attempt_number: int
    raw_output: str
    is_valid: bool
    validation_errors: List[str] = []
    duration_seconds: float = 0.0


class ExtractionResult(BaseModel, Generic[T]):
    """Aggregated outcome of an extraction request."""
    success: bool
    mode: str
    data: Optional[Dict[str, Any]] = None
    validation_errors: List[str] = []
    attempts: List[ExtractionAttempt] = []
    total_retries: int = 0
    provider_used: str = ""

    def get_validated_model(self, model_cls: Type[T]) -> Optional[T]:
        """Convert data dict back to strongly-typed Pydantic instance."""
        if self.success and self.data:
            return model_cls.model_validate(self.data)
        return None

    def to_formatted_json(self) -> str:
        """Return pretty-printed JSON of the extracted data."""
        if self.data:
            return json.dumps(self.data, indent=2)
        return json.dumps({"error": "Extraction failed", "details": self.validation_errors}, indent=2)


def clean_json_markdown(text: str) -> str:
    """Strip markdown codeblock wrappers and isolate raw JSON object."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    text = text.strip()
    # Find matching first { and last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace:last_brace + 1]
    return text


class StructuredExtractor:
    """Core extractor coordinating prompt dispatch, schema validation, and bounded retry cycles."""

    def __init__(self, provider: Optional[LLMProvider] = None, max_retries: int = 3):
        self.provider = provider or get_provider()
        self.max_retries = max_retries

    def extract_invoice(self, text: str) -> ExtractionResult[InvoiceExtraction]:
        """Extract and validate structured invoice from raw text."""
        return self._extract(mode="invoice", text=text, model_cls=InvoiceExtraction)

    def extract_resume(self, text: str) -> ExtractionResult[ResumeExtraction]:
        """Extract and validate structured resume from raw text."""
        return self._extract(mode="resume", text=text, model_cls=ResumeExtraction)

    def _extract(self, mode: str, text: str, model_cls: Type[T]) -> ExtractionResult[T]:
        attempts: List[ExtractionAttempt] = []
        messages = build_extraction_prompt(mode=mode, document_text=text)
        
        last_raw_output = ""
        last_errors: List[str] = []

        for attempt_idx in range(1, self.max_retries + 1):
            start_time = time.time()
            try:
                # First attempt uses few-shot template; subsequent attempts use corrective repair prompt
                if attempt_idx == 1:
                    raw_output = self.provider.generate(messages)
                else:
                    repair_prompt = CORRECTIVE_REPAIR_PROMPT.format(
                        validation_errors="\n".join(f"- {e}" for e in last_errors),
                        previous_output=last_raw_output,
                        source_text=text
                    )
                    repair_messages = [
                        {"role": "system", "content": "You are a precise data repair engine. Fix schema validation errors."},
                        {"role": "user", "content": repair_prompt}
                    ]
                    raw_output = self.provider.generate(repair_messages)

                last_raw_output = raw_output
                elapsed = time.time() - start_time

                cleaned = clean_json_markdown(raw_output)
                parsed_json = json.loads(cleaned)

                # Validate with Pydantic v2
                validated_model = model_cls.model_validate(parsed_json)
                
                # Success
                attempts.append(ExtractionAttempt(
                    attempt_number=attempt_idx,
                    raw_output=raw_output,
                    is_valid=True,
                    validation_errors=[],
                    duration_seconds=round(elapsed, 3)
                ))

                return ExtractionResult(
                    success=True,
                    mode=mode,
                    data=validated_model.model_dump(mode="json"),
                    validation_errors=[],
                    attempts=attempts,
                    total_retries=attempt_idx - 1,
                    provider_used=self.provider.provider_name
                )

            except json.JSONDecodeError as jde:
                elapsed = time.time() - start_time
                error_msg = f"Invalid JSON syntax: {str(jde)}"
                last_errors = [error_msg]
                attempts.append(ExtractionAttempt(
                    attempt_number=attempt_idx,
                    raw_output=last_raw_output,
                    is_valid=False,
                    validation_errors=last_errors,
                    duration_seconds=round(elapsed, 3)
                ))
                logger.warning("Attempt %d failed JSON decoding: %s", attempt_idx, error_msg)

            except ValidationError as ve:
                elapsed = time.time() - start_time
                formatted_errors = []
                for err in ve.errors():
                    loc = " -> ".join(str(p) for p in err.get("loc", []))
                    formatted_errors.append(f"Field '{loc}': {err.get('msg')}")
                last_errors = formatted_errors
                attempts.append(ExtractionAttempt(
                    attempt_number=attempt_idx,
                    raw_output=last_raw_output,
                    is_valid=False,
                    validation_errors=formatted_errors,
                    duration_seconds=round(elapsed, 3)
                ))
                logger.warning("Attempt %d failed Pydantic validation: %s", attempt_idx, formatted_errors)

            except Exception as e:
                elapsed = time.time() - start_time
                error_msg = f"Unexpected provider exception: {type(e).__name__}: {str(e)}"
                last_errors = [error_msg]
                attempts.append(ExtractionAttempt(
                    attempt_number=attempt_idx,
                    raw_output=last_raw_output,
                    is_valid=False,
                    validation_errors=[error_msg],
                    duration_seconds=round(elapsed, 3)
                ))
                logger.error("Attempt %d encountered critical error: %s", attempt_idx, error_msg)

        # Retries exhausted
        return ExtractionResult(
            success=False,
            mode=mode,
            data=None,
            validation_errors=last_errors,
            attempts=attempts,
            total_retries=len(attempts) - 1,
            provider_used=self.provider.provider_name
        )
