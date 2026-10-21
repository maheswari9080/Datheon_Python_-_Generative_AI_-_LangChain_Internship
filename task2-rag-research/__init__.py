"""
Task 2: Document Q&A Assistant with RAG & Vector Embeddings.
"""
try:
    from .document_loader import Document, load_pdf, load_txt, load_uploaded_files, DocumentProcessingError
    from .chunking import DocumentChunk, DocumentChunker
    from .vector_store import (
        EmbeddingProvider,
        LocalDeterministicEmbedding,
        GeminiEmbeddingProvider,
        OpenAIEmbeddingProvider,
        InMemoryVectorStore,
        ChromaVectorStore,
        create_vector_store,
        SearchResult
    )
    from .qa_pipeline import RAGQAPipeline, QAResponse, Citation, UNSUPPORTED_QUESTION_RESPONSE
except (ImportError, TypeError):
    from document_loader import Document, load_pdf, load_txt, load_uploaded_files, DocumentProcessingError
    from chunking import DocumentChunk, DocumentChunker
    from vector_store import (
        EmbeddingProvider,
        LocalDeterministicEmbedding,
        GeminiEmbeddingProvider,
        OpenAIEmbeddingProvider,
        InMemoryVectorStore,
        ChromaVectorStore,
        create_vector_store,
        SearchResult
    )
    from qa_pipeline import RAGQAPipeline, QAResponse, Citation, UNSUPPORTED_QUESTION_RESPONSE

__all__ = [
    "Document",
    "load_pdf",
    "load_txt",
    "load_uploaded_files",
    "DocumentProcessingError",
    "DocumentChunk",
    "DocumentChunker",
    "EmbeddingProvider",
    "LocalDeterministicEmbedding",
    "GeminiEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "InMemoryVectorStore",
    "ChromaVectorStore",
    "create_vector_store",
    "SearchResult",
    "RAGQAPipeline",
    "QAResponse",
    "Citation",
    "UNSUPPORTED_QUESTION_RESPONSE",
]
