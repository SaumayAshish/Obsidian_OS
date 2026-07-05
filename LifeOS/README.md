# LifeOS

An Obsidian-first Life Operating System using Markdown as the primary interface, PostgreSQL for structured data, and local AI retrieval for low-token RAG.

## Phase 1 Scope

This scaffold includes:

- Full system architecture
- Vault folder structure
- Obsidian plugin setup
- PostgreSQL schema for structured data and Phase 4-ready embedding storage
- Phase 2 dashboards, templates, and Obsidian workflows
- Phase 3 Python sync scripts and SQLAlchemy models
- Phase 4 chunking, embedding abstraction, text-backed retrieval, and pgvector migration

Later phases should add templates, dashboards, sync scripts, embeddings, retrieval, and assistant workflows module by module.

## Design Rules

- Obsidian is the frontend and daily workspace.
- Markdown files are the source of truth for notes and knowledge.
- PostgreSQL stores structured records only: tasks, habits, finance, analytics, AI metadata, and embeddings.
- Raw Markdown note bodies are not stored in PostgreSQL.
- RAG retrieves small chunks, filters by metadata, compresses context, then calls the LLM.
- Local-first operation is preferred; cloud services are optional, not required.

## Setup Order

1. Open `LifeOS/` as an Obsidian vault.
2. Install the plugins listed in `Config/Plugin Setup.md`.
3. Create the PostgreSQL database and apply `Config/database/schema.sql`.
4. Open `Dashboard/Home.md` inside Obsidian.
5. Configure Periodic Notes to use the templates in `Templates/`.
6. Configure `Scripts/.env`.
7. Run `python Scripts/sync_vault.py` from `LifeOS/`.
8. Run `python Scripts/index_embeddings.py` to build retrieval chunks.
9. Use `python Scripts/semantic_search.py "query" --context` for compressed RAG context.

## Developer tooling

- Linting: flake8 with plugins (flake8-bugbear, flake8-docstrings). Install dev tools:

  pip install -r requirements-dev.txt

- Run lint locally:

  flake8 LifeOS

- Pre-commit hooks: install dev requirements then enable pre-commit hooks locally. This keeps commits consistent with CI:

  pip install -r requirements-dev.txt
  pre-commit install
  # To run checks across all files:
  pre-commit run --all-files

- CI: the repository CI installs requirements-dev.txt and runs pre-commit and flake8 before tests.

Badges (replace OWNER and REPO with your repository details)

- CI workflow badge:

  [![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

- Pre-commit scheduled job badge:

  [![Precommit scheduled](https://github.com/OWNER/REPO/actions/workflows/precommit-schedule.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/precommit-schedule.yml)

- Pre-commit auto-fix job badge:

  [![Precommit autofix](https://github.com/OWNER/REPO/actions/workflows/precommit-autofix.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/precommit-autofix.yml)

Add these lines at the top of your main README.md replacing OWNER/REPO to surface CI status publicly.

