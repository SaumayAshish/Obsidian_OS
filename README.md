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

License

- Add your license here.
