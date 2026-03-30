# Day 9 — AI Sentiment Analyzer
### 35,000 Hotel Reviews → Business Insights in One Prompt | 10x.in

---

## The Problem

A hotel chain has 35,000 customer reviews.
Reading them all takes weeks.
Most managers read 20 and guess the rest.

Today the computer reads all 35,000 in seconds
and tells you exactly what guests love,
what they hate, and what to fix first.

---

## What We Are Building

Input: A CSV of 35,000 real hotel reviews from Kaggle
Output: A full customer intelligence system

Not just "positive or negative."
We go deeper — topics, trends, mismatches, word patterns.

---

## What the Analyzer Will Find

| Analysis | What It Reveals |
|---|---|
| Sentiment scoring | Is each review positive, negative, or neutral? |
| Emotion detection | Beyond pos/neg — joy, anger, disappointment, trust, surprise |
| Topic detection | WHAT are guests complaining about? Cleanliness? Noise? WiFi? |
| Word frequency | What words appear in angry reviews vs happy ones? |
| Bigram analysis | 2-word phrases like "front desk" or "hot water" — more specific |
| Hotel ranking | Which hotel has happiest guests? Which has angriest? |
| City ranking | Which city has the best hotel experience? |
| Rating mismatches | 5-star rating but negative words — what's really going on? |
| Sentiment over time | Is satisfaction improving or getting worse year by year? |
| Review length | Do angry guests write longer reviews? |
| Word clouds | Visual map of what guests talk about most |

---

## How Sentiment Scoring Works

Every review gets a polarity score from -1 to +1:

```
"Beautiful hotel, amazing staff!"            → +0.82 (positive)
"Room was okay, nothing special"             → +0.04 (neutral)
"Dirty bathroom, rude staff. Never again."   → -0.71 (negative)
```

The computer reads the words, understands the tone,
and assigns a number. For every single review. In seconds.

---

## How Topic Detection Works

The computer doesn't just say "this review is negative."
It tells you WHY.

```
"Room smelled like mold"              → Topic: Cleanliness
"Staff was incredibly rude"           → Topic: Service
"WiFi didn't work at all"             → Topic: WiFi
"Walls are paper thin, heard everything" → Topic: Noise
"Breakfast was stale and cold"        → Topic: Food
"Way overpriced for what you get"     → Topic: Price
```

Now you know: 35% of complaints are about cleanliness,
22% about service, 18% about noise.
That's where to spend the budget.

---

## The 11 Outputs

### 1. Interactive Dashboard
Opens in browser. Dark theme. Donut charts, bar charts,
quote cards, city comparison, emotion breakdown.
Not a spreadsheet — a real intelligence dashboard.

### 2. Positive Word Cloud
Giant word cloud of what happy guests say most.
Bigger word = more frequent. Green theme.

### 3. Negative Word Cloud
What angry guests say most. Red theme.
Instantly see what frustrates people.

### 4. Topic Chart
Complaints vs Praise — side by side per topic.
Cleanliness? Service? Noise? Food? Ranked.

### 5. Sentiment Timeline
Satisfaction trend over years.
Green fill above zero, red below. Drops marked.

### 6. Hotel Ranking
Top 10 hotels ranked by guest sentiment.
Color gradient green to red. Review counts shown.

### 7. Emotion Chart
Beyond positive/negative — what EMOTIONS do guests feel?
Joy, anger, disappointment, trust, surprise. Counted and ranked.

### 8. Review Length Chart
Do angry guests write longer reviews?
Bar chart + scatter plot showing the pattern.

### 9. City Sentiment Map
Which city has the happiest hotel guests?
Top 10 cities ranked by sentiment.

### 10. Bigram Chart
Most common 2-word phrases in negative reviews.
"front desk", "air conditioning", "hot water" —
more insightful than single words.

### 11. Business Insights Report
Written by AI. Executive summary. Emotions. Quotes.
Hotel ranking. City ranking. Bigrams. Trends.
5 recommendations. The consulting-grade report.

---

## Project Structure

```
sentiment-analyzer/
├── CLAUDE.md              ← Claude Code reads this
├── data/
│   └── hotel_reviews.csv         ← 35,000 hotel reviews
└── output/                ← 11 files land here
    ├── dashboard.html
    ├── word_cloud_positive.png
    ├── word_cloud_negative.png
    ├── topic_chart.png
    ├── sentiment_timeline.png
    ├── hotel_ranking.png
    ├── emotion_chart.png
    ├── review_length_chart.png
    ├── city_sentiment.png
    ├── bigram_chart.png
    └── insights_report.md
```

---

## The Data

35,000 real hotel reviews from Kaggle:
- Hotel name, city, country
- Star rating (1-5)
- Review text + review title
- Date of review
- Reviewer username
- Would recommend (yes/no)

---

## The Prompts

---

### Prompt 01 — Run It

```
Run it
```

Builds the full pipeline. Creates all 11 visual outputs.

---

### Prompt 02 — Dashboard

```
Open the dashboard
```

---

### Prompt 03 — Word Clouds

```
Show me positive vs negative word clouds side by side in one image
```

---

### Prompt 04 — Complaints

```
What do guests complain about most? Show me with example quotes
```

---

### Prompt 05 — Hotels

```
Compare the best and worst hotels with their actual reviews
```

---

### Prompt 06 — Hidden Frustrations

```
Find 5-star reviews that are actually negative. Show me what they said
```

---

### Prompt 07 — Cities

```
Which city has the happiest hotel guests? Rank the top 10
```

---

### Prompt 08 — Executive Memo

```
Write a 1-page executive memo for hotel management. Make it visual
```

35,000 reviews became one page. One problem. One fix.

---

## What You Built Today

| Before | After |
|---|---|
| Read 20 reviews, guess the rest | 35,000 analyzed in seconds |
| "Reviews seem negative" | "35% complain about cleanliness specifically" |
| Gut feeling about hotels | Hotels ranked by sentiment data |
| No trend visibility | Years of satisfaction trends |
| No emotion understanding | Joy, anger, disappointment detected |
| Single words | 2-word phrases reveal real issues |
| No city comparison | Cities ranked by guest happiness |
| Hours of manual reading | Interactive dashboard + 11 visual outputs |
| Generic advice | Specific: "fix cleanliness, then noise, then wifi" |

---

## The Real Insight

> Your guests are already telling you what to fix.
> They're telling you in 35,000 reviews.
> You just weren't reading all of them.
>
> Now you can. In seconds.
> And the computer finds patterns
> you would have missed in weeks of reading.

---

*Day 9 of 28 | Built with Claude Code | 10x.in*
