"""
Conversation State and History Management for Task 4 Conversation Studio.
Handles multi-turn message retention, token budgeting, formatting, and export serialization.
"""

from datetime import datetime, timezone
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Immutable chat message record."""
    role: str = Field(description="Role identifier: 'user', 'assistant', or 'system'")
    content: str = Field(description="Message textual body")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"))
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Telemetry, mode, citations")


class ConversationManager:
    """Manages session-isolated conversation state, system directives, and exports."""

    def __init__(self, system_instruction: Optional[str] = None):
        self.system_instruction = system_instruction or (
            "You are an expert AI Research Assistant. Provide accurate, clear, and comprehensive responses."
        )
        self.messages: List[ChatMessage] = []

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        msg = ChatMessage(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        return msg

    def clear(self):
        """Reset conversation history."""
        self.messages = []

    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """Format history for API consumption."""
        formatted = [{"role": "system", "content": self.system_instruction}]
        for m in self.messages:
            formatted.append({"role": m.role, "content": m.content})
        return formatted

    def estimate_tokens(self) -> int:
        """Heuristic character-based token estimator (~4 chars per token)."""
        total_chars = len(self.system_instruction) + sum(len(m.content) for m in self.messages)
        return max(1, total_chars // 4)

    def export_to_json(self) -> str:
        """Serialize conversation history to JSON."""
        payload = {
            "system_instruction": self.system_instruction,
            "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
            "message_count": len(self.messages),
            "messages": [m.model_dump() for m in self.messages]
        }
        return json.dumps(payload, indent=2)

    def export_to_markdown(self) -> str:
        """Format conversation as human-readable Markdown transcript."""
        lines = [
            "# AI Research Workbench - Conversation Transcript",
            f"**Exported At:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}",
            f"**System Prompt:** *{self.system_instruction}*",
            "\n---\n"
        ]
        for m in self.messages:
            role_title = m.role.upper()
            lines.append(f"### {role_title} ({m.timestamp})")
            lines.append(m.content)
            if m.metadata and "citations" in m.metadata:
                lines.append("\n*Citations:*")
                for cit in m.metadata["citations"]:
                    lines.append(f"- {cit.get('filename')} (p.{cit.get('page_number')})")
            lines.append("\n---\n")
        return "\n".join(lines)
