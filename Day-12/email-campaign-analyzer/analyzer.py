import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Setup
os.makedirs('output', exist_ok=True)
df = pd.read_csv('data/email_campaigns.csv')
print(f"Loaded {len(df)} rows")
print(f"Segments: {df['segment'].unique()}")
print(f"Campaigns: {df['campaign'].unique()}")

EMAIL_COST = 0.05

# ============================================================
# 1. EMAIL FUNNEL
# ============================================================
emailed_df = df[df['email_sent'] == 1]
total_sent = int(df['email_sent'].sum())
total_opened = int(df['opened'].sum())
total_clicked = int(df['clicked'].sum())
total_purchased_from_click = int(df[(df['clicked'] == 1) & (df['purchased'] == 1)].shape[0])
total_purchased = int(df['purchased'].sum())
total_revenue = df['revenue'].sum()

open_rate = total_opened / total_sent * 100
click_rate = total_clicked / total_opened * 100
conversion_rate = total_purchased_from_click / total_clicked * 100

funnel_stages = ['Sent', 'Opened', 'Clicked', 'Purchased']
funnel_values = [total_sent, total_opened, total_clicked, total_purchased_from_click]
funnel_dropoffs = []
for i in range(1, len(funnel_values)):
    drop = (1 - funnel_values[i] / funnel_values[i-1]) * 100
    funnel_dropoffs.append(drop)

print(f"\n=== FUNNEL ===")
print(f"Sent: {total_sent}, Opened: {total_opened}, Clicked: {total_clicked}, Purchased: {total_purchased}")
print(f"Open Rate: {open_rate:.1f}%, Click Rate: {click_rate:.1f}%, Conv Rate: {conversion_rate:.1f}%")
print(f"Drop-offs: Sent→Open: {funnel_dropoffs[0]:.1f}%, Open→Click: {funnel_dropoffs[1]:.1f}%, Click→Purchase: {funnel_dropoffs[2]:.1f}%")

# Funnel by segment
seg_funnel = df.groupby('segment').agg(
    sent=('email_sent', 'sum'),
    opened=('opened', 'sum'),
    clicked=('clicked', 'sum'),
    purchased_count=('purchased', 'sum'),
    revenue=('revenue', 'sum')
).reset_index()
# Purchased from click (funnel metric)
seg_pfc = df[df['clicked'] == 1].groupby('segment')['purchased'].sum().reset_index()
seg_pfc.columns = ['segment', 'purchased_from_click']
seg_funnel = seg_funnel.merge(seg_pfc, on='segment', how='left').fillna(0)
seg_funnel['open_rate'] = (seg_funnel['opened'] / seg_funnel['sent'] * 100).round(1)
seg_funnel['click_rate'] = (seg_funnel['clicked'] / seg_funnel['opened'] * 100).round(1)
seg_funnel['conv_rate'] = (seg_funnel['purchased_from_click'] / seg_funnel['clicked'] * 100).round(1)
print(f"\n=== FUNNEL BY SEGMENT ===")
print(seg_funnel[['segment', 'open_rate', 'click_rate', 'conv_rate']].to_string(index=False))

# Funnel by campaign
camp_funnel = df.groupby('campaign').agg(
    sent=('email_sent', 'sum'),
    opened=('opened', 'sum'),
    clicked=('clicked', 'sum'),
    purchased_count=('purchased', 'sum'),
    revenue=('revenue', 'sum')
).reset_index()
camp_pfc = df[df['clicked'] == 1].groupby('campaign')['purchased'].sum().reset_index()
camp_pfc.columns = ['campaign', 'purchased_from_click']
camp_funnel = camp_funnel.merge(camp_pfc, on='campaign', how='left').fillna(0)
camp_funnel['open_rate'] = (camp_funnel['opened'] / camp_funnel['sent'] * 100).round(1)
camp_funnel['click_rate'] = (camp_funnel['clicked'] / camp_funnel['opened'] * 100).round(1)
camp_funnel['conv_rate'] = (camp_funnel['purchased_from_click'] / camp_funnel['clicked'] * 100).round(1)
print(f"\n=== FUNNEL BY CAMPAIGN ===")
print(camp_funnel[['campaign', 'open_rate', 'click_rate', 'conv_rate']].to_string(index=False))

# ============================================================
# 2. CAMPAIGN EFFECTIVENESS — EMAIL vs NO EMAIL
# ============================================================
emailed = df[df['email_sent'] == 1]
not_emailed = df[df['email_sent'] == 0]

overall_email_purchase_rate = emailed['purchased'].mean() * 100 if len(emailed) > 0 else 0
overall_no_email_purchase_rate = not_emailed['purchased'].mean() * 100 if len(not_emailed) > 0 else 0
overall_lift = overall_email_purchase_rate - overall_no_email_purchase_rate

print(f"\n=== EMAIL vs NO EMAIL ===")
print(f"Emailed purchase rate: {overall_email_purchase_rate:.1f}%")
print(f"Not emailed purchase rate: {overall_no_email_purchase_rate:.1f}%")
print(f"Overall lift: {overall_lift:.1f}pp")

# Per segment
seg_email = df.groupby(['segment', 'email_sent']).agg(
    users=('user_id', 'count'),
    purchases=('purchased', 'sum'),
    revenue=('revenue', 'sum')
).reset_index()
seg_email['purchase_rate'] = (seg_email['purchases'] / seg_email['users'] * 100).round(2)

