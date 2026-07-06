---
type: finance-report
status: active
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags: [finance, monthly]
month: <% tp.date.now("YYYY-MM") %>
currency: INR
---

# Finance - <% tp.date.now("YYYY-MM") %>

## Budget

| Category | Budget | Actual | Difference |
|---|---:|---:|---:|
| Food | 0 | 0 | 0 |
| Transport | 0 | 0 | 0 |
| Housing | 0 | 0 | 0 |
| Learning | 0 | 0 | 0 |
| Subscriptions | 0 | 0 | 0 |
| Investments | 0 | 0 | 0 |

## Transactions

| Date | Type | Category | Merchant | Amount | Currency | Note |
|---|---|---|---|---:|---|---|

## Subscriptions

```dataview
TABLE amount, currency, billing_cycle, next_due_date, active
FROM "Finance"
WHERE type = "subscription" AND active = true
SORT next_due_date ASC
```

## Review

- Biggest expense:
- Avoidable expense:
- Savings rate:
- Next action:

