import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

OUT = Path('output')
df = pd.read_csv('data/pricing_data.csv')
buyers = df[df['converted'] == 1].copy()
non_buyers = df[df['converted'] == 0].copy()

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
PINK = '#ff4081'

# ══════════════════════════════════════════════════════════════════
# CONSUMER METRICS
# ══════════════════════════════════════════════════════════════════

strat = df.groupby('pricing_strategy').agg(
    avg_mrp=('original_mrp', 'mean'),
    avg_displayed=('displayed_price', 'mean'),
    avg_discount_pct=('discount_percent', 'mean'),
    avg_time=('time_on_page_seconds', 'mean'),
    conv_rate=('converted', 'mean'),
).reset_index()
strat['real_discount'] = (strat['avg_mrp'] - strat['avg_displayed']) / strat['avg_mrp'] * 100
strat['short'] = strat['pricing_strategy'].map(SHORT)

buyer_met = buyers.groupby('pricing_strategy').agg(
    avg_satisfaction=('satisfaction_rating', 'mean'),
    return_rate=('returned', 'mean'),
    repeat_rate=('repeat_purchase_30d', 'mean'),
    avg_paid=('revenue', 'mean'),
    avg_items=('items_in_cart', 'mean'),
    avg_discount_buyers=('discount_percent', 'mean'),
).reset_index()

combo = strat.merge(buyer_met, on='pricing_strategy')
# Consumer Value Score: high satisfaction + high real discount + low return rate + high repeat
# = satisfaction/5 * real_discount/max * (1-return_rate) * (repeat_rate normalized)
max_disc = combo['real_discount'].max()
combo['consumer_value'] = (
    (combo['avg_satisfaction'] / 5) *
    (combo['real_discount'] / max_disc) *
    (1 - combo['return_rate']) *
    (combo['repeat_rate'] / combo['repeat_rate'].max())
) * 100

combo = combo.sort_values('consumer_value', ascending=False)

# ── MRP Inflation analysis: is the MRP jacked up? ──
# Compare MRP across strategies for same products
mrp_by_prod = df.groupby(['product', 'pricing_strategy'])['original_mrp'].mean().unstack()
overall_mrp = df.groupby('product')['original_mrp'].mean()
mrp_inflation = pd.DataFrame()
for strat_name in mrp_by_prod.columns:
    inflation = ((mrp_by_prod[strat_name] - overall_mrp) / overall_mrp * 100).mean()
    mrp_inflation = pd.concat([mrp_inflation, pd.DataFrame({
        'pricing_strategy': [strat_name], 'mrp_inflation_pct': [inflation]
    })])
mrp_inflation['short'] = mrp_inflation['pricing_strategy'].map(SHORT)
mrp_inflation = mrp_inflation.sort_values('mrp_inflation_pct', ascending=False)

# ── Slow buyers vs fast buyers: who gets better outcomes? ──
buyers['speed'] = pd.qcut(buyers['time_on_page_seconds'], 3, labels=['Fast (<30s)', 'Medium', 'Slow (Deliberate)'])
speed = buyers.groupby('speed').agg(
    avg_satisfaction=('satisfaction_rating', 'mean'),
    return_rate=('returned', 'mean'),
    avg_discount=('discount_percent', 'mean'),
    repeat_rate=('repeat_purchase_30d', 'mean'),
    avg_paid=('revenue', 'mean'),
).reset_index()

# ── Segment exploitation: who overpays / gets worst deals? ──
seg = buyers.groupby('user_segment').agg(
    avg_discount=('discount_percent', 'mean'),
    avg_satisfaction=('satisfaction_rating', 'mean'),
    return_rate=('returned', 'mean'),
    avg_paid=('revenue', 'mean'),
    repeat_rate=('repeat_purchase_30d', 'mean'),
).reset_index()
seg['savvy_score'] = (seg['avg_satisfaction'] / 5) * (1 - seg['return_rate']) * (seg['avg_discount'] / seg['avg_discount'].max()) * 100

