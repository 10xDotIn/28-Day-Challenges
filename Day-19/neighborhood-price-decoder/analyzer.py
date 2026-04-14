#!/usr/bin/env python3
"""Neighborhood Price Decoder — Real Estate Intelligence Analyzer"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import os, json, textwrap

# Setup
os.makedirs('output', exist_ok=True)
plt.rcParams.update({
    'figure.facecolor': '#0f0f0f', 'axes.facecolor': '#1a1a2e',
    'axes.edgecolor': '#333', 'text.color': '#e0e0e0',
    'axes.labelcolor': '#e0e0e0', 'xtick.color': '#aaa',
    'ytick.color': '#aaa', 'grid.color': '#333', 'grid.alpha': 0.3,
    'font.size': 11
})

df = pd.read_csv('data/listings.csv')
print(f"Loaded {len(df)} listings across {df['neighborhood'].nunique()} neighborhoods")

# ============================================================
# 1. NEIGHBORHOOD PRICE MAP
# ============================================================
print("\n=== 1. Neighborhood Price Map ===")
hood_stats = df.groupby('neighborhood').agg(
    avg_ppsf=('price_per_sqft', 'mean'),
    med_ppsf=('price_per_sqft', 'median'),
    min_ppsf=('price_per_sqft', 'min'),
    max_ppsf=('price_per_sqft', 'max'),
    avg_price=('listing_price', 'mean'),
    count=('listing_id', 'count'),
    avg_gap=('price_gap_percent', 'mean'),
    avg_appr=('predicted_1yr_appreciation', 'mean'),
    avg_crime=('crime_index', 'mean'),
    avg_school=('school_rating', 'mean'),
    avg_metro=('metro_distance_miles', 'mean'),
).sort_values('avg_ppsf', ascending=False)

for i, (n, r) in enumerate(hood_stats.iterrows(), 1):
    print(f"  {i:2d}. {n:25s} ${r.avg_ppsf:6.0f}/sqft  (${r.min_ppsf:.0f}-${r.max_ppsf:.0f})")

# ============================================================
# 2. PRICE DRIVERS — Feature Importance
# ============================================================
print("\n=== 2. What Drives Price? ===")

# Encode categoricals
df_model = df.copy()
df_model['condition_score'] = df_model['condition'].map({
    'Needs Work': 1, 'Average': 2, 'Good': 3, 'Renovated': 4, 'New': 5
})
df_model['decade_built'] = (df_model['year_built'] - 1950) / 10
prop_dummies = pd.get_dummies(df_model['property_type'], prefix='type', drop_first=True)
df_model = pd.concat([df_model, prop_dummies], axis=1)

features = ['sqft', 'bedrooms', 'bathrooms', 'floor', 'decade_built', 'condition_score',
            'has_parking', 'has_gym', 'has_pool', 'has_doorman',
            'metro_distance_miles', 'school_rating', 'crime_index',
            'restaurants_nearby', 'park_access_score', 'noise_level']
features += [c for c in prop_dummies.columns]

X = df_model[features].fillna(0)
y = df_model['listing_price']

model = LinearRegression()
model.fit(X, y)
r2 = model.score(X, y)
print(f"  R² = {r2:.4f}")

coef_df = pd.DataFrame({'feature': features, 'coef': model.coef_})

# Calculate dollar impacts with meaningful units
impact_items = []
def add_impact(name, label, multiplier=1):
    c = coef_df.loc[coef_df.feature == name, 'coef'].values[0]
    dollar = c * multiplier
    impact_items.append({'factor': label, 'dollar_impact': dollar, 'raw_coef': c, 'mult': multiplier})

add_impact('metro_distance_miles', 'Metro: +1 mile further', 1)
add_impact('school_rating', 'School: +1 rating point', 1)
add_impact('crime_index', 'Crime: +10 points higher', 10)
add_impact('park_access_score', 'Park access: +1 point', 1)
add_impact('noise_level', 'Noise: +10 points higher', 10)
add_impact('floor', 'Floor: +1 floor higher', 1)
add_impact('has_parking', 'Having parking', 1)
add_impact('has_gym', 'Having gym', 1)
add_impact('has_pool', 'Having pool', 1)
add_impact('has_doorman', 'Having doorman', 1)
add_impact('sqft', 'Size: +100 sqft', 100)
add_impact('bedrooms', 'Bedrooms: +1 bedroom', 1)
add_impact('bathrooms', 'Bathrooms: +1 bathroom', 1)
add_impact('condition_score', 'Condition: New vs Needs Work', 4)  # 4 steps from NW to New
add_impact('decade_built', 'Age: 1 decade newer', 1)
add_impact('restaurants_nearby', 'Restaurants: +10 nearby', 10)

impact_df = pd.DataFrame(impact_items).sort_values('dollar_impact', key=abs, ascending=False)

for _, r in impact_df.iterrows():
    sign = '+' if r.dollar_impact > 0 else ''
    print(f"  {r.factor:35s} = {sign}${r.dollar_impact:,.0f}")

# ============================================================
# 3. OVERPRICED / UNDERPRICED DETECTOR
# ============================================================
print("\n=== 3. Overpriced / Underpriced Detector ===")
df['price_gap_dollar'] = df['listing_price'] - df['estimated_fair_value']

overpriced = df.nlargest(10, 'price_gap_percent')
underpriced = df.nsmallest(10, 'price_gap_percent')

print("  TOP 10 OVERPRICED:")
for _, r in overpriced.iterrows():
    print(f"    {r.listing_id} {r.neighborhood:20s} ${r.listing_price:>10,.0f}  gap: +{r.price_gap_percent:.1f}%  DOM: {r.days_on_market}")

print("  TOP 10 UNDERPRICED (deals):")
for _, r in underpriced.iterrows():
    print(f"    {r.listing_id} {r.neighborhood:20s} ${r.listing_price:>10,.0f}  gap: {r.price_gap_percent:.1f}%  DOM: {r.days_on_market}")

avg_dom_over = df[df.price_gap_percent > 10]['days_on_market'].mean()
avg_dom_under = df[df.price_gap_percent < -10]['days_on_market'].mean()
avg_dom_fair = df[df.price_gap_percent.abs() <= 5]['days_on_market'].mean()
dom_gap_corr = df['days_on_market'].corr(df['price_gap_percent'])
print(f"  Avg DOM: overpriced={avg_dom_over:.0f}, underpriced={avg_dom_under:.0f}, fair={avg_dom_fair:.0f}")
print(f"  DOM vs price_gap correlation: {dom_gap_corr:.3f}")

# ============================================================
# 4. METRO PREMIUM
# ============================================================
print("\n=== 4. Metro Premium ===")
metro_bins = [0, 0.2, 0.5, 1.0, 2.0, 4.0, 10.0]
metro_labels = ['<0.2mi', '0.2-0.5', '0.5-1.0', '1.0-2.0', '2.0-4.0', '4.0+']
df['metro_band'] = pd.cut(df['metro_distance_miles'], bins=metro_bins, labels=metro_labels)
metro_ppsf = df.groupby('metro_band', observed=True)['price_per_sqft'].mean()
for band, val in metro_ppsf.items():
    print(f"  {band:12s}: ${val:.0f}/sqft")

metro_coef = coef_df.loc[coef_df.feature == 'metro_distance_miles', 'coef'].values[0]
avg_sqft = df['sqft'].mean()
print(f"  Every 1 mile further = ${metro_coef:,.0f} on listing price")
print(f"  At avg {avg_sqft:.0f} sqft, metro premium per mile = ${metro_coef:,.0f}")

# ============================================================
# 5. SCHOOL RATING TAX
# ============================================================
print("\n=== 5. School Rating Tax ===")
school_ppsf = df.groupby('school_rating')['price_per_sqft'].mean().sort_index()
for rating, val in school_ppsf.items():
    print(f"  Rating {rating}: ${val:.0f}/sqft")

school_coef = coef_df.loc[coef_df.feature == 'school_rating', 'coef'].values[0]
print(f"  Each school rating point = ${school_coef:,.0f} on listing price")

# Best school-to-price ratio
hood_school_val = df.groupby('neighborhood').agg(
    avg_school=('school_rating', 'mean'),
    avg_ppsf=('price_per_sqft', 'mean')
)
hood_school_val['school_per_dollar'] = hood_school_val['avg_school'] / hood_school_val['avg_ppsf'] * 100
best_sv = hood_school_val.sort_values('school_per_dollar', ascending=False)
print("  Best school-to-price ratio:")
for n, r in best_sv.head(5).iterrows():
    print(f"    {n:25s} school={r.avg_school:.1f} ppsf=${r.avg_ppsf:.0f}")

# ============================================================
# 6. SAFETY PREMIUM
# ============================================================
print("\n=== 6. Safety Premium ===")
crime_coef = coef_df.loc[coef_df.feature == 'crime_index', 'coef'].values[0]
print(f"  Every 10 points on crime index = ${crime_coef*10:,.0f}")
crime_corr = df['crime_index'].corr(df['price_per_sqft'])
print(f"  Crime vs price/sqft correlation: {crime_corr:.3f}")

# Safe-but-far vs close-but-risky
safe_far = df[(df.crime_index < 25) & (df.metro_distance_miles > 2)]
risky_close = df[(df.crime_index > 50) & (df.metro_distance_miles < 0.5)]
print(f"  Safe-but-far ({len(safe_far)} listings): avg ${safe_far.price_per_sqft.mean():.0f}/sqft")
print(f"  Close-but-risky ({len(risky_close)} listings): avg ${risky_close.price_per_sqft.mean():.0f}/sqft")

# ============================================================
# 7. SMART BUYER SCORE
# ============================================================
print("\n=== 7. Smart Buyer Score ===")

def normalize(s, invert=False):
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series(0.5, index=s.index)
    n = (s - mn) / (mx - mn)
    return 1 - n if invert else n

df['score_value'] = normalize(-df['price_gap_percent'])  # more negative = better deal
df['score_growth'] = normalize(df['predicted_1yr_appreciation'])
df['score_quality'] = (normalize(df['school_rating']) + normalize(df['crime_index'], invert=True)) / 2
df['score_access'] = (normalize(df['metro_distance_miles'], invert=True) +
                      normalize(df['has_parking'] + df['has_gym'] + df['has_pool'] + df['has_doorman'])) / 2

df['smart_buyer_score'] = (
    0.30 * df['score_value'] +
    0.25 * df['score_growth'] +
    0.25 * df['score_quality'] +
    0.20 * df['score_access']
)

top_deals = df.nlargest(20, 'smart_buyer_score')
print("  TOP 20 DEALS:")
for i, (_, r) in enumerate(top_deals.iterrows(), 1):
    print(f"  {i:2d}. #{r.listing_id} {r.neighborhood:20s} ${r.listing_price:>10,.0f} "
          f"gap={r.price_gap_percent:+.1f}% appr={r.predicted_1yr_appreciation:+.1f}% "
          f"score={r.smart_buyer_score:.3f}")

# ============================================================
# 8. NEIGHBORHOOD INVESTMENT RECOMMENDATIONS
# ============================================================
print("\n=== 8. Investment Recommendations ===")

hood_inv = df.groupby('neighborhood').agg(
    avg_ppsf=('price_per_sqft', 'mean'),
    avg_gap=('price_gap_percent', 'mean'),
    avg_appr=('predicted_1yr_appreciation', 'mean'),
    avg_school=('school_rating', 'mean'),
    avg_crime=('crime_index', 'mean'),
    avg_metro=('metro_distance_miles', 'mean'),
    pct_sold=('sold', 'mean'),
    avg_dom=('days_on_market', 'mean'),
).sort_values('avg_appr', ascending=False)

def classify(r):
    if r.avg_gap < -3 and r.avg_appr > 5:
        return 'BUY NOW'
    elif r.avg_gap > 3 and r.avg_school >= 7 and r.avg_crime < 30:
        return 'PREMIUM BUT WORTH IT'
    elif r.avg_gap > 5 and r.avg_appr < 3:
        return 'OVERPRICED RISK'
    elif r.avg_crime > 50 and r.avg_school < 6 and r.avg_appr < 3:
        return 'AVOID'
    elif r.avg_gap < 0 and r.avg_appr > 4:
        return 'HIDDEN GEM'
    elif r.avg_gap < -2:
        return 'BUY NOW'
    elif r.avg_appr > 5:
        return 'HIDDEN GEM'
    elif r.avg_gap > 3:
        return 'OVERPRICED RISK'
    else:
        return 'HOLD / NEUTRAL'

hood_inv['recommendation'] = hood_inv.apply(classify, axis=1)
hood_inv['est_3yr_return'] = hood_inv['avg_appr'] * 2.8  # slightly compounded

rec_colors = {
    'BUY NOW': '#00c853', 'HIDDEN GEM': '#00e5ff', 'PREMIUM BUT WORTH IT': '#ffd600',
    'HOLD / NEUTRAL': '#888', 'OVERPRICED RISK': '#ff6d00', 'AVOID': '#ff1744'
}

for n, r in hood_inv.iterrows():
    print(f"  {r.recommendation:22s} | {n:25s} | gap={r.avg_gap:+.1f}% appr={r.avg_appr:+.1f}% crime={r.avg_crime:.0f} school={r.avg_school:.1f}")

# ============================================================
# CHARTS
# ============================================================
print("\n=== Generating Charts ===")

# --- neighborhood_map.png ---
fig, ax = plt.subplots(figsize=(14, 8))
hs = hood_stats.sort_values('avg_ppsf')
colors = [rec_colors.get(hood_inv.loc[n, 'recommendation'], '#888') for n in hs.index]
bars = ax.barh(hs.index, hs['avg_ppsf'], color=colors, edgecolor='#333', height=0.7)
# Range whiskers
for i, (n, r) in enumerate(hs.iterrows()):
    ax.plot([r.min_ppsf, r.max_ppsf], [i, i], color='#fff', alpha=0.3, linewidth=1)
ax.set_xlabel('Avg Price per Sqft ($)')
ax.set_title('Neighborhood Price Map — Ranked by $/sqft', fontsize=16, fontweight='bold', pad=15)
for bar, (n, r) in zip(bars, hs.iterrows()):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
            f'${r.avg_ppsf:.0f}', va='center', fontsize=10, color='#e0e0e0')
# Legend
from matplotlib.patches import Patch
legend_items = [Patch(facecolor=c, label=l) for l, c in rec_colors.items() if l in hood_inv['recommendation'].values]
ax.legend(handles=legend_items, loc='lower right', fontsize=9, facecolor='#1a1a2e', edgecolor='#333')
plt.tight_layout()
plt.savefig('output/neighborhood_map.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved neighborhood_map.png")

# --- price_drivers.png ---
fig, ax = plt.subplots(figsize=(14, 9))
idf = impact_df.sort_values('dollar_impact')
colors_drv = ['#00c853' if v > 0 else '#ff1744' for v in idf['dollar_impact']]
ax.barh(idf['factor'], idf['dollar_impact'], color=colors_drv, edgecolor='#333', height=0.7)
ax.axvline(0, color='#555', linewidth=1)
ax.set_xlabel('Dollar Impact on Listing Price ($)')
ax.set_title('What Drives Price? — Every Factor Ranked by Dollar Impact', fontsize=16, fontweight='bold', pad=15)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
for i, (_, r) in enumerate(idf.iterrows()):
    sign = '+' if r.dollar_impact > 0 else ''
    ax.text(r.dollar_impact + (500 if r.dollar_impact >= 0 else -500),
            i, f'{sign}${r.dollar_impact:,.0f}', va='center', fontsize=9,
            ha='left' if r.dollar_impact >= 0 else 'right', color='#e0e0e0')
plt.tight_layout()
plt.savefig('output/price_drivers.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved price_drivers.png")

# --- overpriced_underpriced.png ---
fig, ax = plt.subplots(figsize=(12, 10))
neighborhoods = df['neighborhood'].unique()
palette = sns.color_palette('husl', len(neighborhoods))
hood_color = {n: palette[i] for i, n in enumerate(sorted(neighborhoods))}

for n in sorted(neighborhoods):
    sub = df[df.neighborhood == n].sample(min(200, len(df[df.neighborhood == n])), random_state=42)
    ax.scatter(sub['listing_price'], sub['estimated_fair_value'],
               c=[hood_color[n]], alpha=0.4, s=12, label=n)

mn, mx = df['listing_price'].min(), df['listing_price'].max()
ax.plot([mn, mx], [mn, mx], color='#ffd600', linewidth=2, linestyle='--', alpha=0.8, label='Fair Value Line')

# Highlight biggest gaps
for _, r in overpriced.head(3).iterrows():
    ax.annotate(f"#{r.listing_id}\n+{r.price_gap_percent:.0f}%",
                (r.listing_price, r.estimated_fair_value),
                fontsize=7, color='#ff6d00', fontweight='bold')
for _, r in underpriced.head(3).iterrows():
    ax.annotate(f"#{r.listing_id}\n{r.price_gap_percent:.0f}%",
                (r.listing_price, r.estimated_fair_value),
                fontsize=7, color='#00e5ff', fontweight='bold')

ax.set_xlabel('Listing Price ($)')
ax.set_ylabel('Estimated Fair Value ($)')
ax.set_title('Overpriced vs Underpriced — Listing Price vs Fair Value', fontsize=15, fontweight='bold', pad=15)
ax.legend(fontsize=7, loc='upper left', facecolor='#1a1a2e', edgecolor='#333', ncol=2)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M'))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M'))
plt.tight_layout()
plt.savefig('output/overpriced_underpriced.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved overpriced_underpriced.png")

# --- metro_premium.png ---
fig, ax = plt.subplots(figsize=(12, 7))
metro_fine = df.groupby(df['metro_distance_miles'].round(1))['price_per_sqft'].mean()
metro_fine = metro_fine[metro_fine.index <= 5]
ax.plot(metro_fine.index, metro_fine.values, color='#00e5ff', linewidth=2.5, marker='o', markersize=4)
ax.fill_between(metro_fine.index, metro_fine.values, alpha=0.15, color='#00e5ff')
ax.set_xlabel('Distance from Metro (miles)')
ax.set_ylabel('Avg Price per Sqft ($)')
ax.set_title('The Metro Premium — How Distance Kills Value', fontsize=15, fontweight='bold', pad=15)
ax.axhline(metro_fine.values[-1], color='#555', linestyle=':', alpha=0.5)
ax.annotate(f'Premium vanishes ~{metro_fine.index[metro_fine.values < metro_fine.values[0]*0.85].min():.1f} mi',
            xy=(3, metro_fine.values.mean()), fontsize=11, color='#ffd600')
plt.tight_layout()
plt.savefig('output/metro_premium.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved metro_premium.png")

# --- school_tax.png ---
fig, ax = plt.subplots(figsize=(12, 7))
school_ppsf_sorted = school_ppsf.sort_index()
colors_sch = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(school_ppsf_sorted)))
bars = ax.bar(school_ppsf_sorted.index.astype(str), school_ppsf_sorted.values,
              color=colors_sch, edgecolor='#333', width=0.6)
for bar, val in zip(bars, school_ppsf_sorted.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f'${val:.0f}', ha='center', fontsize=11, color='#e0e0e0')
ax.set_xlabel('School Rating')
ax.set_ylabel('Avg Price per Sqft ($)')
ax.set_title('The School Rating Tax — What Each Point Costs You', fontsize=15, fontweight='bold', pad=15)
# Delta annotation
lo, hi = school_ppsf_sorted.iloc[0], school_ppsf_sorted.iloc[-1]
ax.annotate(f'Rating {int(school_ppsf_sorted.index[-1])} vs {int(school_ppsf_sorted.index[0])}: +${hi-lo:.0f}/sqft',
            xy=(0.5, 0.92), xycoords='axes fraction', fontsize=12, color='#ffd600',
            ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('output/school_tax.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved school_tax.png")

# --- deal_finder.png ---
fig, ax = plt.subplots(figsize=(16, 10))
ax.axis('off')
ax.set_title('Top 20 Hidden Gems — Smart Buyer Deal Finder', fontsize=18, fontweight='bold', pad=20, color='#00e5ff')
cols = ['#', 'ID', 'Neighborhood', 'Type', 'Price', 'Gap%', '1yr Appr', 'School', 'Crime', 'Score']
col_x = [0.0, 0.04, 0.12, 0.32, 0.44, 0.56, 0.66, 0.76, 0.84, 0.92]

for j, col in enumerate(cols):
    ax.text(col_x[j], 0.97, col, fontsize=10, fontweight='bold', color='#ffd600',
            transform=ax.transAxes, va='top')

for i, (_, r) in enumerate(top_deals.iterrows()):
    y = 0.93 - i * 0.043
    bg_alpha = 0.08 if i % 2 == 0 else 0.03
    ax.axhspan(y - 0.015, y + 0.025, color='white', alpha=bg_alpha, transform=ax.transAxes)
    vals = [
        f'{i+1}', f'{r.listing_id}', r.neighborhood, r.property_type,
        f'${r.listing_price:,.0f}', f'{r.price_gap_percent:+.1f}%',
        f'{r.predicted_1yr_appreciation:+.1f}%', f'{r.school_rating}',
        f'{r.crime_index:.0f}', f'{r.smart_buyer_score:.3f}'
    ]
    gap_color = '#00c853' if r.price_gap_percent < 0 else '#ff6d00'
    for j, v in enumerate(vals):
        c = gap_color if j == 5 else ('#00c853' if j == 6 and r.predicted_1yr_appreciation > 5 else '#e0e0e0')
        ax.text(col_x[j], y, v, fontsize=9, color=c, transform=ax.transAxes, va='top')

plt.tight_layout()
plt.savefig('output/deal_finder.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved deal_finder.png")

# ============================================================
# INVESTMENT REPORT (Markdown)
# ============================================================
print("\n=== Generating Investment Report ===")

most_overpriced_hood = hood_inv['avg_gap'].idxmax()
best_value_hood = hood_inv['avg_gap'].idxmin()
biggest_growth_hood = hood_inv['avg_appr'].idxmax()
top1_deal = top_deals.iloc[0]
pct_overpriced = (df['price_gap_percent'] > 5).mean() * 100
pct_underpriced = (df['price_gap_percent'] < -5).mean() * 100
avg_appreciation = df['predicted_1yr_appreciation'].mean()

report = f"""# Neighborhood Price Decoder — Investment Report
*Generated from {len(df):,} property listings across {df['neighborhood'].nunique()} neighborhoods*

