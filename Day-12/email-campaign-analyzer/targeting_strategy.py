import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/email_campaigns.csv')
EMAIL_COST = 0.05

# ============================================================
# DEEP TARGETING ANALYSIS
# ============================================================

# 1. Segment x Campaign lift matrix
results = []
for seg in df['segment'].unique():
    for camp in df['campaign'].unique():
        subset = df[(df['segment'] == seg) & (df['campaign'] == camp)]
        em = subset[subset['email_sent'] == 1]
        no = subset[subset['email_sent'] == 0]
        if len(em) > 5 and len(no) > 5:
            em_rate = em['purchased'].mean() * 100
            no_rate = no['purchased'].mean() * 100
            lift = em_rate - no_rate
            em_rev = em[em['purchased'] == 1]['revenue'].mean() if em['purchased'].sum() > 0 else 0
            no_rev = no[no['purchased'] == 1]['revenue'].mean() if no['purchased'].sum() > 0 else 0
            results.append({
                'segment': seg, 'campaign': camp,
                'emailed_users': len(em), 'not_emailed_users': len(no),
                'email_purchase_rate': round(em_rate, 2),
                'no_email_purchase_rate': round(no_rate, 2),
                'lift_pp': round(lift, 2),
                'avg_email_revenue': round(em_rev, 2),
                'avg_no_email_revenue': round(no_rev, 2),
                'email_cost': round(len(em) * EMAIL_COST, 2)
            })

matrix = pd.DataFrame(results)

# 2. Segment-level summary
seg_summary = []
for seg in df['segment'].unique():
    seg_data = df[df['segment'] == seg]
    em = seg_data[seg_data['email_sent'] == 1]
    no = seg_data[seg_data['email_sent'] == 0]
    em_rate = em['purchased'].mean() * 100
    no_rate = no['purchased'].mean() * 100
    lift = em_rate - no_rate

    total_emails = len(em)
    total_cost = total_emails * EMAIL_COST

    # Revenue from emailed purchasers
    em_revenue = em['revenue'].sum()
    no_revenue = no['revenue'].sum()
    avg_order = seg_data[seg_data['purchased'] == 1]['revenue'].mean() if seg_data['purchased'].sum() > 0 else 0

    # If we STOP emailing: these users would revert to no_email purchase rate
    # Lost purchases = (em_rate - no_rate)/100 * total_emails (if positive)
    # Gained savings = total_cost
    if lift <= 0:
        # Email hurts or does nothing - STOP
        saved_cost = total_cost
        # No revenue lost (they buy more without email)
        expected_extra_purchases = abs(lift) / 100 * total_emails
        revenue_gained = expected_extra_purchases * avg_order
        action = 'STOP'
        net_impact = saved_cost + revenue_gained
    elif lift < 2:
        # Marginal - REDUCE by 50%
        saved_cost = total_cost * 0.5
        lost_purchases = lift / 100 * total_emails * 0.5
        revenue_lost = lost_purchases * avg_order
        action = 'REDUCE'
        net_impact = saved_cost - revenue_lost
    else:
        # Email works - INCREASE
        not_emailed_count = len(no)
        new_purchases = lift / 100 * not_emailed_count
        new_revenue = new_purchases * avg_order
        new_cost = not_emailed_count * EMAIL_COST
        action = 'INCREASE'
        net_impact = new_revenue - new_cost
        saved_cost = 0

    # Best and worst campaigns for this segment
    seg_matrix = matrix[matrix['segment'] == seg].sort_values('lift_pp', ascending=False)
    best_camp = seg_matrix.iloc[0] if len(seg_matrix) > 0 else None
    worst_camp = seg_matrix.iloc[-1] if len(seg_matrix) > 0 else None

    seg_summary.append({
        'segment': seg,
        'total_users': len(seg_data),
        'emailed': total_emails,
        'not_emailed': len(no),
        'email_rate_pct': round(total_emails / len(seg_data) * 100, 1),
        'em_purchase_rate': round(em_rate, 1),
        'no_em_purchase_rate': round(no_rate, 1),
        'lift_pp': round(lift, 1),
        'current_email_cost': round(total_cost, 2),
        'avg_order': round(avg_order, 2),
        'total_revenue': round(seg_data['revenue'].sum(), 2),
        'action': action,
        'net_impact': round(net_impact, 2),
        'saved_cost': round(saved_cost, 2),
        'best_campaign': best_camp['campaign'] if best_camp is not None else 'N/A',
        'best_camp_lift': best_camp['lift_pp'] if best_camp is not None else 0,
        'worst_campaign': worst_camp['campaign'] if worst_camp is not None else 'N/A',
        'worst_camp_lift': worst_camp['lift_pp'] if worst_camp is not None else 0,
    })

