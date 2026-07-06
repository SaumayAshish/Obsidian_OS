---
type: career-index
status: active
created: 2026-07-06
updated: 2026-07-06
tags: [career]
---

# Career Index

Resume versions, interview prep, applications, and skill evidence.

## Applications

```dataview
TABLE status, company, role, applied_date
FROM "Career"
WHERE type = "application"
SORT applied_date DESC
```

## Skill Evidence

```dataview
TABLE skill, evidence, date
FROM "Career"
WHERE type = "skill-evidence"
SORT date DESC
```
