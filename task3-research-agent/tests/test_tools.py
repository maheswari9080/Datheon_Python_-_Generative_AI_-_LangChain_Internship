import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import pytest

try:
    from tools.calculator_tool import SafeCalculatorTool, CalculatorSecurityError
    from tools.file_tool import SandboxedFileReaderTool, FileSandboxSecurityError
    from tools.search_tool import DuckDuckGoSearchTool
except ImportError:
    from task3_research_agent.tools.calculator_tool import SafeCalculatorTool, CalculatorSecurityError
    from task3_research_agent.tools.file_tool import SandboxedFileReaderTool, FileSandboxSecurityError
    from task3_research_agent.tools.search_tool import DuckDuckGoSearchTool


# ==============================================================================
# CALCULATOR TOOL TESTS
# ==============================================================================

def test_calculator_arithmetic():
    calc = SafeCalculatorTool()
    res = calc.run(expression="15 * 4 + 10 / 2")
    assert res.success is True
    assert res.output == "65"


def test_calculator_functions():
    calc = SafeCalculatorTool()
    res = calc.run(expression="sqrt(144) + abs(-8)")
    assert res.success is True
    assert res.output == "20"


def test_calculator_division_by_zero():
    calc = SafeCalculatorTool()
    res = calc.run(expression="100 / 0")
    assert "ZeroDivisionError" in res.output or "Calculation Error" in res.output


def test_calculator_security_blocks_code_execution():
    calc = SafeCalculatorTool()

    # Attempt import
    res1 = calc.run(expression="__import__('os').system('ls')")
    assert "Security Violation" in res1.output or not res1.success

    # Attempt attribute lookup
    res2 = calc.run(expression="(1).__class__.__bases__")
    assert "Security Violation" in res2.output or not res2.success

    # Attempt function definition / eval
    res3 = calc.run(expression="eval('2 + 2')")
    assert "Security Violation" in res3.output or not res3.success


# ==============================================================================
# FILE READER TOOL TESTS
# ==============================================================================

def test_file_reader_sandbox_success(tmp_path):
    # Setup test sandbox
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    sample_file = sandbox / "allowed_data.txt"
    sample_file.write_text("Confidential sandbox facts 2026", encoding="utf-8")

    reader = SandboxedFileReaderTool(sandbox_directory=str(sandbox))
    res = reader.run(filename="allowed_data.txt")

    assert res.success is True
    assert "Confidential sandbox facts 2026" in res.output


def test_file_reader_blocks_path_traversal(tmp_path):
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    secret_file = tmp_path / "outside_secret.txt"
    secret_file.write_text("Top secret outside sandbox", encoding="utf-8")

    reader = SandboxedFileReaderTool(sandbox_directory=str(sandbox))

    # Attempt directory traversal
    res = reader.run(filename="../outside_secret.txt")
    assert res.success is False or "Access Denied" in res.output or "traversal" in res.output.lower()
    assert "Top secret" not in res.output


def test_file_reader_nonexistent_file(tmp_path):
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    reader = SandboxedFileReaderTool(sandbox_directory=str(sandbox))
    res = reader.run(filename="does_not_exist.txt")
    assert "File Not Found" in res.output


# ==============================================================================
# SEARCH TOOL TESTS
# ==============================================================================

def test_search_tool_execution():
    search = DuckDuckGoSearchTool()
    res = search.run(query="Python programming language", max_results=2)
    assert res.success is True
    assert "URL:" in res.output
