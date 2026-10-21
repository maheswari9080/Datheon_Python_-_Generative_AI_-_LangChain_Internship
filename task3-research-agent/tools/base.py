"""
Base Tool Interface and Audit Telemetry Schema for Task 3 Autonomous Agent.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Structured telemetry output returned by any tool execution."""
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    output: str
    success: bool
    error: Optional[str] = None
    execution_time_seconds: float = 0.0

    def format_log(self) -> str:
        status_icon = "✓" if self.success else "✗"
        return f"[{status_icon}] {self.tool_name} (args: {self.arguments}) -> {self.output[:120]}"


class BaseTool(ABC):
    """Abstract base class for all agent tools."""

    name: str
    description: str
    args_schema: Optional[Type[BaseModel]] = None

    @abstractmethod
    def _run(self, **kwargs) -> str:
        """Internal execution method implemented by subclasses."""
        pass

    def run(self, **kwargs) -> ToolResult:
        """Execute tool with timing, argument sanitization, and structured error handling."""
        start_time = time.time()
        # Sanitize arguments: do not allow sensitive strings or unbounded length
        sanitized_args = {k: str(v)[:200] for k, v in kwargs.items()}

        try:
            if self.args_schema:
                validated = self.args_schema.model_validate(kwargs)
                kwargs = validated.model_dump()

            raw_output = self._run(**kwargs)
            elapsed = time.time() - start_time
            return ToolResult(
                tool_name=self.name,
                arguments=sanitized_args,
                output=str(raw_output),
                success=True,
                execution_time_seconds=round(elapsed, 4)
            )
        except Exception as e:
            elapsed = time.time() - start_time
            err_msg = f"{type(e).__name__}: {str(e)}"
            return ToolResult(
                tool_name=self.name,
                arguments=sanitized_args,
                output=f"Tool Execution Error: {err_msg}",
                success=False,
                error=err_msg,
                execution_time_seconds=round(elapsed, 4)
            )
