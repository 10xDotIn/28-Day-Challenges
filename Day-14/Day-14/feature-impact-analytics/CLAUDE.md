# Feature Impact Analytics — Product Intelligence Analyzer

> You are a senior product analytics expert at a top-tier product company.
> Your job is not to describe data — but to find which features actually drive
> user behavior, retention, and revenue. Analyze `data/product_usage.csv`
> and separate signal from noise. Find what matters, what misleads, and what's hidden.

## Setup
- CSV is in `data/product_usage.csv`
- ~19,000 rows across 10,000 unique users
- Each row = one feature interaction in a user session
- Columns: user_id, session_id, feature_used, time_spent_seconds, actions_count, returned_within_7d (1/0), purchased (1/0), revenue, user_type, sessions_last_30d, days_since_last_visit
- Features: search, product_view, cart, wishlist, recommendations, reviews, notifications, offers, filters, compare, share, live_chat
- User Types: New, Regular, Power, Inactive, VIP
- Install packages: pandas matplotlib numpy seaborn pillow
- Save all outputs in `output/`
- Use ALL rows — do not sample

---

## What to Analyze

### 1. Feature Truth Engine — Does This Feature Actually Matter?
For EACH feature:
- Split users into two groups: those who used it vs those who didn't
- Compare retention rate (returned_within_7d) between both groups
- Compare purchase rate between both groups
- Calculate LIFT: how much does using this feature increase retention/purchase?
- A feature with high usage but low lift = vanity feature
- A feature with low usage but high lift = hidden gold

### 2. Behavior Shift Detection
Does using a specific feature CHANGE what users do next?
- Users who use "wishlist" → do they return more?
- Users who use "notifications" → do they purchase more?
- Users who use "compare" → higher average revenue?
- Show the behavioral shift for each feature as a clear before/after

### 3. Hidden Gold Detection
Find features with:
- Low usage (< 15% of users)
- BUT high retention lift OR high purchase lift
- These are growth levers that most users haven't discovered
- Rank them by untapped potential
- Calculate: if usage doubled, how much would retention/revenue increase?

### 4. Vanity Trap Detection
Find features with:
- High usage (> 50% of users)
- BUT low or zero retention/purchase lift
- These features feel important but contribute nothing
- They consume engineering resources without driving growth
- Flag them clearly with wasted investment estimate

### 5. Feature Funnel Analysis
Track the journey: Feature → Return → Purchase
- For each feature: what % of users return? Of those, what % purchase?
- Where does the funnel break for each feature?
- Which features have the best full-funnel conversion?
- Which features lose users between return and purchase?

### 6. Segment Intelligence
Which features work for which user types?
- For each segment (New, Regular, Power, Inactive, VIP):
  - Which features drive the most retention?
  - Which features drive the most revenue?
  - Which features are useless for this segment?
- Key question: does "wishlist" work better for New users or VIP users?
- Find segment-specific growth levers

### 7. Feature Power Score
Create a composite score for each feature:
- 40% weight: retention lift (returned_within_7d improvement)
- 40% weight: purchase lift (purchase rate improvement)
- 20% weight: revenue per user improvement
- Rank ALL 12 features from MOST IMPACTFUL to MOST USELESS
- This is the master ranking that drives product decisions

### 8. Product Strategy Engine
Based on ALL analyses above, output clear decisions:
- **PUSH** — High impact, invest more (top features by power score)
- **IMPROVE** — High potential but underperforming (high lift, low usage or broken funnel)
- **MONITOR** — Moderate impact, maintain current investment
- **REMOVE** — Low impact, consuming resources (vanity traps)
- Include estimated business impact for each decision

---

## Output Files

### 1. `output/dashboard.html`
Dark-themed product analytics dashboard (single self-contained HTML file):
- **Hero section**: total users, overall retention rate, overall purchase rate, total revenue, number of features analyzed
- **Feature Power Ranking**: horizontal bar chart ranking all 12 features by impact score — color coded (green = push, yellow = improve, red = remove)
- **The Truth Chart**: grouped bar chart showing for each feature: usage rate vs retention lift vs purchase lift — this reveals vanity vs gold
- **Hidden Gold Alert**: styled cards highlighting low-usage high-impact features with growth potential numbers
- **Vanity Trap Alert**: styled cards highlighting high-usage low-impact features with wasted resource estimate
- **Retention Comparison**: for each feature, side-by-side bars: retention WITH feature vs WITHOUT feature
- **Purchase Comparison**: same as above but for purchase rate
- **Segment Heatmap**: features on y-axis, segments on x-axis, color = effectiveness
- **Feature Funnel**: funnel visualization showing Feature → Return → Purchase conversion for top features
- **Product Strategy Board**: visual board with PUSH / IMPROVE / MONITOR / REMOVE columns
- **Key Insights**: 5 insight cards with business impact numbers
- Responsive design, professional styling, dark background (#0f0f0f), card-based layout

### 2. `output/feature_truth.png`
The most important chart: for each feature, show two grouped bars:
- Retention rate of users who used it vs didn't
- Purchase rate of users who used it vs didn't
- The GAP between bars = true impact
- Sort by impact (biggest gap first)
- Clear labels, professional styling

### 3. `output/hidden_gold.png`
Scatter plot or quadrant chart:
- X-axis: usage rate
- Y-axis: impact score (retention + purchase lift)
- Each dot = one feature, labeled
- Top-left quadrant = HIDDEN GOLD (low usage, high impact)
- Bottom-right quadrant = VANITY TRAP (high usage, low impact)
- Color code quadrants

### 4. `output/vanity_features.png`
Bar chart comparing usage rank vs impact rank for each feature.
Features where usage rank >> impact rank = vanity traps.
Features where impact rank >> usage rank = hidden opportunities.
Show the disconnect clearly.

### 5. `output/feature_funnel.png`
Funnel visualization for top 6 features:
- Stage 1: Users who used feature (100%)
- Stage 2: Users who returned (% of stage 1)
- Stage 3: Users who purchased (% of stage 2)
- Side-by-side funnels for comparison
- Highlight where each feature's funnel breaks

### 6. `output/segment_heatmap.png`
Heatmap: features (rows) x segments (columns)
- Cell value = retention lift or purchase lift for that feature in that segment
- Color intensity = impact strength
- Annotate cells with actual values
- This shows: "wishlist works for VIP but not for Inactive"

### 7. `output/power_ranking.png`
Horizontal bar chart ranking all 12 features by composite power score.
- Color: green (top 4), yellow (middle 4), red (bottom 4)
- Show score breakdown: retention component + purchase component + revenue component
- Clear, presentation-ready

### 8. `output/product_strategy.md`
Business report:
- Executive summary (3 bullet points)
- Feature truth analysis with numbers
- Hidden gold features with growth potential
- Vanity trap features with waste estimate
- Segment-specific recommendations
- Feature power ranking (table)
- Product strategy: PUSH / IMPROVE / MONITOR / REMOVE with reasoning
- 5 specific actions to increase retention and revenue
- ROI estimate: if recommendations are followed, projected improvement
- Final verdict: most powerful feature, most misleading feature, biggest missed opportunity

---

## Rules
1. Read this file FIRST before doing anything
2. Install packages silently (`pip install -q`)
3. Write and run `analyzer.py` — fix errors yourself, do not stop
4. Use ALL data — do not sample or skip rows
5. Create ALL 8 output files
6. End with: most powerful feature, most misleading feature, biggest missed opportunity, 1 decision that increases revenue immediately

## IMPORTANT: Visual Output Rule
Follow-up questions from the user → ALWAYS create a NEW visual file (PNG or HTML), never just text output.