seg_comparison = seg_email.pivot(index='segment', columns='email_sent', values='purchase_rate').reset_index()
seg_comparison.columns = ['segment', 'no_email_rate', 'email_rate']
seg_comparison['lift'] = (seg_comparison['email_rate'] - seg_comparison['no_email_rate']).round(2)
seg_comparison['lift_pct'] = ((seg_comparison['lift'] / seg_comparison['no_email_rate'].replace(0, 0.01)) * 100).round(1)

print(f"\n=== EMAIL LIFT BY SEGMENT ===")
print(seg_comparison.to_string(index=False))

# ============================================================
# 3. OVER-TARGETING
# ============================================================
# Segments where email has little or negative impact
over_targeted = seg_comparison[seg_comparison['lift'] < 2].copy()
over_targeted = over_targeted.sort_values('lift')

# Calculate wasted cost for over-targeted segments
wasted_data = []
for _, row in over_targeted.iterrows():
    seg = row['segment']
    seg_emailed = df[(df['segment'] == seg) & (df['email_sent'] == 1)]
    emails_sent = len(seg_emailed)
    cost = emails_sent * EMAIL_COST
    wasted_data.append({'segment': seg, 'emails_sent': emails_sent, 'cost': cost, 'lift': row['lift']})
over_target_df = pd.DataFrame(wasted_data)
total_wasted = over_target_df['cost'].sum()

print(f"\n=== OVER-TARGETING ===")
print(over_target_df.to_string(index=False))
print(f"Total potentially wasted: ${total_wasted:.2f}")

# ============================================================
# 4. UNDER-TARGETED HIDDEN OPPORTUNITY
# ============================================================
under_targeted = seg_comparison[seg_comparison['lift'] >= 2].copy()
if len(under_targeted) == 0:
    # If no segment has 2+pp lift, take the best ones (positive lift)
    under_targeted = seg_comparison[seg_comparison['lift'] > 0].copy()
under_targeted = under_targeted.sort_values('lift', ascending=False)

# Calculate potential revenue
potential_data = []
for _, row in under_targeted.iterrows():
    seg = row['segment']
    seg_not_emailed = df[(df['segment'] == seg) & (df['email_sent'] == 0)]
    not_emailed_count = len(seg_not_emailed)
    additional_conv_rate = row['lift'] / 100
    avg_rev = df[(df['segment'] == seg) & (df['purchased'] == 1)]['revenue'].mean()
    potential_new_purchases = not_emailed_count * additional_conv_rate
    potential_rev = potential_new_purchases * avg_rev
    email_cost = not_emailed_count * EMAIL_COST
    potential_data.append({
        'segment': seg, 'not_emailed': not_emailed_count,
        'lift': row['lift'], 'potential_purchases': round(potential_new_purchases, 1),
        'potential_revenue': round(potential_rev, 2), 'email_cost': round(email_cost, 2),
        'net_gain': round(potential_rev - email_cost, 2)
    })
under_target_df = pd.DataFrame(potential_data)
total_opportunity = under_target_df['net_gain'].sum()

print(f"\n=== UNDER-TARGETING OPPORTUNITY ===")
print(under_target_df.to_string(index=False))
print(f"Total potential net gain: ${total_opportunity:.2f}")

# ============================================================
# 5. ENGAGEMENT DROP ANALYSIS
# ============================================================
camp_drops = []
for _, row in camp_funnel.iterrows():
    camp = row['campaign']
    sent_open_drop = (1 - row['opened'] / row['sent']) * 100 if row['sent'] > 0 else 0
    open_click_drop = (1 - row['clicked'] / row['opened']) * 100 if row['opened'] > 0 else 0
    click_purchase_drop = (1 - row['purchased_from_click'] / row['clicked']) * 100 if row['clicked'] > 0 else 0
    worst_stage = max(
        [('Subject Line (Sent→Open)', sent_open_drop),
         ('Content (Open→Click)', open_click_drop),
         ('Landing Page (Click→Purchase)', click_purchase_drop)],
        key=lambda x: x[1]
    )
    camp_drops.append({
        'campaign': camp,
        'sent_open_drop': round(sent_open_drop, 1),
        'open_click_drop': round(open_click_drop, 1),
        'click_purchase_drop': round(click_purchase_drop, 1),
        'biggest_problem': worst_stage[0]
    })
camp_drops_df = pd.DataFrame(camp_drops)
print(f"\n=== ENGAGEMENT DROPS BY CAMPAIGN ===")
print(camp_drops_df.to_string(index=False))

# ============================================================
# 6. SEGMENT DEEP DIVE
# ============================================================
segment_deep = []
for seg in df['segment'].unique():
    seg_data = df[df['segment'] == seg]
    seg_comp = seg_comparison[seg_comparison['segment'] == seg].iloc[0]
    lift = seg_comp['lift']

    if lift < 2:
        action = "REDUCE / STOP emailing"
    elif lift < 5:
        action = "KEEP current level"
    else:
        action = "EMAIL MORE"

    segment_deep.append({
        'segment': seg,
        'total_users': len(seg_data),
        'email_rate': f"{seg_data['email_sent'].mean()*100:.0f}%",
        'purchase_rate': f"{seg_data['purchased'].mean()*100:.1f}%",
        'email_lift': f"{lift:.1f}pp",
        'avg_revenue': f"${seg_data[seg_data['purchased']==1]['revenue'].mean():.2f}" if seg_data['purchased'].sum() > 0 else "$0",
        'total_revenue': f"${seg_data['revenue'].sum():.2f}",
        'recommendation': action
    })
