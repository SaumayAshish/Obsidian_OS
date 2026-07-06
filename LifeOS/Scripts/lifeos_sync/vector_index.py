from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy import delete, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .chunker import NoteChunkData, chunk_note
from .embedding_service import EmbeddingService
from .embedding_store import TextEmbeddingStore
from .markdown import iter_markdown_files, parse_note
from .models import EmbeddingRecord, Note, NoteChunk

logger = logging.getLogger(__name__)


def apply_pgvector_migration(session: Session, vault_path: Path) -> None:
    migration = vault_path / "Config" / "database" / "phase4_pgvector.sql"
    session.connection().exec_driver_sql(migration.read_text(encoding="utf-8"))
    session.commit()


def index_vault(session: Session, vault_path: Path, service: EmbeddingService) -> dict[str, int]:
    store = TextEmbeddingStore()
    has_vector = has_pgvector_column(session)
    counts = {"files": 0, "chunks": 0, "embeddings": 0}
    for path in iter_markdown_files(vault_path):
        note = parse_note(path, vault_path)
        db_note = session.query(Note).filter(Note.path == note.relative_path).one_or_none()
        if not db_note:
            logger.debug("Skipping unsynced note: %s", note.relative_path)
            continue
        chunks = chunk_note(note)
        replace_chunks(session, db_note.id, chunks, service, store, has_vector)
        counts["files"] += 1
        counts["chunks"] += len(chunks)
        counts["embeddings"] += len(chunks)
    session.commit()
    logger.info("Indexed vault chunks: %s", counts)
    return counts


def replace_chunks(
    session: Session,
    note_id: int,
    chunks: list[NoteChunkData],
    service: EmbeddingService,
    store: TextEmbeddingStore,
    has_vector: bool,
) -> None:
    session.execute(delete(NoteChunk).where(NoteChunk.note_id == note_id))
    session.flush()
    for chunk in chunks:
        chunk_id = insert_chunk(session, note_id, chunk)
        embedding = service.embed(chunk.text)
        payload = {
            "chunk_id": chunk_id,
            "embedding_model": embedding.model,
            "embedding_text": store.serialize(embedding.values),
            "dimensions": embedding.dimensions,
            "provider": embedding.provider,
            "metadata": {"phase": 4},
        }
        stmt = insert(EmbeddingRecord.__table__).values(**payload)
        stmt = stmt.on_conflict_do_update(
            index_elements=[EmbeddingRecord.__table__.c.chunk_id],
            set_={key: getattr(stmt.excluded, key) for key in payload if key != "chunk_id"},
        )
        session.execute(stmt)
        if has_vector and embedding.dimensions == 384:
            vector_literal = "[" + ",".join(f"{value:.8f}" for value in embedding.values) + "]"
            session.execute(
                text(
                    """
                    UPDATE lifeos.embeddings
                    SET embedding_vector = CAST(:vector AS vector)
                    WHERE chunk_id = :chunk_id
                    """
                ),
                {"vector": vector_literal, "chunk_id": chunk_id},
            )


def insert_chunk(session: Session, note_id: int, chunk: NoteChunkData) -> int:
    payload = {
        "note_id": note_id,
        "chunk_index": chunk.chunk_index,
        "heading_path": chunk.heading_path,
        "chunk_hash": chunk.chunk_hash,
        "token_estimate": chunk.token_estimate,
        "summary": chunk.summary,
        "keywords": chunk.keywords,
        "metadata": {
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
        },
    }
    stmt = insert(NoteChunk.__table__).values(**payload).returning(NoteChunk.__table__.c.id)
    return session.execute(stmt).scalar_one()


def vector_literal(values: list[float]) -> str:
    return json.dumps(values, separators=(",", ":"))


def has_pgvector_column(session: Session) -> bool:
    return bool(
        session.execute(
            text(
                """
                SELECT count(*)
                FROM information_schema.columns
                WHERE table_schema = 'lifeos'
                  AND table_name = 'embeddings'
                  AND column_name = 'embedding_vector'
                """
            )
        ).scalar_one()
    )
