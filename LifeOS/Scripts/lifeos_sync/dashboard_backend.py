from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def backend_dashboard(session: Session) -> dict[str, object]:
    return {
        "tasks": task_stats(session),
        "habits": habit_stats(session),
        "finance": finance_stats(session),
        "goals": goal_stats(session),
        "productivity": productivity_stats(session),
    }


def task_stats(session: Session) -> dict[str, object]:
    return {
        "open": scalar(session, "SELECT count(*) FROM lifeos.tasks WHERE status <> 'done'"),
        "due_today": scalar(session, "SELECT count(*) FROM lifeos.tasks WHERE status <> 'done' AND due_date = current_date"),
        "overdue": scalar(session, "SELECT count(*) FROM lifeos.tasks WHERE status <> 'done' AND due_date < current_date"),
        "completed_7d": scalar(session, "SELECT count(*) FROM lifeos.tasks WHERE status = 'done' AND completed_at >= now() - interval '7 days'"),
    }


def habit_stats(session: Session) -> dict[str, object]:
    return {
        "active": scalar(session, "SELECT count(*) FROM lifeos.habit_definitions WHERE active"),
        "completion_7d": scalar(
            session,
            "SELECT coalesce(round(avg(completion_rate), 2), 0) FROM lifeos.habit_completion_daily WHERE log_date >= current_date - interval '7 days'",
        ),
        "completed_today": scalar(session, "SELECT count(*) FROM lifeos.habit_logs WHERE completed AND log_date = current_date"),
    }


def finance_stats(session: Session) -> dict[str, object]:
    return {
        "expense_today": scalar(
            session,
            "SELECT coalesce(sum(amount), 0) FROM lifeos.finance_transactions WHERE tx_type = 'expense' AND tx_date = current_date",
        ),
        "expense_month": scalar(
            session,
            "SELECT coalesce(sum(amount), 0) FROM lifeos.finance_transactions WHERE tx_type = 'expense' AND tx_date >= date_trunc('month', current_date)",
        ),
        "income_month": scalar(
            session,
            "SELECT coalesce(sum(amount), 0) FROM lifeos.finance_transactions WHERE tx_type = 'income' AND tx_date >= date_trunc('month', current_date)",
        ),
    }


def goal_stats(session: Session) -> dict[str, object]:
    return {
        "active": scalar(session, "SELECT count(*) FROM lifeos.goals WHERE status = 'active'"),
        "avg_progress": scalar(session, "SELECT coalesce(round(avg(progress), 2), 0) FROM lifeos.goals WHERE status = 'active'"),
        "due_30d": scalar(session, "SELECT count(*) FROM lifeos.goals WHERE status = 'active' AND target_date <= current_date + interval '30 days'"),
    }


def productivity_stats(session: Session) -> dict[str, object]:
    return {
        "avg_mood_7d": scalar(session, "SELECT coalesce(round(avg(mood), 2), 0) FROM lifeos.daily_metrics WHERE metric_date >= current_date - interval '7 days'"),
        "avg_productivity_7d": scalar(session, "SELECT coalesce(round(avg(productivity), 2), 0) FROM lifeos.daily_metrics WHERE metric_date >= current_date - interval '7 days'"),
        "learning_minutes_7d": scalar(session, "SELECT coalesce(sum(learning_minutes), 0) FROM lifeos.daily_metrics WHERE metric_date >= current_date - interval '7 days'"),
    }


def scalar(session: Session, sql: str) -> object:
    return session.execute(text(sql)).scalar_one()