---

## Executive Summary

- **{len(df):,} listings** analyzed across **{df['neighborhood'].nunique()} neighborhoods**
- **{pct_overpriced:.1f}%** of listings are overpriced (>5% above fair value)
- **{pct_underpriced:.1f}%** are hidden deals (>5% below fair value)
- Average predicted 1-year appreciation: **{avg_appreciation:+.1f}%**
- The #1 price driver is **{impact_df.iloc[0]['factor']}** at **${abs(impact_df.iloc[0]['dollar_impact']):,.0f}**

---

## Neighborhood Rankings by Price/Sqft

| Rank | Neighborhood | Avg $/sqft | Avg Gap | 1yr Growth | Recommendation |
|------|-------------|-----------|---------|------------|---------------|
"""

for i, (n, r) in enumerate(hood_inv.sort_values('avg_ppsf', ascending=False).iterrows(), 1):
    report += f"| {i} | {n} | ${r.avg_ppsf:.0f} | {r.avg_gap:+.1f}% | {r.avg_appr:+.1f}% | {r.recommendation} |\n"

report += f"""
---

## What Drives Price — Every Factor Ranked

| Factor | Dollar Impact |
|--------|-------------|
"""

for _, r in impact_df.iterrows():
    sign = '+' if r.dollar_impact > 0 else ''
    report += f"| {r.factor} | {sign}${r.dollar_impact:,.0f} |\n"

report += f"""
Model R² = {r2:.4f} — the model explains {r2*100:.1f}% of price variation.

