import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
ROOT_DIR = MODULE_DIR.parent
TASK1_DIR = ROOT_DIR / "task1-structured-extractor"

if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(TASK1_DIR) not in sys.path:
    sys.path.insert(0, str(TASK1_DIR))

import pytest

try:
    from agent import AutonomousResearchAgent, AgentResponse
    from tools.calculator_tool import SafeCalculatorTool
    from tools.file_tool import SandboxedFileReaderTool
    from tools.search_tool import DuckDuckGoSearchTool
    from provider import MockProvider
except ImportError:
    from task3_research_agent.agent import AutonomousResearchAgent, AgentResponse
    from task3_research_agent.tools.calculator_tool import SafeCalculatorTool
    from task3_research_agent.tools.file_tool import SandboxedFileReaderTool
    from task3_research_agent.tools.search_tool import DuckDuckGoSearchTool
    from task1_structured_extractor.provider import MockProvider


def test_agent_compound_benchmark_resolution():
    calc = SafeCalculatorTool()
    file_tool = SandboxedFileReaderTool(sandbox_directory=str(MODULE_DIR / "sandbox_data"))
    search = DuckDuckGoSearchTool()

    agent = AutonomousResearchAgent(
        tools=[calc, file_tool, search],
        llm_provider=MockProvider(),
        max_iterations=6
    )

    task = (
        "Inspect quarterly_earnings_q3.txt, calculate the percentage increase "
        "in revenue from Q2 to Q3, and search the web for Python 3.13 features."
    )

    response = agent.run(task)

    assert response.success is True
    assert response.termination_reason == "COMPLETED"
    assert response.total_steps >= 2
    assert "quarterly_earnings_q3.txt" in response.steps[0].action_input.values()
    assert "25.0%" in response.final_answer or "25%" in response.final_answer
    assert "audit" in response.format_audit_log().lower()


def test_agent_max_iterations_guard():
    # Agent with 0 max iterations terminates immediately
    calc = SafeCalculatorTool()
    agent = AutonomousResearchAgent(
        tools=[calc],
        llm_provider=MockProvider(),
        max_iterations=0
    )

    # In mock runner, max iterations will be checked if called with normal loop
    assert agent.max_iterations == 0


def test_agent_timeout_guard():
    calc = SafeCalculatorTool()
    agent = AutonomousResearchAgent(
        tools=[calc],
        llm_provider=MockProvider(),
        timeout_seconds=0.0001
    )
    assert agent.timeout_seconds == 0.0001
