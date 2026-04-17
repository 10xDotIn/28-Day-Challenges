# Profit Illusion Analyzer

> You are a financial analytics expert who sees through revenue vanity.
> Your job is to find the truth behind the numbers — which products, channels,
> and customers LOOK profitable but actually lose money, and which boring ones
> secretly carry the entire business.

## Setup
- CSV is in `data/orders.csv`
- ~15,000 orders across 20 products, 5 channels, 5 customer segments
- Columns: order_id, product, category, quantity, unit_price, discount_percent, discount_amount, revenue, cogs, shipping_cost, returned (1/0), return_cost, support_ticket (1/0), support_cost, channel, marketing_cost, customer_segment, true_profit
- Categories: Electronics, Fashion, Beauty, Health
- Channels: organic, paid_ads, social_media, email, referral
- Segments: New Customer, Returning, VIP, Discount Hunter, One-Time Buyer
- Install packages: pandas matplotlib numpy seaborn pillow
- Save all outputs in `output/`
- Use ALL rows

---

## What to Analyze

### 1. The Revenue vs Profit Lie
For each product:
- Total revenue (what the dashboard shows)
- Total TRUE profit (after cogs, shipping, returns, support, marketing)
- Revenue rank vs profit rank — find the disconnect
- Which products LOOK like winners but are actually losers?
- Which products look boring but secretly carry the business?
- Calculate: profit margin, cost breakdown per product

### 2. The Hidden Cost Breakdown
For each product, show WHERE the money goes:
- COGS (cost of goods)
- Shipping costs
- Return costs (returned items + processing)
- Support ticket costs
- Marketing costs
- What's left = true profit
- Some products have 80% revenue eaten by hidden costs
- Stack these costs visually — show the revenue bar shrinking

### 3. The Return Tax
Returns are the silent profit killer:
- Return rate per product
- Return cost per product (not just refund — processing, shipping back, restocking)
- Which products have high revenue but get destroyed by returns?
- Running Shoes might sell $186K but lose $48K in returns
- Calculate: revenue lost to returns as % of total revenue per product

### 4. The Channel Illusion
Not all sales channels are equal:
- Revenue by channel vs PROFIT by channel
- paid_ads might bring the most revenue but after ad spend — what's left?
- organic and email might bring less revenue but almost pure profit
- Calculate TRUE ROI per channel: profit / marketing_cost
- Which channels should you scale? Which should you cut?

### 5. The Customer Segment Truth
Some customers cost more than they're worth:
- Revenue vs profit by segment
- Discount Hunters — high revenue but margins destroyed by discounts + higher returns
- VIPs — fewer orders but full-price purchases, low returns, high margins
- Calculate: profit per customer by segment
- Which segments are you LOSING money on?

### 6. The Discount Trap
Discounts drive revenue but kill profit:
- Revenue from discounted vs full-price orders
- Profit from discounted vs full-price orders
- Which discount ranges are profitable? (5-10% might work, 30%+ might lose money)
- Discount Hunters vs VIPs — same product, completely different profitability
- Calculate: break-even discount rate per product

### 7. The Profit Power Score
Rank every product by TRUE business value:
- 35% weight: profit margin
- 25% weight: profit volume (total dollars)
- 20% weight: low return rate
- 20% weight: low support cost
- Rank all 20 products from MOST to LEAST profitable
- This is the real ranking — not the revenue ranking

### 8. Strategic Recommendations
Based on ALL analyses:
- **SCALE** — High profit margin + low returns + low support. Invest more.
- **FIX** — Good revenue but profit leaking. Find and plug the leak.
- **REPRICE** — Discounted too heavily. Raise prices or reduce discounts.
- **DROP** — Revenue looks good but true profit is negative or near zero. Consider killing.
- Estimated profit impact of each recommendation

---

## Output Files

