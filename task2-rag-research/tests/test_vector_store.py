import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import pytest
import numpy as np

try:
    from vector_store import (
        LocalDeterministicEmbedding,
        InMemoryVectorStore,
        ChromaVectorStore,
        create_vector_store
    )
    from chunking import DocumentChunk
except ImportError:
    from task2_rag_research.vector_store import (
        LocalDeterministicEmbedding,
        InMemoryVectorStore,
        ChromaVectorStore,
        create_vector_store
    )
    from task2_rag_research.chunking import DocumentChunk


def test_local_deterministic_embedding():
    embedder = LocalDeterministicEmbedding(dimension=256)
    assert embedder.dimension == 256

    vec1 = embedder.embed_text("Raft leader election heartbeat")
    vec2 = embedder.embed_text("Raft leader election heartbeat")
    vec3 = embedder.embed_text("Completely unrelated culinary recipe")

    assert len(vec1) == 256
    # Determinism: exact same string yields exact same vector
    assert vec1 == vec2

    # L2 norm is ~1.0
    norm = np.linalg.norm(np.array(vec1))
    assert abs(norm - 1.0) < 1e-4

    # Dot product of identical strings is 1.0, unrelated string has lower similarity
    sim_unrelated = np.dot(np.array(vec1), np.array(vec3))
    assert sim_unrelated < 0.85


def test_in_memory_vector_store():
    embedder = LocalDeterministicEmbedding(dimension=256)
    store = InMemoryVectorStore(embedding_provider=embedder)

    chunks = [
        DocumentChunk(
            chunk_id="c1",
            page_content="Heartbeat intervals are calibrated to 150ms in Raft clusters.",
            metadata={"filename": "doc1.txt", "page_number": 1}
        ),
        DocumentChunk(
            chunk_id="c2",
            page_content="Write ahead logs are flushed using synchronous fsync system calls.",
            metadata={"filename": "doc2.txt", "page_number": 2}
        )
    ]

    added = store.add_chunks(chunks)
    assert added == 2
    assert store.count == 2

    results = store.similarity_search("Raft heartbeat interval", top_k=1)
    assert len(results) == 1
    assert "Heartbeat" in results[0].page_content
    assert results[0].metadata["filename"] == "doc1.txt"


def test_chroma_vector_store_integration():
    embedder = LocalDeterministicEmbedding(dimension=128)
    store = create_vector_store(embedding_provider=embedder, use_chroma=True)

    chunks = [
        DocumentChunk(
            chunk_id="test_chroma_1",
            page_content="High dimensional vector search uses HNSW graphs with M=16.",
            metadata={"filename": "hnsw_guide.txt", "page_number": 3}
        )
    ]

    store.add_chunks(chunks)
    results = store.similarity_search("HNSW graphs", top_k=1)
    assert len(results) >= 1
    assert "HNSW" in results[0].page_content