segment_deep_df = pd.DataFrame(segment_deep)
print(f"\n=== SEGMENT DEEP DIVE ===")
print(segment_deep_df.to_string(index=False))

# ============================================================
# 7. CAMPAIGN COMPARISON
# ============================================================
camp_rank = camp_funnel.copy()
camp_rank['total_users'] = df.groupby('campaign')['user_id'].count().values
camp_rank['email_purchase_rate'] = df[df['email_sent']==1].groupby('campaign')['purchased'].mean().values * 100
camp_rank['no_email_purchase_rate'] = df[df['email_sent']==0].groupby('campaign')['purchased'].mean().values * 100
camp_rank['email_lift'] = camp_rank['email_purchase_rate'] - camp_rank['no_email_purchase_rate']
camp_rank['roi'] = ((camp_rank['revenue'] - camp_rank['sent'] * EMAIL_COST) / (camp_rank['sent'] * EMAIL_COST) * 100).round(1)
camp_rank = camp_rank.sort_values('revenue', ascending=False)
print(f"\n=== CAMPAIGN RANKING ===")
print(camp_rank[['campaign', 'open_rate', 'click_rate', 'conv_rate', 'revenue', 'roi']].to_string(index=False))

# ============================================================
# 8. TARGETING MATRIX
# ============================================================
targeting_matrix = seg_comparison[['segment', 'no_email_rate', 'email_rate', 'lift']].copy()
targeting_matrix['action'] = targeting_matrix['lift'].apply(
    lambda x: 'STOP' if x < 1 else ('REDUCE' if x < 3 else ('KEEP' if x < 6 else 'INCREASE'))
)

savings = total_wasted * 0.7  # assume 70% reduction
revenue_gain = total_opportunity
net_roi_improvement = savings + revenue_gain

print(f"\n=== TARGETING MATRIX ===")
print(targeting_matrix.to_string(index=False))
print(f"\nEstimated savings from reducing over-targeting: ${savings:.2f}")
print(f"Estimated revenue gain from under-targeting: ${revenue_gain:.2f}")
print(f"Net ROI improvement: ${net_roi_improvement:.2f}")

# ============================================================
# CHARTS
# ============================================================
plt.style.use('dark_background')
COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']

# --- Chart 1: email_funnel.png ---
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.patch.set_facecolor('#1a1a2e')

# Overall funnel
ax = axes[0]
ax.set_facecolor('#16213e')
bars = ax.bar(funnel_stages, funnel_values, color=['#4ECDC4', '#45B7D1', '#FFEAA7', '#FF6B6B'], width=0.6, edgecolor='white', linewidth=0.5)
for i, (bar, val) in enumerate(zip(bars, funnel_values)):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(funnel_values)*0.02,
            f'{val:,}', ha='center', va='bottom', fontsize=13, fontweight='bold', color='white')
    if i > 0:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                f'-{funnel_dropoffs[i-1]:.1f}%', ha='center', va='center', fontsize=11, color='white', fontweight='bold')
ax.set_title('Overall Email Funnel', fontsize=16, fontweight='bold', color='white', pad=15)
ax.set_ylabel('Count', fontsize=12, color='white')
ax.tick_params(colors='white')

# Funnel by segment
ax = axes[1]
ax.set_facecolor('#16213e')
segments = seg_funnel['segment'].values
x = np.arange(len(segments))
width = 0.2
for i, (stage, color) in enumerate(zip(['sent', 'opened', 'clicked', 'purchased_from_click'], ['#4ECDC4', '#45B7D1', '#FFEAA7', '#FF6B6B'])):
    vals = seg_funnel[stage].values
    bars = ax.bar(x + i*width, vals, width, label=funnel_stages[i], color=color, edgecolor='white', linewidth=0.3)
ax.set_xticks(x + 1.5*width)
ax.set_xticklabels(segments, rotation=20, ha='right', fontsize=10, color='white')
ax.set_title('Funnel by Segment', fontsize=16, fontweight='bold', color='white', pad=15)
ax.legend(fontsize=10, loc='upper right')
ax.tick_params(colors='white')

