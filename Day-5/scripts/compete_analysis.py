import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from pathlib import Path

# ── Setup ──────────────────────────────────────────────────────────────────────
dataset = 'netflix-data'
df = pd.read_csv(f'output/{dataset}/{dataset}_cleaned.csv')
out_dir = Path(f'output/{dataset}/compete')
out_dir.mkdir(parents=True, exist_ok=True)

COLORS = sns.color_palette('Set2', 20)
sns.set_style('whitegrid')

# ── Genre explosion ────────────────────────────────────────────────────────────
genre_col = 'listed_in'
df_genres = df.dropna(subset=[genre_col]).copy()
df_genres[genre_col] = df_genres[genre_col].str.split(',')
df_genres = df_genres.explode(genre_col)
df_genres[genre_col] = df_genres[genre_col].str.strip()

genre_counts = df_genres[genre_col].value_counts()
top20 = genre_counts.head(20)

# ── Chart 1: Genre Volume Ranking ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 9))
bars = ax.barh(top20.index[::-1], top20.values[::-1],
               color=COLORS[0], edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, top20.values[::-1]):
    ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
            f'{val:,}', va='center', fontsize=9, color='#333')
ax.set_xlabel('Number of Titles', fontsize=12)
ax.set_title('Top 20 Genres by Content Volume', fontsize=15, fontweight='bold', pad=15)
ax.set_xlim(0, top20.values.max() * 1.12)
plt.tight_layout()
plt.savefig(out_dir / 'chart_01_genre_ranking.png', dpi=150)
plt.close()
print('Chart 1 saved')

# ── Chart 2: Genre Growth Rate ─────────────────────────────────────────────────
year_min = int(df_genres['year_added'].dropna().min())
year_max = int(df_genres['year_added'].dropna().max())
total_years = max(year_max - year_min + 1, 1)
recent_cutoff = year_max - 2  # last 3 years

top15_genres = genre_counts.head(15).index.tolist()
growth_data = []
for g in top15_genres:
    g_df = df_genres[df_genres[genre_col] == g]
    rec = g_df[g_df['year_added'] >= recent_cutoff].shape[0]
    old = g_df[g_df['year_added'] < recent_cutoff].shape[0]
    old_years = max(total_years - 3, 1)
    old_avg = old / old_years
    rec_avg = rec / 3
    gr = (rec_avg - old_avg) / max(old_avg, 1) * 100
    growth_data.append({'genre': g, 'growth_rate': gr})

gdf = pd.DataFrame(growth_data).sort_values('growth_rate', ascending=True)

fig, ax = plt.subplots(figsize=(12, 7))
bar_colors = [COLORS[2] if v >= 0 else COLORS[3] for v in gdf['growth_rate']]
bars = ax.barh(gdf['genre'], gdf['growth_rate'], color=bar_colors, edgecolor='white')
ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
for bar, val in zip(bars, gdf['growth_rate']):
    x_pos = bar.get_width() + 1 if val >= 0 else bar.get_width() - 1
    ha = 'left' if val >= 0 else 'right'
    ax.text(x_pos, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
            va='center', ha=ha, fontsize=9)
ax.set_xlabel('Growth Rate % (recent 3yr avg vs prior avg)', fontsize=11)
ax.set_title('Genre Growth Rate — Recent 3 Years vs Historical Average', fontsize=14,
             fontweight='bold', pad=15)
pos_patch = mpatches.Patch(color=COLORS[2], label='Growing')
neg_patch = mpatches.Patch(color=COLORS[3], label='Declining')
ax.legend(handles=[pos_patch, neg_patch], loc='lower right')
plt.tight_layout()
plt.savefig(out_dir / 'chart_02_genre_growth.png', dpi=150)
plt.close()
print('Chart 2 saved')

# ── Chart 3: Genre x Content Type Heatmap ─────────────────────────────────────
type_genre = df_genres.groupby([genre_col, 'type']).size().unstack(fill_value=0)
type_genre = type_genre.loc[type_genre.sum(axis=1).nlargest(18).index]

fig, ax = plt.subplots(figsize=(10, 9))
sns.heatmap(type_genre, annot=True, fmt='d', cmap='YlOrRd',
            linewidths=0.5, linecolor='white', ax=ax,
            cbar_kws={'label': 'Number of Titles'})
ax.set_title('Genre x Content Type Matrix (Top 18 Genres)', fontsize=14,
             fontweight='bold', pad=15)
ax.set_xlabel('Content Type', fontsize=12)
ax.set_ylabel('Genre', fontsize=12)
plt.tight_layout()
plt.savefig(out_dir / 'chart_03_genre_type_matrix.png', dpi=150)
plt.close()
print('Chart 3 saved')

