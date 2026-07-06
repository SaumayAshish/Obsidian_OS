# Obsidian Plugin Setup

Install these community plugins in Obsidian.

| Plugin | Role |
|---|---|
| Dataview | Query notes, tasks, habits, finance, and goal metadata |
| Tasks | Task recurrence, due dates, status, filtering |
| Calendar | Daily note navigation |
| Tracker | Habit graphs, streaks, heatmaps |
| Templater | Dynamic note templates |
| QuickAdd | Fast capture workflows |
| Kanban | Project boards |
| Periodic Notes | Daily, weekly, monthly note workflows |
| Advanced Tables | Cleaner finance and planning tables |

## Recommended Core Settings

### Files and Links

- Default location for new notes: `Daily Notes/` or same folder as current file.
- New link format: shortest path when possible.
- Use Markdown links: enabled.
- Detect all file extensions: enabled.

### Daily Notes / Periodic Notes

- Daily notes folder: `Daily Notes/`
- Daily format: `YYYY-MM-DD`
- Weekly format: `YYYY-[W]ww Review`
- Monthly format: `YYYY-MM Review`
- Template folder: `Templates/`

### Templater

- Template folder location: `Templates/`
- Trigger Templater on new file creation: enabled.
- User scripts folder: `Scripts/templater` once Phase 2 scripts exist.

### Dataview

- Enable JavaScript queries only if needed.
- Keep dashboards mostly Dataview Query Language for portability.
- Use frontmatter fields consistently to avoid expensive query logic.

### Tasks

- Use global task filter if desired: `#task`
- Prefer explicit dates:
  - due: `📅 YYYY-MM-DD`
  - scheduled: `⏳ YYYY-MM-DD`
  - start: `🛫 YYYY-MM-DD`
- Use priority markers sparingly.

### Tracker

- Use daily note fields for numeric tracking:
  - `mood:: 1-5`
  - `productivity:: 1-10`
  - `sleep:: hours`
- Use checklist habits for boolean tracking.

### QuickAdd

Initial captures to configure in Phase 2:

- Quick task -> append to today's daily note.
- Expense -> append to today's expense table.
- Journal capture -> append to today's journal section.
- Learning note -> create from learning template.
- Project -> create from project template.

### Kanban

- Store project boards in `Projects/`.
- Use one board per major project.
- Keep operational tasks as Markdown tasks so Tasks and Dataview can read them.

## Plugin Installation Notes

Obsidian community plugins are not bundled in this vault. Install them from `Settings -> Community plugins -> Browse`.

After installation, use this order:

1. Enable Periodic Notes and Templater.
2. Configure daily, weekly, and monthly templates.
3. Enable Dataview and Tasks.
4. Add dashboard queries.
5. Add Tracker charts.
6. Add QuickAdd workflows.
7. Add Kanban boards.

