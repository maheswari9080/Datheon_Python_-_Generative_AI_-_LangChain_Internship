"""
Document Loader for Task 2 (RAG & Vector Embeddings).
Extracts text from PDF and TXT files, preserving filename, page numbers, and structural metadata.
Gracefully handles corrupted PDFs, empty files, and encoding anomalies.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Union, Tuple, BinaryIO
from pydantic import BaseModel, Field
import pypdf


class Document(BaseModel):
    """Normalized document representation containing page text and metadata."""
    page_content: str = Field(description="Extracted textual content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary: source, page, filename")

    @property
    def source(self) -> str:
        return self.metadata.get("source", "unknown")

    @property
    def filename(self) -> str:
        return self.metadata.get("filename", "unknown")

    @property
    def page_number(self) -> int:
        return self.metadata.get("page_number", 1)


class DocumentProcessingError(Exception):
    """Exception raised when document extraction fails."""
    pass


def load_pdf(file_source: Union[str, Path, BinaryIO], filename: str = "document.pdf") -> List[Document]:
    """
    Extracts pages from a PDF file with page-level metadata.
    Handles unreadable/encrypted files and empty pages.
    """
    documents: List[Document] = []
    
    try:
        reader = pypdf.PdfReader(file_source)
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise DocumentProcessingError(f"PDF '{filename}' is password-encrypted and cannot be parsed.")

        total_pages = len(reader.pages)
        if total_pages == 0:
            raise DocumentProcessingError(f"PDF '{filename}' contains 0 pages.")

        for page_idx, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception as e:
                page_text = f"[Warning: Text extraction failed on page {page_idx}: {str(e)}]"

            page_text = page_text.strip()
            if page_text:
                documents.append(Document(
                    page_content=page_text,
                    metadata={
                        "source": str(filename),
                        "filename": str(filename),
                        "page_number": page_idx,
                        "total_pages": total_pages,
                        "char_count": len(page_text),
                        "file_type": "pdf"
                    }
                ))

        if not documents:
            raise DocumentProcessingError(f"PDF '{filename}' has no extractable text (may be image-only scan).")

        return documents

    except DocumentProcessingError:
        raise
    except Exception as e:
        raise DocumentProcessingError(f"Failed to parse PDF '{filename}': {str(e)}") from e


def load_txt(file_source: Union[str, Path, BinaryIO], filename: str = "document.txt") -> List[Document]:
    """
    Extracts text from a TXT file with metadata.
    Handles multiple text encodings and detects empty files.
    """
    raw_content = ""
    
    if hasattr(file_source, "read"):
        content_bytes = file_source.read()
        if isinstance(content_bytes, str):
            raw_content = content_bytes
        else:
            for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
                try:
                    raw_content = content_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
    else:
        path = Path(file_source)
        if not path.exists():
            raise DocumentProcessingError(f"File not found: {path}")
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                raw_content = path.read_text(encoding=enc)
                break
            except UnicodeDecodeError:
                continue

    cleaned_content = raw_content.strip()
    if not cleaned_content:
        raise DocumentProcessingError(f"TXT document '{filename}' is empty.")

    return [Document(
        page_content=cleaned_content,
        metadata={
            "source": str(filename),
            "filename": str(filename),
            "page_number": 1,
            "total_pages": 1,
            "char_count": len(cleaned_content),
            "file_type": "txt"
        }
    )]


def load_uploaded_files(uploaded_files: List[Any]) -> Tuple[List[Document], List[str]]:
    """
    Batch processor for multiple uploaded files (Streamlit UploadedFile or local paths).
    Returns (loaded_documents, error_log).
    """
    all_docs: List[Document] = []
    errors: List[str] = []

    for file_obj in uploaded_files:
        name = getattr(file_obj, "name", str(file_obj))
        lower_name = name.lower()
        try:
            if lower_name.endswith(".pdf"):
                docs = load_pdf(file_obj, filename=name)
                all_docs.extend(docs)
            elif lower_name.endswith(".txt") or lower_name.endswith(".md"):
                docs = load_txt(file_obj, filename=name)
                all_docs.extend(docs)
            else:
                errors.append(f"Skipped '{name}': Unsupported format. Only PDF and TXT are supported.")
        except DocumentProcessingError as dpe:
            errors.append(str(dpe))
        except Exception as e:
            errors.append(f"Unexpected error processing '{name}': {str(e)}")

    return all_docs, errors
