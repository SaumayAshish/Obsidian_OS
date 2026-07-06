from __future__ import annotations

import json

from lifeos_sync.config import load_settings
from lifeos_sync.db import build_session_factory
from lifeos_sync.validation import issue_counts, validate_database, validate_vault


def main() -> None:
    settings = load_settings()
    vault_issues = validate_vault(settings.vault_path)
    database_issues = []
    try:
        session_factory = build_session_factory(settings)
        with session_factory() as session:
            database_issues = validate_database(session)
    except Exception as exc:
        database_issues.append({"severity": "error", "path": "database", "message": str(exc)})

    issues = [issue.__dict__ for issue in vault_issues]
    issues.extend(issue if isinstance(issue, dict) else issue.__dict__ for issue in database_issues)
    print(json.dumps({"summary": issue_counts(vault_issues), "issues": issues}, indent=2))


if __name__ == "__main__":
    main()
