# LifeOS Scripts

Phase 3 adds PostgreSQL sync for structured data extracted from Markdown.

Phase 3 does not require pgvector. Embedding storage is text-backed temporarily so Phase 4 can replace it with pgvector without changing the rest of the sync architecture.

## Install

```powershell
cd LifeOS\Scripts
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`:

```env
LIFEOS_VAULT_PATH=../
DATABASE_URL=postgresql+psycopg://lifeos:lifeos@localhost:5432/lifeos
LIFEOS_SCHEMA=lifeos
LIFEOS_LOG_LEVEL=INFO
```

If the password contains `@`, URL-encode it as `%40`.

## Initialize Database

Preferred:

```powershell
psql -d lifeos -f ..\Config\database\schema.sql
```

Alternative SQLAlchemy bootstrap:

```powershell
python sync_vault.py --init-db
```

The SQL file remains the authoritative schema because it includes indexes and analytics views.

## Sync Vault

```powershell
python sync_vault.py
```

Validate without syncing:

```powershell
python sync_vault.py --validate-only
```

Backend dashboard JSON:

```powershell
python backend_dashboard.py
```

The sync extracts:

- Note metadata
- Markdown tasks
- Habit checkboxes tagged `#habit`
- Finance table rows with `Date`, `Category`, `Amount`, and optional `Type`, `Merchant`, `Currency`, `Note`
- Daily metrics
- Goal metadata

Raw Markdown bodies are not stored in PostgreSQL.

## Duplicate Prevention

- Notes use unique `path`.
- Tasks use unique `external_id`.
- Finance rows use unique `external_id`.
- Habit logs use unique `(habit_id, log_date)`.
- Sync deletes and replaces note-scoped tasks and finance rows before inserting the current Markdown state.

## Logging

Set `LIFEOS_LOG_LEVEL=DEBUG` in `.env` for per-file sync logs.

## Dashboard Stats

```powershell
python dashboard_stats.py
```

## Phase 4 Retrieval

Text-backed indexing works without pgvector:

```powershell
$env:LIFEOS_EMBEDDING_PROVIDER="hash"
python index_embeddings.py
python semantic_search.py "goals dashboard" --limit 5
python semantic_search.py "goals dashboard" --context
```

Production semantic embeddings:

```powershell
pip install -r requirements.txt
$env:LIFEOS_EMBEDDING_PROVIDER="sentence-transformers"
python index_embeddings.py
```

Enable pgvector after the PostgreSQL server has the `vector` extension installed:

```powershell
python index_embeddings.py --migrate
```

If `--migrate` fails with `extension "vector" is not available`, install pgvector for the PostgreSQL server first. The text-backed retrieval path remains usable.

## Finance Table Format

```markdown
| Date | Type | Category | Merchant | Amount | Currency | Note |
|---|---|---|---|---:|---|---|
| 2026-05-13 | expense | Food | Cafe | 250 | INR | Lunch |
```

## Task Format

```markdown
- [ ] #task Finish project brief due: 2026-05-14
- [x] #task Review goals done: 2026-05-13
```

## Habit Format

```markdown
- [ ] #habit/exercise Exercise
- [x] #habit/reading Read
```
