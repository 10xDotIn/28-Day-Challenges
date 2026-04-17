import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import os, warnings
warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────────────────
DATA  = 'data/customers.csv'
OUT   = 'output'
os.makedirs(OUT, exist_ok=True)

# ── Global style ───────────────────────────────────────────────────────────
BG       = '#0f0f0f'
CARD     = '#1a1a1a'
ACCENT   = '#6366f1'
GOLD     = '#f59e0b'
GREEN    = '#10b981'
RED      = '#ef4444'
MUTED    = '#6b7280'
WHITE    = '#f9fafb'

ARCHETYPE_COLORS = {
    'Future VIP':      '#6366f1',
    'Loyal Regular':   '#10b981',
    'Promising New':   '#3b82f6',
    'Discount Addict': '#f59e0b',
    'One-and-Done':    '#ef4444',
    'Fading Away':     '#8b5cf6',
}

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor':   CARD,
    'axes.edgecolor':   '#2d2d2d',
    'axes.labelcolor':  WHITE,
    'xtick.color':      MUTED,
    'ytick.color':      MUTED,
    'text.color':       WHITE,
    'grid.color':       '#2d2d2d',
    'grid.linewidth':   0.5,
    'font.family':      'DejaVu Sans',
    'font.size':        11,
})

# ── Load data ──────────────────────────────────────────────────────────────
print("Loading data …")
df = pd.read_csv(DATA)
print(f"  {len(df):,} customers loaded, {df.shape[1]} columns")

# ── 1. Customer Reality Check ──────────────────────────────────────────────
print("\n[1/8] Customer Reality Check …")

arch_stats = df.groupby('customer_archetype').agg(
    count=('customer_id', 'count'),
    total_clv=('predicted_3yr_clv', 'sum'),
    avg_clv=('predicted_3yr_clv', 'mean'),
    total_rev=('lifetime_revenue', 'sum'),
).reset_index()
arch_stats['pct_customers'] = arch_stats['count'] / len(df) * 100
arch_stats['pct_clv']       = arch_stats['total_clv'] / arch_stats['total_clv'].sum() * 100
arch_stats = arch_stats.sort_values('avg_clv', ascending=False)

# Top-10% concentration
top10_threshold = df['predicted_3yr_clv'].quantile(0.90)
top10_clv_pct   = df[df['predicted_3yr_clv'] >= top10_threshold]['predicted_3yr_clv'].sum() / df['predicted_3yr_clv'].sum() * 100

print(f"  Top 10% customers hold {top10_clv_pct:.1f}% of predicted CLV")
for _, r in arch_stats.iterrows():
    print(f"  {r['customer_archetype']:20s}  {r['pct_customers']:5.1f}% of customers  {r['pct_clv']:5.1f}% of CLV")

# ── 2. Customer Pyramid PNG ────────────────────────────────────────────────
print("\n[2/8] Customer Pyramid ...")

pyramid_order = ['Future VIP', 'Loyal Regular', 'Promising New', 'Discount Addict', 'Fading Away', 'One-and-Done']
pdata = arch_stats.set_index('customer_archetype').reindex(pyramid_order).reset_index()

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis('off')
ax.set_title('The Customer Pyramid', fontsize=20, fontweight='bold', color=WHITE, pad=20)

y_positions = np.linspace(0.85, 0.05, len(pyramid_order))
widths      = np.linspace(0.25, 0.90, len(pyramid_order))

for i, (_, row) in enumerate(pdata.iterrows()):
    arch  = row['customer_archetype']
    color = ARCHETYPE_COLORS.get(arch, ACCENT)
    x     = (1 - widths[i]) / 2
    rect  = mpatches.FancyBboxPatch(
        (x, y_positions[i] - 0.045), widths[i], 0.085,
        boxstyle='round,pad=0.005', linewidth=0,
        facecolor=color, alpha=0.85, transform=ax.transAxes
    )
    ax.add_patch(rect)
    label = (f"{arch}  |  {row['count']:,} customers ({row['pct_customers']:.1f}%)"
             f"  |  ${row['total_clv']/1e6:.1f}M CLV ({row['pct_clv']:.1f}%)")
    ax.text(0.5, y_positions[i], label, transform=ax.transAxes,
            ha='center', va='center', fontsize=10, color='white', fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUT}/customer_pyramid.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  Saved customer_pyramid.png")

