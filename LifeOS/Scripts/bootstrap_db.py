"""
Bootstrap LifeOS database with minimal sample data for CI and local dev.

Idempotent: inserts use ON CONFLICT DO NOTHING where appropriate.
"""
import os
from textwrap import dedent
import psycopg
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = (
    os.environ.get('DATABASE_URL')
    or os.environ.get('PGDATABASE_URL')
    or os.environ.get('DATABASE')
)
if not DATABASE_URL:
    host = os.environ.get('POSTGRES_HOST', 'localhost')
    user = os.environ.get('POSTGRES_USER', 'lifeos')
    password = os.environ.get('POSTGRES_PASSWORD')
    db = os.environ.get('POSTGRES_DB', 'lifeos')
    if not password:
        raise SystemExit('DATABASE_URL or POSTGRES_PASSWORD required in environment')
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:5432/{db}"

print('Connecting to', DATABASE_URL)

with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
    with conn.cursor() as cur:
        # Create a sample note
        cur.execute(
            dedent(
                """
                INSERT INTO lifeos.notes (
                    path, title, note_type, status, tags, created_at,
                    updated_at, file_mtime, content_hash, metadata
                )
                VALUES (%s, %s, %s, %s, %s, now(), now(), now(), %s, %s)
                ON CONFLICT (path) DO UPDATE SET title = EXCLUDED.title
                RETURNING id
                """
            ),
            (
                "sample/sample-note.md",
                "Sample Note",
                "note",
                "active",
                ["sample"],
                "samplehash123",
                "{}",
            ),
        )
        note_id = cur.fetchone()[0]

        # Insert a sample task linked to the note
        cur.execute(
            dedent(
                """
                INSERT INTO lifeos.tasks (
                    note_id, source_path, source_line, description, status,
                    priority, external_id, synced_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, now())
                ON CONFLICT (external_id) DO NOTHING
                RETURNING id
                """
            ),
            (
                note_id,
                "sample/sample-note.md",
                10,
                "Sample task for CI",
                "open",
                "medium",
                "sample-task-1",
            ),
        )
        _ = cur.fetchone()

        # Insert a sample goal
        cur.execute(
            dedent(
                """
                INSERT INTO lifeos.goals (
                    note_id, title, level, status, start_date,
                    target_date, progress
                )
                VALUES (
                    %s, %s, %s, %s, current_date,
                    current_date + interval '30 days', 0
                )
                ON CONFLICT DO NOTHING
                RETURNING id
                """
            ),
            (note_id, "Sample Goal", "weekly", "active"),
        )
        _ = cur.fetchone()

        # Insert a sample habit definition and log
        cur.execute(
            dedent(
                """
                INSERT INTO lifeos.habit_definitions (
                    name, category, target_frequency, active
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
                """
            ),
            ("sample-habit", "health", "daily", True),
        )
        habit_row = cur.fetchone()
        habit_id = habit_row[0] if habit_row else None
        if habit_id:
            cur.execute(
                dedent(
                    """
                    INSERT INTO lifeos.habit_logs (
                        habit_id, note_id, log_date, completed
                    )
                    VALUES (%s, %s, current_date, true)
                    ON CONFLICT (habit_id, log_date) DO NOTHING
                    """
                ),
                (habit_id, note_id),
            )

        # Insert a sample finance transaction
        cur.execute(
            dedent(
                """
                INSERT INTO lifeos.finance_transactions (
                    note_id, tx_date, account, category, merchant,
                    description, amount, currency, tx_type, external_id
                )
                VALUES (%s, current_date, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (external_id) DO NOTHING
                """
            ),
            (note_id, "card", "test", "ACME", "CI sample", 9.99, "USD",
             "expense", "sample-tx-1"),
        )

print('Bootstrap complete')
