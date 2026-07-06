from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from .markdown import iter_markdown_files, parse_finance_rows, parse_note, parse_tasks


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    path: str
    message: str


def validate_vault(vault_path: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not vault_path.exists():
        return [ValidationIssue("error", str(vault_path), "Vault path does not exist")]

    for path in iter_markdown_files(vault_path):
        try:
            note = parse_note(path, vault_path)
        except Exception as exc:
            issues.append(ValidationIssue("error", path.as_posix(), f"Could not parse note: {exc}"))
            continue

        note_type = note.frontmatter.get("type")
        if not note_type:
            issues.append(ValidationIssue("warning", note.relative_path, "Missing frontmatter field: type"))

        for task in parse_tasks(note):
            if not task.description:
                issues.append(ValidationIssue("warning", note.relative_path, f"Empty task on line {task.line}"))

        for row in parse_finance_rows(note):
            if row.amount < 0:
                issues.append(ValidationIssue("warning", note.relative_path, f"Negative finance amount on line {row.line}"))
    return issues


def validate_database(session: Session) -> list[ValidationIssue]:
    checks = {
        "duplicate note paths": "SELECT path, count(*) FROM lifeos.notes GROUP BY path HAVING count(*) > 1",
        "duplicate task external ids": "SELECT external_id, count(*) FROM lifeos.tasks GROUP BY external_id HAVING count(*) > 1",
        "duplicate finance external ids": "SELECT external_id, count(*) FROM lifeos.finance_transactions GROUP BY external_id HAVING count(*) > 1",
        "orphan tasks": "SELECT id, count(*) FROM lifeos.tasks WHERE note_id NOT IN (SELECT id FROM lifeos.notes) GROUP BY id",
    }
    issues: list[ValidationIssue] = []
    for label, sql in checks.items():
        rows = session.execute(text(sql)).all()
        for row in rows:
            issues.append(ValidationIssue("error", "database", f"{label}: {row[0]}"))
    return issues


def issue_counts(issues: list[ValidationIssue]) -> dict[str, int]:
    return {
        "errors": sum(1 for issue in issues if issue.severity == "error"),
        "warnings": sum(1 for issue in issues if issue.severity == "warning"),
        "total": len(issues),
    }

