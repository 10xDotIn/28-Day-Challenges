# Day 7 — Computer Vision Practical
### Product Photo Analyzer: Amazon vs eBay | 10x.in

---

## Quick Recap — Yesterday to Today

Yesterday we understood **what** computer vision is.
Today we **build** with it.

| Yesterday (Theory) | Today (Practical) |
|---|---|
| What is a pixel | Analyze real product photos |
| What is K-Means clustering | Extract dominant product colors |
| What is edge detection | Measure product detail and complexity |
| What is histogram analysis | Check lighting and exposure |
| What is blur detection | Score image sharpness |
| What is GrabCut segmentation | Measure product coverage in frame |

---

## The Problem

Two sellers list the same product — wireless headphones.
One photo sells. The other doesn't.

**Why?**

The difference is not the product.
The difference is the photo.

Today we build a system that scores every product photo
and tells you exactly what makes one better than the other.

---

## Two Layers of Analysis

### Layer 1 — Computer Vision (Python + OpenCV)
The computer measures pixels. Math on images.
Sharpness, colors, edges, backgrounds, exposure, coverage.

### Layer 2 — AI Vision (Claude looks at the photo)
Claude Code actually SEES the photo like a human.
Brand recognition, centering, professionalism, selling points.
Then writes product listing copy from the photo alone.

---

## What the Computer Will See

| Signal | What CV Measures | Why It Matters |
|---|---|---|
| Sharpness | Laplacian variance | Blurry = no trust = no sale |
| Background | Pixel intensity analysis | Clean white bg converts better |
| Dominant colors | K-Means pixel clustering | Does the product pop or blend in? |
| Color temperature | Warm / cool / neutral | Mood and audience perception |
| Product size | GrabCut segmentation | Too small in frame = missed detail |
| Edge detail | Canny edge detection | More edges = more visible features |
| Brightness | Histogram analysis | Over/underexposed = amateur |
| Mood | Brightness + saturation + contrast | Premium vs budget feel |
| Visual complexity | Edge density scoring | Simple and clean vs cluttered |
| Text/Graphics | Region-based detection | Overlays hurt trust |

---

## What AI Vision Will See

| Signal | What Claude Sees | Why It Matters |
|---|---|---|
| Brand recognition | Identifies the brand from the photo | Knows what it's looking at |
| Centering | Is the product properly placed? | Off-center = amateur |
| Professionalism | Pro or amateur — and why? | Trust signal for buyers |
| Selling point | What stands out visually? | The photo should sell itself |
| Listing copy | Writes title + bullets from the photo | Photo becomes the product page |

---

## Thumbnail Simulation

80% of buyers browse on mobile.
They see your photo at **150x150 pixels** — not full size.

The analyzer shrinks every photo to thumbnail size and checks:
- Is the product still recognizable?
- Does the image hold up or turn into a blob?

---

## Fake / Stock Photo Detection

The analyzer runs **Error Level Analysis (ELA)** on every image.
- Real photos have uniform error patterns
- Edited or stock photos show patchy bright regions
- This flags photos that aren't authentic

---

## The 5 Outputs

### 1. Interactive HTML Dashboard
Opens in your browser. Click, filter, sort.
Every image with scores, signals, and color coding.
Not a spreadsheet — a real dashboard.

### 2. Vision Maps
What the computer literally SEES inside each photo:
- Original image
- Edge detection output (white lines on black)
- ELA heatmap (editing/compression patterns)

### 3. Radar Charts
One spider chart per image showing all 6 signals at once.
Instantly see which photos are balanced and which have gaps.

### 4. Platform Scorecard
Amazon vs eBay — head to head.
Bar charts comparing every metric.
One clear winner.

### 5. AI-Generated Listings
Product title + 3 bullet points written by Claude
based ONLY on what it sees in the photo.
No product description needed — the photo IS the input.

---

## Project Structure

```
product-photo-analyzer/
├── CLAUDE.md                ← Claude Code reads this
├── images/
│   ├── Amazon/              ← 11 product photos
│   └── Ebay/                ← 7 product photos
└── output/                  ← results land here
    ├── dashboard.html
    ├── vision_maps.png
    ├── radar_charts.png
    ├── platform_scorecard.png
    └── listings.md
```

---

## How Engagement Scoring Works

```
Sharp focus                    → +2  (clear = trustworthy)
High contrast                  → +2  (stops the scroll)
Clean white background         → +1  (industry standard)
Product fills 40-80% of frame  → +1  (right size in frame)
Good exposure                  → +1  (professional lighting)
No text/graphic overlays       → +1  (clean presentation)
Colors pop against background  → +1  (product stands out)
High resolution                → +1  (zoom-ready)
```

---

## How Mood Detection Works

| Mood | What It Means |
|---|---|
| Premium | High contrast, dark tones, clean |
| Professional | Even lighting, white bg, sharp |
| Budget | Cluttered, uneven light, busy bg |
| Minimal | Simple, lots of white space |
| Energetic | Bright colors, high saturation |
| Cluttered | Too much going on |

---

## The 10 Prompts

---

### Prompt 01 — Kickoff

```
Run it
```

Two words. Claude Code reads CLAUDE.md,
builds the entire pipeline, and runs it.

---

### Prompt 02 — Open the Dashboard

```
Open the dashboard.html in my browser. Walk me
through what you see.
```

---

### Prompt 03 — What Does the Computer See?

```
Show me the vision_maps.png. Explain what the edge
detection and ELA maps are telling us about each photo.
```

---

### Prompt 04 — Radar Charts

```
Show me the radar_charts.png. Which images have the
most balanced signal profile? Which ones have obvious
weak spots?
```

---

### Prompt 05 — Amazon vs eBay Scorecard

```
Show me the platform_scorecard.png. Which platform
wins and in which categories?
```

---

### Prompt 06 — AI Vision: What Do You See?

```
Look at each image in images/Amazon/ and images/Ebay/.
For each photo tell me — what brand is it, is it
centered, does it look professional, and would you
click on this listing?
```

---

### Prompt 07 — Auto Listing Copy

```
Pick the top 5 photos by engagement score. For each one,
write a product title and 3 bullet points based ONLY
on what you see in the photo. No external knowledge.
```

---

### Prompt 08 — Add Shadow Detection

```
Add shadow detection to the analyzer. Do any products
cast harsh shadows? Rerun the analysis and update
the dashboard.
```

---

### Prompt 09 — Seller Photography Guide

```
Based on all the CV data AND your AI vision observations,
write a Product Photography Guide — a checklist any
seller can follow to score 8 or above.
```

---

---

## What You Built Today

| Before | After |
|---|---|
| Static PNG grid | Interactive HTML dashboard |
| Raw CSV data | Radar charts showing all signals |
| Couldn't see what CV sees | Edge detection + ELA visualizations |
| No platform comparison | Head-to-head scorecard with charts |
| Wrote listing copy manually | AI writes copy from the photo alone |
| Pixel math only | AI vision that understands the photo |

---

## What to Try After This

- Analyze your own product photos
- Compare your listings vs a competitor
- Open the dashboard and filter by score
- Generate listing copy from your best photos
- Share the scorecard with your team

---

*Day 7 of 10 | Built with Claude Code | 10x.in*
