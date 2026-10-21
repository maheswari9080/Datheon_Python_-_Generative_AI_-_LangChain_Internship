import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
ROOT_DIR = MODULE_DIR.parent
TASK1_DIR = ROOT_DIR / "task1-structured-extractor"
TASK2_DIR = ROOT_DIR / "task2-rag-research"
TASK3_DIR = ROOT_DIR / "task3-research-agent"

for p in (MODULE_DIR, ROOT_DIR, TASK1_DIR, TASK2_DIR, TASK3_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pytest

try:
    from integrations import ChatBridge, stream_text_chunks
    from provider import MockProvider
    from vector_store import InMemoryVectorStore, LocalDeterministicEmbedding
    from chunking import DocumentChunk
except ImportError:
    from task4_conversation_studio.integrations import ChatBridge, stream_text_chunks
    from task1_structured_extractor.provider import MockProvider
    from task2_rag_research.vector_store import InMemoryVectorStore, LocalDeterministicEmbedding
    from task2_rag_research.chunking import DocumentChunk


def test_streaming_generator():
    original = "This is a streaming token test"
    streamed = "".join(list(stream_text_chunks(original, delay=0.001)))
    assert streamed == original


def test_bridge_general_chat():
    prov = MockProvider()
    bridge = ChatBridge(provider=prov)

    msgs = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello AI"}
    ]
    resp = bridge.process_general_chat(msgs)
    assert len(resp) > 0
    assert "AI Research Workbench" in resp


def test_bridge_rag_query():
    embedder = LocalDeterministicEmbedding()
    store = InMemoryVectorStore(embedding_provider=embedder)
    store.add_chunks([
        DocumentChunk(
            chunk_id="chk1",
            page_content="Consensus nodes maintain heartbeat frequencies at 150ms.",
            metadata={"filename": "consensus_guide.txt", "page_number": 1}
        )
    ])

    bridge = ChatBridge(provider=MockProvider(), rag_vector_store=store)
    answer, citations = bridge.process_rag_query("What is the heartbeat frequency?")

    assert len(answer) > 0
    assert len(citations) > 0
    assert citations[0]["filename"] == "consensus_guide.txt"


def test_bridge_agent_task():
    bridge = ChatBridge(
        provider=MockProvider(),
        agent_sandbox_dir=str(TASK3_DIR / "sandbox_data")
    )
    answer, audit_log, steps = bridge.process_agent_task("Calculate revenue growth and search web")

    assert len(answer) > 0
    assert len(audit_log) > 0
    assert len(steps) >= 1
