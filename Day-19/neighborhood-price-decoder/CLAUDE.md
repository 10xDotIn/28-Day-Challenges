# Neighborhood Price Decoder — Real Estate Intelligence

> You are a real estate data scientist. Your job is to decode what ACTUALLY drives
> property prices — not just size and bedrooms, but the invisible neighborhood factors
> that add or subtract tens of thousands of dollars. Find overpriced listings,
> hidden deals, and the exact dollar value of every neighborhood feature.

## Setup
- CSV is in `data/listings.csv`
- 12,000 property listings across 12 neighborhoods
- Columns: listing_id, neighborhood, property_type, sqft, bedrooms, bathrooms, floor, year_built, condition, has_parking, has_gym, has_pool, has_doorman, metro_distance_miles, school_rating, crime_index, restaurants_nearby, park_access_score, noise_level, listing_price, price_per_sqft, estimated_fair_value, price_gap_percent, days_on_market, sold, predicted_1yr_appreciation
- Property types: Apartment, Condo, Townhouse, Studio, Penthouse
- Conditions: New, Renovated, Good, Average, Needs Work
- 12 Neighborhoods with unique characteristics
- Install packages: pandas matplotlib numpy seaborn pillow scikit-learn
- Save all outputs in `output/`
- Use ALL rows

---

## What to Analyze

### 1. The Neighborhood Price Map
- Average price per sqft by neighborhood
- Price range (min to max) per neighborhood
- Which neighborhoods are most and least expensive?
- Rank all 12 neighborhoods by value
- Show the price gradient across neighborhoods

### 2. What Actually Drives Price? (Feature Importance)
This is the core analysis. For EVERY factor, calculate its dollar impact:
- Metro distance: every 0.1 mile further = how much $ lost?
- School rating: every 1 point higher = how much $ gained?
- Crime index: every 10 points higher = how much $ lost?
- Park access: every 1 point = how much $ gained?
- Noise level: every 10 points higher = how much $ lost?
- Floor level: every floor higher = how much $ gained?
- Parking: having parking adds how much $?
- Gym: adds how much?
- Pool: adds how much?
- Doorman: adds how much?
- Condition: New vs Needs Work = how much $ difference?
- Year built: every decade newer = how much?
- Build a regression model and show feature importance
- Rank ALL factors by dollar impact — from biggest to smallest

### 3. The Overpriced / Underpriced Detector
- Compare listing_price vs estimated_fair_value
- Find the most OVERPRICED listings (biggest positive gap)
- Find the most UNDERPRICED listings (biggest negative gap) — these are the deals
- How long do overpriced listings sit on market?
- Do underpriced listings sell faster?
- Show: days_on_market vs price_gap_percent correlation

### 4. The Metro Premium
Deep dive into metro distance:
- Price per sqft at 0.2 miles vs 0.5 vs 1.0 vs 2.0 vs 4.0 miles from metro
- The exact dollar cost of living 1 mile further from metro
- At what distance does the metro premium disappear?
- "Moving 0.5 miles from the station saves you $X but costs you Y minutes daily"

### 5. The School Rating Tax
Families pay a massive premium for good schools:
- Price per sqft by school rating (4 to 9)
- The exact dollar value of each school rating point
- Which neighborhoods have the best school-to-price ratio?
- "A school rating of 9 vs 7 adds $X to your property — is it worth it?"

### 6. The Safety Premium
Low crime = higher prices. But how much exactly?
- Price vs crime index correlation
- The dollar cost of crime — every 10 points on crime index = how much?
- Neighborhoods where you're paying for safety vs getting it free
- Compare: safe-but-far vs close-but-risky — which costs more?

### 7. The Smart Buyer Score
Score every listing on a "deal quality" scale:
- 30% weight: price vs fair value gap (bigger undervalue = better deal)
- 25% weight: predicted 1yr appreciation (higher growth = better)
- 25% weight: school rating + safety combo
- 20% weight: metro access + amenities
- Rank all listings from BEST DEAL to WORST DEAL
- Find the top 20 hidden gems

### 8. Neighborhood Investment Recommendations
Based on ALL analyses:
- **BUY NOW** — Underpriced neighborhoods with high growth trend
- **PREMIUM BUT WORTH IT** — Expensive but strong fundamentals (schools, safety, metro)
- **OVERPRICED RISK** — Prices higher than fundamentals justify
- **AVOID** — High crime, poor schools, no growth, overpriced
- **HIDDEN GEM** — Affordable now but growth signals are strong
- Estimated 1-year and 3-year return per neighborhood

