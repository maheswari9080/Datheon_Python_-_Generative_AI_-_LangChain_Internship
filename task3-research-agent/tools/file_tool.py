"""
Sandboxed Local File Reader Tool for Task 3 Agent.
Strictly constrains file access to an explicitly designated local directory.
Enforces strict path canonicalization to prevent directory traversal attacks (e.g. ../, symlinks).
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

try:
    from .base import BaseTool
except ImportError:
    from base import BaseTool


class FileReadInput(BaseModel):
    filename: str = Field(
        description="Relative filename to read from the permitted sandbox directory, e.g. 'financial_report.txt'"
    )


class FileSandboxSecurityError(Exception):
    """Raised when a file read request attempts directory traversal outside sandbox."""
    pass


class SandboxedFileReaderTool(BaseTool):
    """File reader constrained to an explicitly permitted sandbox directory."""

    name = "file_reader"
    description = (
        "Reads textual files strictly within the permitted sandbox directory. "
        "Provide a relative filename such as 'financial_report.txt' or 'data.json'. "
        "Access outside the sandbox directory is strictly blocked."
    )
    args_schema = FileReadInput

    def __init__(self, sandbox_directory: Optional[str] = None, max_bytes: int = 50_000):
        super().__init__()
        if sandbox_directory:
            self.sandbox_path = Path(sandbox_directory).resolve()
        else:
            # Default to 'sandbox_data' under task3 directory
            self.sandbox_path = (Path(__file__).resolve().parent.parent / "sandbox_data").resolve()

        self.sandbox_path.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes

    def _run(self, filename: str) -> str:
        clean_name = filename.strip().lstrip("/\\")
        if not clean_name:
            raise ValueError("No filename specified.")

        # Resolve target canonical path
        target_path = (self.sandbox_path / clean_name).resolve()

        # Security check: Target MUST reside strictly inside sandbox directory
        try:
            target_path.relative_to(self.sandbox_path)
        except ValueError:
            raise FileSandboxSecurityError(
                f"Access Denied: Path traversal detected. '{filename}' attempts access outside the permitted sandbox directory."
            )

        if not target_path.exists():
            available = [f.name for f in self.sandbox_path.iterdir() if f.is_file()]
            return f"File Not Found: '{clean_name}'. Available sandbox files: {available}"

        if not target_path.is_file():
            return f"Error: '{clean_name}' is a directory, not a readable text file."

        # Read safely with byte limit and encoding fallbacks
        file_size = target_path.stat().st_size
        if file_size > self.max_bytes:
            return f"Error: File '{clean_name}' ({file_size} bytes) exceeds maximum safe read limit of {self.max_bytes} bytes."

        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                content = target_path.read_text(encoding=enc)
                return content
            except UnicodeDecodeError:
                continue

        return f"Error: Unable to decode file '{clean_name}' as text."
