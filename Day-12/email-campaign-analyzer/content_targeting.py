import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/email_campaigns.csv')
EMAIL_COST = 0.05

# ============================================================
# Build full segment x campaign matrix
# ============================================================
combos = []
for seg in df['segment'].unique():
    for camp in df['campaign'].unique():
        s = df[(df['segment'] == seg) & (df['campaign'] == camp)]
        em = s[s['email_sent'] == 1]
        no = s[s['email_sent'] == 0]
        if len(em) < 5 or len(no) < 5:
            continue
        em_rate = em['purchased'].mean() * 100
        no_rate = no['purchased'].mean() * 100
        lift = em_rate - no_rate
        open_rate = em['opened'].mean() * 100
        click_rate = em['clicked'].mean() * 100
        avg_rev = s[s['purchased'] == 1]['revenue'].mean() if s['purchased'].sum() > 0 else 0
        n_emailed = len(em)
        n_not_emailed = len(no)

        # ROI of emailing this combo
        cost = n_emailed * EMAIL_COST
        incremental_purchases = lift / 100 * n_emailed
        incremental_rev = incremental_purchases * avg_rev
        roi = incremental_rev - cost

        combos.append({
            'segment': seg, 'campaign': camp,
            'email_rate': round(em_rate, 1), 'no_email_rate': round(no_rate, 1),
            'lift': round(lift, 1), 'open_rate': round(open_rate, 1),
            'click_rate': round(click_rate, 1), 'avg_revenue': round(avg_rev, 2),
            'emailed': n_emailed, 'not_emailed': n_not_emailed,
            'email_cost': round(cost, 2), 'incremental_rev': round(incremental_rev, 2),
            'roi': round(roi, 2), 'total_n': len(s)
        })

combo_df = pd.DataFrame(combos)

# Classify each combo
def classify(row):
    if row['lift'] >= 3:
        return 'SEND'
    elif row['lift'] >= 0:
        return 'TEST'
    else:
        return 'STOP'

combo_df['action'] = combo_df.apply(classify, axis=1)

# Winners and losers
winners = combo_df[combo_df['lift'] > 0].sort_values('lift', ascending=False)
losers = combo_df[combo_df['lift'] < 0].sort_values('lift')

print("TOP 10 WINNING COMBOS (email increases purchases):")
for _, r in winners.head(10).iterrows():
    print(f"  {r['segment']:16s} x {r['campaign']:18s} | Lift: {r['lift']:+6.1f}pp | Open: {r['open_rate']:4.1f}% | ROI: ${r['roi']:+,.0f}")

print("\nTOP 10 LOSING COMBOS (email hurts purchases):")
for _, r in losers.head(10).iterrows():
    print(f"  {r['segment']:16s} x {r['campaign']:18s} | Lift: {r['lift']:+6.1f}pp | Open: {r['open_rate']:4.1f}% | ROI: ${r['roi']:+,.0f}")

total_winner_roi = winners['roi'].sum()
total_loser_roi = losers['roi'].sum()
print(f"\nWinner combos total ROI: ${total_winner_roi:+,.0f}")
print(f"Loser combos total ROI: ${total_loser_roi:+,.0f}")
print(f"Net swing if optimized: ${total_winner_roi - total_loser_roi:+,.0f}")

# ============================================================
# CHART: content_targeting.png
# ============================================================
fig = plt.figure(figsize=(26, 32))
fig.patch.set_facecolor('#0f0f1a')
gs = GridSpec(5, 2, figure=fig, hspace=0.35, wspace=0.3, height_ratios=[1.2, 1, 1, 1, 0.8])

action_colors_map = {'SEND': '#00b894', 'TEST': '#f1c40f', 'STOP': '#e74c3c'}
seg_colors = {'VIP': '#9b59b6', 'Frequent Buyer': '#3498db', 'Regular': '#1abc9c', 'New User': '#f39c12', 'Inactive': '#e74c3c'}
camp_colors = {'Flash Deal': '#FF6B6B', 'Loyalty Reward': '#4ECDC4', 'New Arrival': '#45B7D1',
               'Summer Sale': '#FFEAA7', 'Weekend Special': '#DDA0DD', 'Welcome Series': '#98D8C8', 'Win-Back': '#F8B500'}

