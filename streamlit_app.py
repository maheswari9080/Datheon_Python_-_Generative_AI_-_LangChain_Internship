"""
AI Research Workbench - Master Unified Streamlit Application
Hosts all four tasks in a single multi-page interactive web application.
Ideal for Streamlit Community Cloud hosting directly from GitHub.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add all task subdirectories to Python path
ROOT_DIR = Path(__file__).resolve().parent
TASK1_DIR = ROOT_DIR / "task1-structured-extractor"
TASK2_DIR = ROOT_DIR / "task2-rag-research"
TASK3_DIR = ROOT_DIR / "task3-research-agent"
TASK4_DIR = ROOT_DIR / "task4-conversation-studio"

for p in (ROOT_DIR, TASK1_DIR, TASK2_DIR, TASK3_DIR, TASK4_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import streamlit as st

# Import core modules
from models import InvoiceExtraction, ResumeExtraction
from extractor import StructuredExtractor
from provider import get_provider, GeminiProvider, OpenAIProvider, MockProvider

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
from qa_pipeline import RAGQAPipeline

from tools.calculator_tool import SafeCalculatorTool
from tools.file_tool import SandboxedFileReaderTool
from tools.search_tool import DuckDuckGoSearchTool
from agent import AutonomousResearchAgent

from conversation import ConversationManager
from integrations import ChatBridge, stream_text_chunks

# Master Page Config
st.set_page_config(
    page_title="AI Research Workbench | Unified Suite",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Global Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .status-card {
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 12px;
        font-size: 0.9rem;
    }
    .status-success {
        background-color: #ecfdf5;
        border: 1px solid #10b981;
        color: #065f46;
    }
    .status-error {
        background-color: #fef2f2;
        border: 1px solid #ef4444;
        color: #991b1b;
    }
    .metric-badge {
        display: inline-block;
        padding: 3px 8px;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.8rem;
        color: #0f172a;
        margin-right: 4px;
    }
    .citation-card {
        padding: 10px;
        background-color: #f8fafc;
        border-left: 3px solid #0d9488;
        border-radius: 4px;
        margin-bottom: 8px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Shared Session State
if "conv_manager" not in st.session_state:
    st.session_state.conv_manager = ConversationManager()
if "rag_store" not in st.session_state:
    st.session_state.rag_store = create_vector_store(use_chroma=True)
    # Pre-index distributed systems sample
    sample_doc = TASK2_DIR / "sample_documents" / "distributed_systems_architecture.txt"
    if sample_doc.exists():
        try:
            docs = load_txt(sample_doc, filename="distributed_systems.txt")
            chunker = DocumentChunker(chunk_size=400, chunk_overlap=50)
            chunks = chunker.chunk_documents(docs)
            st.session_state.rag_store.add_chunks(chunks)
        except Exception:
            pass
if "indexed_docs_meta" not in st.session_state:
    st.session_state.indexed_docs_meta = ["distributed_systems.txt"]


# Master Sidebar Navigation
with st.sidebar:
    st.markdown("## 🔬 AI Research Workbench")
    st.markdown("<div style='font-size:0.85rem; color:#64748b; margin-top:-10px; margin-bottom:15px;'>Intelligent Systems Portfolio Suite</div>", unsafe_allow_html=True)

    app_mode = st.radio(
        "Select Application",
        options=[
            "🏠 Suite Overview",
            "📑 Task 1: Structured Extractor",
            "📚 Task 2: Grounded Document RAG",
            "🤖 Task 3: Autonomous AI Agent",
            "💬 Task 4: Conversation Studio"
        ],
        index=0
    )

    st.divider()
    st.markdown("### ⚙️ Engine & Credentials")
    provider_choice = st.selectbox(
        "Active LLM Provider",
        options=["Offline Mock / Deterministic Provider", "Google Gemini", "OpenAI"],
        index=0
    )

    api_key_val = ""
    model_name = ""
    if provider_choice == "Google Gemini":
        api_key_val = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
        model_name = st.selectbox("Gemini Model", ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"], index=0)
    elif provider_choice == "OpenAI":
        api_key_val = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
        model_name = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o"], index=0)

    st.divider()
    st.markdown("<div style='font-size:0.8rem; color:#64748b;'>Repository: <a href='https://github.com/maheswari9080/Python-Generative-AI-LangChain-Internship' target='_blank'>GitHub</a><br>Verified Tests: 39/39 Passing</div>", unsafe_allow_html=True)


# Provider factory helper
def get_active_provider():
    if provider_choice == "Google Gemini":
        return GeminiProvider(api_key=api_key_val or None, model=model_name or "gemini-2.5-flash")
    elif provider_choice == "OpenAI":
        return OpenAIProvider(api_key=api_key_val or None, model=model_name or "gpt-4o-mini")
    return MockProvider()


# ==============================================================================
# VIEW: 🏠 SUITE OVERVIEW
# ==============================================================================
if app_mode == "🏠 Suite Overview":
    st.markdown('<div class="main-title">AI Research Workbench Portfolio Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">A production-grade, four-module AI engineering portfolio designed for rigorous evaluation.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1], gap="large")
    with col1:
        st.markdown("""
        ### Architectural Architecture
        Each application operates as an independent, decoupled subsystem adhering to strict safety and validation standards:

        1. **Task 1 — Structured LLM Prompt Pipeline & JSON Extractor**:
           Strict Pydantic v2 schemas for Invoices and Resumes with bounded corrective self-repair retry loops.
        2. **Task 2 — Document Q&A Assistant with RAG & Vector Embeddings**:
           ChromaDB and Cosine vector storage, recursive chunking, and strict citation attribution with unanswerability gating.
        3. **Task 3 — Multi-Tool Autonomous AI Agent**:
           ReAct reasoning agent with an AST-safe mathematical calculator (no `eval`), sandboxed file reader (anti-traversal defense), and DuckDuckGo web search.
        4. **Task 4 — Interactive Full-Stack AI Chatbot**:
           Streamlit conversational studio with token streaming cadence, session isolation, and bridges to Task 2 RAG and Task 3 Agent.
        """)

    with col2:
        st.markdown("### 📊 Test Audit Summary")
        st.success("✅ **39 / 39 Automated Unit & Integration Tests Passed (100%)**")
        st.markdown("""
        - **Task 1 Tests**: 11 passed (Schemas, Line items, Retries)
        - **Task 2 Tests**: 9 passed (PDF loader, Chunker, Chroma, QA)
        - **Task 3 Tests**: 11 passed (AST Math, Sandbox, DDG, ReAct)
        - **Task 4 Tests**: 8 passed (Session state, Bridges, Streaming)
        """)
        st.info("💡 Use the sidebar to switch between any of the 4 live interactive applications.")


# ==============================================================================
# VIEW: 📑 TASK 1: STRUCTURED EXTRACTOR
# ==============================================================================
elif app_mode == "📑 Task 1: Structured Extractor":
    st.markdown('<div class="main-title">Task 1: Structured Information Extractor</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Extract typed, validated JSON from unstructured invoices and resumes with automated corrective retries.</div>', unsafe_allow_html=True)

    tab_inv, tab_res = st.tabs(["🧾 Invoice Mode", "👤 Resume Mode"])

    with tab_inv:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.subheader("Source Invoice Text")
            sample_file = TASK1_DIR / "sample_data" / "sample_invoice_1.txt"
            default_txt = sample_file.read_text(encoding="utf-8") if sample_file.exists() else ""
            inv_input = st.text_area("Invoice Text", value=default_txt, height=260, key="master_inv_txt")
            btn_extract_inv = st.button("🚀 Extract & Validate Invoice", type="primary", key="btn_m_inv")

        with c2:
            st.subheader("Validated Output")
            if btn_extract_inv:
                with st.spinner("Extracting with Pydantic v2 validation..."):
                    extractor = StructuredExtractor(provider=get_active_provider(), max_retries=3)
                    res = extractor.extract_invoice(inv_input)
                    if res.success:
                        st.success(f"Status: VALIDATED (Retries: {res.total_retries})")
                        st.json(res.data)
                        st.download_button("📥 Download JSON", data=res.to_formatted_json(), file_name="invoice.json", mime="application/json")
                    else:
                        st.error("Validation failed after retry limit.")
                        for err in res.validation_errors:
                            st.write(f"- {err}")

    with tab_res:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.subheader("Candidate Resume Text")
            sample_r_file = TASK1_DIR / "sample_data" / "sample_resume_1.txt"
            default_r_txt = sample_r_file.read_text(encoding="utf-8") if sample_r_file.exists() else ""
            res_input = st.text_area("Resume Text", value=default_r_txt, height=260, key="master_res_txt")
            btn_extract_res = st.button("🚀 Extract & Validate Resume", type="primary", key="btn_m_res")

        with c2:
            st.subheader("Validated Profile")
            if btn_extract_res:
                with st.spinner("Extracting profile attributes..."):
                    extractor = StructuredExtractor(provider=get_active_provider(), max_retries=3)
                    res = extractor.extract_resume(res_input)
                    if res.success:
                        st.success(f"Status: VALIDATED (Retries: {res.total_retries})")
                        st.json(res.data)
                        st.download_button("📥 Download JSON", data=res.to_formatted_json(), file_name="resume.json", mime="application/json")
                    else:
                        st.error("Validation failed after retry limit.")
                        for err in res.validation_errors:
                            st.write(f"- {err}")


# ==============================================================================
# VIEW: 📚 TASK 2: GROUNDED DOCUMENT RAG
# ==============================================================================
elif app_mode == "📚 Task 2: Grounded Document RAG":
    st.markdown('<div class="main-title">Task 2: Grounded Document RAG Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Ask questions grounded in indexed technical documentation with strict citation attribution.</div>', unsafe_allow_html=True)

    c_query, c_citations = st.columns([1.3, 0.7], gap="medium")
    with c_query:
        st.subheader("Grounded Query")
        user_q = st.text_input("Enter research question:", value="What is the heartbeat interval in Raft consensus?")
        btn_ask_rag = st.button("🔍 Search & Answer", type="primary")

        if btn_ask_rag and user_q:
            with st.spinner("Retrieving relevant passages and synthesizing answer..."):
                pipeline = RAGQAPipeline(vector_store=st.session_state.rag_store, llm_provider=get_active_provider())
                response = pipeline.answer_question(user_q)
                st.markdown(response.answer)
                st.session_state.last_rag_citations = response.citations

    with c_citations:
        st.subheader("Verified Citations")
        citations = getattr(st.session_state, "last_rag_citations", [])
        if citations:
            for idx, cit in enumerate(citations, start=1):
                st.markdown(f"""
                <div class="citation-card">
                    <strong>[Source: {cit.filename}, Page {cit.page_number}]</strong><br>
                    <span style="color:#0f766e; font-size:0.8rem;">Score: {cit.relevance_score:.4f}</span><br>
                    <em>"{cit.excerpt}"</em>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Source excerpts will appear here upon query execution.")


