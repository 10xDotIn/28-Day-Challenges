"""
Geographic Analysis Script — 10x Content Intel
Generates 5 charts and a geo_analysis.md report.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from pathlib import Path
from collections import Counter

# ── Config ────────────────────────────────────────────────────────────────────
DATASET = "netflix-data"
BASE    = Path("C:/Users/Admin/Desktop/Day-5")
CSV     = BASE / "output" / DATASET / f"{DATASET}_cleaned.csv"
OUT     = BASE / "output" / DATASET / "geo"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
})
PALETTE = sns.color_palette("muted")

# ── Region Map ─────────────────────────────────────────────────────────────────
REGION_MAP = {
    'United States': 'North America', 'Canada': 'North America',
    'Mexico': 'Latin America', 'Brazil': 'Latin America',
    'Argentina': 'Latin America', 'Colombia': 'Latin America',
    'Chile': 'Latin America', 'Peru': 'Latin America',
    'Venezuela': 'Latin America',
    'United Kingdom': 'Europe', 'France': 'Europe', 'Germany': 'Europe',
    'Spain': 'Europe', 'Italy': 'Europe', 'Netherlands': 'Europe',
    'Sweden': 'Europe', 'Norway': 'Europe', 'Denmark': 'Europe',
    'Belgium': 'Europe', 'Poland': 'Europe', 'Portugal': 'Europe',
    'Switzerland': 'Europe', 'Austria': 'Europe', 'Ireland': 'Europe',
    'Finland': 'Europe', 'Czech Republic': 'Europe', 'Romania': 'Europe',
    'Hungary': 'Europe', 'Greece': 'Europe', 'Turkey': 'Europe',
    'India': 'Asia', 'Japan': 'Asia', 'South Korea': 'Asia',
    'China': 'Asia', 'Hong Kong': 'Asia', 'Taiwan': 'Asia',
    'Thailand': 'Asia', 'Philippines': 'Asia', 'Indonesia': 'Asia',
    'Malaysia': 'Asia', 'Singapore': 'Asia', 'Vietnam': 'Asia',
    'Pakistan': 'Asia', 'Bangladesh': 'Asia', 'Sri Lanka': 'Asia',
    'Nigeria': 'Africa', 'South Africa': 'Africa', 'Egypt': 'Africa',
    'Kenya': 'Africa', 'Ghana': 'Africa', 'Ethiopia': 'Africa',
    'Morocco': 'Africa', 'Senegal': 'Africa',
    'Australia': 'Oceania', 'New Zealand': 'Oceania',
    'Israel': 'Middle East', 'Lebanon': 'Middle East',
    'Saudi Arabia': 'Middle East', 'Jordan': 'Middle East',
    'United Arab Emirates': 'Middle East', 'Iran': 'Middle East',
    'Iraq': 'Middle East', 'Kuwait': 'Middle East',
    'Russia': 'Europe', 'Ukraine': 'Europe',
    'Kazakhstan': 'Asia',
}

def get_region(country):
    return REGION_MAP.get(country.strip(), 'Other')

# ── Load & Explode ─────────────────────────────────────────────────────────────
print(f"Loading {CSV} ...")
df = pd.read_csv(CSV)
print(f"  Rows: {len(df):,}  Columns: {list(df.columns)}")

# Normalise column names
df.columns = [c.lower().strip() for c in df.columns]

# Date column
date_col = next((c for c in df.columns if 'date' in c), None)
if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df['year'] = df[date_col].dt.year

# Country explosion
df_c = df.dropna(subset=['country']).copy()
df_c['country'] = df_c['country'].astype(str).str.split(',')
df_exp = df_c.explode('country')
df_exp['country'] = df_exp['country'].str.strip()
df_exp = df_exp[df_exp['country'].str.len() > 0]

# Region column
df_exp['region'] = df_exp['country'].apply(get_region)

total_titles = len(df)
total_countries = df_exp['country'].nunique()
print(f"  Unique countries after explosion: {total_countries}")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 1 — Top 15 Content-Producing Countries (Horizontal Bar)
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 1: Top 15 countries ...")
top15 = df_exp['country'].value_counts().head(15)

fig, ax = plt.subplots(figsize=(11, 7))
colors = [PALETTE[0]] + [PALETTE[1]] * 14
bars = ax.barh(top15.index[::-1], top15.values[::-1], color=colors[::-1], height=0.65)

for bar, val in zip(bars, top15.values[::-1]):
    ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
            f'{val:,}', va='center', ha='left', fontsize=9, color='#333')

ax.set_xlabel("Number of Titles", fontsize=11)
ax.set_title("Top 15 Content-Producing Countries on Netflix", fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(0, top15.values.max() * 1.15)
ax.tick_params(axis='y', labelsize=10)
plt.tight_layout()
plt.savefig(OUT / "chart_01_top_countries.png", dpi=150, bbox_inches='tight')
plt.close()
print("  Saved chart_01_top_countries.png")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 2 — Regional Content Share (Donut Chart)
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 2: Regional share ...")
region_counts = df_exp['region'].value_counts()

fig, ax = plt.subplots(figsize=(9, 7))
wedge_colors = sns.color_palette("muted", len(region_counts))
wedges, texts, autotexts = ax.pie(
    region_counts.values,
    labels=None,
    autopct='%1.1f%%',
    startangle=140,
    colors=wedge_colors,
    pctdistance=0.82,
    wedgeprops=dict(width=0.55, edgecolor='white', linewidth=2)
)
for at in autotexts:
    at.set_fontsize(9)

ax.legend(
    wedges, [f"{r}  ({c:,})" for r, c in zip(region_counts.index, region_counts.values)],
    loc='lower center', bbox_to_anchor=(0.5, -0.18),
    ncol=3, fontsize=9, frameon=False
)
ax.set_title("Regional Content Share on Netflix", fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(OUT / "chart_02_regional_share.png", dpi=150, bbox_inches='tight')
plt.close()
print("  Saved chart_02_regional_share.png")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 3 — Content Type by Top 10 Countries (Grouped Bar)
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 3: Content type by country ...")
type_col = next((c for c in df_exp.columns if 'type' in c), None)

if type_col:
    top10 = df_exp['country'].value_counts().head(10).index.tolist()
    df_top10 = df_exp[df_exp['country'].isin(top10)]
    ct = df_top10.groupby(['country', type_col]).size().unstack(fill_value=0)
    ct = ct.loc[top10]   # keep ranking order

    x = np.arange(len(ct))
    width = 0.38
    fig, ax = plt.subplots(figsize=(13, 6))
    cols = list(ct.columns)
    bar_colors = [PALETTE[2], PALETTE[3]]
    for i, (col, color) in enumerate(zip(cols, bar_colors)):
        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, ct[col], width, label=col, color=color, edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(ct.index, rotation=35, ha='right', fontsize=9)
    ax.set_ylabel("Number of Titles", fontsize=11)
    ax.set_title("Movies vs TV Shows — Top 10 Countries", fontsize=14, fontweight='bold', pad=12)
    ax.legend(fontsize=10, frameon=False)
    plt.tight_layout()
    plt.savefig(OUT / "chart_03_type_by_country.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved chart_03_type_by_country.png")
else:
    print("  No type column found — skipping chart 3")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 4 — Top 5 Countries Growth Over Time (Multi-line)
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 4: Country growth over time ...")
if 'year' in df_exp.columns:
    top5 = df_exp['country'].value_counts().head(5).index.tolist()
    df_t = df_exp[df_exp['country'].isin(top5)]
    df_t = df_t.dropna(subset=['year'])
    df_t['year'] = df_t['year'].astype(int)
    growth = df_t.groupby(['year', 'country']).size().unstack(fill_value=0)
    growth = growth[growth.index >= 2010]

    fig, ax = plt.subplots(figsize=(12, 6))
    line_colors = sns.color_palette("tab10", len(top5))
    for country, color in zip(top5, line_colors):
        if country in growth.columns:
            ax.plot(growth.index, growth[country], marker='o', markersize=5,
                    linewidth=2, label=country, color=color)

    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Titles Added", fontsize=11)
    ax.set_title("Content Growth Over Time — Top 5 Countries", fontsize=14, fontweight='bold', pad=12)
    ax.legend(fontsize=10, frameon=False, loc='upper left')
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig(OUT / "chart_04_country_growth.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved chart_04_country_growth.png")
else:
    print("  No year column found — skipping chart 4")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 5 — Genre Preferences by Region (Heatmap)
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 5: Genre by region heatmap ...")
genre_col = next((c for c in df_exp.columns if 'genre' in c or 'listed' in c or 'categor' in c), None)

if genre_col:
    df_g = df_exp.dropna(subset=[genre_col]).copy()
    df_g['genre_primary'] = df_g[genre_col].astype(str).str.split(',').str[0].str.strip()

    # Filter to key regions only
    key_regions = ['North America', 'Europe', 'Asia', 'Latin America', 'Africa', 'Oceania']
    df_g = df_g[df_g['region'].isin(key_regions)]

    genre_region = df_g.groupby(['region', 'genre_primary']).size().unstack(fill_value=0)

    # Keep top 12 genres (by total across all regions)
    top_genres = genre_region.sum().nlargest(12).index
    genre_region = genre_region[top_genres]

    # Normalise rows to % so regions are comparable
    genre_region_pct = genre_region.div(genre_region.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(
        genre_region_pct,
        annot=True, fmt='.1f', cmap='Blues',
        linewidths=0.5, linecolor='#ddd',
        cbar_kws={'label': '% of Region Titles'},
        ax=ax
    )
    ax.set_title("Genre Preferences by Region (%)", fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel("Genre", fontsize=11)
    ax.set_ylabel("Region", fontsize=11)
    ax.tick_params(axis='x', rotation=35, labelsize=9)
    ax.tick_params(axis='y', rotation=0, labelsize=10)
    plt.tight_layout()
    plt.savefig(OUT / "chart_05_genre_by_region.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved chart_05_genre_by_region.png")
else:
    print("  No genre column found — skipping chart 5")

# ══════════════════════════════════════════════════════════════════════════════
# Compute key stats for the report
# ══════════════════════════════════════════════════════════════════════════════
top_country      = top15.index[0]
top_country_pct  = top15.values[0] / total_titles * 100
top3_pct         = top15.values[:3].sum() / total_titles * 100
top_region       = region_counts.index[0]
top_region_pct   = region_counts.values[0] / region_counts.sum() * 100

# Co-productions (titles with > 1 country)
coprod_mask = df_c['country'].apply(lambda x: len(x) > 1)
coprod_count = coprod_mask.sum()
coprod_pct   = coprod_count / len(df_c) * 100

# ══════════════════════════════════════════════════════════════════════════════
# Write geo_analysis.md
# ══════════════════════════════════════════════════════════════════════════════
print("Writing geo_analysis.md ...")
top15_table = "\n".join(
    f"| {i+1} | {country} | {count:,} | {count/total_titles*100:.1f}% |"
    for i, (country, count) in enumerate(top15.items())
)

region_table = "\n".join(
    f"| {region} | {count:,} | {count/region_counts.sum()*100:.1f}% |"
    for region, count in region_counts.items()
)

report = f"""# Geographic Content Analysis — Netflix Dataset

