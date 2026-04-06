import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import json

OUT = Path("output")
df = pd.read_csv("data/product_usage.csv")

plt.rcParams.update({
    "figure.facecolor": "#0f0f0f",
    "axes.facecolor": "#1a1a2e",
    "axes.edgecolor": "#333",
    "axes.labelcolor": "#ccc",
    "text.color": "#ccc",
    "xtick.color": "#aaa",
    "ytick.color": "#aaa",
    "grid.color": "#333",
    "font.size": 11,
})

TOTAL_USERS = df['user_id'].nunique()

# Per-user summary
user_agg = df.groupby('user_id').agg(
    returned=('returned_within_7d', 'max'),
    purchased=('purchased', 'max'),
    revenue=('revenue', 'sum'),
    user_type=('user_type', 'first'),
).reset_index()
user_features = df.groupby('user_id')['feature_used'].apply(set).reset_index()
user_features.columns = ['user_id', 'features_used']
user_agg = user_agg.merge(user_features, on='user_id')

ALL_FEATURES = sorted(df['feature_used'].unique())
overall_ret = user_agg['returned'].mean()
overall_pur = user_agg['purchased'].mean()
overall_rev = user_agg['revenue'].sum()
avg_rev_per_user = user_agg['revenue'].mean()

# Build truth table
rows = []
for feat in ALL_FEATURES:
    used = user_agg[user_agg['features_used'].apply(lambda s: feat in s)]
    not_used = user_agg[user_agg['features_used'].apply(lambda s: feat not in s)]
    n_used = len(used)
    usage_rate = n_used / TOTAL_USERS
    ret_with = used['returned'].mean()
    ret_without = not_used['returned'].mean()
    pur_with = used['purchased'].mean()
    pur_without = not_used['purchased'].mean()
    rev_with = used['revenue'].mean()
    rev_without = not_used['revenue'].mean()
    rows.append({
        'feature': feat,
        'users': n_used,
        'usage_rate': usage_rate,
        'ret_with': ret_with, 'ret_without': ret_without,
        'ret_lift': ret_with - ret_without,
        'pur_with': pur_with, 'pur_without': pur_without,
        'pur_lift': pur_with - pur_without,
        'rev_with': rev_with, 'rev_without': rev_without,
        'rev_lift': rev_with - rev_without,
    })
truth = pd.DataFrame(rows)

# Hidden gold = usage < 15%
gold = truth[truth['usage_rate'] < 0.15].copy()
gold['impact'] = gold['ret_lift'] + gold['pur_lift']
gold = gold.sort_values('impact', ascending=False)

# Projections if usage doubles
for i, r in gold.iterrows():
    new_users = min(r['users'] * 2, TOTAL_USERS) - r['users']  # incremental new users
    # Retention gain: new users get the "with" retention rate instead of baseline
    gold.loc[i, 'new_retained'] = new_users * r['ret_with']
    gold.loc[i, 'new_purchased'] = new_users * r['pur_with']
    gold.loc[i, 'new_revenue'] = new_users * r['rev_with']
    gold.loc[i, 'current_revenue'] = r['users'] * r['rev_with']
    # Overall impact
    gold.loc[i, 'ret_boost_pct'] = (new_users * r['ret_lift']) / TOTAL_USERS
    gold.loc[i, 'pur_boost_pct'] = (new_users * r['pur_lift']) / TOTAL_USERS
    gold.loc[i, 'rev_boost_total'] = new_users * r['rev_lift']
    gold.loc[i, 'incremental_users'] = new_users

# Filter to positive-impact features only
gold_positive = gold[gold['impact'] > 0].copy()

print("="*70)
print("HIDDEN GOLD DEEP DIVE — Features Almost Nobody Uses But Drive Results")
print("="*70)
for _, r in gold_positive.iterrows():
    print(f"\n{'='*50}")
    print(f"  {r['feature'].upper()}")
    print(f"{'='*50}")
    print(f"  Current Users:    {int(r['users']):,} / {TOTAL_USERS:,} ({r['usage_rate']:.1%})")
    print(f"  Retention:        {r['ret_with']:.1%} (vs {r['ret_without']:.1%} without) → +{r['ret_lift']:.1%} lift")
    print(f"  Purchase Rate:    {r['pur_with']:.1%} (vs {r['pur_without']:.1%} without) → +{r['pur_lift']:.1%} lift")
    print(f"  Avg Revenue:      ${r['rev_with']:.2f} (vs ${r['rev_without']:.2f} without) → +${r['rev_lift']:.2f} lift")
    print(f"  ─── If Usage Doubles ({int(r['incremental_users']):,} new users) ───")
    print(f"  Overall Retention Boost:  +{r['ret_boost_pct']:.2%}")
    print(f"  Overall Purchase Boost:   +{r['pur_boost_pct']:.2%}")
    print(f"  Additional Revenue:       +${r['rev_boost_total']:,.0f}")
    print(f"  New Retained Users:       +{int(r['new_retained']):,}")
    print(f"  New Purchasers:           +{int(r['new_purchased']):,}")

