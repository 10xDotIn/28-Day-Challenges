# Day 22 — The Refund Prediction Engine
### 500 Orders Just Came In. 80 Will Come Back. Which 80? | 10x.in

---

## What is this?

You just shipped 500 orders. Feels great. But 80 of them are coming back. Returns. Refunds. Lost shipping. Processing costs. Wasted packaging.

What if you could predict WHICH 80 — before you ship a single box?

This project analyzes 15,000 orders and finds the signals that predict returns at the moment of purchase — time of day, browse behavior, discount used, payment method, device, customer history. Then builds a prediction model that scores every order by return risk.

---

## The Core Idea

Returns are not random. They follow patterns.

Late-night purchases return more — impulse buying. Heavy discounts attract the wrong buyers. "Buy Now Pay Later" customers return more — less commitment. Customers who browse for under 3 minutes return at double the rate of those who research for 30 minutes.

These signals are ALL visible at the moment of purchase. Before you ship. Before you lose money.

**The shift**: stop treating returns as a cost of business. Start predicting and preventing them.

---

## The Data

15,000 orders across 6 categories:

| Column | What It Tells Us |
|---|---|
| purchase_hour / is_late_night | When they bought (impulse signal) |
| time_browsing_minutes / reviews_read / items_compared | How much they researched (confidence signal) |
| used_coupon / discount_percent | Were they buying the product or buying the deal? |
| payment_method | Buy Now Pay Later = less commitment |
| device / channel | Mobile impulse vs desktop research |
| customer_type / previous_return_rate | Are they a serial returner? |
| is_gift / multiple_sizes_ordered | Known high-return scenarios |
| cart_removals | Indecision signal |
| returned | Did it come back? (1 = yes) |
| return_reason | Why they say they returned it |

---

## The 8 Outputs

1. **Return Intelligence Dashboard** — the complete prediction view
2. **The Time Bomb** — return rate by hour of purchase
3. **The Impulse Map** — browse time, reviews, comparisons vs returns
4. **The Discount Curse** — how discounts drive returns
5. **Category Returns** — why fashion is a nightmare
6. **Feature Importance** — which signals predict returns best (ML model)
7. **Risk Tiers** — High / Medium / Low risk order distribution
8. **Return Strategy Report** — what to flag, fix, limit, and monitor

---

## Project Structure

```
refund-predictor/
├── CLAUDE.md            ← Claude Code reads this
├── data/
│   └── orders.csv       ← 15,000 orders
└── output/              ← 8 files land here
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

### Prompt 03 — The Danger Hours
```
Show me which hours of the day have the highest return rates. What's the difference between a 2am purchase and a 2pm purchase?
```

### Prompt 04 — The Impulse Problem
```
How does browsing behavior predict returns? Compare customers who researched for 30 minutes vs those who bought in under 3 minutes.
```

### Prompt 05 — The Discount Trap
```
At what discount level do returns start spiking? Show me the break-even point where discounts stop being profitable after returns.
```

### Prompt 06 — The Fashion Nightmare
```
Why does fashion have the highest return rate? Break down the reasons and find which fashion behaviors predict returns.
```

### Prompt 07 — Predict My Order
```
Build a prediction model — score every order by return risk. Which features matter most? Show me the top 20 highest-risk orders.
```

### Prompt 08 — The Money Math
```
If we flagged every high-risk order and added a confirmation step — how many returns would we prevent? How much money would we save annually?
```

### Prompt 09 — The Return Strategy
```
Write a return reduction strategy — what to flag before shipping, which discounts to limit, which customer behaviors to watch. Include the dollar impact.
```

---

## What You'll Discover

| What You Think | What's Actually True |
|---|---|
| Returns are random | Returns follow clear, predictable patterns |
| All orders are equal | Late-night orders return at nearly double the rate |
| Discounts bring good customers | Heavy discounts bring returners |
| Buy Now Pay Later is convenient | BNPL customers return 36% more |
| You can't predict returns | A model can flag high-risk orders before shipping |

---

## The Shift

> Returns are not a cost of doing business.
> They're a prediction problem.
>
> The signals are there at the moment of purchase.
> Time. Device. Discount. Browse behavior. History.
>
> You just need to read them before you ship.

---

*Day 22 of 28 | Built with Claude Code | 10x.in*
