# LifeOS Architecture

## System Boundary

LifeOS runs inside an Obsidian vault. Obsidian is the primary UI. Python automation and PostgreSQL support the vault without replacing it.

```text
Obsidian Vault
  -> Markdown notes
  -> Dataview / Tasks / Tracker dashboards
  -> Python sync scripts
  -> PostgreSQL structured backend
  -> text-backed embedding store in Phase 3
  -> pgvector semantic index in Phase 4
  -> Ollama local LLM
```

## Core Layers

### 1. Interface Layer

- Obsidian notes, dashboards, backlinks, templates, and plugin views.
- Users interact with Markdown files directly.
- Dashboards use Dataview, Tasks, Tracker, and Kanban queries.

### 2. Knowledge Layer

- Markdown remains the human-readable knowledge store.
- Notes use YAML frontmatter for stable metadata.
- Links and tags provide lightweight graph structure.
- Summary notes are used to reduce AI context size.

### 3. Structured Data Layer

- PostgreSQL stores normalized records derived from Markdown.
- Tables cover tasks, habits, finance, analytics, embeddings, and AI memory metadata.
- Raw note content is never persisted in PostgreSQL.

### 4. Automation Layer

- Python scripts parse Markdown, extract metadata, sync structured rows, generate analytics, and build vector indexes.
- Scripts are modular and environment-driven.
- Scheduled execution can use OS task scheduler, cron, or manual Obsidian commands.

### 5. AI/RAG Layer

```text
Markdown notes
  -> chunking
  -> local embeddings
  -> text-backed embedding storage
  -> pgvector in Phase 4
  -> filtered semantic search
  -> context compression
  -> Ollama response
```

The AI pipeline retrieves only relevant chunks. It avoids sending complete notes to the model.

## Token Efficiency Strategy

- Store short summaries in `AI Memory/` for long-running context.
- Retrieve by semantic similarity plus metadata filters.
- Limit chunks by score, recency, domain, and note type.
- Compress retrieved chunks before final LLM calls.
- Prefer IDs, note paths, and headings over repeated full text.

## Data Ownership

| Data Type | Source of Truth | PostgreSQL Use |
|---|---|---|
| Notes | Markdown | Metadata and embeddings only |
| Tasks | Markdown tasks | Structured sync and analytics |
| Habits | Daily notes | Completion/streak analytics |
| Finance | Finance notes / daily expenses | Reports and aggregates |
| Goals | Goal notes | Progress rollups |
| AI memory | Markdown summaries | Metadata and retrieval index |

## Phase Roadmap

1. Foundation: architecture, structure, plugins, database schema.
2. Obsidian UI: dashboards, Dataview queries, task system, templates.
3. Sync: Markdown parser, SQLAlchemy models, PostgreSQL sync.
4. Retrieval: chunking, embeddings, pgvector search, compressed context.
5. Assistant: local AI workflows, memory updates, retrieval commands.
