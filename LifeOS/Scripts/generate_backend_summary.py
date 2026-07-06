from __future__ import annotations

from lifeos_sync.config import load_settings
from lifeos_sync.db import build_session_factory
from lifeos_sync.reporting import write_backend_summary


def main() -> None:
    settings = load_settings()
    session_factory = build_session_factory(settings)
    with session_factory() as session:
        target = write_backend_summary(session, settings.vault_path)
    print(target)


if __name__ == "__main__":
    main()

