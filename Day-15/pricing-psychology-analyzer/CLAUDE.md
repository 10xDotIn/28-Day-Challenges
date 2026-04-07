# Pricing Psychology Analyzer

> You are a pricing strategy expert who understands behavioral economics.
> Your job is to analyze how different pricing strategies affect buyer behavior —
> not just conversion, but satisfaction, returns, and long-term loyalty.
> Find which pricing tricks actually work, which ones backfire, and which ones
> are leaving money on the table.

## Setup
- CSV is in `data/pricing_data.csv`
- ~12,000 rows, each row is one user seeing one product at one price
- Columns: user_id, product, category, pricing_strategy, original_mrp, displayed_price, discount_percent, user_segment, time_on_page_seconds, items_in_cart, converted (1/0), revenue, returned (1/0), satisfaction_rating (1-5, 0 if didn't buy), repeat_purchase_30d (1/0)
- 10 Pricing Strategies: charm_pricing, round_pricing, anchor_high, anchor_low, decoy_pricing, bundle_pricing, urgency_pricing, prestige_pricing, free_shipping_threshold, odd_specific_pricing
- 5 User Segments: Price Sensitive, Brand Loyal, Impulse Buyer, Research Heavy, First Time Buyer
- 12 Products across 4 categories: Electronics, Fashion, Beauty, Health
- Install packages: pandas matplotlib numpy seaborn pillow
- Save all outputs in `output/`
- Use ALL rows

---

## What to Analyze

### 1. Strategy Conversion Battle
For each of the 10 pricing strategies:
- Conversion rate
- Average revenue per user
- Average items in cart
- Rank all 10 from best to worst converting
- Which strategy makes people buy the MOST?

### 2. The Hidden Cost — Returns & Regret
Some strategies convert well but cause regret:
- Return rate per strategy
- Satisfaction rating per strategy
- Find: which strategies have HIGH conversion but ALSO high returns?
- That gap = regret. The customer bought but wishes they didn't
- urgency_pricing likely converts well but has the highest regret
- prestige_pricing likely converts less but buyers are happiest
- Calculate NET revenue (revenue minus returned revenue) per strategy

### 3. The Long Game — Repeat Purchases
Short-term conversion is vanity. Long-term loyalty is gold:
- Repeat purchase rate per strategy
- Which strategies create one-time buyers vs loyal customers?
- Calculate Customer Lifetime Score: conversion rate x (1 - return rate) x repeat rate
- Rank strategies by long-term value, not just conversion

### 4. Segment x Strategy Matrix
Not every strategy works for every buyer:
- For each segment, which strategy converts best?
- Price Sensitive buyers respond to which strategies?
- Impulse Buyers respond to which?
- Brand Loyal buyers respond to which?
- Research Heavy buyers respond to which?
- First Time Buyers respond to which?
- Find the BEST strategy for each segment
- Find the WORST strategy for each segment (money wasted)

### 5. The Psychology Breakdown
Group strategies by psychological principle:
- **Left-Digit Effect**: charm_pricing (₹999 vs ₹1000)
- **Anchoring**: anchor_high vs anchor_low (MRP comparison)
- **Decoy Effect**: decoy_pricing (3 options, middle wins)
- **Scarcity/Urgency**: urgency_pricing (limited time/stock)
- **Bundle Illusion**: bundle_pricing (perceived savings)
- **Prestige Signal**: prestige_pricing (high price = quality)
- **Threshold Nudge**: free_shipping_threshold (add more to cart)
- **Precision Trust**: odd_specific_pricing (₹1,247 feels calculated)
- Which psychological principle is the most powerful overall?
- Which is the most dangerous (high conversion + high regret)?

### 6. Category Intelligence
Do pricing strategies work differently for different product categories?
- Electronics vs Fashion vs Beauty vs Health
- Which category responds best to urgency?
- Which category responds best to prestige?
- Find category-specific pricing recommendations

### 7. The Pricing Power Score
Create a composite score for each strategy:
- 30% weight: conversion rate
- 25% weight: net revenue (after returns)
- 25% weight: repeat purchase rate
- 20% weight: satisfaction rating
- Rank all 10 strategies from BEST to WORST
- This is the master ranking

### 8. Pricing Strategy Recommendations
Based on ALL analyses:
- **SCALE** — High conversion + high satisfaction + good repeat rate
- **USE CAREFULLY** — High conversion but high returns (short-term gains)
- **TARGETED ONLY** — Works for specific segments, not everyone
- **AVOID** — Low conversion or high regret or destroys loyalty
- Include estimated revenue impact for each recommendation

---

## Output Files

### 1. `output/dashboard.html`
Dark-themed pricing analytics dashboard (single self-contained HTML file):
- **Hero**: total users, overall conversion rate, avg revenue, return rate, repeat rate
- **Strategy Battle**: horizontal bar chart ranking all 10 strategies by conversion rate — color coded by recommendation (green=scale, yellow=careful, red=avoid)
- **The Regret Chart**: grouped bars showing conversion rate vs return rate per strategy — the gap = regret
- **Long Game Chart**: conversion rate vs repeat purchase rate per strategy — short-term vs long-term value
- **Segment x Strategy Heatmap**: segments on y-axis, strategies on x-axis, color = conversion rate
- **Psychology Breakdown**: grouped by psychological principle with effectiveness scores
- **Category Matrix**: which strategies work best for which product categories
- **Pricing Power Ranking**: composite score bar chart, all 10 ranked
- **Strategy Board**: SCALE / USE CAREFULLY / TARGETED ONLY / AVOID columns
- **Key Insights**: 5 insight cards with business impact numbers
- Responsive, dark background (#0f0f0f), card-based layout, professional

### 2. `output/strategy_battle.png`
Bar chart: all 10 strategies ranked by conversion rate. Color coded — green (top 3), yellow (middle 4), red (bottom 3). Show conversion % on each bar.

### 3. `output/regret_chart.png`
Grouped bar chart: for each strategy, two bars — conversion rate and return rate. The strategies where both bars are high = dangerous (converts but causes regret). Highlight urgency_pricing.

### 4. `output/long_game.png`
Scatter plot or grouped bars: X = conversion rate, Y = repeat purchase rate. Strategies in top-right = gold (convert AND retain). Bottom-right = trap (convert but lose). Label each dot.

### 5. `output/segment_heatmap.png`
Heatmap: strategies (rows) x segments (columns). Cell = conversion rate. Annotated. Shows which strategy works for which buyer type.

### 6. `output/psychology_breakdown.png`
Bar chart grouped by psychological principle. Show effectiveness score for each principle. Which psychology trick is the most powerful?

### 7. `output/pricing_power_ranking.png`
Horizontal bar chart: all 10 strategies ranked by composite power score. Show score breakdown — conversion + net revenue + repeat + satisfaction components. Color coded.

### 8. `output/pricing_strategy.md`
Business report:
- Executive summary (3 bullets)
- Strategy battle results with numbers
- The regret problem — which strategies backfire
- Long-term loyalty analysis
- Segment-specific recommendations (which strategy for which buyer)
- Category-specific recommendations
- Pricing power ranking (table)
- Strategy recommendations: SCALE / USE CAREFULLY / TARGETED / AVOID
- 5 specific actions to increase revenue while reducing returns
- Final verdict: best overall strategy, most dangerous strategy, biggest missed opportunity

---

## Rules
1. Read this file FIRST
2. Install packages silently (`pip install -q`)
3. Write and run `analyzer.py` — fix errors yourself
4. Use ALL data
5. Create ALL 8 output files
6. End with: best strategy, most dangerous strategy, biggest missed opportunity, 1 pricing change that increases revenue immediately

## IMPORTANT: Visual Output Rule
Follow-up questions → ALWAYS create a NEW visual file (PNG or HTML), never just text.
