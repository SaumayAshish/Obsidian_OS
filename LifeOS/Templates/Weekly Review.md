---
type: weekly-review
status: active
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags: [review, weekly]
week: <% tp.date.now("GGGG-[W]WW") %>
---

# <% tp.date.now("GGGG-[W]WW") %> Review

## Outcomes

- Wins:
- Problems:
- Decisions:

## Metrics

```dataview
TABLE mood, productivity, sleep, learning_minutes
FROM "Daily Notes"
WHERE file.day >= date(today) - dur(7 days)
SORT file.day ASC
```

## Completed Tasks

```tasks
done after last monday
done before next monday
sort by done
```

## Open Loops

```tasks
not done
due before next monday
sort by due
```

## Goal Review

```dataview
TABLE progress, target_date, next_action
FROM "Goals"
WHERE type = "goal" AND status = "active"
SORT target_date ASC
```

## Next Week Plan

- [ ] #task Define next week's top 3 outcomes
- [ ] #task Review active projects
- [ ] #task Update goal progress

