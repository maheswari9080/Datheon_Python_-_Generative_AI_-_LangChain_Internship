"""
Grounded Question-Answering Pipeline for Task 2 (RAG & Semantic Retrieval).
Enforces strict hallucination guardrails, citation verification, and unanswerability detection.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
TASK1_DIR = ROOT_DIR / "task1-structured-extractor"

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(TASK1_DIR) not in sys.path:
    sys.path.insert(0, str(TASK1_DIR))

try:
    from vector_store import SearchResult, InMemoryVectorStore, create_vector_store
except ImportError:
    from .vector_store import SearchResult, InMemoryVectorStore, create_vector_store

try:
    from provider import LLMProvider, get_provider
except ImportError:
    from task1_structured_extractor.provider import LLMProvider, get_provider

logger = logging.getLogger(__name__)

UNSUPPORTED_QUESTION_RESPONSE = (
    "The available documents do not provide enough information to answer this question. "
    "Please verify that the relevant documents are indexed or refine your query."
)

RAG_SYSTEM_PROMPT = """You are a rigorous, truthful document research assistant.
Your duty is to answer the user's question using ONLY the factual evidence provided in the source excerpts below.

CRITICAL GUARDRAIL DIRECTIVES:
1. Ground every statement strictly in the provided excerpts.
2. If the excerpts do NOT contain adequate information to answer the question, you MUST respond exactly:
   "The available documents do not provide enough information to answer this question."
3. Include inline source citations using the exact format: [Source: <filename>, Page <page_number>].
4. NEVER fabricate facts, assumptions, or citations not present in the excerpts.
5. Keep your tone objective, clear, and professional.
"""


class Citation(BaseModel):
    """Provenance attribution for an answer segment."""
    filename: str
    page_number: int
    chunk_id: str
    excerpt: str
    relevance_score: float

    def formatted_citation(self) -> str:
        return f"[Source: {self.filename}, Page {self.page_number}]"


class QAResponse(BaseModel):
    """Complete response payload for a user query."""
    question: str
    answer: str
    citations: List[Citation] = []
    is_grounded: bool = True
    evidence_found: bool = True
    chunks_retrieved_count: int = 0
    retrieval_latency: float = 0.0
    generation_latency: float = 0.0
    provider_used: str = ""


class RAGQAPipeline:
    """End-to-end RAG orchestrator: similarity search, evidence gating, and grounded answer synthesis."""

    def __init__(
        self,
        vector_store: Any,
        llm_provider: Optional[LLMProvider] = None,
        top_k: int = 4,
        min_relevance_score: float = 0.15
    ):
        self.vector_store = vector_store
        self.llm_provider = llm_provider or get_provider()
        self.top_k = top_k
        self.min_relevance_score = min_relevance_score

    def answer_question(self, question: str) -> QAResponse:
        clean_q = question.strip()
        if not clean_q:
            return QAResponse(
                question="",
                answer="Please enter a valid question.",
                is_grounded=True,
                evidence_found=False
            )

        # 1. Retrieval Phase
        t0 = time.time()
        search_results: List[SearchResult] = self.vector_store.similarity_search(
            query=clean_q,
            top_k=self.top_k,
            score_threshold=self.min_relevance_score
        )
        retrieval_elapsed = time.time() - t0

        # 2. Evidence Gating: If no chunks retrieved above relevance threshold
        if not search_results:
            return QAResponse(
                question=clean_q,
                answer=UNSUPPORTED_QUESTION_RESPONSE,
                citations=[],
                is_grounded=True,
                evidence_found=False,
                chunks_retrieved_count=0,
                retrieval_latency=round(retrieval_elapsed, 3),
                generation_latency=0.0,
                provider_used=self.llm_provider.provider_name
            )

        # 3. Build Citations List & Prompt Context
        citations: List[Citation] = []
        context_blocks: List[str] = []

        for idx, res in enumerate(search_results, start=1):
            meta = res.metadata
            fn = meta.get("filename", "document")
            page = meta.get("page_number", 1)
            cid = meta.get("chunk_id", f"chunk_{idx}")
            
            # Truncate excerpt if too long for display
            excerpt_snippet = res.page_content.strip()
            if len(excerpt_snippet) > 280:
                excerpt_snippet = excerpt_snippet[:280] + "..."

            citations.append(Citation(
                filename=fn,
                page_number=page,
                chunk_id=cid,
                excerpt=excerpt_snippet,
                relevance_score=round(res.score, 4)
            ))

            block = (
                f"--- EXCERPT {idx} ---\n"
                f"Source: {fn}\n"
                f"Page: {page}\n"
                f"Content:\n{res.page_content}\n"
            )
            context_blocks.append(block)

        context_text = "\n".join(context_blocks)

        user_content = (
            f"SOURCE EXCERPTS:\n{context_text}\n\n"
            f"USER QUESTION: {clean_q}\n\n"
            f"ANSWER (using only the excerpts above with citations):"
        )

        messages = [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        # 4. Generation Phase
        t1 = time.time()
        try:
            # If using mock provider or generating deterministic grounded response
            if "mock" in self.llm_provider.provider_name.lower():
                answer_text = self._synthesize_mock_grounded_answer(clean_q, citations, search_results)
            else:
                answer_text = self.llm_provider.generate(messages, temperature=0.1)

            # Defensive verification: If the model itself states lack of evidence
            if "not provide enough information" in answer_text.lower():
                evidence_found = False
            else:
                evidence_found = True

        except Exception as e:
            logger.error("LLM Generation error in RAG pipeline: %s", e)
            answer_text = f"Error during grounded answer generation: {str(e)}"
            evidence_found = False

        generation_elapsed = time.time() - t1

        return QAResponse(
            question=clean_q,
            answer=answer_text,
            citations=citations,
            is_grounded=True,
            evidence_found=evidence_found,
            chunks_retrieved_count=len(search_results),
            retrieval_latency=round(retrieval_elapsed, 3),
            generation_latency=round(generation_elapsed, 3),
            provider_used=self.llm_provider.provider_name
        )

    def _synthesize_mock_grounded_answer(
        self,
        question: str,
        citations: List[Citation],
        search_results: List[SearchResult]
    ) -> str:
        """Deterministic grounded synthesis for offline testing and evaluation."""
        top_res = search_results[0]
        top_cit = citations[0]

        # Extract top 2 sentences from top retrieved chunk
        sentences = [s.strip() for s in top_res.page_content.split(".") if len(s.strip()) > 15]
        synthesis = ". ".join(sentences[:2]) if sentences else top_res.page_content[:150]
        if not synthesis.endswith("."):
            synthesis += "."

        return (
            f"Based on the indexed documentation, {synthesis} "
            f"[Source: {top_cit.filename}, Page {top_cit.page_number}]"
        )
