---
type: dashboard
status: active
created: 2026-05-13
updated: 2026-05-13
tags: [dashboard, weekly-review]
---

# Weekly Review Dashboard

## Completed This Week

```tasks
done after last monday
done before next monday
sort by done
```

## Still Open

```tasks
not done
due before next monday
sort by due
```

## Goal Progress

```dataview
TABLE progress, metric_current, metric_target, target_date
FROM "Goals"
WHERE type = "goal" AND status = "active"
SORT target_date ASC
```

## Daily Metrics

```dataview
TABLE mood, productivity, sleep, learning_minutes
FROM "Daily Notes"
WHERE file.day >= date(today) - dur(7 days)
SORT file.day ASC
```

## Expense Review

```dataview
TABLE WITHOUT ID
  file.link AS "Day",
  expense_total AS "Expense Total"
FROM "Daily Notes"
WHERE type = "daily" AND file.day >= date(today) - dur(7 days)
SORT file.link ASC
```
