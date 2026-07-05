from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .markdown import (
    ParsedFinanceRow,
    ParsedHabit,
    ParsedNote,
    iter_markdown_files,
    normalized_tags,
    parse_date,
    parse_finance_rows,
    parse_habits,
    parse_note,
    parse_number,
    parse_tasks,
)
from .models import DailyMetric, FinanceTransaction, Goal, HabitDefinition, HabitLog, Note, SyncRun, Task

logger = logging.getLogger(__name__)


def sync_vault(session: Session, vault_path: Path) -> dict[str, int]:
    run = SyncRun(run_type="markdown-sync", status="running")
    session.add(run)
    session.flush()

    counts = {"files": 0, "notes": 0, "tasks": 0, "habits": 0, "finance": 0, "metrics": 0, "goals": 0}
    try:
        for path in iter_markdown_files(vault_path):
            note = parse_note(path, vault_path)
            logger.debug("Syncing %s", note.relative_path)
            db_note = upsert_note(session, note)
            counts["files"] += 1
            counts["notes"] += 1
            counts["tasks"] += sync_tasks(session, db_note.id, note)
            counts["habits"] += sync_habits(session, db_note.id, note)
            counts["finance"] += sync_finance(session, db_note.id, note)
            counts["metrics"] += sync_daily_metrics(session, db_note.id, note)
            counts["goals"] += sync_goal(session, db_note.id, note)

        run.status = "ok"
        run.finished_at = datetime.now(timezone.utc)
        run.files_scanned = counts["files"]
        run.rows_changed = sum(value for key, value in counts.items() if key != "files")
        run.sync_metadata = counts
        session.commit()
        logger.info("Sync completed: %s", counts)
    except Exception as exc:
        session.rollback()
        logger.exception("Sync failed")
        failed_run = SyncRun(
            run_type="markdown-sync",
            status="error",
            finished_at=datetime.now(timezone.utc),
            files_scanned=counts["files"],
            rows_changed=sum(value for key, value in counts.items() if key != "files"),
            error=str(exc),
            sync_metadata=counts,
        )
        session.add(failed_run)
        session.commit()
        raise
    return counts


def upsert_note(session: Session, note: ParsedNote) -> Note:
    frontmatter = dict(note.frontmatter)
    payload = {
        "path": note.relative_path,
        "title": note.title,
        "note_type": str(frontmatter.get("type") or "note"),
        "status": str(frontmatter.get("status") or "active"),
        "tags": normalized_tags(frontmatter.get("tags")),
        "created_at": parse_datetime_field(frontmatter.get("created")),
        "updated_at": parse_datetime_field(frontmatter.get("updated")),
        "file_mtime": note.file_mtime,
        "content_hash": note.content_hash,
        "metadata": json_safe(frontmatter),
    }
    table = Note.__table__
    stmt = insert(table).values(**payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=[table.c.path],
        set_={key: getattr(stmt.excluded, key) for key in payload if key != "path"},
    ).returning(table.c.id)
    note_id = session.execute(stmt).scalar_one()
    return session.get(Note, note_id)


def sync_tasks(session: Session, note_id: int, note: ParsedNote) -> int:
    parsed = parse_tasks(note)
    session.execute(delete(Task).where(Task.note_id == note_id))
    for task in parsed:
        session.add(
            Task(
                note_id=note_id,
                source_path=note.relative_path,
                source_line=task.line,
                description=task.description,
                status="done" if task.done else "open",
                priority=task.priority,
                due_date=task.due_date,
                scheduled_date=task.scheduled_date,
                completed_at=task.completed_at,
                project=str(note.frontmatter.get("project") or note.frontmatter.get("area") or "") or None,
                goal=str(note.frontmatter.get("goal") or "") or None,
                tags=task.tags,
                external_id=task.external_id,
            )
        )
    return len(parsed)


def sync_habits(session: Session, note_id: int, note: ParsedNote) -> int:
    log_date = date_for_note(note)
    if not log_date:
        return 0
    parsed = parse_habits(note)
    existing_habits = {habit.name: habit for habit in session.scalars(select(HabitDefinition)).all()}
    count = 0
    for habit in parsed:
        definition = existing_habits.get(habit.name)
        if not definition:
            definition = HabitDefinition(name=habit.name, category=habit.category)
            session.add(definition)
            session.flush()
            existing_habits[habit.name] = definition
        upsert_habit_log(session, definition.id, note_id, log_date, habit)
        count += 1
    return count


