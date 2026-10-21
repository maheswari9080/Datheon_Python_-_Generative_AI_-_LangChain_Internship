# AI Research Workbench: Installation & Execution Guide

## 1. System Requirements & Prerequisites
- **Python**: Version 3.11 or 3.12+ (tested and verified on Python 3.12.10)
- **Operating Systems**: Windows 10/11, macOS (Apple Silicon & Intel), Ubuntu/Debian Linux
- **Package Manager**: `pip` (or `uv`)
- **Web Browser**: Chrome, Edge, Firefox, or Safari for interactive Streamlit applications and portal.

---

## 2. Environment Configuration

### Step 1: Clone or Navigate to the Repository
```bash
git clone https://github.com/maheswari9080/Python-Generative-AI-LangChain-Internship.git
cd Python-Generative-AI-LangChain-Internship
```

### Step 2: Create and Activate Virtual Environment (Recommended)
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Core Dependencies
You can install dependencies across the suite using:
```bash
pip install -r task1-structured-extractor/requirements.txt
pip install -r task2-rag-research/requirements.txt
pip install -r task3-research-agent/requirements.txt
pip install -r task4-conversation-studio/requirements.txt
```

### Step 4: Configure Environment Variables
Copy the template `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Open `.env` and configure your API keys (optional — all modules include offline mock fallbacks for testing without keys):
```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_LLM_PROVIDER=mock
```

---

## 3. Running Applications

### Central Master Launcher (Recommended)
The root directory includes a master Python orchestrator:
```bash
# Run interactive launcher menu
python launch.py

# Launch all web applications simultaneously (Tasks 1, 2, and 4)
python launch.py --all

# Run full automated test suite
python launch.py --test
```

### Independent Subsystem Launch Commands

| Subsystem | Mode | Command | Port / Target |
| :--- | :--- | :--- | :--- |
| **Central Portal** | Static Web | Open `index.html` in browser or `python -m http.server 8000` | `http://localhost:8000` |
| **Task 1: Structured Extractor** | Streamlit UI | `streamlit run task1-structured-extractor/app.py --server.port 8501` | `http://localhost:8501` |
| **Task 2: Grounded RAG** | Streamlit UI | `streamlit run task2-rag-research/app.py --server.port 8502` | `http://localhost:8502` |
| **Task 3: Autonomous Agent** | Console CLI | `python task3-research-agent/main.py` | Terminal Console |
| **Task 4: Conversation Studio**| Streamlit UI | `streamlit run task4-conversation-studio/app.py --server.port 8504` | `http://localhost:8504` |

---

## 4. Running the Automated Test Suite
To execute all 39 unit and integration tests across the 4 subsystems:
```bash
pytest task1-structured-extractor/tests/ task2-rag-research/tests/ task3-research-agent/tests/ task4-conversation-studio/tests/ -v
```
Expected output: `39 passed in ~6.0s`.
