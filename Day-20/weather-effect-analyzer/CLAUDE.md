# The Weather Effect Analyzer

> You are a business intelligence expert who understands how weather silently
> controls revenue. Your job is to decode the exact dollar impact of every weather
> condition on every type of business — and find the patterns that business owners
> never see because they blame marketing, not the sky.

## Setup
- CSV is in `data/weather_business.csv`
- 7,300 rows — 730 days (2 years) × 10 business types
- Columns: date, day_of_week, is_weekend, is_holiday, season, weather_condition, temperature_f, humidity_pct, wind_mph, precipitation_inches, is_raining, is_snowing, business_type, revenue, customer_count, online_order_pct, cancellation_rate
- Weather conditions: Sunny, Cloudy, Light Rain, Heavy Rain, Snow, Windy, Hot & Humid, Thunderstorm, Foggy, Clear & Cold
- Business types: Food Delivery, Restaurant Dine-In, Coffee Shop, Ice Cream / Cold Drinks, Gym / Fitness, E-Commerce, Retail Store, Ride-Hailing, Movie Theater, Outdoor Events
- Install packages: pandas matplotlib numpy seaborn pillow scikit-learn
- Save all outputs in `output/`
- Use ALL rows

---

## What to Analyze

### 1. The Weather Revenue Map
For each weather condition:
- Average revenue across all businesses
- Which weather makes the MOST money overall?
- Which weather kills revenue the most?
- Rank all 10 weather conditions by total business impact

### 2. Winners and Losers — Who Benefits from Bad Weather?
For each business type, compare revenue in good weather vs bad weather:
- Sunny day revenue vs Rainy day revenue — the % change
- Some businesses LOVE rain (food delivery, ride-hailing, e-commerce)
- Some businesses DIE in rain (outdoor events, restaurants, retail)
- Create a clear Winners vs Losers matrix
- Calculate exact dollar gained/lost per rainy day for each business

### 3. The Temperature Sweet Spot
Revenue vs temperature for each business:
- At what temperature does each business peak?
- Ice cream peaks at 85-95°F — obvious. But at what temp does food delivery peak?
- Find the "sweet spot" temperature range for each business
- Find the "danger zone" — temperatures that kill revenue
- Show the revenue curve across temperature ranges

### 4. The Rain Tax
Deep dive into rain's impact:
- Light rain vs heavy rain vs thunderstorm — different impacts?
- How much revenue does each inch of precipitation cost/add per business?
- Customer count change in rain
- Online order percentage spike in rain (do people shift to online?)
- Cancellation rate spike in bad weather
- Calculate: total annual revenue lost to rain per business

### 5. The Snow Effect
Snow is different from rain:
- Which businesses get destroyed by snow?
- Which ones benefit?
- Customer count in snow vs normal
- Cancellation rates in snow
- Is snow worse than heavy rain for business?

### 6. Weekend × Weather Combo
The interaction between day of week and weather:
- Rainy weekend vs rainy weekday — different impact?
- Sunny weekend is obvious gold — but HOW much more?
- The worst combo: what weather + day destroys revenue most?
- The best combo: what weather + day maximizes revenue?

### 7. The Seasonal Weather Playbook
Weather affects businesses differently by season:
- Rain in summer vs rain in winter — same impact?
- Cold snap in spring vs cold in winter — which hurts more?
- Build a season × weather matrix for each business
- Find: which seasonal weather events are most costly?

### 8. Strategic Recommendations
Based on ALL analyses:
- **PREPARE** — High-impact weather events to plan for (staffing, inventory, marketing)
- **CAPITALIZE** — Weather conditions that boost your business (run promos when it rains)
- **HEDGE** — How to offset bad weather losses (shift to online, adjust pricing)
- **IGNORE** — Weather conditions that don't actually affect revenue (stop blaming weather)
- Dollar impact estimates for each recommendation

---

## Output Files

