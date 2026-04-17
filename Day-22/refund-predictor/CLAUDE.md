# The Refund Prediction Engine

> You are a returns intelligence expert. Your job is not to analyze WHY people return
> products after the fact. Your job is to predict WHICH orders will be returned
> BEFORE they ship — from signals visible at the moment of purchase. Find the
> patterns that predict regret, impulse, and mismatch.

## Setup
- CSV is in `data/orders.csv`
- 15,000 orders across 6 product categories
- Columns: order_id, order_date, purchase_hour, is_late_night, is_weekend, category, order_total, quantity, device, channel, payment_method, customer_type, previous_orders, previous_returns, previous_return_rate, used_coupon, discount_percent, pages_viewed, time_browsing_minutes, items_compared, reviews_read, time_in_cart_minutes, cart_additions, cart_removals, is_gift, multiple_sizes_ordered, delivery_days, free_shipping, returned (1/0), return_reason
- Categories: Electronics, Fashion, Beauty, Home & Kitchen, Sports, Books & Media
- Devices: Mobile, Desktop, Tablet, App
- Channels: Organic Search, Paid Ads, Social Media, Email, Direct, Referral
- Payment: Credit Card, Debit Card, Digital Wallet, Buy Now Pay Later, Gift Card
- Customer Types: New, Returning, Frequent, VIP
- Install packages: pandas matplotlib numpy seaborn pillow scikit-learn
- Save all outputs in `output/`
- Use ALL rows

---

## What to Analyze

### 1. The Return Reality Check
- Overall return rate
- Return rate by category — which products come back most?
- Total cost of returns (assume $15 processing cost per return + lost revenue)
- Return reasons breakdown — what do people say?
- Set the baseline: how big is this problem?

### 2. The Time-of-Day Signal
- Return rate by hour of purchase (0-23)
- Late night purchases (10pm-5am) vs daytime — return rate difference
- Weekend vs weekday return rates
- Find the EXACT hours where return risk is highest
- "Orders placed at 2am have X% return rate vs 2pm at Y%"

### 3. The Impulse Detector
- Browse time before purchase vs return rate
- Under 3 minutes = impulse buy? What's the return rate?
- Reviews read vs return rate (informed buyer = fewer returns?)
- Items compared vs return rate
- Cart removals vs return rate (indecision signal)
- Build an "impulse score" from these signals

### 4. The Discount Curse (Returns Edition)
- Return rate for coupon users vs non-coupon users
- Return rate at different discount levels (5%, 15%, 25%, 35%+)
- At what discount level do returns spike?
- "Buy Now Pay Later" vs other payment methods — return rate comparison
- Calculate: net profit after returns for discounted vs full-price orders

### 5. The Fashion Problem
- Fashion has the highest return rate — deep dive
- Multiple sizes ordered = guaranteed returns
- Return rate for multiple_sizes_ordered = 1 vs 0
- Most common return reason by category
- What makes fashion returns different from electronics returns?

### 6. The Customer History Signal
- Previous return rate vs current order return probability
- Serial returners — customers with >30% return history
- New customers vs VIP customers — who returns more?
- Can you predict returns from customer history alone?

### 7. The Device & Channel Signal
- Return rate by device (Mobile vs Desktop vs Tablet vs App)
- Return rate by acquisition channel
- Mobile + impulse combo — is it the worst?
- Desktop + long browse — is it the safest?
- Which channel brings the most "returner" customers?

### 8. Build a Prediction Model
- Use scikit-learn to build a return prediction model
- Features: purchase_hour, is_late_night, category, device, payment_method, time_browsing_minutes, reviews_read, items_compared, cart_removals, used_coupon, discount_percent, previous_return_rate, is_gift, multiple_sizes_ordered, delivery_days
- Train/test split (80/20)
- Show feature importance — which signals predict returns best?
- Calculate prediction accuracy, precision, recall
- Score every order with a "return risk %" (0-100)
- Create risk tiers: High Risk (>60%), Medium (30-60%), Low (<30%)

### 9. The Dollar Impact
- How much money is lost to returns annually?
- If we flagged high-risk orders and intervened (confirmation step, no free return shipping) — how much would we save?
- If we stopped offering 30%+ discounts — how many returns disappear?
- Calculate ROI of implementing this prediction system