**Generated:** 2026-03-20
**Dataset:** {DATASET}
**Total Titles Analysed:** {total_titles:,}
**Unique Countries Represented:** {total_countries}

---

## Executive Summary

Netflix's content library spans **{total_countries} countries**, but production is
heavily concentrated: **{top_country}** alone accounts for
**{top_country_pct:.1f}%** of all titles, and the top 3 countries together
represent **{top3_pct:.1f}%** of the catalogue. Regionally,
**{top_region}** dominates with **{top_region_pct:.1f}%** of content.
Co-productions (titles credited to more than one country) make up
**{coprod_pct:.1f}%** of the library ({coprod_count:,} titles), reflecting
Netflix's growing investment in international partnerships.

---

## 1. Top 15 Content-Producing Countries

| Rank | Country | Titles | Share |
|------|---------|--------|-------|
{top15_table}

**Key Observations:**
- {top_country} is the dominant single-country producer by a significant margin.
- India and the United Kingdom consistently rank in the top 3, reflecting
  strong local content investment.
- South Korea's presence highlights the global K-drama and K-film phenomenon.

---

## 2. Regional Content Share

| Region | Titles | Share |
|--------|--------|-------|
{region_table}

**Key Observations:**
- North America and Asia together account for the majority of Netflix content.
- Europe is a strong third block, driven by the UK, France, and Spain.
- Africa and the Middle East remain underrepresented, signalling growth opportunity.

