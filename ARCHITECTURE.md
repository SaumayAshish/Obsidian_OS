Architecture for Obsidian_OS (LifeOS)

Overview
- Primary UX: Obsidian vault (Markdown-first). Users edit notes locally; Obsidian plugins (Dataview, Tasks, Templater) provide dashboards.
- Backend: Python automation (LifeOS/Scripts) that parses Markdown, syncs structured records to PostgreSQL, indexes semantic chunks, and runs RAG workflows.
- Database: PostgreSQL 15+ (schema in LifeOS/Config/database/schema.sql). Phase 4: pgvector for vector indexes and semantic search.
- Embeddings: sentence-transformers (local) or hash fallback for offline testing; embeddings metadata stored in DB and text-backup preserved outside DB.
- LLM: Local-first (Ollama) with clear fallbacks to cloud providers; compressed context and token-efficiency strategies applied.

Components & Responsibilities
- Obsidian Vault (LifeOS/): source-of-truth markdown, templates, dashboards, AI Memory notes.
- Scripts (LifeOS/Scripts/): sync_vault.py, index_embeddings.py, semantic_search.py, bootstrap_db.py — idempotent scripts for sync, indexing, backup.
- Database (Postgres): structured records (notes metadata, tasks, goals, habits, finance, embeddings metadata) — raw note bodies are NOT persisted.
- Vector Index (Phase 4): pgvector extension + note_chunks + embeddings tables for fast semantic retrieval.
- CI/CD: GitHub Actions workflows under .github/workflows for tests, linting, pre-commit, scheduled maintenance, and auto-fix PRs.

Security & Operations
- Secrets: environment variables only (LifeOS/Scripts/.env local; GitHub secrets for CI). No secrets in repo.
- Backups: backup_lifeos.py writes vault + db dumps to LifeOS/Archive/Backups (ignored in git).
- Monitoring: Use simple health checks (pg_isready) in docker-compose and CI; add observability with papertrail/Datadog or Prometheus exporters for production.

Deployment & Local Dev
- Local dev: docker-compose up -d (Postgres 15), psql $DATABASE_URL -f LifeOS/Config/database/schema.sql, python -m pip install -r LifeOS/Scripts/requirements.txt
- CI: .github/workflows/ci.yml runs lint, pre-commit, schema apply (main/manual), bootstraps sample data, and runs pytest.

Extensibility notes
- To enable pgvector in CI, provide a Postgres image with pgvector installed or use a custom container build.
- To add cloud sync or multi-user features, introduce a backend API service with authentication and tenancy (OAuth + role-based access), and migrate structured writes through that API rather than direct DB manipulation.

Validation & Tests
- Unit tests live under LifeOS/Scripts/tests; run pytest LifeOS/Scripts/tests
- Integration: use docker-compose and bootstrap_db.py for sample data then run sync scripts in CI to validate end-to-end flows.

Resume/Interview pointers
- This repo demonstrates: markdown-first UX, structured-sync architecture, RAG with token-compression, pgvector migration plan, local-first LLM integration, and enterprise-grade CI with auto-fix maintenance. Use the README resume section for recruiter-friendly phrasing and ATS keywords.
