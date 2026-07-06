---
type: learning-roadmap
status: active
created: 2026-05-13
updated: 2026-05-13
tags: [learning, roadmap]
---

# Learning Roadmap

## Domains

- AI/ML
- DevOps
- Cloud
- Networking
- Interview Prep

## Active Topics

```dataview
TABLE domain, status, revision_status, next_review
FROM "Learning"
WHERE type = "learning-topic"
SORT domain ASC, next_review ASC
```

## Review Queue

```dataview
TABLE domain, revision_status, next_review
FROM "Learning"
WHERE type = "learning-topic" AND next_review <= date(today)
SORT next_review ASC
```