# ── People who DIDN'T buy — were they right to walk away? ──
# For strategies with high return rates, non-converters dodged a bullet
walked_away = df.groupby('pricing_strategy').agg(
    total=('converted', 'count'),
    buyers_n=('converted', 'sum'),
    non_buyers_n=('converted', lambda x: (x == 0).sum()),
).reset_index()
walked_away = walked_away.merge(buyer_met[['pricing_strategy', 'return_rate', 'avg_satisfaction']], on='pricing_strategy')
walked_away['bullet_dodged'] = walked_away['non_buyers_n'] * walked_away['return_rate']  # estimated returns avoided
walked_away['short'] = walked_away['pricing_strategy'].map(SHORT)

# ══════════════════════════════════════════════════════════════════
# BUILD THE VISUAL
# ══════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(22, 28), facecolor=DARK_BG)
fig.suptitle('The Consumer\'s Counter-Playbook', fontsize=26, fontweight='bold', color=WHITE, y=0.98)
fig.text(0.5, 0.968, 'How to flip pricing psychology to YOUR advantage — where are the real deals, traps, and smart moves?',
         ha='center', fontsize=13, color='#888', style='italic')

# ── Panel 1: Consumer Value Score ──
ax1 = fig.add_axes([0.06, 0.82, 0.88, 0.12])
ax1.set_facecolor(CARD_BG)
d1 = combo.sort_values('consumer_value', ascending=True)
max_cv = d1['consumer_value'].max()
colors1 = [GREEN if v > max_cv*0.6 else (YELLOW if v > max_cv*0.3 else RED) for v in d1['consumer_value']]
bars = ax1.barh(d1['short'], d1['consumer_value'], color=colors1, edgecolor='none', height=0.6)
for bar, val, sat, disc, rr in zip(bars, d1['consumer_value'], d1['avg_satisfaction'], d1['real_discount'], d1['return_rate']):
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}  (Sat: {sat:.1f}/5 | Disc: {disc:.0f}% | Returns: {rr:.0%})',
             va='center', fontsize=9.5, color=WHITE)
ax1.set_title('Consumer Value Score — Where Buyers Actually Win', fontsize=15, fontweight='bold', color=GREEN, pad=10)
ax1.set_xlabel('Consumer Value Score (satisfaction x real discount x low returns x loyalty)', fontsize=10, color='#aaa')
ax1.set_xlim(0, max_cv * 1.8)
ax1.grid(axis='x', alpha=0.15, color=GRID)
ax1.tick_params(colors=WHITE)
for spine in ax1.spines.values(): spine.set_color(GRID)

# ── Panel 2: Fake Discount Detector — Advertised vs Real Discount ──
ax2 = fig.add_axes([0.06, 0.66, 0.42, 0.13])
ax2.set_facecolor(CARD_BG)
d2 = combo.sort_values('avg_discount_pct', ascending=True)
x2 = np.arange(len(d2))
w2 = 0.35
ax2.barh(x2 - w2/2, d2['avg_discount_pct'], w2, label='Advertised Discount %', color=CYAN, alpha=0.7, edgecolor='none')
ax2.barh(x2 + w2/2, d2['real_discount'], w2, label='Real Discount (MRP vs Price)', color=GREEN, edgecolor='none')
ax2.set_yticks(x2)
ax2.set_yticklabels(d2['short'], fontsize=9)
ax2.set_title('Fake Discount Detector', fontsize=14, fontweight='bold', color=CYAN, pad=10)
ax2.set_xlabel('Discount %', fontsize=10, color='#aaa')
ax2.legend(loc='lower right', framealpha=0.3, fontsize=8)
ax2.grid(axis='x', alpha=0.15, color=GRID)
ax2.tick_params(colors=WHITE)
for spine in ax2.spines.values(): spine.set_color(GRID)

