# Phase 2 Workflows

## Daily Startup

1. Open `Dashboard/Home`.
2. Create today's daily note from `Templates/Daily Note`.
3. Fill top priorities, schedule, and metrics.
4. Capture tasks with explicit dates for Tasks plugin.

## Daily Shutdown

1. Complete habit checkboxes.
2. Add expenses to the daily expense table.
3. Write a short journal entry.
4. Add one `summary::` line for future AI retrieval.

## Weekly Review

1. Create weekly review from `Templates/Weekly Review`.
2. Review completed tasks and open loops.
3. Update active goal progress.
4. Pick next week's top outcomes.

## Goal Workflow

Use `Templates/Goal` for each level:

- Vision: long-term direction.
- Annual: yearly outcomes.
- Quarterly: execution outcomes.
- Weekly: short-term commitments.

Link goals with `parent_goal` and keep `progress` numeric from `0` to `100`.

## Project Workflow

Use `Templates/Project` for project specs and `Templates/Kanban Board` when a visual board is useful. Keep executable items as Markdown tasks so dashboards can query them.

## Finance Workflow

Use daily notes for quick capture and monthly finance reports for review. Phase 3 will sync daily expense rows into PostgreSQL.

## Learning Workflow

Create one note per concept with `Templates/Learning Topic`. Use `next_review` and `revision_status` to drive spaced repetition queries.

## AI Memory Workflow

Only store durable summaries in `AI Memory/`. Keep each memory note short and retrieval-focused.

