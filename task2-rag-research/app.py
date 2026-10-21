"""
Task 2: Document Q&A Assistant with RAG & Vector Embeddings
Interactive Streamlit application for multi-document ingestion, vector indexing,
grounded semantic retrieval, and citation verification.
"""

import sys
import os
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

TASK1_DIR = ROOT_DIR / "task1-structured-extractor"
if str(TASK1_DIR) not in sys.path:
    sys.path.insert(0, str(TASK1_DIR))

import streamlit as st

from document_loader import load_uploaded_files, load_txt
from chunking import DocumentChunker
from vector_store import (
    create_vector_store,
    LocalDeterministicEmbedding,
    GeminiEmbeddingProvider,
    OpenAIEmbeddingProvider,
    InMemoryVectorStore,
    ChromaVectorStore
)
from qa_pipeline import RAGQAPipeline, UNSUPPORTED_QUESTION_RESPONSE
from provider import get_provider, GeminiProvider, OpenAIProvider, MockProvider

# Page configuration
st.set_page_config(
    page_title="Task 2: RAG Document Research | AI Research Workbench",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Research Workbench Aesthetic
st.markdown("""
<style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .citation-card {
        padding: 12px;
        background-color: #f8fafc;
        border-left: 3px solid #0d9488;
        border-radius: 4px;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
    .citation-badge {
        display: inline-block;
        padding: 2px 8px;
        background-color: #e0f2fe;
        color: #0369a1;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-badge {
        display: inline-block;
        padding: 4px 10px;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.85rem;
        color: #0f172a;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "vector_store" not in st.session_state:
    st.session_state.vector_store = create_vector_store(use_chroma=True)
if "indexed_docs_meta" not in st.session_state:
    st.session_state.indexed_docs_meta = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ RAG Engine Settings")
    
    vector_backend = st.selectbox(
        "Vector Store Backend",
        options=["ChromaDB (Local)", "InMemory Cosine Vector Store"],
        index=0,
        help="Select ChromaDB or high-performance zero-dependency in-memory store."
    )
    
    embedding_choice = st.selectbox(
        "Embedding Model",
        options=["Local Semantic Vectorizer (Offline)", "Google Gemini (text-embedding-004)", "OpenAI (text-embedding-3-small)"],
        index=0
    )
    
    llm_choice = st.selectbox(
        "Answer Synthesis LLM",
        options=["Offline Mock / Grounded Extractor", "Google Gemini", "OpenAI"],
        index=0
    )
    
    api_key_input = ""
    if "Gemini" in embedding_choice or "Gemini" in llm_choice:
        api_key_input = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    elif "OpenAI" in embedding_choice or "OpenAI" in llm_choice:
        api_key_input = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")

    top_k = st.slider("Top-K Retrieved Chunks", min_value=1, max_value=8, value=3)
    min_score = st.slider("Relevance Score Threshold", min_value=0.0, max_value=0.8, value=0.15, step=0.05)

    st.divider()
    st.markdown("### 📊 Indexing Status")
    chunk_count = getattr(st.session_state.vector_store, "count", 0)
    st.metric("Indexed Chunks", chunk_count)
    st.metric("Documents Ingested", len(st.session_state.indexed_docs_meta))
    
    if st.button("🗑️ Reset Vector Database", use_container_width=True):
        st.session_state.vector_store.clear()
        st.session_state.indexed_docs_meta = []
        st.session_state.chat_history = []
        st.success("Vector store wiped successfully.")
        st.rerun()

    st.markdown("<div style='font-size:0.8rem; color:#64748b; margin-top:20px;'>AI Research Workbench · Task 2</div>", unsafe_allow_html=True)


# Main Content Header
st.markdown('<div class="main-title">Document Q&A Assistant with Grounded RAG</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload PDF and TXT research papers, index high-dimensional embeddings, and ask grounded questions with strict source attribution.</div>', unsafe_allow_html=True)

tab_qa, tab_library = st.tabs(["💬 Grounded Document Q&A", "📂 Document Library & Indexer"])


# -----------------------------------------------------------------------------
# TAB 2: DOCUMENT LIBRARY & INDEXER
# -----------------------------------------------------------------------------
with tab_library:
    st.subheader("Ingest Research Documents (PDF / TXT)")
    
    col_upload, col_sample = st.columns([1, 1], gap="medium")
    
    with col_upload:
        st.markdown("**Custom File Upload**")
        uploaded_files = st.file_uploader(
            "Upload multiple PDF or TXT files",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True
        )
        btn_index_uploaded = st.button("📥 Index Uploaded Files", type="primary")

    with col_sample:
        st.markdown("**Preloaded Research Samples**")
        sample_choice = st.selectbox(
            "Select Benchmark Corpus",
            options=["Distributed Systems Architecture (WAL, Raft, HNSW)", "AI Safety & Grounding Guardrails Whitepaper"]
        )
        btn_index_sample = st.button("📑 Index Selected Sample", type="secondary")

    # Handle indexing
    files_to_process = []
    if btn_index_uploaded and uploaded_files:
        files_to_process = uploaded_files
    elif btn_index_sample:
        if "Distributed Systems" in sample_choice:
            sample_path = CURRENT_DIR / "sample_documents" / "distributed_systems_architecture.txt"
        else:
            sample_path = CURRENT_DIR / "sample_documents" / "ai_safety_and_guardrails.txt"
        
        if sample_path.exists():
            files_to_process = [sample_path]

    if files_to_process:
        with st.spinner("Extracting content, splitting into recursive chunks, and indexing embeddings..."):
            try:
                # 1. Load documents
                loaded_docs, errors = load_uploaded_files(files_to_process)
                if errors:
                    for err in errors:
                        st.warning(err)

                if loaded_docs:
                    # 2. Chunk documents
                    chunker = DocumentChunker(chunk_size=450, chunk_overlap=60)
                    chunks = chunker.chunk_documents(loaded_docs)

                    # 3. Embedding provider selection
                    if "Gemini" in embedding_choice:
                        emb_prov = GeminiEmbeddingProvider(api_key=api_key_input or None)
                    elif "OpenAI" in embedding_choice:
                        emb_prov = OpenAIEmbeddingProvider(api_key=api_key_input or None)
                    else:
                        emb_prov = LocalDeterministicEmbedding()

                    # 4. Check store backend
                    if "ChromaDB" in vector_backend:
                        try:
                            store = ChromaVectorStore(embedding_provider=emb_prov)
                        except Exception:
                            store = InMemoryVectorStore(embedding_provider=emb_prov)
                    else:
                        store = InMemoryVectorStore(embedding_provider=emb_prov)

                    added_count = store.add_chunks(chunks)
                    st.session_state.vector_store = store

                    # Record metadata
                    for doc in loaded_docs:
                        fn = doc.filename
                        if fn not in st.session_state.indexed_docs_meta:
                            st.session_state.indexed_docs_meta.append(fn)

                    st.success(f"Successfully processed and indexed {len(loaded_docs)} pages into {added_count} vector chunks!")
                    st.rerun()

            except Exception as e:
                st.error(f"Indexing failed: {str(e)}")

    st.divider()
    st.subheader("Currently Indexed Documents")
    if st.session_state.indexed_docs_meta:
        for doc_name in st.session_state.indexed_docs_meta:
            st.markdown(f"- 📄 `{doc_name}`")
    else:
        st.info("No documents indexed yet. Ingest files above to begin questioning.")


# -----------------------------------------------------------------------------
# TAB 1: GROUNDED DOCUMENT Q&A
# -----------------------------------------------------------------------------
with tab_qa:
    col_chat, col_citations = st.columns([1.2, 0.8], gap="medium")

    with col_chat:
        st.subheader("Ask Questions Against Grounded Corpus")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "telemetry" in msg and msg["telemetry"]:
                    st.markdown(msg["telemetry"], unsafe_allow_html=True)

        user_query = st.chat_input("Ask a question about the indexed documents...")

        if user_query:
            # Append user message
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            # Generate grounded response
            with st.chat_message("assistant"):
                with st.spinner("Retrieving relevant passages and synthesizing verified answer..."):
                    # Instantiate LLM provider
                    if "Gemini" in llm_choice:
                        qa_llm = GeminiProvider(api_key=api_key_input or None)
                    elif "OpenAI" in llm_choice:
                        qa_llm = OpenAIProvider(api_key=api_key_input or None)
                    else:
                        qa_llm = MockProvider()

                    pipeline = RAGQAPipeline(
                        vector_store=st.session_state.vector_store,
                        llm_provider=qa_llm,
                        top_k=top_k,
                        min_relevance_score=min_score
                    )

                    response = pipeline.answer_question(user_query)
                    st.markdown(response.answer)

                    # Telemetry footer
                    telemetry_html = f"""
                    <div style="margin-top: 8px;">
                        <span class="metric-badge">Retrieved: {response.chunks_retrieved_count} chunks</span>
                        <span class="metric-badge">Retrieval: {response.retrieval_latency}s</span>
                        <span class="metric-badge">Synthesis: {response.generation_latency}s</span>
                        <span class="metric-badge">Grounded: {'✅' if response.is_grounded else '⚠️'}</span>
                    </div>
                    """
                    st.markdown(telemetry_html, unsafe_allow_html=True)

                    # Store in chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response.answer,
                        "telemetry": telemetry_html,
                        "citations": [c.model_dump() for c in response.citations]
                    })

    with col_citations:
        st.subheader("Retrieved Evidence & Citations")
        
        # Show citations from latest assistant response
        latest_assistant_msg = None
        for m in reversed(st.session_state.chat_history):
            if m["role"] == "assistant" and "citations" in m:
                latest_assistant_msg = m
                break

        if latest_assistant_msg and latest_assistant_msg.get("citations"):
            for idx, cit in enumerate(latest_assistant_msg["citations"], start=1):
                st.markdown(f"""
                <div class="citation-card">
                    <span class="citation-badge">Excerpt #{idx} · {cit.get('filename')} (Page {cit.get('page_number')})</span><br>
                    <strong>Relevance Score:</strong> <code>{cit.get('relevance_score'):.4f}</code><br>
                    <div style="margin-top:6px; color:#334155; font-style:italic;">"{cit.get('excerpt')}"</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No citations for current query. When an answer is synthesized, source excerpts and page references will appear here.")