# ── Panel 3: MRP Inflation — Which strategies jack up MRP? ──
ax3 = fig.add_axes([0.54, 0.66, 0.40, 0.13])
ax3.set_facecolor(CARD_BG)
d3 = mrp_inflation.sort_values('mrp_inflation_pct', ascending=True)
colors3 = [RED if v > 1 else (YELLOW if v > 0 else GREEN) for v in d3['mrp_inflation_pct']]
bars3 = ax3.barh(d3['short'], d3['mrp_inflation_pct'], color=colors3, edgecolor='none', height=0.6)
for bar, val in zip(bars3, d3['mrp_inflation_pct']):
    side = bar.get_width() + 0.2 if val >= 0 else bar.get_width() - 0.8
    ax3.text(side, bar.get_y() + bar.get_height()/2,
             f'{val:+.1f}%', va='center', fontsize=9, color=WHITE, fontweight='bold')
ax3.axvline(x=0, color=WHITE, alpha=0.3, linewidth=1)
ax3.set_title('MRP Inflation Alert — Is the MRP Rigged?', fontsize=14, fontweight='bold', color=ORANGE, pad=10)
ax3.set_xlabel('MRP Inflation vs Product Average (%)', fontsize=10, color='#aaa')
ax3.grid(axis='x', alpha=0.15, color=GRID)
ax3.tick_params(colors=WHITE)
for spine in ax3.spines.values(): spine.set_color(GRID)

# ── Panel 4: The Slow Buyer Advantage ──
ax4 = fig.add_axes([0.06, 0.50, 0.42, 0.13])
ax4.set_facecolor(CARD_BG)
x4 = np.arange(len(speed))
metrics = ['avg_satisfaction', 'return_rate', 'repeat_rate']
labels = ['Satisfaction /5', 'Return Rate', 'Repeat Rate']
clrs = [GREEN, RED, PURPLE]
w4 = 0.25
for i, (m, l, c) in enumerate(zip(metrics, labels, clrs)):
    vals = speed[m].values
    if m == 'avg_satisfaction':
        vals = vals  # keep as-is for visibility
    else:
        vals = vals * 5  # scale to match satisfaction axis
    ax4.bar(x4 + i*w4, vals, w4, label=l, color=c, edgecolor='none', alpha=0.85)
# Add actual values on top
for i, (m, c) in enumerate(zip(metrics, clrs)):
    for j, val in enumerate(speed[m].values):
        display = f'{val:.2f}' if m == 'avg_satisfaction' else f'{val:.0%}'
        ypos = val if m == 'avg_satisfaction' else val * 5
        ax4.text(j + i*w4, ypos + 0.08, display, ha='center', fontsize=8, color=c, fontweight='bold')
ax4.set_xticks(x4 + w4)
ax4.set_xticklabels(speed['speed'].values, fontsize=10)
ax4.set_title('The Slow Buyer Advantage — Take Your Time!', fontsize=14, fontweight='bold', color=PURPLE, pad=10)
ax4.legend(loc='upper right', framealpha=0.3, fontsize=8)
ax4.grid(axis='y', alpha=0.15, color=GRID)
ax4.tick_params(colors=WHITE)
for spine in ax4.spines.values(): spine.set_color(GRID)

# ── Panel 5: Segment Exploitation Index ──
ax5 = fig.add_axes([0.54, 0.50, 0.40, 0.13])
ax5.set_facecolor(CARD_BG)
d5 = seg.sort_values('savvy_score', ascending=True)
colors5 = [GREEN if v > seg['savvy_score'].median() else RED for v in d5['savvy_score']]
bars5 = ax5.barh(d5['user_segment'], d5['savvy_score'], color=colors5, edgecolor='none', height=0.5)
for bar, val, disc, ret in zip(bars5, d5['savvy_score'], d5['avg_discount'], d5['return_rate']):
    ax5.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}  (Disc: {disc:.0f}% | Ret: {ret:.0%})',
             va='center', fontsize=9, color=WHITE)
ax5.set_title('Who\'s Savvy vs Who Gets Exploited?', fontsize=14, fontweight='bold', color=PINK, pad=10)
ax5.set_xlabel('Savvy Score (high satisfaction x low returns x good discounts)', fontsize=10, color='#aaa')
ax5.grid(axis='x', alpha=0.15, color=GRID)
ax5.tick_params(colors=WHITE)
for spine in ax5.spines.values(): spine.set_color(GRID)