summary_df = pd.DataFrame(seg_summary)

# 3. Campaign-level targeting recommendations
camp_summary = []
for camp in df['campaign'].unique():
    camp_data = df[df['campaign'] == camp]
    em = camp_data[camp_data['email_sent'] == 1]
    no = camp_data[camp_data['email_sent'] == 0]
    em_rate = em['purchased'].mean() * 100
    no_rate = no['purchased'].mean() * 100
    lift = em_rate - no_rate

    # Which segments respond best to this campaign?
    camp_matrix = matrix[matrix['campaign'] == camp].sort_values('lift_pp', ascending=False)

    camp_summary.append({
        'campaign': camp,
        'lift_pp': round(lift, 1),
        'total_emails': len(em),
        'cost': round(len(em) * EMAIL_COST, 2),
        'revenue': round(camp_data['revenue'].sum(), 2),
        'best_segment': camp_matrix.iloc[0]['segment'] if len(camp_matrix) > 0 else 'N/A',
        'best_seg_lift': camp_matrix.iloc[0]['lift_pp'] if len(camp_matrix) > 0 else 0,
        'worst_segment': camp_matrix.iloc[-1]['segment'] if len(camp_matrix) > 0 else 'N/A',
        'worst_seg_lift': camp_matrix.iloc[-1]['lift_pp'] if len(camp_matrix) > 0 else 0,
    })

camp_df = pd.DataFrame(camp_summary)

# Print findings
print("="*70)
print("TARGETING STRATEGY ANALYSIS")
print("="*70)

for _, row in summary_df.iterrows():
    print(f"\n--- {row['segment']} ---")
    print(f"  Action: {row['action']}")
    print(f"  Email lift: {row['lift_pp']:+.1f}pp | Email rate: {row['email_rate_pct']}%")
    print(f"  Purchase: {row['em_purchase_rate']}% (emailed) vs {row['no_em_purchase_rate']}% (not emailed)")
    print(f"  Current email cost: ${row['current_email_cost']:.2f}")
    print(f"  Net impact of strategy: ${row['net_impact']:+.2f}")
    print(f"  Best campaign: {row['best_campaign']} ({row['best_camp_lift']:+.1f}pp)")
    print(f"  Worst campaign: {row['worst_campaign']} ({row['worst_camp_lift']:+.1f}pp)")

total_net = summary_df['net_impact'].sum()
total_saved = summary_df['saved_cost'].sum()
print(f"\n{'='*70}")
print(f"TOTAL NET IMPACT: ${total_net:+,.2f}")
print(f"TOTAL EMAIL COST SAVED: ${total_saved:+,.2f}")
print(f"{'='*70}")

# ============================================================
# CHART: targeting_strategy.png (multi-panel)
# ============================================================
fig = plt.figure(figsize=(24, 28))
fig.patch.set_facecolor('#0f0f1a')
gs = GridSpec(4, 2, figure=fig, hspace=0.35, wspace=0.3)

action_colors = {'STOP': '#e74c3c', 'REDUCE': '#e67e22', 'KEEP': '#f1c40f', 'INCREASE': '#00b894'}
seg_colors = {
    'VIP': '#9b59b6', 'Frequent Buyer': '#3498db', 'Regular': '#1abc9c',
    'New User': '#f39c12', 'Inactive': '#e74c3c'
}

# --- Panel 1: Strategy Overview (top-left) ---
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#1a1a2e')

