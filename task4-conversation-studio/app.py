"""
Task 4: Interactive Full-Stack AI Chatbot with Streamlit.
Unified conversational studio supporting streaming tokens, session isolation,
system prompt configuration, export tools, and bridges to Task 2 RAG & Task 3 Autonomous Agent.
"""

import sys
import os
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
TASK1_DIR = ROOT_DIR / "task1-structured-extractor"
TASK2_DIR = ROOT_DIR / "task2-rag-research"
TASK3_DIR = ROOT_DIR / "task3-research-agent"

for p in (CURRENT_DIR, ROOT_DIR, TASK1_DIR, TASK2_DIR, TASK3_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import streamlit as st

try:
    from conversation import ConversationManager, ChatMessage
    from integrations import ChatBridge, stream_text_chunks
    from provider import get_provider, GeminiProvider, OpenAIProvider, MockProvider
    from vector_store import create_vector_store
    from document_loader import load_txt
    from chunking import DocumentChunker
except ImportError:
    from task4_conversation_studio.conversation import ConversationManager, ChatMessage
    from task4_conversation_studio.integrations import ChatBridge, stream_text_chunks
    from provider import get_provider, GeminiProvider, OpenAIProvider, MockProvider
    from vector_store import create_vector_store
    from document_loader import load_txt
    from chunking import DocumentChunker

# Page configuration
st.set_page_config(
    page_title="Task 4: Conversation Studio | AI Research Workbench",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
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
    .mode-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-family: monospace;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .badge-general { background-color: #e0f2fe; color: #0369a1; }
    .badge-rag { background-color: #ccfbf1; color: #0f766e; }
    .badge-agent { background-color: #fef3c7; color: #92400e; }
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
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "conv_manager" not in st.session_state:
    st.session_state.conv_manager = ConversationManager()
if "rag_store" not in st.session_state:
    st.session_state.rag_store = create_vector_store(use_chroma=True)
    # Pre-index sample whitepapers for instant RAG experience
    sample_doc = TASK2_DIR / "sample_documents" / "distributed_systems_architecture.txt"
    if sample_doc.exists():
        try:
            docs = load_txt(sample_doc, filename="distributed_systems.txt")
            chunker = DocumentChunker(chunk_size=400, chunk_overlap=50)
            chunks = chunker.chunk_documents(docs)
            st.session_state.rag_store.add_chunks(chunks)
        except Exception:
            pass


# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Studio Configuration")

    mode = st.radio(
        "Conversation Mode",
        options=["💬 General Assistant", "📚 Grounded RAG Assistant", "🤖 Multi-Tool Autonomous Agent"],
        index=0,
        help="Switch between conversational LLM, document RAG retrieval, and autonomous multi-tool execution."
    )

    provider_choice = st.selectbox(
        "Provider Engine",
        options=["Offline Mock / Deterministic Provider", "Google Gemini", "OpenAI"],
        index=0
    )

    api_key_val = ""
    model_name = ""
    if provider_choice == "Google Gemini":
        api_key_val = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
        model_name = st.selectbox("Model", ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"], index=0)
    elif provider_choice == "OpenAI":
        api_key_val = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
        model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
    enable_streaming = st.checkbox("Enable Output Streaming", value=True)

    with st.expander("🛠️ System Instructions & Persona"):
        system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.conv_manager.system_instruction,
            height=120
        )
        if system_prompt != st.session_state.conv_manager.system_instruction:
            st.session_state.conv_manager.system_instruction = system_prompt

    st.divider()
    st.markdown("### 📊 Session Telemetry")
    msg_count = len(st.session_state.conv_manager.messages)
    token_est = st.session_state.conv_manager.estimate_tokens()
    st.metric("Total Messages", msg_count)
    st.metric("Estimated Tokens", f"~{token_est}")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🗑️ Reset Chat", use_container_width=True):
            st.session_state.conv_manager.clear()
            st.success("Session reset.")
            st.rerun()

    with col_btn2:
        json_export = st.session_state.conv_manager.export_to_json()
        st.download_button(
            "📥 Export JSON",
            data=json_export,
            file_name="conversation_transcript.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<div style='font-size:0.8rem; color:#64748b; margin-top:15px;'>AI Research Workbench · Task 4</div>", unsafe_allow_html=True)


# Main Interface Header
st.markdown('<div class="main-title">Interactive Conversational AI Studio</div>', unsafe_allow_html=True)

# Badge for current mode
if "General" in mode:
    st.markdown('<span class="mode-badge badge-general">MODE: GENERAL CONVERSATION</span>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Multi-turn general reasoning studio with streaming token generation and session state isolation.</div>', unsafe_allow_html=True)
elif "RAG" in mode:
    st.markdown('<span class="mode-badge badge-rag">MODE: GROUNDED RAG ASSISTANT</span>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Answering questions grounded in indexed technical documentation with strict citation attribution.</div>', unsafe_allow_html=True)
else:
    st.markdown('<span class="mode-badge badge-agent">MODE: AUTONOMOUS MULTI-TOOL AGENT</span>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">ReAct autonomous agent executing sequential file reading, AST math calculation, and DuckDuckGo search.</div>', unsafe_allow_html=True)


# Render Existing Conversation Messages
for msg in st.session_state.conv_manager.messages:
    with st.chat_message(msg.role):
        st.markdown(msg.content)
        meta = msg.metadata
        if meta and meta.get("citations"):
            with st.expander("📄 Source Citations"):
                for cit in meta["citations"]:
                    st.markdown(f"- **{cit.get('filename')}** (Page {cit.get('page_number')}): *\"{cit.get('excerpt')}\"*")
        if meta and meta.get("audit_log"):
            with st.expander("🔍 Agent Execution Audit Log"):
                st.code(meta["audit_log"], language="text")


# Handle User Input
user_input = st.chat_input("Enter your message, research query, or compound task...")

if user_input:
    # Append user message
    st.session_state.conv_manager.add_message(role="user", content=user_input)
    with st.chat_message("user"):
        st.markdown(user_input)

    # Instantiate Provider & Bridge
    if provider_choice == "Google Gemini":
        prov = GeminiProvider(api_key=api_key_val or None, model=model_name or "gemini-2.5-flash")
    elif provider_choice == "OpenAI":
        prov = OpenAIProvider(api_key=api_key_val or None, model=model_name or "gpt-4o-mini")
    else:
        prov = MockProvider()

    bridge = ChatBridge(
        provider=prov,
        rag_vector_store=st.session_state.rag_store,
        agent_sandbox_dir=str(TASK3_DIR / "sandbox_data")
    )

    # Process and Stream Response
    with st.chat_message("assistant"):
        citations_to_store = []
        audit_log_to_store = ""

        if "RAG" in mode:
            with st.spinner("Retrieving grounded documents and verifying citations..."):
                answer_text, citations_to_store = bridge.process_rag_query(user_input)

            if enable_streaming:
                st.write_stream(stream_text_chunks(answer_text))
            else:
                st.markdown(answer_text)

            if citations_to_store:
                with st.expander("📄 Source Citations"):
                    for cit in citations_to_store:
                        st.markdown(f"- **{cit.get('filename')}** (Page {cit.get('page_number')}): *\"{cit.get('excerpt')}\"*")

        elif "Agent" in mode:
            with st.spinner("Agent selecting and executing tools sequentially..."):
                answer_text, audit_log_to_store, steps_data = bridge.process_agent_task(user_input)

            if enable_streaming:
                st.write_stream(stream_text_chunks(answer_text))
            else:
                st.markdown(answer_text)

            with st.expander("🔍 Agent Execution Audit Log"):
                st.code(audit_log_to_store, language="text")

        else:
            # General Chat Mode
            messages_llm = st.session_state.conv_manager.get_messages_for_llm()
            with st.spinner("Generating response..."):
                answer_text = bridge.process_general_chat(messages_llm, temperature=temperature)

            if enable_streaming:
                st.write_stream(stream_text_chunks(answer_text))
            else:
                st.markdown(answer_text)

        # Record in Conversation Manager
        msg_metadata = {}
        if citations_to_store:
            msg_metadata["citations"] = citations_to_store
        if audit_log_to_store:
            msg_metadata["audit_log"] = audit_log_to_store

        st.session_state.conv_manager.add_message(
            role="assistant",
            content=answer_text,
            metadata=msg_metadata
        )
