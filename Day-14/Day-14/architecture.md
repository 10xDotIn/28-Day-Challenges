# Feature Impact Analytics — System Architecture

---

## Layer 1: Problem

Too many features, no clarity on impact.
Teams build based on usage metrics — which lie.

**Input Question**: What should we build next?
**Real Question**: What actually changes user behavior?

---

## Layer 2: Data

**Input**: `data/product_usage.csv`
- 10,000 users × 12 features
- ~19,000 interaction rows

**Signals**:

| Signal | What It Measures |
|---|---|
| feature_used | Which feature was touched |
| returned_within_7d | Did the user come back? |
| purchased | Did the user convert? |
| revenue | How much money was generated? |
| user_type | New / Regular / Power / Inactive / VIP |
| sessions_last_30d | User activity level |
| days_since_last_visit | Recency signal |

---

## Layer 3: Intelligence Engine

### Module A — Feature Truth Engine
- Split: users who used feature vs users who didn't
- Compare: retention rate, purchase rate, revenue
- Output: TRUE impact per feature (not usage illusion)

### Module B — Behavior Shift Detector
- Does using a feature change what users do next?
- Measures: return lift, purchase lift, revenue lift
- Output: behavioral cause-and-effect mapping

### Module C — Hidden Gold Detector
- Criteria: low usage (< 15%) + high retention/purchase lift
- Calculates: growth potential if usage is doubled
- Output: undervalued features with untapped potential

### Module D — Vanity Trap Detector
- Criteria: high usage (> 50%) + low/zero impact lift
- Calculates: wasted engineering & resource cost
- Output: overvalued features consuming resources

### Module E — Feature Funnel Engine
- Tracks: Feature → Return → Purchase pipeline
- Identifies: where each feature's funnel breaks
- Output: conversion rates and drop-off points per feature

### Module F — Segment Intelligence
- Cross-references: feature impact × user type
- Finds: segment-specific growth levers
- Output: which features work for which users

### Module G — Power Scoring Engine
- Composite score: 40% retention lift + 40% purchase lift + 20% revenue lift
- Ranks: all 12 features from most impactful to most useless
- Output: master feature ranking

---

## Layer 4: Insight Layer

Converts raw signals into business insights:

| Signal Pattern | Insight |
|---|---|
| High usage + low impact | Vanity trap — stop investing |
| Low usage + high impact | Hidden gold — promote aggressively |
| High impact + broken funnel | Improve — fix the conversion leak |
| Low impact + low usage | Remove — reclaim resources |
| Segment-specific lift | Personalize — target right users |

---

## Layer 5: Decision Layer

**Output Categories**:

```
┌─────────┬────────────┬───────────┬──────────┐
│  PUSH   │  IMPROVE   │  MONITOR  │  REMOVE  │
│         │            │           │          │
│ High    │ High       │ Moderate  │ Low      │
│ impact  │ potential  │ impact    │ impact   │
│ Invest  │ Fix funnel │ Maintain  │ Sunset   │
│ more    │ or boost   │ current   │ and      │
│         │ adoption   │ level     │ reclaim  │
└─────────┴────────────┴───────────┴──────────┘
```

---

## Layer 6: Agentic Layer

**AI Role**:
- Reads and parses all usage data
- Builds comparison groups (used vs didn't use)
- Runs statistical analysis on each feature
- Detects patterns humans would miss
- Generates visual evidence
- Suggests concrete product actions

**Human Role**:
- Sets business context and priorities
- Validates AI findings against domain knowledge
- Makes final investment and sunset decisions
- Communicates strategy to stakeholders

---

## Layer 7: Output Layer

| Output | Purpose |
|---|---|
| `dashboard.html` | Complete decision-making view |
| `feature_truth.png` | Usage vs impact comparison |
| `hidden_gold.png` | Quadrant map of opportunities |
| `vanity_features.png` | Usage rank vs impact rank disconnect |
| `feature_funnel.png` | Conversion pipeline per feature |
| `segment_heatmap.png` | Feature × segment effectiveness |
| `power_ranking.png` | Master feature ranking by score |
| `product_strategy.md` | Business report with recommendations |

---

## Core Philosophy

```
NOT: "What is used the most?"
BUT: "What actually drives growth?"

NOT: "Build more features"
BUT: "Make the right features visible"

NOT: "Usage = importance"
BUT: "Behavior change = importance"
```
