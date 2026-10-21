"""
Console-Based Entrypoint for Task 3: Multi-Tool Autonomous AI Agent.
Provides interactive CLI mode, argument parsing, colorized execution audit tables, and telemetry summaries.
"""

import sys
import os
import argparse
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
TASK1_DIR = ROOT_DIR / "task1-structured-extractor"

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(TASK1_DIR) not in sys.path:
    sys.path.insert(0, str(TASK1_DIR))

try:
    from tools.calculator_tool import SafeCalculatorTool
    from tools.file_tool import SandboxedFileReaderTool
    from tools.search_tool import DuckDuckGoSearchTool
    from agent import AutonomousResearchAgent
    from provider import get_provider, GeminiProvider, OpenAIProvider, MockProvider
except ImportError:
    from task3_research_agent.tools.calculator_tool import SafeCalculatorTool
    from task3_research_agent.tools.file_tool import SandboxedFileReaderTool
    from task3_research_agent.tools.search_tool import DuckDuckGoSearchTool
    from task3_research_agent.agent import AutonomousResearchAgent
    from provider import get_provider, GeminiProvider, OpenAIProvider, MockProvider


def print_banner():
    banner = """
======================================================================
  AI RESEARCH WORKBENCH - TASK 3: AUTONOMOUS RESEARCH AGENT
  Multi-Tool ReAct Engine · Strict AST Calculator · Sandboxed File Reader
======================================================================
    """
    print(banner)


def run_cli():
    parser = argparse.ArgumentParser(description="Multi-Tool Autonomous Research Agent CLI")
    parser.add_argument("--task", type=str, default="", help="Compound task or research query to resolve")
    parser.add_argument("--provider", type=str, choices=["mock", "gemini", "openai"], default="mock", help="LLM Provider")
    parser.add_argument("--max-iterations", type=int, default=6, help="Maximum permitted tool calls")
    parser.add_argument("--timeout", type=float, default=30.0, help="Maximum execution timeout in seconds")
    parser.add_argument("--sandbox", type=str, default=str(CURRENT_DIR / "sandbox_data"), help="Path to sandbox directory")

    args = parser.parse_args()
    print_banner()

    # 1. Initialize Tools with Safe Configuration
    calc_tool = SafeCalculatorTool()
    file_tool = SandboxedFileReaderTool(sandbox_directory=args.sandbox)
    search_tool = DuckDuckGoSearchTool(timeout_seconds=8)
    tools = [calc_tool, file_tool, search_tool]

    print(f"[*] Initialized 3 active safety-constrained tools:")
    for t in tools:
        print(f"    - {t.name}: {t.description[:60]}...")
    print(f"[*] Sandbox directory: {file_tool.sandbox_path}")
    print(f"[*] Provider: {args.provider.upper()} | Max Iterations: {args.max_iterations} | Timeout: {args.timeout}s\n")

    # 2. Select LLM Provider
    if args.provider == "gemini":
        llm = GeminiProvider()
    elif args.provider == "openai":
        llm = OpenAIProvider()
    else:
        llm = MockProvider()

    agent = AutonomousResearchAgent(
        tools=tools,
        llm_provider=llm,
        max_iterations=args.max_iterations,
        timeout_seconds=args.timeout
    )

    # 3. Obtain Task Prompt
    task_prompt = args.task.strip()
    if not task_prompt:
        print("Enter your compound research task below (or type 'sample' to run standard benchmark, 'exit' to quit):")
        try:
            task_prompt = input("\nAgent Task >> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting agent.")
            return

    if not task_prompt or task_prompt.lower() == "exit":
        print("Goodbye.")
        return

    if task_prompt.lower() == "sample":
        task_prompt = (
            "Analyze quarterly_earnings_q3.txt in the sandbox, calculate the percentage increase "
            "in revenue from Q2 to Q3, and search the web for Python 3.13 features."
        )
        print(f"\n[Running Sample Benchmark Task]:\n{task_prompt}\n")

    print(f"\n[Agent Started] Resolving compound task...")
    response = agent.run(task_prompt)

    # 4. Display Execution Audit Log
    print("\n" + response.format_audit_log())
    print("\n" + "=" * 60)
    print(f"Execution Status: {response.termination_reason}")
    print(f"Total Steps: {response.total_steps} | Duration: {response.total_duration:.3f}s | Success: {response.success}")
    print("=" * 60)


if __name__ == "__main__":
    run_cli()
