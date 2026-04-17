# Day 16 — Profit Illusion Analyzer
### Your Best-Selling Product Might Be Losing You Money | 10x.in

---

## What is this?

Every business has a dirty secret hiding in plain sight. Your revenue dashboard says $1M. But after returns, shipping, support tickets, discounts, and ad spend — your actual profit might be $300K. And the product you think is your "best seller"? It might be your biggest money pit.

This project analyzes 15,000 real orders across 20 products and reveals:
- Which products LOOK profitable but actually lose money
- Which boring products secretly carry the entire business
- Which sales channels burn cash disguised as revenue
- Which customer segments cost more than they're worth

---

## The Core Idea

Revenue is vanity. Profit is sanity.

A product that sells $186K sounds amazing. But after $40K in COGS, $12K in returns, $8K in support tickets, $15K in shipping, and $6K in marketing — you're left with $105K. Meanwhile a $15K product with zero returns, no support tickets, and 58% margins is quietly funding your business.

**The Profit Illusion**: high revenue ≠ high profit. And most businesses never do this math.

---

## The Data

15,000 orders across 20 products in 4 categories:

| Column | What It Tells Us |
|---|---|
| product / category | What was sold (Electronics, Fashion, Beauty, Health) |
| revenue | What the dashboard shows you |
| cogs | What the product actually costs to make/buy |
| shipping_cost | What it costs to deliver |
| returned / return_cost | Did they send it back? What did that cost? |
| support_ticket / support_cost | Did they file a complaint? How much did that cost? |
| channel / marketing_cost | Where the sale came from and what you paid for it |
| customer_segment | New, Returning, VIP, Discount Hunter, One-Time Buyer |
| true_profit | Revenue minus ALL hidden costs. The real number. |

---

## The 8 Outputs

1. **Profit Intelligence Dashboard** — the complete truth view
2. **Revenue vs Profit Chart** — the core lie exposed for every product
3. **Cost Waterfall** — watch revenue melt away layer by layer
4. **Channel Truth** — which sales channels actually make money
5. **Segment Profitability** — which customers are worth it
6. **The Return Tax** — how returns silently kill profit
7. **Profit Power Ranking** — all 20 products ranked by real value
8. **Strategy Report** — what to scale, fix, reprice, or drop

---

## Project Structure

```
profit-illusion-analyzer/
├── CLAUDE.md           ← Claude Code reads this
├── data/
│   └── orders.csv      ← 15,000 orders × 20 products
└── output/             ← 8 files land here
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

### Prompt 03 — The Biggest Lie
```
Show me the products where revenue and profit tell completely different stories. Which best-seller is actually a money pit?
```

### Prompt 04 — Cost Autopsy
```
For the top 5 revenue products, break down exactly where the money goes. Show the waterfall from revenue to profit.
```

### Prompt 05 — Channel ROI
```
Which sales channels actually make money after ad spend? Show me revenue vs profit by channel with true ROI
```

### Prompt 06 — Customer Truth
```
Which customer segments are profitable and which ones cost more than they're worth? Show me the Discount Hunter problem
```

### Prompt 07 — The Discount Trap
```
How much profit are we losing to discounts? What's the break-even discount rate? Show me where discounting goes from smart to stupid
```

### Prompt 08 — Fix the Business
```
If we follow the SCALE/FIX/REPRICE/DROP recommendations, how much more profit do we make? Show the math
```

### Prompt 09 — The Profit Brief
```
Write a profit strategy brief I can hand to my finance team. Which products to push, which to kill, which channels to scale. Include the numbers.
```

---

## What You'll Discover

| What You Think | What's Actually True |
|---|---|
| Best-seller = most profitable | Best-seller might be biggest loss |
| Revenue growth = business health | Revenue can grow while profit shrinks |
| All customers are valuable | Some customers cost more than they pay |
| Discounts drive growth | Discounts can destroy margins |
| More sales channels = better | Some channels burn money disguised as revenue |

---

## The Shift

> Stop celebrating revenue. Start measuring profit.
>
> The product everyone talks about might be bleeding money.
> The product nobody notices might be keeping the lights on.
>
> Revenue is what you earn. Profit is what you keep.

---

*Day 16 of 28 | Built with Claude Code | 10x.in*