# ── Chart 4: Opportunity Matrix ────────────────────────────────────────────────
opp_data = []
for g in genre_counts.head(25).index:
    vol = genre_counts[g]
    g_df = df_genres[df_genres[genre_col] == g]
    rec = g_df[g_df['year_added'] >= recent_cutoff].shape[0]
    old = g_df[g_df['year_added'] < recent_cutoff].shape[0]
    old_avg = old / max(total_years - 3, 1)
    rec_avg = rec / 3
    gr = (rec_avg - old_avg) / max(old_avg, 1) * 100
    opp_data.append({'genre': g, 'volume': vol, 'growth_rate': gr})

odf = pd.DataFrame(opp_data)
med_vol = odf['volume'].median()
med_grow = odf['growth_rate'].median()

fig, ax = plt.subplots(figsize=(13, 9))
sc = ax.scatter(odf['volume'], odf['growth_rate'],
                s=odf['volume']/10 + 60, alpha=0.75,
                c=odf['growth_rate'], cmap='RdYlGn',
                edgecolors='grey', linewidth=0.5)
ax.axvline(med_vol, color='grey', linestyle='--', linewidth=1)
ax.axhline(med_grow, color='grey', linestyle='--', linewidth=1)

for _, row in odf.iterrows():
    ax.annotate(row['genre'], (row['volume'], row['growth_rate']),
                fontsize=7.5, ha='center', va='bottom',
                xytext=(0, 6), textcoords='offset points')

xlim = ax.get_xlim()
ylim = ax.get_ylim()
x_lo = xlim[0] + (xlim[1]-xlim[0])*0.02
x_hi = xlim[1] - (xlim[1]-xlim[0])*0.02
y_hi = ylim[1] - (ylim[1]-ylim[0])*0.05
y_lo = ylim[0] + (ylim[1]-ylim[0])*0.05

ax.text(x_hi, y_hi, 'STARS', fontsize=11, color='green',
        fontweight='bold', ha='right', alpha=0.7)
ax.text(x_hi, y_lo, 'CASH COWS', fontsize=11, color='goldenrod',
        fontweight='bold', ha='right', alpha=0.7)
ax.text(x_lo, y_hi, 'RISING STARS', fontsize=11, color='steelblue',
        fontweight='bold', alpha=0.7)
ax.text(x_lo, y_lo, 'NICHE', fontsize=11, color='#888',
        fontweight='bold', alpha=0.7)

plt.colorbar(sc, ax=ax, label='Growth Rate %')
ax.set_xlabel('Content Volume (# titles)', fontsize=12)
ax.set_ylabel('Growth Rate % (recent 3yr vs historical avg)', fontsize=12)
ax.set_title('Genre Opportunity Matrix', fontsize=15, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(out_dir / 'chart_04_opportunity_matrix.png', dpi=150)
plt.close()
print('Chart 4 saved')

# ── Chart 5: Rating Distribution by Top Genres ────────────────────────────────
top8 = genre_counts.head(8).index.tolist()
df_top8 = df_genres[df_genres[genre_col].isin(top8)]

all_ratings = df_top8['rating'].dropna().unique().tolist()
rating_order_pref = ['G','PG','PG-13','R','NC-17','TV-Y','TV-Y7','TV-Y7-FV',
                     'TV-G','TV-PG','TV-14','TV-MA']
rating_order = [r for r in rating_order_pref if r in all_ratings]
remaining = [r for r in all_ratings if r not in rating_order]
rating_order = rating_order + remaining

pivot = df_top8.groupby([genre_col, 'rating']).size().unstack(fill_value=0)
pivot = pivot[[c for c in rating_order if c in pivot.columns]]

fig, ax = plt.subplots(figsize=(14, 7))
pivot.plot(kind='bar', ax=ax, colormap='tab20', edgecolor='white', width=0.75)
ax.set_xlabel('Genre', fontsize=12)
ax.set_ylabel('Number of Titles', fontsize=12)
ax.set_title('Rating Distribution by Top 8 Genres', fontsize=14,
             fontweight='bold', pad=15)
ax.legend(title='Rating', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=9)
plt.xticks(rotation=35, ha='right')
plt.tight_layout()
plt.savefig(out_dir / 'chart_05_rating_by_genre.png', dpi=150)
plt.close()
print('Chart 5 saved')

# ── Summary stats ──────────────────────────────────────────────────────────────
print()
print('=== SUMMARY STATS ===')
print('Top 10 genres:')
print(genre_counts.head(10).to_string())
print()
print('Opportunity data (sorted by growth rate):')
print(odf.sort_values('growth_rate', ascending=False).to_string())
print()
print('Total titles:', len(df))
print('Movies:', (df['type']=='Movie').sum())
print('TV Shows:', (df['type']=='TV Show').sum())
print()
print('Top ratings:')
print(df['rating'].value_counts().head(8).to_string())
