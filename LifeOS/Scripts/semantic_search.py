from __future__ import annotations

import argparse
import json

from lifeos_sync.config import load_settings
from lifeos_sync.db import build_session_factory
from lifeos_sync.embedding_service import build_embedding_service
from lifeos_sync.retrieval import compressed_context, semantic_search


def main() -> None:
    parser = argparse.ArgumentParser(description="Search LifeOS with pgvector semantic retrieval.")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--note-type")
    parser.add_argument("--context", action="store_true", help="Print compressed RAG context instead of JSON.")
    args = parser.parse_args()

    settings = load_settings()
    service = build_embedding_service()
    session_factory = build_session_factory(settings)
    with session_factory() as session:
        results = semantic_search(session, settings.vault_path, service, args.query, args.limit, args.note_type)

    if args.context:
        print(compressed_context(results))
    else:
        print(json.dumps([result.__dict__ for result in results], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

