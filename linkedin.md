# 🚀 LinkedIn Project Launch: AI Research Workbench

> **Post Asset Attached:** [`assets/linkedin_banner.png`](assets/linkedin_banner.png) *(or vector format: [`assets/linkedin_banner.svg`](assets/linkedin_banner.svg))*

---

### 📝 Copy-Paste Ready LinkedIn Post Content

```text
🚀 Excited to unveil the AI Research Workbench — a production-grade, four-application AI portfolio suite engineered with Python 3.12, LangChain, Pydantic v2, ChromaDB, and Streamlit!

Rather than building isolated toy demos, I focused on solving real-world production challenges in Generative AI: schema drift, model hallucinations, arbitrary code execution risks, and stateful session management.

Here is a look under the hood at the 4 decoupled applications:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📑 TASK 1: Structured LLM Prompt Pipeline & JSON Extractor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ingests unstructured financial invoices and candidate resumes.
• Enforces strict Pydantic v2 schemas: ISO 8601 date parsing, non-negative amounts, and mathematical line-item audits (quantity × unit price = total).
• Engineered a Bounded Corrective Self-Repair Loop: when an LLM produces schema violations, the engine intercepts validation errors, isolates the faulted fields, and prompts the model to repair only the erroneous keys.
• Includes formatted JSON inspection, download tools, and 11 automated verification tests.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 TASK 2: Document Q&A Assistant with Grounded RAG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ingestion pipeline for multi-page PDFs (via pypdf) and text whitepapers, retaining page-level metadata.
• Chunking with RecursiveCharacterTextSplitter and token overlap.
• Dual Vector Storage: native ChromaDB integration paired with a high-performance in-memory Cosine store powered by 256-d deterministic semantic hashing embeddings for offline reliability.
• Strict Anti-Hallucination Guardrails: Relevance score gating filters ungrounded context. If documents lack sufficient evidence, it returns a verified unanswerable response rather than hallucinating.
• Mandatory inline citation attribution: [Source: filename.pdf, Page N].

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 TASK 3: Multi-Tool Autonomous AI Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Console-based ReAct autonomous reasoning agent capable of chaining tools sequentially to solve compound tasks.
• Defense-in-Depth Safety Architecture:
  1. Restricted AST Math Calculator: Directly traverses Abstract Syntax Tree nodes; completely eliminates eval() / exec() to prevent arbitrary code execution.
  2. Sandboxed File Reader: Path canonicalization strictly confines reads to the sandbox_data/ directory, blocking ../ directory traversal attacks.
  3. DuckDuckGo Web Search: Queries live web snippets with verified URL citations and offline fallback resilience.
• Structured audit telemetry logging each tool call, sanitized arguments, duration, and observation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 TASK 4: Full-Stack Conversational AI Studio
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Polished Streamlit conversational interface utilizing st.chat_message, st.chat_input, and st.session_state.
• Natural streaming token cadence delivery.
• Tri-Mode Operational Bridge: Seamlessly switches between General Chat, Grounded RAG Knowledge Base, and Autonomous Multi-Tool Agent execution within a single UI.
• Session isolation ensuring API credentials are never logged or persisted to disk, with one-click transcript export to JSON and Markdown.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 ENGINEERING METRICS & TESTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 39 / 39 Unit & Integration Tests Passing (100% test suite via pytest)
✅ Pure Python 3.12 architecture with type hinting
✅ Zero-Dependency Offline Mocks: Every module runs without remote API dependencies or keys
✅ Hosted on GitHub with automated GitHub Actions CI/CD workflows and GitHub Pages

🔗 GitHub Repository: https://github.com/maheswari9080/Python-Generative-AI-LangChain-Internship
🌐 Live Research Portal: https://maheswari9080.github.io/Python-Generative-AI-LangChain-Internship/

I’d love to hear your thoughts, feedback, and architecture suggestions in the comments below! 👇

#ArtificialIntelligence #GenerativeAI #Python #LangChain #MachineLearning #RAG #AIAgents #Streamlit #Pydantic #VectorDatabase #SoftwareEngineering #DataScience #LLM #OpenSource
```

---

### 🎨 Visual Preview of the Included LinkedIn Banner

<p align="center">
  <img src="image.png" alt="AI Research Workbench LinkedIn Banner" width="100%" style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06);" />
</p>

*Direct Links to Post Graphics:*
- **Standard Post Raster Image**: [`image.png`](image.png) or [`assets/linkedin_banner.png`](assets/linkedin_banner.png) (1200 x 628 px)
- **High-Definition Vector Format**: [`image.svg`](image.svg) or [`assets/linkedin_banner.svg`](assets/linkedin_banner.svg)
- **Hero Landscape Banner**: [`assets/hero_banner.svg`](assets/hero_banner.svg) / [`assets/hero_banner.png`](assets/hero_banner.png)
- **Architecture Flow Infographic**: [`assets/modules_architecture.svg`](assets/modules_architecture.svg)