---

## Top 10 Overpriced Traps to Avoid

| Listing | Neighborhood | Price | Fair Value | Gap | DOM |
|---------|-------------|-------|-----------|-----|-----|
"""

for _, r in overpriced.iterrows():
    report += f"| {r.listing_id} | {r.neighborhood} | ${r.listing_price:,.0f} | ${r.estimated_fair_value:,.0f} | +{r.price_gap_percent:.1f}% | {r.days_on_market} |\n"

report += f"""
---

## Top 10 Hidden Deals to Grab

| Listing | Neighborhood | Price | Fair Value | Gap | 1yr Appr | DOM |
|---------|-------------|-------|-----------|-----|----------|-----|
"""

for _, r in underpriced.iterrows():
    report += f"| {r.listing_id} | {r.neighborhood} | ${r.listing_price:,.0f} | ${r.estimated_fair_value:,.0f} | {r.price_gap_percent:.1f}% | {r.predicted_1yr_appreciation:+.1f}% | {r.days_on_market} |\n"

report += f"""
---

## The Metro Premium

Every mile further from metro = **${abs(metro_coef):,.0f}** less on listing price.

| Distance Band | Avg $/sqft |
|--------------|-----------|
"""

for band, val in metro_ppsf.items():
    report += f"| {band} | ${val:.0f} |\n"

report += f"""
Moving 0.5 miles from the station saves you approximately **${abs(metro_coef)*0.5:,.0f}** but costs commute time daily.

