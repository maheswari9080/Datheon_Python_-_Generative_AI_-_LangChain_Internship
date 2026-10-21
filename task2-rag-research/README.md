# Task 2: Document Q&A Assistant with RAG & Vector Embeddings
*AI Research Workbench · Subsystem Documentation*

## Overview
The Document Q&A Assistant is a document-grounded question-answering architecture built to extract, index, and retrieve dense semantic embeddings from multi-page PDFs and text files while enforcing strict citation attribution and hallucination guardrails.

If a query cannot be answered based on the available indexed documentation, the pipeline rejects speculative generation and returns a verified unanswerable response:
> *"The available documents do not provide enough information to answer this question."*

## Key Features
- **Multi-Format Ingestion**: Ingests PDF documents via `pypdf` (extracting individual pages with page numbers and metadata) and plaintext files with encoding fallbacks.
- **Recursive Character Chunking**: Leverages `RecursiveCharacterTextSplitter` with configurable chunk boundaries and token overlap.
- **Dual Vector Storage Engine**:
  - **ChromaDB**: Native vector storage and similarity querying.
  - **InMemoryVectorStore**: High-speed, zero-dependency cosine similarity search engine with normalized dot products.
- **Flexible Embeddings**:
  - `LocalDeterministicEmbedding`: 256-dimensional semantic term-frequency hashing vectorizer for zero-dependency offline testing.
  - `GeminiEmbeddingProvider`: Google Gemini `text-embedding-004`.
  - `OpenAIEmbeddingProvider`: OpenAI `text-embedding-3-small`.
- **Grounded Verification**: Mandatory inline citation tracking `[Source: <filename>, Page: <page>]` with relevance score metrics.
- **Edge-Case Resilience**: Handles empty files, password-locked PDFs, corrupted files, and unanswerable queries without crashes.

## Project Structure
```text
task2-rag-research/
├── app.py                  # Streamlit visual application
├── document_loader.py      # PDF & TXT parser with page tracking
├── chunking.py             # RecursiveCharacterTextSplitter engine
├── vector_store.py         # Vector stores & embedding providers
├── qa_pipeline.py          # Grounded synthesis & citation verification
├── sample_documents/       # Preloaded technical whitepapers
├── requirements.txt        # Subsystem dependencies
├── README.md               # Subsystem manual
└── tests/                  # Automated pytest suite
    ├── test_loader_chunker.py
    ├── test_vector_store.py
    └── test_qa_pipeline.py
```

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Running the Interactive UI
```bash
streamlit run app.py --server.port 8502
```

### 3. Programmatic Usage
```python
from task2_rag_research.document_loader import load_txt
from task2_rag_research.chunking import DocumentChunker
from task2_rag_research.vector_store import create_vector_store, LocalDeterministicEmbedding
from task2_rag_research.qa_pipeline import RAGQAPipeline

# Load documents
docs = load_txt("sample_documents/distributed_systems_architecture.txt", filename="distributed_systems.txt")

# Chunk
chunker = DocumentChunker(chunk_size=400, chunk_overlap=50)
chunks = chunker.chunk_documents(docs)

# Index in Vector Store
embedder = LocalDeterministicEmbedding()
store = create_vector_store(embedding_provider=embedder, use_chroma=True)
store.add_chunks(chunks)

# Query
pipeline = RAGQAPipeline(vector_store=store)
response = pipeline.answer_question("What is the heartbeat interval in Raft consensus?")
print("Answer:", response.answer)
for citation in response.citations:
    print(f"Citation: {citation.filename} (Page {citation.page_number}) - Score: {citation.relevance_score}")
```

## Running Automated Tests
```bash
pytest tests/ -v
```
