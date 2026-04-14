# Day 19 — Neighborhood Price Decoder
### Your Neighbor's Apartment Sold for $80K More. Here's Why. | 10x.in

---

## What is this?

Two identical apartments. Same building. Same floor. Same size. One sold for $450,000. The other for $370,000. Why?

Because property prices aren't about the property. They're about everything AROUND it. Metro distance. School rating. Crime rate. Noise level. Park access. Even the floor number.

This project analyzes 12,000 real estate listings across 12 neighborhoods and decodes the exact dollar value of every invisible factor — so you know exactly what you're paying for (or overpaying for).

---

## The Core Idea

Every property price is a combination of hidden multipliers. Some you see — bedrooms, sqft. Most you don't — metro proximity, school quality, safety, noise.

This analysis puts a dollar amount on each one. "Every 0.1 mile further from metro = $X less. Every school rating point = $Y more. Having a pool adds $Z."

Once you see the formula, you can spot overpriced traps and hidden deals that most buyers miss.

---

## The Data

12,000 property listings across 12 neighborhoods:

| Column | What It Tells Us |
|---|---|
| neighborhood | Which of the 12 areas |
| property_type | Apartment, Condo, Townhouse, Studio, Penthouse |
| sqft / bedrooms / bathrooms | The property itself |
| floor / year_built / condition | Physical characteristics |
| has_parking / gym / pool / doorman | Amenities |
| metro_distance_miles | How far from the nearest station |
| school_rating | Nearby school quality (1-10) |
| crime_index | Area safety (lower = safer) |
| restaurants_nearby / park_access / noise_level | Lifestyle factors |
| listing_price / price_per_sqft | What they're asking |
| estimated_fair_value | What it SHOULD cost |
| price_gap_percent | Overpriced (+) or underpriced (-) |
| days_on_market / sold | Did it sell? How long did it take? |
| predicted_1yr_appreciation | Growth forecast |

---

## The 8 Outputs

1. **Real Estate Intelligence Dashboard** — the complete price decoder view
2. **Neighborhood Price Map** — all 12 areas ranked by value
3. **Price Drivers** — every factor ranked by dollar impact (THE key chart)
4. **Overpriced vs Underpriced** — scatter plot revealing deals and traps
5. **Metro Premium Curve** — exact cost of distance from station
6. **School Rating Tax** — what you're paying for school quality
7. **Smart Buyer Deal Finder** — top 20 hidden deals in the dataset
8. **Investment Report** — where to buy, what to avoid, growth predictions

---

## Project Structure

```
neighborhood-price-decoder/
├── CLAUDE.md              ← Claude Code reads this
├── data/
│   └── listings.csv       ← 12,000 listings
└── output/                ← 8 files land here
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

### Prompt 03 — What Am I Paying For?
```
Show me the exact dollar value of every factor — metro distance, school rating, crime, parking, pool, floor level. Rank them by impact.
```

### Prompt 04 — Find the Deals
```
Show me the most underpriced listings — properties where the asking price is significantly below fair value. Why are they cheap?
```

### Prompt 05 — The Metro Tax
```
How much does every 0.1 mile from the metro station cost? At what distance does the premium disappear? Show the curve.
```

### Prompt 06 — School vs Price
```
How much extra are people paying for school ratings? Is a rating of 9 vs 7 worth the premium? Show the math.
```

### Prompt 07 — Overpriced Traps
```
Show me the most overpriced listings that are sitting on the market. How long have they been listed and why aren't they selling?
```

### Prompt 08 — Where to Invest
```
If I had to buy one property as an investment — best appreciation potential, best value, best fundamentals — which neighborhood and what type? Show the data.
```

### Prompt 09 — The Full Report
```
Write a real estate intelligence brief — best neighborhoods, worst neighborhoods, what drives price, top deals, investment recommendations. Make it visual.
```

---

## What You'll Discover

| What You Think | What's Actually True |
|---|---|
| Price = size + bedrooms | Size is only 30% of the story |
| Location is vague | "0.3 miles from metro" has exact dollar value |
| School districts matter | Each rating point = specific $ premium |
| All apartments in same area cost similar | Same building, 20% price difference based on floor + amenities |
| You need a broker to spot deals | Data finds deals brokers don't show you |

---

## The Shift

> Property prices aren't random. Every dollar is explained by something.
>
> Metro distance. School rating. Crime rate. Floor level. Noise.
> Each one has an exact price tag.
>
> Once you see the formula, you can never look at a listing the same way.

---

*Day 19 of 28 | Built with Claude Code | 10x.in*
