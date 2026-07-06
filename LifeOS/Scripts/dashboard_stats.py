from __future__ import annotations

import json

from lifeos_sync.analytics import dashboard_stats
from lifeos_sync.config import load_settings
from lifeos_sync.db import build_session_factory


def main() -> None:
    settings = load_settings()
    session_factory = build_session_factory(settings)
    with session_factory() as session:
        print(json.dumps(dashboard_stats(session), indent=2, default=str, sort_keys=True))


if __name__ == "__main__":
    main()