sorted_sum = summary_df.sort_values('lift_pp')
y = np.arange(len(sorted_sum))
colors = [action_colors[a] for a in sorted_sum['action']]

bars = ax1.barh(y, sorted_sum['lift_pp'], color=colors, edgecolor='white', linewidth=0.5, height=0.6)
ax1.axvline(x=0, color='white', linewidth=1, linestyle='--', alpha=0.5)

for i, (_, row) in enumerate(sorted_sum.iterrows()):
    label = f"  {row['action']} | ${row['net_impact']:+,.0f}"
    x_pos = row['lift_pp'] + (0.3 if row['lift_pp'] >= 0 else -0.3)
    ha = 'left' if row['lift_pp'] >= 0 else 'right'
    ax1.text(x_pos, i, label, va='center', ha=ha, fontsize=11, fontweight='bold', color='white')

ax1.set_yticks(y)
ax1.set_yticklabels(sorted_sum['segment'], fontsize=12, fontweight='bold', color='white')
ax1.set_xlabel('Email Lift (percentage points)', fontsize=12, color='white')
ax1.set_title('STRATEGY: Email Lift by Segment\n& Recommended Action', fontsize=14, fontweight='bold', color='#4ECDC4', pad=15)
ax1.tick_params(colors='white')
for spine in ax1.spines.values():
    spine.set_color('#2a2a4a')

# --- Panel 2: Money Impact Waterfall (top-right) ---
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#1a1a2e')

sorted_impact = summary_df.sort_values('net_impact', ascending=False)
segs = sorted_impact['segment'].values
impacts = sorted_impact['net_impact'].values
bar_colors = ['#00b894' if v > 0 else '#e74c3c' for v in impacts]

bars = ax2.bar(range(len(segs)), impacts, color=bar_colors, edgecolor='white', linewidth=0.5, width=0.6)
for i, (bar, val) in enumerate(zip(bars, impacts)):
    y_pos = bar.get_height() + (5 if val >= 0 else -15)
    ax2.text(bar.get_x() + bar.get_width()/2, y_pos, f'${val:+,.0f}',
             ha='center', fontsize=12, fontweight='bold', color='white')

# Total bar
ax2.bar(len(segs), total_net, color='#4ECDC4', edgecolor='white', linewidth=1.5, width=0.6)
ax2.text(len(segs), total_net + 10, f'${total_net:+,.0f}\nTOTAL', ha='center', fontsize=13, fontweight='bold', color='#4ECDC4')

ax2.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)
ax2.set_xticks(range(len(segs) + 1))
ax2.set_xticklabels(list(segs) + ['TOTAL'], rotation=25, ha='right', fontsize=10, color='white')
ax2.set_ylabel('Net Impact ($)', fontsize=12, color='white')
ax2.set_title('MONEY IMPACT: Net Gain Per Segment\nFrom Strategy Change', fontsize=14, fontweight='bold', color='#4ECDC4', pad=15)
ax2.tick_params(colors='white')
for spine in ax2.spines.values():
    spine.set_color('#2a2a4a')

# --- Panel 3: Segment x Campaign Heatmap (middle-left spanning full width) ---
ax3 = fig.add_subplot(gs[1, :])
ax3.set_facecolor('#1a1a2e')

pivot = matrix.pivot(index='segment', columns='campaign', values='lift_pp')
# Sort segments by overall lift
seg_order = summary_df.sort_values('lift_pp')['segment'].values
pivot = pivot.reindex(seg_order)

import seaborn as sns
hm = sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', center=0, ax=ax3,
                  linewidths=2, linecolor='#1a1a2e', cbar_kws={'label': 'Lift (pp)', 'shrink': 0.6},
                  annot_kws={'fontsize': 12, 'fontweight': 'bold'}, vmin=-20, vmax=20)
ax3.set_title('TARGETING HEATMAP: Email Lift by Segment x Campaign\n(Green = email helps, Red = email hurts)',
              fontsize=14, fontweight='bold', color='#4ECDC4', pad=15)
