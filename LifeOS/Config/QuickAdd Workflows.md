# QuickAdd Workflows

Use QuickAdd to call scripts or append Markdown snippets. These workflows keep Obsidian as the primary UI.

## Commands

| Workflow | Action |
|---|---|
| Sync LifeOS | Run `python Scripts/sync_vault.py` |
| Reindex Retrieval | Run `python Scripts/index_embeddings.py` |
| Generate Backend Summary | Run `python Scripts/generate_backend_summary.py` |
| Daily Automation | Run `python Scripts/run_daily_automation.py` |
| Ask LifeOS | Run `python Scripts/ask_lifeos.py "{{VALUE:Question}}"` |

## Suggested Capture Macros

### Quick Task

Append to today's daily note:

```markdown
- [ ] #task {{VALUE:Task}} due: {{DATE:YYYY-MM-DD}}
```

### Expense

Append under today's `Expenses` table:

```markdown
| {{DATE:YYYY-MM-DD}} | expense | {{VALUE:Category}} | {{VALUE:Merchant}} | {{VALUE:Amount}} | INR | {{VALUE:Note}} |
```

### Journal

Append under today's `Journal` section:

```markdown
### {{DATE:HH:mm}}

{{VALUE:Entry}}
```

