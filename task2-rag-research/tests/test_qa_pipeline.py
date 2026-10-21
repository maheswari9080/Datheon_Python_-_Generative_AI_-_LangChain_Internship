import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import pytest

try:
    from qa_pipeline import RAGQAPipeline, UNSUPPORTED_QUESTION_RESPONSE
    from vector_store import InMemoryVectorStore, LocalDeterministicEmbedding
    from chunking import DocumentChunk
except ImportError:
    from task2_rag_research.qa_pipeline import RAGQAPipeline, UNSUPPORTED_QUESTION_RESPONSE
    from task2_rag_research.vector_store import InMemoryVectorStore, LocalDeterministicEmbedding
    from task2_rag_research.chunking import DocumentChunk


def test_grounded_qa_with_evidence():
    embedder = LocalDeterministicEmbedding()
    store = InMemoryVectorStore(embedding_provider=embedder)

    chunks = [
        DocumentChunk(
            chunk_id="chunk_raft",
            page_content="Heartbeat intervals in Raft are strictly calibrated to 150ms to detect node crashes.",
            metadata={"filename": "consensus.txt", "page_number": 2}
        )
    ]
    store.add_chunks(chunks)

    pipeline = RAGQAPipeline(vector_store=store, min_relevance_score=0.10)
    response = pipeline.answer_question("What is the heartbeat interval in Raft?")

    assert response.is_grounded is True
    assert response.evidence_found is True
    assert len(response.citations) > 0
    assert response.citations[0].filename == "consensus.txt"
    assert response.citations[0].page_number == 2
    assert "150ms" in response.answer


def test_unsupported_question_rejection():
    embedder = LocalDeterministicEmbedding()
    store = InMemoryVectorStore(embedding_provider=embedder)

    # Empty store or unrelated content with high threshold
    pipeline = RAGQAPipeline(vector_store=store, min_relevance_score=0.50)
    response = pipeline.answer_question("What is the recipe for baking chocolate cookies?")

    assert response.evidence_found is False
    assert len(response.citations) == 0
    assert "not provide enough information" in response.answer.lower()