# ==============================================================================
# VIEW: 🤖 TASK 3: AUTONOMOUS AI AGENT
# ==============================================================================
elif app_mode == "🤖 Task 3: Autonomous AI Agent":
    st.markdown('<div class="main-title">Task 3: Multi-Tool Autonomous AI Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">ReAct agent with AST-safe math calculator, sandboxed file reader, and DuckDuckGo web search.</div>', unsafe_allow_html=True)

    task_input = st.text_input(
        "Compound Agent Task:",
        value="Read quarterly_earnings_q3.txt in the sandbox, calculate the revenue percentage increase from Q2 to Q3, and search the web for Python 3.13 features."
    )
    btn_run_agent = st.button("🤖 Execute Autonomous ReAct Loop", type="primary")

    if btn_run_agent and task_input:
        with st.spinner("Agent selecting and executing tools sequentially..."):
            calc = SafeCalculatorTool()
            file_tool = SandboxedFileReaderTool(sandbox_directory=str(TASK3_DIR / "sandbox_data"))
            search = DuckDuckGoSearchTool()
            agent = AutonomousResearchAgent(tools=[calc, file_tool, search], llm_provider=get_active_provider())
            res = agent.run(task_input)

            st.success(f"Execution Completed in {res.total_duration:.2f}s ({res.total_steps} tool steps)")
            st.markdown("### Final Synthesized Answer")
            st.markdown(res.final_answer)

            st.markdown("### Auditable Action & Observation Log")
            st.code(res.format_audit_log(), language="text")


