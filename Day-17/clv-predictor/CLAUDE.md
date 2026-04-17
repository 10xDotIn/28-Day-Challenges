# Customer Lifetime Value Predictor

> You are a customer intelligence expert. Your job is to predict the future value
> of every customer based on their early behavior — find who will become a VIP,
> who is a one-time buyer disguised as a customer, who is fading away, and which
> acquisition channels bring customers that actually stay.

## Setup
- CSV is in `data/customers.csv`
- 8,000 customers with full behavioral profiles
- Columns: customer_id, customer_archetype, acquisition_channel, join_date, first_order_value, first_order_discount_pct, first_order_category, total_orders, lifetime_revenue, avg_order_value, days_to_second_order, pages_viewed_first_30d, sessions_first_30d, email_opens_first_30d, items_browsed_first_30d, returns_count, support_tickets, days_since_last_order, churned (1/0), predicted_3yr_clv
- 6 Archetypes: Future VIP, Loyal Regular, Promising New, Discount Addict, One-and-Done, Fading Away
- 5 Channels: organic, paid_ads, social_media, email, referral
- 5 Categories: Electronics, Fashion, Beauty, Health, Home
- Install packages: pandas matplotlib numpy seaborn pillow scikit-learn
- Save all outputs in `output/`
- Use ALL rows

---

## What to Analyze

### 1. The Customer Reality Check
- Distribution of customer archetypes
- Revenue contribution by archetype (who ACTUALLY pays the bills?)
- Future VIPs are 8% of customers but might be 50%+ of future value
- One-and-Done are 25% of customers but worth almost nothing
- Show the concentration: how much revenue comes from the top 10% of customers?

### 2. First Purchase DNA
The first order predicts everything. Analyze:
- First order value by archetype — do VIPs start big or small?
- First order discount — do heavy discounts attract the wrong customers?
- First order category — do certain categories produce more loyal customers?
- Acquisition channel — which channels bring future VIPs vs one-time buyers?
- Build a "first purchase profile" that predicts archetype

### 3. The 30-Day Crystal Ball
Early behavioral signals that predict lifetime value:
- Pages viewed in first 30 days
- Sessions in first 30 days
- Email opens in first 30 days
- Items browsed in first 30 days
- Days to second order (critical — fast second order = likely VIP)
- Correlate each signal with predicted_3yr_clv
- Which signals are the strongest predictors?

### 4. Channel Quality Score
Not all channels bring equal customers:
- Average CLV by acquisition channel
- Channel that brings most customers vs channel that brings BEST customers
- paid_ads brings volume but what quality?
- referral and email might bring fewer but far more valuable customers
- Calculate: cost-adjusted channel value (if you know paid_ads costs more, factor that in)
- Which channel should you SCALE and which should you RETHINK?

### 5. The Discount Curse
Heavy first-order discounts attract the wrong customers:
- CLV of customers acquired with 0-5% discount vs 10-20% vs 20%+ discount
- Discount Addicts vs Full-Price buyers — lifetime value comparison
- Calculate: every 10% increase in first-order discount = how much CLV is lost?
- Show the break-even: at what discount level do you START losing money long-term?

### 6. Churn Early Warning System
Which behavioral signals predict churn?
- Days since last order by archetype
- Order frequency trend (increasing vs decreasing)
- Churned vs not-churned comparison across all behavioral metrics
- Build a churn risk profile: what does a "about to leave" customer look like?
- How many "Fading Away" customers can be saved?

### 7. CLV Prediction Model
Build a simple predictive model:
- Use first purchase data + 30-day behavior to predict 3yr CLV
- Features: first_order_value, first_order_discount_pct, acquisition_channel, pages_viewed, sessions, email_opens, days_to_second_order
- Show which features have the highest predictive power
- Create CLV tiers: Platinum (top 10%), Gold (next 20%), Silver (next 30%), Bronze (bottom 40%)
- Assign every customer to a tier

### 8. Strategic Recommendations
Based on ALL analyses:
- **INVEST** — Future VIPs and Loyal Regulars. Increase spend on retention.
- **NURTURE** — Promising New customers. They could go either way.
- **CONVERT** — Discount Addicts. Wean them off discounts gradually.
- **LET GO** — One-and-Done. Stop spending retention budget on them.
- **SAVE** — Fading Away. Identify and intervene before they churn.
- Estimated revenue impact of treating each group correctly

