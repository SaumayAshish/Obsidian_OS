# Phase 4 Semantic Retrieval

## Purpose

Phase 4 adds local semantic retrieval while preserving the Phase 3 rule that raw Markdown bodies are not stored in PostgreSQL.

## Flow

```text
Markdown notes
  -> chunker reads local files
  -> note_chunks stores metadata, line ranges, summaries
  -> sentence-transformers creates local embeddings
  -> embeddings stores text fallback and pgvector column
  -> semantic_search retrieves chunk metadata
  -> chunk text is read from Markdown only when needed
  -> compressed context is sent to the LLM
```

## Setup

```powershell
pip install -r LifeOS\Scripts\requirements.txt
python LifeOS\Scripts\sync_vault.py
python LifeOS\Scripts\index_embeddings.py --migrate
```

Use hash embeddings for offline testing without model download:

```powershell
$env:LIFEOS_EMBEDDING_PROVIDER="hash"
python LifeOS\Scripts\index_embeddings.py --migrate
```

## Search

```powershell
python LifeOS\Scripts\semantic_search.py "active goals and next actions"
python LifeOS\Scripts\semantic_search.py "active goals and next actions" --context
```

## Token Control

- Store summaries and line ranges in PostgreSQL, not full note bodies.
- Retrieve top chunks only.
- Build compressed context from summaries first.
- Read raw Markdown chunks only for final grounding.

