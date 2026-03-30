---
name: trends
description: "Analyze temporal patterns, content growth, genre shifts, and seasonal trends in the content library"
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

# Trends — Content Trend Analysis

You are executing the `:trends` skill for the **10x-content-intel** plugin.

## What This Skill Does

Analyzes how the content library has evolved over time — growth patterns, genre shifts, format changes, and seasonal patterns.

## Instructions

### Step 1: Load Cleaned Data
- Check if `output/{argument}/{argument}_cleaned.csv` exists
- If NOT, first run the Content Profiler (read `agents/content-profiler.md`) to clean the data
- Load the cleaned CSV into a pandas DataFrame

### Step 2: Read Agent Instructions
- Read `agents/trend-analyst.md` for detailed analysis instructions

### Step 3: Run Trend Analysis
Create a Python script that generates the following analyses and charts:

```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# Setup
sns.set_style("whitegrid")
PALETTE = sns.color_palette("muted")
plt.rcParams.update({
    'figure.dpi': 120,
    'axes.titlesize': 14, 'axes.titleweight': 'bold',
    'axes.labelsize': 12, 'figure.facecolor': 'white',
    'axes.facecolor': 'white', 'axes.edgecolor': '#cccccc',
    'grid.color': '#eeeeee'
})

dataset = "{argument}"
df = pd.read_csv(f"output/{dataset}/{dataset}_cleaned.csv")
out_dir = Path(f"output/{dataset}/trends")
out_dir.mkdir(parents=True, exist_ok=True)
```

### Charts to Generate (minimum 6):

1. **Yearly Content Additions** — Stacked bar (Movies vs TV Shows per year)
2. **Cumulative Content Growth** — Line chart showing library size over time
3. **Monthly Release Seasonality** — Which months get the most content?
4. **Top 10 Genres Over Time** — How genre popularity has shifted
5. **Average Movie Duration by Year** — Is content getting shorter?
6. **Rating Distribution Over Time** — Content maturity shift

### Step 4: Generate Insights
After each chart, write a 2-3 sentence insight explaining what the data reveals.

### Step 5: Save Outputs
- Save all charts to `output/{argument}/trends/chart_*.png`
- Write `output/{argument}/trends/trend_analysis.md` with all insights and embedded chart references

## Output
- `output/{argument}/trends/trend_analysis.md`
- `output/{argument}/trends/chart_01_yearly_additions.png`
- `output/{argument}/trends/chart_02_cumulative_growth.png`
- `output/{argument}/trends/chart_03_monthly_seasonality.png`
- `output/{argument}/trends/chart_04_genre_trends.png`
- `output/{argument}/trends/chart_05_duration_trends.png`
- `output/{argument}/trends/chart_06_rating_shift.png`
