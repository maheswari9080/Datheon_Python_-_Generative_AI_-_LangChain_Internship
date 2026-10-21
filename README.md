# AI Research Workbench: Intelligent Systems Suite

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.10-teal.svg)](https://docs.pydantic.dev/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange.svg)](https://www.trychroma.com/)
[![Tests Passed](https://img.shields.io/badge/Pytest-39%2F39_Passed-brightgreen.svg)](docs/validation-report.md)

A production-grade, enterprise-ready AI Portfolio Suite designed for rigorous technical evaluation. The suite encompasses four independent, decoupled Python AI applications unified through a central research-laboratory entry portal (`index.html`) and master launcher (`launch.py`).

---

## 🏛️ Subsystem Architecture Overview

| Subsystem | Core Stack | Primary Architecture Pattern | Default Port / Access |
| :--- | :--- | :--- | :--- |
| **Central Portal** | HTML5 / CSS3 / Vanilla JS | Research Workbench Laboratory Dashboard | `index.html` |
| **Task 1: Structured Extractor** | Pydantic v2, Gemini, OpenAI, Streamlit | Bounded Self-Corrective Feedback Repair Loops | `http://localhost:8501` |
| **Task 2: Grounded Document RAG** | ChromaDB, pypdf, LangChain, Cosine Sim | Dense Semantic Retrieval with Citation Attribution | `http://localhost:8502` |
| **Task 3: Autonomous AI Agent** | ReAct Loop, AST Math, Sandboxed FS, DDGS | Defense-in-Depth Tool Calling & Audit Telemetry | Terminal Console CLI |
| **Task 4: Conversation Studio** | Streamlit Chat, Session State, Bridges | Streaming Cadence with RAG & Agent Bridges | `http://localhost:8504` |

---

## 📂 Project Structure

```text
mw/
├── index.html                           # Unified Research Workbench Portal
├── README.md                            # Suite Overview Documentation
├── launch.py                            # Central Application Orchestrator CLI
├── .gitignore                           # Git Ignore rules
├── .env.example                         # Environment configuration template
├── task1-structured-extractor/          # Task 1: Information Extractor
│   ├── app.py                          # Streamlit UI
│   ├── models.py                       # Pydantic v2 schemas (Invoice & Resume)
│   ├── prompt_templates.py             # Parameterized prompts & repair templates
│   ├── provider.py                     # LLM Provider abstraction (Gemini, OpenAI, Mock)
│   ├── extractor.py                    # Multi-pass bounded repair engine
│   ├── sample_data/                    # Sample invoices and resumes
│   ├── requirements.txt
│   ├── README.md
│   └── tests/                          # 11 Unit tests (100% pass)
├── task2-rag-research/                  # Task 2: Grounded RAG Assistant
│   ├── app.py                          # Streamlit UI
│   ├── document_loader.py              # PDF/TXT loader with page metadata
│   ├── chunking.py                     # RecursiveCharacterTextSplitter engine
│   ├── vector_store.py                 # ChromaDB & InMemory Cosine Vector Stores
│   ├── qa_pipeline.py                  # Grounded synthesis with citation guards
│   ├── sample_documents/               # Technical whitepapers
│   ├── requirements.txt
│   ├── README.md
│   └── tests/                          # 9 Unit tests (100% pass)
├── task3-research-agent/                # Task 3: Autonomous AI Agent
│   ├── main.py                         # Console CLI entrypoint
│   ├── agent.py                        # ReAct multi-tool reasoning engine
│   ├── tools/                          # Safety-sandboxed tools
│   │   ├── base.py                     # Tool base class & telemetry schemas
│   │   ├── calculator_tool.py          # AST-safe mathematical evaluator (no eval)
│   │   ├── file_tool.py                # Sandboxed directory reader (anti-traversal)
│   │   └── search_tool.py              # DuckDuckGo search with source URLs
│   ├── sandbox_data/                   # Permitted directory for file reader
│   ├── requirements.txt
│   ├── README.md
│   └── tests/                          # 11 Unit tests (100% pass)
├── task4-conversation-studio/           # Task 4: Full-Stack AI Chatbot
│   ├── app.py                          # Streamlit Chat Studio
│   ├── conversation.py                 # Session history & token estimation
│   ├── integrations.py                 # Unified bridge to Task 2 RAG & Task 3 Agent
│   ├── requirements.txt
│   ├── README.md
│   └── tests/                          # 8 Unit tests (100% pass)
└── docs/                                # Technical Documentation
    ├── architecture.md                 # System architecture & Mermaid diagrams
    ├── installation.md                 # Setup & execution guide
    └── validation-report.md            # Detailed verification audit ledger
```

---

## 🚀 Quick Start Guide

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/maheswari9080/Python-Generative-AI-LangChain-Internship.git
cd Python-Generative-AI-LangChain-Internship

# Optional: configure .env from template (Mock providers operate offline without keys)
cp .env.example .env

# Install dependencies across all modules
pip install -r task1-structured-extractor/requirements.txt
pip install -r task2-rag-research/requirements.txt
pip install -r task3-research-agent/requirements.txt
pip install -r task4-conversation-studio/requirements.txt
```

### 2. Launching with Master CLI (`launch.py`)
```bash
# Launch interactive launcher menu
python launch.py

# Launch all web applications simultaneously (Tasks 1, 2, and 4)
python launch.py --all

# Run full automated verification test suite
python launch.py --test
```

### 3. Individual Subsystem Commands

```bash
# Task 1: Structured Extractor (Port 8501)
streamlit run task1-structured-extractor/app.py --server.port 8501

# Task 2: Grounded RAG Assistant (Port 8502)
streamlit run task2-rag-research/app.py --server.port 8502

# Task 3: Autonomous Research Agent (Console CLI)
python task3-research-agent/main.py --task sample

# Task 4: Conversation Studio (Port 8504)
streamlit run task4-conversation-studio/app.py --server.port 8504
```

---

## 🧪 Automated Verification Suite

All 39 unit and integration tests execute with a single command:
```bash
pytest task1-structured-extractor/tests/ task2-rag-research/tests/ task3-research-agent/tests/ task4-conversation-studio/tests/ -v
```

### Verification Highlights:
- **Task 1**: Pydantic v2 schemas, date normalization, mathematical consistency, bounded self-repair retry loops.
- **Task 2**: PDF multi-page extraction, empty file handling, vector indexing, citation attribution, unanswerability gating.
- **Task 3**: AST mathematical safety (code execution attempts blocked), path traversal sandbox prevention, DuckDuckGo citations, ReAct compound resolution.
- **Task 4**: Multi-turn session isolation, token estimation, export serialization, streaming cadence, RAG & Agent bridge hooks.

---

## 🎨 Visual Identity & Aesthetic
The portal and interfaces adhere to the **AI Research Workbench** aesthetic:
- **Clean Light Palette**: `#f8fafc` canvas, crisp `#ffffff` cards, `#0f172a` deep navy typography.
- **Restrained Accents**: Professional Teal (`#0d9488`) and Cobalt (`#2563eb`) with functional state colors.
- **Typography**: Modern system sans-serif hierarchy paired with monospace telemetry typography (`JetBrains Mono` / `SF Mono` / `Consolas`).
- **No Gimmicks**: Designed purely around information architecture, legible data tables, audit ledgers, and responsive controls.

---

## 📄 License & Attribution
Authored as part of the **AI Internship Project Suite**. Built with Google Antigravity.
All rights reserved.
