import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import pytest

try:
    from extractor import StructuredExtractor, clean_json_markdown
    from provider import MockProvider
    from models import InvoiceExtraction, ResumeExtraction
except ImportError:
    from task1_structured_extractor.extractor import StructuredExtractor, clean_json_markdown
    from task1_structured_extractor.provider import MockProvider
    from task1_structured_extractor.models import InvoiceExtraction, ResumeExtraction


def test_clean_json_markdown():
    wrapped = "```json\n{\"key\": \"value\"}\n```"
    assert clean_json_markdown(wrapped) == "{\"key\": \"value\"}"

    with_preamble = "Here is the result:\n{\"key\": \"value\"}\nHope this helps!"
    assert clean_json_markdown(with_preamble) == "{\"key\": \"value\"}"


def test_mock_invoice_extraction_first_attempt():
    provider = MockProvider()
    extractor = StructuredExtractor(provider=provider, max_retries=3)

    raw_text = "Sample invoice text..."
    result = extractor.extract_invoice(raw_text)

    assert result.success is True
    assert result.total_retries == 0
    assert len(result.attempts) == 1
    assert result.data["invoice_number"] == "INV-2026-0042"
    assert result.data["total_amount"] == 9222.50

    # Ensure model validation helper works
    validated = result.get_validated_model(InvoiceExtraction)
    assert validated is not None
    assert validated.vendor_name == "Nexus Cloud Architectures LLC"


def test_mock_resume_extraction():
    provider = MockProvider()
    extractor = StructuredExtractor(provider=provider, max_retries=3)

    raw_text = "Candidate Elena Rostova resume..."
    result = extractor.extract_resume(raw_text)

    assert result.success is True
    assert result.data["full_name"] == "Elena Rostova"
    assert "Python" in result.data["technical_skills"]

    validated = result.get_validated_model(ResumeExtraction)
    assert validated is not None
    assert validated.contact_info.email == "elena.rostova@datasphere.ai"


def test_bounded_corrective_retry_simulation():
    # simulate_error_once causes first call to return invalid JSON, then second call to return repaired JSON
    provider = MockProvider(simulate_error_once=True)
    extractor = StructuredExtractor(provider=provider, max_retries=3)

    result = extractor.extract_invoice("Raw invoice text...")

    assert result.success is True
    assert result.total_retries == 1
    assert len(result.attempts) == 2
    assert result.attempts[0].is_valid is False
    assert len(result.attempts[0].validation_errors) > 0
    assert result.attempts[1].is_valid is True
    assert result.data["invoice_number"] == "INV-2026-0042"