---

## Output Files

### 1. `output/dashboard.html`
Dark-themed real estate intelligence dashboard (single self-contained HTML file):
- **Hero**: total listings, avg price, avg price/sqft, % overpriced, % underpriced, avg 1yr appreciation
- **Neighborhood Price Map**: bar chart or heatmap of all 12 neighborhoods by avg price/sqft
- **What Drives Price**: horizontal bar chart of every factor ranked by dollar impact — metro distance, school, crime, parking, pool, floor, condition, etc.
- **The Hidden Deals**: table of top 10 most underpriced listings with gap % and details
- **The Overpriced Traps**: table of top 10 most overpriced listings
- **Metro Premium Curve**: line chart showing price drop as metro distance increases
- **School Tax Chart**: price per sqft by school rating
- **Crime vs Price**: scatter plot
- **Smart Buyer Top Deals**: top 20 listings by deal score
- **Investment Board**: BUY NOW / PREMIUM / OVERPRICED / AVOID / HIDDEN GEM neighborhoods
- **Key Insights**: 5 insight cards
- Responsive, dark background (#0f0f0f), card-based layout

### 2. `output/neighborhood_map.png`
Bar chart: all 12 neighborhoods ranked by avg price/sqft. Color coded by investment recommendation. Show price range bands.

### 3. `output/price_drivers.png`
Horizontal bar chart: every factor ranked by dollar impact on price. Metro distance, school rating, crime, pool, parking, floor, condition, etc. This is THE chart — shows exactly what you're paying for.

### 4. `output/overpriced_underpriced.png`
Scatter plot: X = listing price, Y = fair value. Dots above the diagonal = overpriced. Below = underpriced. Color by neighborhood. Highlight the biggest gaps.

### 5. `output/metro_premium.png`
Line chart: X = distance from metro (0.1 to 4+ miles), Y = avg price per sqft. Clear downward curve showing exactly how much each mile costs.

### 6. `output/school_tax.png`
Bar chart: school rating (4-9) vs avg price per sqft. Show the dollar premium of each rating point.

### 7. `output/deal_finder.png`
Top 20 deals ranked by Smart Buyer Score. Show listing details, gap %, appreciation forecast, and why it's a deal.

### 8. `output/investment_report.md`
Business report:
- Executive summary: "12,000 listings analyzed. X% are overpriced. Y% are hidden deals."
- Neighborhood ranking with price/sqft and growth trends
- What drives price — every factor ranked with exact dollar amounts
- Top 10 overpriced traps to avoid
- Top 10 hidden deals to grab
- The metro premium — is proximity worth the cost?
- The school rating tax — are you overpaying for schools?
- The safety premium — crime's real dollar impact
- Neighborhood investment recommendations
- 5 rules for smart property buying based on the data
- Final verdict: best value neighborhood, most overpriced neighborhood, biggest growth opportunity

---

## System Architecture

```
Layer 1: Problem     → Property prices seem random. They're not. Every dollar is explained by something.
Layer 2: Data        → 12K listings, 12 neighborhoods, every feature tracked
Layer 3: Engine      → 8 modules: Neighborhood Map, Price Drivers, Over/Under Detection,
                       Metro Premium, School Tax, Safety Premium, Deal Scorer, Investment Strategy
Layer 4: Insights    → "0.5 miles from metro = $45K premium. School rating 9 vs 7 = $62K."
Layer 5: Decisions   → Buy Now, Premium Worth It, Overpriced Risk, Avoid, Hidden Gem
Layer 6: Agentic     → AI decodes every price factor, human decides where to invest
Layer 7: Outputs     → Dashboard, charts, deal finder, investment report
```

---

## Rules
1. Read this file FIRST
2. Install packages silently (`pip install -q`)
3. Write and run `analyzer.py` — fix errors yourself
4. Use ALL data
5. Create ALL 8 output files
6. End with: most overpriced neighborhood, best value neighborhood, #1 price driver, best deal in the dataset

## IMPORTANT: Visual Output Rule
Follow-up questions → ALWAYS create a NEW visual file (PNG or HTML), never just text.
