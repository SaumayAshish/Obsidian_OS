from __future__ import annotations

from sqlalchemy.orm import Session

from .embedding_service import EmbeddingService
from .ollama_client import generate
from .retrieval import compressed_context, semantic_search


SYSTEM_RULES = """You are the local LifeOS assistant.
Use only the provided context unless the user asks for general reasoning.
Prefer concise, actionable answers.
If context is insufficient, say what is missing.
Never claim you read the whole vault; you only receive retrieved chunks."""


def answer_question(
    session: Session,
    vault_path,
    service: EmbeddingService,
    question: str,
    limit: int = 8,
    token_budget: int = 1200,
) -> str:
    results = semantic_search(session, vault_path, service, question, limit=limit)
    context = compressed_context(results, token_budget=token_budget)
    prompt = f"{SYSTEM_RULES}\n\nContext:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
    return generate(prompt)

