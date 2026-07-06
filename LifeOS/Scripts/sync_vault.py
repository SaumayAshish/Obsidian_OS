from __future__ import annotations

import argparse
import json
import logging

from lifeos_sync.config import load_settings
from lifeos_sync.db import build_session_factory, create_tables
from lifeos_sync.logging_config import configure_logging
from lifeos_sync.sync import sync_vault
from lifeos_sync.validation import issue_counts, validate_database, validate_vault


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync LifeOS Markdown into PostgreSQL structured tables.")
    parser.add_argument("--init-db", action="store_true", help="Create tables from SQLAlchemy metadata.")
    parser.add_argument("--validate-only", action="store_true", help="Validate the vault and database without syncing.")
    parser.add_argument("--skip-db-validation", action="store_true", help="Validate only Markdown files.")
    args = parser.parse_args()

    settings = load_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    vault_issues = validate_vault(settings.vault_path)
    if any(issue.severity == "error" for issue in vault_issues):
        print(json.dumps({"vault_validation": issue_counts(vault_issues), "issues": [issue.__dict__ for issue in vault_issues]}, indent=2))
        raise SystemExit(1)

    if args.init_db:
        create_tables(settings)

    session_factory = build_session_factory(settings)
    with session_factory() as session:
        db_issues = [] if args.skip_db_validation else validate_database(session)
        if args.validate_only:
            result = {"vault_validation": issue_counts(vault_issues), "database_validation": issue_counts(db_issues)}
        else:
            logger.info("Starting sync for vault: %s", settings.vault_path)
            counts = sync_vault(session, settings.vault_path)
            post_issues = [] if args.skip_db_validation else validate_database(session)
            result = {
                "sync": counts,
                "vault_validation": issue_counts(vault_issues),
                "database_validation": issue_counts(post_issues),
            }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
