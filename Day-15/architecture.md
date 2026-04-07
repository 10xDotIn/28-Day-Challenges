# Pricing Psychology Analytics — System Architecture

---

## Layer 1: Problem

Same product, different price, completely different behavior.
Companies guess pricing. We measure it.

**Input Question**: What price should we set?
**Real Question**: Which pricing psychology actually works — and for whom?

---

## Layer 2: Data

**Input**: `data/pricing_data.csv`
- 12,000 users × 10 pricing strategies × 12 products

**Signals**:

| Signal | What It Measures |
|---|---|
| pricing_strategy | Which psychological trick was used |
| displayed_price | What the buyer actually saw |
| original_mrp | The anchor price (creates contrast) |
| discount_percent | Perceived savings |
| converted | Did they buy? |
| returned | Did they regret it? |
| satisfaction_rating | How they felt after buying |
| repeat_purchase_30d | Did they come back? |
| user_segment | What type of buyer they are |

---

## Layer 3: Intelligence Engine

### Module A — Strategy Battle Engine
- Compare all 10 strategies head-to-head
- Rank by conversion rate, revenue, cart size
- Output: which strategy sells the most

### Module B — Regret Detection Engine
- Compare conversion rate vs return rate per strategy
- High conversion + high returns = regret pricing
- Output: which strategies backfire

### Module C — Loyalty Engine
- Compare conversion rate vs repeat purchase rate
- Short-term wins vs long-term value
- Output: which strategies build vs destroy loyalty

### Module D — Segment Match Engine
- Cross-reference: strategy effectiveness × buyer type
- Find best strategy per segment
- Output: personalized pricing recommendations

### Module E — Psychology Classifier
- Group strategies by psychological principle
- Measure effectiveness of each principle
- Output: which type of psychology is most powerful

### Module F — Category Intelligence
- Strategy effectiveness by product category
- Output: category-specific pricing recommendations

### Module G — Pricing Power Score
- Composite: 30% conversion + 25% net revenue + 25% repeat + 20% satisfaction
- Rank all 10 strategies
- Output: master pricing ranking

---

## Layer 4: Insight Layer

| Signal Pattern | Insight |
|---|---|
| High conversion + high returns | Regret pricing — sells but backfires |
| High conversion + high repeat | Gold strategy — scale immediately |
| Low conversion + high satisfaction | Prestige play — niche but loyal |
| Segment-specific lift | Personalization opportunity |
| Category-specific variation | Context-dependent pricing |

---

## Layer 5: Decision Layer

```
┌─────────┬────────────────┬─────────────────┬──────────┐
│  SCALE  │ USE CAREFULLY  │ TARGETED ONLY   │  AVOID   │
│         │                │                 │          │
│ High    │ High convert   │ Works for       │ Low      │
│ convert │ but high       │ specific        │ convert  │
│ + happy │ returns/regret │ segments only   │ or high  │
│ + loyal │                │                 │ regret   │
└─────────┴────────────────┴─────────────────┴──────────┘
```

---

## Layer 6: Agentic Layer

**AI Role**:
- Tests all 10 strategies against real behavior
- Detects regret patterns humans miss
- Finds segment-specific opportunities
- Generates visual evidence
- Suggests pricing playbook

**Human Role**:
- Sets brand positioning and pricing floors
- Validates against competitive landscape
- Makes final pricing decisions

---

## Layer 7: Output Layer

| Output | Purpose |
|---|---|
| `dashboard.html` | Complete pricing decision view |
| `strategy_battle.png` | Conversion ranking |
| `regret_chart.png` | Conversion vs returns |
| `long_game.png` | Conversion vs loyalty |
| `segment_heatmap.png` | Strategy × segment matrix |
| `psychology_breakdown.png` | Which psychology wins |
| `pricing_power_ranking.png` | Master composite ranking |
| `pricing_strategy.md` | Business report with playbook |

---

## Core Philosophy

```
NOT: "What's the lowest price we can offer?"
BUT: "What's the price that makes people buy AND stay?"

NOT: "Which price converts most?"
BUT: "Which price creates the least regret?"

NOT: "One price for everyone"
BUT: "Right price for the right buyer"
```
