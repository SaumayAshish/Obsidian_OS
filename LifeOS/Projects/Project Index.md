---
type: project-index
status: active
created: 2026-05-13
updated: 2026-05-13
tags: [project]
---

# Project Index

## Active Projects

```dataview
TABLE status, area, goal, due, next_action
FROM "Projects"
WHERE type = "project" AND status = "active"
SORT due ASC
```

## Waiting

```dataview
TABLE next_action, due
FROM "Projects"
WHERE type = "project" AND status = "waiting"
SORT due ASC
```

## Archived

```dataview
TABLE updated
FROM "Projects"
WHERE type = "project" AND status = "archived"
SORT updated DESC
```

