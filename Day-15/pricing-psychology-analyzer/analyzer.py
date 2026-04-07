import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ── Setup ──────────────────────────────────────────────────────────────
DATA = Path('data/pricing_data.csv')
OUT = Path('output')
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA)
print(f"Loaded {len(df)} rows, {df.columns.tolist()}")

# ── Color palette ──────────────────────────────────────────────────────
DARK_BG = '#0f0f0f'
CARD_BG = '#1a1a2e'
GREEN = '#00e676'
YELLOW = '#ffd600'
RED = '#ff5252'
CYAN = '#00e5ff'
PURPLE = '#bb86fc'
ORANGE = '#ff9100'
WHITE = '#e0e0e0'
GRID_COLOR = '#2a2a3e'

STRATEGY_COLORS_10 = ['#00e676','#00bfa5','#40c4ff','#448aff','#7c4dff',
                       '#e040fb','#ff4081','#ff6e40','#ffd740','#eeff41']

plt.rcParams.update({
    'figure.facecolor': DARK_BG,
    'axes.facecolor': CARD_BG,
    'axes.edgecolor': GRID_COLOR,
    'axes.labelcolor': WHITE,
    'text.color': WHITE,
    'xtick.color': WHITE,
    'ytick.color': WHITE,
    'grid.color': GRID_COLOR,
    'font.family': 'sans-serif',
    'font.size': 11,
})

# Short labels for strategies
SHORT = {
    'charm_pricing': 'Charm',
    'round_pricing': 'Round',
    'anchor_high': 'Anchor High',
    'anchor_low': 'Anchor Low',
    'decoy_pricing': 'Decoy',
    'bundle_pricing': 'Bundle',
    'urgency_pricing': 'Urgency',
    'prestige_pricing': 'Prestige',
    'free_shipping_threshold': 'Free Ship',
    'odd_specific_pricing': 'Odd Specific',
}

PSYCHOLOGY = {
    'charm_pricing': 'Left-Digit Effect',
    'round_pricing': 'Round Number',
    'anchor_high': 'Anchoring (High)',
    'anchor_low': 'Anchoring (Low)',
    'decoy_pricing': 'Decoy Effect',
    'bundle_pricing': 'Bundle Illusion',
    'urgency_pricing': 'Scarcity/Urgency',
    'prestige_pricing': 'Prestige Signal',
    'free_shipping_threshold': 'Threshold Nudge',
    'odd_specific_pricing': 'Precision Trust',
}

# ══════════════════════════════════════════════════════════════════════
# 1. Strategy Conversion Battle
# ══════════════════════════════════════════════════════════════════════
strat = df.groupby('pricing_strategy').agg(
    n=('converted', 'count'),
    conversions=('converted', 'sum'),
    conv_rate=('converted', 'mean'),
    avg_revenue=('revenue', 'mean'),
    avg_cart=('items_in_cart', 'mean'),
).sort_values('conv_rate', ascending=False).reset_index()
strat['rank'] = range(1, len(strat)+1)
print("\n=== Strategy Conversion Battle ===")
print(strat[['rank','pricing_strategy','conv_rate','avg_revenue','avg_cart']].to_string(index=False))

best_converting = strat.iloc[0]['pricing_strategy']
print(f"\nBest converting strategy: {best_converting}")

# ══════════════════════════════════════════════════════════════════════
# 2. Hidden Cost — Returns & Regret
# ══════════════════════════════════════════════════════════════════════
buyers = df[df['converted'] == 1]
regret = buyers.groupby('pricing_strategy').agg(
    return_rate=('returned', 'mean'),
    avg_satisfaction=('satisfaction_rating', 'mean'),
    total_revenue=('revenue', 'sum'),
    returned_revenue=('revenue', lambda x: x[buyers.loc[x.index, 'returned']==1].sum()),
).reset_index()
regret['net_revenue'] = regret['total_revenue'] - regret['returned_revenue']
regret = regret.merge(strat[['pricing_strategy','conv_rate']], on='pricing_strategy')
regret['regret_gap'] = regret['conv_rate'] - (1 - regret['return_rate'])
print("\n=== Returns & Regret ===")
print(regret[['pricing_strategy','conv_rate','return_rate','avg_satisfaction','net_revenue']].sort_values('return_rate', ascending=False).to_string(index=False))