# --- Panel 1: Master Heatmap with SEND/TEST/STOP labels ---
ax1 = fig.add_subplot(gs[0, :])
ax1.set_facecolor('#1a1a2e')

pivot_lift = combo_df.pivot(index='segment', columns='campaign', values='lift')
pivot_action = combo_df.pivot(index='segment', columns='campaign', values='action')

# Order segments by avg lift
seg_avg_lift = combo_df.groupby('segment')['lift'].mean().sort_values()
pivot_lift = pivot_lift.reindex(seg_avg_lift.index)
pivot_action = pivot_action.reindex(seg_avg_lift.index)

# Custom annotations: lift + action
annot_text = []
for seg in pivot_lift.index:
    row_text = []
    for camp in pivot_lift.columns:
        l = pivot_lift.loc[seg, camp]
        a = pivot_action.loc[seg, camp]
        if pd.isna(l):
            row_text.append('')
        else:
            row_text.append(f'{l:+.1f}\n{a}')
    annot_text.append(row_text)
annot_arr = np.array(annot_text)

hm = sns.heatmap(pivot_lift, annot=annot_arr, fmt='', cmap='RdYlGn', center=0, ax=ax1,
                  linewidths=3, linecolor='#0f0f1a', cbar_kws={'label': 'Email Lift (pp)', 'shrink': 0.5},
                  annot_kws={'fontsize': 11, 'fontweight': 'bold'}, vmin=-20, vmax=10)
ax1.set_title('CONTENT TARGETING MATRIX: Which Email Content Works for Which Customer?\nGreen = SEND  |  Yellow = TEST  |  Red = STOP',
              fontsize=16, fontweight='bold', color='#4ECDC4', pad=20)
ax1.tick_params(colors='white', labelsize=12)
plt.setp(ax1.get_xticklabels(), color='white', rotation=25, ha='right', fontsize=12)
plt.setp(ax1.get_yticklabels(), color='white', rotation=0, fontsize=12)
cbar = hm.collections[0].colorbar
cbar.ax.tick_params(colors='white')
cbar.set_label('Email Lift (pp)', color='white', fontsize=11)

# --- Panel 2: Top Winners - Which content WORKS ---
ax2 = fig.add_subplot(gs[1, 0])
ax2.set_facecolor('#1a1a2e')

top_w = winners.head(8).iloc[::-1]
y = np.arange(len(top_w))
labels = [f"{r['segment']} x {r['campaign']}" for _, r in top_w.iterrows()]
colors = [seg_colors.get(r['segment'], '#888') for _, r in top_w.iterrows()]

bars = ax2.barh(y, top_w['lift'], color=colors, edgecolor='white', linewidth=0.5, height=0.6)
for i, (bar, (_, r)) in enumerate(zip(bars, top_w.iterrows())):
    ax2.text(bar.get_width() + 0.2, i, f"+{r['lift']}pp | Open:{r['open_rate']}% | ROI:${r['roi']:+,.0f}",
             va='center', fontsize=10, fontweight='bold', color='white')
ax2.set_yticks(y)
ax2.set_yticklabels(labels, fontsize=10, color='white')
ax2.set_title('TOP WINNERS: Email Content That INCREASES Purchases', fontsize=13, fontweight='bold', color='#00b894', pad=15)
ax2.set_xlabel('Email Lift (pp)', color='white', fontsize=11)
ax2.tick_params(colors='white')
for spine in ax2.spines.values():
    spine.set_color('#2a2a4a')

# --- Panel 3: Top Losers - Which content HURTS ---
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_facecolor('#1a1a2e')

top_l = losers.head(8).iloc[::-1]
y = np.arange(len(top_l))
labels = [f"{r['segment']} x {r['campaign']}" for _, r in top_l.iterrows()]
colors = [seg_colors.get(r['segment'], '#888') for _, r in top_l.iterrows()]

bars = ax3.barh(y, top_l['lift'], color=colors, edgecolor='white', linewidth=0.5, height=0.6)
for i, (bar, (_, r)) in enumerate(zip(bars, top_l.iterrows())):
    ax3.text(bar.get_width() - 0.3, i, f"{r['lift']}pp | Lost:${abs(r['roi']):,.0f}",
             va='center', ha='right', fontsize=10, fontweight='bold', color='white')