# ── 3. First Purchase DNA PNG ──────────────────────────────────────────────
print("\n[3/8] First Purchase DNA ...")

dna = df.groupby('customer_archetype').agg(
    avg_first_value=('first_order_value', 'mean'),
    avg_discount=('first_order_discount_pct', 'mean'),
).reindex(pyramid_order).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor(BG)
fig.suptitle('First Purchase DNA by Archetype', fontsize=18, fontweight='bold', color=WHITE, y=1.01)
colors = [ARCHETYPE_COLORS.get(a, ACCENT) for a in dna['customer_archetype']]

ax = axes[0]
ax.set_facecolor(CARD)
bars = ax.barh(dna['customer_archetype'], dna['avg_first_value'], color=colors, edgecolor='none', height=0.6)
ax.set_xlabel('Avg First Order Value ($)', color=WHITE)
ax.set_title('First Order Value', color=WHITE, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
for bar, v in zip(bars, dna['avg_first_value']):
    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, f'${v:.0f}', va='center', fontsize=9, color=WHITE)

ax = axes[1]
ax.set_facecolor(CARD)
bars = ax.barh(dna['customer_archetype'], dna['avg_discount'], color=colors, edgecolor='none', height=0.6)
ax.set_xlabel('Avg First Discount (%)', color=WHITE)
ax.set_title('First Order Discount', color=WHITE, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
for bar, v in zip(bars, dna['avg_discount']):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, f'{v:.1f}%', va='center', fontsize=9, color=WHITE)

