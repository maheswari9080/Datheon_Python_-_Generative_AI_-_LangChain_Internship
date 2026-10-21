"""
Task 1: Structured Information Extraction Studio
Interactive Streamlit application for parsing and validating Invoices and Resumes.
"""

import sys
import os
import json
from pathlib import Path

# Ensure task directory and root are in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import streamlit as st

try:
    from models import InvoiceExtraction, ResumeExtraction
    from extractor import StructuredExtractor
    from provider import get_provider, GeminiProvider, OpenAIProvider, MockProvider
except ImportError:
    from task1_structured_extractor.models import InvoiceExtraction, ResumeExtraction
    from task1_structured_extractor.extractor import StructuredExtractor
    from task1_structured_extractor.provider import get_provider, GeminiProvider, OpenAIProvider, MockProvider

# Page configuration
st.set_page_config(
    page_title="Task 1: Structured Extractor | AI Research Workbench",
    page_icon="📑",
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
    .status-card {
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 0.95rem;
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
</style>
""", unsafe_allow_html=True)


def load_sample_file(rel_path: str) -> str:
    full_path = CURRENT_DIR / "sample_data" / rel_path
    if full_path.exists():
        return full_path.read_text(encoding="utf-8")
    return ""


# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    provider_choice = st.selectbox(
        "LLM Provider",
        options=["Offline Mock Provider", "Google Gemini", "OpenAI"],
        index=0,
        help="Select live API integration or offline deterministic mock."
    )
    
    api_key = ""
    model_name = ""
    
    if provider_choice == "Google Gemini":
        api_key = st.text_input(
            "Gemini API Key",
            value=os.getenv("GEMINI_API_KEY", ""),
            type="password",
            help="Required if not set in .env"
        )
        model_name = st.selectbox(
            "Gemini Model",
            options=["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
            index=0
        )
    elif provider_choice == "OpenAI":
        api_key = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="Required if not set in .env"
        )
        model_name = st.selectbox(
            "OpenAI Model",
            options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0
        )
        
    max_retries = st.slider("Max Corrective Retries", min_value=1, max_value=5, value=3)
    
    st.divider()
    st.markdown("### 🔬 Schema Architecture")
    st.markdown("""
    - **Pydantic v2 Engine**
    - **Bounded Feedback Loop**
    - **ISO 8601 Date Standardization**
    - **Mathematical Consistency Audit**
    """)
    st.markdown("<div style='font-size:0.8rem; color:#64748b;'>AI Research Workbench · Task 1</div>", unsafe_allow_html=True)


# Main Content Header
st.markdown('<div class="main-title">Structured LLM Extraction & Validation Pipeline</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Extract typed, validated JSON from unstructured invoices and candidate resumes with automated corrective retries.</div>', unsafe_allow_html=True)

# Tabs for Mode Selection
tab_invoice, tab_resume = st.tabs(["🧾 Invoice Extractor", "👤 Resume Extractor"])


# -----------------------------------------------------------------------------
# TAB 1: INVOICE EXTRACTOR
# -----------------------------------------------------------------------------
with tab_invoice:
    col_input, col_output = st.columns([1, 1], gap="medium")

    with col_input:
        st.subheader("Source Document Input")
        
        sample_choice = st.selectbox(
            "Load Sample Invoice",
            options=["Select a sample...", "Sample 1: Cloud Consulting Invoice", "Sample 2: GPU Compute & Software"],
            key="inv_sample"
        )
        
        default_text = ""
        if sample_choice == "Sample 1: Cloud Consulting Invoice":
            default_text = load_sample_file("sample_invoice_1.txt")
        elif sample_choice == "Sample 2: GPU Compute & Software":
            default_text = load_sample_file("sample_invoice_2.txt")

        invoice_text = st.text_area(
            "Raw Invoice Text",
            value=default_text,
            height=320,
            placeholder="Paste raw invoice text or receipt transcript here...",
            key="inv_text"
        )

        btn_extract_inv = st.button("🚀 Extract & Validate Invoice", type="primary", use_container_width=True, key="btn_inv")

    with col_output:
        st.subheader("Validated Extraction Output")
        
        if btn_extract_inv:
            if not invoice_text.strip():
                st.warning("Please paste invoice text or select a sample document.")
            else:
                with st.spinner("Executing extraction and schema verification..."):
                    try:
                        # Instantiate provider
                        if provider_choice == "Google Gemini":
                            prov = GeminiProvider(api_key=api_key or None, model=model_name)
                        elif provider_choice == "OpenAI":
                            prov = OpenAIProvider(api_key=api_key or None, model=model_name)
                        else:
                            prov = MockProvider()

                        extractor = StructuredExtractor(provider=prov, max_retries=max_retries)
                        result = extractor.extract_invoice(invoice_text)

                        # Telemetry Badges
                        status_color = "status-success" if result.success else "status-error"
                        status_label = "✅ VALIDATED & CONFORMANT" if result.success else "❌ VALIDATION FAILED"
                        
                        st.markdown(f"""
                        <div class="status-card {status_color}">
                            <strong>Status:</strong> {status_label}<br>
                            <span class="metric-badge">Provider: {result.provider_used}</span>
                            <span class="metric-badge">Retries: {result.total_retries}</span>
                            <span class="metric-badge">Attempts: {len(result.attempts)}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        if result.success:
                            formatted_json = result.to_formatted_json()
                            st.json(result.data)

                            st.download_button(
                                label="📥 Download Validated JSON",
                                data=formatted_json,
                                file_name=f"invoice_{result.data.get('invoice_number', 'extracted')}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                        else:
                            st.error("Extraction failed after corrective retry limit.")
                            st.write("Validation Errors Encountered:")
                            for err in result.validation_errors:
                                st.markdown(f"- `{err}`")

                        # Diagnostics Accordion
                        with st.expander("🔍 Telemetry & Corrective Trace"):
                            for attempt in result.attempts:
                                st.markdown(f"**Attempt #{attempt.attempt_number}** (Latency: `{attempt.duration_seconds}s`, Valid: `{attempt.is_valid}`)")
                                if attempt.validation_errors:
                                    st.markdown("*Errors:*")
                                    for e in attempt.validation_errors:
                                        st.code(e, language="text")
                                st.text_area(f"Raw Output (Attempt {attempt.attempt_number})", value=attempt.raw_output, height=120)

                    except Exception as e:
                        st.error(f"Error initializing provider or pipeline: {str(e)}")


# -----------------------------------------------------------------------------
# TAB 2: RESUME EXTRACTOR
# -----------------------------------------------------------------------------
with tab_resume:
    col_r_input, col_r_output = st.columns([1, 1], gap="medium")

    with col_r_input:
        st.subheader("Candidate Resume Input")
        
        sample_r_choice = st.selectbox(
            "Load Sample Resume",
            options=["Select a sample...", "Sample 1: Elena Rostova (Staff AI Architect)", "Sample 2: Marcus Vance (Full Stack Cloud)"],
            key="res_sample"
        )
        
        default_r_text = ""
        if sample_r_choice == "Sample 1: Elena Rostova (Staff AI Architect)":
            default_r_text = load_sample_file("sample_resume_1.txt")
        elif sample_r_choice == "Sample 2: Marcus Vance (Full Stack Cloud)":
            default_r_text = load_sample_file("sample_resume_2.txt")

        resume_text = st.text_area(
            "Raw Resume Text",
            value=default_r_text,
            height=320,
            placeholder="Paste raw resume or curriculum vitae text here...",
            key="res_text"
        )

        btn_extract_res = st.button("🚀 Extract & Validate Resume", type="primary", use_container_width=True, key="btn_res")

    with col_r_output:
        st.subheader("Structured Profile Output")
        
        if btn_extract_res:
            if not resume_text.strip():
                st.warning("Please paste resume text or select a sample profile.")
            else:
                with st.spinner("Extracting profile attributes and skills..."):
                    try:
                        if provider_choice == "Google Gemini":
                            prov = GeminiProvider(api_key=api_key or None, model=model_name)
                        elif provider_choice == "OpenAI":
                            prov = OpenAIProvider(api_key=api_key or None, model=model_name)
                        else:
                            prov = MockProvider()

                        extractor = StructuredExtractor(provider=prov, max_retries=max_retries)
                        result = extractor.extract_resume(resume_text)

                        status_color = "status-success" if result.success else "status-error"
                        status_label = "✅ VALIDATED & CONFORMANT" if result.success else "❌ VALIDATION FAILED"
                        
                        st.markdown(f"""
                        <div class="status-card {status_color}">
                            <strong>Status:</strong> {status_label}<br>
                            <span class="metric-badge">Provider: {result.provider_used}</span>
                            <span class="metric-badge">Retries: {result.total_retries}</span>
                            <span class="metric-badge">Attempts: {len(result.attempts)}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        if result.success:
                            formatted_json = result.to_formatted_json()
                            st.json(result.data)

                            full_name = result.data.get("full_name", "candidate").replace(" ", "_").lower()
                            st.download_button(
                                label="📥 Download Profile JSON",
                                data=formatted_json,
                                file_name=f"resume_{full_name}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                        else:
                            st.error("Extraction failed after corrective retry limit.")
                            st.write("Validation Errors Encountered:")
                            for err in result.validation_errors:
                                st.markdown(f"- `{err}`")

                        with st.expander("🔍 Telemetry & Corrective Trace"):
                            for attempt in result.attempts:
                                st.markdown(f"**Attempt #{attempt.attempt_number}** (Latency: `{attempt.duration_seconds}s`, Valid: `{attempt.is_valid}`)")
                                if attempt.validation_errors:
                                    st.markdown("*Errors:*")
                                    for e in attempt.validation_errors:
                                        st.code(e, language="text")
                                st.text_area(f"Raw Output (Attempt {attempt.attempt_number})", value=attempt.raw_output, height=120)

                    except Exception as e:
                        st.error(f"Error initializing provider or pipeline: {str(e)}")