def upsert_habit_log(session: Session, habit_id: int, note_id: int, log_date: Any, habit: ParsedHabit) -> None:
    payload = {
        "habit_id": habit_id,
        "note_id": note_id,
        "log_date": log_date,
        "completed": habit.completed,
        "source_line": habit.line,
    }
    stmt = insert(HabitLog).values(**payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=[HabitLog.habit_id, HabitLog.log_date],
        set_={key: payload[key] for key in payload if key not in {"habit_id", "log_date"}},
    )
    session.execute(stmt)


def sync_finance(session: Session, note_id: int, note: ParsedNote) -> int:
    parsed = parse_finance_rows(note)
    session.execute(delete(FinanceTransaction).where(FinanceTransaction.note_id == note_id))
    for row in parsed:
        session.add(finance_model(note_id, row))
    return len(parsed)


def finance_model(note_id: int, row: ParsedFinanceRow) -> FinanceTransaction:
    return FinanceTransaction(
        note_id=note_id,
        tx_date=row.tx_date,
        category=row.category,
        merchant=row.merchant,
        description=row.note,
        amount=Decimal(str(row.amount)),
        currency=row.currency,
        tx_type=row.tx_type if row.tx_type in {"expense", "income", "transfer", "investment", "saving"} else "expense",
        tags=[],
        source_line=row.line,
        external_id=row.external_id,
    )


def sync_daily_metrics(session: Session, note_id: int, note: ParsedNote) -> int:
    metric_date = date_for_note(note)
    if not metric_date or note.frontmatter.get("type") != "daily":
        return 0

    tasks = parse_tasks(note)
    habits = parse_habits(note)
    finance_rows = parse_finance_rows(note)
    expense_total = sum(row.amount for row in finance_rows if row.tx_type == "expense")
    if not expense_total:
        expense_total = parse_number(note.frontmatter.get("expense_total")) or 0

    payload = {
        "metric_date": metric_date,
        "mood": int_or_none(note.frontmatter.get("mood")),
        "productivity": int_or_none(note.frontmatter.get("productivity")),
        "sleep_hours": decimal_or_none(note.frontmatter.get("sleep")),
        "tasks_opened": len(tasks),
        "tasks_completed": sum(1 for task in tasks if task.done),
        "habits_completed": sum(1 for habit in habits if habit.completed),
        "habits_total": len(habits),
        "expense_total": Decimal(str(expense_total)),
        "learning_minutes": int_or_zero(note.frontmatter.get("learning_minutes")),
        "metadata": {"note_id": note_id, "path": note.relative_path},
    }
    table = DailyMetric.__table__
    stmt = insert(table).values(**payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=[table.c.metric_date],
        set_={key: getattr(stmt.excluded, key) for key in payload if key != "metric_date"},
    )
    session.execute(stmt)
    return 1


def sync_goal(session: Session, note_id: int, note: ParsedNote) -> int:
    if note.frontmatter.get("type") != "goal":
        return 0
    session.execute(delete(Goal).where(Goal.note_id == note_id))
    session.add(
        Goal(
            note_id=note_id,
            title=note.title,
            level=str(note.frontmatter.get("level") or "quarterly"),
            status=str(note.frontmatter.get("status") or "active"),
            start_date=parse_date(note.frontmatter.get("start_date")),
            target_date=parse_date(note.frontmatter.get("target_date")),
            progress=Decimal(str(parse_number(note.frontmatter.get("progress")) or 0)),
            metric_name=blank_to_none(note.frontmatter.get("metric_name")),
            metric_current=decimal_or_none(note.frontmatter.get("metric_current")),
            metric_target=decimal_or_none(note.frontmatter.get("metric_target")),
        )
    )
    return 1


def date_for_note(note: ParsedNote) -> Any:
    return parse_date(note.frontmatter.get("date")) or parse_date(note.path.stem)


def parse_datetime_field(value: Any) -> datetime | None:
    parsed = parse_date(value)
    if not parsed:
        return None
    return datetime(parsed.year, parsed.month, parsed.day, tzinfo=timezone.utc)


def json_safe(data: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = value
        elif isinstance(value, (list, tuple)):
            safe[key] = [str(item) for item in value]
        else:
            safe[key] = str(value)
    return safe


def int_or_none(value: Any) -> int | None:
    number = parse_number(value)
    return int(number) if number is not None else None


def int_or_zero(value: Any) -> int:
    return int_or_none(value) or 0


def decimal_or_none(value: Any) -> Decimal | None:
    number = parse_number(value)
    return Decimal(str(number)) if number is not None else None


def blank_to_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)
