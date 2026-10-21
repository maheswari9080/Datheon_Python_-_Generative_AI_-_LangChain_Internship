import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import pytest
import json

try:
    from conversation import ConversationManager, ChatMessage
except ImportError:
    from task4_conversation_studio.conversation import ConversationManager, ChatMessage


def test_conversation_manager_add_and_format():
    mgr = ConversationManager(system_instruction="Be concise.")
    assert len(mgr.messages) == 0

    mgr.add_message("user", "Hello there!")
    mgr.add_message("assistant", "Greetings, researcher.")

    assert len(mgr.messages) == 2
    llm_msgs = mgr.get_messages_for_llm()
    assert len(llm_msgs) == 3
    assert llm_msgs[0]["role"] == "system"
    assert llm_msgs[0]["content"] == "Be concise."
    assert llm_msgs[1]["role"] == "user"
    assert llm_msgs[2]["role"] == "assistant"


def test_token_estimation():
    mgr = ConversationManager(system_instruction="System prompt.")
    mgr.add_message("user", "What is Raft consensus?")
    tokens = mgr.estimate_tokens()
    assert tokens > 0


def test_export_serialization():
    mgr = ConversationManager()
    mgr.add_message("user", "Query test")
    mgr.add_message("assistant", "Answer test", metadata={"citations": [{"filename": "doc.txt", "page_number": 1}]})

    json_str = mgr.export_to_json()
    parsed = json.loads(json_str)
    assert parsed["message_count"] == 2
    assert parsed["messages"][0]["content"] == "Query test"

    md_str = mgr.export_to_markdown()
    assert "### USER" in md_str
    assert "### ASSISTANT" in md_str
    assert "doc.txt" in md_str


def test_conversation_reset():
    mgr = ConversationManager()
    mgr.add_message("user", "Test message")
    assert len(mgr.messages) == 1

    mgr.clear()
    assert len(mgr.messages) == 0
