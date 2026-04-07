# Day 15 — Pricing Psychology Analytics
### Why ₹999 Sells 3x More Than ₹1000 | 10x.in

---

## The Problem

Every product has a price.
But the price you see is never just a number.
It's a psychological weapon.

₹999 vs ₹1000. Same product. ₹1 difference.
But one sells 3x more. Why?

Because pricing is not math.
Pricing is psychology.

Today we break down 10 pricing strategies used by every major company — and find out which ones actually work, which ones backfire, and which ones are manipulating you right now.

---

## The Psychology

```
See Price  →  Feel Something  →  Decide  →  Buy (or Leave)
```

Between "see" and "decide" — that's where psychology lives.
Companies engineer that gap. Today we measure it.

---

## The 4 Big Insights

### 1. Conversion is a Lie
A strategy that converts 50% sounds amazing.
But what if 30% of those buyers return the product?
What if none of them come back?
High conversion + high regret = dangerous pricing.

### 2. The Regret Gap
Some strategies make people buy fast and regret later.
Urgency pricing — "Only 2 left!" — creates impulse.
Impulse creates regret. Regret creates returns.
The best pricing doesn't just sell. It satisfies.

### 3. Different Brains, Different Tricks
A price-sensitive buyer responds to ₹999.
A brand-loyal buyer responds to ₹1,600 premium pricing.
An impulse buyer responds to "Sale ends in 2 hours."
Same product. Different price. Different psychology. Different result.

### 4. Short-Term vs Long-Term
Some strategies win today and lose tomorrow.
Urgency converts now but kills loyalty.
Prestige converts less but builds repeat buyers.
The right question: which strategy makes money over 12 months, not 12 hours?

---

## The Data

12,000 users across 10 pricing strategies and 12 products:

| Column | What It Tells Us |
|---|---|
| user_id | Unique buyer |
| product | What they were shown (Wireless Earbuds, Running Shoes, etc.) |
| category | Electronics, Fashion, Beauty, Health |
| pricing_strategy | Which of the 10 strategies was used |
| original_mrp | The "original" price shown (anchor) |
| displayed_price | The actual price they see |
| discount_percent | How big the perceived discount is |
| user_segment | Price Sensitive / Brand Loyal / Impulse Buyer / Research Heavy / First Time Buyer |
| time_on_page_seconds | How long they looked before deciding |
| items_in_cart | How many items they added |
| converted | Did they buy? (1 = yes, 0 = no) |
| revenue | How much they spent |
| returned | Did they return the product? (1 = yes) |
| satisfaction_rating | 1-5 rating (0 if didn't buy) |
| repeat_purchase_30d | Did they buy again within 30 days? |

The 10 strategies: charm_pricing (₹999), round_pricing (₹1000), anchor_high (big MRP slash), anchor_low (small discount), decoy_pricing (3 options), bundle_pricing (buy more save more), urgency_pricing (limited time), prestige_pricing (premium price), free_shipping_threshold (add to qualify), odd_specific_pricing (₹1,247)

---

## The 8 Outputs

### 1. Pricing Analytics Dashboard — the complete strategy view
### 2. Strategy Battle — all 10 strategies ranked by conversion
### 3. Regret Chart — conversion vs returns (which strategies backfire)
### 4. Long Game Chart — conversion vs repeat purchases (short-term vs loyalty)
### 5. Segment Heatmap — which strategies work for which buyer types
### 6. Psychology Breakdown — which psychological principle is most powerful
### 7. Pricing Power Ranking — composite score ranking all 10
### 8. Pricing Strategy Report — what to scale, use carefully, or avoid

---

## Project Structure

```
pricing-psychology-analyzer/
├── CLAUDE.md                ← Claude Code reads this
├── data/
│   └── pricing_data.csv     ← 12,000 users × 10 strategies
└── output/                  ← 8 files land here
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

The complete pricing intelligence view — strategy rankings, regret analysis, segment heatmap, psychology breakdown.

---

### Prompt 03 — The Regret Problem

```
Which pricing strategies make people buy but then regret it? Show conversion vs return rates and the cost of regret
```

Find strategies that look great on paper but destroy customer trust.

---

### Prompt 04 — Segment Match

```
Which pricing strategy works best for each buyer type? Show me the segment x strategy matrix with conversion rates
```

Price-sensitive buyers need charm pricing. Impulse buyers need urgency. Or do they?

---

### Prompt 05 — Short-Term vs Long-Term

```
Rank all strategies by long-term value — not just who converts now, but who comes back and buys again. Show the loyalty gap
```

The real money isn't in the first sale. It's in the tenth.

---

### Prompt 06 — Psychology Battle

```
Group strategies by psychological principle and show which type of psychology is the most effective at driving purchases. Which is the most dangerous?
```

Left-digit effect vs anchoring vs scarcity vs prestige — who wins?

---

### Prompt 07 — Category Pricing

```
Do pricing strategies work differently for electronics vs fashion vs beauty vs health? Show category-specific recommendations
```

Urgency might work for fashion but fail for electronics.

---

### Prompt 08 — The Pricing Playbook

```
Build a complete pricing playbook — which strategy for which segment and category. Include the revenue impact and what to avoid
```

A ready-to-use pricing strategy document.

---

### Prompt 09 — The Money Question

```
If we switch every segment to their optimal pricing strategy, how much more revenue do we make and how much do returns drop? Show the math
```

The ROI of getting pricing right.

---

## What You Built Today

| Before | After |
|---|---|
| Pricing based on gut feeling | 10 strategies tested with data |
| No idea which strategy works | Every strategy ranked by real impact |
| Ignoring returns and regret | Regret gap identified per strategy |
| Same price for everyone | Segment-specific pricing strategy |
| Chasing short-term conversion | Long-term loyalty factored in |

---

## The Real Insight

> The best price is not the lowest price.
> It's the price that makes people buy AND come back.
>
> ₹999 is not cheaper than ₹1000.
> It just feels different.
>
> Pricing is not math. Pricing is psychology.
> And now you can measure it.

---

*Day 15 of 28 | Built with Claude Code | 10x.in*
