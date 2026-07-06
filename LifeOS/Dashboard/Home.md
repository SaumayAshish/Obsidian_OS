---
type: dashboard
status: active
created: 2026-05-13
updated: 2026-05-13
tags: [dashboard, lifeos]
---

# LifeOS Dashboard

> Open this note first. It is the control panel for today, goals, habits, finance, learning, projects, and AI memory.

Quick links: [[Backend Summary]] · [[../Config/Completion and Usage Guide|Usage Guide]] · [[../Config/QuickAdd Workflows|QuickAdd Workflows]]

## Today

```dataview
TABLE WITHOUT ID
  file.link AS "Daily Note",
  mood AS "Mood",
  productivity AS "Productivity",
  sleep AS "Sleep"
FROM "Daily Notes"
WHERE file.name = dateformat(date(today), "yyyy-MM-dd")
LIMIT 1
```

## Tasks Due Today

```tasks
not done
due today
sort by priority
sort by path
```

## Overdue Tasks

```tasks
not done
due before today
sort by due
sort by priority
```

## Active Goals

```dataview
TABLE
  level AS "Level",
  progress AS "Progress",
  target_date AS "Target",
  status AS "Status"
FROM "Goals"
WHERE type = "goal" AND status = "active"
SORT target_date ASC
```

## Active Projects

```dataview
TABLE
  status AS "Status",
  area AS "Area",
  next_action AS "Next Action",
  due AS "Due"
FROM "Projects"
WHERE type = "project" AND status != "archived"
SORT due ASC
```

## Habits

```dataview
TASK
FROM "Daily Notes"
WHERE contains(text, "#habit") AND file.name = dateformat(date(today), "yyyy-MM-dd")
```

```tracker
searchType: task.done
searchTarget: "#habit"
folder: Daily Notes
startDate: -30d
endDate: 0d
summary:
    template: "30-day habit completions: {{sum()}}"
```

## Finance Snapshot

```dataview
TABLE WITHOUT ID
  file.link AS "Day",
  expense_total AS "Expense Total"
FROM "Daily Notes"
WHERE type = "daily" AND expense_total
SORT file.day DESC
LIMIT 7
```

## Learning Progress

```dataview
TABLE
  domain AS "Domain",
  status AS "Status",
  revision_status AS "Revision",
  next_review AS "Next Review"
FROM "Learning"
WHERE type = "learning-topic"
SORT next_review ASC
LIMIT 10
```

## Recent Journal Entries

```dataview
LIST
FROM "Journal" OR "Daily Notes"
WHERE contains(tags, "journal")
SORT file.mtime DESC
LIMIT 8
```

## AI Summaries

```dataview
TABLE
  memory_type AS "Type",
  importance AS "Importance",
  updated AS "Updated"
FROM "AI Memory"
WHERE type = "ai-memory"
SORT importance DESC, updated DESC
LIMIT 10
```
