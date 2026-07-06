from __future__ import annotations

from pathlib import Path

from lifeos_sync.markdown import parse_note, parse_tasks


def test_parse_task_labels(tmp_path: Path) -> None:
    vault = tmp_path
    note = vault / "Daily Notes"
    note.mkdir()
    path = note / "2026-05-13.md"
    path.write_text("---\ntype: daily\ntags: [daily]\n---\n- [ ] #task Finish brief due: 2026-05-14\n", encoding="utf-8")

    parsed = parse_note(path, vault)
    tasks = parse_tasks(parsed)

    assert len(tasks) == 1
    assert tasks[0].description == "#task Finish brief"
    assert str(tasks[0].due_date) == "2026-05-14"

