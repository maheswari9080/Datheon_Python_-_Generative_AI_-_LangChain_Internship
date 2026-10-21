"""
Task 3: Multi-Tool Autonomous AI Agent.
"""
try:
    from .agent import AutonomousResearchAgent, AgentResponse, AgentStep
    from .tools.base import BaseTool, ToolResult
    from .tools.calculator_tool import SafeCalculatorTool, CalculatorSecurityError
    from .tools.file_tool import SandboxedFileReaderTool, FileSandboxSecurityError
    from .tools.search_tool import DuckDuckGoSearchTool
except (ImportError, TypeError):
    from agent import AutonomousResearchAgent, AgentResponse, AgentStep
    from tools.base import BaseTool, ToolResult
    from tools.calculator_tool import SafeCalculatorTool, CalculatorSecurityError
    from tools.file_tool import SandboxedFileReaderTool, FileSandboxSecurityError
    from tools.search_tool import DuckDuckGoSearchTool

__all__ = [
    "AutonomousResearchAgent",
    "AgentResponse",
    "AgentStep",
    "BaseTool",
    "ToolResult",
    "SafeCalculatorTool",
    "CalculatorSecurityError",
    "SandboxedFileReaderTool",
    "FileSandboxSecurityError",
    "DuckDuckGoSearchTool",
]
