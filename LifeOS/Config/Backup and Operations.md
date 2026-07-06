# Backup and Operations

## Daily Command

```powershell
python Scripts/run_daily_automation.py
```

This runs:

- Markdown to PostgreSQL sync
- Chunk and embedding indexing
- Backend summary generation

## Backup

```powershell
python Scripts/backup_lifeos.py
```

This writes vault and PostgreSQL backups into `Archive/Backups/`.

If `pg_dump` is unavailable:

```powershell
python Scripts/backup_lifeos.py --skip-db
```

## Validation

```powershell
python Scripts/sync_vault.py --validate-only
pytest Scripts/tests
```

## pgvector Upgrade

Install pgvector on the PostgreSQL server, then run:

```powershell
python Scripts/index_embeddings.py --migrate
```

Until then, LifeOS uses text-backed embedding retrieval.

