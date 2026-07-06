---
type: ai-memory-index
status: active
created: 2026-05-13
updated: 2026-05-13
tags: [ai-memory]
---

# AI Memory Index

AI memory notes should be concise summaries, not raw dumps. Use them as durable retrieval anchors for preferences, identity, projects, decisions, and recurring context.

```dataview
TABLE memory_type, importance, valid_from, valid_until, updated
FROM "AI Memory"
WHERE type = "ai-memory"
SORT importance DESC, updated DESC
```

