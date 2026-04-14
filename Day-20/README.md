# Day 20 — The Weather Effect Analyzer
### It Rained Last Tuesday. Your Revenue Dropped 18%. You Blamed Marketing. | 10x.in

---

## What is this?

It rained. Your restaurant was empty. You blamed the new menu. Your food delivery app had record orders. You credited the marketing campaign. Both were wrong. It was the weather.

Weather silently controls what people buy, where they go, what they order, and how much they spend. But nobody tracks it. Nobody connects the dots. Today we do.

This project analyzes 730 days of weather data across 10 different business types and decodes the exact dollar impact of every weather condition — rain, snow, temperature, wind, humidity — on every business.

---

## The Core Idea

Every business blames slow days on marketing, competition, or bad luck. But the biggest invisible factor is weather. Rain adds thousands to food delivery revenue and kills restaurant walk-ins. Snow destroys outdoor events but boosts e-commerce. A 10°F temperature drop changes coffee sales by double digits.

The problem: nobody connects weather data to revenue data. Today we fix that.

---

## The Data

730 days (2 years) × 10 business types = 7,300 data points:

| Column | What It Tells Us |
|---|---|
| date / day_of_week / is_weekend | When it happened |
| weather_condition | Sunny, Cloudy, Light Rain, Heavy Rain, Snow, Windy, Hot & Humid, Thunderstorm, Foggy, Clear & Cold |
| temperature_f / humidity / wind_mph | Exact weather metrics |
| precipitation_inches | How much rain or snow |
| business_type | Food Delivery, Restaurant, Coffee Shop, Ice Cream, Gym, E-Commerce, Retail, Ride-Hailing, Movie Theater, Outdoor Events |
| revenue / customer_count | How much they made and how many showed up |
| online_order_pct | Did people shift to online ordering? |
| cancellation_rate | Did people cancel plans? |

---

## The 8 Outputs

1. **Weather Intelligence Dashboard** — the complete weather × business view
2. **Weather Revenue Map** — which weather makes money, which kills it
3. **Winners & Losers Matrix** — who benefits from bad weather, who suffers
4. **Temperature Curve** — revenue sweet spot for each business
5. **The Rain Tax** — exact dollar cost/gain of rain per business
6. **Snow Impact** — how snow changes everything
7. **Best & Worst Combos** — weather + day combinations that make or break revenue
8. **Weather Strategy Report** — what to prepare for, capitalize on, and hedge against

---

## Project Structure

```
weather-effect-analyzer/
├── CLAUDE.md                 ← Claude Code reads this
├── data/
│   └── weather_business.csv  ← 730 days × 10 businesses
└── output/                   ← 8 files land here
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

### Prompt 03 — Who Wins in Rain?
```
Show me exactly which businesses make MORE money when it rains and which ones lose. How much per rainy day?
```

### Prompt 04 — The Temperature Sweet Spot
```
At what temperature does each business peak in revenue? Show me the curve for all 10 businesses.
```

### Prompt 05 — The Rain Tax
```
How much total revenue does rain cost or add to each business per year? Show the annual rain tax.
```

### Prompt 06 — Snow vs Rain
```
Is snow worse than heavy rain for business? Compare the impact side by side for all 10 businesses.
```

### Prompt 07 — The Killer Combos
```
What's the best weather + day combo for maximum revenue and the worst combo? Show the top 5 and bottom 5.
```

### Prompt 08 — Seasonal Playbook
```
Does rain in summer affect business differently than rain in winter? Build a seasonal weather playbook.
```

### Prompt 09 — The Weather Strategy
```
Write a weather strategy brief — for each business type, what to prepare for, what to capitalize on, and how to hedge against bad weather. Include the dollar impact.
```

---

## What You'll Discover

| What You Think | What's Actually True |
|---|---|
| Bad weather = bad for business | Bad weather is GREAT for some businesses |
| Rain hurts everyone | Rain adds 35%+ to food delivery and ride-hailing |
| Snow kills everything | Snow boosts e-commerce by 25% |
| Temperature doesn't matter | Each business has an exact revenue sweet spot temperature |
| Slow days are random | Most "slow days" are predictable from the weather forecast |

---

## The Shift

> Stop blaming marketing for slow days. Check the weather.
>
> Rain isn't bad for business. It's bad for SOME businesses.
> For others, it's the best sales day of the month.
>
> The weather forecast isn't just about umbrellas.
> It's a revenue forecast. Now you can read it.

---

*Day 20 of 28 | Built with Claude Code | 10x.in*