### 10. Strategic Recommendations
Based on ALL analyses:
- **FLAG** — High-risk orders to add confirmation steps before shipping
- **FIX** — Categories/channels/times with fixable return problems
- **LIMIT** — Discount levels and payment methods that drive returns
- **MONITOR** — Serial returners who abuse the system
- **KEEP** — Low-risk segments to leave alone
- Estimated savings from each recommendation

---

## Output Files

### 1. `output/dashboard.html`
Dark-themed return intelligence dashboard (single self-contained HTML file):
- **Hero**: total orders, return rate, total returns cost, #1 return signal, prediction accuracy
- **The Time Bomb Chart**: return rate by hour of day — bar chart showing which hours are dangerous
- **The Impulse Map**: scatter or grouped chart — browse time vs return rate, review count vs return rate
- **The Discount Curse**: line chart — discount % vs return rate (clear upward curve)
- **Category Breakdown**: return rates by category with Fashion highlighted
- **Payment Risk**: return rates by payment method — Buy Now Pay Later highlighted
- **Feature Importance**: horizontal bar chart from the ML model — which signals matter most
- **Risk Tier Distribution**: how many orders in High/Medium/Low risk buckets
- **Dollar Impact**: cost of returns + projected savings from intervention
- **Strategy Board**: FLAG / FIX / LIMIT / MONITOR / KEEP recommendations
- Responsive, dark background (#0f0f0f), card-based layout

### 2. `output/time_bomb.png`
Bar chart: return rate by hour of purchase (0-23). Highlight the danger zone (late night hours in red). Show the safe zone (afternoon hours in green).

### 3. `output/impulse_map.png`
Multi-panel chart: browse time vs return rate, reviews read vs return rate, cart removals vs return rate. Show clear correlations — less research = more returns.

### 4. `output/discount_curse.png`
Line chart: discount percentage (X) vs return rate (Y). Clear upward curve. Mark the "danger zone" where returns spike. Show break-even point.

### 5. `output/category_returns.png`
Horizontal bar chart: return rate by category. Fashion at top. Show return reasons as stacked segments within each bar.

### 6. `output/feature_importance.png`
Horizontal bar chart from the ML model: which features predict returns best. Rank all features by importance. This is the "these are the signals that matter" chart.

### 7. `output/risk_tiers.png`
Distribution chart: High Risk / Medium Risk / Low Risk order counts and what percentage of actual returns each tier catches.

### 8. `output/return_report.md`
Business report:
- Executive summary: "X% of orders are returned, costing $Y annually"
- Time-of-day analysis with danger hours
- Impulse buying signals ranked
- The discount-returns connection with break-even point
- Category deep dive (fashion problem)
- Payment method risks
- Customer history as predictor
- ML model results — accuracy, top features
- Risk tier breakdown
- Dollar impact and ROI of prediction system
- Strategic recommendations: FLAG / FIX / LIMIT / MONITOR / KEEP
- 5 specific actions to reduce returns by 20%+
- Final verdict: #1 return predictor, biggest fixable problem, estimated annual savings

---

## System Architecture

```
Layer 1: Problem     → 25% of orders come back. Most businesses only find out AFTER shipping.
Layer 2: Data        → 15K orders with every purchase signal tracked
Layer 3: Engine      → 10 modules: Reality Check, Time Signal, Impulse Detector, Discount Curse,
                       Fashion Problem, Customer History, Device/Channel, Prediction Model,
                       Dollar Impact, Strategy
Layer 4: Prediction  → ML model scores every order 0-100 return risk BEFORE shipping
Layer 5: Decisions   → Flag, Fix, Limit, Monitor, Keep
Layer 6: Agentic     → AI predicts returns, human decides intervention strategy
Layer 7: Outputs     → Dashboard, risk scores, prediction model, strategy report
```

---

## Rules
1. Read this file FIRST
2. Install packages silently (`pip install -q`)
3. Write and run `analyzer.py` — fix errors yourself
4. Use ALL data
5. Create ALL 8 output files
6. End with: #1 return predictor signal, biggest fixable return problem, prediction accuracy, estimated annual savings from implementation

## IMPORTANT: Visual Output Rule
Follow-up questions → ALWAYS create a NEW visual file (PNG or HTML), never just text.
