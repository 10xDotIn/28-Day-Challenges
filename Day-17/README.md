# Day 17 — Customer Lifetime Value Predictor
### Your $20 Customer Might Be Worth $5,000 | 10x.in

---

## What is this?

Two customers walk into your store. Customer A spends $500 on day one. Customer B spends $20. Every business would celebrate Customer A and ignore Customer B.

But what if Customer B comes back every month for 3 years and spends $5,000 total? And Customer A never returns?

This project analyzes 8,000 customers and predicts their 3-year lifetime value from their first purchase behavior — revealing who will become a VIP, who is a one-time buyer, and which acquisition channels bring customers that actually stay.

---

## The Core Idea

Not all customers are equal. And the signals are there from day one.

What they bought first. How much they paid. Whether they used a discount. Which channel brought them. How many pages they viewed in the first 30 days. How fast they placed a second order.

These early signals predict whether someone will spend $5,000 over 3 years or $20 and vanish.

**The shift**: stop treating all customers the same. Start predicting who's worth fighting for.

---

## The Data

8,000 customers with full behavioral profiles:

| Column | What It Tells Us |
|---|---|
| customer_archetype | Future VIP / Loyal Regular / Promising New / Discount Addict / One-and-Done / Fading Away |
| acquisition_channel | How they found you (organic, paid_ads, social, email, referral) |
| first_order_value | How much they spent on day one |
| first_order_discount_pct | Did they need a discount to buy? |
| total_orders / lifetime_revenue | Their full history |
| pages_viewed / sessions / email_opens (first 30 days) | Early engagement signals |
| days_to_second_order | How fast they came back |
| churned | Did they leave? |
| predicted_3yr_clv | What they're worth over 3 years |

---

## The 8 Outputs

1. **Customer Intelligence Dashboard** — the complete CLV view
2. **Customer Pyramid** — who pays the bills (8% of customers = 50%+ of value)
3. **First Purchase DNA** — what a VIP's first order looks like vs a one-timer
4. **30-Day Crystal Ball** — which early signals predict lifetime value
5. **Channel Quality** — which channels bring valuable vs worthless customers
6. **Discount Curse** — how discounts destroy long-term customer value
7. **CLV Tiers** — Platinum / Gold / Silver / Bronze distribution
8. **Strategy Report** — who to invest in, nurture, convert, let go, or save

---

## Project Structure

```
clv-predictor/
├── CLAUDE.md           ← Claude Code reads this
├── data/
│   └── customers.csv   ← 8,000 customers
└── output/             ← 8 files land here
```

---

## The Prompts

### Prompt 01 — Run It
```
Run it
```

### Prompt 02 — Dashboard
```
Open the dashboard
```

### Prompt 03 — Who Pays the Bills?
```
Show me how much of the total value comes from the top 10% of customers. Break down each archetype's contribution.
```

### Prompt 04 — First Purchase DNA
```
What does a future VIP's first order look like compared to a one-time buyer? Show me the signals from day one.
```

### Prompt 05 — The Crystal Ball
```
Which behaviors in the first 30 days best predict 3-year lifetime value? Rank the signals by predictive power.
```

### Prompt 06 — Channel Quality
```
Which acquisition channels bring the most valuable long-term customers? Show me CLV by channel — not volume, but quality.
```

### Prompt 07 — The Discount Problem
```
How do first-order discounts affect lifetime value? At what discount level do you start destroying long-term customer value?
```

### Prompt 08 — Save the Fading
```
How many Fading Away customers can we identify early? What signals show they're leaving? How much revenue is at risk?
```

### Prompt 09 — The CLV Playbook
```
Write a customer strategy brief — who to invest in, who to let go, which channels to scale, and how to increase total 3-year CLV. Include the numbers.
```

---

## What You'll Discover

| What You Think | What's Actually True |
|---|---|
| All customers are roughly equal | 8% of customers hold 50%+ of future value |
| Big first order = great customer | First order size barely predicts loyalty |
| Discounts attract good customers | Heavy discounts attract the worst long-term customers |
| Paid ads bring the most value | Paid ads bring volume, referrals bring value |
| You can't predict who'll stay | First 30 days of behavior predict almost everything |

---

## The Shift

> Stop asking "how many customers do we have?"
> Start asking "how many customers are WORTH having?"
>
> A $20 customer who comes back every month
> is worth more than a $500 customer who never returns.
>
> The first purchase is not a transaction. It's a prediction.

---

*Day 17 of 28 | Built with Claude Code | 10x.in*
