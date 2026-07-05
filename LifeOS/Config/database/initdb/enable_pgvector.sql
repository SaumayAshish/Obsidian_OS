-- Enable pgvector extension if the Postgres image/host provides it.
-- This will succeed only if the vector extension is available on the server.

CREATE EXTENSION IF NOT EXISTS vector;

-- If this fails during container init, either use a Postgres image with pgvector
-- preinstalled or install pgvector on the host server and re-run migration.