### 1. `output/dashboard.html`
Dark-themed weather intelligence dashboard (single self-contained HTML file):
- **Hero**: total days analyzed, avg daily revenue, best weather day, worst weather day, total rain days impact
- **Weather Revenue Map**: bar chart of all 10 weather conditions by avg revenue
- **Winners & Losers Matrix**: heatmap — businesses (rows) × weather conditions (columns), color = revenue change %
- **Temperature Curve**: line chart showing revenue vs temperature for top 5 businesses
- **Rain Tax Calculator**: for each business, show $ lost or gained per rainy day
- **Snow Impact**: comparison chart — snow day revenue vs normal day
- **Weekend × Weather**: grouped bars showing best and worst combos
- **Seasonal Playbook**: season × weather heatmap
- **Strategy Board**: PREPARE / CAPITALIZE / HEDGE / IGNORE recommendations
- **Key Insights**: 5 insight cards with dollar amounts
- Responsive, dark background (#0f0f0f), card-based layout

### 2. `output/weather_revenue_map.png`
Bar chart: all 10 weather conditions ranked by average revenue. Color coded — green (revenue boost), red (revenue killer).

### 3. `output/winners_losers.png`
Heatmap: businesses (rows) × weather conditions (columns). Cell = % revenue change from average. Green = boost, red = loss. This is THE chart — shows exactly who wins and loses in every weather.

### 4. `output/temperature_curve.png`
Multi-line chart: temperature (X-axis) vs revenue (Y-axis) for each business. Each business gets its own colored line. Show where each one peaks and crashes.

### 5. `output/rain_tax.png`
Horizontal bar chart: for each business, show the dollar amount gained or lost per rainy day. Food delivery and ride-hailing on the positive side. Outdoor events and restaurants on the negative side.

### 6. `output/snow_impact.png`
Grouped bar chart: normal day revenue vs snow day revenue for each business. Show the % drop or boost.

### 7. `output/best_worst_combos.png`
Bar chart: top 5 best weather+day combos and top 5 worst combos for revenue. "Sunny Saturday" vs "Thunderstorm Monday" type comparisons.

### 8. `output/weather_report.md`
Business report:
- Executive summary: "Weather silently controls $X of your annual revenue"
- Weather revenue ranking with dollar amounts
- Winners and losers matrix with specific recommendations
- The temperature sweet spot for each business
- The rain tax — annual cost of rain per business
- Snow impact analysis
- Best and worst weather+day combinations
- Seasonal weather playbook
- Strategic recommendations: Prepare, Capitalize, Hedge, Ignore
- 5 specific weather-based actions each business should take
- Final verdict: most weather-sensitive business, most weather-proof business, biggest hidden weather opportunity

---

## System Architecture

```
Layer 1: Problem     → Weather changes revenue but businesses blame marketing, not the sky
Layer 2: Data        → 730 days × 10 businesses, every weather metric tracked
Layer 3: Engine      → 8 modules: Weather Map, Winners/Losers, Temperature Curves,
                       Rain Tax, Snow Effect, Weekend×Weather, Seasonal Playbook, Strategy
Layer 4: Insights    → "Rain adds $3,200/day to food delivery but costs outdoor events $5,900"
Layer 5: Decisions   → Prepare, Capitalize, Hedge, Ignore
Layer 6: Agentic     → AI finds weather patterns, human adjusts operations
Layer 7: Outputs     → Dashboard, heatmaps, curves, strategy report
```

---

## Rules
1. Read this file FIRST
2. Install packages silently (`pip install -q`)
3. Write and run `analyzer.py` — fix errors yourself
4. Use ALL data
5. Create ALL 8 output files
6. End with: most weather-sensitive business, most weather-proof business, biggest weather opportunity, 1 weather-based action that increases revenue immediately

## IMPORTANT: Visual Output Rule
Follow-up questions → ALWAYS create a NEW visual file (PNG or HTML), never just text.
