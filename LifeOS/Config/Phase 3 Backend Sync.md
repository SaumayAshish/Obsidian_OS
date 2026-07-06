# Phase 3 Backend Sync

## Purpose

The backend sync converts selected Markdown structures into PostgreSQL rows for analytics and future AI retrieval. Markdown remains the source of truth.

Phase 3 intentionally does not use pgvector. Embedding rows use `TEXT` storage as a temporary abstraction. Phase 4 can migrate this to pgvector.

## Data Flow

```text
Obsidian Markdown
  -> LifeOS/Scripts/lifeos_sync markdown parser
  -> SQLAlchemy models
  -> PostgreSQL lifeos schema
  -> analytics views and scripts
```

## Synced Entities

| Entity | Markdown Source | PostgreSQL Table |
|---|---|---|
| Notes | frontmatter and file metadata | `lifeos.notes` |
| Tasks | Markdown checkboxes | `lifeos.tasks` |
| Habits | `#habit` checkboxes | `lifeos.habit_definitions`, `lifeos.habit_logs` |
| Finance | Markdown tables | `lifeos.finance_transactions` |
| Goals | goal note frontmatter | `lifeos.goals` |
| Daily metrics | daily note frontmatter and checkboxes | `lifeos.daily_metrics` |

## Commands

```powershell
cd LifeOS\Scripts
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python sync_vault.py
```

Validate only:

```powershell
python sync_vault.py --validate-only
```

Backend dashboard:

```powershell
python backend_dashboard.py
```

## Constraints

- The sync is designed to be re-runnable.
- Raw Markdown bodies are not stored.
- Stable IDs are based on note path, source line, and content.
- Duplicate prevention is enforced with unique constraints and note-scoped replace operations.
- Logging is controlled by `LIFEOS_LOG_LEVEL`.
- Phase 4 will add chunking, real embeddings, pgvector search, and context compression.