ax3.set_yticks(y)
ax3.set_yticklabels(labels, fontsize=10, color='white')
ax3.set_title('TOP LOSERS: Email Content That HURTS Purchases', fontsize=13, fontweight='bold', color='#e74c3c', pad=15)
ax3.set_xlabel('Email Lift (pp)', color='white', fontsize=11)
ax3.tick_params(colors='white')
for spine in ax3.spines.values():
    spine.set_color('#2a2a4a')

# --- Panel 4: Per-Segment Best Content ---
ax4 = fig.add_subplot(gs[2, 0])
ax4.set_facecolor('#1a1a2e')

# For each segment, show best and worst campaign
seg_best = combo_df.loc[combo_df.groupby('segment')['lift'].idxmax()]
seg_worst = combo_df.loc[combo_df.groupby('segment')['lift'].idxmin()]

segs = sorted(df['segment'].unique())
y = np.arange(len(segs))
width = 0.35

best_vals = [seg_best[seg_best['segment'] == s]['lift'].values[0] for s in segs]
worst_vals = [seg_worst[seg_worst['segment'] == s]['lift'].values[0] for s in segs]
best_camps = [seg_best[seg_best['segment'] == s]['campaign'].values[0] for s in segs]
worst_camps = [seg_worst[seg_worst['segment'] == s]['campaign'].values[0] for s in segs]

bars1 = ax4.barh(y + width/2, best_vals, width, color='#00b894', edgecolor='white', linewidth=0.5, label='Best Campaign')
bars2 = ax4.barh(y - width/2, worst_vals, width, color='#e74c3c', edgecolor='white', linewidth=0.5, label='Worst Campaign')
ax4.axvline(x=0, color='white', linewidth=0.5, alpha=0.3)

for i in range(len(segs)):
    ax4.text(best_vals[i] + 0.3, y[i] + width/2, f'{best_camps[i]} ({best_vals[i]:+.1f}pp)',
             va='center', fontsize=9, color='#00b894', fontweight='bold')
    ax4.text(worst_vals[i] - 0.3, y[i] - width/2, f'{worst_camps[i]} ({worst_vals[i]:+.1f}pp)',
             va='center', ha='right', fontsize=9, color='#e74c3c', fontweight='bold')

ax4.set_yticks(y)
ax4.set_yticklabels(segs, fontsize=11, fontweight='bold', color='white')
ax4.set_title('BEST vs WORST Content Per Segment', fontsize=13, fontweight='bold', color='#4ECDC4', pad=15)
ax4.legend(fontsize=10)
ax4.tick_params(colors='white')
for spine in ax4.spines.values():
    spine.set_color('#2a2a4a')

# --- Panel 5: Content Engagement Quality ---
ax5 = fig.add_subplot(gs[2, 1])
ax5.set_facecolor('#1a1a2e')

# Scatter: open rate vs lift, sized by revenue
sc = ax5.scatter(combo_df['open_rate'], combo_df['lift'],
                  c=[seg_colors.get(s, '#888') for s in combo_df['segment']],
                  s=combo_df['avg_revenue'] / 2, alpha=0.7, edgecolors='white', linewidth=0.5)
ax5.axhline(y=0, color='white', linewidth=0.5, alpha=0.3, linestyle='--')
ax5.axhline(y=3, color='#00b894', linewidth=1, alpha=0.5, linestyle='--')

# Label notable points
for _, r in winners.head(3).iterrows():
    ax5.annotate(f"{r['segment'][:4]}\n{r['campaign'][:8]}", (r['open_rate'], r['lift']),
                 fontsize=8, color='#00b894', fontweight='bold', ha='center')
for _, r in losers.head(3).iterrows():
    ax5.annotate(f"{r['segment'][:4]}\n{r['campaign'][:8]}", (r['open_rate'], r['lift']),
                 fontsize=8, color='#e74c3c', fontweight='bold', ha='center')

ax5.set_xlabel('Open Rate (%)', fontsize=11, color='white')
ax5.set_ylabel('Email Lift (pp)', fontsize=11, color='white')
ax5.set_title('Engagement vs Impact\n(High opens != high purchases)', fontsize=13, fontweight='bold', color='#4ECDC4', pad=15)
ax5.tick_params(colors='white')

# Legend
for seg, col in seg_colors.items():
    ax5.scatter([], [], c=col, s=60, label=seg)
