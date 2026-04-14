# The Data Crime Detective — Anomaly Hunter

> You are a forensic data analyst and fraud investigator. Your job is not to
> find patterns. Your job is to find the WEIRD stuff — the transactions that
> don't fit, the employees acting strangely, the accounts behaving suspiciously.
> Every normal dataset has crimes hiding inside. Find them.

## Setup
- CSV is in `data/transactions.csv`
- ~14,000 transactions with real weird stuff planted inside
- Columns: transaction_id, timestamp, customer_id, employee_id, store_location, category, amount, payment_method, card_last_4, ip_address, country, city, device_type, items_count, discount_applied_pct, is_refund, original_transaction_id, processing_time_seconds, hidden_anomaly_type
- **IMPORTANT**: The `hidden_anomaly_type` column is the GROUND TRUTH. Use it ONLY to validate your detection at the end. Your analysis should discover anomalies WITHOUT relying on this column during detection.
- Anomaly types to hunt: card_testing_fraud, stolen_card, employee_refund_fraud, bot_traffic, price_glitch, data_entry_error, discount_abuse, account_takeover, round_number_fraud
- Install packages: pandas matplotlib numpy seaborn pillow scikit-learn
- Save all outputs in `output/`
- Use ALL rows

---

## What to Hunt

### 1. The Impossible Geography Detective
- Find cards used in multiple countries within short time windows
- Same `card_last_4` appearing in 2+ countries within 2 hours = physically impossible
- These are stolen card signals
- List every suspicious card + timeline of transactions

### 2. The Rapid-Fire Detective (Card Testing)
- Find IPs or cards with many transactions in very short time
- Small dollar amounts + rapid succession = card testing fraud
- Fraudsters test stolen cards with tiny charges before the big hit
- Flag IPs with 20+ transactions under $5 within 1 hour

### 3. The Employee Anomaly Detective
- Compare each employee against their peers
- Refund rates per employee — find outliers (3x+ average)
- Average discount applied per employee — who's giving weird discounts?
- Transactions per hour per employee — who's working "too much"?
- Ghost refunds — refunds without valid `original_transaction_id`
- Flag employees whose behavior deviates >2 standard deviations from peers