ax3.tick_params(colors='white', labelsize=11)
plt.setp(ax3.get_xticklabels(), color='white', rotation=25, ha='right')
plt.setp(ax3.get_yticklabels(), color='white', rotation=0)
cbar = hm.collections[0].colorbar
cbar.ax.tick_params(colors='white')
cbar.set_label('Lift (pp)', color='white')

# --- Panel 4: Current vs Optimal Email Distribution (bottom-left) ---
ax4 = fig.add_subplot(gs[2, 0])
ax4.set_facecolor('#1a1a2e')

segs_sorted = summary_df.sort_values('lift_pp', ascending=False)
current_emails = segs_sorted['emailed'].values
total_pool = segs_sorted['total_users'].values

# Optimal: email proportional to lift (only positive lift)
optimal_emails = []
for _, row in segs_sorted.iterrows():
    if row['action'] == 'STOP':
        optimal_emails.append(0)
    elif row['action'] == 'REDUCE':
        optimal_emails.append(int(row['emailed'] * 0.5))
    elif row['action'] == 'INCREASE':
        optimal_emails.append(row['total_users'])
    else:
        optimal_emails.append(row['emailed'])

y = np.arange(len(segs_sorted))
width = 0.35
ax4.barh(y + width/2, current_emails, width, label='Current Emails', color='#636e72', edgecolor='white', linewidth=0.5)
ax4.barh(y - width/2, optimal_emails, width, label='Optimal Emails', color='#00b894', edgecolor='white', linewidth=0.5)

for i, (curr, opt) in enumerate(zip(current_emails, optimal_emails)):
    diff = opt - curr
    color = '#00b894' if diff >= 0 else '#e74c3c'
    ax4.text(max(curr, opt) + 20, i, f'{diff:+,}', va='center', fontsize=11, fontweight='bold', color=color)

ax4.set_yticks(y)
ax4.set_yticklabels(segs_sorted['segment'], fontsize=11, fontweight='bold', color='white')
ax4.set_xlabel('Emails Sent', fontsize=12, color='white')
ax4.set_title('REALLOCATION: Current vs Optimal\nEmail Volume by Segment', fontsize=14, fontweight='bold', color='#4ECDC4', pad=15)
ax4.legend(fontsize=10, loc='lower right')
ax4.tick_params(colors='white')
for spine in ax4.spines.values():
    spine.set_color('#2a2a4a')

# --- Panel 5: Cost Breakdown (bottom-right) ---
ax5 = fig.add_subplot(gs[2, 1])
ax5.set_facecolor('#1a1a2e')

# Current cost vs optimal cost
current_costs = segs_sorted['current_email_cost'].values
optimal_costs = [c * EMAIL_COST for c in optimal_emails]
seg_names = segs_sorted['segment'].values

x = np.arange(len(seg_names))
bars1 = ax5.bar(x - 0.2, current_costs, 0.35, label='Current Cost', color='#e74c3c', edgecolor='white', linewidth=0.5)
bars2 = ax5.bar(x + 0.2, optimal_costs, 0.35, label='Optimal Cost', color='#00b894', edgecolor='white', linewidth=0.5)

for i, (c, o) in enumerate(zip(current_costs, optimal_costs)):
    saved = c - o
    if saved > 0:
        ax5.text(i, max(c, o) + 2, f'-${saved:.0f}', ha='center', fontsize=10, fontweight='bold', color='#00b894')