# ── Panel 6: The Trap Map — Conversion Rate vs Satisfaction ──
ax6 = fig.add_axes([0.06, 0.32, 0.42, 0.15])
ax6.set_facecolor(CARD_BG)
d6 = combo.copy()
# Size = return rate (bigger = more dangerous)
sizes = (d6['return_rate'] * 800) + 50
colors6 = [RED if r > 0.2 else (YELLOW if r > 0.1 else GREEN) for r in d6['return_rate']]
ax6.scatter(d6['conv_rate']*100, d6['avg_satisfaction'], s=sizes, c=colors6,
            edgecolors=WHITE, linewidth=1, alpha=0.85, zorder=5)
for _, row in d6.iterrows():
    ax6.annotate(row['short'], (row['conv_rate']*100, row['avg_satisfaction']),
                 textcoords='offset points', xytext=(10, 5), fontsize=9, color=WHITE, fontweight='bold')
ax6.axhline(y=d6['avg_satisfaction'].mean(), color=GRID, linestyle='--', alpha=0.5)
ax6.axvline(x=d6['conv_rate'].mean()*100, color=GRID, linestyle='--', alpha=0.5)
# Quadrant labels
ax6.text(5, 4.35, 'SMART BUY\nLow pressure + Happy', fontsize=8, color=GREEN, fontstyle='italic')
ax6.text(45, 4.35, 'GENUINE DEAL\nHigh demand + Happy', fontsize=8, color=CYAN, fontstyle='italic')
ax6.text(45, 2.95, 'TRAP!\nPressured + Unhappy', fontsize=8, color=RED, fontstyle='italic')
ax6.text(5, 2.95, 'IGNORED\nNo demand + Unhappy', fontsize=8, color='#666', fontstyle='italic')
ax6.set_xlabel('Conversion Rate % (how many fell for it)', fontsize=10, color='#aaa')
ax6.set_ylabel('Buyer Satisfaction (1-5)', fontsize=10, color='#aaa')
ax6.set_title('The Trap Map — Bubble size = Return Rate', fontsize=14, fontweight='bold', color=YELLOW, pad=10)
ax6.grid(alpha=0.15, color=GRID)
ax6.tick_params(colors=WHITE)
for spine in ax6.spines.values(): spine.set_color(GRID)

# ── Panel 7: Smart Buyers Who Walked Away — Bullets Dodged ──
ax7 = fig.add_axes([0.54, 0.32, 0.40, 0.15])
ax7.set_facecolor(CARD_BG)
d7 = walked_away.sort_values('bullet_dodged', ascending=True)
colors7 = [GREEN if v > walked_away['bullet_dodged'].median() else YELLOW for v in d7['bullet_dodged']]
bars7 = ax7.barh(d7['short'], d7['bullet_dodged'], color=colors7, edgecolor='none', height=0.6)
for bar, val, nb, rr in zip(bars7, d7['bullet_dodged'], d7['non_buyers_n'], d7['return_rate']):
    ax7.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
             f'{val:.0f} dodged  ({nb} walked away, {rr:.0%} would\'ve returned)',
             va='center', fontsize=8.5, color=WHITE)
ax7.set_title('Bullets Dodged — Non-Buyers Who Were RIGHT', fontsize=14, fontweight='bold', color=GREEN, pad=10)
ax7.set_xlabel('Estimated Returns Avoided (non-buyers x return rate)', fontsize=10, color='#aaa')
ax7.grid(axis='x', alpha=0.15, color=GRID)
ax7.tick_params(colors=WHITE)
for spine in ax7.spines.values(): spine.set_color(GRID)

# ── Panel 8: Consumer Cheat Sheet ──
ax8 = fig.add_axes([0.06, 0.03, 0.88, 0.26])
ax8.set_facecolor(CARD_BG)
ax8.axis('off')
ax8.set_title('THE CONSUMER CHEAT SHEET — How to Beat Every Pricing Trick',
              fontsize=16, fontweight='bold', color=CYAN, pad=15, loc='center')

