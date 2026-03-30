---
name: geo
description: "Analyze geographic content distribution — which countries and regions produce the most content"
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

# Geo — Geographic Content Analysis

You are executing the `:geo` skill for the **10x-content-intel** plugin.

## What This Skill Does

Analyzes the geographic distribution of content — which countries produce the most, regional patterns, and co-production networks.

## Instructions

### Step 1: Load Cleaned Data
- Check if `output/{argument}/{argument}_cleaned.csv` exists
- If NOT, first run the Content Profiler (read `agents/content-profiler.md`) to clean the data
- Load the cleaned CSV into a pandas DataFrame

### Step 2: Read Agent Instructions
- Read `agents/geo-analyst.md` for detailed analysis instructions

### Step 3: Handle Multi-Country Data
The `country` column often contains multiple countries separated by commas. Split and explode:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

dataset = "{argument}"
df = pd.read_csv(f"output/{dataset}/{dataset}_cleaned.csv")
out_dir = Path(f"output/{dataset}/geo")
out_dir.mkdir(parents=True, exist_ok=True)

# Split multi-country entries
if 'country' in df.columns:
    df_countries = df.dropna(subset=['country']).copy()
    df_countries['country'] = df_countries['country'].str.split(',')
    df_exploded = df_countries.explode('country')
    df_exploded['country'] = df_exploded['country'].str.strip()
```

### Step 4: Generate Charts (minimum 5):

1. **Top 15 Content-Producing Countries** — Horizontal bar chart with value labels
2. **Regional Content Share** — Donut chart (group countries into continents/regions)
3. **Content Type by Top 10 Countries** — Grouped bar (Movies vs TV Shows)
4. **Top 5 Countries Growth Over Time** — Multi-line chart
5. **Genre Preferences by Top Regions** — Heatmap showing genre × region

### Step 5: Region Mapping
Map countries to regions:
```python
region_map = {
    'United States': 'North America', 'Canada': 'North America', 'Mexico': 'Latin America',
    'United Kingdom': 'Europe', 'France': 'Europe', 'Germany': 'Europe', 'Spain': 'Europe',
    'India': 'Asia', 'Japan': 'Asia', 'South Korea': 'Asia', 'China': 'Asia',
    'Nigeria': 'Africa', 'South Africa': 'Africa', 'Egypt': 'Africa',
    'Australia': 'Oceania', 'Brazil': 'Latin America', 'Argentina': 'Latin America',
    # ... extend as needed, default to 'Other'
}
```

### Step 6: Save Outputs
- Save all charts to `output/{argument}/geo/chart_*.png`
- Write `output/{argument}/geo/geo_analysis.md` with insights

## Output
- `output/{argument}/geo/geo_analysis.md`
- `output/{argument}/geo/chart_01_top_countries.png`
- `output/{argument}/geo/chart_02_regional_share.png`
- `output/{argument}/geo/chart_03_type_by_country.png`
- `output/{argument}/geo/chart_04_country_growth.png`
- `output/{argument}/geo/chart_05_genre_by_region.png`
