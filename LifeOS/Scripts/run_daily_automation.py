from __future__ import annotations

import json

from lifeos_sync.config import load_settings
from lifeos_sync.db import build_session_factory
from lifeos_sync.embedding_service import build_embedding_service
from lifeos_sync.reporting import write_backend_summary
from lifeos_sync.sync import sync_vault
from lifeos_sync.vector_index import index_vault


def main() -> None:
    settings = load_settings()
    session_factory = build_session_factory(settings)
    service = build_embedding_service()
    with session_factory() as session:
        sync_counts = sync_vault(session, settings.vault_path)
        index_counts = index_vault(session, settings.vault_path, service)
        summary_path = write_backend_summary(session, settings.vault_path)
    print(json.dumps({"sync": sync_counts, "index": index_counts, "summary": str(summary_path)}, indent=2))


if __name__ == "__main__":
    main()