total_rev_gain = gold_positive['rev_boost_total'].sum()
total_ret_gain = gold_positive['ret_boost_pct'].sum()
total_pur_gain = gold_positive['pur_boost_pct'].sum()
print(f"\n{'='*70}")
print(f"TOTAL GROWTH POTENTIAL (if ALL hidden gold features double usage):")
print(f"  Retention: {overall_ret:.1%} → {overall_ret + total_ret_gain:.1%} (+{total_ret_gain:.2%})")
print(f"  Purchases: {overall_pur:.1%} → {overall_pur + total_pur_gain:.1%} (+{total_pur_gain:.2%})")
print(f"  Revenue:   +${total_rev_gain:,.0f}")
print(f"{'='*70}")

# ═══════════════════════════════════════════════════════════════════════
# Chart: hidden_gold_growth.png
# ═══════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(3, 2, hspace=0.4, wspace=0.3)

gp = gold_positive.sort_values('impact', ascending=False)
feat_names = gp['feature'].str.title().tolist()
n = len(feat_names)
colors = ['#00ffaa', '#00d4ff', '#ff6bff', '#ffd700'][:n]

# ── Panel 1: Usage Rate (tiny bars showing how underused) ──
ax1 = fig.add_subplot(gs[0, 0])
bars = ax1.barh(range(n), gp['usage_rate'] * 100, color=colors, height=0.6, edgecolor='white', linewidth=0.5)
ax1.set_yticks(range(n))
ax1.set_yticklabels(feat_names, fontsize=13, fontweight='bold')
ax1.set_xlabel('Usage Rate (%)', fontsize=12)
ax1.set_title('Almost Nobody Uses Them', fontsize=14, fontweight='bold', color='#ff6b6b')
for i, (_, r) in enumerate(gp.iterrows()):
    ax1.text(r['usage_rate'] * 100 + 0.3, i, f"{r['usage_rate']:.1%}  ({int(r['users']):,} users)",
             va='center', fontsize=11, color='white', fontweight='bold')
ax1.set_xlim(0, max(gp['usage_rate'] * 100) * 2.5)
ax1.grid(axis='x', alpha=0.3)

# ── Panel 2: Retention & Purchase Lift ──
ax2 = fig.add_subplot(gs[0, 1])
x = np.arange(n)
w = 0.35
bars1 = ax2.bar(x - w/2, gp['ret_lift'] * 100, w, color='#00d4aa', label='Retention Lift', edgecolor='white', linewidth=0.5)
bars2 = ax2.bar(x + w/2, gp['pur_lift'] * 100, w, color='#ff6b6b', label='Purchase Lift', edgecolor='white', linewidth=0.5)
ax2.set_xticks(x)
ax2.set_xticklabels(feat_names, fontsize=11, fontweight='bold')
ax2.set_ylabel('Lift (percentage points)', fontsize=12)
ax2.set_title('But They Massively Move the Needle', fontsize=14, fontweight='bold', color='#00ff88')
ax2.legend(fontsize=11)
ax2.grid(axis='y', alpha=0.3)
for bar in bars1:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, h + 0.2, f"+{h:.1f}pp", ha='center', fontsize=10, color='#00d4aa', fontweight='bold')
for bar in bars2:
    h = bar.get_height()
    if h > 0:
        ax2.text(bar.get_x() + bar.get_width()/2, h + 0.2, f"+{h:.1f}pp", ha='center', fontsize=10, color='#ff6b6b', fontweight='bold')

# ── Panel 3: Revenue per user comparison ──
ax3 = fig.add_subplot(gs[1, 0])
x = np.arange(n)
w = 0.35
ax3.bar(x - w/2, gp['rev_without'], w, color='#555', label='Without Feature', edgecolor='white', linewidth=0.5)
ax3.bar(x + w/2, gp['rev_with'], w, color='#ffd700', label='With Feature', edgecolor='white', linewidth=0.5)
ax3.set_xticks(x)
ax3.set_xticklabels(feat_names, fontsize=11, fontweight='bold')
ax3.set_ylabel('Avg Revenue per User ($)', fontsize=12)
ax3.set_title('Revenue Per User: With vs Without', fontsize=14, fontweight='bold', color='#ffd700')
ax3.legend(fontsize=11)
ax3.grid(axis='y', alpha=0.3)
for i, (_, r) in enumerate(gp.iterrows()):
    if r['rev_lift'] > 0:
        ax3.text(i + w/2, r['rev_with'] + 1, f"+${r['rev_lift']:.1f}", ha='center', fontsize=10, color='#ffd700', fontweight='bold')

# ── Panel 4: Projected gains if doubled ──
ax4 = fig.add_subplot(gs[1, 1])
gains = gp[gp['rev_boost_total'] > 0]
bars = ax4.barh(range(len(gains)), gains['rev_boost_total'], color=colors[:len(gains)], height=0.6, edgecolor='white', linewidth=0.5)
ax4.set_yticks(range(len(gains)))
ax4.set_yticklabels(gains['feature'].str.title(), fontsize=13, fontweight='bold')
ax4.set_xlabel('Additional Revenue ($)', fontsize=12)
ax4.set_title('Revenue Gain if Usage Doubles', fontsize=14, fontweight='bold', color='#00ffaa')
for i, (_, r) in enumerate(gains.iterrows()):
    ax4.text(r['rev_boost_total'] + 50, i, f"+${r['rev_boost_total']:,.0f}", va='center', fontsize=12, color='white', fontweight='bold')
