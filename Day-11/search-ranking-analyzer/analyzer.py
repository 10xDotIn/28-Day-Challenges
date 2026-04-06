import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from io import BytesIO
import base64
import os
import warnings
warnings.filterwarnings('ignore')

# ── Setup ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#1a1a2e',
    'axes.facecolor': '#16213e',
    'axes.edgecolor': '#e94560',
    'axes.labelcolor': '#eee',
    'text.color': '#eee',
    'xtick.color': '#ccc',
    'ytick.color': '#ccc',
    'grid.color': '#333',
    'font.size': 12,
    'figure.dpi': 150,
})

os.makedirs('output', exist_ok=True)
df = pd.read_csv('data/search_rankings.csv')
print(f"Loaded {len(df)} rows, {df['query'].nunique()} queries, {df['product'].nunique()} products")

# Derived metrics
df['ctr'] = df['clicks'] / df['impressions']
df['conversion_rate'] = df['purchases'] / df['clicks'].replace(0, np.nan)
df['add_to_cart_rate'] = df['add_to_cart'] / df['clicks'].replace(0, np.nan)

# ══════════════════════════════════════════════════════════════════════════════
# 1. Position Bias Analysis
# ══════════════════════════════════════════════════════════════════════════════
pos_stats = df.groupby('position').agg(
    avg_ctr=('ctr', 'mean'),
    total_clicks=('clicks', 'sum'),
    total_impressions=('impressions', 'sum'),
    avg_conv=('conversion_rate', 'mean'),
).reset_index()
pos_stats['overall_ctr'] = pos_stats['total_clicks'] / pos_stats['total_impressions']

pos1_ctr = pos_stats.loc[pos_stats['position']==1, 'avg_ctr'].values[0]
pos5_ctr = pos_stats.loc[pos_stats['position']==5, 'avg_ctr'].values[0]
pos10_ctr = pos_stats.loc[pos_stats['position']==10, 'avg_ctr'].values[0]
pos1_vs_5 = pos1_ctr / pos5_ctr
pos1_vs_10 = pos1_ctr / pos10_ctr

# Position bias chart
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(pos_stats['position'], pos_stats['avg_ctr']*100, 'o-', color='#e94560', linewidth=3, markersize=10)
ax.fill_between(pos_stats['position'], pos_stats['avg_ctr']*100, alpha=0.2, color='#e94560')
ax.set_xlabel('Search Result Position', fontsize=14)
ax.set_ylabel('Average CTR (%)', fontsize=14)
ax.set_title('Position Bias: Click-Through Rate by Position', fontsize=16, fontweight='bold')
ax.set_xticks(range(1, 11))
ax.annotate(f'Pos 1: {pos1_ctr*100:.1f}%', xy=(1, pos1_ctr*100), xytext=(2.5, pos1_ctr*100+1),
            arrowprops=dict(arrowstyle='->', color='#00d2ff'), fontsize=12, color='#00d2ff', fontweight='bold')
ax.annotate(f'Pos 10: {pos10_ctr*100:.1f}%', xy=(10, pos10_ctr*100), xytext=(7.5, pos10_ctr*100+2),
            arrowprops=dict(arrowstyle='->', color='#ffd700'), fontsize=12, color='#ffd700', fontweight='bold')
