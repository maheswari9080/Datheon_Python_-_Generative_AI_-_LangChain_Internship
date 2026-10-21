import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import pytest
import io

try:
    from document_loader import load_txt, load_pdf, load_uploaded_files, DocumentProcessingError
    from chunking import DocumentChunker, DocumentChunk
except ImportError:
    from task2_rag_research.document_loader import load_txt, load_pdf, load_uploaded_files, DocumentProcessingError
    from task2_rag_research.chunking import DocumentChunker, DocumentChunk


def test_load_txt_success(tmp_path):
    test_file = tmp_path / "sample.txt"
    test_file.write_text("Paragraph 1.\n\nParagraph 2 with details.", encoding="utf-8")

    docs = load_txt(test_file, filename="sample.txt")
    assert len(docs) == 1
    assert "Paragraph 1" in docs[0].page_content
    assert docs[0].metadata["filename"] == "sample.txt"
    assert docs[0].metadata["page_number"] == 1
    assert docs[0].metadata["char_count"] > 0


def test_load_txt_empty_raises(tmp_path):
    test_file = tmp_path / "empty.txt"
    test_file.write_text("   \n   ", encoding="utf-8")

    with pytest.raises(DocumentProcessingError):
        load_txt(test_file, filename="empty.txt")


def test_load_pdf_pages():
    pdf_path = MODULE_DIR / "sample_documents" / "sample_document.pdf"
    if pdf_path.exists():
        # Blank PDF has 0 extractable text, so should raise or return pages
        try:
            docs = load_pdf(pdf_path, filename="sample_document.pdf")
            assert len(docs) >= 1
        except DocumentProcessingError as e:
            assert "no extractable text" in str(e).lower()


def test_chunker_metadata_preservation(tmp_path):
    test_file = tmp_path / "long_doc.txt"
    content = "Raft Consensus Algorithm. " * 30  # ~800 chars
    test_file.write_text(content, encoding="utf-8")

    docs = load_txt(test_file, filename="long_doc.txt")
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=30)
    chunks = chunker.chunk_documents(docs)

    assert len(chunks) > 1
    for idx, c in enumerate(chunks):
        assert c.metadata["filename"] == "long_doc.txt"
        assert c.metadata["page_number"] == 1
        assert c.metadata["chunk_index"] == idx
        assert f"c{idx}" in c.chunk_id