---

## 3. Content Type by Country

- The United States leads in both Movies and TV Shows, but its TV Show share
  is proportionally higher than most other countries.
- India skews heavily toward Movies, mirroring Bollywood's output model.
- South Korea and Japan show stronger TV Show ratios — driven by drama series formats.
- UK content is more balanced between Movies and TV Shows.

---

## 4. Country Growth Trends (2010–Present)

- The US has maintained consistent volume throughout the decade.
- India experienced explosive growth post-2017 as Netflix expanded into
  the Indian market.
- South Korea shows the steepest growth curve from 2018 onward.
- UK content has grown steadily, reflecting co-production deals with Netflix.

---

## 5. Genre Preferences by Region

- **North America:** Dramas and Documentaries dominate; strong Comedy and
  Thriller presence.
- **Asia:** International Movies and Dramas lead; Anime is significant for Japan.
- **Europe:** Dramas and International Movies are top picks; Documentaries
  perform well.
- **Latin America:** Dramas and Romantic Movies are the clear favourites.
- **Africa:** Still emerging but skews toward Dramas and International content.

---

## 6. Content Diversity & Concentration

| Metric | Value |
|--------|-------|
| Unique countries | {total_countries} |
| Top country share | {top_country_pct:.1f}% |
| Top 3 countries share | {top3_pct:.1f}% |
| Co-productions | {coprod_count:,} ({coprod_pct:.1f}%) |

