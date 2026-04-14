# Day 21 — The Data Crime Detective
### Every Business Has Crimes Hiding Inside. Most Never Look. | 10x.in

---

## What is this?

14,000 transactions. Look fine on the surface. But hidden inside — stolen credit cards, bot traffic, insider theft, price glitches, fake refunds, data errors, account takeovers.

Most businesses never find these. They see the revenue number. They celebrate. They miss the leak.

Today we hunt them. This isn't pattern analysis. This is forensic investigation — finding the weird stuff that shouldn't exist.

---

## The Core Idea

All previous days — we looked for patterns. Today we look for what BREAKS the pattern. Anomalies. Outliers. Crimes.

A business with 14,000 transactions might have 600 that are suspicious. Card testing fraud. Employee refund scams. Bot-driven purchases. Price glitches where a $120 product sold for $12. Data entry errors inflating reports.

None of these show up in a revenue dashboard. All of them cost money. Every business has them. Almost nobody looks.

---

## The Data

14,157 transactions with 9 types of anomalies hidden inside:

| Column | What It Tells Us |
|---|---|
| transaction_id / timestamp | When it happened |
| customer_id / employee_id | Who did it |
| store_location / country / city | Where it happened |
| amount | How much money was involved |
| payment_method / card_last_4 | How they paid |
| ip_address / device_type | Digital fingerprint |
| items_count / discount_applied_pct | What they bought and at what discount |
| is_refund / original_transaction_id | Is this a refund? Is it legitimate? |
| processing_time_seconds | How fast was the transaction processed (bots are fast) |

**Hidden inside this data**:
- Card testing fraud (rapid-fire small charges)
- Stolen cards (same card in 4 countries in 1 hour)
- Employee refund fraud (ghost refunds)
- Bot traffic (identical processing times)
- Price glitches (products sold 90% below normal)
- Data entry errors (impossible values)
- Discount abuse (80%+ unauthorized discounts)
- Account takeover (dormant accounts going wild)
- Round-number fraud (gift card scams at 3am)

---

## The 8 Outputs

1. **Fraud Investigation Dashboard** — the complete crime board
2. **Stolen Card Timeline** — impossible geography cases mapped
3. **Employee Watchlist** — staff ranked by suspicious behavior
4. **Bot vs Human Detector** — processing time fingerprints
5. **Price Glitch Report** — products sold at wrong prices
6. **Anomaly Hotspots** — when and where crimes cluster
7. **Suspicion Ranking** — top 20 transactions to investigate
8. **Investigation Report** — full forensic write-up with actions

---

## Project Structure

```
fraud-detective/
├── CLAUDE.md                ← Claude Code reads this
├── data/
│   └── transactions.csv     ← 14,157 transactions, anomalies hidden inside
└── output/                  ← 8 files land here
```

---

## The Prompts

### Prompt 01 — Run It
```
Run it
```

### Prompt 02 — Dashboard
```
Open the dashboard
```

### Prompt 03 — The Stolen Cards
```
Find all cases where the same card was used in multiple countries within a short time window. Show the timeline.
```

### Prompt 04 — The Dirty Employee
```
Which employee has the most suspicious behavior? Show me refund rates, discount patterns, and transaction volume per employee.
```

### Prompt 05 — Bot Traffic
```
Are bots hitting our checkout? Show me processing time distributions and identify IPs with non-human patterns.
```

### Prompt 06 — The Price Glitch
```
Find products sold far below their normal price. How much revenue did we lose to pricing errors?
```

### Prompt 07 — Account Takeover
```
Find customer accounts whose behavior suddenly and dramatically changed — new countries, new devices, much higher spending.
```

### Prompt 08 — The Crime Scene
```
When and where do anomalies cluster? Show me the hour-of-day and location breakdown.
```

### Prompt 09 — The Action Report
```
Write a forensic report — every crime found, every suspect identified, and 5 immediate actions to protect the business. Include financial impact for each.
```

---

## What You'll Discover

| What You See | What's Actually Happening |
|---|---|
| "Record online orders" | 500 bot transactions inflating the numbers |
| "Employee #12 is productive" | Employee #12 is processing ghost refunds |
| "A product went viral" | Price glitch — sold 294 times at 10% of real price |
| "We have loyal customers abroad" | 3 accounts hijacked, buying from Mumbai instead of New York |
| "Revenue looks great" | Data entry error added $4.9M in fake sales |

---

## The Shift

> Every business has losses hiding in the data.
> Not fake numbers — but real crimes disguised as normal activity.
>
> The revenue dashboard shows what came in.
> This analysis shows what was stolen, wasted, or faked along the way.
>
> Most businesses never look. The ones that do — save millions.

---

*Day 21 of 28 | Built with Claude Code | 10x.in*
