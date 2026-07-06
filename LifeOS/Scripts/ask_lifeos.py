from __future__ import annotations

import argparse

from lifeos_sync.assistant import answer_question
from lifeos_sync.config import load_settings
from lifeos_sync.db import build_session_factory
from lifeos_sync.embedding_service import build_embedding_service
from lifeos_sync.logging_config import configure_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the local LifeOS assistant through retrieved vault context.")
    parser.add_argument("question")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--token-budget", type=int, default=1200)
    args = parser.parse_args()

    settings = load_settings()
    configure_logging(settings.log_level)
    service = build_embedding_service()
    session_factory = build_session_factory(settings)
    with session_factory() as session:
        print(answer_question(session, settings.vault_path, service, args.question, args.limit, args.token_budget))


if __name__ == "__main__":
    main()