ax4.grid(axis='x', alpha=0.3)

# ── Panel 5: Overall impact summary ──
ax5 = fig.add_subplot(gs[2, :])
ax5.axis('off')

summary_text = (
    f"TOTAL GROWTH POTENTIAL IF ALL HIDDEN GOLD FEATURES DOUBLE USAGE\n\n"
    f"Retention:  {overall_ret:.1%}  →  {overall_ret + total_ret_gain:.1%}   (+{total_ret_gain:.2%} boost)\n"
    f"Purchases:  {overall_pur:.1%}  →  {overall_pur + total_pur_gain:.1%}   (+{total_pur_gain:.2%} boost)\n"
    f"Revenue:    +${total_rev_gain:,.0f} additional revenue"
)

# Feature breakdown
breakdown = "\n\nFEATURE BREAKDOWN:\n"
for _, r in gold_positive.iterrows():
    stars = int(r['impact'] / gold_positive['impact'].max() * 5)
    breakdown += (
        f"\n{'*' * stars}  {r['feature'].upper():15s}  |  "
        f"Usage: {r['usage_rate']:.1%}  |  "
        f"Ret Lift: +{r['ret_lift']:.1%}  |  "
        f"Pur Lift: +{r['pur_lift']:.1%}  |  "
        f"Rev if 2x: +${r['rev_boost_total']:,.0f}"
    )

ax5.text(0.5, 0.95, summary_text, transform=ax5.transAxes,
         fontsize=15, fontweight='bold', color='#00ffaa',
         ha='center', va='top', fontfamily='monospace',
         bbox=dict(boxstyle='round,pad=0.8', facecolor='#1a1a2e', edgecolor='#00ffaa', linewidth=2))

ax5.text(0.5, 0.25, breakdown, transform=ax5.transAxes,
         fontsize=11, color='#ccc', ha='center', va='center', fontfamily='monospace',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a2e', edgecolor='#333'))

fig.suptitle('HIDDEN GOLD DEEP DIVE — Low Usage, High Impact Features',
             fontsize=18, fontweight='bold', color='white', y=0.98)

plt.savefig(OUT / 'hidden_gold_growth.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n✓ output/hidden_gold_growth.png")

# ═══════════════════════════════════════════════════════════════════════
# Segment breakdown for hidden gold features
# ═══════════════════════════════════════════════════════════════════════
SEGMENTS = sorted(df['user_type'].unique())

fig2, axes = plt.subplots(2, 2, figsize=(18, 12))
fig2.suptitle('HIDDEN GOLD — Which Segments Benefit Most?', fontsize=16, fontweight='bold', color='white', y=0.98)

for idx, (_, feat_row) in enumerate(gold_positive.iterrows()):
    feat = feat_row['feature']
    ax = axes[idx // 2][idx % 2]

    seg_data = []
    for seg in SEGMENTS:
        seg_users = user_agg[user_agg['user_type'] == seg]
        used = seg_users[seg_users['features_used'].apply(lambda s: feat in s)]
        not_used = seg_users[seg_users['features_used'].apply(lambda s: feat not in s)]
        if len(used) > 5 and len(not_used) > 5:
            seg_data.append({
                'segment': seg,
                'ret_lift': used['returned'].mean() - not_used['returned'].mean(),
                'pur_lift': used['purchased'].mean() - not_used['purchased'].mean(),
                'usage': len(used) / len(seg_users),
                'n_users': len(used),
            })

    sd = pd.DataFrame(seg_data)
    x = np.arange(len(sd))
    w = 0.35
    ax.bar(x - w/2, sd['ret_lift'] * 100, w, color='#00d4aa', label='Retention Lift')
    ax.bar(x + w/2, sd['pur_lift'] * 100, w, color='#ff6b6b', label='Purchase Lift')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s}\n({sd.iloc[i]['usage']:.1%} use)" for i, s in enumerate(sd['segment'])], fontsize=10)
    ax.set_ylabel('Lift (pp)', fontsize=11)
    ax.set_title(f'{feat.upper()} — Segment Impact', fontsize=13, fontweight='bold', color=colors[idx])
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(0, color='#666', linewidth=0.5)

    for i, r in sd.iterrows():
        if r['ret_lift'] > 0:
            ax.text(i - w/2, r['ret_lift'] * 100 + 0.3, f"+{r['ret_lift']*100:.1f}", ha='center', fontsize=9, color='#00d4aa', fontweight='bold')
        if r['pur_lift'] > 0:
            ax.text(i + w/2, r['pur_lift'] * 100 + 0.3, f"+{r['pur_lift']*100:.1f}", ha='center', fontsize=9, color='#ff6b6b', fontweight='bold')

plt.tight_layout()
plt.savefig(OUT / 'hidden_gold_segments.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ output/hidden_gold_segments.png")
