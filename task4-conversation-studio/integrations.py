"""
Integration Bridge Connecting Conversation Studio to Task 2 RAG and Task 3 Autonomous Agent.
Allows seamless switching between General Conversational Mode, Grounded RAG, and Multi-Tool Agent.
"""

import sys
import time
from pathlib import Path
from typing import Generator, Dict, Any, Optional

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
TASK1_DIR = ROOT_DIR / "task1-structured-extractor"
TASK2_DIR = ROOT_DIR / "task2-rag-research"
TASK3_DIR = ROOT_DIR / "task3-research-agent"

for d in (CURRENT_DIR, TASK1_DIR, TASK2_DIR, TASK3_DIR):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

try:
    from provider import LLMProvider, get_provider
    from qa_pipeline import RAGQAPipeline
    from vector_store import create_vector_store, LocalDeterministicEmbedding
    from agent import AutonomousResearchAgent
    from tools.calculator_tool import SafeCalculatorTool
    from tools.file_tool import SandboxedFileReaderTool
    from tools.search_tool import DuckDuckGoSearchTool
except ImportError:
    pass


def stream_text_chunks(text: str, delay: float = 0.015) -> Generator[str, None, None]:
    """Generates streaming tokens/words with natural timing cadence for smooth UI rendering."""
    words = text.split(" ")
    for idx, word in enumerate(words):
        yield word + (" " if idx < len(words) - 1 else "")
        time.sleep(delay)


class ChatBridge:
    """Unified dispatch bridge connecting chat UI to General LLM, Task 2 RAG, and Task 3 Agent."""

    def __init__(
        self,
        provider: Optional[Any] = None,
        rag_vector_store: Optional[Any] = None,
        agent_sandbox_dir: Optional[str] = None
    ):
        self.provider = provider or get_provider()
        self.vector_store = rag_vector_store or create_vector_store(use_chroma=True)
        
        # Initialize Agent
        calc = SafeCalculatorTool()
        file_tool = SandboxedFileReaderTool(sandbox_directory=agent_sandbox_dir)
        search = DuckDuckGoSearchTool()
        self.agent = AutonomousResearchAgent(
            tools=[calc, file_tool, search],
            llm_provider=self.provider
        )

        # Initialize RAG
        self.rag_pipeline = RAGQAPipeline(
            vector_store=self.vector_store,
            llm_provider=self.provider
        )

    def process_general_chat(self, messages_for_llm: list[dict], temperature: float = 0.7) -> str:
        """Standard conversational turn."""
        if "mock" in self.provider.provider_name.lower():
            last_user_query = messages_for_llm[-1]["content"] if messages_for_llm else ""
            return (
                f"I have received your inquiry regarding '{last_user_query}'. "
                f"As an AI Research Workbench assistant, I can assist you with structured data extraction, "
                f"grounded document question-answering with verified citations, or autonomous multi-tool investigations."
            )
        return self.provider.generate(messages_for_llm, temperature=temperature)

    def process_rag_query(self, query: str) -> tuple[str, list[dict]]:
        """Document-grounded RAG retrieval query."""
        resp = self.rag_pipeline.answer_question(query)
        citations_data = [c.model_dump() for c in resp.citations]
        return resp.answer, citations_data

    def process_agent_task(self, task: str) -> tuple[str, str, list[dict]]:
        """Delegates compound task to Task 3 autonomous agent."""
        agent_resp = self.agent.run(task)
        audit_log = agent_resp.format_audit_log()
        steps_data = [s.model_dump() for s in agent_resp.steps]
        return agent_resp.final_answer, audit_log, steps_data
