# Task 4: Interactive Full-Stack AI Chatbot with Streamlit
*AI Research Workbench · Subsystem Documentation*

## Overview
The Interactive Full-Stack Conversation Studio is a production-grade conversational application featuring streaming token generation, session state management, configurable system instructions, and unified bridges into the Task 2 Document RAG engine and Task 3 Multi-Tool Autonomous Agent.

The application allows users to seamlessly switch across three specialized execution modes within a single, cohesive research workbench.

## Key Features
- **Modern Chat Primitives**: Implemented with Streamlit's official `st.chat_message`, `st.chat_input`, and `st.session_state`.
- **Streaming Output**: Realistic streaming token delivery using natural cadence generator or live SDK streams.
- **Tri-Mode Operational Architecture**:
  1. **General Assistant Mode**: Conversational reasoning, code assistance, and multi-turn brainstorming.
  2. **Grounded RAG Mode**: Direct bridge to Task 2 Vector Store, retrieving grounded chunks with citations.
  3. **Autonomous Multi-Tool Agent Mode**: Delegates complex compound tasks to Task 3's ReAct agent, rendering the execution audit log directly into the chat timeline.
- **Session Isolation & Privacy**: API keys and conversational memory remain strictly isolated within the user's browser session; secrets are never logged or stored on disk.
- **Export Capabilities**: One-click download of conversational sessions to structured JSON and human-readable Markdown transcripts.

## Project Structure
```text
task4-conversation-studio/
├── app.py                  # Streamlit visual application
├── conversation.py         # Session history & state management
├── integrations.py         # RAG & Agent integration bridge
├── requirements.txt        # Subsystem dependencies
├── README.md               # Subsystem manual
└── tests/                  # Automated pytest suite
    ├── test_conversation.py
    └── test_integrations.py
```

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Running the Interactive Studio
```bash
streamlit run app.py --server.port 8504
```

### 3. Programmatic Usage
```python
from task4_conversation_studio.conversation import ConversationManager
from task4_conversation_studio.integrations import ChatBridge

conv = ConversationManager(system_instruction="You are an AI research consultant.")
conv.add_message("user", "Summarize key principles of high-availability consensus.")

bridge = ChatBridge()
answer = bridge.process_general_chat(conv.get_messages_for_llm())
conv.add_message("assistant", answer)

print(conv.export_to_markdown())
```

## Running Automated Tests
```bash
pytest tests/ -v
```
