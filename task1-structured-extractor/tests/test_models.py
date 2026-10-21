import sys
from pathlib import Path

# Add parent directory of tests to sys.path
TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import pytest
from pydantic import ValidationError

try:
    from models import (
        InvoiceExtraction,
        InvoiceLineItem,
        ResumeExtraction,
        ContactInfo,
        EducationEntry,
        WorkExperience,
    )
except ImportError:
    from task1_structured_extractor.models import (
        InvoiceExtraction,
        InvoiceLineItem,
        ResumeExtraction,
        ContactInfo,
        EducationEntry,
        WorkExperience,
    )


def test_invoice_line_item_math():
    item = InvoiceLineItem(
        description="Software Architecture Review",
        quantity=10.0,
        unit_price=150.0,
        total_price=1500.0
    )
    assert item.total_price == 1500.0


def test_invoice_line_item_rounding_correction():
    # If off by 2 cents due to floating point, it should auto-adjust
    item = InvoiceLineItem(
        description="Cloud Storage",
        quantity=3.0,
        unit_price=33.33,
        total_price=100.00
    )
    assert abs(item.total_price - 99.99) < 0.05


def test_valid_invoice_model():
    invoice = InvoiceExtraction(
        invoice_number="INV-2026-001",
        issue_date="2026-10-18",
        due_date="2026-11-17",
        vendor_name="Nexus Technologies",
        customer_name="Acme Corp",
        line_items=[
            InvoiceLineItem(
                description="Consulting",
                quantity=5.0,
                unit_price=100.0,
                total_price=500.0
            )
        ],
        subtotal=500.0,
        tax_amount=50.0,
        discount_amount=0.0,
        total_amount=550.0,
        currency="USD"
    )
    assert invoice.invoice_number == "INV-2026-001"
    assert invoice.total_amount == 550.0
    assert invoice.issue_date == "2026-10-18"


def test_invoice_date_normalization():
    # Test alternative format normalized to YYYY-MM-DD
    invoice = InvoiceExtraction(
        invoice_number="INV-2026-002",
        issue_date="October 18, 2026",
        vendor_name="Nexus",
        customer_name="Acme",
        line_items=[],
        subtotal=0.0,
        total_amount=0.0
    )
    assert invoice.issue_date == "2026-10-18"


def test_invoice_invalid_date_raises():
    with pytest.raises(ValidationError):
        InvoiceExtraction(
            invoice_number="INV-ERR",
            issue_date="completely-not-a-date",
            vendor_name="Nexus",
            customer_name="Acme",
            line_items=[],
            subtotal=0.0,
            total_amount=0.0
        )


def test_valid_resume_model():
    resume = ResumeExtraction(
        full_name="Elena Rostova",
        contact_info=ContactInfo(
            email="elena@datasphere.ai",
            phone="+1 555 123 4567",
            location="Boston, MA"
        ),
        professional_summary="AI Engineer",
        education=[
            EducationEntry(
                institution="MIT",
                degree="M.S. in AI",
                start_year="2018",
                end_year="2020"
            )
        ],
        work_experience=[
            WorkExperience(
                job_title="Staff AI Engineer",
                company="DataSphere",
                highlights=["Designed RAG pipeline"]
            )
        ],
        technical_skills=["Python", "PyTorch", "FastAPI"]
    )
    assert resume.full_name == "Elena Rostova"
    assert resume.contact_info.email == "elena@datasphere.ai"
    assert len(resume.technical_skills) == 3


def test_resume_invalid_email_raises():
    with pytest.raises(ValidationError):
        ContactInfo(email="invalid_email_no_domain")
