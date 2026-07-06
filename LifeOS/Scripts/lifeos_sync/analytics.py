from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def dashboard_stats(session: Session) -> dict[str, object]:
    return {
        "open_tasks": scalar(session, "SELECT count(*) FROM lifeos.tasks WHERE status <> 'done'"),
        "overdue_tasks": scalar(
            session,
            "SELECT count(*) FROM lifeos.tasks WHERE status <> 'done' AND due_date < current_date",
        ),
        "active_goals": scalar(session, "SELECT count(*) FROM lifeos.goals WHERE status = 'active'"),
        "month_expenses": scalar(
            session,
            """
            SELECT coalesce(sum(amount), 0)
            FROM lifeos.finance_transactions
            WHERE tx_type = 'expense'
              AND tx_date >= date_trunc('month', current_date)
            """,
        ),
        "habit_7d_completion": scalar(
            session,
            """
            SELECT coalesce(round(avg(completion_rate), 2), 0)
            FROM lifeos.habit_completion_daily
            WHERE log_date >= current_date - interval '7 days'
            """,
        ),
    }


def scalar(session: Session, sql: str) -> object:
    return session.execute(text(sql)).scalar_one()

