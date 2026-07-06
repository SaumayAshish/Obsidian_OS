---
type: finance-index
status: active
created: 2026-05-13
updated: 2026-05-13
tags: [finance]
---

# Finance Index

## Monthly Reports

```dataview
TABLE month, currency
FROM "Finance"
WHERE type = "finance-report"
SORT month DESC
```

## Active Subscriptions

```dataview
TABLE amount, currency, billing_cycle, next_due_date
FROM "Finance"
WHERE type = "subscription" AND active = true
SORT next_due_date ASC
```