plt.tight_layout(pad=3)
plt.savefig('output/email_funnel.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print("Saved email_funnel.png")

# --- Chart 2: email_vs_no_email.png ---
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

segs = seg_comparison['segment'].values
x = np.arange(len(segs))
width = 0.35
bars1 = ax.bar(x - width/2, seg_comparison['no_email_rate'], width, label='No Email', color='#636e72', edgecolor='white', linewidth=0.5)
bars2 = ax.bar(x + width/2, seg_comparison['email_rate'], width, label='With Email', color='#00b894', edgecolor='white', linewidth=0.5)

for i, (b1, b2) in enumerate(zip(bars1, bars2)):
    lift = seg_comparison.iloc[i]['lift']
    ax.annotate(f'+{lift:.1f}pp', xy=(x[i], max(b1.get_height(), b2.get_height()) + 1),
                ha='center', fontsize=12, fontweight='bold',
                color='#FF6B6B' if lift < 3 else '#00b894')
    ax.text(b1.get_x() + b1.get_width()/2, b1.get_height() + 0.3, f'{b1.get_height():.1f}%', ha='center', fontsize=9, color='white')
    ax.text(b2.get_x() + b2.get_width()/2, b2.get_height() + 0.3, f'{b2.get_height():.1f}%', ha='center', fontsize=9, color='white')

ax.set_xticks(x)
ax.set_xticklabels(segs, fontsize=12, color='white')
ax.set_ylabel('Purchase Rate (%)', fontsize=13, color='white')
ax.set_title('Does Email Work? Purchase Rate: Email vs No Email by Segment', fontsize=16, fontweight='bold', color='white', pad=15)
ax.legend(fontsize=12, loc='upper left')
ax.tick_params(colors='white')

plt.tight_layout(pad=3)
plt.savefig('output/email_vs_no_email.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print("Saved email_vs_no_email.png")

# --- Chart 3: over_vs_under.png ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
fig.patch.set_facecolor('#1a1a2e')

ax1.set_facecolor('#16213e')
if len(over_target_df) > 0:
    bars = ax1.barh(over_target_df['segment'], over_target_df['cost'], color='#e74c3c', edgecolor='white', linewidth=0.5)
    for bar, row in zip(bars, over_target_df.itertuples()):
        ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'${row.cost:.0f} (lift: {row.lift:.1f}pp)', va='center', fontsize=11, color='white')
ax1.set_title(f'OVER-TARGETED — Wasted ${total_wasted:.0f}', fontsize=15, fontweight='bold', color='#e74c3c', pad=15)
ax1.set_xlabel('Wasted Email Cost ($)', fontsize=12, color='white')
ax1.tick_params(colors='white')

ax2.set_facecolor('#16213e')
if len(under_target_df) > 0:
    bars = ax2.barh(under_target_df['segment'], under_target_df['net_gain'], color='#00b894', edgecolor='white', linewidth=0.5)
    for bar, row in zip(bars, under_target_df.itertuples()):
        ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'${row.net_gain:.0f} (lift: {row.lift:.1f}pp)', va='center', fontsize=11, color='white')
ax2.set_title(f'UNDER-TARGETED — Missed ${total_opportunity:.0f}', fontsize=15, fontweight='bold', color='#00b894', pad=15)
ax2.set_xlabel('Potential Net Revenue ($)', fontsize=12, color='white')
ax2.tick_params(colors='white')

plt.tight_layout(pad=3)
plt.savefig('output/over_vs_under.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print("Saved over_vs_under.png")

# --- Chart 4: campaign_ranking.png ---
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

camp_sorted = camp_rank.sort_values('revenue', ascending=True)
colors_camp = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(camp_sorted)))
bars = ax.barh(camp_sorted['campaign'], camp_sorted['revenue'], color=colors_camp, edgecolor='white', linewidth=0.5)
for bar, row in zip(bars, camp_sorted.itertuples()):
    ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
            f'${row.revenue:,.0f} | OR:{row.open_rate}% CR:{row.conv_rate}%',
            va='center', fontsize=10, color='white')
ax.set_title('Campaign Ranking by Revenue', fontsize=16, fontweight='bold', color='white', pad=15)
ax.set_xlabel('Revenue ($)', fontsize=12, color='white')
ax.tick_params(colors='white')

