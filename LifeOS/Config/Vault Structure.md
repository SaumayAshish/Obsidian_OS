# Vault Structure

```text
LifeOS/
├── Dashboard/
├── Daily Notes/
├── Goals/
├── Learning/
├── Projects/
├── Finance/
├── Journal/
├── Career/
├── AI Memory/
├── Templates/
├── Attachments/
├── Scripts/
├── Config/
└── Archive/
```

## Folder Responsibilities

| Folder | Purpose |
|---|---|
| `Dashboard/` | Home dashboard, weekly dashboard, analytics views |
| `Daily Notes/` | Daily planning, habit logs, daily expenses, journal capture |
| `Goals/` | Vision, annual goals, quarterly goals, goal progress |
| `Learning/` | Roadmaps, topic notes, resources, revision logs |
| `Projects/` | Active project notes, Kanban boards, specs, reviews |
| `Finance/` | Budgets, subscriptions, investments, monthly reports |
| `Journal/` | Long-form reflections and personal logs |
| `Career/` | Resume, interview prep, applications, skill evidence |
| `AI Memory/` | Summaries, durable preferences, compressed memory notes |
| `Templates/` | Templater templates for notes and reviews |
| `Attachments/` | Images, PDFs, exported files |
| `Scripts/` | Python automation and RAG scripts |
| `Config/` | Setup docs, database schema, environment examples |
| `Archive/` | Inactive projects, old goals, closed notes |

## Naming Conventions

- Daily notes: `YYYY-MM-DD.md`
- Weekly reviews: `YYYY-[W]ww Review.md`
- Monthly reviews: `YYYY-MM Review.md`
- Goal notes: `Goal - <Outcome>.md`
- Project notes: `Project - <Name>.md`
- Learning topics: `<Domain> - <Topic>.md`
- Finance reports: `Finance - YYYY-MM.md`

## Minimal Frontmatter Standard

```yaml
---
type: note
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
---
```

Specialized templates should extend this standard instead of replacing it.

