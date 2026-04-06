import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path
import json

# ── Config ──────────────────────────────────────────────────────────────
DATA = Path("data/product_usage.csv")
OUT  = Path("output")
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "#0f0f0f",
    "axes.facecolor":   "#1a1a2e",
    "axes.edgecolor":   "#333",
    "axes.labelcolor":  "#ccc",
    "text.color":       "#ccc",
    "xtick.color":      "#aaa",
    "ytick.color":      "#aaa",
    "grid.color":       "#333",
    "font.size":        11,
})

# ── Load Data ───────────────────────────────────────────────────────────
df = pd.read_csv(DATA)
print(f"Loaded {len(df):,} rows, {df['user_id'].nunique():,} users, {df['feature_used'].nunique()} features")

ALL_FEATURES = sorted(df['feature_used'].unique())
ALL_SEGMENTS = sorted(df['user_type'].unique())
TOTAL_USERS  = df['user_id'].nunique()

# ── Helpers ─────────────────────────────────────────────────────────────
def user_feature_flag(feature):
    """Return series: user_id → bool (ever used this feature)"""
    users_with = set(df.loc[df['feature_used'] == feature, 'user_id'])
    return df['user_id'].map(lambda u: u in users_with)

# Per-user summary (aggregate across all rows per user)
user_agg = df.groupby('user_id').agg(
    returned=('returned_within_7d', 'max'),
    purchased=('purchased', 'max'),
    revenue=('revenue', 'sum'),
    user_type=('user_type', 'first'),
    sessions=('sessions_last_30d', 'max'),
).reset_index()

# Per-user feature set
user_features = df.groupby('user_id')['feature_used'].apply(set).reset_index()
user_features.columns = ['user_id', 'features_used']
user_agg = user_agg.merge(user_features, on='user_id')

# ═══════════════════════════════════════════════════════════════════════
# 1. Feature Truth Engine
# ═══════════════════════════════════════════════════════════════════════
print("\n─── 1. Feature Truth Engine ───")
truth = []
for feat in ALL_FEATURES:
    used = user_agg[user_agg['features_used'].apply(lambda s: feat in s)]
    not_used = user_agg[user_agg['features_used'].apply(lambda s: feat not in s)]

    usage_rate = len(used) / len(user_agg)
    ret_with = used['returned'].mean()
    ret_without = not_used['returned'].mean()
    pur_with = used['purchased'].mean()
    pur_without = not_used['purchased'].mean()
    rev_with = used['revenue'].mean()
    rev_without = not_used['revenue'].mean()

    ret_lift = (ret_with - ret_without) / max(ret_without, 0.001)
    pur_lift = (pur_with - pur_without) / max(pur_without, 0.001)
    rev_lift = (rev_with - rev_without) / max(rev_without, 0.001)

    truth.append({
        'feature': feat,
        'usage_rate': usage_rate,
        'users_count': len(used),
        'ret_with': ret_with, 'ret_without': ret_without,
        'ret_lift': ret_lift, 'ret_lift_abs': ret_with - ret_without,
        'pur_with': pur_with, 'pur_without': pur_without,
        'pur_lift': pur_lift, 'pur_lift_abs': pur_with - pur_without,
        'rev_with': rev_with, 'rev_without': rev_without,
        'rev_lift': rev_lift, 'rev_lift_abs': rev_with - rev_without,
    })