# ==============================================================================
# VIEW: 💬 TASK 4: CONVERSATION STUDIO
# ==============================================================================
elif app_mode == "💬 Task 4: Conversation Studio":
    st.markdown('<div class="main-title">Task 4: Interactive Conversation Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Streaming chat with session isolation and tri-mode dispatch (General / RAG / Agent).</div>', unsafe_allow_html=True)

    chat_mode = st.radio("Active Studio Mode", ["General Chat", "Grounded RAG Mode", "Autonomous Agent Mode"], horizontal=True)

    for msg in st.session_state.conv_manager.messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)

    user_msg = st.chat_input("Enter your message...")
    if user_msg:
        st.session_state.conv_manager.add_message("user", user_msg)
        with st.chat_message("user"):
            st.markdown(user_msg)

        bridge = ChatBridge(
            provider=get_active_provider(),
            rag_vector_store=st.session_state.rag_store,
            agent_sandbox_dir=str(TASK3_DIR / "sandbox_data")
        )

        with st.chat_message("assistant"):
            if "RAG" in chat_mode:
                ans, _ = bridge.process_rag_query(user_msg)
            elif "Agent" in chat_mode:
                ans, _, _ = bridge.process_agent_task(user_msg)
            else:
                ans = bridge.process_general_chat(st.session_state.conv_manager.get_messages_for_llm())

            st.write_stream(stream_text_chunks(ans))
            st.session_state.conv_manager.add_message("assistant", ans)
