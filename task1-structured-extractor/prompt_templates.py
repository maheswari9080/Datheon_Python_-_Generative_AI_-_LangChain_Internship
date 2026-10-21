"""
Prompt templates and few-shot examples for structured information extraction.
Supports parameterized prompts and corrective retry cycles.
"""

# ==============================================================================
# INVOICE EXTRACTION PROMPTS
# ==============================================================================

INVOICE_SYSTEM_PROMPT = """You are an expert financial document parser and data extraction specialist.
Your task is to extract structured invoice data from the provided raw text and output strictly valid JSON conforming to the requested schema.

CRITICAL RULES:
1. ONLY extract information explicitly present in the document. DO NOT fabricate, guess, or extrapolate dates, numbers, or names.
2. If a field (e.g. tax_id, payment_terms, due_date) is missing or unstated, return null (None).
3. Standardize dates to ISO 8601 format: YYYY-MM-DD.
4. Numerical values (quantities, prices, totals) must be clean floats/integers without currency symbols.
5. Ensure line item calculations (quantity * unit_price = total_price) are mathematically consistent.
6. Return ONLY the raw JSON object. Do not wrap in markdown quotes (` ```json `), do not include preambles or postscripts.
"""

INVOICE_FEW_SHOT_USER = """Acme Software Inc.
100 Innovation Way, Suite 400, Austin, TX 78701
Tax ID: US-882910394

INVOICE #: INV-2026-089
Date: 15 Oct 2026
Due Date: 14 Nov 2026
Terms: Net 30

Billed To:
Global Logistics Partners
500 Harbor Blvd, Long Beach, CA 90802

Description                     Qty    Rate      Amount
Cloud Architecture Consulting   40.0   $175.00   $7,000.00
API Gateway Integration Setup   1.0    $2,500.00 $2,500.00

Subtotal: $9,500.00
Tax (8.25%): $783.75
Total Due: $10,283.75 USD
"""

INVOICE_FEW_SHOT_ASSISTANT = """{
  "invoice_number": "INV-2026-089",
  "issue_date": "2026-10-15",
  "due_date": "2026-11-14",
  "vendor_name": "Acme Software Inc.",
  "vendor_address": "100 Innovation Way, Suite 400, Austin, TX 78701",
  "vendor_tax_id": "US-882910394",
  "customer_name": "Global Logistics Partners",
  "customer_address": "500 Harbor Blvd, Long Beach, CA 90802",
  "line_items": [
    {
      "description": "Cloud Architecture Consulting",
      "quantity": 40.0,
      "unit_price": 175.0,
      "total_price": 7000.0
    },
    {
      "description": "API Gateway Integration Setup",
      "quantity": 1.0,
      "unit_price": 2500.0,
      "total_price": 2500.0
    }
  ],
  "subtotal": 9500.0,
  "tax_amount": 783.75,
  "discount_amount": 0.0,
  "total_amount": 10283.75,
  "currency": "USD",
  "payment_terms": "Net 30"
}"""


# ==============================================================================
# RESUME EXTRACTION PROMPTS
# ==============================================================================

RESUME_SYSTEM_PROMPT = """You are an expert talent recruitment analyst and resume parsing engine.
Your task is to parse unstructured resume text into a strictly typed, structured JSON representation.

CRITICAL RULES:
1. ONLY extract information that is explicitly stated. Do not infer unmentioned credentials, degrees, or companies.
2. Differentiate technical skills (languages, libraries, platforms) from soft skills (communication, leadership).
3. If contact information (phone, email, links) is not provided, set the respective field to null.
4. Output strictly valid JSON conforming to the schema. Do not include markdown codeblocks or conversational commentary.
"""

RESUME_FEW_SHOT_USER = """Alex Morgan
alex.morgan@cybertech.io | (415) 555-0199 | San Francisco, CA
linkedin.com/in/alexmorgan-dev | github.com/alexm-ai

Professional Summary
Senior Machine Learning Engineer with 6+ years designing real-time inference microservices, vector search architectures, and distributed training pipelines.

Education
University of California, Berkeley - B.S. in Computer Science (2016 - 2020)
GPA: 3.85 / 4.0

Experience
Lead AI Platform Engineer | Datastream AI | San Francisco, CA
June 2022 - Present
- Architected enterprise vector search cluster reducing query latency by 45%.
- Supervised migration to Python 3.12 and async FastAPI endpoints serving 50M requests daily.

Machine Learning Engineer | Apex Neural Labs | Oakland, CA
August 2020 - May 2022
- Built automated model evaluation and data validation harness using PyTest and Pydantic.
- Optimized PyTorch model quantization for edge deployment.

Technical Skills: Python, PyTorch, LangChain, FastAPI, Docker, Kubernetes, PostgreSQL, Redis
Soft Skills: Technical Mentorship, Cross-Functional Collaboration, Agile Leadership
Certifications: AWS Certified Machine Learning - Specialty (Amazon Web Services, 2023)
Languages: English, Spanish
"""

