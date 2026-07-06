---
type: journal-index
status: active
created: 2026-07-06
updated: 2026-07-06
tags: [journal]
---

# Journal Index

Long-form reflections and personal logs. Use `Templates/Journal Entry.md` to capture entries here or via the "Journal" QuickAdd macro (which appends to today's daily note instead, for short in-the-moment entries).

## Entries

```dataview
TABLE mood, created
FROM "Journal"
WHERE type = "journal"
SORT created DESC
```
