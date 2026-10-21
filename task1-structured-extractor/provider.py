"""
LLM Provider Abstraction Layer
Supports Google Gemini (via google-genai), OpenAI, and an offline Mock Provider.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base provider for LLM completion."""

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
        """
        Generate completion for a sequence of chat messages.
        messages format: [{"role": "system"|"user"|"assistant", "content": "..."}]
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini integration using official google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiProvider.")
        self.model_name = model
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except ImportError as e:
            raise ImportError("Please install google-genai: pip install google-genai") from e

    @property
    def provider_name(self) -> str:
        return f"Gemini ({self.model_name})"

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
        # Separate system instruction from conversational contents
        system_instruction = None
        contents = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = content
            elif role == "user":
                contents.append(content)
            elif role == "assistant":
                contents.append(f"Model: {content}")

        combined_prompt = "\n\n".join(contents)
        
        from google.genai import types
        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction,
            response_mime_type="application/json"
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=combined_prompt,
            config=config
        )
        return response.text or ""


class OpenAIProvider(LLMProvider):
    """OpenAI integration using official openai SDK."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIProvider.")
        self.model_name = model
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError as e:
            raise ImportError("Please install openai: pip install openai") from e

    @property
    def provider_name(self) -> str:
        return f"OpenAI ({self.model_name})"

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content or ""


class MockProvider(LLMProvider):
    """
    Offline Mock Provider for zero-dependency local testing and demonstrations.
    Intelligently inspects prompt content to return realistic, schema-valid JSON
    for Invoices or Resumes, and simulates bounded corrective retry resolution.
    """

    def __init__(self, model: str = "mock-model-v1", simulate_error_once: bool = False):
        self.model_name = model
        self.simulate_error_once = simulate_error_once
        self._error_simulated = False

    @property
    def provider_name(self) -> str:
        return "Offline Mock Provider"

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
        last_message = messages[-1]["content"] if messages else ""

        # Check if this is a corrective repair prompt
        if "VALIDATION ERRORS:" in last_message:
            # Return fixed valid response for repair prompts
            if "invoice" in last_message.lower():
                return self._mock_invoice(repaired=True)
            return self._mock_resume(repaired=True)

        if self.simulate_error_once and not self._error_simulated:
            self._error_simulated = True
            # Return intentionally invalid JSON to test retry loop
            return '{"invoice_number": "INV-SIMULATED", "issue_date": "not-a-date", "total_amount": "invalid"}'

        # Detect domain
        lower_content = " ".join(m.get("content", "").lower() for m in messages)
        if "resume" in lower_content or "curriculum vitae" in lower_content or "candidate" in lower_content:
            return self._mock_resume()
        return self._mock_invoice()

    def _mock_invoice(self, repaired: bool = False) -> str:
        data = {
            "invoice_number": "INV-2026-0042",
            "issue_date": "2026-10-18",
            "due_date": "2026-11-17",
            "vendor_name": "Nexus Cloud Architectures LLC",
            "vendor_address": "742 Evergreen Terrace, Seattle, WA 98101",
            "vendor_tax_id": "US-47-9201842",
            "customer_name": "Apex Enterprise Systems Inc.",
            "customer_address": "1200 Financial Plaza, New York, NY 10005",
            "line_items": [
                {
                    "description": "High-Throughput Vector Pipeline Implementation",
                    "quantity": 30.0,
                    "unit_price": 200.0,
                    "total_price": 6000.0
                },
                {
                    "description": "Enterprise Security & IAM Audit",
                    "quantity": 10.0,
                    "unit_price": 250.0,
                    "total_price": 2500.0
                }
            ],
            "subtotal": 8500.0,
            "tax_amount": 722.5,
            "discount_amount": 0.0,
            "total_amount": 9222.5,
            "currency": "USD",
            "payment_terms": "Net 30"
        }
        return json.dumps(data, indent=2)

    def _mock_resume(self, repaired: bool = False) -> str:
        data = {
            "full_name": "Elena Rostova",
            "contact_info": {
                "email": "elena.rostova@datasphere.ai",
                "phone": "+1 (555) 234-5678",
                "location": "Boston, MA",
                "linkedin_url": "linkedin.com/in/elena-rostova-ai",
                "github_url": "github.com/erostova",
                "portfolio_url": "https://erostova.ai"
            },
            "professional_summary": "Staff AI Engineer specializing in distributed LLM architectures, RAG retrieval pipelines, and autonomous agent orchestration.",
            "education": [
                {
                    "institution": "Massachusetts Institute of Technology",
                    "degree": "Master of Science in Artificial Intelligence",
                    "field_of_study": "Computer Science & AI",
                    "start_year": "2018",
                    "end_year": "2020",
                    "gpa": "3.92 / 4.0"
                }
            ],
            "work_experience": [
                {
                    "job_title": "Senior AI Systems Architect",
                    "company": "DataSphere AI Systems",
                    "location": "Boston, MA",
                    "start_date": "2021",
                    "end_date": "Present",
                    "highlights": [
                        "Architected hybrid BM25 and vector semantic retrieval system serving 10M+ queries.",
                        "Deployed autonomous multi-tool agent cluster reducing support escalation by 60%."
                    ]
                }
            ],
            "technical_skills": [
                "Python", "PyTorch", "LangChain", "FastAPI", "Docker", "ChromaDB", "PostgreSQL", "Streamlit"
            ],
            "soft_skills": [
                "System Architecture Design", "Technical Mentorship", "Cross-Team Communication"
            ],
            "certifications": [
                {
                    "name": "Google Professional Machine Learning Engineer",
                    "issuer": "Google Cloud",
                    "issue_date": "2023"
                }
            ],
            "languages": ["English", "German"]
        }
        return json.dumps(data, indent=2)


def get_provider(
    provider_type: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> LLMProvider:
    """Factory to instantiate configured provider with graceful fallback to Mock."""
    requested = (provider_type or os.getenv("DEFAULT_LLM_PROVIDER") or "mock").lower().strip()

    if requested == "gemini":
        gemini_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            model_name = model or os.getenv("DEFAULT_GEMINI_MODEL") or "gemini-2.5-flash"
            return GeminiProvider(api_key=gemini_key, model=model_name)
        logger.warning("No GEMINI_API_KEY provided; falling back to Offline Mock Provider.")
        return MockProvider()

    if requested == "openai":
        openai_key = api_key or os.getenv("OPENAI_API_KEY")
        if openai_key:
            model_name = model or os.getenv("DEFAULT_OPENAI_MODEL") or "gpt-4o-mini"
            return OpenAIProvider(api_key=openai_key, model=model_name)
        logger.warning("No OPENAI_API_KEY provided; falling back to Offline Mock Provider.")
        return MockProvider()

    return MockProvider()
