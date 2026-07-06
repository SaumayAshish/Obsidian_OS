from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from .markdown import ParsedNote


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")


@dataclass(frozen=True)
class NoteChunkData:
    chunk_index: int
    heading_path: str | None
    text: str
    chunk_hash: str
    token_estimate: int
    summary: str
    keywords: list[str]
    start_line: int
    end_line: int


def chunk_note(note: ParsedNote, max_tokens: int = 350) -> list[NoteChunkData]:
    chunks: list[NoteChunkData] = []
    heading_stack: list[str] = []
    current_lines: list[tuple[int, str]] = []
    current_heading: str | None = None

    for line_no, line in enumerate(note.lines, start=1):
        if line_no <= frontmatter_line_count(note.lines):
            continue

        heading = HEADING_RE.match(line)
        if heading:
            flush_chunk(chunks, current_lines, current_heading, max_tokens)
            current_lines = []
            level = len(heading.group(1))
            heading_stack = heading_stack[: level - 1]
            heading_stack.append(heading.group(2).strip())
            current_heading = " > ".join(heading_stack)
            continue

        if not line.strip() and not current_lines:
            continue
        current_lines.append((line_no, line))
        if estimate_tokens("\n".join(text for _, text in current_lines)) >= max_tokens:
            flush_chunk(chunks, current_lines, current_heading, max_tokens)
            current_lines = []

    flush_chunk(chunks, current_lines, current_heading, max_tokens)
    return [chunk for chunk in chunks if chunk.text.strip()]


def flush_chunk(
    chunks: list[NoteChunkData],
    lines: list[tuple[int, str]],
    heading_path: str | None,
    max_tokens: int,
) -> None:
    if not lines:
        return
    text = "\n".join(line for _, line in lines).strip()
    if not text:
        return

    start_line = lines[0][0]
    remaining = text
    while remaining:
        part, remaining = split_to_token_limit(remaining, max_tokens)
        digest = hashlib.sha256(part.encode("utf-8")).hexdigest()
        chunks.append(
            NoteChunkData(
                chunk_index=len(chunks),
                heading_path=heading_path,
                text=part,
                chunk_hash=digest,
                token_estimate=estimate_tokens(part),
                summary=summarize(part),
                keywords=extract_keywords(part),
                start_line=start_line,
                end_line=lines[-1][0],
            )
        )


def split_to_token_limit(text: str, max_tokens: int) -> tuple[str, str]:
    words = text.split()
    max_words = max(50, int(max_tokens * 0.75))
    if len(words) <= max_words:
        return text.strip(), ""
    return " ".join(words[:max_words]).strip(), " ".join(words[max_words:]).strip()


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text.split()) / 0.75))


def summarize(text: str, max_chars: int = 420) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rsplit(" ", 1)[0] + "..."


def extract_keywords(text: str, limit: int = 12) -> list[str]:
    stop = {"the", "and", "for", "with", "that", "this", "from", "into", "your", "you", "are", "use"}
    counts: dict[str, int] = {}
    for word in WORD_RE.findall(text.lower()):
        if word in stop:
            continue
        counts[word] = counts.get(word, 0) + 1
    return [word for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def frontmatter_line_count(lines: list[str]) -> int:
    if not lines or lines[0].strip() != "---":
        return 0
    for index, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return index
    return 0

