from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

from sqlalchemy import text
from sqlalchemy.orm import Session

from .embedding_service import EmbeddingService
from .embedding_store import TextEmbeddingStore


@dataclass(frozen=True)
class RetrievalResult:
    path: str
    title: str
    heading_path: str | None
    summary: str | None
    similarity: float
    token_estimate: int
    text: str


def semantic_search(
    session: Session,
    vault_path: Path,
    service: EmbeddingService,
    query: str,
    limit: int = 8,
    note_type: str | None = None,
) -> list[RetrievalResult]:
    embedding = service.embed(query)
    if not has_match_function(session):
        return text_embedding_search(session, vault_path, embedding.values, limit, note_type)
    vector = "[" + ",".join(f"{value:.8f}" for value in embedding.values) + "]"
    rows = session.execute(
        text(
            """
            SELECT *
            FROM lifeos.match_note_chunks(CAST(:embedding AS vector), :limit, :note_type, NULL)
            """
        ),
        {"embedding": vector, "limit": limit, "note_type": note_type},
    ).mappings()
    return [row_to_result(vault_path, row) for row in rows]


def text_embedding_search(
    session: Session,
    vault_path: Path,
    query_embedding: list[float],
    limit: int,
    note_type: str | None,
) -> list[RetrievalResult]:
    store = TextEmbeddingStore()
    rows = session.execute(
        text(
            """
            SELECT
                c.id AS chunk_id,
                n.path,
                n.title,
                n.note_type,
                c.heading_path,
                c.summary,
                c.token_estimate,
                c.metadata,
                e.embedding_text
            FROM lifeos.embeddings e
            JOIN lifeos.note_chunks c ON c.id = e.chunk_id
            JOIN lifeos.notes n ON n.id = c.note_id
            WHERE (CAST(:note_type AS TEXT) IS NULL OR n.note_type = CAST(:note_type AS TEXT))
            """
        ),
        {"note_type": note_type},
    ).mappings()

    scored = []
    for row in rows:
        score = cosine_similarity(query_embedding, store.deserialize(str(row["embedding_text"])))
        scored.append((score, row))
    scored.sort(key=lambda item: item[0], reverse=True)

    results: list[RetrievalResult] = []
    for score, row in scored[:limit]:
        result = row_to_result(vault_path, row)
        results.append(
            RetrievalResult(
                path=result.path,
                title=result.title,
                heading_path=result.heading_path,
                summary=result.summary,
                similarity=score,
                token_estimate=result.token_estimate,
                text=result.text,
            )
        )
    return results


def row_to_result(vault_path: Path, row: dict) -> RetrievalResult:
    metadata = row.get("metadata") or {}
    path = str(row["path"])
    text_value = read_chunk_text(vault_path / path, metadata.get("start_line"), metadata.get("end_line"))
    return RetrievalResult(
        path=path,
        title=str(row["title"]),
        heading_path=row.get("heading_path"),
        summary=row.get("summary"),
        similarity=float(row.get("similarity") or 0),
        token_estimate=int(row["token_estimate"]),
        text=text_value,
    )


def read_chunk_text(path: Path, start_line: int | None, end_line: int | None) -> str:
    if not path.exists() or not start_line or not end_line:
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[start_line - 1 : end_line]).strip()


def compressed_context(results: list[RetrievalResult], token_budget: int = 1200) -> str:
    blocks: list[str] = []
    used = 0
    for index, result in enumerate(results, start=1):
        text = result.summary or result.text
        estimate = max(1, int(len(text.split()) / 0.75))
        if used + estimate > token_budget:
            break
        used += estimate
        blocks.append(
            "\n".join(
                [
                    f"[{index}] {result.title}",
                    f"path: {result.path}",
                    f"heading: {result.heading_path or ''}",
                    f"similarity: {result.similarity:.3f}",
                    f"summary: {text}",
                ]
            )
        )
    return "\n\n".join(blocks)


def has_match_function(session: Session) -> bool:
    return bool(
        session.execute(
            text(
                """
                SELECT count(*)
                FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                WHERE n.nspname = 'lifeos'
                  AND p.proname = 'match_note_chunks'
                """
            )
        ).scalar_one()
    )


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
    right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
    return dot / (left_norm * right_norm)