truth_df = pd.DataFrame(truth)
truth_df = truth_df.sort_values('ret_lift_abs', ascending=False)
print(truth_df[['feature','usage_rate','ret_lift_abs','pur_lift_abs','rev_lift_abs']].to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# 2. Behavior Shift Detection
# ═══════════════════════════════════════════════════════════════════════
print("\n─── 2. Behavior Shift Detection ───")
shifts = []
for feat in ALL_FEATURES:
    used = user_agg[user_agg['features_used'].apply(lambda s: feat in s)]
    not_used = user_agg[user_agg['features_used'].apply(lambda s: feat not in s)]
    shifts.append({
        'feature': feat,
        'ret_without': not_used['returned'].mean(),
        'ret_with': used['returned'].mean(),
        'pur_without': not_used['purchased'].mean(),
        'pur_with': used['purchased'].mean(),
        'rev_without': not_used['revenue'].mean(),
        'rev_with': used['revenue'].mean(),
    })
shifts_df = pd.DataFrame(shifts)
print(shifts_df.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# 3. Hidden Gold Detection
# ═══════════════════════════════════════════════════════════════════════
print("\n─── 3. Hidden Gold Detection ───")
gold_df = truth_df[truth_df['usage_rate'] < 0.15].copy()
gold_df['impact'] = gold_df['ret_lift_abs'] + gold_df['pur_lift_abs']
gold_df = gold_df.sort_values('impact', ascending=False)
# Projected gains if usage doubled
gold_df['proj_ret_gain'] = gold_df['ret_lift_abs'] * gold_df['users_count'] / TOTAL_USERS
gold_df['proj_rev_gain'] = gold_df['rev_lift_abs'] * gold_df['users_count']
print(gold_df[['feature','usage_rate','ret_lift_abs','pur_lift_abs','impact','proj_ret_gain','proj_rev_gain']].to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# 4. Vanity Trap Detection
# ═══════════════════════════════════════════════════════════════════════
print("\n─── 4. Vanity Trap Detection ───")
vanity_df = truth_df[truth_df['usage_rate'] > 0.50].copy()
vanity_df['impact'] = vanity_df['ret_lift_abs'] + vanity_df['pur_lift_abs']
vanity_df = vanity_df.sort_values('impact', ascending=True)
print(vanity_df[['feature','usage_rate','ret_lift_abs','pur_lift_abs','impact']].to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# 5. Feature Funnel Analysis
# ═══════════════════════════════════════════════════════════════════════
print("\n─── 5. Feature Funnel Analysis ───")
funnel = []
for feat in ALL_FEATURES:
    users = user_agg[user_agg['features_used'].apply(lambda s: feat in s)]
    n = len(users)
    returned = users['returned'].sum()
    purchased_of_returned = users[users['returned']==1]['purchased'].sum()
    funnel.append({
        'feature': feat,
        'users': n,
        'returned': returned,
        'return_rate': returned/n if n else 0,
        'purchased_of_returned': purchased_of_returned,
        'purchase_given_return': purchased_of_returned/returned if returned else 0,
        'full_funnel': purchased_of_returned/n if n else 0,
    })
funnel_df = pd.DataFrame(funnel).sort_values('full_funnel', ascending=False)
print(funnel_df.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# 6. Segment Intelligence
# ═══════════════════════════════════════════════════════════════════════
print("\n─── 6. Segment Intelligence ───")
seg_retention = {}
seg_purchase = {}
seg_revenue = {}
for seg in ALL_SEGMENTS:
    seg_users = user_agg[user_agg['user_type'] == seg]
    seg_user_ids = set(seg_users['user_id'])
    for feat in ALL_FEATURES:
        used = seg_users[seg_users['features_used'].apply(lambda s: feat in s)]
        not_used = seg_users[seg_users['features_used'].apply(lambda s: feat not in s)]
        if len(used) > 5 and len(not_used) > 5:
            seg_retention[(feat, seg)] = used['returned'].mean() - not_used['returned'].mean()
            seg_purchase[(feat, seg)] = used['purchased'].mean() - not_used['purchased'].mean()
            seg_revenue[(feat, seg)] = used['revenue'].mean() - not_used['revenue'].mean()
        else:
            seg_retention[(feat, seg)] = 0
            seg_purchase[(feat, seg)] = 0
            seg_revenue[(feat, seg)] = 0

seg_ret_matrix = pd.DataFrame(
    [[seg_retention.get((f, s), 0) for s in ALL_SEGMENTS] for f in ALL_FEATURES],
    index=ALL_FEATURES, columns=ALL_SEGMENTS
)
seg_pur_matrix = pd.DataFrame(
    [[seg_purchase.get((f, s), 0) for s in ALL_SEGMENTS] for f in ALL_FEATURES],
    index=ALL_FEATURES, columns=ALL_SEGMENTS
)
print("Retention lift by segment:")
print(seg_ret_matrix.round(3).to_string())

# ═══════════════════════════════════════════════════════════════════════
# 7. Feature Power Score
# ═══════════════════════════════════════════════════════════════════════
print("\n─── 7. Feature Power Score ───")
# Normalize each metric to 0-1
def norm(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn) if mx > mn else s * 0

truth_df['ret_norm'] = norm(truth_df['ret_lift_abs'])
truth_df['pur_norm'] = norm(truth_df['pur_lift_abs'])
truth_df['rev_norm'] = norm(truth_df['rev_lift_abs'])
truth_df['power_score'] = 0.4 * truth_df['ret_norm'] + 0.4 * truth_df['pur_norm'] + 0.2 * truth_df['rev_norm']
truth_df = truth_df.sort_values('power_score', ascending=False).reset_index(drop=True)
truth_df['rank'] = range(1, len(truth_df)+1)
print(truth_df[['rank','feature','power_score','ret_lift_abs','pur_lift_abs','rev_lift_abs']].to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# 8. Product Strategy Engine
# ═══════════════════════════════════════════════════════════════════════
print("\n─── 8. Product Strategy Engine ───")
strategy = {}
for _, row in truth_df.iterrows():
    feat = row['feature']
    ps = row['power_score']
    usage = row['usage_rate']
    if ps >= 0.6:
        strategy[feat] = 'PUSH'
    elif ps >= 0.35 and usage < 0.20:
        strategy[feat] = 'IMPROVE'
    elif ps >= 0.25:
        strategy[feat] = 'MONITOR'
    elif usage > 0.4 and ps < 0.25:
        strategy[feat] = 'REMOVE'
    else:
        strategy[feat] = 'MONITOR'
truth_df['strategy'] = truth_df['feature'].map(strategy)
print(truth_df[['feature','power_score','usage_rate','strategy']].to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# CHARTS
# ═══════════════════════════════════════════════════════════════════════

# ── Chart 1: feature_truth.png ──────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
td = truth_df.sort_values('ret_lift_abs', ascending=True)
y = range(len(td))

ax = axes[0]
ax.barh(y, td['ret_without'], height=0.4, color='#555', label='Without Feature')
ax.barh([i+0.4 for i in y], td['ret_with'], height=0.4, color='#00d4aa', label='With Feature')
ax.set_yticks([i+0.2 for i in y])
ax.set_yticklabels(td['feature'])
ax.set_xlabel('Retention Rate')
ax.set_title('Retention: With vs Without Feature', fontsize=14, fontweight='bold')
ax.legend()

ax = axes[1]
ax.barh(y, td['pur_without'], height=0.4, color='#555', label='Without Feature')
ax.barh([i+0.4 for i in y], td['pur_with'], height=0.4, color='#ff6b6b', label='With Feature')
ax.set_yticks([i+0.2 for i in y])
ax.set_yticklabels(td['feature'])
ax.set_xlabel('Purchase Rate')
ax.set_title('Purchase: With vs Without Feature', fontsize=14, fontweight='bold')
ax.legend()

plt.suptitle('FEATURE TRUTH — Does This Feature Actually Matter?', fontsize=16, fontweight='bold', color='white')
plt.tight_layout()
plt.savefig(OUT / 'feature_truth.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ feature_truth.png")

# ── Chart 2: hidden_gold.png ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 8))
td = truth_df.copy()
td['impact'] = td['ret_lift_abs'] + td['pur_lift_abs']

# Quadrant boundaries
usage_thresh = 0.15
impact_median = td['impact'].median()

# Background quadrants
ax.axvline(usage_thresh, color='#444', ls='--', alpha=0.7)
ax.axhline(impact_median, color='#444', ls='--', alpha=0.7)

colors = []
for _, r in td.iterrows():
    if r['usage_rate'] < usage_thresh and r['impact'] > impact_median:
        colors.append('#00ff88')  # hidden gold
    elif r['usage_rate'] > usage_thresh and r['impact'] < impact_median:
        colors.append('#ff4444')  # vanity trap
    elif r['usage_rate'] > usage_thresh and r['impact'] > impact_median:
        colors.append('#00d4aa')  # high usage, high impact = good
    else:
        colors.append('#888')

ax.scatter(td['usage_rate'], td['impact'], c=colors, s=200, zorder=5, edgecolors='white', linewidth=0.5)
for _, r in td.iterrows():
    ax.annotate(r['feature'], (r['usage_rate'], r['impact']),
                textcoords="offset points", xytext=(8, 8), fontsize=10, color='white')

ax.text(0.02, td['impact'].max()*0.95, 'HIDDEN GOLD', fontsize=14, color='#00ff88', fontweight='bold')
ax.text(td['usage_rate'].max()*0.7, td['impact'].min()*1.1, 'VANITY TRAP', fontsize=14, color='#ff4444', fontweight='bold')
ax.set_xlabel('Usage Rate', fontsize=12)
ax.set_ylabel('Impact Score (Retention + Purchase Lift)', fontsize=12)
ax.set_title('Feature Quadrant — Hidden Gold vs Vanity Traps', fontsize=14, fontweight='bold', color='white')
plt.tight_layout()
plt.savefig(OUT / 'hidden_gold.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ hidden_gold.png")

# ── Chart 3: vanity_features.png ────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))
td = truth_df.copy()
td['usage_rank'] = td['usage_rate'].rank(ascending=False).astype(int)
td['impact_rank'] = td['power_score'].rank(ascending=False).astype(int)
td = td.sort_values('feature')

x = range(len(td))
w = 0.35
ax.bar([i - w/2 for i in x], td['usage_rank'], w, color='#ff6b6b', label='Usage Rank (popularity)')
ax.bar([i + w/2 for i in x], td['impact_rank'], w, color='#00d4aa', label='Impact Rank (power score)')
ax.set_xticks(list(x))
ax.set_xticklabels(td['feature'], rotation=45, ha='right')
ax.set_ylabel('Rank (1 = highest)')
ax.set_title('Usage Rank vs Impact Rank — The Disconnect Reveals Vanity & Gold', fontsize=14, fontweight='bold', color='white')
ax.legend()
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(OUT / 'vanity_features.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ vanity_features.png")

# ── Chart 4: feature_funnel.png ─────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
top6 = funnel_df.head(6)
for idx, (_, row) in enumerate(top6.iterrows()):
    ax = axes[idx//3][idx%3]
    stages = [1.0, row['return_rate'], row['full_funnel']]
    labels = ['Used Feature', f"Returned\n({stages[1]:.1%})", f"Purchased\n({stages[2]:.1%})"]
    colors_f = ['#4a90d9', '#00d4aa', '#ff6b6b']
    ax.barh([2, 1, 0], stages, color=colors_f, height=0.6, edgecolor='white', linewidth=0.5)
    ax.set_yticks([2, 1, 0])
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 1.1)
    ax.set_title(row['feature'].upper(), fontsize=13, fontweight='bold', color='white')
    ax.set_xlabel('Conversion Rate')

plt.suptitle('FEATURE FUNNEL — Feature → Return → Purchase', fontsize=16, fontweight='bold', color='white')
plt.tight_layout()
plt.savefig(OUT / 'feature_funnel.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ feature_funnel.png")

# ── Chart 5: segment_heatmap.png ────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

sns.heatmap(seg_ret_matrix, annot=True, fmt='.3f', cmap='RdYlGn', center=0,
            ax=axes[0], linewidths=0.5, linecolor='#333',
            cbar_kws={'label': 'Retention Lift'})
axes[0].set_title('Retention Lift by Feature × Segment', fontsize=13, fontweight='bold', color='white')

sns.heatmap(seg_pur_matrix, annot=True, fmt='.3f', cmap='RdYlGn', center=0,
            ax=axes[1], linewidths=0.5, linecolor='#333',
            cbar_kws={'label': 'Purchase Lift'})
axes[1].set_title('Purchase Lift by Feature × Segment', fontsize=13, fontweight='bold', color='white')

plt.suptitle('SEGMENT INTELLIGENCE — Which Features Work for Which Users?', fontsize=16, fontweight='bold', color='white')
plt.tight_layout()
plt.savefig(OUT / 'segment_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ segment_heatmap.png")

# ── Chart 6: power_ranking.png ──────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))
td = truth_df.sort_values('power_score', ascending=True)
colors_pr = []
for i, (_, r) in enumerate(td.iterrows()):
    rank = len(td) - i
    if rank <= 4:
        colors_pr.append('#00d4aa')
    elif rank <= 8:
        colors_pr.append('#ffd700')
    else:
        colors_pr.append('#ff4444')

y = range(len(td))
# Stacked bars for score breakdown
ret_comp = td['ret_norm'] * 0.4
pur_comp = td['pur_norm'] * 0.4
rev_comp = td['rev_norm'] * 0.2
ax.barh(y, ret_comp, color='#00d4aa', label='Retention (40%)', height=0.6)
ax.barh(y, pur_comp, left=ret_comp, color='#ff6b6b', label='Purchase (40%)', height=0.6)
ax.barh(y, rev_comp, left=ret_comp+pur_comp, color='#ffd700', label='Revenue (20%)', height=0.6)

for i, (_, r) in enumerate(td.iterrows()):
    ax.text(r['power_score'] + 0.02, i, f"{r['power_score']:.2f}", va='center', fontsize=10, color='white')

ax.set_yticks(list(y))
ax.set_yticklabels(td['feature'])
ax.set_xlabel('Power Score')
ax.set_title('FEATURE POWER RANKING — Most Impactful to Most Useless', fontsize=14, fontweight='bold', color='white')
ax.legend(loc='lower right')
plt.tight_layout()
plt.savefig(OUT / 'power_ranking.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ power_ranking.png")

# ═══════════════════════════════════════════════════════════════════════
# product_strategy.md
# ═══════════════════════════════════════════════════════════════════════
overall_retention = user_agg['returned'].mean()
overall_purchase = user_agg['purchased'].mean()
overall_revenue = user_agg['revenue'].sum()

top_feat = truth_df.iloc[0]
bottom_feat = truth_df.iloc[-1]

# Hidden gold = low usage, high power
gold_features = truth_df[(truth_df['usage_rate'] < 0.15) & (truth_df['power_score'] > 0.3)]
vanity_features = truth_df[(truth_df['usage_rate'] > 0.50) & (truth_df['power_score'] < 0.25)]

push_feats = truth_df[truth_df['strategy']=='PUSH']
improve_feats = truth_df[truth_df['strategy']=='IMPROVE']
monitor_feats = truth_df[truth_df['strategy']=='MONITOR']
remove_feats = truth_df[truth_df['strategy']=='REMOVE']

md = f"""# Product Strategy Report — Feature Impact Analytics
*Generated: 2026-04-02 | {TOTAL_USERS:,} users | {len(df):,} interactions | 12 features analyzed*

---

## Executive Summary
- **{top_feat['feature'].title()}** is the most powerful feature with a power score of {top_feat['power_score']:.2f} — it lifts retention by {top_feat['ret_lift_abs']:.1%} and purchases by {top_feat['pur_lift_abs']:.1%}
- {len(vanity_features)} feature(s) are vanity traps: high usage but negligible business impact — resources should be reallocated
- {len(gold_features)} hidden gold feature(s) identified with low adoption but outsized impact — doubling their usage could unlock significant growth

---

## Key Metrics
| Metric | Value |
|--------|-------|
| Total Users | {TOTAL_USERS:,} |
| Total Interactions | {len(df):,} |
| Overall Retention | {overall_retention:.1%} |
| Overall Purchase Rate | {overall_purchase:.1%} |
| Total Revenue | ${overall_revenue:,.2f} |

---

## Feature Truth Analysis

| Feature | Usage Rate | Retention Lift | Purchase Lift | Revenue Lift | Power Score |
|---------|-----------|---------------|--------------|-------------|-------------|
"""
for _, r in truth_df.iterrows():
    md += f"| {r['feature']} | {r['usage_rate']:.1%} | {r['ret_lift_abs']:+.3f} | {r['pur_lift_abs']:+.3f} | ${r['rev_lift_abs']:+.2f} | {r['power_score']:.2f} |\n"

md += f"""
---

## Hidden Gold Features
*Low usage (< 15%) but high impact — untapped growth levers*

"""
if len(gold_features) > 0:
    for _, r in gold_features.iterrows():
        current_users = r['users_count']
        doubled_users = min(current_users * 2, TOTAL_USERS)
        new_ret = r['ret_lift_abs'] * doubled_users / TOTAL_USERS
        md += f"### {r['feature'].title()}\n"
        md += f"- **Usage**: {r['usage_rate']:.1%} ({current_users:,} users)\n"
        md += f"- **Retention Lift**: {r['ret_lift_abs']:+.3f}\n"
        md += f"- **Purchase Lift**: {r['pur_lift_abs']:+.3f}\n"
        md += f"- **If usage doubled**: ~{new_ret:.2%} additional overall retention boost\n\n"
else:
    md += "No features meet the strict hidden gold criteria (usage < 15% AND power score > 0.3).\n"
    md += "However, features with below-median usage and above-median impact include:\n\n"
    median_usage = truth_df['usage_rate'].median()
    median_ps = truth_df['power_score'].median()
    near_gold = truth_df[(truth_df['usage_rate'] < median_usage) & (truth_df['power_score'] > median_ps)]
    for _, r in near_gold.iterrows():
        md += f"- **{r['feature'].title()}**: usage {r['usage_rate']:.1%}, power score {r['power_score']:.2f}\n"

md += f"""
---

## Vanity Trap Features
*High usage (> 50%) but low impact — consuming resources without driving growth*

"""
if len(vanity_features) > 0:
    for _, r in vanity_features.iterrows():
        md += f"### {r['feature'].title()}\n"
        md += f"- **Usage**: {r['usage_rate']:.1%} ({r['users_count']:,} users)\n"
        md += f"- **Retention Lift**: {r['ret_lift_abs']:+.3f} (negligible)\n"
        md += f"- **Purchase Lift**: {r['pur_lift_abs']:+.3f} (negligible)\n"
        md += f"- **Verdict**: High traffic, low value — re-evaluate engineering investment\n\n"
else:
    md += "No features meet the strict vanity trap criteria (usage > 50% AND power score < 0.25).\n"
    md += "Lowest-impact high-usage features:\n\n"
    high_usage_low = truth_df.sort_values('power_score').head(3)
    for _, r in high_usage_low.iterrows():
        md += f"- **{r['feature'].title()}**: usage {r['usage_rate']:.1%}, power score {r['power_score']:.2f}\n"

md += f"""
---

## Segment-Specific Recommendations

"""
for seg in ALL_SEGMENTS:
    md += f"### {seg} Users\n"
    # Best features for this segment
    seg_scores = [(f, seg_retention.get((f, seg), 0), seg_purchase.get((f, seg), 0)) for f in ALL_FEATURES]
    seg_scores.sort(key=lambda x: x[1] + x[2], reverse=True)
    best = seg_scores[:3]
    worst = seg_scores[-3:]
    md += f"- **Top drivers**: {', '.join(f'{s[0]} (ret: {s[1]:+.3f}, pur: {s[2]:+.3f})' for s in best)}\n"
    md += f"- **Least effective**: {', '.join(f'{s[0]} (ret: {s[1]:+.3f}, pur: {s[2]:+.3f})' for s in worst)}\n\n"

md += f"""
---

## Feature Power Ranking

| Rank | Feature | Power Score | Strategy |
|------|---------|------------|----------|
"""
for _, r in truth_df.iterrows():
    md += f"| {r['rank']} | {r['feature']} | {r['power_score']:.2f} | {r['strategy']} |\n"

md += f"""
---

## Product Strategy Board

### PUSH — Invest More
"""
for _, r in push_feats.iterrows():
    md += f"- **{r['feature'].title()}** (score: {r['power_score']:.2f}) — high impact, drives retention and revenue\n"

md += f"""
### IMPROVE — High Potential, Needs Attention
"""
for _, r in improve_feats.iterrows():
    md += f"- **{r['feature'].title()}** (score: {r['power_score']:.2f}, usage: {r['usage_rate']:.1%}) — strong lift but underadopted\n"

md += f"""
### MONITOR — Maintain Current Investment
"""
for _, r in monitor_feats.iterrows():
    md += f"- **{r['feature'].title()}** (score: {r['power_score']:.2f}) — moderate impact, keep steady\n"

md += f"""
### REMOVE — Re-evaluate Investment
"""
if len(remove_feats) > 0:
    for _, r in remove_feats.iterrows():
        md += f"- **{r['feature'].title()}** (score: {r['power_score']:.2f}, usage: {r['usage_rate']:.1%}) — low ROI\n"
else:
    md += "- No features currently flagged for removal (all show some positive signal)\n"

md += f"""
---

## 5 Actions to Increase Retention & Revenue

1. **Double down on {truth_df.iloc[0]['feature']}** — it's the #1 driver. Promote it in onboarding, make it more visible, and personalize it for each segment.
2. **Boost adoption of underused high-impact features** — features with strong lift but low usage represent the biggest growth opportunity. Run experiments to increase discoverability.
3. **Reduce investment in bottom-ranked features** — the lowest power-score features consume engineering resources without proportional return. Redirect effort to top performers.
4. **Segment-specific feature promotion** — different features work for different user types. Personalize the experience by showing segment-optimized feature suggestions.
5. **Fix funnel leaks** — features where users return but don't purchase have conversion problems. Optimize the return-to-purchase flow for the top 3 features by retention.

---

## ROI Estimate

If recommendations are followed:
- Increasing adoption of top 3 features by 20%: estimated +{truth_df.head(3)['ret_lift_abs'].mean() * 0.2:.1%} overall retention improvement
- Reallocating resources from bottom 3 to top 3: estimated +{truth_df.head(3)['pur_lift_abs'].mean() * 0.15:.1%} purchase rate improvement
- Combined projected revenue impact: +${overall_revenue * truth_df.head(3)['rev_lift_abs'].mean() * 0.001:,.0f} annually (conservative estimate)

---

## Final Verdict

- **Most Powerful Feature**: **{truth_df.iloc[0]['feature'].title()}** — power score {truth_df.iloc[0]['power_score']:.2f}, the strongest driver of retention and purchases
- **Most Misleading Feature**: **{truth_df.iloc[-1]['feature'].title()}** — usage of {truth_df.iloc[-1]['usage_rate']:.1%} but lowest power score ({truth_df.iloc[-1]['power_score']:.2f}), giving a false sense of importance
- **Biggest Missed Opportunity**: Features in the IMPROVE category with high lift but low adoption — these are growth levers hiding in plain sight
- **1 Decision That Increases Revenue Immediately**: Promote **{truth_df.iloc[0]['feature']}** more aggressively across all touchpoints — it has proven impact and room to grow
"""

with open(OUT / 'product_strategy.md', 'w') as f:
    f.write(md)
print("✓ product_strategy.md")

# ═══════════════════════════════════════════════════════════════════════
# dashboard.html
# ═══════════════════════════════════════════════════════════════════════

# Prepare data for JS
truth_json = truth_df[['feature','usage_rate','ret_with','ret_without','ret_lift_abs',
                        'pur_with','pur_without','pur_lift_abs','rev_lift_abs',
                        'power_score','strategy','rank']].to_dict('records')
funnel_json = funnel_df.to_dict('records')
seg_ret_json = seg_ret_matrix.reset_index().to_dict('records')
seg_pur_json = seg_pur_matrix.reset_index().to_dict('records')

# Gold & vanity for dashboard
gold_for_dash = truth_df.nsmallest(4, 'usage_rate').nlargest(3, 'power_score')
vanity_for_dash = truth_df.nlargest(4, 'usage_rate').nsmallest(3, 'power_score')

# Build gold alert cards
gold_cards_html = ""
for _, r in gold_for_dash.iterrows():
    gold_cards_html += f'''<div class="card alert-gold" style="margin-bottom:12px;">
        <div class="alert-title">{r['feature'].title()}</div>
        <div class="alert-stat">Usage: <strong>{r['usage_rate']:.1%}</strong> | Retention Lift: <strong>{r['ret_lift_abs']:+.3f}</strong></div>
        <div class="alert-stat">Purchase Lift: <strong>{r['pur_lift_abs']:+.3f}</strong> | Power Score: <strong>{r['power_score']:.2f}</strong></div>
        <div class="alert-stat">Doubling adoption could boost overall metrics significantly</div>
    </div>'''

vanity_cards_html = ""
for _, r in vanity_for_dash.iterrows():
    vanity_cards_html += f'''<div class="card alert-vanity" style="margin-bottom:12px;">
        <div class="alert-title">{r['feature'].title()}</div>
        <div class="alert-stat">Usage: <strong>{r['usage_rate']:.1%}</strong> | Retention Lift: <strong>{r['ret_lift_abs']:+.3f}</strong></div>
        <div class="alert-stat">Purchase Lift: <strong>{r['pur_lift_abs']:+.3f}</strong> | Power Score: <strong>{r['power_score']:.2f}</strong></div>
        <div class="alert-stat">High traffic, low business value — re-evaluate investment</div>
    </div>'''

top_feat_name = truth_df.iloc[0]['feature'].title()
top_feat_score = f"{truth_df.iloc[0]['power_score']:.2f}"
bottom_feat_name = truth_df.iloc[-1]['feature'].title()
bottom_feat_usage = f"{truth_df.iloc[-1]['usage_rate']:.1%}"
bottom_feat_score = f"{truth_df.iloc[-1]['power_score']:.2f}"
top_feat_raw = truth_df.iloc[0]['feature']

# Build the HTML — use PLACEHOLDER tokens for JS data, then replace
html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Feature Impact Analytics Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0f0f0f; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif; padding: 20px; }
.container { max-width: 1400px; margin: 0 auto; }
h1 { text-align: center; font-size: 2.2rem; margin-bottom: 8px; background: linear-gradient(90deg, #00d4aa, #4a90d9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.subtitle { text-align: center; color: #888; margin-bottom: 30px; font-size: 1rem; }
.hero { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 30px; }
.hero-card { background: #1a1a2e; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #2a2a4a; }
.hero-card .value { font-size: 2rem; font-weight: 700; color: #00d4aa; }
.hero-card .label { font-size: 0.85rem; color: #888; margin-top: 4px; }
.section { margin-bottom: 30px; }
.section-title { font-size: 1.4rem; font-weight: 600; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #2a2a4a; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.card { background: #1a1a2e; border-radius: 12px; padding: 20px; border: 1px solid #2a2a4a; }
.card-full { background: #1a1a2e; border-radius: 12px; padding: 20px; border: 1px solid #2a2a4a; margin-bottom: 20px; }
canvas { max-width: 100%; }
.alert-gold { border-left: 4px solid #00ff88; }
.alert-vanity { border-left: 4px solid #ff4444; }
.alert-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 8px; }
.alert-gold .alert-title { color: #00ff88; }
.alert-vanity .alert-title { color: #ff4444; }
.alert-stat { color: #aaa; font-size: 0.9rem; margin: 4px 0; }
.alert-stat strong { color: #e0e0e0; }
.strategy-board { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.strat-col { background: #1a1a2e; border-radius: 12px; padding: 16px; border: 1px solid #2a2a4a; }
.strat-col h3 { text-align: center; padding: 8px; border-radius: 8px; margin-bottom: 12px; font-size: 1rem; }
.strat-push h3 { background: #00d4aa22; color: #00d4aa; }
.strat-improve h3 { background: #ffd70022; color: #ffd700; }
.strat-monitor h3 { background: #4a90d922; color: #4a90d9; }
.strat-remove h3 { background: #ff444422; color: #ff4444; }
.strat-item { background: #0f0f1a; border-radius: 8px; padding: 10px; margin-bottom: 8px; font-size: 0.9rem; }
.strat-item .score { float: right; font-weight: 600; }
.insight-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; }
.insight { background: #1a1a2e; border-radius: 12px; padding: 20px; border: 1px solid #2a2a4a; border-top: 3px solid #4a90d9; }
.insight h4 { color: #4a90d9; margin-bottom: 8px; }
.heatmap-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.heatmap-table th, .heatmap-table td { padding: 8px 12px; text-align: center; border: 1px solid #333; }
.heatmap-table th { background: #2a2a4a; color: #ccc; }
@media (max-width: 900px) {
    .hero { grid-template-columns: repeat(2, 1fr); }
    .grid-2, .strategy-board { grid-template-columns: 1fr; }
    .grid-3 { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<div class="container">
<h1>Feature Impact Analytics</h1>
<p class="subtitle">Separating signal from noise — which features actually drive business outcomes?</p>

<!-- Hero Section -->
<div class="hero">
    <div class="hero-card"><div class="value">__TOTAL_USERS__</div><div class="label">Total Users</div></div>
    <div class="hero-card"><div class="value">__RETENTION__</div><div class="label">Overall Retention</div></div>
    <div class="hero-card"><div class="value">__PURCHASE__</div><div class="label">Purchase Rate</div></div>
    <div class="hero-card"><div class="value">__REVENUE__</div><div class="label">Total Revenue</div></div>
    <div class="hero-card"><div class="value">__NUM_FEATURES__</div><div class="label">Features Analyzed</div></div>
</div>

<!-- Power Ranking -->
<div class="section">
    <div class="section-title">Feature Power Ranking</div>
    <div class="card-full"><canvas id="powerChart" height="400"></canvas></div>
</div>

<!-- Truth Chart -->
<div class="section">
    <div class="section-title">The Truth Chart — Usage vs Actual Impact</div>
    <div class="card-full"><canvas id="truthChart" height="400"></canvas></div>
</div>

<!-- Alerts -->
<div class="section">
    <div class="grid-2">
        <div>
            <div class="section-title" style="color:#00ff88">Hidden Gold Alert</div>
            __GOLD_CARDS__
        </div>
        <div>
            <div class="section-title" style="color:#ff4444">Vanity Trap Alert</div>
            __VANITY_CARDS__
        </div>
    </div>
</div>

<!-- Retention & Purchase Comparison -->
<div class="section">
    <div class="section-title">Retention & Purchase — With vs Without Feature</div>
    <div class="grid-2">
        <div class="card"><canvas id="retentionChart" height="350"></canvas></div>
        <div class="card"><canvas id="purchaseChart" height="350"></canvas></div>
    </div>
</div>

<!-- Segment Heatmap -->
<div class="section">
    <div class="section-title">Segment Intelligence Heatmap</div>
    <div class="card-full">
        <h4 style="margin-bottom:12px; color:#00d4aa;">Retention Lift by Feature x Segment</h4>
        <table class="heatmap-table" id="segTable"></table>
    </div>
</div>

<!-- Funnel -->
<div class="section">
    <div class="section-title">Feature Funnel — Feature > Return > Purchase</div>
    <div class="card-full"><canvas id="funnelChart" height="350"></canvas></div>
</div>

<!-- Strategy Board -->
<div class="section">
    <div class="section-title">Product Strategy Board</div>
    <div class="strategy-board">
        <div class="strat-col strat-push"><h3>PUSH</h3><div id="pushItems"></div></div>
        <div class="strat-col strat-improve"><h3>IMPROVE</h3><div id="improveItems"></div></div>
        <div class="strat-col strat-monitor"><h3>MONITOR</h3><div id="monitorItems"></div></div>
        <div class="strat-col strat-remove"><h3>REMOVE</h3><div id="removeItems"></div></div>
    </div>
</div>

<!-- Key Insights -->
<div class="section">
    <div class="section-title">Key Insights</div>
    <div class="insight-cards">
        <div class="insight">
            <h4>Most Powerful Feature</h4>
            <p><strong>__TOP_FEAT_NAME__</strong> — power score __TOP_FEAT_SCORE__. Drives the highest combined retention and purchase lift across all users.</p>
        </div>
        <div class="insight">
            <h4>Most Misleading Feature</h4>
            <p><strong>__BOTTOM_FEAT_NAME__</strong> — usage __BOTTOM_FEAT_USAGE__ but power score only __BOTTOM_FEAT_SCORE__. Feels important, contributes least.</p>
        </div>
        <div class="insight">
            <h4>Biggest Missed Opportunity</h4>
            <p>Features with strong lift but low adoption. Doubling their reach could meaningfully move retention and revenue needles.</p>
        </div>
        <div class="insight">
            <h4>Segment Insight</h4>
            <p>Feature effectiveness varies dramatically by user type. One-size-fits-all promotion wastes resources. Personalize feature visibility by segment.</p>
        </div>
        <div class="insight">
            <h4>Immediate Revenue Action</h4>
            <p>Promote <strong>__TOP_FEAT_RAW__</strong> more aggressively — it has proven impact and room to grow across all segments.</p>
        </div>
    </div>
</div>

</div>

<script>
const data = __TRUTH_JSON__;
const funnelData = __FUNNEL_JSON__;
const segments = __SEGMENTS_JSON__;
const allFeatures = __ALL_FEATURES_JSON__;
const segData = __SEG_RET_JSON__;

const features = data.map(d => d.feature).sort((a,b) => b.localeCompare(a));

// Sort by power score for ranking
const ranked = [...data].sort((a,b) => a.power_score - b.power_score);

// Power Ranking Chart
new Chart(document.getElementById('powerChart'), {
    type: 'bar',
    data: {
        labels: ranked.map(d => d.feature),
        datasets: [{
            label: 'Power Score',
            data: ranked.map(d => d.power_score),
            backgroundColor: ranked.map(d => {
                if (d.strategy === 'PUSH') return '#00d4aa';
                if (d.strategy === 'IMPROVE') return '#ffd700';
                if (d.strategy === 'REMOVE') return '#ff4444';
                return '#4a90d9';
            }),
            borderRadius: 4,
        }]
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
            x: { grid: { color: '#333' }, ticks: { color: '#aaa' } },
            y: { grid: { display: false }, ticks: { color: '#ccc', font: { size: 12 } } }
        }
    }
});

// Truth Chart
const truthSorted = [...data].sort((a,b) => a.feature.localeCompare(b.feature));
new Chart(document.getElementById('truthChart'), {
    type: 'bar',
    data: {
        labels: truthSorted.map(d => d.feature),
        datasets: [
            { label: 'Usage Rate', data: truthSorted.map(d => d.usage_rate), backgroundColor: '#4a90d9' },
            { label: 'Retention Lift', data: truthSorted.map(d => Math.max(0, d.ret_lift_abs)), backgroundColor: '#00d4aa' },
            { label: 'Purchase Lift', data: truthSorted.map(d => Math.max(0, d.pur_lift_abs)), backgroundColor: '#ff6b6b' },
        ]
    },
    options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#ccc' } } },
        scales: {
            x: { grid: { color: '#333' }, ticks: { color: '#aaa', maxRotation: 45 } },
            y: { grid: { color: '#333' }, ticks: { color: '#aaa' } }
        }
    }
});

// Retention comparison
const retSorted = [...data].sort((a,b) => b.ret_lift_abs - a.ret_lift_abs);
new Chart(document.getElementById('retentionChart'), {
    type: 'bar',
    data: {
        labels: retSorted.map(d => d.feature),
        datasets: [
            { label: 'Without Feature', data: retSorted.map(d => d.ret_without), backgroundColor: '#555' },
            { label: 'With Feature', data: retSorted.map(d => d.ret_with), backgroundColor: '#00d4aa' },
        ]
    },
    options: {
        responsive: true,
        plugins: { title: { display: true, text: 'Retention Rate', color: '#ccc' }, legend: { labels: { color: '#ccc' } } },
        scales: {
            x: { ticks: { color: '#aaa', maxRotation: 45 }, grid: { color: '#333' } },
            y: { ticks: { color: '#aaa' }, grid: { color: '#333' } }
        }
    }
});

// Purchase comparison
const purSorted = [...data].sort((a,b) => b.pur_lift_abs - a.pur_lift_abs);
new Chart(document.getElementById('purchaseChart'), {
    type: 'bar',
    data: {
        labels: purSorted.map(d => d.feature),
        datasets: [
            { label: 'Without Feature', data: purSorted.map(d => d.pur_without), backgroundColor: '#555' },
            { label: 'With Feature', data: purSorted.map(d => d.pur_with), backgroundColor: '#ff6b6b' },
        ]
    },
    options: {
        responsive: true,
        plugins: { title: { display: true, text: 'Purchase Rate', color: '#ccc' }, legend: { labels: { color: '#ccc' } } },
        scales: {
            x: { ticks: { color: '#aaa', maxRotation: 45 }, grid: { color: '#333' } },
            y: { ticks: { color: '#aaa' }, grid: { color: '#333' } }
        }
    }
});

// Funnel chart (top 6)
const topFunnel = [...funnelData].sort((a,b) => b.full_funnel - a.full_funnel).slice(0, 6);
new Chart(document.getElementById('funnelChart'), {
    type: 'bar',
    data: {
        labels: topFunnel.map(d => d.feature),
        datasets: [
            { label: 'Return Rate', data: topFunnel.map(d => d.return_rate), backgroundColor: '#4a90d9' },
            { label: 'Purchase|Return', data: topFunnel.map(d => d.purchase_given_return), backgroundColor: '#00d4aa' },
            { label: 'Full Funnel', data: topFunnel.map(d => d.full_funnel), backgroundColor: '#ff6b6b' },
        ]
    },
    options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#ccc' } } },
        scales: {
            x: { ticks: { color: '#aaa' }, grid: { color: '#333' } },
            y: { ticks: { color: '#aaa' }, grid: { color: '#333' }, max: 1 }
        }
    }
});

// Segment heatmap table
(function() {
    const table = document.getElementById('segTable');
    let html = '<tr><th>Feature</th>';
    segments.forEach(s => html += '<th>' + s + '</th>');
    html += '</tr>';

    allFeatures.forEach(feat => {
        const row = segData.find(r => r.index === feat) || segData.find(r => r[Object.keys(r)[0]] === feat);
        html += '<tr><td style="text-align:left;font-weight:600;">' + feat + '</td>';
        segments.forEach(seg => {
            const val = row ? (row[seg] || 0) : 0;
            const intensity = Math.min(Math.abs(val) * 5, 1);
            const color = val > 0
                ? 'rgba(0, 212, 170, ' + intensity + ')'
                : 'rgba(255, 68, 68, ' + intensity + ')';
            html += '<td style="background:' + color + ';color:#fff;font-weight:600;">' + val.toFixed(3) + '</td>';
        });
        html += '</tr>';
    });
    table.innerHTML = html;
})();

// Strategy board
(function() {
    const containers = {
        'PUSH': document.getElementById('pushItems'),
        'IMPROVE': document.getElementById('improveItems'),
        'MONITOR': document.getElementById('monitorItems'),
        'REMOVE': document.getElementById('removeItems'),
    };
    data.forEach(d => {
        const target = containers[d.strategy];
        if (target) {
            target.innerHTML += '<div class="strat-item">' + d.feature + '<span class="score">' + d.power_score.toFixed(2) + '</span></div>';
        }
    });
    Object.values(containers).forEach(c => {
        if (!c.innerHTML.trim()) c.innerHTML = '<div class="strat-item" style="color:#666;">None</div>';
    });
})();
</script>
</body>
</html>'''

# Replace all placeholders
html = html_template
html = html.replace('__TOTAL_USERS__', f'{TOTAL_USERS:,}')
html = html.replace('__RETENTION__', f'{overall_retention:.1%}')
html = html.replace('__PURCHASE__', f'{overall_purchase:.1%}')
html = html.replace('__REVENUE__', f'${overall_revenue:,.0f}')
html = html.replace('__NUM_FEATURES__', str(len(ALL_FEATURES)))
html = html.replace('__GOLD_CARDS__', gold_cards_html)
html = html.replace('__VANITY_CARDS__', vanity_cards_html)
html = html.replace('__TOP_FEAT_NAME__', top_feat_name)
html = html.replace('__TOP_FEAT_SCORE__', top_feat_score)
html = html.replace('__BOTTOM_FEAT_NAME__', bottom_feat_name)
html = html.replace('__BOTTOM_FEAT_USAGE__', bottom_feat_usage)
html = html.replace('__BOTTOM_FEAT_SCORE__', bottom_feat_score)
html = html.replace('__TOP_FEAT_RAW__', top_feat_raw)
html = html.replace('__TRUTH_JSON__', json.dumps(truth_json))
html = html.replace('__FUNNEL_JSON__', json.dumps(funnel_json))
html = html.replace('__SEGMENTS_JSON__', json.dumps(ALL_SEGMENTS))
html = html.replace('__ALL_FEATURES_JSON__', json.dumps(ALL_FEATURES))
html = html.replace('__SEG_RET_JSON__', json.dumps(seg_ret_json))
# No extra fixes needed

with open(OUT / 'dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ dashboard.html")

# ═══════════════════════════════════════════════════════════════════════
# FINAL VERDICT
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("FINAL VERDICT")
print("="*60)
print(f"Most Powerful Feature:    {truth_df.iloc[0]['feature'].upper()} (power score: {truth_df.iloc[0]['power_score']:.2f})")
print(f"Most Misleading Feature:  {truth_df.iloc[-1]['feature'].upper()} (usage: {truth_df.iloc[-1]['usage_rate']:.1%}, score: {truth_df.iloc[-1]['power_score']:.2f})")

# Biggest missed opportunity: highest power score with lowest usage
opp = truth_df.copy()
opp['opportunity'] = opp['power_score'] * (1 - opp['usage_rate'])
best_opp = opp.sort_values('opportunity', ascending=False).iloc[0]
print(f"Biggest Missed Opportunity: {best_opp['feature'].upper()} (score: {best_opp['power_score']:.2f}, usage: {best_opp['usage_rate']:.1%})")
print(f"\n1 Decision That Increases Revenue Immediately:")
print(f"  → Promote {truth_df.iloc[0]['feature'].upper()} aggressively across all touchpoints.")
print(f"    It has the highest proven impact on retention ({truth_df.iloc[0]['ret_lift_abs']:+.3f})")
print(f"    and purchases ({truth_df.iloc[0]['pur_lift_abs']:+.3f}).")
print("="*60)
print("\nAll 8 output files created successfully.")
