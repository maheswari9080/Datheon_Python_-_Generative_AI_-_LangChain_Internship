# Task 3: Multi-Tool Autonomous AI Agent
*AI Research Workbench · Subsystem Documentation*

## Overview
The Multi-Tool Autonomous AI Agent is a console-based ReAct agent engineered to autonomously select, parameterize, and chain specialized tools to resolve complex, compound objectives.

The agent enforces rigorous safety constraints:
1. **Mathematical Safety**: An AST-based calculator that strictly parses mathematical nodes without invoking `eval()` or `exec()`.
2. **Directory Isolation**: A local file reader strictly bounded by path canonicalization within a designated `sandbox_data/` directory, preventing path traversal attacks.
3. **Web Search & Evidence Attribution**: DuckDuckGo web search tool extracting concise snippets with verified source URLs.
4. **Execution Governance**: Hard limits on maximum tool call iterations and overall execution timeout.
5. **Auditable Action Logs**: Structured logging of sanitized arguments, execution timing, and tool observations without leaking private scratchpad thoughts.

## Project Structure
```text
task3-research-agent/
├── main.py                 # Interactive and scripted CLI runner
├── agent.py                # ReAct orchestrator & state machine
├── tools/                  # Safety-constrained tool definitions
│   ├── base.py             # Tool base class & telemetry schemas
│   ├── calculator_tool.py  # Safe AST math parser (no eval)
│   ├── file_tool.py        # Sandboxed directory reader
│   └── search_tool.py      # DuckDuckGo search with URL citations
├── sandbox_data/           # Permitted directory for local files
│   ├── quarterly_earnings_q3.txt
│   └── cluster_telemetry.json
├── requirements.txt        # Subsystem dependencies
├── README.md               # Subsystem manual
└── tests/                  # Automated pytest suite
    ├── test_tools.py
    └── test_agent.py
```

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Interactive Console Mode
```bash
python main.py
```

### 3. Running Sample Compound Benchmark via CLI
```bash
python main.py --task "Read quarterly_earnings_q3.txt, calculate the percentage increase in revenue from Q2 to Q3, and search the web for Python 3.13 features." --provider mock
```

### 4. Running with Live LLM Providers
```bash
python main.py --task "Analyze sandbox data" --provider gemini
# OR
python main.py --task "Analyze sandbox data" --provider openai
```

## Running Automated Tests
```bash
pytest tests/ -v
```
