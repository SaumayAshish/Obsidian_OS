from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml


TASK_RE = re.compile(r"^\s*[-*]\s+\[(?P<mark>[ xX])\]\s+(?P<body>.+)$")
TAG_RE = re.compile(r"(?<!\w)#([\w/-]+)")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


@dataclass(frozen=True)
class ParsedNote:
    path: Path
    relative_path: str
    title: str
    frontmatter: dict[str, Any]
    body: str
    lines: list[str]
    content_hash: str
    file_mtime: datetime


@dataclass(frozen=True)
class ParsedTask:
    line: int
    description: str
    done: bool
    due_date: date | None
    scheduled_date: date | None
    completed_at: datetime | None
    priority: str | None
    tags: list[str]
    external_id: str


@dataclass(frozen=True)
class ParsedHabit:
    line: int
    name: str
    category: str | None
    completed: bool


@dataclass(frozen=True)
class ParsedFinanceRow:
    line: int
    tx_date: date
    tx_type: str
    category: str
    merchant: str | None
    amount: float
    currency: str
    note: str | None
    external_id: str


def iter_markdown_files(vault_path: Path) -> list[Path]:
    ignored_parts = {".obsidian", ".trash", "Attachments", "Archive", "Config", "Scripts", "Templates"}
    files: list[Path] = []
    for path in vault_path.rglob("*.md"):
        if path.name.lower() == "readme.md":
            continue
        if ignored_parts.intersection(path.relative_to(vault_path).parts):
            continue
        files.append(path)
    return sorted(files)


def parse_note(path: Path, vault_path: Path) -> ParsedNote:
    text = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text)
    relative_path = path.relative_to(vault_path).as_posix()
    title = str(frontmatter.get("title") or path.stem)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return ParsedNote(
        path=path,
        relative_path=relative_path,
        title=title,
        frontmatter=frontmatter,
        body=body,
        lines=text.splitlines(),
        content_hash=digest,
        file_mtime=mtime,
    )


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    try:
        _, raw_yaml, body = text.split("---", 2)
    except ValueError:
        return {}, text
    data = yaml.safe_load(raw_yaml) or {}
    if not isinstance(data, dict):
        data = {}
    return data, body.lstrip("\n")


def parse_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not value:
        return None
    match = DATE_RE.search(str(value))
    if not match:
        return None
    return date.fromisoformat(match.group(1))


def parse_datetime(value: Any) -> datetime | None:
    parsed = parse_date(value)
    if not parsed:
        return None
    return datetime(parsed.year, parsed.month, parsed.day, tzinfo=timezone.utc)


def parse_number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def normalized_tags(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        raw = [value]
    else:
        raw = list(value)
    return sorted({str(tag).strip().lstrip("#") for tag in raw if str(tag).strip()})


def parse_tasks(note: ParsedNote) -> list[ParsedTask]:
    tasks: list[ParsedTask] = []
    for line_no, line in enumerate(note.lines, start=1):
        match = TASK_RE.match(line)
        if not match:
            continue
        body = match.group("body").strip()
        external_id = stable_id(note.relative_path, line_no, body)
        tasks.append(
            ParsedTask(
                line=line_no,
                description=clean_task_description(body),
                done=match.group("mark").lower() == "x",
                due_date=parse_marker_date(body, "📅") or parse_label_date(body, "due"),
                scheduled_date=parse_marker_date(body, "⏳") or parse_label_date(body, "scheduled"),
                completed_at=parse_completed_at(body),
                priority=parse_priority(body),
                tags=sorted({tag for tag in TAG_RE.findall(body) if not tag.startswith("habit") and tag != "task"}),
                external_id=external_id,
            )
        )
    return tasks


def parse_habits(note: ParsedNote) -> list[ParsedHabit]:
    habits: list[ParsedHabit] = []
    for line_no, line in enumerate(note.lines, start=1):
        match = TASK_RE.match(line)
        if not match or "#habit" not in line:
            continue
        tags = TAG_RE.findall(line)
        habit_tag = next((tag for tag in tags if tag.startswith("habit")), "habit")
        category = habit_tag.split("/", 1)[1] if "/" in habit_tag else None
        name = clean_task_description(match.group("body")).replace("#habit", "").strip()
        habits.append(ParsedHabit(line=line_no, name=name, category=category, completed=match.group("mark").lower() == "x"))
    return habits


def parse_finance_rows(note: ParsedNote) -> list[ParsedFinanceRow]:
    rows: list[ParsedFinanceRow] = []
    in_table = False
    headers: list[str] = []
    for line_no, line in enumerate(note.lines, start=1):
        if line.strip().lower().startswith("| date |"):
            headers = [cell.strip().lower() for cell in split_table_row(line)]
            in_table = "amount" in headers and "category" in headers
            continue
        if not in_table:
            continue
        if re.match(r"^\|\s*-+", line):
            continue
        if not line.strip().startswith("|"):
            in_table = False
            continue
        cells = split_table_row(line)
        row = {headers[i]: cells[i].strip() for i in range(min(len(headers), len(cells)))}
        amount = parse_number(row.get("amount"))
        tx_date = parse_date(row.get("date"))
        if amount is None or not tx_date or amount == 0:
            continue
        tx_type = (row.get("type") or "expense").lower()
        category = row.get("category") or "Uncategorized"
        merchant = row.get("merchant") or None
        currency = row.get("currency") or str(note.frontmatter.get("currency") or "INR")
        note_text = row.get("note") or None
        external_id = stable_id(note.relative_path, line_no, "|".join(cells))
        rows.append(
            ParsedFinanceRow(
                line=line_no,
                tx_date=tx_date,
                tx_type=tx_type,
                category=category,
                merchant=merchant,
                amount=amount,
                currency=currency[:3].upper(),
                note=note_text,
                external_id=external_id,
            )
        )
    return rows


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_marker_date(body: str, marker: str) -> date | None:
    marker_index = body.find(marker)
    if marker_index < 0:
        return None
    return parse_date(body[marker_index:])


def parse_completed_at(body: str) -> datetime | None:
    for marker in ("✅", "done:"):
        marker_index = body.find(marker)
        if marker_index >= 0:
            return parse_datetime(body[marker_index:])
    return None


def parse_label_date(body: str, label: str) -> date | None:
    match = re.search(rf"\b{re.escape(label)}:\s*(\d{{4}}-\d{{2}}-\d{{2}})", body, flags=re.IGNORECASE)
    if not match:
        return None
    return date.fromisoformat(match.group(1))


def parse_priority(body: str) -> str | None:
    if "🔺" in body:
        return "high"
    if "⏫" in body:
        return "medium"
    if "🔽" in body:
        return "low"
    return None


def clean_task_description(body: str) -> str:
    cleaned = re.sub(r"[📅⏳✅]\s*\d{4}-\d{2}-\d{2}", "", body)
    cleaned = re.sub(r"\b(?:due|scheduled|done):\s*\d{4}-\d{2}-\d{2}", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[🔺⏫🔽]", "", cleaned)
    return " ".join(cleaned.split())


def stable_id(*parts: object) -> str:
    raw = "::".join(str(part) for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
