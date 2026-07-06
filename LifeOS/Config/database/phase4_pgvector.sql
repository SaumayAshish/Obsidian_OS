-- Phase 4 pgvector migration.
-- Apply after Config/database/schema.sql.

CREATE EXTENSION IF NOT EXISTS vector;

SET search_path TO lifeos, public;

ALTER TABLE embeddings
ADD COLUMN IF NOT EXISTS embedding_vector vector(384);

CREATE INDEX IF NOT EXISTS idx_embeddings_vector_cosine
ON embeddings USING ivfflat (embedding_vector vector_cosine_ops)
WITH (lists = 100);

CREATE OR REPLACE FUNCTION match_note_chunks(
    query_embedding vector(384),
    match_count INTEGER DEFAULT 8,
    note_type_filter TEXT DEFAULT NULL,
    tag_filter TEXT[] DEFAULT NULL
)
RETURNS TABLE (
    chunk_id BIGINT,
    note_id BIGINT,
    path TEXT,
    title TEXT,
    heading_path TEXT,
    summary TEXT,
    similarity DOUBLE PRECISION,
    token_estimate INTEGER,
    metadata JSONB
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        c.id AS chunk_id,
        n.id AS note_id,
        n.path,
        n.title,
        c.heading_path,
        c.summary,
        1 - (e.embedding_vector <=> query_embedding) AS similarity,
        c.token_estimate,
        c.metadata
    FROM embeddings e
    JOIN note_chunks c ON c.id = e.chunk_id
    JOIN notes n ON n.id = c.note_id
    WHERE e.embedding_vector IS NOT NULL
      AND (note_type_filter IS NULL OR n.note_type = note_type_filter)
      AND (tag_filter IS NULL OR n.tags && tag_filter)
    ORDER BY e.embedding_vector <=> query_embedding
    LIMIT match_count;
$$;

