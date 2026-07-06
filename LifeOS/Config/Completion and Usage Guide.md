# LifeOS Completion and Usage Guide

## What Is Built

LifeOS is now an Obsidian-first operating system with:

- Markdown dashboards, templates, and indexes
- PostgreSQL structured backend
- SQLAlchemy sync layer
- Tasks, habits, goals, finance, and metrics sync
- Backend analytics dashboard
- Markdown chunking
- Text-backed semantic retrieval
- Optional pgvector migration
- Local Ollama assistant wrapper
- QuickAdd workflow guide
- Backup, validation, and daily automation scripts

## Daily Use

1. Open `Dashboard/Home.md`.
2. Create or update today's daily note.
3. Capture tasks, habits, expenses, learning, and journal notes.
4. Run:

```powershell
python Scripts/run_daily_automation.py
```

5. Open `Dashboard/Backend Summary.md` for database-backed analytics.

## Ask the Vault

Index first:

```powershell
python Scripts/index_embeddings.py
```

Search:

```powershell
python Scripts/semantic_search.py "What goals need attention?" --context
```

Ask Ollama:

```powershell
python Scripts/ask_lifeos.py "What should I focus on today?"
```

Ollama must be running locally and the model in `OLLAMA_MODEL` must be available.

## Environment

Settings live in `Scripts/.env`.

Important values:

```env
LIFEOS_VAULT_PATH=...
DATABASE_URL=...
LIFEOS_EMBEDDING_PROVIDER=hash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

Use `hash` for reliable offline testing. Use `sentence-transformers` for better semantic quality.

## PostgreSQL

Initialize and validate:

```powershell
python Scripts/sync_vault.py --init-db --validate-only
```

Sync:

```powershell
python Scripts/sync_vault.py
```

## pgvector

pgvector is optional. Your current database can run text-backed retrieval without it.

After installing pgvector on PostgreSQL:

```powershell
python Scripts/index_embeddings.py --migrate
```

## Validation

```powershell
python Scripts/sync_vault.py --validate-only
pytest Scripts/tests
```

## Backup

```powershell
python Scripts/backup_lifeos.py
```

Use `--skip-db` if `pg_dump` is not installed.

## Architecture Rule

Markdown remains the source of truth. PostgreSQL stores structured records, summaries, metadata, chunks, and embeddings. Raw note bodies are read from the vault only when needed for retrieval grounding.

