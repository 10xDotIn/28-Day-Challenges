# Day 12 — Email Campaign Targeting Analyzer
### Stop Sending Emails to Everyone | 10x.in

---

## The Problem

Companies send millions of emails.
Most get ignored. Some annoy customers.
A few actually work.

The question is not "should we send emails?"
The question is "WHO should get them?"

Today we answer that with data.

---

## The Email Funnel

```
Sent  →  Opened  →  Clicked  →  Purchased
```

At every step, people drop off.
The data tells us WHERE and WHY.

---

## The 4 Big Insights

### 1. Does Email Even Work?
Compare: people who got email vs people who didn't.
If both groups buy at the same rate — email is useless for that group.

### 2. Over-Targeting
Frequent buyers buy whether you email them or not.
Emailing them = paying to convince people who already decided.

### 3. Under-Targeting (Hidden Gold)
Inactive users almost never buy on their own.
But when emailed — their purchase rate jumps.
These are your highest ROI targets.

### 4. Funnel Drop Diagnosis
- Low open rate? Subject line problem.
- Opens but no clicks? Content problem.
- Clicks but no purchase? Landing page problem.

---

## The Data

8,000 users across 7 email campaigns:

| Column | What It Tells Us |
|---|---|
| user_id | Unique customer |
| segment | New User / Regular / Frequent Buyer / Inactive / VIP |
| campaign | Summer Sale / Flash Deal / Welcome Series / Win-Back / Loyalty Reward / New Arrival / Weekend Special |
| email_sent | Did they get the email? (1 = yes, 0 = no) |
| opened | Did they open it? |
| clicked | Did they click a link? |
| purchased | Did they buy something? |
| revenue | How much they spent |
| past_purchases | How many times they bought before |
| avg_order_value | Their typical order size |
| days_since_last_purchase | How long since they last bought |

The key column: **email_sent** — some users got the email, some didn't.
That's what lets us compare: does email actually cause more purchases?

---

## The 8 Outputs

### 1. Marketing Dashboard
### 2. Email Funnel Chart
### 3. Email vs No Email Comparison
### 4. Over-Targeting vs Under-Targeting
### 5. Campaign Ranking
### 6. Funnel Drop Heatmap
### 7. Targeting Matrix
### 8. Business Report

---

## Project Structure

```
email-campaign-analyzer/
├── CLAUDE.md                ← Claude Code reads this
├── data/
│   └── email_campaigns.csv  ← 8,000 users
└── output/                  ← 8 files land here
```

---

## The Prompts

---

### Prompt 01 — Run It

```
Run it
```

---

### Prompt 02 — Dashboard

```
Open the dashboard
```

---

### Prompt 03 — Targeting Strategy

```
Build a targeting strategy — who should get emails and who should we stop emailing? Show the money impact
```

---

### Prompt 04 — Over-Targeting

```
Show me which users are getting emails they don't need. How much money is wasted?
```

---

### Prompt 05 — Hidden Gold Audience

```
Find the users who respond best to email but aren't being targeted enough
```

---

### Prompt 06 — Campaign Battle

```
Rank all 7 campaigns from best to worst. Which one should we kill and which one should we scale?
```

---

### Prompt 07 — Fix the Funnel

```
Where is the biggest drop in the email funnel? Is it a subject line problem, content problem, or landing page problem?
```

---

### Prompt 08 — The Money Slide

```
If we follow your targeting recommendations, how much do we save per month and how much more revenue do we make? Show the ROI math
```

---

### Prompt 09 — Write the Brief

```
Write a marketing brief I can hand to my email team. Who to target, which campaigns to run, what to fix. Make it visual
```

---

## What You Built Today

| Before | After |
|---|---|
| Email everyone | Email the right people |
| No idea what works | Every campaign ranked |
| Wasting money on frequent buyers | Over-targeting identified |
| Missing inactive users | Hidden opportunity found |
| Gut feeling targeting | Data-driven targeting matrix |

---

## The Real Insight

> Don't send more emails.
> Send better emails.
> To better people.
>
> The best marketing is not louder.
> It's smarter.

---

*Day 12 of 28 | Built with Claude Code | 10x.in*
