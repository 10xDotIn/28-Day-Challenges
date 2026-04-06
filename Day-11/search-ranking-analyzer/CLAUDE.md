# Product Search Ranking Analyzer

> You are a search analytics expert at an e-commerce company.
> Analyze the search ranking data in `data/search_rankings.csv` and find
> where the company is losing money because of bad product rankings.

## Setup
- Data is in `data/search_rankings.csv`
- ~13,500 rows: 15 search queries x 10 products x 90 days
- Columns: date, query, product, position, impressions, clicks, add_to_cart, purchases, revenue, rating, review_count, price, category
- Save all outputs in `output/` folder
- Install missing packages: pandas matplotlib numpy seaborn pillow
- Use ALL rows, no sampling

## What to Analyze

### 1. Position Bias Analysis
- Group by position (1-10) and calculate average CTR (clicks/impressions)
- Show that position 1 gets dramatically more clicks than position 5 or 10
- Calculate: how much of clicking behavior is driven by position vs product quality?
- Create a position vs CTR curve — this shows the "manipulation" effect

### 2. Hidden Gold Products
- Find products with LOW impressions but HIGH conversion rate (purchases/clicks)
- These are buried at low positions but convert amazingly when people find them
- Calculate: how much revenue is the company LOSING by hiding these products?
- Estimate potential revenue if these products were moved to position 1-3

### 3. Fake Winners (Clickbait Products)
- Find products with HIGH CTR but LOW conversion rate
- These get clicks but nobody buys — wasting valuable ranking positions
- Compare CTR vs conversion for all products — find the biggest gaps
- Calculate: how much ranking space is wasted on these products?

### 4. Revenue Impact Analysis
- For each query, calculate total revenue by product
- Compare: current revenue vs estimated revenue if products were ranked by conversion rate
- Show the revenue gap — how much money is being left on the table

### 5. Search Funnel Analysis
- For each query: impressions → clicks → add_to_cart → purchases
- Calculate drop-off at each stage
- Which stage loses the most customers?
- Which queries have the worst funnel?

### 6. Product Ranking Recommendations
- For each query, create a "smart ranking" based on conversion rate + revenue
- Compare current average position vs recommended position for each product
- Show which products should move UP and which should move DOWN
- Calculate estimated revenue increase from re-ranking

### 7. Query Performance Comparison
- Average CTR per query
- Average conversion per query
- Which queries bring the most revenue?
- Which queries have the worst conversion?

## Output Files

### 1. `output/dashboard.html`
Interactive e-commerce analytics dashboard — dark theme, modern design:

**Hero section:**
- Total queries analyzed, total products, total impressions, total clicks, total purchases, total revenue
- Key metric: "Revenue left on the table" — the money lost from bad rankings

**Position Bias section:**
- Line chart: position (x) vs CTR (y) — the position bias curve
- Annotation: "Position 1 gets Xx more clicks than position 5"

**Hidden Gold Products section:**
- Table/cards showing top 10 hidden gems: product name, current position, conversion rate, estimated revenue if promoted
- Green accent — these are opportunities

**Fake Winners section:**
- Table/cards showing top 10 clickbait products: product name, CTR, conversion rate, gap
- Red accent — these are wasting space

**Revenue Impact section:**
- Bar chart: current revenue vs potential revenue per query
- The gap between bars = money being lost

**Search Funnel section:**
- Funnel visualization: impressions → clicks → add_to_cart → purchases
- Drop-off percentages at each stage

**Smart Ranking section:**
- For top 3 queries: current ranking vs recommended ranking side by side
- Show which products move up (green arrows) and down (red arrows)

**Top Quotes/Insights section:**
- 5 key insights as styled cards
- Each insight = one sentence + one number

All in ONE self-contained HTML file. Dark theme. Embed charts as base64 PNG.

### 2. `output/position_bias.png`
Line chart showing position vs CTR curve. Clear downward slope.
Annotate position 1 and position 10 with their CTR values.
Show the dramatic difference.

### 3. `output/hidden_gold.png`
Scatter plot: impressions (x) vs conversion rate (y), dot size = revenue.
Color: green for high conversion, red for low.
Label the top 5 hidden gems.

### 4. `output/fake_winners.png`
Scatter plot: CTR (x) vs conversion rate (y), dot size = impressions.
Highlight the quadrant: high CTR + low conversion = clickbait.
Label the top 5 fake winners.

### 5. `output/revenue_gap.png`
Grouped bar chart: current revenue vs potential revenue per query.
Gap highlighted. Total revenue gap number on top.

### 6. `output/search_funnel.png`
Funnel chart showing: impressions → clicks → add_to_cart → purchases.
With drop-off percentages between each stage.

### 7. `output/ranking_recommendations.png`
For top 5 queries: show current rank vs recommended rank per product.
Green arrows for products moving up. Red arrows for products moving down.

### 8. `output/query_performance.png`
Bar chart comparing all 15 queries by: CTR, conversion rate, and revenue.
Sorted by revenue. Color-coded.

### 9. `output/analysis_report.md`
Business report:
- Executive summary: how much revenue is being lost?
- Position bias findings with numbers
- Top 5 hidden gold products with estimated revenue uplift
- Top 5 fake winners that should be demoted
- Search funnel analysis — where are customers dropping off?
- Revenue gap per query
- Smart ranking recommendations — specific products to move
- 5 actionable business recommendations
- Final verdict: what is the #1 change that would increase revenue most?

## Rules
1. Read this file first
2. Install packages silently
3. Write and run analyzer.py — fix errors yourself
4. Use ALL data, no sampling
5. Create ALL 9 output files
6. End with: total revenue gap, #1 hidden gold product, #1 fake winner

## IMPORTANT: Visual Output Rule
When I ask follow-up questions:
- NEVER just print text in terminal
- ALWAYS create a NEW visual file (PNG or HTML) in output/
- Every answer must produce a file I can open and show on screen