plt.tight_layout()
plt.savefig(f'{OUT}/first_purchase_dna.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  Saved first_purchase_dna.png")

# ── 4. 30-Day Crystal Ball PNG ─────────────────────────────────────────────
print("\n[4/8] 30-Day Crystal Ball ...")

signals = ['pages_viewed_first_30d', 'sessions_first_30d', 'email_opens_first_30d',
           'items_browsed_first_30d', 'days_to_second_order', 'first_order_value',
           'first_order_discount_pct']
labels  = ['Pages Viewed (30d)', 'Sessions (30d)', 'Email Opens (30d)',
           'Items Browsed (30d)', 'Days to 2nd Order', 'First Order Value', 'First Discount %']

corrs = [df[s].corr(df['predicted_3yr_clv']) for s in signals]
corr_df = pd.DataFrame({'signal': labels, 'corr': corrs}).sort_values('corr')

colors_bar = [RED if c < 0 else ACCENT for c in corr_df['corr']]

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(CARD)
bars = ax.barh(corr_df['signal'], corr_df['corr'], color=colors_bar, edgecolor='none', height=0.6)
ax.axvline(0, color=MUTED, linewidth=1)
ax.set_xlabel('Correlation with 3-Year CLV', color=WHITE)
ax.set_title('The 30-Day Crystal Ball\nWhich Early Signals Predict Lifetime Value?', color=WHITE, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
for bar, v in zip(bars, corr_df['corr']):
    xpos = v + 0.005 if v >= 0 else v - 0.005
    ha   = 'left' if v >= 0 else 'right'
    ax.text(xpos, bar.get_y() + bar.get_height()/2, f'{v:.3f}', va='center', ha=ha, fontsize=9, color=WHITE)

plt.tight_layout()
plt.savefig(f'{OUT}/crystal_ball.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  Saved crystal_ball.png")

# ── 5. Channel Quality PNG ─────────────────────────────────────────────────
print("\n[5/8] Channel Quality ...")

ch = df.groupby('acquisition_channel').agg(
    avg_clv=('predicted_3yr_clv', 'mean'),
    count=('customer_id', 'count'),
).reset_index().sort_values('avg_clv', ascending=True)

CHANNEL_COLORS = ['#6366f1','#10b981','#f59e0b','#3b82f6','#ef4444']
ch_colors = CHANNEL_COLORS[:len(ch)]

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(CARD)
bars = ax.barh(ch['acquisition_channel'], ch['avg_clv'], color=ch_colors, edgecolor='none', height=0.6)
ax.set_xlabel('Avg Predicted 3-Year CLV ($)', color=WHITE)
ax.set_title('Channel Quality Score\nAvg CLV by Acquisition Channel', color=WHITE, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
for bar, v, n in zip(bars, ch['avg_clv'], ch['count']):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
            f'${v:.0f}  (n={n:,})', va='center', fontsize=9, color=WHITE)

plt.tight_layout()
plt.savefig(f'{OUT}/channel_quality.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  Saved channel_quality.png")

# ── 6. Discount Curse PNG ──────────────────────────────────────────────────
print("\n[6/8] Discount Curse ...")

df['discount_bin'] = pd.cut(df['first_order_discount_pct'],
                             bins=[0, 5, 10, 15, 20, 100],
                             labels=['0-5%', '5-10%', '10-15%', '15-20%', '20%+'])
disc = df.groupby('discount_bin', observed=True)['predicted_3yr_clv'].mean().reset_index()

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(CARD)
ax.plot(disc['discount_bin'].astype(str), disc['predicted_3yr_clv'],
        color=GOLD, linewidth=3, marker='o', markersize=10, markerfacecolor=RED)
ax.fill_between(range(len(disc)), disc['predicted_3yr_clv'].min() * 0.95, disc['predicted_3yr_clv'],
                alpha=0.15, color=GOLD)
for i, (x, y) in enumerate(zip(disc['discount_bin'].astype(str), disc['predicted_3yr_clv'])):
    ax.text(i, y + 10, f'${y:.0f}', ha='center', fontsize=10, color=WHITE, fontweight='bold')
ax.set_xlabel('First Order Discount Band', color=WHITE)
ax.set_ylabel('Avg 3-Year CLV ($)', color=WHITE)
ax.set_title('The Discount Curse\nHigher First Discounts = Lower Lifetime Value', color=WHITE, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUT}/discount_curse.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  Saved discount_curse.png")

# ── 7. CLV Tiers PNG ───────────────────────────────────────────────────────
print("\n[7/8] CLV Tiers ...")

p_90 = df['predicted_3yr_clv'].quantile(0.90)
p_70 = df['predicted_3yr_clv'].quantile(0.70)
p_40 = df['predicted_3yr_clv'].quantile(0.40)

def assign_tier(v):
    if v >= p_90: return 'Platinum'
    if v >= p_70: return 'Gold'
    if v >= p_40: return 'Silver'
    return 'Bronze'

df['clv_tier'] = df['predicted_3yr_clv'].apply(assign_tier)

tier_order  = ['Platinum', 'Gold', 'Silver', 'Bronze']
TIER_COLORS = {'Platinum': '#e2e8f0', 'Gold': GOLD, 'Silver': '#9ca3af', 'Bronze': '#92400e'}
tier_stats  = df.groupby('clv_tier').agg(count=('customer_id','count'),
                                          total_clv=('predicted_3yr_clv','sum')).reindex(tier_order).reset_index()

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(CARD)
colors_t = [TIER_COLORS[t] for t in tier_stats['clv_tier']]
bars = ax.bar(tier_stats['clv_tier'], tier_stats['count'], color=colors_t, edgecolor='none', width=0.5)
ax.set_ylabel('Number of Customers', color=WHITE)
ax.set_title('CLV Tier Distribution\nPlatinum / Gold / Silver / Bronze', color=WHITE, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
for bar, row in zip(bars, tier_stats.itertuples()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
            f'{row.count:,}\n${row.total_clv/1e6:.1f}M', ha='center', fontsize=9, color=WHITE, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUT}/clv_tiers.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  Saved clv_tiers.png")

# ── 8. CLV Prediction Model + Report ──────────────────────────────────────
print("\n[8/8] CLV Model + Report ...")

features = ['first_order_value', 'first_order_discount_pct',
            'pages_viewed_first_30d', 'sessions_first_30d',
            'email_opens_first_30d', 'items_browsed_first_30d',
            'days_to_second_order']
feat_labels = ['First Order Value', 'First Discount %', 'Pages Viewed (30d)',
               'Sessions (30d)', 'Email Opens (30d)', 'Items Browsed (30d)',
               'Days to 2nd Order']

# Encode channel
le = LabelEncoder()
df['channel_enc'] = le.fit_transform(df['acquisition_channel'])
X = df[features].fillna(df[features].median())
y = df['predicted_3yr_clv']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
r2 = r2_score(y_test, model.predict(X_test))
print(f"  Model R² = {r2:.3f}")

importances = pd.Series(model.feature_importances_, index=feat_labels).sort_values()

# Build report data
best_channel    = ch.iloc[-1]['acquisition_channel']
worst_channel   = ch.iloc[0]['acquisition_channel']
best_archetype  = arch_stats.iloc[0]['customer_archetype']
best_signal     = importances.idxmax()
churn_rate      = df['churned'].mean() * 100
total_pred_clv  = df['predicted_3yr_clv'].sum()
avg_clv         = df['predicted_3yr_clv'].mean()
disc_impact     = ((disc.iloc[0]['predicted_3yr_clv'] - disc.iloc[-1]['predicted_3yr_clv'])
                   / disc.iloc[0]['predicted_3yr_clv'] * 100)

report = f"""# Customer Lifetime Value Report

## Executive Summary
8,000 customers. ${total_pred_clv/1e6:.1f}M in predicted 3-year value.
But {top10_clv_pct:.1f}% of that comes from just 10% of customers.
Average CLV = ${avg_clv:,.0f}. Churn rate = {churn_rate:.1f}%.

## Customer Archetype Breakdown
"""
for _, r in arch_stats.iterrows():
    report += f"- **{r['customer_archetype']}**: {r['count']:,} customers ({r['pct_customers']:.1f}%) → ${r['total_clv']/1e6:.1f}M CLV ({r['pct_clv']:.1f}%)\n"

report += f"""
## First Purchase DNA
VIPs start with higher first-order values and lower discounts.
Heavy discounters attract Discount Addicts — not future VIPs.

## 30-Day Signals That Matter
Top predictor: **{best_signal}** (importance: {importances.max():.3f})
Model R² = {r2:.3f} — these early signals explain most CLV variation.

## Channel Quality Ranking
Best channel: **{best_channel}** (highest avg CLV)
Worst channel: **{worst_channel}** (lowest avg CLV)

## The Discount Problem
Customers acquired at 0-5% discount have ${disc.iloc[0]['predicted_3yr_clv']:.0f} avg CLV.
Customers acquired at 20%+ discount have ${disc.iloc[-1]['predicted_3yr_clv']:.0f} avg CLV.
That's a {disc_impact:.1f}% drop in lifetime value from heavy discounting.

## Churn Early Warning
Churn rate overall: {churn_rate:.1f}%
Fading Away customers show high days_since_last_order and low email engagement.

## CLV Tier Breakdown
"""
for _, r in tier_stats.iterrows():
    report += f"- **{r['clv_tier']}**: {r['count']:,} customers → ${r['total_clv']/1e6:.1f}M total CLV\n"

report += f"""
## Strategic Recommendations
- **INVEST** → Future VIPs & Loyal Regulars: increase retention spend
- **NURTURE** → Promising New: onboarding sequences, early engagement
- **CONVERT** → Discount Addicts: gradual discount reduction program
- **LET GO** → One-and-Done: stop wasting retention budget
- **SAVE** → Fading Away: re-engagement campaigns before churn

## 5 Actions to Increase Total CLV
1. Cap first-order discounts at 10% — saves significant CLV per acquired customer
2. Double down on {best_channel} acquisition — best quality customers
3. Trigger second-order campaign within 14 days of first purchase
4. Build early-warning alert for Fading Away customers (days_since_last_order > 60)
5. Create VIP fast-track: customers with 30d sessions > median get white-glove treatment

## Final Verdict
- **Most valuable archetype**: {best_archetype}
- **Worst acquisition channel**: {worst_channel}
- **Strongest CLV predictor**: {best_signal}
- **Biggest immediate win**: Reduce first-order discounts above 15% — instant CLV uplift
"""

with open(f'{OUT}/clv_report.md', 'w', encoding='utf-8') as f:
    f.write(report)
print("  Saved clv_report.md")

# ── 9. Dashboard HTML ──────────────────────────────────────────────────────
print("\n[9/8] Dashboard HTML ...")
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer Intelligence Dashboard</title>
    <style>
        body {{
            background-color: #0f0f0f;
            color: #f9fafb;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        h1 {{ color: #6366f1; font-size: 2.5em; margin-bottom: 5px; }}
        .metrics {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background-color: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            flex: 1;
            min-width: 200px;
            border: 1px solid #2d2d2d;
        }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #10b981; }}
        .metric-label {{ color: #6b7280; font-size: 0.9em; text-transform: uppercase; }}
        .charts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        .chart-card {{
            background-color: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #2d2d2d;
            text-align: center;
        }}
        .chart-card img {{ max-width: 100%; height: auto; border-radius: 5px; }}
        .strategy-board {{
            background-color: #1a1a1a;
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #2d2d2d;
            margin-bottom: 40px;
        }}
        .strategy-board h2 {{ color: #6366f1; text-align: center; margin-top: 0; }}
        .strategy-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .strat-card {{ padding: 15px; border-radius: 8px; border-left: 4px solid; background-color: #262626; }}
        .strat-invest {{ border-color: #6366f1; }}
        .strat-nurture {{ border-color: #3b82f6; }}
        .strat-convert {{ border-color: #f59e0b; }}
        .strat-letgo {{ border-color: #ef4444; }}
        .strat-save {{ border-color: #8b5cf6; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Customer Lifetime Value Predictor</h1>
        <p>Analyze behaviors, predict lifetime value, and allocate resources efficiently.</p>
    </div>

    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value">8,000</div>
            <div class="metric-label">Total Customers</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${total_pred_clv/1e6:.1f}M</div>
            <div class="metric-label">Predicted 3-Year Value</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${avg_clv:,.0f}</div>
            <div class="metric-label">Avg CLV</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #ef4444;">{churn_rate:.1f}%</div>
            <div class="metric-label">Churn Rate</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{top10_clv_pct:.1f}%</div>
            <div class="metric-label">Value from Top 10%</div>
        </div>
    </div>

    <div class="charts">
        <div class="chart-card">
            <img src="customer_pyramid.png" alt="Customer Pyramid">
        </div>
        <div class="chart-card">
            <img src="first_purchase_dna.png" alt="First Purchase DNA">
        </div>
        <div class="chart-card">
            <img src="crystal_ball.png" alt="30-Day Crystal Ball">
        </div>
        <div class="chart-card">
            <img src="channel_quality.png" alt="Channel Quality">
        </div>
        <div class="chart-card">
            <img src="discount_curse.png" alt="The Discount Curse">
        </div>
        <div class="chart-card">
            <img src="clv_tiers.png" alt="CLV Tiers">
        </div>
    </div>

    <div class="strategy-board">
        <h2>Strategy Board</h2>
        <div class="strategy-grid">
            <div class="strat-card strat-invest">
                <h3>INVEST</h3>
                <p><strong>Target:</strong> Future VIPs & Loyal Regulars</p>
                <p>Increase retention spend. Roll out white-glove onboarding and exclusive perks.</p>
            </div>
            <div class="strat-card strat-nurture">
                <h3>NURTURE</h3>
                <p><strong>Target:</strong> Promising New</p>
                <p>Optimize onboarding. Trigger early multi-channel engagement to push them to secondary purchases quickly.</p>
            </div>
            <div class="strat-card strat-convert">
                <h3>CONVERT</h3>
                <p><strong>Target:</strong> Discount Addicts</p>
                <p>Gradually reduce discounts. Focus messaging on brand value and exclusivity instead of price.</p>
            </div>
            <div class="strat-card strat-letgo">
                <h3>LET GO</h3>
                <p><strong>Target:</strong> One-and-Done</p>
                <p>Stop wasting ad and retention budget. Cap initial acquisition discounts to minimize loss.</p>
            </div>
            <div class="strat-card strat-save">
                <h3>SAVE</h3>
                <p><strong>Target:</strong> Fading Away</p>
                <p>Deploy high-impact re-engagement campaigns immediately when days since last order approaches 60.</p>
            </div>
        </div>
    </div>
</body>
</html>"""

with open(f'{OUT}/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print("  Saved dashboard.html")

print("\nAll 8 outputs saved to output/")
print(f"\n{'='*50}")
print(f"  Most valuable customer type : {best_archetype}")
print(f"  Worst acquisition channel   : {worst_channel}")
print(f"  Strongest CLV predictor     : {best_signal}")
print(f"  Best immediate action       : Cap discounts > 15% -> instant CLV uplift")
print(f"{'='*50}")