current_total = sum(current_costs)
optimal_total = sum(optimal_costs)
ax5.text(0.98, 0.95, f'Current total: ${current_total:.0f}\nOptimal total: ${optimal_total:.0f}\nSaved: ${current_total - optimal_total:.0f}',
         transform=ax5.transAxes, ha='right', va='top', fontsize=11, color='white',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#16213e', edgecolor='#4ECDC4'))

ax5.set_xticks(x)
ax5.set_xticklabels(seg_names, rotation=25, ha='right', fontsize=10, color='white')
ax5.set_ylabel('Email Cost ($)', fontsize=12, color='white')
ax5.set_title('COST SAVINGS: Current vs Optimal\nEmail Spend by Segment', fontsize=14, fontweight='bold', color='#4ECDC4', pad=15)
ax5.legend(fontsize=10, loc='upper left')
ax5.tick_params(colors='white')
for spine in ax5.spines.values():
    spine.set_color('#2a2a4a')

# --- Panel 6: Action Summary Cards (bottom) ---
ax6 = fig.add_subplot(gs[3, :])
ax6.set_facecolor('#0f0f1a')
ax6.axis('off')

# Build the action cards as a table-like layout
card_y = 0.85
ax6.text(0.5, 0.98, 'TARGETING PLAYBOOK: SEGMENT-BY-SEGMENT ACTIONS',
         transform=ax6.transAxes, ha='center', va='top', fontsize=18, fontweight='bold', color='#4ECDC4')

for i, (_, row) in enumerate(summary_df.sort_values('lift_pp').iterrows()):
    x_start = 0.02 + (i % 5) * 0.196
    y_start = 0.75 if i < 5 else 0.35

    color = action_colors[row['action']]
    rect = mpatches.FancyBboxPatch((x_start, y_start), 0.18, 0.2,
                                    boxstyle="round,pad=0.01",
                                    facecolor='#1a1a2e', edgecolor=color, linewidth=2.5,
                                    transform=ax6.transAxes)
    ax6.add_patch(rect)

    cx = x_start + 0.09
    ax6.text(cx, y_start + 0.18, row['segment'], transform=ax6.transAxes,
             ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    ax6.text(cx, y_start + 0.14, row['action'], transform=ax6.transAxes,
             ha='center', va='center', fontsize=13, fontweight='900', color=color)
    ax6.text(cx, y_start + 0.10, f"Lift: {row['lift_pp']:+.1f}pp", transform=ax6.transAxes,
             ha='center', va='center', fontsize=9, color='#aaa')
    ax6.text(cx, y_start + 0.06, f"Impact: ${row['net_impact']:+,.0f}", transform=ax6.transAxes,
             ha='center', va='center', fontsize=10, fontweight='bold',
             color='#00b894' if row['net_impact'] > 0 else '#e74c3c')
    ax6.text(cx, y_start + 0.02, f"Best: {row['best_campaign']}", transform=ax6.transAxes,
             ha='center', va='center', fontsize=8, color='#888')

# Bottom line totals
ax6.text(0.5, 0.12, f'TOTAL NET IMPACT: ${total_net:+,.0f}', transform=ax6.transAxes,
         ha='center', fontsize=22, fontweight='900', color='#00b894' if total_net > 0 else '#e74c3c')
ax6.text(0.5, 0.04, f'Email cost saved: ${total_saved:,.0f}  |  '
         f'Current spend: ${current_total:,.0f}  |  Optimal spend: ${optimal_total:,.0f}  |  '
         f'Emails eliminated: {sum(current_emails) - sum(optimal_emails):,}',
         transform=ax6.transAxes, ha='center', fontsize=12, color='#aaa')

plt.savefig('output/targeting_strategy.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("Saved targeting_strategy.png")

# ============================================================
# HTML: targeting_strategy.html
# ============================================================

# Build segment cards HTML
segment_cards_html = ""
for _, row in summary_df.sort_values('net_impact', ascending=False).iterrows():
    color = action_colors[row['action']]
    impact_color = '#00b894' if row['net_impact'] > 0 else '#e74c3c'
    arrow = "&#9650;" if row['net_impact'] > 0 else "&#9660;"

    # Reasoning
    if row['action'] == 'STOP':
        reason = f"Users buy at {row['no_em_purchase_rate']}% WITHOUT email vs {row['em_purchase_rate']}% WITH email. Email actually <strong>reduces</strong> purchases by {abs(row['lift_pp'])}pp. Stop spending ${row['current_email_cost']:.0f} on these emails."
    elif row['action'] == 'REDUCE':
        reason = f"Marginal +{row['lift_pp']}pp lift doesn't justify full email volume. Cut 50% to save ${row['saved_cost']:.0f} while retaining most benefit."
    else:
        reason = f"Strong +{row['lift_pp']}pp lift. {row['not_emailed']:,} users not receiving emails. Email them all for additional revenue."

    segment_cards_html += f"""
    <div class="strategy-card" style="border-left: 4px solid {color};">
        <div class="card-header">
            <div>
                <h3>{row['segment']}</h3>
                <span class="badge" style="background:{color};">{row['action']} EMAILING</span>
            </div>
            <div class="impact-number" style="color:{impact_color};">{arrow} ${row['net_impact']:+,.0f}</div>
        </div>
        <div class="card-body">
            <div class="metrics-row">
                <div class="metric">
                    <div class="metric-label">With Email</div>
                    <div class="metric-value">{row['em_purchase_rate']}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Without Email</div>
                    <div class="metric-value">{row['no_em_purchase_rate']}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Lift</div>
                    <div class="metric-value" style="color:{impact_color}">{row['lift_pp']:+.1f}pp</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Emails Sent</div>
                    <div class="metric-value">{row['emailed']:,}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Email Cost</div>
                    <div class="metric-value">${row['current_email_cost']:.0f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Avg Order</div>
                    <div class="metric-value">${row['avg_order']:.0f}</div>
                </div>
            </div>
            <div class="reason">{reason}</div>
            <div class="camp-rec">
                <span style="color:#00b894;">Best campaign: <strong>{row['best_campaign']}</strong> ({row['best_camp_lift']:+.1f}pp)</span> &nbsp;|&nbsp;
                <span style="color:#e74c3c;">Worst campaign: <strong>{row['worst_campaign']}</strong> ({row['worst_camp_lift']:+.1f}pp)</span>
            </div>
        </div>
    </div>"""

# Heatmap HTML table
heatmap_rows = ""
pivot = matrix.pivot(index='segment', columns='campaign', values='lift_pp')
seg_order = summary_df.sort_values('lift_pp')['segment'].values
pivot = pivot.reindex(seg_order)

for seg in seg_order:
    heatmap_rows += f"<tr><td class='seg-label'>{seg}</td>"
    for camp in pivot.columns:
        val = pivot.loc[seg, camp]
        if pd.isna(val):
            heatmap_rows += "<td>-</td>"
        else:
            # Color scale: red for negative, green for positive
            if val > 5:
                bg = '#00b894'; txt = 'white'
            elif val > 0:
                bg = '#1a6e5a'; txt = 'white'
            elif val > -5:
                bg = '#8b3a3a'; txt = 'white'
            else:
                bg = '#e74c3c'; txt = 'white'
            heatmap_rows += f"<td style='background:{bg};color:{txt};font-weight:700;'>{val:+.1f}</td>"
    # Action column
    action = summary_df[summary_df['segment'] == seg].iloc[0]['action']
    ac = action_colors[action]
    heatmap_rows += f"<td><span class='badge' style='background:{ac};'>{action}</span></td></tr>"

camp_headers = "".join([f"<th>{c}</th>" for c in pivot.columns])

# Campaign strategy rows
camp_strat_rows = ""
for _, row in camp_df.sort_values('lift_pp', ascending=False).iterrows():
    lift_color = '#00b894' if row['lift_pp'] > 0 else '#e74c3c'
    camp_strat_rows += f"""<tr>
        <td>{row['campaign']}</td>
        <td style="color:{lift_color};font-weight:700;">{row['lift_pp']:+.1f}pp</td>
        <td>{row['total_emails']:,}</td>
        <td>${row['cost']:.0f}</td>
        <td>${row['revenue']:,.0f}</td>
        <td style="color:#00b894;">{row['best_segment']} ({row['best_seg_lift']:+.1f}pp)</td>
        <td style="color:#e74c3c;">{row['worst_segment']} ({row['worst_seg_lift']:+.1f}pp)</td>
    </tr>"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email Targeting Strategy</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0f0f1a; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif; padding: 20px; }}
.container {{ max-width: 1400px; margin: 0 auto; }}
h1 {{ text-align: center; font-size: 2.4em; margin-bottom: 5px; background: linear-gradient(135deg, #4ECDC4, #45B7D1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.subtitle {{ text-align: center; color: #888; margin-bottom: 30px; font-size: 1.1em; }}

.hero {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 35px; }}
.hero-card {{ background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #2a2a4a; }}
.hero-card .label {{ color: #888; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; }}
.hero-card .value {{ font-size: 2.2em; font-weight: 900; margin-top: 5px; }}

.section {{ margin-bottom: 40px; }}
.section h2 {{ color: #4ECDC4; font-size: 1.5em; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #2a2a4a; }}

.strategy-card {{ background: #1a1a2e; border-radius: 10px; padding: 20px; margin-bottom: 15px; }}
.card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
.card-header h3 {{ font-size: 1.3em; color: white; }}
.impact-number {{ font-size: 1.8em; font-weight: 900; }}
.card-body {{ }}
.metrics-row {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 15px; }}
.metric {{ background: #16213e; border-radius: 8px; padding: 10px; text-align: center; }}
.metric-label {{ color: #888; font-size: 0.8em; text-transform: uppercase; }}
.metric-value {{ font-size: 1.2em; font-weight: 700; margin-top: 4px; }}
.reason {{ background: #16213e; border-radius: 8px; padding: 12px; margin-bottom: 10px; line-height: 1.5; }}
.camp-rec {{ font-size: 0.9em; color: #aaa; }}
.badge {{ padding: 4px 14px; border-radius: 20px; font-size: 0.85em; font-weight: 700; color: white; display: inline-block; }}

table {{ width: 100%; border-collapse: collapse; background: #1a1a2e; border-radius: 10px; overflow: hidden; }}
th {{ background: #16213e; color: #4ECDC4; padding: 12px; text-align: center; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; }}
td {{ padding: 10px 12px; border-bottom: 1px solid #2a2a4a; text-align: center; }}
.seg-label {{ font-weight: 700; text-align: left !important; }}
tr:hover {{ background: #16213e; }}

.verdict {{ background: linear-gradient(135deg, #0f3460, #1a1a2e); border: 2px solid #4ECDC4; border-radius: 12px; padding: 30px; text-align: center; margin: 20px 0; }}
.verdict h2 {{ color: #4ECDC4; margin-bottom: 20px; font-size: 1.8em; }}
.verdict-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }}
.verdict-item .num {{ font-size: 2.5em; font-weight: 900; }}
.verdict-item .desc {{ color: #aaa; margin-top: 5px; }}

.playbook {{ background: #1a1a2e; border-radius: 10px; padding: 25px; }}
.playbook-item {{ padding: 12px 0; border-bottom: 1px solid #2a2a4a; display: flex; align-items: flex-start; gap: 15px; }}
.playbook-item:last-child {{ border-bottom: none; }}
.step-num {{ background: #4ECDC4; color: #0f0f1a; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; flex-shrink: 0; }}
.footer {{ text-align: center; color: #555; padding: 20px; font-size: 0.9em; }}
</style>
</head>
<body>
<div class="container">

<h1>Email Targeting Strategy</h1>
<p class="subtitle">Who to email, who to stop emailing, and the money impact</p>

<!-- Hero -->
<div class="hero">
    <div class="hero-card">
        <div class="label">Total Net Impact</div>
        <div class="value" style="color:{'#00b894' if total_net > 0 else '#e74c3c'};">${total_net:+,.0f}</div>
    </div>
    <div class="hero-card">
        <div class="label">Email Cost Saved</div>
        <div class="value" style="color:#00b894;">${total_saved:,.0f}</div>
    </div>
    <div class="hero-card">
        <div class="label">Current Email Spend</div>
        <div class="value" style="color:#e74c3c;">${current_total:,.0f}</div>
    </div>
    <div class="hero-card">
        <div class="label">Emails to Eliminate</div>
        <div class="value" style="color:#FFEAA7;">{sum(current_emails) - sum(optimal_emails):,}</div>
    </div>
</div>

<!-- Verdict Box -->
<div class="verdict">
    <h2>THE VERDICT</h2>
    <p style="font-size:1.2em; max-width:800px; margin:0 auto 20px; line-height:1.6;">
        Email has <strong style="color:#e74c3c;">negative lift</strong> in 4 out of 5 segments.
        The company is spending <strong>${current_total:.0f}</strong> on emails that actively <em>reduce</em> purchase rates.
        Only <strong style="color:#00b894;">Inactive users</strong> (+1.1pp lift) benefit from email.
        Stop emailing segments that buy on their own and reallocate budget.
    </p>
    <div class="verdict-grid">
        <div class="verdict-item">
            <div class="num" style="color:#e74c3c;">4 / 5</div>
            <div class="desc">Segments with negative email lift</div>
        </div>
        <div class="verdict-item">
            <div class="num" style="color:#00b894;">${total_net:+,.0f}</div>
            <div class="desc">Net gain from strategy change</div>
        </div>
        <div class="verdict-item">
            <div class="num" style="color:#FFEAA7;">{sum(current_emails) - sum(optimal_emails):,}</div>
            <div class="desc">Unnecessary emails eliminated</div>
        </div>
    </div>
</div>

<!-- Segment Strategy Cards -->
<div class="section">
    <h2>Segment-by-Segment Strategy</h2>
    {segment_cards_html}
</div>

<!-- Heatmap Table -->
<div class="section">
    <h2>Segment x Campaign Targeting Matrix</h2>
    <p style="color:#888; margin-bottom:15px;">Values show email lift in percentage points. Green = email helps. Red = email hurts.</p>
    <table>
        <tr><th>Segment</th>{camp_headers}<th>Action</th></tr>
        {heatmap_rows}
    </table>
</div>

<!-- Campaign Strategy -->
<div class="section">
    <h2>Campaign-Level Targeting</h2>
    <table>
        <tr><th>Campaign</th><th>Overall Lift</th><th>Emails</th><th>Cost</th><th>Revenue</th><th>Best Segment</th><th>Worst Segment</th></tr>
        {camp_strat_rows}
    </table>
</div>

<!-- Action Playbook -->
<div class="section">
    <h2>Action Playbook</h2>
    <div class="playbook">
        <div class="playbook-item">
            <div class="step-num">1</div>
            <div><strong>Immediately stop emailing VIP, Regular, and Frequent Buyer segments.</strong><br>
            These segments have -7.4pp, -6.8pp, and -5.1pp lift respectively. They buy at <em>higher</em> rates without email. Savings: ${summary_df[summary_df['action']=='STOP']['current_email_cost'].sum():.0f}.</div>
        </div>
        <div class="playbook-item">
            <div class="step-num">2</div>
            <div><strong>Stop emailing New Users.</strong><br>
            -2.5pp lift means emails are counterproductive. These users need onboarding, not sales emails. Save ${summary_df[summary_df['segment']=='New User']['current_email_cost'].values[0]:.0f}.</div>
        </div>
        <div class="playbook-item">
            <div class="step-num">3</div>
            <div><strong>Focus all email resources on Inactive users.</strong><br>
            Only segment with positive lift (+1.1pp). Email all {summary_df[summary_df['segment']=='Inactive']['not_emailed'].values[0]:,} non-emailed Inactive users.</div>
        </div>
        <div class="playbook-item">
            <div class="step-num">4</div>
            <div><strong>Investigate why email hurts purchase rates.</strong><br>
            Negative lift across 4 segments suggests emails may be annoying customers, creating decision fatigue, or diluting urgency. Run A/B tests with reduced frequency.</div>
        </div>
        <div class="playbook-item">
            <div class="step-num">5</div>
            <div><strong>Reallocate the ${total_saved:.0f} saved to improve email quality.</strong><br>
            Better subject lines (54.5% open drop), better content (60.2% click drop), and targeted offers for Inactive users where email actually drives incremental revenue.</div>
        </div>
    </div>
</div>

<div class="footer">
    Email Targeting Strategy | Generated 2026-03-31 | 8,000 records analyzed
</div>

</div>
</body>
</html>"""

with open('output/targeting_strategy.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved targeting_strategy.html")

print(f"\n{'='*70}")
print(f"DONE: targeting_strategy.png + targeting_strategy.html")
print(f"{'='*70}")
