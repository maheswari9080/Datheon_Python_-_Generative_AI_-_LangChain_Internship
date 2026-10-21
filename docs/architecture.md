# AI Research Workbench: System Architecture & Data Flow

## 1. Architectural Philosophy & Design Principles
The **AI Research Workbench** is designed as a modular, decoupled suite of four independent Python AI subsystems.
Each subsystem is self-contained with its own models, pipelines, user interfaces, dependency manifests, and automated test fixtures.

### Core Architectural Tenets:
1. **Defensive Schema Boundaries**: Model completions are never trusted unconditionally; strict Pydantic v2 schemas govern all structured ingestion and extraction boundaries.
2. **Grounded Retrieval & Anti-Hallucination Guardrails**: Document Q&A enforces explicit threshold gating and citation provenance attribution. When evidence is insufficient, answers default to deterministic unanswerability statements rather than speculative generation.
3. **Defense-in-Depth Tool Sandboxing**: Agents interact with the local operating system and arithmetic capabilities only through sandboxed AST evaluators and path-canonicalized directory limits. Raw `eval()` or unconstrained shell calls are strictly banned.
4. **Resilient Offline Decoupling**: All modules feature deterministic offline mock engines and local vector embeddings, ensuring that evaluation, CI/CD pipelines, and local unit test suites run with 100% predictability even when network connectivity or remote API keys are absent.

---

## 2. Global Architecture Diagram

```mermaid
graph TD
    subgraph Central["Central Entry Portal"]
        Portal["index.html (Port 8000 / Static Browser)"]
        Launcher["launch.py (Orchestrator CLI)"]
    end

    subgraph Task1["Task 1: Structured Extractor (:8501)"]
        T1_Input["Raw Invoice / Resume Text"] --> T1_Prompt["Few-Shot Parameterized Prompts"]
        T1_Prompt --> T1_LLM["LLM Provider (Gemini / OpenAI / Mock)"]
        T1_LLM --> T1_Val["Pydantic v2 Validation"]
        T1_Val -- Fail --> T1_Repair["Bounded Corrective Retry Loop"]
        T1_Repair --> T1_LLM
        T1_Val -- Pass --> T1_JSON["Validated JSON + Download"]
    end

    subgraph Task2["Task 2: Grounded RAG (:8502)"]
        T2_Docs["PDF / TXT Ingestion"] --> T2_Chunk["RecursiveCharacterTextSplitter"]
        T2_Chunk --> T2_Vector["ChromaDB / InMemory Cosine Store"]
        T2_Query["User Research Question"] --> T2_Retriever["Relevance Score Gating"]
        T2_Vector --> T2_Retriever
        T2_Retriever -- Below Threshold --> T2_Reject["Insufficient Evidence Notice"]
        T2_Retriever -- Valid Chunks --> T2_Gen["Grounded Answer Synthesis"]
        T2_Gen --> T2_Cit["Source Excerpts & Citations"]
    end

    subgraph Task3["Task 3: Autonomous Agent (Console CLI)"]
        T3_Task["Compound Research Task"] --> T3_ReAct["ReAct Reasoning Loop"]
        T3_ReAct --> T3_Calc["AST-Safe Calculator"]
        T3_ReAct --> T3_File["Sandboxed File Reader"]
        T3_ReAct --> T3_Search["DuckDuckGo Web Search"]
        T3_Calc --> T3_Obs["Tool Observation"]
        T3_File --> T3_Obs
        T3_Search --> T3_Obs
        T3_Obs --> T3_ReAct
        T3_ReAct --> T3_Audit["Auditable Action Log & Telemetry"]
    end

    subgraph Task4["Task 4: Conversation Studio (:8504)"]
        T4_Chat["Streamlit Chat Studio"] --> T4_Session["Session State & Token Budget"]
        T4_Session --> T4_Stream["Cadence / Provider Token Streaming"]
        T4_Session --> T4_Bridge["Integration Bridge"]
        T4_Bridge --> Task2
        T4_Bridge --> Task3
    end

    Central --> Task1
    Central --> Task2
    Central --> Task3
    Central --> Task4
```

---

## 3. Subsystem Breakdown & Implementation Decisions

### Task 1: Structured Extractor
- **Pydantic v2 Models**: `InvoiceExtraction` and `ResumeExtraction` enforce ISO 8601 date parsing (`YYYY-MM-DD`), non-negative currency amounts, and line-item summation validation (`quantity * unit_price = total_price`).
- **Self-Repair Feedback Loop**: Intercepts `ValidationError`, extracts field location and error string, and constructs a corrective repair prompt providing the LLM with previous faulty output, validation messages, and original document text. Configurable up to 5 bounded retries.

### Task 2: Grounded Document RAG
- **Provenance Preservation**: `document_loader.py` captures `source`, `filename`, `page_number`, `char_count`.
- **Hybrid Embeddings**: Supports local deterministic 256-d hashing embeddings (zero external API calls), Gemini `text-embedding-004`, and OpenAI `text-embedding-3-small`.
- **Threshold Gating**: Any candidate chunk scoring below `min_relevance_score` is discarded before prompt synthesis, preventing hallucinations on out-of-scope inquiries.

### Task 3: Autonomous AI Agent
- **AST Mathematical Evaluation**: Recursively walks parsed Abstract Syntax Tree nodes (`ast.parse`), permitting only mathematical operators and standard functions (`sqrt`, `log`, `sin`, `round`). Rejects variable access, imports, and system calls.
- **Directory Traversal Defense**: Canonicalizes relative file paths against an absolute `sandbox_data/` boundary using `Path.resolve()` and `relative_to()` validation.
- **Auditable Observability**: Separates public action-observation logs from internal reasoning tokens, producing clean verification tables suitable for enterprise auditing.

### Task 4: Conversation Studio
- **Full-Stack Chat Primitives**: Implements Streamlit `st.chat_message`, `st.chat_input`, and `st.session_state`.
- **Tri-Mode Dispatcher**: Seamlessly connects user messages to general conversation, Task 2 RAG vector collections, or Task 3 multi-tool autonomous execution.
- **Session Privacy**: API keys remain in transient browser session state and are never written to disk or logs.
