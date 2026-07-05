# Obsidian_OS (LifeOS)

Obsidian-first life operating system that keeps Markdown as the source of truth and uses PostgreSQL for structured data and local AI retrieval for RAG.

```
┌─────────────────────────────────────────────────────────────┐
│                    Obsidian UI (Frontend)                    │
│  • Markdown notes + frontmatter                              │
│  • Dataview dashboards, Tasks plugins, Tracker habit graphs │
│────────────────────────────────────────────────────────────┐│
   │                                                           ││
   ├─→ Markdown Files (Source of Truth)                       ││
   │   ├─ Daily Notes, Goals, Finance, Learning               ││
   │   └─ AI Memory (summaries, preferences)                  ││
   │                                                           ││
   ├─→ Python Sync Layer (LifeOS/Scripts)                     ││
   │   ├─ sync_vault.py: Parse Markdown → Extract metadata   ││
   │   ├─ index_embeddings.py: Build semantic chunks          ││
   │   └─ semantic_search.py: Retrieve + compress context    ││
   │                                                           ││
   └─→ PostgreSQL Backend (Structured Data)                   ││
       ├─ Tables: notes, tasks, goals, habits, finance, etc   ││
       ├─ Embeddings metadata (not raw note bodies)           ││
       └─ pgvector support (Phase 4) for vector search        ││
                                                              ││
       ├─→ Local LLM / Cloud API                             ││
       │   └─ Token-efficient compressed context             ││
       │                                                      ││
       └─→ CI/CD (GitHub Actions)                            ││
           ├─ Pre-commit hooks (local + scheduled)           ││
           ├─ Linting (flake8 + plugins)                     ││
           ├─ Tests (pytest + sample data)                   ││
           └─ Auto-fix maintenance PRs                       ││
└───────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

1. **Clone & setup environment:**

   git clone https://github.com/SaumayAshish/Obsidian_OS.git
   cd Obsidian_OS
   cp LifeOS/Scripts/.env.example LifeOS/Scripts/.env
   # Edit .env and set POSTGRES_PASSWORD, DATABASE_URL

2. **Start PostgreSQL (docker-compose):**

   docker-compose up -d
   # Wait ~10 seconds for Postgres to be ready

3. **Apply database schema:**

   psql "$DATABASE_URL" -f LifeOS/Config/database/schema.sql

4. **(Optional) Enable pgvector for vector search (Phase 4):**

   psql "$DATABASE_URL" -f LifeOS/Config/database/phase4_pgvector.sql

5. **Install Python dependencies:**

   pip install -r LifeOS/Scripts/requirements.txt
   pip install -r requirements-dev.txt  # Dev tools (linting, pre-commit)

6. **Bootstrap sample data (for testing):**

   python LifeOS/Scripts/bootstrap_db.py

7. **Open Obsidian vault:**

   # Open LifeOS/ as an Obsidian vault
   # See LifeOS/Config/Plugin Setup.md for required plugins

8. **Run sync and RAG commands:**

   # From repo root:
   python LifeOS/Scripts/sync_vault.py         # Parse notes → store in DB
   python LifeOS/Scripts/index_embeddings.py   # Build semantic chunks
   python LifeOS/Scripts/semantic_search.py "your query" --context

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for an in-depth walkthrough covering:
- System layers (UI, sync, storage, AI/RAG, CI/CD)
- Security & operations
- Extensibility patterns
- Deployment & local dev

## Testing & CI

### Local development

- **Pre-commit hooks** (catch formatting/lint issues before commit):

  pip install -r requirements-dev.txt
  pre-commit install
  pre-commit run --all-files  # Run on all files

- **Linting:**

  flake8 LifeOS

- **Tests:**

  pytest LifeOS/Scripts/tests -q

### GitHub Actions CI

- Set `POSTGRES_PASSWORD` secret in repo settings (Settings → Secrets).
- CI runs on push/PR and automatically:
  - Checks pre-commit hooks (on changed files)
  - Runs flake8 linting
  - Applies schema to test DB (on main branch or manual trigger)
  - Bootstraps sample data
  - Runs pytest test suite
- Scheduled jobs (weekly) run pre-commit on all files and auto-create PRs for fixes.

## Resume Highlights

Use these bullets on your CV / LinkedIn:

- **Markdown-first knowledge platform:** Built an Obsidian-integrated system where Markdown remains the source of truth; Python automation syncs structured records to PostgreSQL for analytics and retrieval without persisting raw note bodies.

- **Token-efficient RAG pipeline:** Designed semantic chunking, local embeddings (sentence-transformers), metadata-driven filtering, and context compression to minimize LLM token usage while maintaining retrieval quality.

- **Production-grade CI/CD:** Implemented GitHub Actions workflows with pre-commit enforcement, flake8 linting, scheduled maintenance, and auto-fix PR generation—demonstrating DevOps maturity and code quality discipline.

- **Phased architecture evolution:** Planned pgvector migration (Phase 4) to add vector search without breaking existing deployments, showcasing enterprise-level schema migration strategy.

- **Full-stack system design:** Integrated Obsidian UI, Python sync layer, PostgreSQL backend, and local LLM into a cohesive, extensible system suitable for personal knowledge management or as a foundation for SaaS multi-tenant features.

## Demo / Interview Talking Points

**"Walk me through how this system works:"**

1. **Show the vault:** Open `LifeOS/` in Obsidian. Highlight a daily note with structured frontmatter (task, goal, expense, habit).

2. **Trigger sync:** Run `python LifeOS/Scripts/sync_vault.py`. Show how structured records appear in PostgreSQL (use `psql` to query `lifeos.tasks`, `lifeos.finance_transactions`, etc.).

3. **Index & search:** Run `python LifeOS/Scripts/index_embeddings.py` to build semantic chunks, then `python LifeOS/Scripts/semantic_search.py "active goals and next actions" --context` to retrieve and show compressed context ready for an LLM.

4. **CI/CD:** Show GitHub Actions dashboard. Explain pre-commit hooks, linting, schema validation, and auto-fix maintenance PRs.

5. **Architecture:** Reference ARCHITECTURE.md and explain the phased approach (Phase 1 = foundation, Phase 4 = pgvector). Highlight design decisions (Markdown as source of truth, token efficiency, local-first).

**Key talking points for interviews:**

- "This system demonstrates understanding of data ownership (Markdown truth, DB metadata only) and practical RAG implementation (chunking, compression, filtering)."
- "The CI/CD setup shows production maturity: automated linting, pre-commit, schema migrations, and auto-fix workflows—things real teams care about."
- "The phased architecture shows thinking about scalability and migration paths without breaking users."

## Contributing

- Install dev tools and enable pre-commit hooks (see "Local development" above).
- Make changes in a feature branch; CI will check your code.
- PRs that pass CI can be merged.

## Security

- **Never commit secrets.** Use environment variables (LifeOS/Scripts/.env, ignored in git).
- CI uses GitHub Secrets for POSTGRES_PASSWORD and other sensitive data.

## License

- Add your license here (e.g., MIT, Apache 2.0, etc.).