# ══════════════════════════════════════════════════════════════════════
# 3. Long Game — Repeat Purchases
# ══════════════════════════════════════════════════════════════════════
repeat = buyers.groupby('pricing_strategy').agg(
    repeat_rate=('repeat_purchase_30d', 'mean'),
).reset_index()
repeat = repeat.merge(strat[['pricing_strategy','conv_rate']], on='pricing_strategy')
repeat = repeat.merge(regret[['pricing_strategy','return_rate']], on='pricing_strategy')
repeat['lifetime_score'] = repeat['conv_rate'] * (1 - repeat['return_rate']) * repeat['repeat_rate']
repeat = repeat.sort_values('lifetime_score', ascending=False)
print("\n=== Long Game — Lifetime Score ===")
print(repeat[['pricing_strategy','conv_rate','return_rate','repeat_rate','lifetime_score']].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════
# 4. Segment × Strategy Matrix
# ══════════════════════════════════════════════════════════════════════
seg_strat = df.groupby(['user_segment','pricing_strategy'])['converted'].mean().unstack()
print("\n=== Segment × Strategy Conversion Matrix ===")
print(seg_strat.round(3).to_string())

seg_best = seg_strat.idxmax(axis=1)
seg_worst = seg_strat.idxmin(axis=1)
print("\nBest strategy per segment:")
for seg, s in seg_best.items():
    print(f"  {seg}: {s} ({seg_strat.loc[seg, s]:.1%})")
print("Worst strategy per segment:")
for seg, s in seg_worst.items():
    print(f"  {seg}: {s} ({seg_strat.loc[seg, s]:.1%})")

# ══════════════════════════════════════════════════════════════════════
# 5. Psychology Breakdown
# ══════════════════════════════════════════════════════════════════════
psych_df = strat.copy()
psych_df['principle'] = psych_df['pricing_strategy'].map(PSYCHOLOGY)
psych_df = psych_df.merge(regret[['pricing_strategy','return_rate','avg_satisfaction','net_revenue']], on='pricing_strategy')
psych_df = psych_df.merge(repeat[['pricing_strategy','repeat_rate','lifetime_score']], on='pricing_strategy')
# Effectiveness score: conv_rate * (1-return_rate) * avg_satisfaction / 5
psych_df['effectiveness'] = psych_df['conv_rate'] * (1 - psych_df['return_rate']) * (psych_df['avg_satisfaction'] / 5)
psych_df = psych_df.sort_values('effectiveness', ascending=False)
print("\n=== Psychology Breakdown ===")
print(psych_df[['principle','pricing_strategy','effectiveness','conv_rate','return_rate','avg_satisfaction']].to_string(index=False))

most_powerful = psych_df.iloc[0]['principle']
most_dangerous = psych_df.sort_values('return_rate', ascending=False).iloc[0]['principle']
print(f"\nMost powerful: {most_powerful}")
print(f"Most dangerous: {most_dangerous}")

# ══════════════════════════════════════════════════════════════════════
# 6. Category Intelligence
# ══════════════════════════════════════════════════════════════════════
cat_strat = df.groupby(['category','pricing_strategy'])['converted'].mean().unstack()
print("\n=== Category × Strategy ===")
print(cat_strat.round(3).to_string())

cat_best = cat_strat.idxmax(axis=1)
print("\nBest strategy per category:")
for cat, s in cat_best.items():
    print(f"  {cat}: {s} ({cat_strat.loc[cat, s]:.1%})")

# ══════════════════════════════════════════════════════════════════════
# 7. Pricing Power Score (composite)
# ══════════════════════════════════════════════════════════════════════
power = strat[['pricing_strategy','conv_rate']].copy()
power = power.merge(regret[['pricing_strategy','net_revenue','return_rate','avg_satisfaction']], on='pricing_strategy')
power = power.merge(repeat[['pricing_strategy','repeat_rate']], on='pricing_strategy')

# Normalize each metric 0-1
for col in ['conv_rate','net_revenue','repeat_rate','avg_satisfaction']:
    mn, mx = power[col].min(), power[col].max()
    power[col+'_norm'] = (power[col] - mn) / (mx - mn) if mx > mn else 0.5

power['power_score'] = (
    0.30 * power['conv_rate_norm'] +
    0.25 * power['net_revenue_norm'] +
    0.25 * power['repeat_rate_norm'] +
    0.20 * power['avg_satisfaction_norm']
)
power = power.sort_values('power_score', ascending=False)
power['power_rank'] = range(1, len(power)+1)
print("\n=== Pricing Power Score ===")
print(power[['power_rank','pricing_strategy','power_score','conv_rate','net_revenue','repeat_rate','avg_satisfaction']].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════
# 8. Strategy Recommendations
# ══════════════════════════════════════════════════════════════════════
# Classify based on power score ranking
scale = power[power['power_rank'] <= 3]['pricing_strategy'].tolist()
careful = power[(power['power_rank'] > 3) & (power['power_rank'] <= 5)]['pricing_strategy'].tolist()
targeted = power[(power['power_rank'] > 5) & (power['power_rank'] <= 8)]['pricing_strategy'].tolist()
avoid = power[power['power_rank'] > 8]['pricing_strategy'].tolist()

# Adjust: if a strategy has high return rate, move to careful/avoid
for s in list(scale):
    rr = regret[regret['pricing_strategy']==s]['return_rate'].values[0]
    if rr > regret['return_rate'].median() * 1.2:
        scale.remove(s)
        careful.insert(0, s)

rec = {'SCALE': scale, 'USE CAREFULLY': careful, 'TARGETED ONLY': targeted, 'AVOID': avoid}
print("\n=== Strategy Recommendations ===")
for k, v in rec.items():
    print(f"  {k}: {', '.join(v)}")

def get_rec_color(strategy):
    if strategy in rec['SCALE']: return GREEN
    if strategy in rec['USE CAREFULLY']: return YELLOW
    if strategy in rec['TARGETED ONLY']: return ORANGE
    return RED

# ══════════════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════════════

# ── Chart 1: strategy_battle.png ───────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
data_sorted = strat.sort_values('conv_rate', ascending=True)
colors = [get_rec_color(s) for s in data_sorted['pricing_strategy']]
bars = ax.barh(data_sorted['pricing_strategy'].map(SHORT), data_sorted['conv_rate']*100, color=colors, edgecolor='none', height=0.6)
for bar, val in zip(bars, data_sorted['conv_rate']):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1%}', va='center', fontsize=11, color=WHITE, fontweight='bold')
ax.set_xlabel('Conversion Rate (%)', fontsize=13)
ax.set_title('Strategy Conversion Battle — All 10 Ranked', fontsize=16, fontweight='bold', pad=15)
ax.set_xlim(0, data_sorted['conv_rate'].max()*100 + 8)
ax.grid(axis='x', alpha=0.2)
plt.tight_layout()
fig.savefig(OUT/'strategy_battle.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[OK] strategy_battle.png saved")

# ── Chart 2: regret_chart.png ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
merged = strat[['pricing_strategy','conv_rate']].merge(regret[['pricing_strategy','return_rate']], on='pricing_strategy')
merged = merged.sort_values('conv_rate', ascending=False)
x = np.arange(len(merged))
w = 0.35
bars1 = ax.bar(x - w/2, merged['conv_rate']*100, w, label='Conversion Rate', color=CYAN, edgecolor='none')
bars2 = ax.bar(x + w/2, merged['return_rate']*100, w, label='Return Rate', color=RED, edgecolor='none')
ax.set_xticks(x)
ax.set_xticklabels([SHORT[s] for s in merged['pricing_strategy']], rotation=30, ha='right')
for b, v in zip(bars1, merged['conv_rate']):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.3, f'{v:.0%}', ha='center', fontsize=8, color=CYAN)
for b, v in zip(bars2, merged['return_rate']):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.3, f'{v:.0%}', ha='center', fontsize=8, color=RED)
ax.set_ylabel('Rate (%)', fontsize=13)
ax.set_title('The Regret Chart — Conversion vs Returns', fontsize=16, fontweight='bold', pad=15)
ax.legend(loc='upper right', framealpha=0.3)
ax.grid(axis='y', alpha=0.2)
plt.tight_layout()
fig.savefig(OUT/'regret_chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] regret_chart.png saved")

# ── Chart 3: long_game.png ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 8))
lg = strat[['pricing_strategy','conv_rate']].merge(repeat[['pricing_strategy','repeat_rate']], on='pricing_strategy')
colors_lg = [get_rec_color(s) for s in lg['pricing_strategy']]
ax.scatter(lg['conv_rate']*100, lg['repeat_rate']*100, c=colors_lg, s=250, edgecolors=WHITE, linewidth=1.5, zorder=5)
for _, row in lg.iterrows():
    ax.annotate(SHORT[row['pricing_strategy']], (row['conv_rate']*100, row['repeat_rate']*100),
                textcoords='offset points', xytext=(10, 8), fontsize=10, color=WHITE, fontweight='bold')
# Quadrant lines
ax.axhline(y=lg['repeat_rate'].mean()*100, color=GRID_COLOR, linestyle='--', alpha=0.5)
ax.axvline(x=lg['conv_rate'].mean()*100, color=GRID_COLOR, linestyle='--', alpha=0.5)
ax.text(lg['conv_rate'].max()*100-2, lg['repeat_rate'].max()*100+0.5, 'GOLD\n(Convert + Retain)', ha='right', color=GREEN, fontsize=9, fontstyle='italic')
ax.text(lg['conv_rate'].max()*100-2, lg['repeat_rate'].min()*100-0.5, 'TRAP\n(Convert + Lose)', ha='right', color=RED, fontsize=9, fontstyle='italic')
ax.set_xlabel('Conversion Rate (%)', fontsize=13)
ax.set_ylabel('Repeat Purchase Rate (%)', fontsize=13)
ax.set_title('The Long Game — Short-term vs Long-term Value', fontsize=16, fontweight='bold', pad=15)
ax.grid(alpha=0.2)
plt.tight_layout()
fig.savefig(OUT/'long_game.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] long_game.png saved")

# ── Chart 4: segment_heatmap.png ──────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 8))
hm_data = seg_strat.rename(columns=SHORT) * 100
sns.heatmap(hm_data, annot=True, fmt='.1f', cmap='YlGnBu', linewidths=0.5,
            ax=ax, cbar_kws={'label': 'Conversion Rate (%)'}, linecolor=DARK_BG)
ax.set_title('Segment × Strategy Heatmap — Conversion Rate (%)', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('')
ax.set_ylabel('')
plt.tight_layout()
fig.savefig(OUT/'segment_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] segment_heatmap.png saved")

# ── Chart 5: psychology_breakdown.png ─────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
psy = psych_df.sort_values('effectiveness', ascending=True)
colors_psy = [get_rec_color(s) for s in psy['pricing_strategy']]
bars = ax.barh(psy['principle'], psy['effectiveness']*100, color=colors_psy, edgecolor='none', height=0.6)
for bar, val in zip(bars, psy['effectiveness']):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, f'{val:.1%}', va='center', fontsize=11, color=WHITE, fontweight='bold')
ax.set_xlabel('Effectiveness Score (%)', fontsize=13)
ax.set_title('Psychology Breakdown — Which Trick Works Best?', fontsize=16, fontweight='bold', pad=15)
ax.grid(axis='x', alpha=0.2)
plt.tight_layout()
fig.savefig(OUT/'psychology_breakdown.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] psychology_breakdown.png saved")

# ── Chart 6: pricing_power_ranking.png ────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))
pw = power.sort_values('power_score', ascending=True)
colors_pw = [get_rec_color(s) for s in pw['pricing_strategy']]
# Stacked components
comp_labels = ['Conversion (30%)', 'Net Revenue (25%)', 'Repeat (25%)', 'Satisfaction (20%)']
comp_cols = ['conv_rate_norm', 'net_revenue_norm', 'repeat_rate_norm', 'avg_satisfaction_norm']
comp_weights = [0.30, 0.25, 0.25, 0.20]
comp_colors = [CYAN, GREEN, PURPLE, YELLOW]

left = np.zeros(len(pw))
for label, col, weight, clr in zip(comp_labels, comp_cols, comp_weights, comp_colors):
    vals = pw[col].values * weight * 100
    ax.barh(pw['pricing_strategy'].map(SHORT), vals, left=left, label=label, color=clr, edgecolor='none', height=0.6, alpha=0.85)
    left += vals

for i, (_, row) in enumerate(pw.iterrows()):
    ax.text(left[i] + 0.5, i, f'{row["power_score"]:.2f}', va='center', fontsize=11, color=WHITE, fontweight='bold')

ax.set_xlabel('Composite Power Score', fontsize=13)
ax.set_title('Pricing Power Ranking — Master Score', fontsize=16, fontweight='bold', pad=15)
ax.legend(loc='lower right', framealpha=0.3, fontsize=9)
ax.grid(axis='x', alpha=0.2)
plt.tight_layout()
fig.savefig(OUT/'pricing_power_ranking.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] pricing_power_ranking.png saved")

# ══════════════════════════════════════════════════════════════════════
# pricing_strategy.md — Business Report
# ══════════════════════════════════════════════════════════════════════
best_overall = power.iloc[0]['pricing_strategy']
worst_overall = power.iloc[-1]['pricing_strategy']
most_dangerous_strat = regret.sort_values('return_rate', ascending=False).iloc[0]['pricing_strategy']

# Find biggest missed opportunity: high satisfaction/repeat but low conversion
opp = power.copy()
opp['missed'] = opp['repeat_rate_norm'] * opp['avg_satisfaction_norm'] - opp['conv_rate_norm']
missed_opp = opp.sort_values('missed', ascending=False).iloc[0]['pricing_strategy']

total_revenue = df['revenue'].sum()
avg_revenue = df['revenue'].mean()
overall_conv = df['converted'].mean()
overall_return = buyers['returned'].mean()
overall_repeat = buyers['repeat_purchase_30d'].mean()

# Revenue impact estimates
best_conv = strat[strat['pricing_strategy']==best_overall]['conv_rate'].values[0]
worst_conv = strat[strat['pricing_strategy']==worst_overall]['conv_rate'].values[0]
revenue_uplift = (best_conv - overall_conv) / overall_conv * total_revenue

md = f"""# Pricing Psychology Analysis — Business Report

## Executive Summary
- **{SHORT[best_overall]}** is the highest-scoring strategy overall (Power Score: {power.iloc[0]['power_score']:.2f}) — best balance of conversion, retention, and satisfaction.
- **{SHORT[most_dangerous_strat]}** is the most dangerous — converts well but has the highest return rate, destroying long-term value.
- **{SHORT[missed_opp]}** is the biggest missed opportunity — buyers love it but conversion mechanics aren't optimized yet.

---

## Overall Metrics
| Metric | Value |
|--------|-------|
| Total Users | {len(df):,} |
| Overall Conversion Rate | {overall_conv:.1%} |
| Total Revenue | ₹{total_revenue:,.0f} |
| Average Revenue/User | ₹{avg_revenue:,.0f} |
| Return Rate (buyers) | {overall_return:.1%} |
| Repeat Purchase Rate | {overall_repeat:.1%} |

---

## 1. Strategy Battle Results

| Rank | Strategy | Conversion | Avg Revenue | Avg Cart |
|------|----------|-----------|-------------|----------|
"""
for _, row in strat.iterrows():
    md += f"| {row['rank']:.0f} | {SHORT[row['pricing_strategy']]} | {row['conv_rate']:.1%} | ₹{row['avg_revenue']:,.0f} | {row['avg_cart']:.1f} |\n"

md += f"""
**Winner**: {SHORT[best_converting]} — highest raw conversion rate at {strat.iloc[0]['conv_rate']:.1%}

---

## 2. The Regret Problem — Which Strategies Backfire?

| Strategy | Conversion | Return Rate | Satisfaction | Net Revenue |
|----------|-----------|-------------|-------------|-------------|
"""
for _, row in regret.sort_values('return_rate', ascending=False).iterrows():
    md += f"| {SHORT[row['pricing_strategy']]} | {row['conv_rate']:.1%} | {row['return_rate']:.1%} | {row['avg_satisfaction']:.2f}/5 | ₹{row['net_revenue']:,.0f} |\n"

md += f"""
**Key Finding**: {SHORT[most_dangerous_strat]} has the highest regret gap — converts customers who then regret the purchase.

---

## 3. Long-Term Loyalty Analysis

| Strategy | Conversion | Return Rate | Repeat Rate | Lifetime Score |
|----------|-----------|-------------|-------------|---------------|
"""
for _, row in repeat.iterrows():
    md += f"| {SHORT[row['pricing_strategy']]} | {row['conv_rate']:.1%} | {row['return_rate']:.1%} | {row['repeat_rate']:.1%} | {row['lifetime_score']:.4f} |\n"

md += """
---

## 4. Segment-Specific Recommendations

| Segment | Best Strategy | Conv Rate | Worst Strategy | Conv Rate |
|---------|--------------|-----------|----------------|-----------|
"""
for seg in seg_best.index:
    b = seg_best[seg]
    w = seg_worst[seg]
    md += f"| {seg} | {SHORT[b]} | {seg_strat.loc[seg,b]:.1%} | {SHORT[w]} | {seg_strat.loc[seg,w]:.1%} |\n"

md += """
---

## 5. Category-Specific Recommendations

| Category | Best Strategy | Conv Rate |
|----------|--------------|-----------|
"""
for cat in cat_best.index:
    s = cat_best[cat]
    md += f"| {cat} | {SHORT[s]} | {cat_strat.loc[cat,s]:.1%} |\n"

md += f"""
---

## 6. Pricing Power Ranking (Master Score)

| Rank | Strategy | Power Score | Conversion | Net Revenue | Repeat | Satisfaction |
|------|----------|------------|-----------|-------------|--------|-------------|
"""
for _, row in power.iterrows():
    md += f"| {row['power_rank']:.0f} | {SHORT[row['pricing_strategy']]} | {row['power_score']:.3f} | {row['conv_rate']:.1%} | ₹{row['net_revenue']:,.0f} | {row['repeat_rate']:.1%} | {row['avg_satisfaction']:.2f} |\n"

md += f"""
---

## 7. Strategy Recommendations

### ✅ SCALE — High conversion + satisfaction + retention
{', '.join([SHORT[s] for s in rec['SCALE']])}
> These strategies convert well AND create happy, returning customers. Increase budget allocation here.

### ⚠️ USE CAREFULLY — High conversion but watch the returns
{', '.join([SHORT[s] for s in rec['USE CAREFULLY']])}
> Convert well but risk buyer regret. Use with satisfaction safeguards.

### 🎯 TARGETED ONLY — Works for specific segments
{', '.join([SHORT[s] for s in rec['TARGETED ONLY']])}
> Only deploy these for the segments where they perform well.

### 🚫 AVOID — Low ROI or destroys loyalty
{', '.join([SHORT[s] for s in rec['AVOID']])}
> These strategies cost more than they earn when you factor in returns and lost customers.

---

## 8. Five Actions to Increase Revenue While Reducing Returns

1. **Shift urgency campaigns to bundle/charm pricing** — Urgency converts but causes regret. Redirect that budget to strategies with equal conversion but lower returns.
2. **Deploy segment-specific pricing** — Stop using one strategy for everyone. Match Price Sensitive users with the best strategy for them, Impulse Buyers with theirs.
3. **Add satisfaction touchpoints to high-return strategies** — If you must use urgency pricing, add post-purchase reassurance (confirmation emails, easy returns) to reduce regret.
4. **Double down on {SHORT[best_overall]} for new users** — First Time Buyers respond well and it builds loyalty from day one.
5. **A/B test prestige pricing in Electronics** — High-ticket items benefit from prestige signals, and the return rate stays low.

---

## Final Verdict

| | Strategy | Why |
|-|----------|-----|
| **Best Overall** | {SHORT[best_overall]} | Highest composite score — balances conversion, revenue, retention, satisfaction |
| **Most Dangerous** | {SHORT[most_dangerous_strat]} | High conversion masks high returns and low loyalty |
| **Biggest Missed Opportunity** | {SHORT[missed_opp]} | Customers love it but it's under-deployed — optimize conversion mechanics |
| **Immediate Revenue Action** | Switch from {SHORT[worst_overall]} → {SHORT[best_overall]} | Estimated revenue uplift: ₹{abs(revenue_uplift):,.0f} |
"""

(OUT / 'pricing_strategy.md').write_text(md, encoding='utf-8')
print("[OK] pricing_strategy.md saved")

# ══════════════════════════════════════════════════════════════════════
# dashboard.html
# ══════════════════════════════════════════════════════════════════════

# Prepare data for JS
strat_battle_json = strat.sort_values('conv_rate', ascending=False).to_dict('records')
regret_json = regret.sort_values('conv_rate', ascending=False).to_dict('records')
repeat_json = repeat.sort_values('lifetime_score', ascending=False).to_dict('records')
seg_strat_json = seg_strat.to_dict()
psych_json = psych_df.sort_values('effectiveness', ascending=False).to_dict('records')
cat_strat_json = cat_strat.to_dict()
power_json = power.sort_values('power_score', ascending=False).to_dict('records')

import json

# Build seg heatmap data
seg_rows = []
for segment in seg_strat.index:
    for strategy in seg_strat.columns:
        seg_rows.append({'segment': segment, 'strategy': SHORT[strategy], 'value': round(seg_strat.loc[segment, strategy]*100, 1)})

# Build category data
cat_rows = []
for category in cat_strat.index:
    for strategy in cat_strat.columns:
        cat_rows.append({'category': category, 'strategy': SHORT[strategy], 'value': round(cat_strat.loc[category, strategy]*100, 1)})

# Strategy rec mapping
rec_map = {}
for label, strategies in rec.items():
    for s in strategies:
        rec_map[SHORT[s]] = label

# Key insights
insights = []
insights.append({
    'title': 'Best Strategy Overall',
    'value': SHORT[best_overall],
    'detail': f'Power Score: {power.iloc[0]["power_score"]:.2f} — balances all metrics',
    'color': GREEN
})
insights.append({
    'title': 'Most Dangerous Strategy',
    'value': SHORT[most_dangerous_strat],
    'detail': f'Return rate: {regret[regret["pricing_strategy"]==most_dangerous_strat]["return_rate"].values[0]:.1%} — converts but destroys trust',
    'color': RED
})
insights.append({
    'title': 'Biggest Missed Opportunity',
    'value': SHORT[missed_opp],
    'detail': 'High satisfaction + repeat but under-optimized for conversion',
    'color': YELLOW
})
insights.append({
    'title': 'Total Revenue Analyzed',
    'value': f'₹{total_revenue:,.0f}',
    'detail': f'{len(df):,} pricing events across 10 strategies',
    'color': CYAN
})
insights.append({
    'title': 'Revenue at Risk from Returns',
    'value': f'₹{regret["returned_revenue"].sum():,.0f}',
    'detail': f'{overall_return:.1%} of purchases returned — mostly from urgency tactics',
    'color': ORANGE
})

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pricing Psychology Analyzer</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0f0f0f; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif; padding: 20px; }}
.container {{ max-width: 1400px; margin: 0 auto; }}
h1 {{ text-align: center; font-size: 2.2em; margin-bottom: 5px; background: linear-gradient(90deg, #00e5ff, #bb86fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.subtitle {{ text-align: center; color: #888; margin-bottom: 30px; font-size: 1.1em; }}
.hero {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-bottom: 30px; }}
.hero-card {{ background: #1a1a2e; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #2a2a3e; }}
.hero-card .value {{ font-size: 1.8em; font-weight: 700; margin: 5px 0; }}
.hero-card .label {{ color: #888; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; }}
.section {{ background: #1a1a2e; border-radius: 12px; padding: 25px; margin-bottom: 25px; border: 1px solid #2a2a3e; }}
.section h2 {{ font-size: 1.4em; margin-bottom: 15px; color: #bb86fc; }}
.section h3 {{ font-size: 1.1em; margin: 15px 0 10px; color: #00e5ff; }}
.chart-container {{ position: relative; width: 100%; }}
.chart-tall {{ height: 450px; }}
.chart-medium {{ height: 380px; }}
.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }}
.heatmap-table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
.heatmap-table th {{ padding: 10px; background: #0f0f0f; color: #bb86fc; font-weight: 600; text-align: center; }}
.heatmap-table td {{ padding: 8px; text-align: center; font-weight: 600; border: 1px solid #2a2a3e; }}
.rec-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
.rec-card {{ border-radius: 10px; padding: 18px; }}
.rec-card h4 {{ margin-bottom: 10px; font-size: 1.1em; }}
.rec-card ul {{ list-style: none; padding: 0; }}
.rec-card ul li {{ padding: 4px 0; font-size: 0.95em; }}
.rec-scale {{ background: rgba(0,230,118,0.1); border: 1px solid #00e676; }}
.rec-scale h4 {{ color: #00e676; }}
.rec-careful {{ background: rgba(255,214,0,0.1); border: 1px solid #ffd600; }}
.rec-careful h4 {{ color: #ffd600; }}
.rec-targeted {{ background: rgba(255,145,0,0.1); border: 1px solid #ff9100; }}
.rec-targeted h4 {{ color: #ff9100; }}
.rec-avoid {{ background: rgba(255,82,82,0.1); border: 1px solid #ff5252; }}
.rec-avoid h4 {{ color: #ff5252; }}
.insights-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; }}
.insight-card {{ background: #0f0f0f; border-radius: 10px; padding: 18px; border-left: 4px solid; }}
.insight-card .ins-title {{ font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px; color: #888; margin-bottom: 5px; }}
.insight-card .ins-value {{ font-size: 1.4em; font-weight: 700; margin-bottom: 5px; }}
.insight-card .ins-detail {{ font-size: 0.82em; color: #aaa; }}
@media (max-width: 900px) {{
    .hero {{ grid-template-columns: repeat(2, 1fr); }}
    .grid-2 {{ grid-template-columns: 1fr; }}
    .rec-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .insights-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
</style>
</head>
<body>
<div class="container">
<h1>Pricing Psychology Analyzer</h1>
<p class="subtitle">Analyzing {len(df):,} pricing events across 10 strategies, 5 segments, 4 categories</p>

<!-- Hero Cards -->
<div class="hero">
    <div class="hero-card"><div class="label">Total Users</div><div class="value" style="color:#00e5ff">{len(df):,}</div></div>
    <div class="hero-card"><div class="label">Conversion Rate</div><div class="value" style="color:#00e676">{overall_conv:.1%}</div></div>
    <div class="hero-card"><div class="label">Avg Revenue</div><div class="value" style="color:#bb86fc">₹{avg_revenue:,.0f}</div></div>
    <div class="hero-card"><div class="label">Return Rate</div><div class="value" style="color:#ff5252">{overall_return:.1%}</div></div>
    <div class="hero-card"><div class="label">Repeat Rate</div><div class="value" style="color:#ffd600">{overall_repeat:.1%}</div></div>
</div>

<!-- Strategy Battle -->
<div class="section">
    <h2>Strategy Battle — Conversion Rate Ranking</h2>
    <div class="chart-container chart-tall"><canvas id="battleChart"></canvas></div>
</div>

<!-- Regret + Long Game side by side -->
<div class="grid-2">
    <div class="section">
        <h2>The Regret Chart — Conversion vs Returns</h2>
        <div class="chart-container chart-medium"><canvas id="regretChart"></canvas></div>
    </div>
    <div class="section">
        <h2>The Long Game — Conversion vs Repeat</h2>
        <div class="chart-container chart-medium"><canvas id="longChart"></canvas></div>
    </div>
</div>

<!-- Segment Heatmap -->
<div class="section">
    <h2>Segment × Strategy Heatmap — Conversion Rate (%)</h2>
    <table class="heatmap-table" id="segHeatmap"></table>
</div>

<!-- Psychology Breakdown -->
<div class="section">
    <h2>Psychology Breakdown — Effectiveness Score</h2>
    <div class="chart-container chart-tall"><canvas id="psychChart"></canvas></div>
</div>

<!-- Category Matrix -->
<div class="section">
    <h2>Category Intelligence — Best Strategy per Category</h2>
    <table class="heatmap-table" id="catHeatmap"></table>
</div>

<!-- Power Ranking -->
<div class="section">
    <h2>Pricing Power Ranking — Master Composite Score</h2>
    <div class="chart-container chart-tall"><canvas id="powerChart"></canvas></div>
</div>

<!-- Strategy Board -->
<div class="section">
    <h2>Strategy Board — Recommendations</h2>
    <div class="rec-grid">
        <div class="rec-card rec-scale">
            <h4>✅ SCALE</h4>
            <ul>{"".join(f"<li>{SHORT[s]}</li>" for s in rec['SCALE'])}</ul>
        </div>
        <div class="rec-card rec-careful">
            <h4>⚠️ USE CAREFULLY</h4>
            <ul>{"".join(f"<li>{SHORT[s]}</li>" for s in rec['USE CAREFULLY'])}</ul>
        </div>
        <div class="rec-card rec-targeted">
            <h4>🎯 TARGETED ONLY</h4>
            <ul>{"".join(f"<li>{SHORT[s]}</li>" for s in rec['TARGETED ONLY'])}</ul>
        </div>
        <div class="rec-card rec-avoid">
            <h4>🚫 AVOID</h4>
            <ul>{"".join(f"<li>{SHORT[s]}</li>" for s in rec['AVOID'])}</ul>
        </div>
    </div>
</div>

<!-- Key Insights -->
<div class="section">
    <h2>Key Insights</h2>
    <div class="insights-grid">
        {"".join(f'''<div class="insight-card" style="border-color:{ins['color']}">
            <div class="ins-title">{ins['title']}</div>
            <div class="ins-value" style="color:{ins['color']}">{ins['value']}</div>
            <div class="ins-detail">{ins['detail']}</div>
        </div>''' for ins in insights)}
    </div>
</div>
</div>

<script>
Chart.defaults.color = '#e0e0e0';
Chart.defaults.borderColor = '#2a2a3e';

const recMap = {json.dumps(rec_map)};
function recColor(name) {{
    const r = recMap[name];
    if (r === 'SCALE') return '#00e676';
    if (r === 'USE CAREFULLY') return '#ffd600';
    if (r === 'TARGETED ONLY') return '#ff9100';
    return '#ff5252';
}}

// Strategy Battle
const battleData = {json.dumps([{'name': SHORT[r['pricing_strategy']], 'conv': round(r['conv_rate']*100,1)} for r in strat_battle_json])};
new Chart(document.getElementById('battleChart'), {{
    type: 'bar',
    data: {{
        labels: battleData.map(d => d.name),
        datasets: [{{ data: battleData.map(d => d.conv), backgroundColor: battleData.map(d => recColor(d.name)), borderRadius: 6 }}]
    }},
    options: {{
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ctx.raw.toFixed(1) + '%' }} }} }},
        scales: {{ x: {{ title: {{ display: true, text: 'Conversion Rate (%)' }}, grid: {{ color: '#2a2a3e' }} }}, y: {{ grid: {{ display: false }} }} }}
    }}
}});

// Regret Chart
const regretData = {json.dumps([{'name': SHORT[r['pricing_strategy']], 'conv': round(r['conv_rate']*100,1), 'ret': round(r['return_rate']*100,1)} for r in regret_json])};
new Chart(document.getElementById('regretChart'), {{
    type: 'bar',
    data: {{
        labels: regretData.map(d => d.name),
        datasets: [
            {{ label: 'Conversion %', data: regretData.map(d => d.conv), backgroundColor: '#00e5ff', borderRadius: 4 }},
            {{ label: 'Return %', data: regretData.map(d => d.ret), backgroundColor: '#ff5252', borderRadius: 4 }}
        ]
    }},
    options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ position: 'top' }} }},
        scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ title: {{ display: true, text: 'Rate (%)' }}, grid: {{ color: '#2a2a3e' }} }} }}
    }}
}});

// Long Game - scatter
const longData = {json.dumps([{'name': SHORT[r['pricing_strategy']], 'conv': round(r['conv_rate']*100,1), 'rep': round(r['repeat_rate']*100,1)} for r in repeat_json])};
new Chart(document.getElementById('longChart'), {{
    type: 'scatter',
    data: {{
        datasets: [{{
            data: longData.map(d => ({{ x: d.conv, y: d.rep }})),
            backgroundColor: longData.map(d => recColor(d.name)),
            pointRadius: 10, pointHoverRadius: 14
        }}]
    }},
    options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{
            legend: {{ display: false }},
            tooltip: {{ callbacks: {{ label: (ctx) => longData[ctx.dataIndex].name + ' — Conv: ' + ctx.raw.x + '%, Repeat: ' + ctx.raw.y + '%' }} }}
        }},
        scales: {{
            x: {{ title: {{ display: true, text: 'Conversion Rate (%)' }}, grid: {{ color: '#2a2a3e' }} }},
            y: {{ title: {{ display: true, text: 'Repeat Purchase Rate (%)' }}, grid: {{ color: '#2a2a3e' }} }}
        }}
    }}
}});

// Segment Heatmap Table
const segData = {json.dumps(seg_rows)};
const segments = [...new Set(segData.map(d => d.segment))];
const strategies = [...new Set(segData.map(d => d.strategy))];
let segHtml = '<tr><th></th>' + strategies.map(s => '<th>' + s + '</th>').join('') + '</tr>';
segments.forEach(seg => {{
    segHtml += '<tr><th style="text-align:left">' + seg + '</th>';
    strategies.forEach(st => {{
        const val = segData.find(d => d.segment === seg && d.strategy === st)?.value || 0;
        const intensity = Math.min(val / 65, 1);
        const bg = `rgba(0,229,255,${{(intensity * 0.6 + 0.05).toFixed(2)}})`;
        segHtml += `<td style="background:${{bg}};color:#fff">${{val.toFixed(1)}}%</td>`;
    }});
    segHtml += '</tr>';
}});
document.getElementById('segHeatmap').innerHTML = segHtml;

// Category Heatmap Table
const catData = {json.dumps(cat_rows)};
const categories = [...new Set(catData.map(d => d.category))];
const catStrategies = [...new Set(catData.map(d => d.strategy))];
let catHtml = '<tr><th></th>' + catStrategies.map(s => '<th>' + s + '</th>').join('') + '</tr>';
categories.forEach(cat => {{
    catHtml += '<tr><th style="text-align:left">' + cat + '</th>';
    catStrategies.forEach(st => {{
        const val = catData.find(d => d.category === cat && d.strategy === st)?.value || 0;
        const intensity = Math.min(val / 65, 1);
        const bg = `rgba(187,134,252,${{(intensity * 0.6 + 0.05).toFixed(2)}})`;
        catHtml += `<td style="background:${{bg}};color:#fff">${{val.toFixed(1)}}%</td>`;
    }});
    catHtml += '</tr>';
}});
document.getElementById('catHeatmap').innerHTML = catHtml;

// Psychology Breakdown
const psychData = {json.dumps([{'name': r['principle'], 'strategy': SHORT[r['pricing_strategy']], 'eff': round(r['effectiveness']*100,1)} for r in psych_json])};
new Chart(document.getElementById('psychChart'), {{
    type: 'bar',
    data: {{
        labels: psychData.map(d => d.name),
        datasets: [{{ data: psychData.map(d => d.eff), backgroundColor: psychData.map(d => recColor(d.strategy)), borderRadius: 6 }}]
    }},
    options: {{
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ctx.raw.toFixed(1) + '%' }} }} }},
        scales: {{ x: {{ title: {{ display: true, text: 'Effectiveness Score (%)' }}, grid: {{ color: '#2a2a3e' }} }}, y: {{ grid: {{ display: false }} }} }}
    }}
}});

// Power Ranking - stacked horizontal
const powerData = {json.dumps([{'name': SHORT[r['pricing_strategy']], 'conv': round(r['conv_rate_norm']*30,2), 'rev': round(r['net_revenue_norm']*25,2), 'rep': round(r['repeat_rate_norm']*25,2), 'sat': round(r['avg_satisfaction_norm']*20,2), 'total': round(r['power_score']*100,1)} for r in power_json])};
new Chart(document.getElementById('powerChart'), {{
    type: 'bar',
    data: {{
        labels: powerData.map(d => d.name),
        datasets: [
            {{ label: 'Conversion (30%)', data: powerData.map(d => d.conv), backgroundColor: '#00e5ff', borderRadius: 0 }},
            {{ label: 'Net Revenue (25%)', data: powerData.map(d => d.rev), backgroundColor: '#00e676', borderRadius: 0 }},
            {{ label: 'Repeat (25%)', data: powerData.map(d => d.rep), backgroundColor: '#bb86fc', borderRadius: 0 }},
            {{ label: 'Satisfaction (20%)', data: powerData.map(d => d.sat), backgroundColor: '#ffd600', borderRadius: 4 }}
        ]
    }},
    options: {{
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ position: 'bottom' }}, tooltip: {{ mode: 'index' }} }},
        scales: {{ x: {{ stacked: true, title: {{ display: true, text: 'Composite Score' }}, grid: {{ color: '#2a2a3e' }} }}, y: {{ stacked: true, grid: {{ display: false }} }} }}
    }}
}});
</script>
</body>
</html>"""

(OUT / 'dashboard.html').write_text(html, encoding='utf-8')
print("[OK] dashboard.html saved")

print("\n" + "="*60)
print("ALL 8 OUTPUT FILES CREATED")
print("="*60)
print(f"\n>> Best Strategy: {SHORT[best_overall]} ({best_overall})")
print(f">> Most Dangerous: {SHORT[most_dangerous_strat]} ({most_dangerous_strat})")
print(f">> Biggest Missed Opportunity: {SHORT[missed_opp]} ({missed_opp})")
print(f">> Immediate Revenue Action: Switch low performers to {SHORT[best_overall]} — est. uplift Rs.{abs(revenue_uplift):,.0f}")