### 4. The Bot Detector
- Find transactions with identical processing times (bots don't vary)
- Same IP + high volume + exact time intervals
- Processing time distributions — humans cluster around 2-8 seconds
- Bot traffic often has processing times under 1 second
- Identify IPs with suspicious uniformity

### 5. The Price Glitch Hunter
- Find products sold at prices far below category norms
- Amount distribution per category — look for impossible low values
- Example: a $120 product sold for $12 hundreds of times
- Calculate total revenue lost to glitches

### 6. The Data Corruption Detective
- Find impossible values in the data
- Negative item counts
- Amounts in extreme outlier range (99.99th percentile)
- Future timestamps
- Missing required fields
- These aren't fraud — they're data quality issues that inflate reports

### 7. The Discount Abuse Detective
- Find discounts above normal ceiling (e.g., >50%)
- Which employees apply unusual discounts?
- Cluster of high discounts at specific stores or times
- Calculate money lost to unauthorized discounts

### 8. The Account Takeover Hunter
- Find customers whose behavior dramatically shifted
- Sudden change in country of purchase
- Sudden change in spending amount (5x normal)
- Same customer, multiple different payment cards in short time
- Device type changes (usually iOS, suddenly Desktop)

### 9. Pattern Clustering
- Group anomalies by time, location, employee
- Do anomalies cluster at certain hours? (e.g., all happen 2-4am)
- Do they cluster in certain stores?
- Do they cluster around specific employees?
- Reveal the "crime hotspots"

### 10. Anomaly Scoring & Validation
- Calculate a suspicion score for every transaction (0-100)
- Score based on how many anomaly rules it triggers
- Rank the top 50 most suspicious transactions
- At the END, compare your detected anomalies vs `hidden_anomaly_type` column
- Report: detection accuracy for each anomaly type

---

## Output Files

### 1. `output/dashboard.html`
Dark-themed fraud investigation dashboard (single self-contained HTML file):
- **Hero / Alert Board**: total transactions, anomalies detected, estimated financial impact, fraud rate %, top 3 crime types
- **Crime Scene Map**: anomaly count by store location and time of day (heatmap)
- **Impossible Geography**: timeline visualization of stolen card cases
- **Employee Watch List**: bar chart of employees ranked by suspicion score with specific flags
- **Bot Traffic Detector**: processing time distribution showing human vs bot clusters
- **Price Glitch Report**: products sold far below category norm
- **Account Takeover List**: customers with dramatic behavior shifts
- **Anomaly Hotspot Heatmap**: hour-of-day × day-of-week showing when crimes happen
- **Top 50 Most Suspicious Transactions**: table with transaction IDs, suspicion score, flags triggered
- **Detection Accuracy**: how well the system caught each type of planted anomaly
- Responsive, dark background (#0f0f0f), "investigation board" aesthetic

### 2. `output/stolen_card_timeline.png`
Visualization of stolen card cases. Timeline showing card #XXXX used in multiple cities within impossible time windows. This is the most "movie-like" chart.

### 3. `output/employee_watchlist.png`
Bar chart ranking employees by suspicion score. Show refund rate, avg discount, transactions per hour. Highlight the top 3 suspects in red.

### 4. `output/bot_vs_human.png`
Histogram of processing times. Human transactions form a bell curve around 3-5 seconds. Bot transactions spike at specific values. Show both clearly overlaid.

### 5. `output/price_glitch_report.png`
Scatter plot: price vs category. Normal products cluster. Glitch products appear as outliers far below the cluster. Annotate affected products.

### 6. `output/anomaly_hotspots.png`
Heatmap: hour of day (Y-axis) × day of week (X-axis). Cell intensity = number of anomalies. Reveals WHEN crimes happen most.

### 7. `output/suspicion_ranking.png`
Horizontal bar chart of top 20 most suspicious transactions with their suspicion scores and primary flags.

### 8. `output/investigation_report.md`
Forensic investigation report:
- Executive summary: "Detected X anomalies worth $Y in financial impact"
- Crime by crime breakdown with evidence
- Stolen card cases — timeline per card
- Employee suspicion list with specific behaviors flagged
- Bot traffic findings — IPs and patterns
- Price glitch evidence
- Account takeover cases
- Hotspot analysis — when and where crimes cluster
- Top 50 transactions to investigate
- Detection accuracy vs planted anomalies (validation)
- 5 immediate actions to implement based on findings

---

## System Architecture

```
Layer 1: Problem     → Every business has hidden losses. Normal analysis misses them.
Layer 2: Data        → 14K transactions with 9 types of anomalies planted inside
Layer 3: Detective   → 9 hunters: Geography, Rapid-Fire, Employee, Bot, Glitch,
                       Corruption, Discount, Takeover, Pattern Clustering
Layer 4: Evidence    → Scoring system — each transaction gets a suspicion score
Layer 5: Verdict     → Top 50 suspicious transactions with specific flags triggered
Layer 6: Agentic     → AI hunts anomalies, human investigates and acts
Layer 7: Outputs     → Investigation dashboard, crime evidence, action report
```

---

## Rules
1. Read this file FIRST
2. Install packages silently (`pip install -q`)
3. Write and run `analyzer.py` — fix errors yourself
4. Use ALL data
5. Create ALL 8 output files
6. DO NOT use the `hidden_anomaly_type` column during detection. Use it ONLY at the end to validate accuracy.
7. End with: total financial impact of anomalies, most dangerous anomaly type, highest-risk employee, 1 action to implement tomorrow

## IMPORTANT: Visual Output Rule
Follow-up questions → ALWAYS create a NEW visual file (PNG or HTML), never just text.