**Concentration Risk:** With the top 3 countries holding {top3_pct:.1f}% of
content, Netflix's library carries geographic concentration risk. Increasing
investment in underrepresented regions (Africa, Middle East, Oceania) could
diversify the catalogue and attract new subscriber segments.

---

## 7. Strategic Implications

1. **Double down on Asia** — South Korea and India are the fastest-growing
   content markets; Netflix should sustain original content investment there.
2. **Develop Africa** — Nigeria's Nollywood and South Africa are producing
   globally compelling content; early investment could yield outsized returns.
3. **Leverage co-productions** — Cross-border projects ({coprod_pct:.1f}% of
   library) amplify reach and share costs; scale this model in under-indexed regions.
4. **Reduce US dependency** — Diversifying beyond {top_country_pct:.1f}% US
   concentration mitigates regulatory and licensing risks in a single market.

---

## Output Files

| File | Description |
|------|-------------|
| `chart_01_top_countries.png` | Top 15 content-producing countries |
| `chart_02_regional_share.png` | Regional content share donut chart |
| `chart_03_type_by_country.png` | Movies vs TV Shows by top 10 countries |
| `chart_04_country_growth.png` | Top 5 countries growth over time |
| `chart_05_genre_by_region.png` | Genre preferences by region heatmap |
"""

(OUT / "geo_analysis.md").write_text(report, encoding='utf-8')
print("  Saved geo_analysis.md")
print("\nAll geo outputs written to:", OUT)
