---
name: compete
description: "Genre and category competitive analysis — identify oversaturated genres, opportunity gaps, and content positioning"
argument-hint: "<dataset-folder-name>"
risk: "safe"
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
model: claude-sonnet-4-6
context: fork
agent: general-purpose
---

# Compete — Content Competition Analysis

You are executing the `:compete` skill for the **10x-content-intel** plugin.

## What This Skill Does

Performs competitive analysis across genres and categories — identifies which content areas are oversaturated, which have opportunity gaps, and how to position content strategically.

## Instructions

### Step 1: Load Cleaned Data
- Check if `output/{argument}/{argument}_cleaned.csv` exists
- If NOT, first run the Content Profiler to clean the data
- Load the cleaned CSV

### Step 2: Read Agent Instructions
- Read `agents/content-strategist.md` for strategic analysis approach

### Step 3: Genre Competition Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

dataset = "{argument}"
df = pd.read_csv(f"output/{dataset}/{dataset}_cleaned.csv")
out_dir = Path(f"output/{dataset}/compete")
out_dir.mkdir(parents=True, exist_ok=True)

# Handle multi-genre (listed_in) column
genre_col = None
for col in ['listed_in', 'genre', 'genres', 'category']:
    if col in df.columns:
        genre_col = col
        break

if genre_col:
    df_genres = df.dropna(subset=[genre_col]).copy()
    df_genres[genre_col] = df_genres[genre_col].str.split(',')
    df_genres = df_genres.explode(genre_col)
    df_genres[genre_col] = df_genres[genre_col].str.strip()
```

### Step 4: Generate Analysis & Charts (minimum 5):

1. **Genre Volume Ranking** — Top 20 genres by total content count (horizontal bar)
2. **Genre Growth Rate** — Compare recent 3 years vs all-time for each genre (% change)
3. **Genre × Content Type Matrix** — Heatmap showing genre distribution across Movies vs Shows
4. **Opportunity Matrix** — Scatter plot: X = current volume, Y = growth rate (identify quadrants)
   - High volume + High growth = Stars
   - High volume + Low growth = Cash Cows
   - Low volume + High growth = Rising Stars (OPPORTUNITY)
   - Low volume + Low growth = Niche
5. **Rating Distribution by Top Genres** — Box plot or grouped bar

### Step 5: Strategic Insights
For each chart, provide:
- What the data shows
- What it means strategically
- Actionable recommendation

### Step 6: Save Outputs
- Save charts to `output/{argument}/compete/chart_*.png`
- Write `output/{argument}/compete/competitive_analysis.md`

## Output
- `output/{argument}/compete/competitive_analysis.md`
- `output/{argument}/compete/chart_01_genre_ranking.png`
- `output/{argument}/compete/chart_02_genre_growth.png`
- `output/{argument}/compete/chart_03_genre_type_matrix.png`
- `output/{argument}/compete/chart_04_opportunity_matrix.png`
- `output/{argument}/compete/chart_05_rating_by_genre.png`