tips = [
    ["URGENCY\n'Only 2 left!'", "31% of buyers return.\nThe pressure is fake.", "Walk away. Come back\ntomorrow. It'll still\nbe there.", RED],
    ["ANCHOR HIGH\n'Was Rs.5000\nnow Rs.3000!'", "The MRP is real but\n17% still return.", "Compare the ACTUAL\nprice across sites,\nnot the MRP slash.", YELLOW],
    ["BUNDLE\n'Buy 3 save 20%'", "You buy more items\nthan needed. 22% return.", "Ask: would I buy\neach item separately?\nIf no, skip the bundle.", ORANGE],
    ["FREE SHIPPING\n'Add Rs.200 more!'", "Cart inflated to 2 items\navg. 21% return rate.", "Calculate: is shipping\ncheaper than the extra\nitem you don't need?", YELLOW],
    ["CHARM\n'Rs.999 not Rs.1000'", "Good satisfaction (3.8/5)\nOnly 14% returns.", "This one's mostly\nharmless. The Rs.1\ndifference is real.", GREEN],
    ["PRESTIGE\n'Premium at Rs.5000'", "4.3/5 satisfaction!\nOnly 3% returns.", "If you can afford it,\nthis is where quality\nlives. Best buyer score.", GREEN],
    ["DECOY\n'3 plans: S/M/L'", "Nudges you to middle\noption. 15% returns.", "Ignore the middle.\nDo you need S or L?\nDecide before looking.", CYAN],
    ["ODD SPECIFIC\n'Rs.1,247'", "Feels calculated/fair.\nOnly 9% returns.", "Good instinct. Precise\npricing often = honest\ncost-based pricing.", GREEN],
]

cols = 4
rows_per = 2
cell_w = 0.23
cell_h = 0.115
x_start = 0.02
y_positions = [0.52, 0.08]

for idx, (trick, trap, counter, color) in enumerate(tips):
    row = idx // cols
    col = idx % cols
    x = x_start + col * (cell_w + 0.02)
    y = y_positions[row]

    # Card background
    rect = plt.Rectangle((x, y), cell_w, cell_h, transform=ax8.transAxes,
                          facecolor='#0f0f0f', edgecolor=color, linewidth=2, clip_on=False, zorder=2)
    ax8.add_patch(rect)

    # Trick name
    ax8.text(x + cell_w/2, y + cell_h - 0.015, trick, transform=ax8.transAxes,
             ha='center', va='top', fontsize=8, fontweight='bold', color=color, zorder=3)

    # The trap
    ax8.text(x + 0.005, y + cell_h * 0.45, 'TRAP: ' + trap.replace('\n', ' '), transform=ax8.transAxes,
             ha='left', va='center', fontsize=6.5, color='#ccc', zorder=3, style='italic',
             wrap=True)

    # Counter move
    ax8.text(x + 0.005, y + 0.012, 'COUNTER: ' + counter.replace('\n', ' '), transform=ax8.transAxes,
             ha='left', va='bottom', fontsize=6.5, color=WHITE, fontweight='bold', zorder=3,
             wrap=True)

fig.savefig(OUT / 'consumer_counter_playbook.png', dpi=150, bbox_inches='tight', facecolor=DARK_BG)
plt.close()
print("Saved: output/consumer_counter_playbook.png")

# Print key findings
print("\n=== CONSUMER INTELLIGENCE ===")
print(f"\nConsumer Value Score (best to worst):")
for _, row in combo.iterrows():
    print(f"  {row['short']:15s} | Value: {row['consumer_value']:5.1f} | Sat: {row['avg_satisfaction']:.1f}/5 | Real Disc: {row['real_discount']:.0f}% | Returns: {row['return_rate']:.0%}")

print(f"\nSegment Savvy Score:")
for _, row in seg.sort_values('savvy_score', ascending=False).iterrows():
    print(f"  {row['user_segment']:20s} | Savvy: {row['savvy_score']:.1f} | Avg Disc: {row['avg_discount']:.0f}% | Returns: {row['return_rate']:.0%}")

print(f"\nSlow Buyer Advantage:")
for _, row in speed.iterrows():
    print(f"  {row['speed']:20s} | Sat: {row['avg_satisfaction']:.2f} | Returns: {row['return_rate']:.0%} | Repeat: {row['repeat_rate']:.0%}")
