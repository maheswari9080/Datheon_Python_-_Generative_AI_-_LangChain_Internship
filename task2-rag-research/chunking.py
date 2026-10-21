"""
Text Chunking Module for Task 2 (RAG & Vector Embeddings).
Splits documents using RecursiveCharacterTextSplitter while maintaining full metadata provenance.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

try:
    from .document_loader import Document
except ImportError:
    from document_loader import Document

# Attempt import of langchain-text-splitters
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    LANGCHAIN_SPLITTER_AVAILABLE = True
except ImportError:
    LANGCHAIN_SPLITTER_AVAILABLE = False


class DocumentChunk(BaseModel):
    """Segmented unit of text with provenance metadata for vector indexing."""
    chunk_id: str = Field(description="Unique identifier e.g. doc.pdf_p1_c0")
    page_content: str = Field(description="Textual slice")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Provenance metadata")

    @property
    def source(self) -> str:
        return self.metadata.get("source", "unknown")

    @property
    def filename(self) -> str:
        return self.metadata.get("filename", "unknown")

    @property
    def page_number(self) -> int:
        return self.metadata.get("page_number", 1)

    @property
    def chunk_index(self) -> int:
        return self.metadata.get("chunk_index", 0)


class DocumentChunker:
    """Configurable recursive character text splitter maintaining metadata."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        if LANGCHAIN_SPLITTER_AVAILABLE:
            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ". ", "? ", "! ", "; ", " ", ""]
            )
        else:
            self._splitter = None

    def _fallback_split(self, text: str) -> List[str]:
        """Simple recursive-like splitting fallback if langchain is unavailable."""
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            
            # Find best split boundary before end
            if end < text_len:
                best_break = -1
                for sep in ["\n\n", "\n", ". ", " "]:
                    pos = text.rfind(sep, start, end)
                    if pos != -1 and pos > start + self.chunk_overlap:
                        best_break = pos + len(sep)
                        break
                if best_break != -1:
                    end = best_break

            chunk_str = text[start:end].strip()
            if chunk_str:
                chunks.append(chunk_str)

            if end >= text_len:
                break
            start = max(end - self.chunk_overlap, start + 1)

        return chunks

    def split_text(self, text: str) -> List[str]:
        if self._splitter:
            return self._splitter.split_text(text)
        return self._fallback_split(text)

    def chunk_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        """Splits a batch of Document objects into indexed DocumentChunk instances."""
        chunks: List[DocumentChunk] = []

        for doc in documents:
            text = doc.page_content.strip()
            if not text:
                continue

            text_splits = self.split_text(text)

            for idx, split_text in enumerate(text_splits):
                cleaned_split = split_text.strip()
                if not cleaned_split:
                    continue

                fn = doc.metadata.get("filename", "doc")
                safe_fn = fn.replace(" ", "_").replace("/", "_")
                page_num = doc.metadata.get("page_number", 1)
                chunk_id = f"{safe_fn}_p{page_num}_c{idx}"

                chunk_meta = dict(doc.metadata)
                chunk_meta.update({
                    "chunk_id": chunk_id,
                    "chunk_index": idx,
                    "char_count": len(cleaned_split)
                })

                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    page_content=cleaned_split,
                    metadata=chunk_meta
                ))

        return chunks
