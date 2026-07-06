---
type: monthly-review
status: active
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags: [review, monthly]
month: <% tp.date.now("YYYY-MM") %>
---

# <% tp.date.now("YYYY-MM") %> Review

## Summary

- Main wins:
- Main losses:
- Key lesson:
- Next month theme:

## Goal Progress

```dataview
TABLE level, progress, metric_current, metric_target, target_date
FROM "Goals"
WHERE type = "goal" AND status = "active"
SORT level ASC, target_date ASC
```

## Finance

```dataview
TABLE WITHOUT ID
  file.link AS "Day",
  expense_total AS "Expense Total"
FROM "Daily Notes"
WHERE type = "daily" AND dateformat(file.day, "yyyy-MM") = this.month
SORT file.link ASC
```

## Habits

```tracker
searchType: task.done
searchTarget: "#habit"
folder: Daily Notes
startDate: -30d
endDate: 0d
summary:
    template: "Monthly habit completions: {{sum()}}"
```

## Decisions

- Start:
- Stop:
- Continue:
