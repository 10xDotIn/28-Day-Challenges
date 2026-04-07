import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

OUT = Path('output')
df = pd.read_csv('data/pricing_data.csv')
buyers = df[df['converted'] == 1]

SHORT = {
    'charm_pricing': 'Charm', 'round_pricing': 'Round', 'anchor_high': 'Anchor High',
    'anchor_low': 'Anchor Low', 'decoy_pricing': 'Decoy', 'bundle_pricing': 'Bundle',
    'urgency_pricing': 'Urgency', 'prestige_pricing': 'Prestige',
    'free_shipping_threshold': 'Free Ship', 'odd_specific_pricing': 'Odd Specific',
}

DARK_BG = '#0f0f0f'
CARD_BG = '#1a1a2e'
GRID = '#2a2a3e'
WHITE = '#e0e0e0'
GREEN = '#00e676'
RED = '#ff5252'
CYAN = '#00e5ff'
YELLOW = '#ffd600'
ORANGE = '#ff9100'
PURPLE = '#bb86fc'

# ── Compute regret metrics per strategy ──
regret = buyers.groupby('pricing_strategy').agg(
    total_buyers=('converted', 'count'),
    return_count=('returned', 'sum'),
    return_rate=('returned', 'mean'),
    avg_satisfaction=('satisfaction_rating', 'mean'),
    total_revenue=('revenue', 'sum'),
    returned_revenue=('revenue', lambda x: x[buyers.loc[x.index, 'returned'] == 1].sum()),
    avg_revenue_per_buyer=('revenue', 'mean'),
).reset_index()

conv = df.groupby('pricing_strategy')['converted'].mean().reset_index().rename(columns={'converted': 'conv_rate'})
regret = regret.merge(conv, on='pricing_strategy')
regret['net_revenue'] = regret['total_revenue'] - regret['returned_revenue']
regret['revenue_lost_pct'] = regret['returned_revenue'] / regret['total_revenue'] * 100
regret['regret_score'] = regret['conv_rate'] * regret['return_rate']  # high conv + high return = regret
regret = regret.sort_values('regret_score', ascending=False)
regret['short'] = regret['pricing_strategy'].map(SHORT)

# ── Figure: 4-panel regret deep-dive ──
fig = plt.figure(figsize=(20, 22), facecolor=DARK_BG)
fig.suptitle('The Cost of Regret — When Conversion Backfires', fontsize=24, fontweight='bold',
             color=WHITE, y=0.97)
fig.text(0.5, 0.955, 'Strategies that make people buy... then wish they hadn\'t',
         ha='center', fontsize=13, color='#888', style='italic')

# ── Panel 1: Regret Score (conv_rate x return_rate) ──
ax1 = fig.add_subplot(3, 2, (1, 2))
ax1.set_facecolor(CARD_BG)
d = regret.sort_values('regret_score', ascending=True)
# Color: red for high regret, green for low
max_rs = d['regret_score'].max()
colors = [plt.cm.RdYlGn_r(v / max_rs * 0.8 + 0.1) for v in d['regret_score']]
bars = ax1.barh(d['short'], d['regret_score'] * 100, color=colors, edgecolor='none', height=0.6)
for bar, val, ret, cv in zip(bars, d['regret_score'], d['return_rate'], d['conv_rate']):
    ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             f'{val*100:.1f}  (Conv {cv:.0%} x Ret {ret:.0%})',
             va='center', fontsize=10, color=WHITE)
ax1.set_xlabel('Regret Score (Conversion Rate x Return Rate)', fontsize=12, color=WHITE)
ax1.set_title('Regret Score — Who Converts but Causes Buyer Remorse?', fontsize=15,
              fontweight='bold', color=CYAN, pad=12)
ax1.set_xlim(0, d['regret_score'].max() * 100 + 8)
ax1.grid(axis='x', alpha=0.15, color=GRID)
ax1.tick_params(colors=WHITE)
for spine in ax1.spines.values(): spine.set_color(GRID)

# ── Panel 2: Revenue Lost to Returns (Rs.) ──
ax2 = fig.add_subplot(3, 2, 3)
ax2.set_facecolor(CARD_BG)
d2 = regret.sort_values('returned_revenue', ascending=True)
colors2 = [RED if v > regret['returned_revenue'].median() else ORANGE for v in d2['returned_revenue']]
bars2 = ax2.barh(d2['short'], d2['returned_revenue'], color=colors2, edgecolor='none', height=0.6)
for bar, val in zip(bars2, d2['returned_revenue']):
    if val > 0:
        ax2.text(bar.get_width() + 1000, bar.get_y() + bar.get_height()/2,
                 f'Rs.{val:,.0f}', va='center', fontsize=9, color=WHITE)
ax2.set_xlabel('Revenue Lost to Returns (Rs.)', fontsize=11, color=WHITE)
ax2.set_title('Revenue Destroyed by Returns', fontsize=14, fontweight='bold', color=RED, pad=10)
ax2.grid(axis='x', alpha=0.15, color=GRID)
ax2.tick_params(colors=WHITE)
for spine in ax2.spines.values(): spine.set_color(GRID)

# ── Panel 3: % of Revenue Lost ──
ax3 = fig.add_subplot(3, 2, 4)
ax3.set_facecolor(CARD_BG)
d3 = regret.sort_values('revenue_lost_pct', ascending=True)
colors3 = [RED if v > 15 else (YELLOW if v > 8 else GREEN) for v in d3['revenue_lost_pct']]
bars3 = ax3.barh(d3['short'], d3['revenue_lost_pct'], color=colors3, edgecolor='none', height=0.6)
for bar, val in zip(bars3, d3['revenue_lost_pct']):
    ax3.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}%', va='center', fontsize=10, color=WHITE, fontweight='bold')
