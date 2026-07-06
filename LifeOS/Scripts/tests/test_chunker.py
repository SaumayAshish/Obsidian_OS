from __future__ import annotations

from pathlib import Path

from lifeos_sync.chunker import chunk_note
from lifeos_sync.markdown import parse_note


def test_chunk_note_by_heading(tmp_path: Path) -> None:
    path = tmp_path / "Note.md"
    path.write_text("---\ntype: note\n---\n# Title\nSome useful content about goals.\n## Next\nMore content.\n", encoding="utf-8")

    note = parse_note(path, tmp_path)
    chunks = chunk_note(note)

    assert len(chunks) == 2
    assert chunks[0].heading_path == "Title"
    assert chunks[1].heading_path == "Title > Next"