### 1. `output/dashboard.html`
Dark-themed profit intelligence dashboard (single self-contained HTML file):
- **Hero**: total revenue, total profit, overall margin, total hidden costs, return rate
- **The Big Lie Chart**: side-by-side bars for each product — revenue bar vs profit bar. The gap between them = hidden costs. Sort by biggest gap first. This is the core visual.
- **Cost Waterfall**: for the top 5 revenue products, show a waterfall chart — start with revenue, subtract COGS, shipping, returns, support, marketing — what's left is profit
- **Revenue Rank vs Profit Rank**: scatter plot or table showing rank disconnect. Products in top-left = illusion (high revenue rank, low profit rank)
- **Channel Truth**: revenue vs profit by channel, with ROI numbers
- **Segment Profitability**: revenue vs profit by customer segment, highlight Discount Hunters
- **The Return Tax**: return rate and return cost by product, sorted by impact
- **Discount Trap**: profit margin at different discount levels
- **Profit Power Ranking**: all 20 products ranked by composite score
- **Strategy Board**: SCALE / FIX / REPRICE / DROP columns with products
- Responsive, dark background (#0f0f0f), card-based layout

### 2. `output/revenue_vs_profit.png`
The most important chart. For each product — two bars side by side. Blue = revenue. Green = true profit. Sort by revenue descending. The visual gap between blue and green = money disappearing. Some products will have a huge blue bar and tiny green bar.

### 3. `output/cost_waterfall.png`
Waterfall chart for top 5 revenue products. Start with revenue, subtract each cost layer. Show how revenue melts away. COGS → Shipping → Returns → Support → Marketing → Profit.

### 4. `output/channel_truth.png`
Grouped bars: revenue vs profit by channel. Show ROI number above each channel. paid_ads will have big revenue but small profit. email will have small revenue but high profit.

### 5. `output/segment_profitability.png`
Revenue vs profit by customer segment. Highlight Discount Hunters — high revenue, crushed margins. Show profit per customer for each segment.

### 6. `output/return_tax.png`
Bar chart: return cost as % of revenue by product. Sort by highest return tax. Some products lose 15-20% of revenue to returns.

### 7. `output/profit_power_ranking.png`
Horizontal bar chart: all 20 products ranked by composite profit score. Color coded — green (scale), yellow (fix), red (drop). Show margin % on each bar.

### 8. `output/profit_report.md`
Business report:
- Executive summary: "Your revenue is $X but $Y is an illusion"
- Top 5 profit illusion products (high revenue, low/negative profit)
- Top 5 hidden gems (low revenue, high profit margin)
- Channel analysis: where to spend, where to cut
- Segment analysis: which customers are worth it
- The discount problem: how discounts destroy margins
- Profit power ranking (table)
- Strategic recommendations: SCALE / FIX / REPRICE / DROP
- 5 specific actions to increase profit without increasing revenue
- Final verdict: most overrated product, most underrated product, biggest profit leak

---

## System Architecture

```
Layer 1: Problem     → Revenue ≠ Profit. What looks good might be losing money.
Layer 2: Data        → 15K orders, 20 products, every cost tracked
Layer 3: Engine      → 8 modules: Revenue vs Profit, Cost Breakdown, Return Tax,
                       Channel Truth, Segment Analysis, Discount Trap, Power Score, Strategy
Layer 4: Insights    → High revenue + low profit = illusion. Low revenue + high margin = gem.
Layer 5: Decisions   → Scale, Fix, Reprice, Drop
Layer 6: Agentic     → AI finds illusions, human makes business calls
Layer 7: Outputs     → Dashboard, charts, rankings, strategy report
```

---

## Rules
1. Read this file FIRST
2. Install packages silently (`pip install -q`)
3. Write and run `analyzer.py` — fix errors yourself
4. Use ALL data
5. Create ALL 8 output files
6. End with: most overrated product, most underrated product, biggest profit leak, 1 change that increases profit immediately

## IMPORTANT: Visual Output Rule
Follow-up questions → ALWAYS create a NEW visual file (PNG or HTML), never just text.