plt.tight_layout(pad=3)
plt.savefig('output/campaign_ranking.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print("Saved campaign_ranking.png")

# --- Chart 5: funnel_drops.png ---
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

drop_data = camp_drops_df.set_index('campaign')[['sent_open_drop', 'open_click_drop', 'click_purchase_drop']]
drop_data.columns = ['Sent→Open', 'Open→Click', 'Click→Purchase']
sns.heatmap(drop_data, annot=True, fmt='.1f', cmap='RdYlGn_r', ax=ax, linewidths=2,
            linecolor='#1a1a2e', cbar_kws={'label': 'Drop-off %'},
            annot_kws={'fontsize': 13, 'fontweight': 'bold'})
ax.set_title('Funnel Drop-off Heatmap by Campaign', fontsize=16, fontweight='bold', color='white', pad=15)
ax.tick_params(colors='white', labelsize=11)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
plt.setp(ax.get_xticklabels(), color='white')
plt.setp(ax.get_yticklabels(), color='white')

plt.tight_layout(pad=3)
plt.savefig('output/funnel_drops.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print("Saved funnel_drops.png")

# --- Chart 6: targeting_matrix.png ---
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

action_colors = {'STOP': '#e74c3c', 'REDUCE': '#e67e22', 'KEEP': '#f1c40f', 'INCREASE': '#00b894'}
action_order = ['STOP', 'REDUCE', 'KEEP', 'INCREASE']

matrix_segs = targeting_matrix['segment'].values
y_pos = np.arange(len(matrix_segs))

for i, row in targeting_matrix.iterrows():
    action = row['action']
    color = action_colors.get(action, '#95a5a6')
    action_x = action_order.index(action) if action in action_order else 0
    rect = plt.Rectangle((action_x - 0.4, y_pos[i] - 0.4), 0.8, 0.8, facecolor=color, alpha=0.8, edgecolor='white', linewidth=2)
    ax.add_patch(rect)
    ax.text(action_x, y_pos[i], f"{row['segment']}\nLift: {row['lift']:.1f}pp",
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')

ax.set_xlim(-0.5, len(action_order) - 0.5)
ax.set_ylim(-0.5, len(matrix_segs) - 0.5)
ax.set_xticks(range(len(action_order)))
ax.set_xticklabels(action_order, fontsize=13, fontweight='bold', color='white')
ax.set_yticks([])
ax.set_title('Targeting Matrix: Segment Recommendations', fontsize=16, fontweight='bold', color='white', pad=15)
ax.tick_params(colors='white')

# Legend
for act, col in action_colors.items():
    ax.bar(0, 0, color=col, label=act)
ax.legend(loc='upper right', fontsize=11)

plt.tight_layout(pad=3)
plt.savefig('output/targeting_matrix.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print("Saved targeting_matrix.png")

# ============================================================
# CAMPAIGN REPORT (Markdown)
# ============================================================
biggest_waste_seg = over_targeted.iloc[0]['segment'] if len(over_targeted) > 0 else 'N/A'
biggest_opp_seg = under_targeted.iloc[0]['segment'] if len(under_targeted) > 0 else 'N/A'

# Best and worst campaigns
best_campaign = camp_rank.iloc[0]['campaign']
worst_campaign = camp_rank.iloc[-1]['campaign']

report = f"""# Email Campaign Targeting Analysis Report

## Executive Summary

Analyzed **{len(df):,} user-campaign records** across **{df['segment'].nunique()} segments** and **{df['campaign'].nunique()} campaigns**.

**Key Finding:** Email targeting is misaligned. Over-targeting wastes **${total_wasted:.0f}** on users who buy anyway, while under-targeting misses **${total_opportunity:.0f}** in potential revenue from high-response segments. Net ROI improvement possible: **${net_roi_improvement:.0f}**.

---

## 1. Funnel Analysis

| Stage | Count | Rate |
|-------|-------|------|
| Emails Sent | {total_sent:,} | — |
| Opened | {total_opened:,} | {open_rate:.1f}% open rate |
| Clicked | {total_clicked:,} | {click_rate:.1f}% click rate |
| Purchased | {total_purchased:,} | {conversion_rate:.1f}% conversion rate |

**Drop-offs:**
- Sent → Opened: **{funnel_dropoffs[0]:.1f}%** drop
- Opened → Clicked: **{funnel_dropoffs[1]:.1f}%** drop
- Clicked → Purchased: **{funnel_dropoffs[2]:.1f}%** drop

**Biggest leak:** {"Sent → Opened (subject lines)" if funnel_dropoffs[0] == max(funnel_dropoffs) else "Opened → Clicked (content)" if funnel_dropoffs[1] == max(funnel_dropoffs) else "Clicked → Purchased (landing page)"}

### Funnel by Segment
{seg_funnel[['segment', 'open_rate', 'click_rate', 'conv_rate']].to_markdown(index=False)}

### Funnel by Campaign
{camp_funnel[['campaign', 'open_rate', 'click_rate', 'conv_rate']].to_markdown(index=False)}

---

## 2. Does Email Work? Evidence Per Segment

| Segment | No Email Purchase Rate | Email Purchase Rate | Lift |
|---------|----------------------|--------------------|----|
"""

for _, row in seg_comparison.iterrows():
    verdict = "✅ Email helps!" if row['lift'] > 3 else ("⚠️ Marginal" if row['lift'] > 1 else "❌ No impact")
    report += f"| {row['segment']} | {row['no_email_rate']:.1f}% | {row['email_rate']:.1f}% | +{row['lift']:.1f}pp {verdict} |\n"

report += f"""
**Overall:** Emailed users purchase at **{overall_email_purchase_rate:.1f}%** vs **{overall_no_email_purchase_rate:.1f}%** for non-emailed — a **+{overall_lift:.1f}pp** lift.

---

## 3. Over-Targeting: Wasted Money

These segments buy at similar rates whether emailed or not. **Every email to these users is wasted money.**

{over_target_df.to_markdown(index=False)}

**Total wasted email cost: ${total_wasted:.2f}**

> "You're paying ${total_wasted:.0f} to convince people who already decided to buy."

---

## 4. Under-Targeting: Hidden Revenue Opportunity

These segments show massive purchase rate increases when emailed. **These are your highest-ROI targets.**

{under_target_df.to_markdown(index=False)}

**Total missed opportunity: ${total_opportunity:.2f}**

---

## 5. Funnel Drop Diagnosis

{camp_drops_df.to_markdown(index=False)}

**Interpretation:**
- **High Sent→Open drop:** Subject line problem — not compelling enough
- **High Open→Click drop:** Email content/design problem — not driving action
- **High Click→Purchase drop:** Landing page/offer problem — not converting visitors

---

## 6. Segment Deep Dive

{segment_deep_df.to_markdown(index=False)}

---

## 7. Campaign Ranking

{camp_rank[['campaign', 'open_rate', 'click_rate', 'conv_rate', 'revenue', 'roi']].to_markdown(index=False)}

**Winner:** {best_campaign}
**Weakest:** {worst_campaign}

---

## 8. Targeting Matrix & Recommendations

{targeting_matrix.to_markdown(index=False)}

### Estimated Impact

| Metric | Value |
|--------|-------|
| Savings from reducing over-targeting | ${savings:.0f} |
| Revenue gain from under-targeting | ${revenue_gain:.0f} |
| **Net ROI Improvement** | **${net_roi_improvement:.0f}** |

---

## 5 Specific Actions to Improve Email ROI

1. **STOP/REDUCE emails to {biggest_waste_seg}** — they buy at nearly the same rate without emails. Save ${total_wasted*0.4:.0f}+ in email costs.

2. **INCREASE emails to {biggest_opp_seg}** — highest response to email with +{under_targeted.iloc[0]['lift']:.1f}pp lift. Potential ${under_target_df.iloc[0]['net_gain']:.0f} in additional revenue.

3. **Fix subject lines for campaigns with high Sent→Open drops** — this is the biggest funnel leak across most campaigns.

4. **Run {best_campaign} more frequently** — it's the top performer across key metrics.

5. **A/B test landing pages for campaigns with high Click→Purchase drops** — users are interested (they click) but something on the landing page isn't converting them.

---

## Final Verdict

- **Biggest Waste:** {biggest_waste_seg} — emailing users who buy anyway, costing ${total_wasted:.0f}
- **Biggest Opportunity:** {biggest_opp_seg} — high-response users not getting enough emails, missing ${total_opportunity:.0f}
- **Estimated ROI Improvement:** ${net_roi_improvement:.0f} through better targeting alone
- **The fundamental problem:** The company is over-emailing its best customers (who don't need convincing) and under-emailing persuadable segments (who respond strongly to outreach).

*Reallocate email volume from low-lift to high-lift segments for immediate ROI improvement.*
"""

with open('output/campaign_report.md', 'w', encoding='utf-8') as f:
    f.write(report)
print("Saved campaign_report.md")

# ============================================================
# DASHBOARD HTML
# ============================================================
# Prepare data for HTML
seg_chart_data = []
for _, row in seg_comparison.iterrows():
    seg_chart_data.append({
        'segment': row['segment'],
        'no_email': round(row['no_email_rate'], 1),
        'email': round(row['email_rate'], 1),
        'lift': round(row['lift'], 1)
    })

camp_table_rows = ""
for _, row in camp_rank.iterrows():
    camp_table_rows += f"""<tr>
        <td>{row['campaign']}</td>
        <td>{row['open_rate']}%</td>
        <td>{row['click_rate']}%</td>
        <td>{row['conv_rate']}%</td>
        <td>${row['revenue']:,.0f}</td>
        <td>{row['roi']}%</td>
    </tr>"""

over_cards = ""
for _, row in over_target_df.iterrows():
    over_cards += f"""<div class="card alert-red">
        <h3>⚠️ {row['segment']}</h3>
        <p>Email lift: <strong>+{row['lift']:.1f}pp</strong></p>
        <p>Emails sent: {row['emails_sent']:,}</p>
        <p class="big-number" style="color:#e74c3c">${row['cost']:.0f} wasted</p>
    </div>"""

under_cards = ""
for _, row in under_target_df.iterrows():
    under_cards += f"""<div class="card alert-green">
        <h3>💰 {row['segment']}</h3>
        <p>Email lift: <strong>+{row['lift']:.1f}pp</strong></p>
        <p>Not emailed: {row['not_emailed']:,} users</p>
        <p class="big-number" style="color:#00b894">${row['net_gain']:.0f} opportunity</p>
    </div>"""

targeting_rows = ""
for _, row in targeting_matrix.iterrows():
    color = action_colors.get(row['action'], '#95a5a6')
    targeting_rows += f"""<tr>
        <td>{row['segment']}</td>
        <td>{row['no_email_rate']:.1f}%</td>
        <td>{row['email_rate']:.1f}%</td>
        <td>+{row['lift']:.1f}pp</td>
        <td><span class="badge" style="background:{color}">{row['action']}</span></td>
    </tr>"""

# Segment insights
seg_insights = ""
for item in segment_deep:
    seg_insights += f"""<div class="card">
        <h3>{item['segment']}</h3>
        <p>Users: {item['total_users']:,} | Email Rate: {item['email_rate']}</p>
        <p>Purchase Rate: {item['purchase_rate']} | Lift: {item['email_lift']}</p>
        <p>Revenue: {item['total_revenue']}</p>
        <p><strong>{item['recommendation']}</strong></p>
    </div>"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email Campaign Targeting Analyzer</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0f0f1a; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif; padding: 20px; }}
.container {{ max-width: 1400px; margin: 0 auto; }}
h1 {{ text-align: center; font-size: 2.2em; margin-bottom: 5px; background: linear-gradient(135deg, #4ECDC4, #45B7D1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.subtitle {{ text-align: center; color: #888; margin-bottom: 30px; font-size: 1.1em; }}
.hero {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 30px; }}
.hero-card {{ background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #2a2a4a; }}
.hero-card .label {{ color: #888; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; }}
.hero-card .value {{ font-size: 2em; font-weight: 800; margin-top: 5px; }}
.hero-card .value.green {{ color: #00b894; }}
.hero-card .value.blue {{ color: #45B7D1; }}
.hero-card .value.yellow {{ color: #FFEAA7; }}
.hero-card .value.red {{ color: #e74c3c; }}
.hero-card .value.purple {{ color: #DDA0DD; }}
.section {{ margin-bottom: 35px; }}
.section h2 {{ color: #4ECDC4; font-size: 1.5em; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #2a2a4a; }}
.card {{ background: #1a1a2e; border-radius: 10px; padding: 20px; border: 1px solid #2a2a4a; }}
.cards-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; }}
.alert-red {{ border-left: 4px solid #e74c3c; }}
.alert-green {{ border-left: 4px solid #00b894; }}
.big-number {{ font-size: 1.8em; font-weight: 800; margin-top: 10px; }}
table {{ width: 100%; border-collapse: collapse; background: #1a1a2e; border-radius: 10px; overflow: hidden; }}
th {{ background: #16213e; color: #4ECDC4; padding: 12px 15px; text-align: left; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }}
td {{ padding: 10px 15px; border-bottom: 1px solid #2a2a4a; }}
tr:hover {{ background: #16213e; }}
.badge {{ padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 700; color: white; display: inline-block; }}
.funnel-bar {{ display: flex; align-items: center; margin: 8px 0; }}
.funnel-bar .bar {{ height: 40px; border-radius: 6px; display: flex; align-items: center; padding: 0 15px; font-weight: 700; color: white; min-width: 60px; transition: width 0.5s; }}
.funnel-bar .label-text {{ width: 100px; text-align: right; margin-right: 15px; font-weight: 600; }}
.funnel-bar .drop {{ margin-left: 15px; color: #e74c3c; font-weight: 700; }}
.chart-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 10px; margin-top: 15px; }}
.bar-group {{ background: #16213e; border-radius: 8px; padding: 15px; text-align: center; }}
.bar-pair {{ display: flex; justify-content: center; gap: 8px; align-items: flex-end; height: 150px; margin: 10px 0; }}
.bar-single {{ width: 40px; border-radius: 4px 4px 0 0; position: relative; display: flex; align-items: flex-start; justify-content: center; }}
.bar-single span {{ position: absolute; top: -20px; font-size: 0.8em; font-weight: 700; }}
.lift-badge {{ font-size: 1.1em; font-weight: 800; }}
.insight-card {{ background: linear-gradient(135deg, #1a1a2e, #0f3460); border-radius: 10px; padding: 20px; border-left: 4px solid #4ECDC4; margin-bottom: 10px; }}
.insight-card h3 {{ color: #FFEAA7; margin-bottom: 8px; }}
.roi-box {{ background: linear-gradient(135deg, #0f3460, #1a1a2e); border: 2px solid #00b894; border-radius: 12px; padding: 25px; text-align: center; margin: 20px 0; }}
.roi-box .roi-value {{ font-size: 3em; font-weight: 900; color: #00b894; }}
.footer {{ text-align: center; color: #555; padding: 20px; font-size: 0.9em; }}
</style>
</head>
<body>
<div class="container">

<h1>📧 Email Campaign Targeting Analyzer</h1>
<p class="subtitle">Analyzing {len(df):,} user-campaign records across {df['segment'].nunique()} segments and {df['campaign'].nunique()} campaigns</p>

<!-- Hero Metrics -->
<div class="hero">
    <div class="hero-card"><div class="label">Emails Sent</div><div class="value blue">{total_sent:,}</div></div>
    <div class="hero-card"><div class="label">Open Rate</div><div class="value green">{open_rate:.1f}%</div></div>
    <div class="hero-card"><div class="label">Click Rate</div><div class="value yellow">{click_rate:.1f}%</div></div>
    <div class="hero-card"><div class="label">Conversion Rate</div><div class="value purple">{conversion_rate:.1f}%</div></div>
    <div class="hero-card"><div class="label">Total Revenue</div><div class="value green">${total_revenue:,.0f}</div></div>
    <div class="hero-card"><div class="label">Wasted Email Cost</div><div class="value red">${total_wasted:,.0f}</div></div>
</div>

<!-- Funnel -->
<div class="section">
<h2>📊 Email Funnel</h2>
<div class="card">
    <div class="funnel-bar">
        <span class="label-text">Sent</span>
        <div class="bar" style="width:100%; background:#4ECDC4;">{total_sent:,}</div>
    </div>
    <div class="funnel-bar">
        <span class="label-text">Opened</span>
        <div class="bar" style="width:{total_opened/total_sent*100:.0f}%; background:#45B7D1;">{total_opened:,}</div>
        <span class="drop">▼ {funnel_dropoffs[0]:.1f}% drop</span>
    </div>
    <div class="funnel-bar">
        <span class="label-text">Clicked</span>
        <div class="bar" style="width:{total_clicked/total_sent*100:.0f}%; background:#FFEAA7; color:#333;">{total_clicked:,}</div>
        <span class="drop">▼ {funnel_dropoffs[1]:.1f}% drop</span>
    </div>
    <div class="funnel-bar">
        <span class="label-text">Purchased</span>
        <div class="bar" style="width:{max(total_purchased/total_sent*100, 3):.0f}%; background:#FF6B6B;">{total_purchased:,}</div>
        <span class="drop">▼ {funnel_dropoffs[2]:.1f}% drop</span>
    </div>
</div>
</div>

<!-- Email vs No Email -->
<div class="section">
<h2>🎯 Does Email Work? Purchase Rate by Segment</h2>
<div class="chart-container">
"""

max_rate = max(seg_comparison['email_rate'].max(), seg_comparison['no_email_rate'].max())
for item in seg_chart_data:
    h_no = item['no_email'] / max_rate * 130
    h_email = item['email'] / max_rate * 130
    lift_color = '#00b894' if item['lift'] > 3 else '#e74c3c'
    html += f"""<div class="bar-group">
        <div style="font-weight:700;margin-bottom:5px;">{item['segment']}</div>
        <div class="bar-pair">
            <div class="bar-single" style="height:{h_no}px; background:#636e72;"><span>{item['no_email']}%</span></div>
            <div class="bar-single" style="height:{h_email}px; background:#00b894;"><span>{item['email']}%</span></div>
        </div>
        <div style="font-size:0.8em;color:#888;">No Email &nbsp; | &nbsp; Email</div>
        <div class="lift-badge" style="color:{lift_color}; margin-top:5px;">+{item['lift']}pp lift</div>
    </div>"""

html += f"""</div>
</div>

<!-- Over-Targeting -->
<div class="section">
<h2>🔴 Over-Targeting Alert — Wasted Money</h2>
<p style="color:#888;margin-bottom:15px;">These segments buy at similar rates with or without email. You're paying to convince people who already decided to buy.</p>
<div class="cards-grid">{over_cards}</div>
</div>

<!-- Under-Targeting -->
<div class="section">
<h2>🟢 Under-Targeting Opportunity — Hidden Revenue</h2>
<p style="color:#888;margin-bottom:15px;">These segments respond strongly to email. Emailing them more = highest ROI opportunity.</p>
<div class="cards-grid">{under_cards}</div>
</div>

<!-- Campaign Ranking -->
<div class="section">
<h2>🏆 Campaign Ranking</h2>
<table>
    <tr><th>Campaign</th><th>Open Rate</th><th>Click Rate</th><th>Conv Rate</th><th>Revenue</th><th>ROI</th></tr>
    {camp_table_rows}
</table>
</div>

<!-- Targeting Matrix -->
<div class="section">
<h2>🎯 Targeting Matrix — Who to Email More / Less / Stop</h2>
<table>
    <tr><th>Segment</th><th>No Email Rate</th><th>Email Rate</th><th>Lift</th><th>Action</th></tr>
    {targeting_rows}
</table>
</div>

<!-- Segment Deep Dive -->
<div class="section">
<h2>🔍 Segment Deep Dive</h2>
<div class="cards-grid">{seg_insights}</div>
</div>

<!-- ROI Improvement -->
<div class="section">
<h2>💰 ROI Improvement Estimate</h2>
<div class="roi-box">
    <div style="color:#888;margin-bottom:5px;">ESTIMATED NET ROI IMPROVEMENT</div>
    <div class="roi-value">${net_roi_improvement:,.0f}</div>
    <div style="margin-top:15px; display:flex; justify-content:center; gap:40px;">
        <div><span style="color:#e74c3c;font-size:1.3em;font-weight:700;">${savings:,.0f}</span><br><span style="color:#888;">Savings (reduce over-targeting)</span></div>
        <div><span style="color:#00b894;font-size:1.3em;font-weight:700;">${revenue_gain:,.0f}</span><br><span style="color:#888;">Revenue gain (email under-targeted)</span></div>
    </div>
</div>
</div>

<!-- Key Insights -->
<div class="section">
<h2>💡 Key Insights</h2>
<div class="insight-card">
    <h3>Biggest Waste</h3>
    <p>{biggest_waste_seg} segment — emailing users who buy anyway. Costing <strong>${total_wasted:.0f}</strong> with minimal impact on purchase rates.</p>
</div>
<div class="insight-card">
    <h3>Biggest Opportunity</h3>
    <p>{biggest_opp_seg} segment — these users respond strongly to email (+{under_targeted.iloc[0]['lift']:.1f}pp lift) but many aren't being emailed. Missing <strong>${total_opportunity:.0f}</strong> in potential revenue.</p>
</div>
<div class="insight-card">
    <h3>The Core Problem</h3>
    <p>The company is over-emailing its best customers (who don't need convincing) and under-emailing persuadable segments (who respond strongly). Reallocating email volume = immediate ROI improvement.</p>
</div>
</div>

<div class="footer">
    Email Campaign Targeting Analysis | Generated {pd.Timestamp.now().strftime('%Y-%m-%d')} | {len(df):,} records analyzed
</div>

</div>
</body>
</html>"""

with open('output/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved dashboard.html")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "="*60)
print("ANALYSIS COMPLETE — ALL 8 OUTPUT FILES CREATED")
print("="*60)
print(f"\n🔴 BIGGEST WASTE: {biggest_waste_seg}")
print(f"   Emailing users who buy anyway — ${total_wasted:.0f} wasted")
print(f"\n🟢 BIGGEST OPPORTUNITY: {biggest_opp_seg}")
print(f"   High-response users not getting emails — ${total_opportunity:.0f} missed")
print(f"\n💰 ESTIMATED ROI IMPROVEMENT: ${net_roi_improvement:.0f}")
print(f"   Savings: ${savings:.0f} + Revenue gain: ${revenue_gain:.0f}")