---

## The School Rating Tax

Each school rating point = **${abs(school_coef):,.0f}** on listing price.

| Rating | Avg $/sqft |
|--------|-----------|
"""

for rating, val in school_ppsf_sorted.items():
    report += f"| {rating} | ${val:.0f} |\n"

report += f"""
A school rating of 9 vs 7 adds approximately **${abs(school_coef)*2:,.0f}** to your property.

---

## The Safety Premium — Crime's Dollar Impact

Every 10 points on crime index = **${abs(crime_coef)*10:,.0f}** impact on price.
Crime-price correlation: **{crime_corr:.3f}**

- Safe-but-far ({len(safe_far)} listings): avg **${safe_far.price_per_sqft.mean():.0f}/sqft**
- Close-but-risky ({len(risky_close)} listings): avg **${risky_close.price_per_sqft.mean():.0f}/sqft**

---

## Investment Recommendations

"""

for cat in ['BUY NOW', 'HIDDEN GEM', 'PREMIUM BUT WORTH IT', 'HOLD / NEUTRAL', 'OVERPRICED RISK', 'AVOID']:
    hoods = hood_inv[hood_inv.recommendation == cat]
    if len(hoods) > 0:
        report += f"### {cat}\n"
        for n, r in hoods.iterrows():
            report += f"- **{n}**: ${r.avg_ppsf:.0f}/sqft, gap {r.avg_gap:+.1f}%, 1yr {r.avg_appr:+.1f}%, 3yr est {r.est_3yr_return:+.1f}%\n"
        report += "\n"

report += f"""---

