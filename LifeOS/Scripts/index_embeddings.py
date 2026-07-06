from __future__ import annotations

import argparse
import json

from lifeos_sync.config import load_settings
from lifeos_sync.db import build_session_factory
from lifeos_sync.embedding_service import build_embedding_service
from lifeos_sync.logging_config import configure_logging
from lifeos_sync.vector_index import apply_pgvector_migration, index_vault


def main() -> None:
    parser = argparse.ArgumentParser(description="Build LifeOS chunks and pgvector embeddings.")
    parser.add_argument("--migrate", action="store_true", help="Apply Phase 4 pgvector migration first.")
    args = parser.parse_args()

    settings = load_settings()
    configure_logging(settings.log_level)
    service = build_embedding_service()
    session_factory = build_session_factory(settings)
    with session_factory() as session:
        if args.migrate:
            apply_pgvector_migration(session, settings.vault_path)
        counts = index_vault(session, settings.vault_path, service)
    print(json.dumps(counts, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