---

## Output Files

### 1. `output/dashboard.html`
Dark-themed customer intelligence dashboard (single self-contained HTML file):
- **Hero**: total customers, avg CLV, total predicted 3yr value, churn rate, top 10% customer concentration
- **The Customer Pyramid**: visualization showing archetypes stacked by value — VIPs at top (small count, huge value), One-and-Done at bottom (huge count, no value)
- **First Purchase DNA**: what first-order signals predict VIP vs one-time buyer
- **The 30-Day Crystal Ball**: correlation chart — which early behaviors predict high CLV
- **Channel Quality**: CLV by channel — which channels bring the best customers
- **The Discount Curse**: CLV vs first-order discount level — clear downward trend
- **Churn Risk Map**: scatter or chart showing at-risk customers
- **CLV Tier Distribution**: how many customers in Platinum/Gold/Silver/Bronze
- **Strategy Board**: INVEST / NURTURE / CONVERT / LET GO / SAVE with customer counts
- **Key Insights**: 5 insight cards
- Responsive, dark background (#0f0f0f), card-based layout

### 2. `output/customer_pyramid.png`
Pyramid/treemap showing: archetype name, customer count, % of total, total CLV, % of total CLV. Future VIPs = tiny slice of customers, massive slice of value.

### 3. `output/first_purchase_dna.png`
Grouped comparison: for each archetype, show avg first order value, avg discount, top acquisition channel. What does a VIP's first order look like vs a One-and-Done?

### 4. `output/crystal_ball.png`
Correlation heatmap or bar chart: each 30-day behavioral signal vs CLV. Which signals matter most? Days to second order is likely the strongest.

### 5. `output/channel_quality.png`
Bar chart: avg CLV by acquisition channel. paid_ads might bring the most customers but the lowest CLV. referral might bring fewest but highest CLV.

### 6. `output/discount_curse.png`
Line chart or scatter: X = first order discount %, Y = avg 3yr CLV. Clear downward curve showing heavier discounts = lower lifetime value.

### 7. `output/clv_tiers.png`
Distribution chart showing Platinum/Gold/Silver/Bronze customer tiers with counts and total value per tier.

### 8. `output/clv_report.md`
Business report:
- Executive summary: "8,000 customers. $X in predicted 3yr value. But Y% of that comes from just Z% of customers."
- Customer archetype breakdown with value
- First purchase DNA — what predicts a VIP
- The 30-day signals that matter
- Channel quality ranking
- The discount problem with numbers
- Churn early warning signals
- CLV tier breakdown
- Strategic recommendations: INVEST / NURTURE / CONVERT / LET GO / SAVE
- 5 specific actions to increase total CLV
- Final verdict: most valuable customer type, worst acquisition channel, biggest retention opportunity

---

## System Architecture

```
Layer 1: Problem     → Not all customers are equal. Most businesses treat them the same.
Layer 2: Data        → 8K customers, full behavioral profiles, every signal tracked
Layer 3: Engine      → 8 modules: Reality Check, First Purchase DNA, 30-Day Crystal Ball,
                       Channel Quality, Discount Curse, Churn Warning, CLV Model, Strategy
Layer 4: Insights    → High early engagement + low discount + organic/referral = future VIP
Layer 5: Decisions   → Invest, Nurture, Convert, Let Go, Save
Layer 6: Agentic     → AI predicts lifetime value, human decides resource allocation
Layer 7: Outputs     → Dashboard, pyramid, DNA chart, predictions, strategy report
```

---

## Rules
1. Read this file FIRST
2. Install packages silently (`pip install -q`)
3. Write and run `analyzer.py` — fix errors yourself
4. Use ALL data
5. Create ALL 8 output files
6. End with: most valuable customer type, worst acquisition channel, strongest CLV predictor, 1 change that increases total CLV immediately

## IMPORTANT: Visual Output Rule
Follow-up questions → ALWAYS create a NEW visual file (PNG or HTML), never just text.