## 5 Rules for Smart Property Buying

1. **Location over luxury**: Metro distance and school rating drive more value than pools or gyms
2. **The 5% rule**: Any listing >5% above fair value will sit on market — negotiate hard or walk away
3. **Crime costs more than you think**: Every 10 points on crime index = ${abs(crime_coef)*10:,.0f} in lost value
4. **Schools are the hidden tax**: Families pay ${abs(school_coef):,.0f} per rating point — know what you're buying
5. **Buy the dip**: Underpriced listings in growing neighborhoods ({biggest_growth_hood}) offer the best returns

---

## Final Verdict

- **Most overpriced neighborhood**: {most_overpriced_hood} (avg gap {hood_inv.loc[most_overpriced_hood, 'avg_gap']:+.1f}%)
- **Best value neighborhood**: {best_value_hood} (avg gap {hood_inv.loc[best_value_hood, 'avg_gap']:+.1f}%)
- **Biggest growth opportunity**: {biggest_growth_hood} ({hood_inv.loc[biggest_growth_hood, 'avg_appr']:+.1f}% predicted)
- **#1 price driver**: {impact_df.iloc[0]['factor']} = ${abs(impact_df.iloc[0]['dollar_impact']):,.0f}
- **Best deal in dataset**: Listing #{int(top1_deal.listing_id)} in {top1_deal.neighborhood} — ${top1_deal.listing_price:,.0f} ({top1_deal.price_gap_percent:+.1f}% vs fair value, {top1_deal.predicted_1yr_appreciation:+.1f}% growth)
"""

with open('output/investment_report.md', 'w') as f:
    f.write(report)
print("  Saved investment_report.md")

# ============================================================
# DASHBOARD HTML
# ============================================================
print("\n=== Generating Dashboard ===")

# Prepare data for JS
hood_chart_data = []
for n, r in hood_stats.sort_values('avg_ppsf').iterrows():
    rec = hood_inv.loc[n, 'recommendation'] if n in hood_inv.index else 'N/A'
    hood_chart_data.append({
        'name': n, 'avg_ppsf': round(r.avg_ppsf, 0),
        'min_ppsf': round(r.min_ppsf, 0), 'max_ppsf': round(r.max_ppsf, 0),
        'recommendation': rec
    })

driver_chart_data = []
for _, r in impact_df.sort_values('dollar_impact').iterrows():
    driver_chart_data.append({'factor': r.factor, 'impact': round(r.dollar_impact, 0)})

metro_chart_data = [{'dist': float(d), 'ppsf': round(float(v), 0)} for d, v in metro_fine.items()]
school_chart_data = [{'rating': int(r), 'ppsf': round(float(v), 0)} for r, v in school_ppsf_sorted.items()]

crime_scatter = df.sample(2000, random_state=42)[['crime_index', 'price_per_sqft', 'neighborhood']].to_dict('records')
for r in crime_scatter:
    r['crime_index'] = round(r['crime_index'], 1)
    r['price_per_sqft'] = round(r['price_per_sqft'], 0)

underpriced_table = []
for _, r in underpriced.iterrows():
    underpriced_table.append({
        'id': int(r.listing_id), 'hood': r.neighborhood, 'type': r.property_type,
        'price': int(r.listing_price), 'fair': int(r.estimated_fair_value),
        'gap': round(r.price_gap_percent, 1), 'appr': round(r.predicted_1yr_appreciation, 1),
        'dom': int(r.days_on_market)
    })

overpriced_table = []
for _, r in overpriced.iterrows():
    overpriced_table.append({
        'id': int(r.listing_id), 'hood': r.neighborhood, 'type': r.property_type,
        'price': int(r.listing_price), 'fair': int(r.estimated_fair_value),
        'gap': round(r.price_gap_percent, 1), 'dom': int(r.days_on_market)
    })

deals_table = []
for i, (_, r) in enumerate(top_deals.iterrows(), 1):
    deals_table.append({
        'rank': i, 'id': int(r.listing_id), 'hood': r.neighborhood, 'type': r.property_type,
        'price': int(r.listing_price), 'gap': round(r.price_gap_percent, 1),
        'appr': round(r.predicted_1yr_appreciation, 1), 'school': round(r.school_rating, 1),
        'crime': round(r.crime_index, 0), 'score': round(r.smart_buyer_score, 3)
    })

inv_data = []
for n, r in hood_inv.iterrows():
    inv_data.append({
        'name': n, 'rec': r.recommendation, 'ppsf': round(r.avg_ppsf, 0),
        'gap': round(r.avg_gap, 1), 'appr': round(r.avg_appr, 1),
        'crime': round(r.avg_crime, 0), 'school': round(r.avg_school, 1),
        'ret3': round(r.est_3yr_return, 1)
    })

# Key insights
insights = [
    f"The #1 price driver is <b>{impact_df.iloc[0]['factor']}</b> at <b>${abs(impact_df.iloc[0]['dollar_impact']):,.0f}</b>",
    f"<b>{pct_underpriced:.1f}%</b> of listings are underpriced — hidden deals waiting to be grabbed",
    f"Every mile from metro costs <b>${abs(metro_coef):,.0f}</b> — proximity is king",
    f"<b>{most_overpriced_hood}</b> is the most overpriced neighborhood (avg +{hood_inv.loc[most_overpriced_hood, 'avg_gap']:.1f}%)",
    f"<b>{biggest_growth_hood}</b> has the highest predicted growth at <b>{hood_inv.loc[biggest_growth_hood, 'avg_appr']:+.1f}%</b>"
]

avg_price = df['listing_price'].mean()
avg_ppsf_all = df['price_per_sqft'].mean()

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Neighborhood Price Decoder</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0f0f0f; color:#e0e0e0; font-family:'Segoe UI',system-ui,-apple-system,sans-serif; }}
.container {{ max-width:1400px; margin:0 auto; padding:20px; }}
h1 {{ text-align:center; font-size:2.2em; margin:20px 0 5px; background:linear-gradient(135deg,#00e5ff,#ffd600); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.subtitle {{ text-align:center; color:#888; margin-bottom:30px; font-size:1.1em; }}
.hero {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:15px; margin-bottom:30px; }}
.hero-card {{ background:#1a1a2e; border-radius:12px; padding:20px; text-align:center; border:1px solid #333; }}
.hero-card .value {{ font-size:2em; font-weight:700; color:#00e5ff; }}
.hero-card .label {{ color:#888; font-size:0.85em; margin-top:5px; }}
.section {{ background:#1a1a2e; border-radius:12px; padding:25px; margin-bottom:20px; border:1px solid #333; }}
.section h2 {{ color:#ffd600; font-size:1.3em; margin-bottom:15px; }}
.chart-container {{ width:100%; overflow-x:auto; }}
canvas {{ max-width:100%; }}
table {{ width:100%; border-collapse:collapse; font-size:0.9em; }}
th {{ background:#16213e; color:#ffd600; padding:10px 8px; text-align:left; position:sticky; top:0; }}
td {{ padding:8px; border-bottom:1px solid #222; }}
tr:hover {{ background:#16213e44; }}
.positive {{ color:#00c853; }} .negative {{ color:#ff1744; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
@media(max-width:900px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
.inv-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:15px; }}
.inv-card {{ background:#111; border-radius:10px; padding:18px; border-left:4px solid #888; }}
.inv-card.buy {{ border-left-color:#00c853; }} .inv-card.gem {{ border-left-color:#00e5ff; }}
.inv-card.premium {{ border-left-color:#ffd600; }} .inv-card.risk {{ border-left-color:#ff6d00; }}
.inv-card.avoid {{ border-left-color:#ff1744; }} .inv-card.hold {{ border-left-color:#888; }}
.inv-card .rec {{ font-size:0.8em; font-weight:700; margin-bottom:5px; }}
.inv-card .hood {{ font-size:1.1em; font-weight:600; color:#fff; }}
.inv-card .stats {{ color:#aaa; font-size:0.85em; margin-top:8px; line-height:1.6; }}
.insight-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:15px; }}
.insight {{ background:#111; border-radius:10px; padding:15px; border-top:3px solid #00e5ff; font-size:0.95em; line-height:1.5; }}
.insight b {{ color:#ffd600; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
<div class="container">
<h1>Neighborhood Price Decoder</h1>
<p class="subtitle">Real Estate Intelligence Dashboard &mdash; {len(df):,} Listings Analyzed</p>

<div class="hero">
  <div class="hero-card"><div class="value">{len(df):,}</div><div class="label">Total Listings</div></div>
  <div class="hero-card"><div class="value">${avg_price:,.0f}</div><div class="label">Avg Price</div></div>
  <div class="hero-card"><div class="value">${avg_ppsf_all:.0f}</div><div class="label">Avg $/sqft</div></div>
  <div class="hero-card"><div class="value">{pct_overpriced:.1f}%</div><div class="label">Overpriced</div></div>
  <div class="hero-card"><div class="value">{pct_underpriced:.1f}%</div><div class="label">Underpriced</div></div>
  <div class="hero-card"><div class="value">{avg_appreciation:+.1f}%</div><div class="label">Avg 1yr Appreciation</div></div>
</div>

<div class="section">
<h2>Neighborhood Price Map</h2>
<div class="chart-container"><canvas id="hoodChart" height="400"></canvas></div>
</div>

<div class="section">
<h2>What Drives Price? &mdash; Dollar Impact of Every Factor</h2>
<div class="chart-container"><canvas id="driverChart" height="450"></canvas></div>
</div>

<div class="grid2">
<div class="section">
<h2>Top 10 Hidden Deals (Underpriced)</h2>
<div style="overflow-x:auto"><table>
<tr><th>ID</th><th>Neighborhood</th><th>Type</th><th>Price</th><th>Fair Value</th><th>Gap</th><th>1yr Appr</th><th>DOM</th></tr>
{"".join(f'<tr><td>{r["id"]}</td><td>{r["hood"]}</td><td>{r["type"]}</td><td>${r["price"]:,}</td><td>${r["fair"]:,}</td><td class="negative">{r["gap"]}%</td><td class="positive">+{r["appr"]}%</td><td>{r["dom"]}</td></tr>' for r in underpriced_table)}
</table></div>
</div>

<div class="section">
<h2>Top 10 Overpriced Traps</h2>
<div style="overflow-x:auto"><table>
<tr><th>ID</th><th>Neighborhood</th><th>Type</th><th>Price</th><th>Fair Value</th><th>Gap</th><th>DOM</th></tr>
{"".join(f'<tr><td>{r["id"]}</td><td>{r["hood"]}</td><td>{r["type"]}</td><td>${r["price"]:,}</td><td>${r["fair"]:,}</td><td class="positive">+{r["gap"]}%</td><td>{r["dom"]}</td></tr>' for r in overpriced_table)}
</table></div>
</div>
</div>

<div class="grid2">
<div class="section">
<h2>The Metro Premium</h2>
<div class="chart-container"><canvas id="metroChart" height="300"></canvas></div>
</div>
<div class="section">
<h2>The School Rating Tax</h2>
<div class="chart-container"><canvas id="schoolChart" height="300"></canvas></div>
</div>
</div>

<div class="section">
<h2>Crime vs Price</h2>
<div class="chart-container"><canvas id="crimeChart" height="350"></canvas></div>
</div>

<div class="section">
<h2>Smart Buyer Top 20 Deals</h2>
<div style="overflow-x:auto"><table>
<tr><th>#</th><th>ID</th><th>Neighborhood</th><th>Type</th><th>Price</th><th>Gap%</th><th>1yr Appr</th><th>School</th><th>Crime</th><th>Score</th></tr>
{"".join(f'<tr><td>{r["rank"]}</td><td>{r["id"]}</td><td>{r["hood"]}</td><td>{r["type"]}</td><td>${r["price"]:,}</td><td class="{"negative" if r["gap"]<0 else "positive"}">{r["gap"]:+.1f}%</td><td class="positive">{r["appr"]:+.1f}%</td><td>{r["school"]}</td><td>{r["crime"]:.0f}</td><td><b>{r["score"]}</b></td></tr>' for r in deals_table)}
</table></div>
</div>

<div class="section">
<h2>Investment Board</h2>
<div class="inv-grid">
{"".join(f'''<div class="inv-card {'buy' if r['rec']=='BUY NOW' else 'gem' if r['rec']=='HIDDEN GEM' else 'premium' if 'PREMIUM' in r['rec'] else 'risk' if 'OVERPRICED' in r['rec'] else 'avoid' if r['rec']=='AVOID' else 'hold'}">
<div class="rec" style="color:{rec_colors.get(r['rec'],'#888')}">{r['rec']}</div>
<div class="hood">{r['name']}</div>
<div class="stats">${r['ppsf']:.0f}/sqft &bull; Gap: {r['gap']:+.1f}% &bull; 1yr: {r['appr']:+.1f}%<br>Crime: {r['crime']:.0f} &bull; School: {r['school']} &bull; 3yr est: {r['ret3']:+.1f}%</div>
</div>''' for r in inv_data)}
</div>
</div>

<div class="section">
<h2>Key Insights</h2>
<div class="insight-grid">
{"".join(f'<div class="insight">{ins}</div>' for ins in insights)}
</div>
</div>

</div>

<script>
const recColorMap = {json.dumps(rec_colors)};
const hoodData = {json.dumps(hood_chart_data)};
const driverData = {json.dumps(driver_chart_data)};
const metroData = {json.dumps(metro_chart_data)};
const schoolData = {json.dumps(school_chart_data)};
const crimeData = {json.dumps(crime_scatter[:500])};

Chart.defaults.color = '#aaa';
Chart.defaults.borderColor = '#333';

// Neighborhood chart
new Chart(document.getElementById('hoodChart'), {{
  type: 'bar',
  data: {{
    labels: hoodData.map(d => d.name),
    datasets: [{{
      label: 'Avg $/sqft',
      data: hoodData.map(d => d.avg_ppsf),
      backgroundColor: hoodData.map(d => recColorMap[d.recommendation] || '#888'),
      borderColor: '#333', borderWidth: 1
    }}]
  }},
  options: {{
    indexAxis: 'y',
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ title: {{ display:true, text:'Avg Price per Sqft ($)' }}, grid:{{color:'#222'}} }}, y: {{ grid:{{display:false}} }} }}
  }}
}});

// Drivers chart
new Chart(document.getElementById('driverChart'), {{
  type: 'bar',
  data: {{
    labels: driverData.map(d => d.factor),
    datasets: [{{
      label: 'Dollar Impact',
      data: driverData.map(d => d.impact),
      backgroundColor: driverData.map(d => d.impact >= 0 ? '#00c853' : '#ff1744'),
      borderColor: '#333', borderWidth: 1
    }}]
  }},
  options: {{
    indexAxis: 'y',
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ title: {{ display:true, text:'Dollar Impact on Price ($)' }}, grid:{{color:'#222'}} }}, y: {{ grid:{{display:false}} }} }}
  }}
}});

// Metro chart
new Chart(document.getElementById('metroChart'), {{
  type: 'line',
  data: {{
    labels: metroData.map(d => d.dist + ' mi'),
    datasets: [{{
      label: '$/sqft',
      data: metroData.map(d => d.ppsf),
      borderColor: '#00e5ff', backgroundColor: 'rgba(0,229,255,0.1)',
      fill: true, tension: 0.3, pointRadius: 2
    }}]
  }},
  options: {{
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ title: {{ display:true, text:'Avg $/sqft' }}, grid:{{color:'#222'}} }}, x: {{ grid:{{color:'#222'}} }} }}
  }}
}});

// School chart
new Chart(document.getElementById('schoolChart'), {{
  type: 'bar',
  data: {{
    labels: schoolData.map(d => 'Rating ' + d.rating),
    datasets: [{{
      label: '$/sqft',
      data: schoolData.map(d => d.ppsf),
      backgroundColor: schoolData.map((d,i) => `hsl(${{30 + i*15}}, 80%, 55%)`),
      borderColor: '#333', borderWidth: 1
    }}]
  }},
  options: {{
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ title: {{ display:true, text:'Avg $/sqft' }}, grid:{{color:'#222'}} }}, x: {{ grid:{{display:false}} }} }}
  }}
}});

// Crime scatter
new Chart(document.getElementById('crimeChart'), {{
  type: 'scatter',
  data: {{
    datasets: [{{
      label: 'Crime vs Price',
      data: crimeData.map(d => ({{ x: d.crime_index, y: d.price_per_sqft }})),
      backgroundColor: 'rgba(255,107,107,0.4)', pointRadius: 3
    }}]
  }},
  options: {{
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ title: {{ display:true, text:'Crime Index' }}, grid:{{color:'#222'}} }},
      y: {{ title: {{ display:true, text:'Price per Sqft ($)' }}, grid:{{color:'#222'}} }}
    }}
  }}
}});
</script>
</body>
</html>"""

with open('output/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("  Saved dashboard.html")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "="*60)
print("  NEIGHBORHOOD PRICE DECODER — COMPLETE")
print("="*60)
print(f"  Most overpriced neighborhood: {most_overpriced_hood}")
print(f"  Best value neighborhood:      {best_value_hood}")
print(f"  #1 price driver:              {impact_df.iloc[0]['factor']} (${abs(impact_df.iloc[0]['dollar_impact']):,.0f})")
print(f"  Best deal in dataset:         #{int(top1_deal.listing_id)} in {top1_deal.neighborhood}")
print(f"                                ${top1_deal.listing_price:,.0f} ({top1_deal.price_gap_percent:+.1f}% gap, {top1_deal.predicted_1yr_appreciation:+.1f}% growth)")
print("="*60)
print("\nAll 8 output files saved to output/")
