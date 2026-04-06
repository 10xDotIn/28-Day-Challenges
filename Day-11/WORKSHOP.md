# Day 11 — Product Search Ranking Analyzer
### Your Search Results Are Lying to You | 10x.in

---

## The Problem

You search "wireless headphones" on Amazon.
You see 10 products. You click the first one.

But was it the best product?
Or was it just... on top?

Today we analyze 13,500 rows of e-commerce search data
and find where companies lose money because of bad rankings.

---

## The Search Funnel

```
Impressions  →  Clicks  →  Add to Cart  →  Purchase
  (seen)        (interested)  (considering)   (bought)
```

At every step, customers drop off.
The question is — WHERE is the biggest loss?
And WHY?

---

## The 3 Big Insights

### 1. Position Bias
Products get clicks because they're on top — not because they're good.
Position 1 gets 5-10x more clicks than position 5.
Even a bad product wins if it's placed first.

### 2. Hidden Gold Products
Some products have amazing conversion rates — 15-20% of people who click actually buy.
But they're buried at position 8 or 9.
Nobody sees them. The company is hiding its best products.

### 3. Fake Winners (Clickbait)
Some products get tons of clicks but nobody buys.
High CTR. Low conversion. They look good but perform terribly.
They're wasting prime ranking positions.

---

## The Data

13,500 rows of e-commerce search data:
- 15 search queries (headphones, shoes, laptop stand, etc.)
- 10 products per query (real brand names)
- 90 days of data
- Impressions, clicks, add to cart, purchases, revenue
- Product position, rating, price, review count

---

## The 9 Outputs

### 1. Interactive Dashboard
Revenue gaps, position bias curve, hidden gold products,
fake winners, search funnel, smart ranking recommendations.

### 2. Position Bias Chart
The curve that proves: clicks are driven by position, not quality.

### 3. Hidden Gold Scatter Plot
Low impressions + high conversion = buried treasure.

### 4. Fake Winners Scatter Plot
High CTR + low conversion = clickbait wasting space.

### 5. Revenue Gap Chart
Current revenue vs potential revenue — money left on the table.

### 6. Search Funnel
Where customers drop off: impressions → clicks → cart → purchase.

### 7. Ranking Recommendations
Which products to move UP and which to move DOWN.

### 8. Query Performance
All 15 queries compared by CTR, conversion, and revenue.

### 9. Business Report
Full analysis with revenue numbers and 5 recommendations.

---

## Project Structure

```
search-ranking-analyzer/
├── CLAUDE.md                  ← Claude Code reads this
├── data/
│   └── search_rankings.csv    ← 13,500 rows
└── output/                    ← 9 files land here
```

---

## The Prompts

---

### Prompt 01 — Run It

```
Run it
```

---

### Prompt 02 — Dashboard

```
Open the dashboard
```

---

### Prompt 03 — Position Bias

```
Show me the position bias curve
```

---

### Prompt 04 — Hidden Gold

```
Find the hidden gold products that should be ranked higher
```

---

### Prompt 05 — Fake Winners

```
Find the clickbait products wasting ranking space
```

---

### Prompt 06 — Revenue Impact

```
How much money is being lost from bad rankings?
```

---

### Prompt 07 — Smart Ranking

```
Rerank the products by performance. Show me what changes
```

---

### Prompt 08 — Business Report

```
Write the business report with revenue impact. Make it visual
```

---

## What You Built Today

| Before | After |
|---|---|
| Assume top result is best | Position bias proven with data |
| Best products invisible | Hidden gold identified |
| Clickbait gets prime spots | Fake winners exposed |
| No revenue impact data | Exact dollar amount being lost |
| Manual ranking guesses | Data-driven ranking recommendations |
| Analytics = numbers | Analytics = business decisions |

---

## The Real Insight

> Companies don't pay for dashboards.
> They pay for people who can say —
> "We are losing revenue because of this mistake,
> and here's how to fix it."
>
> That's what you built today.
> Not a report. A business decision.

---

*Day 11 of 28 | Built with Claude Code | 10x.in*
