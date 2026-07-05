# Obsidian_OS (LifeOS)

Obsidian-first life operating system that keeps Markdown as the source of truth and uses PostgreSQL for structured data and local AI retrieval for RAG.

Quick start

1. Copy LifeOS/Scripts/.env.example -> LifeOS/Scripts/.env and set POSTGRES_PASSWORD and any LLM env vars.
2. Start Postgres locally (docker-compose):

   docker-compose up -d

3. Apply schema:

   psql "$DATABASE_URL" -f LifeOS/Config/database/schema.sql

4. (Optional) Enable pgvector and run migration if using vector index:

   psql "$DATABASE_URL" -f LifeOS/Config/database/phase4_pgvector.sql

5. Install Python deps:

   pip install -r LifeOS/Scripts/requirements.txt
   pip install -r requirements-dev.txt  # dev tools

6. Bootstrap sample data (for development/CI):

   python LifeOS/Scripts/bootstrap_db.py

7. Run sync and indexing scripts from vault root:

   python LifeOS/Scripts/sync_vault.py
   python LifeOS/Scripts/index_embeddings.py
   python LifeOS/Scripts/semantic_search.py "your query" --context

Testing & CI

- Set repository secret POSTGRES_PASSWORD on GitHub.
- CI runs on push/pull_request and will install deps, run pre-commit checks, flake8, apply schema (on main/manual), bootstrap DB, and run pytest.

Contributing

- Install dev tools and enable pre-commit hooks:

  pip install -r requirements-dev.txt
  pre-commit install

- Run linters locally: pre-commit run --all-files; flake8 LifeOS

Security

- Do not commit secrets. Use LifeOS/Scripts/.env (ignored) and GitHub secrets for CI.

Architecture & Resume Highlights

- Architecture overview: see ARCHITECTURE.md for an enterprise-grade, markdown-first architecture (Obsidian UI, Python sync layer, PostgreSQL structured store, pgvector-ready semantic index, and local-first LLM integration).

- Resume-friendly highlights (copy to your CV):
  - Built an Obsidian-first knowledge platform with a Markdown source-of-truth and a backend sync layer to PostgreSQL for structured analytics and semantic retrieval.
  - Designed and implemented a token-efficient RAG pipeline (chunking, local embeddings, metadata-driven retrieval, context compression, local LLM integration).
  - Developed CI/CD (GitHub Actions) with linting, pre-commit enforcement, scheduled maintenance, and auto-fix PR automation to maintain code quality.
  - Implemented a phased pgvector migration strategy to add vector search without storing raw note content in the database.

How to demo (recommended talking points)
- Show Obsidian vault UI + dashboards (Dataview, Tasks).
- Start Postgres, apply schema, run sync_vault.py to show structured rows appearing in the DB.
- Run index_embeddings.py and semantic_search.py to demonstrate retrieval + compressed context sent to a local LLM.
- Show CI pipeline status and an auto-generated maintenance PR.

License

- Add your license here.
