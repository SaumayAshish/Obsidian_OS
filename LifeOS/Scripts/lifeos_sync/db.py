from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .config import Settings
from .models import Base


def build_session_factory(settings: Settings) -> sessionmaker[Session]:
    engine = create_engine(
        settings.database_url,
        future=True,
        connect_args={"options": f"-csearch_path={settings.schema},public"},
    )
    with engine.begin() as conn:
        conn.execute(text(f"SET search_path TO {safe_identifier(settings.schema)}, public"))
    return sessionmaker(engine, expire_on_commit=False, future=True)


def create_tables(settings: Settings) -> None:
    engine = create_engine(settings.database_url, future=True)
    with engine.begin() as conn:
        schema_file = settings.vault_path / "Config" / "database" / "schema.sql"
        if schema_file.exists():
            conn.exec_driver_sql(schema_file.read_text(encoding="utf-8"))
        else:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {safe_identifier(settings.schema)}"))
            conn.execute(text(f"SET search_path TO {safe_identifier(settings.schema)}, public"))
            Base.metadata.create_all(conn)


def safe_identifier(value: str) -> str:
    if not value.replace("_", "").isalnum():
        raise ValueError(f"Unsafe SQL identifier: {value}")
    return value
