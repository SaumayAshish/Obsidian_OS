from __future__ import annotations

import argparse
import shutil
import subprocess
from datetime import datetime

from lifeos_sync.config import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Create LifeOS vault and PostgreSQL backups.")
    parser.add_argument("--skip-db", action="store_true")
    args = parser.parse_args()

    settings = load_settings()
    backup_root = settings.vault_path / "Archive" / "Backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    vault_zip = backup_root / f"vault-{stamp}.zip"
    shutil.make_archive(str(vault_zip.with_suffix("")), "zip", settings.vault_path)
    print(vault_zip)

    if not args.skip_db:
        sql_file = backup_root / f"postgres-{stamp}.sql"
        subprocess.run(["pg_dump", pg_dump_url(settings.database_url), "-f", str(sql_file)], check=True)
        print(sql_file)


def pg_dump_url(database_url: str) -> str:
    return database_url.replace("postgresql+psycopg://", "postgresql://", 1)


if __name__ == "__main__":
    main()
