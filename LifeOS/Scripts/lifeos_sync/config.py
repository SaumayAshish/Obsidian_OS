from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    vault_path: Path
    database_url: str
    schema: str = "lifeos"
    log_level: str = "INFO"


def load_settings() -> Settings:
    script_root = Path(__file__).resolve().parents[1]
    load_dotenv(script_root / ".env")

    vault_path = Path(os.getenv("LIFEOS_VAULT_PATH") or os.getenv("VAULT_PATH", "../")).expanduser()
    if not vault_path.is_absolute():
        vault_path = (script_root / vault_path).resolve()

    database_url = normalize_database_url(os.getenv("DATABASE_URL"))
    if not database_url:
        raise RuntimeError("DATABASE_URL is required. Copy .env.example to .env and edit it.")

    return Settings(
        vault_path=vault_path,
        database_url=database_url,
        schema=os.getenv("LIFEOS_SCHEMA", "lifeos"),
        log_level=os.getenv("LIFEOS_LOG_LEVEL", "INFO"),
    )


def normalize_database_url(value: str | None) -> str | None:
    if not value:
        return None
    # Support the user-friendly but technically invalid form:
    # postgresql+psycopg://postgres:Caesar@3026@localhost:5432/lifeos
    if value.count("@") > 1 and "://" in value:
        scheme, rest = value.split("://", 1)
        userinfo, hostinfo = rest.rsplit("@", 1)
        if ":" in userinfo:
            user, password = userinfo.split(":", 1)
            return f"{scheme}://{user}:{quote(password, safe='')}@{hostinfo}"
    return value