RESUME_FEW_SHOT_ASSISTANT = """{
  "full_name": "Alex Morgan",
  "contact_info": {
    "email": "alex.morgan@cybertech.io",
    "phone": "(415) 555-0199",
    "location": "San Francisco, CA",
    "linkedin_url": "linkedin.com/in/alexmorgan-dev",
    "github_url": "github.com/alexm-ai",
    "portfolio_url": null
  },
  "professional_summary": "Senior Machine Learning Engineer with 6+ years designing real-time inference microservices, vector search architectures, and distributed training pipelines.",
  "education": [
    {
      "institution": "University of California, Berkeley",
      "degree": "B.S. in Computer Science",
      "field_of_study": "Computer Science",
      "start_year": "2016",
      "end_year": "2020",
      "gpa": "3.85 / 4.0"
    }
  ],
  "work_experience": [
    {
      "job_title": "Lead AI Platform Engineer",
      "company": "Datastream AI",
      "location": "San Francisco, CA",
      "start_date": "June 2022",
      "end_date": "Present",
      "highlights": [
        "Architected enterprise vector search cluster reducing query latency by 45%.",
        "Supervised migration to Python 3.12 and async FastAPI endpoints serving 50M requests daily."
      ]
    },
    {
      "job_title": "Machine Learning Engineer",
      "company": "Apex Neural Labs",
      "location": "Oakland, CA",
      "start_date": "August 2020",
      "end_date": "May 2022",
      "highlights": [
        "Built automated model evaluation and data validation harness using PyTest and Pydantic.",
        "Optimized PyTorch model quantization for edge deployment."
      ]
    }
  ],
  "technical_skills": [
    "Python", "PyTorch", "LangChain", "FastAPI", "Docker", "Kubernetes", "PostgreSQL", "Redis"
  ],
  "soft_skills": [
    "Technical Mentorship", "Cross-Functional Collaboration", "Agile Leadership"
  ],
  "certifications": [
    {
      "name": "AWS Certified Machine Learning - Specialty",
      "issuer": "Amazon Web Services",
      "issue_date": "2023"
    }
  ],
  "languages": ["English", "Spanish"]
}"""


# ==============================================================================
# CORRECTIVE REPAIR PROMPT
# ==============================================================================

CORRECTIVE_REPAIR_PROMPT = """Your previous JSON extraction failed schema validation with the following specific error(s):

VALIDATION ERRORS:
{validation_errors}

PREVIOUS MODEL OUTPUT:
{previous_output}

ORIGINAL SOURCE DOCUMENT:
{source_text}

INSTRUCTIONS:
1. Carefully inspect each validation error listed above.
2. Correct the invalid values, missing required fields, or formatting issues (such as date formats or line-item totals).
3. Do not invent details; verify against the original source document.
4. Return ONLY the repaired, valid JSON object.
"""


def build_extraction_prompt(mode: str, document_text: str) -> list[dict]:
    """
    Constructs parameterized message sequence including system prompt,
    few-shot demonstration, and target document.
    """
    if mode.lower() == "invoice":
        return [
            {"role": "system", "content": INVOICE_SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract invoice data from the following text:\n\n{INVOICE_FEW_SHOT_USER}"},
            {"role": "assistant", "content": INVOICE_FEW_SHOT_ASSISTANT},
            {"role": "user", "content": f"Extract invoice data from the following text:\n\n{document_text}"}
        ]
    elif mode.lower() == "resume":
        return [
            {"role": "system", "content": RESUME_SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract resume details from the following text:\n\n{RESUME_FEW_SHOT_USER}"},
            {"role": "assistant", "content": RESUME_FEW_SHOT_ASSISTANT},
            {"role": "user", "content": f"Extract resume details from the following text:\n\n{document_text}"}
        ]
    else:
        raise ValueError(f"Unsupported extraction mode: {mode}")