ax.annotate(f'Position 1 gets {pos1_vs_5:.1f}x more clicks than Position 5',
            xy=(5, pos5_ctr*100), xytext=(4, pos1_ctr*100*0.6),
            fontsize=11, color='#fff', fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#e94560', alpha=0.7))
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/position_bias.png', bbox_inches='tight')
plt.close()
print("✓ position_bias.png")

# ══════════════════════════════════════════════════════════════════════════════
# 2. Hidden Gold Products
# ══════════════════════════════════════════════════════════════════════════════
prod_stats = df.groupby(['query', 'product']).agg(
    total_impressions=('impressions', 'sum'),
    total_clicks=('clicks', 'sum'),
    total_purchases=('purchases', 'sum'),
    total_revenue=('revenue', 'sum'),
    total_add_to_cart=('add_to_cart', 'sum'),
    avg_position=('position', 'mean'),
    avg_rating=('rating', 'mean'),
    avg_price=('price', 'mean'),
).reset_index()

prod_stats['ctr'] = prod_stats['total_clicks'] / prod_stats['total_impressions']
prod_stats['conv_rate'] = prod_stats['total_purchases'] / prod_stats['total_clicks'].replace(0, np.nan)
prod_stats['atc_rate'] = prod_stats['total_add_to_cart'] / prod_stats['total_clicks'].replace(0, np.nan)
prod_stats['rev_per_click'] = prod_stats['total_revenue'] / prod_stats['total_clicks'].replace(0, np.nan)

# Hidden gold: low position (high number) + high conversion
median_position = prod_stats['avg_position'].median()
median_conv = prod_stats['conv_rate'].median()
hidden_gold = prod_stats[
    (prod_stats['avg_position'] > 5) &
    (prod_stats['conv_rate'] > median_conv) &
    (prod_stats['total_clicks'] > 10)
].copy()
hidden_gold = hidden_gold.sort_values('conv_rate', ascending=False)

# Estimate revenue if promoted to position 1-3
# Use the CTR ratio: if a product moves from pos X to pos 1, its impressions ~= pos1 impressions
# and its clicks increase proportionally
pos1_avg_impressions = df[df['position'] == 1]['impressions'].mean()
for idx, row in hidden_gold.iterrows():
    current_avg_pos = row['avg_position']
    current_pos_ctr = pos_stats.loc[pos_stats['position'] == round(current_avg_pos), 'avg_ctr'].values
    if len(current_pos_ctr) == 0:
        current_pos_ctr = pos_stats['avg_ctr'].iloc[int(current_avg_pos)-1]
    else:
        current_pos_ctr = current_pos_ctr[0]
    ctr_boost = pos1_ctr / max(current_pos_ctr, 0.001)
    estimated_new_clicks = row['total_clicks'] * ctr_boost
    estimated_new_revenue = estimated_new_clicks * row['rev_per_click'] if not np.isnan(row['rev_per_click']) else 0
    hidden_gold.loc[idx, 'estimated_revenue_if_promoted'] = estimated_new_revenue
    hidden_gold.loc[idx, 'revenue_uplift'] = estimated_new_revenue - row['total_revenue']

hidden_gold = hidden_gold.sort_values('revenue_uplift', ascending=False).head(15)
total_hidden_gold_uplift = hidden_gold['revenue_uplift'].sum()

# Hidden gold chart
fig, ax = plt.subplots(figsize=(12, 8))
scatter_data = prod_stats.dropna(subset=['conv_rate']).copy()
colors = ['#00ff88' if cr > median_conv else '#ff4444' for cr in scatter_data['conv_rate']]
sizes = np.clip(scatter_data['total_revenue'] / scatter_data['total_revenue'].max() * 500, 20, 500)
ax.scatter(scatter_data['total_impressions'], scatter_data['conv_rate']*100,
           c=colors, s=sizes, alpha=0.6, edgecolors='white', linewidths=0.5)

# Label top 5 hidden gems
top5_gold = hidden_gold.head(5)
for _, row in top5_gold.iterrows():
    ax.annotate(f"{row['product']}\n({row['query'][:15]}..)",
                xy=(row['total_impressions'], row['conv_rate']*100),
                fontsize=8, color='#00ff88', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a1a2e', alpha=0.8))

ax.set_xlabel('Total Impressions', fontsize=14)
ax.set_ylabel('Conversion Rate (%)', fontsize=14)
ax.set_title('Hidden Gold: Low Impressions but High Conversion', fontsize=16, fontweight='bold')
ax.axhline(y=median_conv*100, color='#ffd700', linestyle='--', alpha=0.5, label=f'Median Conv: {median_conv*100:.1f}%')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/hidden_gold.png', bbox_inches='tight')
plt.close()
print("✓ hidden_gold.png")

# ══════════════════════════════════════════════════════════════════════════════
# 3. Fake Winners (Clickbait Products)
# ══════════════════════════════════════════════════════════════════════════════
prod_stats_valid = prod_stats.dropna(subset=['conv_rate', 'ctr']).copy()
median_ctr = prod_stats_valid['ctr'].median()
fake_winners = prod_stats_valid[
    (prod_stats_valid['ctr'] > median_ctr) &
    (prod_stats_valid['conv_rate'] < median_conv) &
    (prod_stats_valid['total_clicks'] > 10)
].copy()
fake_winners['ctr_conv_gap'] = fake_winners['ctr'] - fake_winners['conv_rate']
fake_winners = fake_winners.sort_values('ctr_conv_gap', ascending=False).head(15)

# Fake winners chart
fig, ax = plt.subplots(figsize=(12, 8))
colors_fw = ['#ff4444' if (row['ctr'] > median_ctr and row['conv_rate'] < median_conv) else '#888'
             for _, row in prod_stats_valid.iterrows()]
sizes_fw = np.clip(prod_stats_valid['total_impressions'] / prod_stats_valid['total_impressions'].max() * 500, 20, 500)
ax.scatter(prod_stats_valid['ctr']*100, prod_stats_valid['conv_rate']*100,
           c=colors_fw, s=sizes_fw, alpha=0.6, edgecolors='white', linewidths=0.5)

# Highlight quadrant
ax.axvline(x=median_ctr*100, color='#ffd700', linestyle='--', alpha=0.5)
ax.axhline(y=median_conv*100, color='#ffd700', linestyle='--', alpha=0.5)
ax.fill_between([median_ctr*100, prod_stats_valid['ctr'].max()*100+1], 0, median_conv*100,
                alpha=0.1, color='#ff4444')
ax.text(prod_stats_valid['ctr'].max()*100*0.8, median_conv*100*0.3, 'CLICKBAIT\nZONE',
        fontsize=16, color='#ff4444', fontweight='bold', alpha=0.7, ha='center')

top5_fake = fake_winners.head(5)
for _, row in top5_fake.iterrows():
    ax.annotate(f"{row['product']}\n({row['query'][:15]}..)",
                xy=(row['ctr']*100, row['conv_rate']*100),
                fontsize=8, color='#ff6666', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a1a2e', alpha=0.8))

ax.set_xlabel('Click-Through Rate (%)', fontsize=14)
ax.set_ylabel('Conversion Rate (%)', fontsize=14)
ax.set_title('Fake Winners: High CTR but Low Conversion (Clickbait)', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/fake_winners.png', bbox_inches='tight')
plt.close()
print("✓ fake_winners.png")

# ══════════════════════════════════════════════════════════════════════════════
# 4. Revenue Impact Analysis
# ══════════════════════════════════════════════════════════════════════════════
query_revenue = df.groupby('query').agg(
    current_revenue=('revenue', 'sum'),
    total_clicks=('clicks', 'sum'),
    total_impressions=('impressions', 'sum'),
    total_purchases=('purchases', 'sum'),
).reset_index()

# Potential revenue: rank by conversion rate instead of current position
potential_revenues = []
for query in df['query'].unique():
    qdf = prod_stats[prod_stats['query'] == query].copy()
    qdf = qdf.sort_values('conv_rate', ascending=False).reset_index(drop=True)
    # Assign new positions 1-10
    potential_rev = 0
    for new_pos, (_, row) in enumerate(qdf.iterrows(), 1):
        # Estimate: give this product the CTR of its new position
        new_pos_ctr = pos_stats.loc[pos_stats['position'] == new_pos, 'avg_ctr'].values[0]
        estimated_clicks = row['total_impressions'] * new_pos_ctr
        rev_per_click_val = row['rev_per_click'] if not np.isnan(row['rev_per_click']) else 0
        potential_rev += estimated_clicks * rev_per_click_val
    potential_revenues.append({'query': query, 'potential_revenue': potential_rev})

potential_df = pd.DataFrame(potential_revenues)
query_revenue = query_revenue.merge(potential_df, on='query')
query_revenue['revenue_gap'] = query_revenue['potential_revenue'] - query_revenue['current_revenue']
total_revenue_gap = query_revenue['revenue_gap'].sum()
total_current_revenue = query_revenue['current_revenue'].sum()

# Revenue gap chart
fig, ax = plt.subplots(figsize=(14, 8))
qr_sorted = query_revenue.sort_values('revenue_gap', ascending=True)
y_pos = range(len(qr_sorted))
bars1 = ax.barh(y_pos, qr_sorted['current_revenue'], height=0.4, color='#e94560', label='Current Revenue')
bars2 = ax.barh([y + 0.4 for y in y_pos], qr_sorted['potential_revenue'], height=0.4, color='#00d2ff', label='Potential Revenue')
ax.set_yticks([y + 0.2 for y in y_pos])
ax.set_yticklabels(qr_sorted['query'], fontsize=9)
ax.set_xlabel('Revenue ($)', fontsize=14)
ax.set_title(f'Revenue Gap: Current vs Potential (Total Gap: ${total_revenue_gap:,.0f})', fontsize=16, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('output/revenue_gap.png', bbox_inches='tight')
plt.close()
print("✓ revenue_gap.png")

# ══════════════════════════════════════════════════════════════════════════════
# 5. Search Funnel Analysis
# ══════════════════════════════════════════════════════════════════════════════
funnel_total = {
    'Impressions': df['impressions'].sum(),
    'Clicks': df['clicks'].sum(),
    'Add to Cart': df['add_to_cart'].sum(),
    'Purchases': df['purchases'].sum(),
}
funnel_stages = list(funnel_total.keys())
funnel_values = list(funnel_total.values())
funnel_dropoffs = []
for i in range(1, len(funnel_values)):
    dropoff = (1 - funnel_values[i] / funnel_values[i-1]) * 100
    funnel_dropoffs.append(dropoff)

# Per-query funnel
query_funnel = df.groupby('query').agg(
    impressions=('impressions', 'sum'),
    clicks=('clicks', 'sum'),
    add_to_cart=('add_to_cart', 'sum'),
    purchases=('purchases', 'sum'),
).reset_index()
query_funnel['ctr'] = query_funnel['clicks'] / query_funnel['impressions']
query_funnel['click_to_atc'] = query_funnel['add_to_cart'] / query_funnel['clicks']
query_funnel['atc_to_purchase'] = query_funnel['purchases'] / query_funnel['add_to_cart']
query_funnel['overall_conv'] = query_funnel['purchases'] / query_funnel['impressions']
worst_funnel_query = query_funnel.sort_values('overall_conv').iloc[0]['query']

# Funnel chart
fig, ax = plt.subplots(figsize=(10, 8))
colors_funnel = ['#e94560', '#ff6b6b', '#ffd700', '#00ff88']
max_width = 0.8
for i, (stage, value) in enumerate(zip(funnel_stages, funnel_values)):
    width = max_width * (value / funnel_values[0])
    left = (max_width - width) / 2
    bar = ax.barh(len(funnel_stages) - 1 - i, width, left=left, height=0.6,
                  color=colors_funnel[i], edgecolor='white', linewidth=2)
    ax.text(max_width/2, len(funnel_stages) - 1 - i,
            f'{stage}\n{value:,.0f}', ha='center', va='center',
            fontsize=13, fontweight='bold', color='white')
    if i > 0:
        ax.text(max_width + 0.02, len(funnel_stages) - 1 - i + 0.35,
                f'↓ {funnel_dropoffs[i-1]:.1f}% drop',
                fontsize=11, color='#ff6b6b', fontweight='bold')

ax.set_xlim(0, max_width + 0.25)
ax.set_ylim(-0.5, len(funnel_stages) - 0.5)
ax.axis('off')
ax.set_title('Search Funnel: Where Are Customers Dropping Off?', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('output/search_funnel.png', bbox_inches='tight')
plt.close()
print("✓ search_funnel.png")

# ══════════════════════════════════════════════════════════════════════════════
# 6. Ranking Recommendations
# ══════════════════════════════════════════════════════════════════════════════
recommendations = []
for query in df['query'].unique():
    qdf = prod_stats[prod_stats['query'] == query].copy()
    qdf['current_rank'] = qdf['avg_position'].rank().astype(int)
    # Smart rank: weighted by conversion rate + revenue per click
    qdf['smart_score'] = (
        qdf['conv_rate'].fillna(0) * 0.6 +
        (qdf['rev_per_click'].fillna(0) / qdf['rev_per_click'].fillna(0).max()) * 0.4
    )
    qdf['recommended_rank'] = qdf['smart_score'].rank(ascending=False).astype(int)
    qdf['rank_change'] = qdf['current_rank'] - qdf['recommended_rank']
    recommendations.append(qdf)

all_recs = pd.concat(recommendations, ignore_index=True)
movers_up = all_recs[all_recs['rank_change'] > 0].sort_values('rank_change', ascending=False)
movers_down = all_recs[all_recs['rank_change'] < 0].sort_values('rank_change')

# Ranking recommendations chart — top 5 queries
fig, axes = plt.subplots(1, 5, figsize=(24, 8), sharey=True)
top5_queries = query_revenue.sort_values('revenue_gap', ascending=False)['query'].head(5).tolist()

for idx, query in enumerate(top5_queries):
    ax = axes[idx]
    qrec = all_recs[all_recs['query'] == query].sort_values('current_rank')
    products = [p[:20] for p in qrec['product'].values]
    current = qrec['current_rank'].values
    recommended = qrec['recommended_rank'].values

    y_pos = range(len(products))
    ax.barh(y_pos, current, height=0.35, color='#e94560', alpha=0.7, label='Current')
    ax.barh([y + 0.35 for y in y_pos], recommended, height=0.35, color='#00ff88', alpha=0.7, label='Recommended')
    ax.set_yticks([y + 0.175 for y in y_pos])
    ax.set_yticklabels(products, fontsize=7)
    ax.set_title(query[:25], fontsize=10, fontweight='bold')
    ax.set_xlabel('Rank', fontsize=9)
    ax.invert_xaxis()

    for i, (c, r) in enumerate(zip(current, recommended)):
        change = int(c - r)
        if change > 0:
            ax.text(0.5, i + 0.175, f'↑{change}', color='#00ff88', fontsize=8, fontweight='bold', va='center')
        elif change < 0:
            ax.text(0.5, i + 0.175, f'↓{abs(change)}', color='#ff4444', fontsize=8, fontweight='bold', va='center')

    if idx == 0:
        ax.legend(fontsize=8)

fig.suptitle('Ranking Recommendations: Current vs Smart Ranking', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('output/ranking_recommendations.png', bbox_inches='tight')
plt.close()
print("✓ ranking_recommendations.png")

# ══════════════════════════════════════════════════════════════════════════════
# 7. Query Performance Comparison
# ══════════════════════════════════════════════════════════════════════════════
qp = query_funnel.merge(query_revenue[['query', 'current_revenue']], on='query')
qp = qp.sort_values('current_revenue', ascending=True)

fig, axes = plt.subplots(1, 3, figsize=(20, 8))

# CTR by query
axes[0].barh(range(len(qp)), qp['ctr']*100, color='#e94560')
axes[0].set_yticks(range(len(qp)))
axes[0].set_yticklabels(qp['query'], fontsize=9)
axes[0].set_xlabel('CTR (%)')
axes[0].set_title('CTR by Query', fontweight='bold')
axes[0].grid(True, alpha=0.3, axis='x')

# Conversion by query
axes[1].barh(range(len(qp)), qp['overall_conv']*100, color='#00d2ff')
axes[1].set_yticks(range(len(qp)))
axes[1].set_yticklabels(qp['query'], fontsize=9)
axes[1].set_xlabel('Conversion Rate (%)')
axes[1].set_title('Conversion Rate by Query', fontweight='bold')
axes[1].grid(True, alpha=0.3, axis='x')

# Revenue by query
axes[2].barh(range(len(qp)), qp['current_revenue'], color='#ffd700')
axes[2].set_yticks(range(len(qp)))
axes[2].set_yticklabels(qp['query'], fontsize=9)
axes[2].set_xlabel('Revenue ($)')
axes[2].set_title('Revenue by Query', fontweight='bold')
axes[2].grid(True, alpha=0.3, axis='x')

fig.suptitle('Query Performance Comparison (Sorted by Revenue)', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('output/query_performance.png', bbox_inches='tight')
plt.close()
print("✓ query_performance.png")

# ══════════════════════════════════════════════════════════════════════════════
# 8. Analysis Report (Markdown)
# ══════════════════════════════════════════════════════════════════════════════
top5_gold_list = hidden_gold.head(5)
top5_fake_list = fake_winners.head(5)
best_gold = hidden_gold.iloc[0] if len(hidden_gold) > 0 else None
best_fake = fake_winners.iloc[0] if len(fake_winners) > 0 else None
biggest_drop_stage = funnel_stages[1 + funnel_dropoffs.index(max(funnel_dropoffs))]

report = f"""# Search Ranking Analysis Report

## Executive Summary

The company is **leaving ${total_revenue_gap:,.0f} on the table** due to suboptimal product rankings across {df['query'].nunique()} search queries.

Current total revenue: **${total_current_revenue:,.0f}**
Potential revenue with smart ranking: **${total_current_revenue + total_revenue_gap:,.0f}**
Revenue uplift opportunity: **{(total_revenue_gap/total_current_revenue)*100:.1f}%**

---

## 1. Position Bias Findings

Search position dramatically impacts click behavior:

| Position | Average CTR |
|----------|------------|
| 1 | {pos1_ctr*100:.2f}% |
| 5 | {pos5_ctr*100:.2f}% |
| 10 | {pos10_ctr*100:.2f}% |

- **Position 1 gets {pos1_vs_5:.1f}x more clicks than Position 5**
- **Position 1 gets {pos1_vs_10:.1f}x more clicks than Position 10**
- This means products buried at lower positions never get a fair chance, regardless of quality.

---

## 2. Top 5 Hidden Gold Products

These products have HIGH conversion rates but are buried at LOW positions:

| Product | Query | Avg Position | Conv Rate | Current Revenue | Est. Revenue if Promoted | Uplift |
|---------|-------|-------------|-----------|----------------|-------------------------|--------|
"""

for _, row in top5_gold_list.iterrows():
    report += f"| {row['product']} | {row['query']} | {row['avg_position']:.1f} | {row['conv_rate']*100:.1f}% | ${row['total_revenue']:,.0f} | ${row['estimated_revenue_if_promoted']:,.0f} | +${row['revenue_uplift']:,.0f} |\n"

report += f"""
**Total revenue uplift from promoting hidden gems: ${total_hidden_gold_uplift:,.0f}**

---

## 3. Top 5 Fake Winners (Clickbait Products)

These products get HIGH clicks but LOW conversions — wasting valuable ranking space:

| Product | Query | CTR | Conv Rate | CTR-Conv Gap |
|---------|-------|-----|-----------|-------------|
"""

for _, row in top5_fake_list.iterrows():
    report += f"| {row['product']} | {row['query']} | {row['ctr']*100:.1f}% | {row['conv_rate']*100:.1f}% | {row['ctr_conv_gap']*100:.1f}% |\n"

report += f"""
---

## 4. Search Funnel Analysis

| Stage | Volume | Drop-off |
|-------|--------|----------|
| Impressions | {funnel_values[0]:,.0f} | — |
| Clicks | {funnel_values[1]:,.0f} | {funnel_dropoffs[0]:.1f}% |
| Add to Cart | {funnel_values[2]:,.0f} | {funnel_dropoffs[1]:.1f}% |
| Purchases | {funnel_values[3]:,.0f} | {funnel_dropoffs[2]:.1f}% |

- **Biggest drop-off: Impressions → Clicks ({funnel_dropoffs[0]:.1f}%)** — most users don't click at all
- **Worst performing query: "{worst_funnel_query}"**

---

## 5. Revenue Gap Per Query

| Query | Current Revenue | Potential Revenue | Gap |
|-------|----------------|-------------------|-----|
"""

for _, row in query_revenue.sort_values('revenue_gap', ascending=False).iterrows():
    report += f"| {row['query']} | ${row['current_revenue']:,.0f} | ${row['potential_revenue']:,.0f} | ${row['revenue_gap']:,.0f} |\n"

report += f"""
---

## 6. Smart Ranking Recommendations

Products that should move UP (currently underranked):
"""

for _, row in movers_up.head(10).iterrows():
    report += f"- **{row['product']}** ({row['query']}): Move UP {int(row['rank_change'])} positions (current: {int(row['current_rank'])}, recommended: {int(row['recommended_rank'])})\n"

report += f"""
Products that should move DOWN (currently overranked):
"""

for _, row in movers_down.head(10).iterrows():
    report += f"- **{row['product']}** ({row['query']}): Move DOWN {abs(int(row['rank_change']))} positions (current: {int(row['current_rank'])}, recommended: {int(row['recommended_rank'])})\n"

report += f"""
---

## 7. Five Actionable Business Recommendations

1. **Promote hidden gold products immediately** — Moving high-conversion products to top positions could unlock ${total_hidden_gold_uplift:,.0f} in additional revenue.

2. **Demote clickbait products** — Products with high CTR but low conversion are wasting premium positions. Replace them with products that actually sell.

3. **Implement conversion-weighted ranking** — Current rankings appear to be driven by click volume, not purchase behavior. A ranking algorithm that weights conversion rate (60%) and revenue-per-click (40%) would significantly outperform.

4. **Focus on the Impressions→Clicks stage** — The {funnel_dropoffs[0]:.1f}% drop-off from impressions to clicks suggests poor product thumbnails, titles, or pricing display. A/B test richer search result cards.

5. **Query-specific optimization** — Not all queries perform equally. Focus optimization efforts on the highest-gap queries first for maximum ROI.

---

## Final Verdict

**#1 change that would increase revenue most: Implement conversion-weighted ranking.**

Re-ranking products by conversion rate and revenue-per-click instead of current position/clicks would capture an estimated **${total_revenue_gap:,.0f}** in additional revenue — a **{(total_revenue_gap/total_current_revenue)*100:.1f}%** increase.

The #1 hidden gold product is **{best_gold['product'] if best_gold is not None else 'N/A'}** ({best_gold['query'] if best_gold is not None else 'N/A'}) with a {best_gold['conv_rate']*100:.1f}% conversion rate buried at position {best_gold['avg_position']:.1f}.

The #1 fake winner is **{best_fake['product'] if best_fake is not None else 'N/A'}** ({best_fake['query'] if best_fake is not None else 'N/A'}) with {best_fake['ctr']*100:.1f}% CTR but only {best_fake['conv_rate']*100:.1f}% conversion.
"""

with open('output/analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(report)
print("✓ analysis_report.md")

# ══════════════════════════════════════════════════════════════════════════════
# 9. Dashboard HTML
# ══════════════════════════════════════════════════════════════════════════════

def img_to_base64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

img_position = img_to_base64('output/position_bias.png')
img_hidden = img_to_base64('output/hidden_gold.png')
img_fake = img_to_base64('output/fake_winners.png')
img_revenue = img_to_base64('output/revenue_gap.png')
img_funnel = img_to_base64('output/search_funnel.png')
img_ranking = img_to_base64('output/ranking_recommendations.png')
img_query = img_to_base64('output/query_performance.png')

# Build hidden gold table rows
gold_rows = ""
for _, row in hidden_gold.head(10).iterrows():
    gold_rows += f"""<tr>
        <td>{row['product']}</td>
        <td>{row['query']}</td>
        <td>{row['avg_position']:.1f}</td>
        <td>{row['conv_rate']*100:.1f}%</td>
        <td>${row['total_revenue']:,.0f}</td>
        <td style="color:#00ff88;font-weight:bold">${row['estimated_revenue_if_promoted']:,.0f}</td>
        <td style="color:#00ff88;font-weight:bold">+${row['revenue_uplift']:,.0f}</td>
    </tr>"""

# Build fake winners table rows
fake_rows = ""
for _, row in fake_winners.head(10).iterrows():
    fake_rows += f"""<tr>
        <td>{row['product']}</td>
        <td>{row['query']}</td>
        <td>{row['ctr']*100:.1f}%</td>
        <td style="color:#ff4444">{row['conv_rate']*100:.1f}%</td>
        <td style="color:#ff4444;font-weight:bold">{row['ctr_conv_gap']*100:.1f}%</td>
    </tr>"""

# Smart ranking sections for top 3 queries
ranking_html = ""
for query in top5_queries[:3]:
    qrec = all_recs[all_recs['query'] == query].sort_values('recommended_rank')
    ranking_html += f'<div class="ranking-card"><h4>{query}</h4><table class="data-table"><tr><th>Product</th><th>Current</th><th>Recommended</th><th>Change</th></tr>'
    for _, row in qrec.iterrows():
        change = int(row['rank_change'])
        if change > 0:
            arrow = f'<span style="color:#00ff88">▲ {change}</span>'
        elif change < 0:
            arrow = f'<span style="color:#ff4444">▼ {abs(change)}</span>'
        else:
            arrow = '<span style="color:#888">—</span>'
        ranking_html += f'<tr><td>{row["product"][:30]}</td><td>{int(row["current_rank"])}</td><td>{int(row["recommended_rank"])}</td><td>{arrow}</td></tr>'
    ranking_html += '</table></div>'

# Insights
insights = [
    (f"${total_revenue_gap:,.0f}", "Revenue left on the table from suboptimal rankings"),
    (f"{pos1_vs_5:.1f}x", "Position 1 gets this many more clicks than Position 5"),
    (f"{funnel_dropoffs[0]:.1f}%", "of users never click — the biggest funnel drop-off"),
    (f"{hidden_gold.iloc[0]['conv_rate']*100:.1f}%", f"conversion rate for {hidden_gold.iloc[0]['product']} — buried at position {hidden_gold.iloc[0]['avg_position']:.0f}"),
    (f"{len(fake_winners)}", "clickbait products wasting premium ranking positions"),
]

insights_html = ""
for number, text in insights:
    insights_html += f'<div class="insight-card"><div class="insight-number">{number}</div><div class="insight-text">{text}</div></div>'

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Search Ranking Analyzer — Dashboard</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0f0f23; color: #e0e0e0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; line-height: 1.6; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
h1 {{ font-size: 2.5em; background: linear-gradient(135deg, #e94560, #00d2ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }}
h2 {{ color: #e94560; font-size: 1.6em; margin: 40px 0 20px; padding-bottom: 10px; border-bottom: 2px solid #e94560; }}
h3 {{ color: #00d2ff; margin: 20px 0 10px; }}
.subtitle {{ color: #888; font-size: 1.1em; margin-bottom: 30px; }}

/* Hero metrics */
.hero {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 30px 0; }}
.metric-card {{ background: linear-gradient(135deg, #1a1a3e, #16213e); border: 1px solid #333; border-radius: 12px; padding: 20px; text-align: center; }}
.metric-card.highlight {{ border-color: #e94560; background: linear-gradient(135deg, #2a1a2e, #1a1a3e); }}
.metric-value {{ font-size: 2em; font-weight: bold; color: #fff; }}
.metric-value.red {{ color: #e94560; }}
.metric-value.green {{ color: #00ff88; }}
.metric-value.blue {{ color: #00d2ff; }}
.metric-value.gold {{ color: #ffd700; }}
.metric-label {{ color: #888; font-size: 0.85em; margin-top: 5px; }}

/* Charts */
.chart-container {{ background: #1a1a2e; border-radius: 12px; padding: 20px; margin: 20px 0; border: 1px solid #333; }}
.chart-container img {{ width: 100%; border-radius: 8px; }}

/* Tables */
.data-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
.data-table th {{ background: #16213e; color: #00d2ff; padding: 12px; text-align: left; font-size: 0.9em; }}
.data-table td {{ padding: 10px 12px; border-bottom: 1px solid #222; font-size: 0.9em; }}
.data-table tr:hover {{ background: #1a1a3e; }}

/* Sections */
.section {{ margin: 40px 0; }}
.section.gold {{ border-left: 4px solid #00ff88; padding-left: 20px; }}
.section.danger {{ border-left: 4px solid #ff4444; padding-left: 20px; }}

/* Rankings */
.ranking-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
.ranking-card {{ background: #16213e; border-radius: 10px; padding: 15px; border: 1px solid #333; }}
.ranking-card h4 {{ color: #ffd700; margin-bottom: 10px; }}

/* Insights */
.insights-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }}
.insight-card {{ background: linear-gradient(135deg, #1a1a3e, #0f2027); border-radius: 12px; padding: 20px; border: 1px solid #e94560; }}
.insight-number {{ font-size: 2em; font-weight: bold; color: #e94560; }}
.insight-text {{ color: #ccc; font-size: 0.95em; margin-top: 5px; }}

/* Funnel */
.funnel-stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 15px 0; }}
.funnel-step {{ text-align: center; padding: 15px; border-radius: 8px; }}
</style>
</head>
<body>
<div class="container">

<h1>Search Ranking Analyzer</h1>
<p class="subtitle">E-Commerce Search Performance Dashboard — {df['query'].nunique()} queries, {df['product'].nunique()} products, {len(df):,} data points</p>

<!-- Hero Metrics -->
<div class="hero">
    <div class="metric-card">
        <div class="metric-value blue">{df['query'].nunique()}</div>
        <div class="metric-label">Queries Analyzed</div>
    </div>
    <div class="metric-card">
        <div class="metric-value blue">{df['product'].nunique()}</div>
        <div class="metric-label">Products Tracked</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{df['impressions'].sum():,.0f}</div>
        <div class="metric-label">Total Impressions</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{df['clicks'].sum():,.0f}</div>
        <div class="metric-label">Total Clicks</div>
    </div>
    <div class="metric-card">
        <div class="metric-value green">{df['purchases'].sum():,.0f}</div>
        <div class="metric-label">Total Purchases</div>
    </div>
    <div class="metric-card">
        <div class="metric-value gold">${total_current_revenue:,.0f}</div>
        <div class="metric-label">Total Revenue</div>
    </div>
    <div class="metric-card highlight">
        <div class="metric-value red">${total_revenue_gap:,.0f}</div>
        <div class="metric-label">Revenue Left on the Table</div>
    </div>
</div>

<!-- Position Bias -->
<div class="section">
    <h2>Position Bias Analysis</h2>
    <p>Position 1 gets <strong>{pos1_vs_5:.1f}x</strong> more clicks than Position 5 and <strong>{pos1_vs_10:.1f}x</strong> more than Position 10. The ranking position dominates click behavior regardless of product quality.</p>
    <div class="chart-container">
        <img src="data:image/png;base64,{img_position}" alt="Position Bias">
    </div>
</div>

<!-- Hidden Gold -->
<div class="section gold">
    <h2>Hidden Gold Products</h2>
    <p>These products have amazing conversion rates but are buried at low positions. Promoting them could unlock <strong style="color:#00ff88">${total_hidden_gold_uplift:,.0f}</strong> in additional revenue.</p>
    <div class="chart-container">
        <img src="data:image/png;base64,{img_hidden}" alt="Hidden Gold">
    </div>
    <table class="data-table">
        <tr><th>Product</th><th>Query</th><th>Avg Position</th><th>Conv Rate</th><th>Current Revenue</th><th>Est. Revenue if Promoted</th><th>Uplift</th></tr>
        {gold_rows}
    </table>
</div>

<!-- Fake Winners -->
<div class="section danger">
    <h2>Fake Winners (Clickbait Products)</h2>
    <p>These products attract clicks but don't convert — they're wasting premium ranking positions that should go to products that actually sell.</p>
    <div class="chart-container">
        <img src="data:image/png;base64,{img_fake}" alt="Fake Winners">
    </div>
    <table class="data-table">
        <tr><th>Product</th><th>Query</th><th>CTR</th><th>Conv Rate</th><th>CTR-Conv Gap</th></tr>
        {fake_rows}
    </table>
</div>

<!-- Revenue Impact -->
<div class="section">
    <h2>Revenue Impact Analysis</h2>
    <p>Total revenue gap across all queries: <strong style="color:#e94560">${total_revenue_gap:,.0f}</strong></p>
    <div class="chart-container">
        <img src="data:image/png;base64,{img_revenue}" alt="Revenue Gap">
    </div>
</div>

<!-- Search Funnel -->
<div class="section">
    <h2>Search Funnel Analysis</h2>
    <div class="funnel-stats">
        <div class="funnel-step" style="background:#e9456033">
            <div style="font-size:1.5em;font-weight:bold;color:#e94560">{funnel_values[0]:,.0f}</div>
            <div>Impressions</div>
        </div>
        <div class="funnel-step" style="background:#ff6b6b33">
            <div style="font-size:1.5em;font-weight:bold;color:#ff6b6b">{funnel_values[1]:,.0f}</div>
            <div>Clicks</div>
            <div style="color:#ff4444;font-size:0.8em">↓ {funnel_dropoffs[0]:.1f}% drop</div>
        </div>
        <div class="funnel-step" style="background:#ffd70033">
            <div style="font-size:1.5em;font-weight:bold;color:#ffd700">{funnel_values[2]:,.0f}</div>
            <div>Add to Cart</div>
            <div style="color:#ff4444;font-size:0.8em">↓ {funnel_dropoffs[1]:.1f}% drop</div>
        </div>
        <div class="funnel-step" style="background:#00ff8833">
            <div style="font-size:1.5em;font-weight:bold;color:#00ff88">{funnel_values[3]:,.0f}</div>
            <div>Purchases</div>
            <div style="color:#ff4444;font-size:0.8em">↓ {funnel_dropoffs[2]:.1f}% drop</div>
        </div>
    </div>
    <div class="chart-container">
        <img src="data:image/png;base64,{img_funnel}" alt="Search Funnel">
    </div>
</div>

<!-- Smart Ranking -->
<div class="section">
    <h2>Smart Ranking Recommendations</h2>
    <p>Current ranking vs conversion-weighted ranking for the top revenue-gap queries:</p>
    <div class="ranking-grid">
        {ranking_html}
    </div>
    <div class="chart-container">
        <img src="data:image/png;base64,{img_ranking}" alt="Ranking Recommendations">
    </div>
</div>

<!-- Query Performance -->
<div class="section">
    <h2>Query Performance Comparison</h2>
    <div class="chart-container">
        <img src="data:image/png;base64,{img_query}" alt="Query Performance">
    </div>
</div>

<!-- Key Insights -->
<div class="section">
    <h2>Key Insights</h2>
    <div class="insights-grid">
        {insights_html}
    </div>
</div>

<div style="text-align:center; padding:40px 0; color:#555;">
    <p>Search Ranking Analysis — Generated from {len(df):,} data points across {df['query'].nunique()} queries</p>
</div>

</div>
</body>
</html>"""

with open('output/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ dashboard.html")

# ══════════════════════════════════════════════════════════════════════════════
# Final Summary
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ANALYSIS COMPLETE — ALL 9 OUTPUT FILES GENERATED")
print("="*60)
print(f"\n💰 Total Revenue Gap: ${total_revenue_gap:,.0f}")
print(f"🏆 #1 Hidden Gold Product: {hidden_gold.iloc[0]['product']} ({hidden_gold.iloc[0]['query']}) — {hidden_gold.iloc[0]['conv_rate']*100:.1f}% conversion at position {hidden_gold.iloc[0]['avg_position']:.1f}")
print(f"🚫 #1 Fake Winner: {fake_winners.iloc[0]['product']} ({fake_winners.iloc[0]['query']}) — {fake_winners.iloc[0]['ctr']*100:.1f}% CTR but {fake_winners.iloc[0]['conv_rate']*100:.1f}% conversion")
print(f"\nFiles saved in output/:")
for f in ['dashboard.html', 'position_bias.png', 'hidden_gold.png', 'fake_winners.png',
          'revenue_gap.png', 'search_funnel.png', 'ranking_recommendations.png',
          'query_performance.png', 'analysis_report.md']:
    print(f"  ✓ {f}")