ax3.set_xlabel('% of Gross Revenue Lost to Returns', fontsize=11, color=WHITE)
ax3.set_title('Revenue Leak Rate — % Lost per Strategy', fontsize=14, fontweight='bold', color=ORANGE, pad=10)
ax3.grid(axis='x', alpha=0.15, color=GRID)
ax3.tick_params(colors=WHITE)
for spine in ax3.spines.values(): spine.set_color(GRID)

# ── Panel 4: Satisfaction of Returners vs Non-Returners ──
ax4 = fig.add_subplot(3, 2, 5)
ax4.set_facecolor(CARD_BG)
sat_ret = buyers[buyers['returned'] == 1].groupby('pricing_strategy')['satisfaction_rating'].mean()
sat_kept = buyers[buyers['returned'] == 0].groupby('pricing_strategy')['satisfaction_rating'].mean()
d4 = pd.DataFrame({'returned_sat': sat_ret, 'kept_sat': sat_kept}).reset_index()
d4['short'] = d4['pricing_strategy'].map(SHORT)
d4['sat_gap'] = d4['kept_sat'] - d4['returned_sat']
d4 = d4.sort_values('sat_gap', ascending=True)

x = np.arange(len(d4))
w = 0.35
ax4.barh(x - w/2, d4['kept_sat'], w, label='Kept Purchase', color=GREEN, edgecolor='none')
ax4.barh(x + w/2, d4['returned_sat'], w, label='Returned', color=RED, edgecolor='none')
ax4.set_yticks(x)
ax4.set_yticklabels(d4['short'])
ax4.set_xlabel('Avg Satisfaction Rating (1-5)', fontsize=11, color=WHITE)
ax4.set_title('Satisfaction: Kept vs Returned Purchases', fontsize=14, fontweight='bold', color=PURPLE, pad=10)
ax4.legend(loc='lower right', framealpha=0.3, fontsize=9)
ax4.grid(axis='x', alpha=0.15, color=GRID)
ax4.tick_params(colors=WHITE)
for spine in ax4.spines.values(): spine.set_color(GRID)

# ── Panel 5: Net vs Gross Revenue comparison ──
ax5 = fig.add_subplot(3, 2, 6)
ax5.set_facecolor(CARD_BG)
d5 = regret.sort_values('total_revenue', ascending=True)
x5 = np.arange(len(d5))
w5 = 0.35
ax5.barh(x5 - w5/2, d5['total_revenue'], w5, label='Gross Revenue', color=CYAN, alpha=0.7, edgecolor='none')
ax5.barh(x5 + w5/2, d5['net_revenue'], w5, label='Net Revenue (after returns)', color=GREEN, edgecolor='none')
# Show the gap
for i, (_, row) in enumerate(d5.iterrows()):
    gap = row['total_revenue'] - row['net_revenue']
    if gap > 5000:
        ax5.text(row['total_revenue'] + 2000, i - w5/2, f'-Rs.{gap:,.0f}',
                 va='center', fontsize=8, color=RED, fontweight='bold')
ax5.set_yticks(x5)
ax5.set_yticklabels(d5['short'])
ax5.set_xlabel('Revenue (Rs.)', fontsize=11, color=WHITE)
ax5.set_title('Gross vs Net Revenue — The Real Picture', fontsize=14, fontweight='bold', color=GREEN, pad=10)
ax5.legend(loc='lower right', framealpha=0.3, fontsize=9)
ax5.grid(axis='x', alpha=0.15, color=GRID)
ax5.tick_params(colors=WHITE)
for spine in ax5.spines.values(): spine.set_color(GRID)

# ── Bottom summary box ──
top3_regret = regret.head(3)
total_lost = regret['returned_revenue'].sum()

summary = (
    f"WORST OFFENDERS:  "
    f"1) {top3_regret.iloc[0]['short']} — {top3_regret.iloc[0]['return_rate']:.0%} returns, Rs.{top3_regret.iloc[0]['returned_revenue']:,.0f} lost  |  "
    f"2) {top3_regret.iloc[1]['short']} — {top3_regret.iloc[1]['return_rate']:.0%} returns, Rs.{top3_regret.iloc[1]['returned_revenue']:,.0f} lost  |  "
    f"3) {top3_regret.iloc[2]['short']} — {top3_regret.iloc[2]['return_rate']:.0%} returns, Rs.{top3_regret.iloc[2]['returned_revenue']:,.0f} lost\n"
    f"TOTAL REVENUE DESTROYED BY RETURNS: Rs.{total_lost:,.0f}  |  "
    f"Urgency alone accounts for Rs.{top3_regret.iloc[0]['returned_revenue']:,.0f} ({top3_regret.iloc[0]['returned_revenue']/total_lost:.0%} of all return losses)"
)

fig.text(0.5, 0.02, summary, ha='center', fontsize=11, color=WHITE,
         fontweight='bold', style='italic',
         bbox=dict(boxstyle='round,pad=0.8', facecolor=CARD_BG, edgecolor=RED, linewidth=2))

plt.subplots_adjust(top=0.93, bottom=0.08, hspace=0.35, wspace=0.28, left=0.1, right=0.95)
fig.savefig(OUT / 'regret_cost_analysis.png', dpi=150, bbox_inches='tight', facecolor=DARK_BG)
plt.close()
print("Saved: output/regret_cost_analysis.png")
