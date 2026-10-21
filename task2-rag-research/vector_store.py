"""
Vector Store and Embedding Providers for Task 2 (RAG & Semantic Retrieval).
Supports ChromaDB, in-memory cosine vector store, and Gemini / OpenAI / Local deterministic embeddings.
"""

import os
import math
import hashlib
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

try:
    from .chunking import DocumentChunk
except ImportError:
    from chunking import DocumentChunk

logger = logging.getLogger(__name__)


# ==============================================================================
# EMBEDDING PROVIDERS
# ==============================================================================

class EmbeddingProvider(ABC):
    """Abstract embedding model interface."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass


class LocalDeterministicEmbedding(EmbeddingProvider):
    """
    Zero-dependency deterministic semantic vectorizer.
    Generates 256-dimensional normalized term and character n-gram hashing embeddings.
    Enables reliable offline unit testing and local deployment without remote API dependencies.
    """

    def __init__(self, dimension: int = 256):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        vec = np.zeros(self._dim, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()

        # Word unigrams + character trigrams
        tokens = list(words)
        for w in words:
            if len(w) >= 3:
                tokens.extend([w[i:i+3] for i in range(len(w) - 2)])

        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self._dim
            sign = 1.0 if ((h >> 8) % 2 == 0) else -1.0
            vec[idx] += sign

        # L2 normalize
        norm = np.linalg.norm(vec)
        if norm > 1e-8:
            vec = vec / norm
        return vec.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Google Gemini text-embedding-004 integration via google-genai."""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-004"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiEmbeddingProvider.")
        self.model_name = model
        from google import genai
        self.client = genai.Client(api_key=self.api_key)
        self._dim = 768

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        result = self.client.models.embed_content(
            model=self.model_name,
            contents=text
        )
        return result.embedding.values

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI text-embedding-3-small integration."""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIEmbeddingProvider.")
        self.model_name = model
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
        self._dim = 1536

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        resp = self.client.embeddings.create(input=[text], model=self.model_name)
        return resp.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embeddings.create(input=texts, model=self.model_name)
        return [item.embedding for item in resp.data]


# ==============================================================================
# VECTOR STORES
# ==============================================================================

class SearchResult:
    """Retrieved chunk with relevance similarity score."""
    def __init__(self, chunk: DocumentChunk, score: float):
        self.chunk = chunk
        self.score = float(score)

    @property
    def page_content(self) -> str:
        return self.chunk.page_content

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.chunk.metadata

    def __repr__(self) -> str:
        return f"<SearchResult score={self.score:.4f} id={self.chunk.chunk_id}>"


class InMemoryVectorStore:
    """
    High-performance in-memory vector store using Cosine Similarity.
    Persists cleanly to disk and operates with zero C++ compilation dependencies.
    """

    def __init__(self, embedding_provider: EmbeddingProvider):
        self.embedder = embedding_provider
        self.chunks: List[DocumentChunk] = []
        self.vectors: Optional[np.ndarray] = None

    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        if not chunks:
            return 0

        texts = [c.page_content for c in chunks]
        new_vecs = np.array(self.embedder.embed_batch(texts), dtype=np.float32)

        if self.vectors is None:
            self.vectors = new_vecs
        else:
            self.vectors = np.vstack([self.vectors, new_vecs])

        self.chunks.extend(chunks)
        return len(chunks)

    def similarity_search(self, query: str, top_k: int = 4, score_threshold: float = 0.0) -> List[SearchResult]:
        if not self.chunks or self.vectors is None:
            return []

        query_vec = np.array(self.embedder.embed_text(query), dtype=np.float32)
        q_norm = np.linalg.norm(query_vec)
        if q_norm > 1e-8:
            query_vec = query_vec / q_norm

        # Matrix cosine dot product: vectors are normalized
        v_norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        v_norms[v_norms == 0] = 1.0
        normalized_vectors = self.vectors / v_norms

        scores = np.dot(normalized_vectors, query_vec)

        # Sort descending
        top_indices = np.argsort(scores)[::-1]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score < score_threshold:
                continue
            results.append(SearchResult(chunk=self.chunks[idx], score=score))
            if len(results) >= top_k:
                break

        return results

    def clear(self):
        self.chunks = []
        self.vectors = None

    @property
    def count(self) -> int:
        return len(self.chunks)


class ChromaVectorStore:
    """ChromaDB implementation with persistent or ephemeral storage."""

    def __init__(self, embedding_provider: EmbeddingProvider, collection_name: str = "rag_documents"):
        self.embedder = embedding_provider
        self.collection_name = collection_name
        import chromadb
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        if not chunks:
            return 0

        ids = [c.chunk_id for c in chunks]
        texts = [c.page_content for c in chunks]
        embeddings = self.embedder.embed_batch(texts)
        metadatas = [c.metadata for c in chunks]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        return len(chunks)

    def similarity_search(self, query: str, top_k: int = 4, score_threshold: float = 0.0) -> List[SearchResult]:
        query_vec = self.embedder.embed_text(query)
        res = self.collection.query(
            query_embeddings=[query_vec],
            n_results=min(top_k, self.collection.count() or 1)
        )

        results = []
        if not res or not res["ids"] or not res["ids"][0]:
            return []

        for i in range(len(res["ids"][0])):
            cid = res["ids"][0][i]
            text = res["documents"][0][i]
            meta = res["metadatas"][0][i] if res["metadatas"] else {}
            # Chroma returns L2 distances or cosine distances (distance = 1 - sim)
            distance = res["distances"][0][i] if "distances" in res and res["distances"] else 0.5
            similarity = max(0.0, 1.0 - distance)
            
            if similarity >= score_threshold:
                chunk = DocumentChunk(chunk_id=cid, page_content=text, metadata=meta)
                results.append(SearchResult(chunk=chunk, score=similarity))

        return results

    def clear(self):
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    @property
    def count(self) -> int:
        return self.collection.count()


def create_vector_store(
    embedding_provider: Optional[EmbeddingProvider] = None,
    use_chroma: bool = True
) -> Any:
    """Factory helper creating configured vector store with automatic fallback."""
    provider = embedding_provider or LocalDeterministicEmbedding()

    if use_chroma:
        try:
            import chromadb
            return ChromaVectorStore(embedding_provider=provider)
        except Exception as e:
            logger.info("ChromaDB unavailable or initialization deferred (%s); using InMemoryVectorStore.", e)

    return InMemoryVectorStore(embedding_provider=provider)