ax5.legend(fontsize=9, loc='lower right', framealpha=0.5)
for spine in ax5.spines.values():
    spine.set_color('#2a2a4a')

# --- Panel 6: ROI by Combo (sorted) ---
ax6 = fig.add_subplot(gs[3, :])
ax6.set_facecolor('#1a1a2e')

sorted_combos = combo_df.sort_values('roi', ascending=True)
x = np.arange(len(sorted_combos))
colors = ['#00b894' if r > 0 else '#e74c3c' for r in sorted_combos['roi']]
bars = ax6.bar(x, sorted_combos['roi'], color=colors, edgecolor='none', width=0.8)

# Label the extremes
for idx in [0, 1, 2, -3, -2, -1]:
    row = sorted_combos.iloc[idx]
    label = f"{row['segment'][:4]}x{row['campaign'][:6]}"
    y_pos = row['roi'] + (30 if row['roi'] >= 0 else -50)
    ax6.text(x[idx], y_pos, label, ha='center', fontsize=7, color='white', rotation=45)

ax6.axhline(y=0, color='white', linewidth=1, alpha=0.5)
ax6.set_title('ROI of Every Segment x Campaign Combo\n(Every bar above zero = money made, below = money lost)',
              fontsize=14, fontweight='bold', color='#4ECDC4', pad=15)
ax6.set_ylabel('ROI ($)', fontsize=12, color='white')
ax6.set_xticks([])
ax6.tick_params(colors='white')

send_count = len(combo_df[combo_df['action'] == 'SEND'])
test_count = len(combo_df[combo_df['action'] == 'TEST'])
stop_count = len(combo_df[combo_df['action'] == 'STOP'])
ax6.text(0.02, 0.95, f'SEND: {send_count} combos  |  TEST: {test_count} combos  |  STOP: {stop_count} combos',
         transform=ax6.transAxes, fontsize=11, color='white',
         bbox=dict(facecolor='#16213e', edgecolor='#4ECDC4', boxstyle='round,pad=0.5'))
for spine in ax6.spines.values():
    spine.set_color('#2a2a4a')

# --- Panel 7: Playbook summary ---
ax7 = fig.add_subplot(gs[4, :])
ax7.set_facecolor('#0f0f1a')
ax7.axis('off')

ax7.text(0.5, 0.95, 'CONTENT TARGETING PLAYBOOK: What to Send to Whom',
         transform=ax7.transAxes, ha='center', fontsize=18, fontweight='bold', color='#4ECDC4')

# Build playbook per segment
playbook_text = []
for seg in sorted(df['segment'].unique()):
    seg_data = combo_df[combo_df['segment'] == seg].sort_values('lift', ascending=False)
    send_camps = seg_data[seg_data['action'] == 'SEND']['campaign'].tolist()
    test_camps = seg_data[seg_data['action'] == 'TEST']['campaign'].tolist()
    stop_camps = seg_data[seg_data['action'] == 'STOP']['campaign'].tolist()
    send_str = ', '.join(send_camps) if send_camps else 'None'
    stop_str = ', '.join(stop_camps) if stop_camps else 'None'
    playbook_text.append((seg, send_str, stop_str))

col_x = [0.05, 0.25, 0.55]
ax7.text(col_x[0], 0.78, 'SEGMENT', transform=ax7.transAxes, fontsize=12, fontweight='bold', color='#888')
ax7.text(col_x[1], 0.78, 'SEND THESE', transform=ax7.transAxes, fontsize=12, fontweight='bold', color='#00b894')
ax7.text(col_x[2], 0.78, 'STOP THESE', transform=ax7.transAxes, fontsize=12, fontweight='bold', color='#e74c3c')

for i, (seg, send, stop) in enumerate(playbook_text):
    y = 0.65 - i * 0.13
    ax7.text(col_x[0], y, seg, transform=ax7.transAxes, fontsize=11, fontweight='bold', color='white')
    ax7.text(col_x[1], y, send, transform=ax7.transAxes, fontsize=10, color='#00b894')
    ax7.text(col_x[2], y, stop, transform=ax7.transAxes, fontsize=10, color='#e74c3c')

