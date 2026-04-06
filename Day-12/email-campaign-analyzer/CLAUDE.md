# Email Campaign Targeting Analyzer

> You are a marketing analytics expert. Analyze the email campaign data in
> `data/email_campaigns.csv` and find who should get emails, who shouldn't,
> and where the company is wasting money on the wrong audience.

## Setup
- CSV is in `data/email_campaigns.csv`
- ~8,000 rows, each row is one user in one campaign
- Columns: date, user_id, segment, campaign, email_sent (1/0), opened (1/0), clicked (1/0), purchased (1/0), revenue, past_purchases, avg_order_value, days_since_last_purchase
- Segments: New User, Regular, Frequent Buyer, Inactive, VIP
- Campaigns: Summer Sale, Flash Deal, Welcome Series, Win-Back, Loyalty Reward, New Arrival, Weekend Special
- Install packages: pandas matplotlib numpy seaborn pillow
- Save all outputs in `output/`
- Use ALL rows

## What to Analyze

### 1. Email Funnel
- Email Sent → Opened → Clicked → Purchased
- Calculate: Open Rate, Click Rate (clicks/opens), Conversion Rate (purchases/clicks)
- Drop-off at each stage — where is the biggest leak?
- Funnel by segment — which segment has the best/worst funnel?
- Funnel by campaign — which campaign performs best?

### 2. Campaign Effectiveness — Does Email Even Work?
- Compare purchase rate: users who got email vs users who didn't
- Do this PER SEGMENT — this is critical
- For Frequent Buyers: do they buy at similar rates with or without email? (over-targeting)
- For Inactive users: does email dramatically increase purchase rate? (under-targeting gold)
- Calculate the email "lift" per segment — how much does email ACTUALLY increase purchases?

### 3. Over-Targeting Problem
- Find segments where email has LITTLE or NO impact on purchase rate
- These users would buy anyway — emailing them is wasting money
- Calculate wasted email cost (assume $0.05 per email sent)
- Show: "You're paying to convince people who already decided to buy"

### 4. Under-Targeted Hidden Opportunity
- Find segments/users where email has HUGE impact on purchase rate
- Low natural buyers who convert strongly when emailed
- These are the gold — highest ROI targets
- Calculate potential revenue if these users were emailed more

### 5. Engagement Drop Analysis
- Sent → Open drop: subject line problem
- Open → Click drop: content/design problem
- Click → Purchase drop: landing page / offer problem
- Which stage has biggest drop per campaign?
- Which campaign has the best/worst at each stage?

### 6. Segment Deep Dive
- For each segment: email impact, funnel performance, revenue contribution, recommended action
- Who to email MORE, who to email LESS, who to STOP emailing

### 7. Campaign Comparison
- Rank all campaigns by: open rate, click rate, conversion rate, revenue, ROI
- Which campaign is the winner? Which is wasting money?

### 8. Targeting Recommendations
- Build a targeting matrix: segment x action (email more / keep same / reduce / stop)
- Calculate estimated savings from reducing over-targeting
- Calculate estimated revenue gain from increasing under-targeting
- Net ROI improvement

## Output Files

### 1. `output/dashboard.html`
Dark theme marketing analytics dashboard:
- Hero: total emails sent, open rate, CTR, conversion rate, total revenue, wasted email cost
- Email funnel visualization (bars with drop-off percentages)
- The "does email work?" comparison chart — emailed vs not emailed purchase rates by segment
- Over-targeting alert cards — segments where email doesn't help (red)
- Under-targeting opportunity cards — segments where email helps most (green)
- Campaign ranking table
- Targeting matrix — who to email more/less/stop
- ROI improvement estimate
- Key insights as styled cards
- ONE self-contained HTML file

### 2. `output/email_funnel.png`
Funnel chart: Sent → Opened → Clicked → Purchased with drop-off % between each stage.
Also show funnel broken down by segment side by side.

### 3. `output/email_vs_no_email.png`
Grouped bar chart — for each segment: purchase rate WITH email vs WITHOUT email.
The GAP between bars = email impact. Some segments have big gaps (email works). Some have tiny gaps (email is useless).
This is the most important chart.

### 4. `output/over_vs_under.png`
Two-panel visualization:
- Left: Over-targeted segments (red) — email has no impact, money wasted
- Right: Under-targeted segments (green) — email has huge impact, opportunity missed
Show dollar amounts for wasted cost and missed revenue.

### 5. `output/campaign_ranking.png`
Bar chart ranking all campaigns by conversion rate or revenue. Best to worst.

### 6. `output/funnel_drops.png`
Heatmap or grouped bars showing where each campaign drops most.
Rows = campaigns, columns = stages (open, click, purchase). Color = drop-off severity.

### 7. `output/targeting_matrix.png`
Visual matrix: segments on y-axis, recommended action on x-axis (email more / keep / reduce / stop).
Color coded. With estimated impact numbers.

### 8. `output/campaign_report.md`
Business report:
- Executive summary
- Funnel analysis with numbers
- Does email work? Evidence per segment
- Over-targeting findings with wasted cost
- Under-targeting findings with missed revenue
- Campaign ranking
- Funnel drop diagnosis (subject vs content vs landing page)
- Targeting matrix with recommendations
- 5 specific actions to improve email ROI
- Final verdict: how much ROI improvement is possible?

## Rules
1. Read this file first
2. Install packages silently
3. Write and run analyzer.py — fix errors yourself
4. Use ALL data
5. Create ALL 8 output files
6. End with: biggest waste, biggest opportunity, estimated ROI improvement

## IMPORTANT: Visual Output Rule
Follow-up questions → ALWAYS create a NEW visual file (PNG or HTML), never just terminal text.
