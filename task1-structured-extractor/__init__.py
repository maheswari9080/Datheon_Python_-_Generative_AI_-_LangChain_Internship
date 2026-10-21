"""
Task 1: Structured LLM Prompt Pipeline & JSON Extractor.
"""
try:
    from .models import InvoiceExtraction, ResumeExtraction, InvoiceLineItem, ContactInfo
    from .extractor import StructuredExtractor, ExtractionResult, ExtractionAttempt
    from .provider import get_provider, LLMProvider, GeminiProvider, OpenAIProvider, MockProvider
except (ImportError, TypeError):
    from models import InvoiceExtraction, ResumeExtraction, InvoiceLineItem, ContactInfo
    from extractor import StructuredExtractor, ExtractionResult, ExtractionAttempt
    from provider import get_provider, LLMProvider, GeminiProvider, OpenAIProvider, MockProvider

__all__ = [
    "InvoiceExtraction",
    "ResumeExtraction",
    "InvoiceLineItem",
    "ContactInfo",
    "StructuredExtractor",
    "ExtractionResult",
    "ExtractionAttempt",
    "get_provider",
    "LLMProvider",
    "GeminiProvider",
    "OpenAIProvider",
    "MockProvider",
]
