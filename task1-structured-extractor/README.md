# Task 1: Structured LLM Prompt Pipeline & JSON Extractor
*AI Research Workbench · Subsystem Documentation*

## Overview
The Structured LLM Extractor converts raw, unstructured textual records (such as billing invoices, receipts, and candidate resumes) into strictly typed, validated JSON objects conforming to Pydantic v2 schemas.

The pipeline integrates automated self-corrective retry loops: when an LLM produces malformed JSON or violates schema constraints (e.g. invalid date formats, negative totals, or broken line-item math), the system captures the precise validator error messages and prompts the model to repair only the faulted fields.

## Key Features
- **Pydantic v2 Schemas**: Strict type enforcement, ISO 8601 date parsing, and model-level mathematical consistency audits.
- **Dual Extraction Modes**: Specialized pipelines for **Invoices** (`InvoiceExtraction`) and **Resumes** (`ResumeExtraction`).
- **Provider Support**: Seamless support for Google Gemini (`google-genai` official SDK), OpenAI (`openai` SDK), and a deterministic **Offline Mock Provider** for zero-dependency local execution and offline CI/CD.
- **Bounded Corrective Retries**: Automatic repair loops (configurable up to 5 attempts) capturing AST and schema exceptions.
- **Web UI & CLI**: Interactive Streamlit workspace with telemetry accordions, download buttons, and preloaded sample files.

## Project Structure
```text
task1-structured-extractor/
├── app.py                  # Streamlit visual application
├── extractor.py            # Extraction engine with retry loops
├── models.py               # Pydantic v2 models (Invoice & Resume)
├── prompt_templates.py     # Few-shot prompts & repair templates
├── provider.py             # LLM provider abstractions (Gemini, OpenAI, Mock)
├── sample_data/            # Sample invoices & resumes
├── requirements.txt        # Subsystem dependencies
├── README.md               # Subsystem manual
└── tests/                  # Automated pytest suite
    ├── test_models.py
    └── test_extractor.py
```

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Running the Interactive UI
```bash
streamlit run app.py --server.port 8501
```

### 3. Programmatic Usage
```python
from task1_structured_extractor.extractor import StructuredExtractor
from task1_structured_extractor.provider import get_provider

# Instantiate with automatic fallback to Mock if API keys are absent
provider = get_provider()
extractor = StructuredExtractor(provider=provider, max_retries=3)

with open("sample_data/sample_invoice_1.txt", "r", encoding="utf-8") as f:
    text = f.read()

result = extractor.extract_invoice(text)
if result.success:
    print("Extracted Invoice:", result.data["invoice_number"])
    print(result.to_formatted_json())
else:
    print("Errors:", result.validation_errors)
```

## Running Automated Tests
```bash
pytest tests/ -v
```
