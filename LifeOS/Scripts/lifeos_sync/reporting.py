from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from .dashboard_backend import backend_dashboard


def write_backend_summary(session: Session, vault_path: Path) -> Path:
    data = backend_dashboard(session)
    target = vault_path / "Dashboard" / "Backend Summary.md"
    target.write_text(render_backend_summary(data), encoding="utf-8")
    return target


def render_backend_summary(data: dict[str, object]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    tasks = data.get("tasks", {})
    habits = data.get("habits", {})
    finance = data.get("finance", {})
    goals = data.get("goals", {})
    productivity = data.get("productivity", {})
    return f"""---
type: dashboard
status: active
created: {datetime.now().date()}
updated: {datetime.now().date()}
tags: [dashboard, backend]
---

# Backend Summary

Generated: {now}

## Tasks

| Metric | Value |
|---|---:|
| Open | {field(tasks, "open")} |
| Due today | {field(tasks, "due_today")} |
| Overdue | {field(tasks, "overdue")} |
| Completed 7d | {field(tasks, "completed_7d")} |

## Goals

| Metric | Value |
|---|---:|
| Active | {field(goals, "active")} |
| Average progress | {field(goals, "avg_progress")} |
| Due in 30d | {field(goals, "due_30d")} |

## Habits

| Metric | Value |
|---|---:|
| Active | {field(habits, "active")} |
| Completed today | {field(habits, "completed_today")} |
| Completion 7d | {field(habits, "completion_7d")} |

## Finance

| Metric | Value |
|---|---:|
| Expense today | {field(finance, "expense_today")} |
| Expense month | {field(finance, "expense_month")} |
| Income month | {field(finance, "income_month")} |

## Productivity

| Metric | Value |
|---|---:|
| Avg mood 7d | {field(productivity, "avg_mood_7d")} |
| Avg productivity 7d | {field(productivity, "avg_productivity_7d")} |
| Learning minutes 7d | {field(productivity, "learning_minutes_7d")} |
"""


def field(data: object, key: str) -> object:
    return data.get(key, "") if isinstance(data, dict) else ""

