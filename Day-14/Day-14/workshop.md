# Day 14 — Feature Impact Analytics
### The Truth Behind Product Growth | 10x.in

---

## The Problem

Companies ship features every sprint.
More features = better product. Right?

Wrong.

Most features get used. Few create value.
And the ones that look important? Often useless.

The question is not "what should we build next?"
The question is "what actually changes user behavior?"

Today we answer that with data.

---

## The Product Loop

```
Open  →  Feature  →  Return  →  Purchase
```

Every feature tries to push users forward in this loop.
Most fail silently.
A few drive the entire business.

---

## The 4 Big Insights

### 1. Usage is a Lie
Just because users click something doesn't mean it creates value.
A feature used by 80% of users can have ZERO impact on retention.
That's a vanity feature — looks impressive, does nothing.

### 2. Small Features Win Big
The most powerful features are often the ones nobody talks about.
Low usage + high retention = hidden gold.
These are growth engines hiding in plain sight.

### 3. Some Features Kill Growth
They distract users. They don't convert. They waste engineering resources.
Every feature you maintain has a cost.
If it doesn't drive behavior change — it's a liability.

### 4. Behavior > Features
Features don't matter. Behavior change matters.
The right question: does this feature make users come back more? Buy more?
If yes — push it. If no — question everything about it.

---

## The Data

10,000 users across 12 features in an e-commerce product:

| Column | What It Tells Us |
|---|---|
| user_id | Unique customer |
| session_id | Unique session |
| feature_used | Which feature they interacted with |
| time_spent_seconds | How long they spent on it |
| actions_count | How many actions they took |
| returned_within_7d | Did they come back within a week? (1 = yes, 0 = no) |
| purchased | Did they buy something? (1 = yes, 0 = no) |
| revenue | How much they spent |
| user_type | New / Regular / Power / Inactive / VIP |
| sessions_last_30d | How active they've been recently |
| days_since_last_visit | Recency signal |

The 12 features: search, product_view, cart, wishlist, recommendations, reviews, notifications, offers, filters, compare, share, live_chat

The key insight: we compare users who used a feature vs those who didn't.
The GAP between those groups = true feature impact.

---

## The 8 Outputs

### 1. Product Analytics Dashboard — the complete decision view
### 2. Feature Truth Chart — usage vs actual impact for every feature
### 3. Hidden Gold Map — low usage, high impact features
### 4. Vanity Feature Detector — high usage, zero impact features
### 5. Feature Funnel — where each feature loses users
### 6. Segment Heatmap — which features work for which user types
### 7. Feature Power Ranking — all 12 features ranked by real impact
### 8. Product Strategy Report — what to push, improve, monitor, remove

---

## Project Structure

```
feature-impact-analytics/
├── CLAUDE.md                  ← Claude Code reads this
├── data/
│   └── product_usage.csv      ← 10,000 users × 12 features
└── output/                    ← 8 files land here
```

---

## The Prompts

---

### Prompt 01 — Run It

```
Run it
```

Claude reads the data, runs all 8 analyses, generates every output.

---

### Prompt 02 — Dashboard

```
Open the dashboard
```

The complete product intelligence view. Feature rankings, hidden gold alerts, vanity traps, segment heatmap — all in one place.

---

### Prompt 03 — The Truth

```
Show me which features actually matter and which ones are lying to us. Compare usage vs real impact
```

This is the money chart. Features ranked by what they DO, not how much they're used.

---

### Prompt 04 — Hidden Gold

```
Find the features that almost nobody uses but have the highest impact on retention and revenue. What's the growth potential if we double their usage?
```

The features hiding in plain sight. Low adoption, massive impact.

---

### Prompt 05 — Vanity Traps

```
Which features look important because of high usage but actually contribute nothing to retention or revenue? How much are we wasting on them?
```

The uncomfortable truth about popular features.

---

### Prompt 06 — Segment Strategy

```
Break down feature effectiveness by user type. Which features work for new users vs power users vs inactive users? Show the heatmap
```

Not every feature works for everyone. This reveals segment-specific growth levers.

---

### Prompt 07 — Feature Funnel

```
For each feature, show the full funnel: usage → return → purchase. Where does each feature lose users? Which has the best conversion?
```

Find where the behavioral chain breaks.

---

### Prompt 08 — Product Decisions

```
What features should we push, improve, monitor, or remove? Show the business impact of each decision with ROI estimates
```

The product roadmap — generated from behavior data, not opinions.

---

### Prompt 09 — The Growth Brief

```
Write a product strategy brief I can hand to my team. Which features to invest in, which to sunset, what to build next. Include the numbers. Make it visual
```

A ready-to-present document for product leadership.

---

## What You Built Today

| Before | After |
|---|---|
| Guessing which features matter | Every feature ranked by real impact |
| Building more features blindly | Knowing what to push and what to remove |
| Treating all features equally | Segment-specific feature strategies |
| No idea what drives retention | Retention and revenue drivers identified |
| Opinion-based roadmap | Data-driven product decisions |

---

## The Real Insight

> The best products are not built by adding more.
> They are built by removing what doesn't matter.
>
> Usage is not importance.
> Behavior change is importance.
>
> Find what actually works. Kill what doesn't.
> That is product growth.

---

*Day 14 of 28 | Built with Claude Code | 10x.in*
