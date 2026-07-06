---
type: goal
status: active
created: 2026-05-13
updated: 2026-05-13
tags: [goal, vision]
level: vision
progress: 0
target_date:
next_action: Define annual goals
---

# Vision

## Life Direction

Write the long-term direction here.

## Annual Goals

```dataview
TABLE progress, target_date, next_action
FROM "Goals"
WHERE type = "goal" AND level = "annual"
SORT target_date ASC
```

