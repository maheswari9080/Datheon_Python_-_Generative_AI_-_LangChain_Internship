"""
Pydantic v2 Models for Structured Information Extraction
Defines schema definitions and validation logic for Invoices and Resumes.
"""

from typing import List, Optional
from datetime import datetime
import re
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class InvoiceLineItem(BaseModel):
    """Line item detailing specific goods or services on an invoice."""
    description: str = Field(description="Description of the item or service rendered")
    quantity: float = Field(ge=0.0, description="Quantity of items or hours billed")
    unit_price: float = Field(ge=0.0, description="Unit rate or price per item")
    total_price: float = Field(ge=0.0, description="Computed total price for this line item")

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_line_total(self) -> "InvoiceLineItem":
        expected = round(self.quantity * self.unit_price, 2)
        # Allow minor rounding tolerance of $0.05
        if abs(self.total_price - expected) > 0.05 and self.total_price != 0:
            # Self-correct if clearly a rounding mismatch
            if abs(self.total_price - expected) <= 0.10:
                self.total_price = expected
        return self


class InvoiceExtraction(BaseModel):
    """Complete structured invoice schema."""
    invoice_number: str = Field(description="Unique invoice identifier or code")
    issue_date: str = Field(description="Invoice issuance date in YYYY-MM-DD format")
    due_date: Optional[str] = Field(default=None, description="Payment due date in YYYY-MM-DD format")
    
    vendor_name: str = Field(description="Legal name of the billing company or entity")
    vendor_address: Optional[str] = Field(default=None, description="Billing address of vendor")
    vendor_tax_id: Optional[str] = Field(default=None, description="Vendor Tax ID / VAT / EIN number")
    
    customer_name: str = Field(description="Recipient company or individual name")
    customer_address: Optional[str] = Field(default=None, description="Billing address of recipient")
    
    line_items: List[InvoiceLineItem] = Field(default_factory=list, description="List of invoiced items")
    
    subtotal: float = Field(ge=0.0, description="Sum of line item amounts before tax and discount")
    tax_amount: Optional[float] = Field(default=0.0, ge=0.0, description="Tax or VAT applied")
    discount_amount: Optional[float] = Field(default=0.0, ge=0.0, description="Discounts applied")
    total_amount: float = Field(ge=0.0, description="Final payable invoice amount")
    currency: str = Field(default="USD", description="ISO 4217 currency code e.g. USD, EUR, GBP")
    payment_terms: Optional[str] = Field(default=None, description="Payment terms e.g. Net 30, Due on Receipt")

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    @field_validator("issue_date", "due_date")
    @classmethod
    def validate_iso_date(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        v = v.strip()
        # Accept YYYY-MM-DD
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"):
            try:
                dt = datetime.strptime(v, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        # If regex matches YYYY-MM-DD directly
        if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            return v
        raise ValueError(f"Invalid date format '{v}'. Expected ISO format YYYY-MM-DD.")

    @model_validator(mode="after")
    def validate_totals(self) -> "InvoiceExtraction":
        computed_subtotal = round(sum(item.total_price for item in self.line_items), 2)
        if self.subtotal == 0.0 and computed_subtotal > 0:
            self.subtotal = computed_subtotal
            
        tax = self.tax_amount or 0.0
        discount = self.discount_amount or 0.0
        expected_total = round(self.subtotal + tax - discount, 2)
        
        # If total_amount was omitted or significantly deviates
        if self.total_amount == 0.0 and expected_total > 0:
            self.total_amount = expected_total
        return self


class ContactInfo(BaseModel):
    """Candidate contact details."""
    email: Optional[str] = Field(default=None, description="Primary email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="City, State / Country")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile link")
    github_url: Optional[str] = Field(default=None, description="GitHub profile link")
    portfolio_url: Optional[str] = Field(default=None, description="Personal website or portfolio")

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        v = v.strip()
        if "@" not in v or "." not in v:
            raise ValueError(f"Invalid email address: '{v}'")
        return v


class EducationEntry(BaseModel):
    """Academic degree or qualification."""
    institution: str = Field(description="College, University or Academy")
    degree: str = Field(description="Degree name e.g. Bachelor of Science")
    field_of_study: Optional[str] = Field(default=None, description="Major or specialization")
    start_year: Optional[str] = Field(default=None, description="Start year or date")
    end_year: Optional[str] = Field(default=None, description="Graduation year or 'Present'")
    gpa: Optional[str] = Field(default=None, description="GPA or honors if provided")

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class WorkExperience(BaseModel):
    """Professional employment history entry."""
    job_title: str = Field(description="Title or role held")
    company: str = Field(description="Employer name")
    location: Optional[str] = Field(default=None, description="Location of employment")
    start_date: Optional[str] = Field(default=None, description="Employment start date")
    end_date: Optional[str] = Field(default=None, description="Employment end date or 'Present'")
    highlights: List[str] = Field(default_factory=list, description="Key accomplishments and responsibilities")

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class CertificationEntry(BaseModel):
    """Professional license or certificate."""
    name: str = Field(description="Certificate title")
    issuer: Optional[str] = Field(default=None, description="Issuing organization")
    issue_date: Optional[str] = Field(default=None, description="Date issued")

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class ResumeExtraction(BaseModel):
    """Complete structured resume schema."""
    full_name: str = Field(description="Candidate's full legal or professional name")
    contact_info: ContactInfo = Field(default_factory=ContactInfo, description="Candidate contact details")
    professional_summary: Optional[str] = Field(default=None, description="Career overview or objective")
    education: List[EducationEntry] = Field(default_factory=list, description="Academic history")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="Employment records")
    technical_skills: List[str] = Field(default_factory=list, description="Programming languages, frameworks, tools")
    soft_skills: List[str] = Field(default_factory=list, description="Interpersonal and leadership competencies")
    certifications: List[CertificationEntry] = Field(default_factory=list, description="Certifications and licenses")
    languages: List[str] = Field(default_factory=list, description="Spoken/written languages")

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)