plt.savefig('output/content_targeting.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("Saved content_targeting.png")

# ============================================================
# HTML: content_targeting.html
# ============================================================

# Build heatmap table
camps = sorted(df['campaign'].unique())
pivot_lift = combo_df.pivot(index='segment', columns='campaign', values='lift')
pivot_action = combo_df.pivot(index='segment', columns='campaign', values='action')
seg_order_list = combo_df.groupby('segment')['lift'].mean().sort_values().index.tolist()

camp_headers = ''.join([f'<th>{c}</th>' for c in camps])
heatmap_rows = ''
for seg in seg_order_list:
    heatmap_rows += f'<tr><td class="seg-label">{seg}</td>'
    for camp in camps:
        try:
            lift_val = pivot_lift.loc[seg, camp]
            action_val = pivot_action.loc[seg, camp]
        except KeyError:
            heatmap_rows += '<td>-</td>'
            continue
        if pd.isna(lift_val):
            heatmap_rows += '<td>-</td>'
            continue
        if action_val == 'SEND':
            bg, bdr = '#0a3d2e', '#00b894'
        elif action_val == 'TEST':
            bg, bdr = '#3d3a0a', '#f1c40f'
        else:
            bg, bdr = '#3d0a0a', '#e74c3c'
        heatmap_rows += f'<td style="background:{bg};border:2px solid {bdr};"><div class="cell-lift">{lift_val:+.1f}pp</div><div class="cell-action" style="color:{bdr};">{action_val}</div></td>'
    heatmap_rows += '</tr>'

# Winner cards
winner_cards = ''
for _, r in winners.head(6).iterrows():
    winner_cards += f'''<div class="combo-card winner">
        <div class="combo-header">
            <span class="combo-seg">{r['segment']}</span>
            <span class="combo-x">x</span>
            <span class="combo-camp">{r['campaign']}</span>
        </div>
        <div class="combo-lift" style="color:#00b894;">+{r['lift']}pp lift</div>
        <div class="combo-details">
            <span>Open: {r['open_rate']}%</span>
            <span>Click: {r['click_rate']}%</span>
            <span>ROI: ${r['roi']:+,.0f}</span>
        </div>
        <div class="combo-verdict">This content DRIVES purchases for this audience</div>
    </div>'''

loser_cards = ''
for _, r in losers.head(6).iterrows():
    loser_cards += f'''<div class="combo-card loser">
        <div class="combo-header">
            <span class="combo-seg">{r['segment']}</span>
            <span class="combo-x">x</span>
            <span class="combo-camp">{r['campaign']}</span>
        </div>
        <div class="combo-lift" style="color:#e74c3c;">{r['lift']}pp lift</div>
        <div class="combo-details">
            <span>Open: {r['open_rate']}%</span>
            <span>Click: {r['click_rate']}%</span>
            <span>Lost: ${abs(r['roi']):,.0f}</span>
        </div>
        <div class="combo-verdict">This content KILLS purchases for this audience</div>
    </div>'''

# Playbook table
playbook_rows = ''
for seg in sorted(df['segment'].unique()):
    seg_data = combo_df[combo_df['segment'] == seg].sort_values('lift', ascending=False)
    send_camps = seg_data[seg_data['action'] == 'SEND']
    test_camps = seg_data[seg_data['action'] == 'TEST']
    stop_camps = seg_data[seg_data['action'] == 'STOP']

    send_html = ''.join([f'<span class="tag send">{r["campaign"]} ({r["lift"]:+.1f}pp)</span>' for _, r in send_camps.iterrows()])
    test_html = ''.join([f'<span class="tag test">{r["campaign"]} ({r["lift"]:+.1f}pp)</span>' for _, r in test_camps.iterrows()])
    stop_html = ''.join([f'<span class="tag stop">{r["campaign"]} ({r["lift"]:+.1f}pp)</span>' for _, r in stop_camps.iterrows()])

    if not send_html:
        send_html = '<span style="color:#666;">None</span>'

    seg_total_roi = seg_data[seg_data['action'] == 'SEND']['roi'].sum()
    seg_wasted = abs(seg_data[seg_data['action'] == 'STOP']['roi'].sum())

    playbook_rows += f'''<tr>
        <td class="seg-label">{seg}</td>
        <td>{send_html}</td>
        <td>{test_html}</td>
        <td>{stop_html}</td>
        <td style="color:#00b894;font-weight:700;">${seg_total_roi:+,.0f}</td>
        <td style="color:#e74c3c;font-weight:700;">${seg_wasted:,.0f}</td>
    </tr>'''

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Content-to-Customer Targeting</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0f0f1a; color:#e0e0e0; font-family:'Segoe UI',system-ui,sans-serif; padding:20px; }}
.container {{ max-width:1500px; margin:0 auto; }}
h1 {{ text-align:center; font-size:2.4em; margin-bottom:5px; background:linear-gradient(135deg,#4ECDC4,#45B7D1); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.subtitle {{ text-align:center; color:#888; margin-bottom:30px; font-size:1.1em; }}

.hero {{ display:grid; grid-template-columns:repeat(4,1fr); gap:15px; margin-bottom:30px; }}
.hero-card {{ background:linear-gradient(135deg,#1a1a2e,#16213e); border-radius:12px; padding:20px; text-align:center; border:1px solid #2a2a4a; }}
.hero-card .label {{ color:#888; font-size:0.85em; text-transform:uppercase; letter-spacing:1px; }}
.hero-card .value {{ font-size:2em; font-weight:900; margin-top:5px; }}

.section {{ margin-bottom:40px; }}
.section h2 {{ color:#4ECDC4; font-size:1.5em; margin-bottom:15px; padding-bottom:8px; border-bottom:2px solid #2a2a4a; }}
.section p.desc {{ color:#888; margin-bottom:15px; }}

table {{ width:100%; border-collapse:collapse; background:#1a1a2e; border-radius:10px; overflow:hidden; }}
th {{ background:#16213e; color:#4ECDC4; padding:12px; text-align:center; font-size:0.85em; text-transform:uppercase; letter-spacing:1px; }}
td {{ padding:10px 12px; border-bottom:1px solid #2a2a4a; text-align:center; vertical-align:middle; }}
.seg-label {{ font-weight:700; text-align:left !important; white-space:nowrap; }}
tr:hover {{ background:#16213e; }}

.cell-lift {{ font-size:1.1em; font-weight:800; }}
.cell-action {{ font-size:0.8em; font-weight:700; margin-top:2px; }}

.combos-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:15px; }}
.combo-card {{ background:#1a1a2e; border-radius:10px; padding:18px; }}
.combo-card.winner {{ border-left:4px solid #00b894; }}
.combo-card.loser {{ border-left:4px solid #e74c3c; }}
.combo-header {{ display:flex; align-items:center; gap:8px; margin-bottom:8px; }}
.combo-seg {{ font-weight:700; font-size:1.1em; color:white; }}
.combo-x {{ color:#888; }}
.combo-camp {{ color:#4ECDC4; font-weight:600; }}
.combo-lift {{ font-size:1.8em; font-weight:900; margin:5px 0; }}
.combo-details {{ display:flex; gap:15px; color:#aaa; font-size:0.9em; margin:8px 0; }}
.combo-verdict {{ background:#16213e; border-radius:6px; padding:8px; font-size:0.9em; }}

.tag {{ display:inline-block; padding:3px 10px; border-radius:15px; font-size:0.8em; font-weight:600; margin:2px; }}
.tag.send {{ background:#0a3d2e; color:#00b894; border:1px solid #00b894; }}
.tag.test {{ background:#3d3a0a; color:#f1c40f; border:1px solid #f1c40f; }}
.tag.stop {{ background:#3d0a0a; color:#e74c3c; border:1px solid #e74c3c; }}

.insight-box {{ background:linear-gradient(135deg,#0f3460,#1a1a2e); border:2px solid #4ECDC4; border-radius:12px; padding:25px; margin:20px 0; }}
.insight-box h3 {{ color:#FFEAA7; margin-bottom:12px; font-size:1.3em; }}
.insight-box p {{ line-height:1.6; margin-bottom:8px; }}

.footer {{ text-align:center; color:#555; padding:20px; font-size:0.9em; }}
</style>
</head>
<body>
<div class="container">

<h1>Content-to-Customer Targeting</h1>
<p class="subtitle">Which email content drives purchases for which customers &mdash; and which content kills sales</p>

<div class="hero">
    <div class="hero-card">
        <div class="label">Combos Analyzed</div>
        <div class="value" style="color:#45B7D1;">{len(combo_df)}</div>
    </div>
    <div class="hero-card">
        <div class="label">SEND (lift 3+pp)</div>
        <div class="value" style="color:#00b894;">{send_count}</div>
    </div>
    <div class="hero-card">
        <div class="label">TEST (0-3pp)</div>
        <div class="value" style="color:#f1c40f;">{test_count}</div>
    </div>
    <div class="hero-card">
        <div class="label">STOP (negative lift)</div>
        <div class="value" style="color:#e74c3c;">{stop_count}</div>
    </div>
</div>

<!-- Insight -->
<div class="insight-box">
    <h3>The Content-Customer Mismatch</h3>
    <p>Out of {len(combo_df)} segment-campaign combinations, only <strong style="color:#00b894;">{send_count}</strong> actually increase purchases.
    <strong style="color:#e74c3c;">{stop_count}</strong> combinations actively REDUCE purchase rates.
    The same campaign can be a <strong>winner</strong> for one segment and a <strong>disaster</strong> for another.</p>
    <p>For example, <strong>Summer Sale</strong> has {combo_df[(combo_df['campaign']=='Summer Sale') & (combo_df['lift']>0)].shape[0]} positive combos but
    destroys purchases for VIP (-18.6pp) and Regular (-16.4pp). Meanwhile <strong>Flash Deal</strong> works great for
    Inactive (+5.7pp) but hurts Frequent Buyers (-7.2pp). <em>Content targeting matters more than volume.</em></p>
</div>

<!-- Master Heatmap -->
<div class="section">
    <h2>Targeting Matrix: Every Segment x Campaign Combination</h2>
    <p class="desc">Each cell shows email lift (pp) and recommended action. Green border = SEND. Yellow = TEST. Red = STOP.</p>
    <table>
        <tr><th>Segment</th>{camp_headers}</tr>
        {heatmap_rows}
    </table>
</div>

<!-- Winners -->
<div class="section">
    <h2>Top Winning Combos &mdash; Content That DRIVES Purchases</h2>
    <p class="desc">These segment-campaign pairs show strong positive lift. Email these users THIS content.</p>
    <div class="combos-grid">{winner_cards}</div>
</div>

<!-- Losers -->
<div class="section">
    <h2>Top Losing Combos &mdash; Content That KILLS Purchases</h2>
    <p class="desc">These segment-campaign pairs have strong negative lift. Stop sending this content to these users immediately.</p>
    <div class="combos-grid">{loser_cards}</div>
</div>

<!-- Playbook -->
<div class="section">
    <h2>Content Playbook: What to Send Each Segment</h2>
    <table>
        <tr><th>Segment</th><th>SEND These Campaigns</th><th>TEST These</th><th>STOP These</th><th>Potential ROI</th><th>Wasted</th></tr>
        {playbook_rows}
    </table>
</div>

<!-- Key Insight -->
<div class="insight-box">
    <h3>Bottom Line: Target the Content, Not Just the Volume</h3>
    <p><strong>1. Inactive users</strong> respond to <strong>Flash Deal</strong> (+5.7pp) and <strong>Win-Back</strong> (+2.8pp) but are HURT by Welcome Series (-3.8pp).</p>
    <p><strong>2. New Users</strong> respond to <strong>Weekend Special</strong> (+6.4pp) and <strong>Flash Deal</strong> (+4.1pp) but are HURT by Loyalty Reward (-8.7pp) and New Arrival (-6.6pp).</p>
    <p><strong>3. VIPs</strong> only respond to <strong>Welcome Series</strong> (+4.8pp). Every other campaign REDUCES their purchases, especially Summer Sale (-18.6pp).</p>
    <p><strong>4. Frequent Buyers</strong> only respond to <strong>New Arrival</strong> (+3.5pp). Sales campaigns kill their purchase rate.</p>
    <p><strong>5. Regular</strong> users barely respond to any email. Best bet is Welcome Series (+0.9pp) but it's marginal.</p>
    <p style="margin-top:15px;font-size:1.1em;"><strong style="color:#4ECDC4;">The fix isn't "email more" or "email less" &mdash; it's "email the RIGHT content to the RIGHT person."</strong></p>
</div>

<div class="footer">Content-to-Customer Targeting Analysis | Generated 2026-03-31 | {len(df):,} records, {len(combo_df)} combinations analyzed</div>

</div>
</body>
</html>'''

with open('output/content_targeting.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved content_targeting.html")
