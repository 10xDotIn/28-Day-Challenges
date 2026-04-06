import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'figure.facecolor': '#1a1a2e',
    'axes.facecolor': '#16213e',
    'axes.edgecolor': '#e94560',
    'axes.labelcolor': '#eee',
    'text.color': '#eee',
    'xtick.color': '#ccc',
    'ytick.color': '#ccc',
    'grid.color': '#333',
    'font.size': 11,
    'figure.dpi': 150,
})

df = pd.read_csv('data/search_rankings.csv')

# Aggregate by product (across all queries and days)
prod = df.groupby('product').agg(
    total_impressions=('impressions', 'sum'),
    total_clicks=('clicks', 'sum'),
    total_purchases=('purchases', 'sum'),
    total_revenue=('revenue', 'sum'),
    total_atc=('add_to_cart', 'sum'),
).reset_index()

total_clicks = prod['total_clicks'].sum()
total_purchases = prod['total_purchases'].sum()

prod['click_share'] = prod['total_clicks'] / total_clicks * 100
prod['conversion_share'] = prod['total_purchases'] / total_purchases * 100
prod['conv_rate'] = prod['total_purchases'] / prod['total_clicks'].replace(0, np.nan) * 100
prod['click_to_conv_ratio'] = prod['conversion_share'] / prod['click_share'].replace(0, np.nan)

# Sort by click share descending
prod = prod.sort_values('click_share', ascending=True)

# ── Chart 1: Side-by-side proportion bars ──
fig, ax = plt.subplots(figsize=(16, 14))

y = np.arange(len(prod))
bar_h = 0.35

bars1 = ax.barh(y + bar_h/2, prod['click_share'], height=bar_h, color='#e94560', label='Click Share (%)', alpha=0.85)
bars2 = ax.barh(y - bar_h/2, prod['conversion_share'], height=bar_h, color='#00ff88', label='Conversion Share (%)', alpha=0.85)

ax.set_yticks(y)
ax.set_yticklabels(prod['product'], fontsize=9)
ax.set_xlabel('Share of Total (%)', fontsize=14)
ax.set_title('Proportion of Clicks vs Conversions by Product', fontsize=18, fontweight='bold', color='#00d2ff')
ax.legend(fontsize=12, loc='lower right')
ax.grid(True, alpha=0.3, axis='x')

# Annotate values
for i, (_, row) in enumerate(prod.iterrows()):
    ax.text(row['click_share'] + 0.05, i + bar_h/2, f"{row['click_share']:.1f}%",
            va='center', fontsize=7, color='#e94560', fontweight='bold')
    ax.text(row['conversion_share'] + 0.05, i - bar_h/2, f"{row['conversion_share']:.1f}%",
            va='center', fontsize=7, color='#00ff88', fontweight='bold')

plt.tight_layout()
plt.savefig('output/product_clicks_conversions.png', bbox_inches='tight')
plt.close()

# ── Chart 2: Efficiency — who converts more than their click share? ──
prod_sorted = prod.sort_values('click_to_conv_ratio', ascending=True).copy()

fig, ax = plt.subplots(figsize=(16, 14))

y2 = np.arange(len(prod_sorted))
ratio_vals = prod_sorted['click_to_conv_ratio'].fillna(0).values
colors = ['#00ff88' if r > 1 else '#e94560' for r in ratio_vals]

ax.barh(y2, ratio_vals, color=colors, alpha=0.85, height=0.6)
ax.axvline(x=1.0, color='#ffd700', linestyle='--', linewidth=2, label='Fair share (1.0)')
ax.set_yticks(y2)
ax.set_yticklabels(prod_sorted['product'], fontsize=9)
ax.set_xlabel('Conversion Share / Click Share Ratio', fontsize=14)
ax.set_title('Conversion Efficiency: Who Converts More Than Their Click Share?',
             fontsize=16, fontweight='bold', color='#00d2ff')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3, axis='x')

for i, val in enumerate(ratio_vals):
    label = f'{val:.2f}x'
    if val > 1:
        label += ' (undervalued)'
    elif val < 1 and val > 0:
        label += ' (overvalued)'
    ax.text(val + 0.02, i, label, va='center', fontsize=7,
            color='#00ff88' if val > 1 else '#e94560', fontweight='bold')

plt.tight_layout()
plt.savefig('output/product_conversion_efficiency.png', bbox_inches='tight')
plt.close()

# ── Chart 3: Detailed HTML table ──
prod_table = prod.sort_values('click_share', ascending=False)

rows_html = ''
for _, row in prod_table.iterrows():
    ratio = row['click_to_conv_ratio']
    if np.isnan(ratio):
        ratio_str = 'N/A'
        ratio_color = '#888'
    elif ratio > 1.2:
        ratio_str = f'{ratio:.2f}x'
        ratio_color = '#00ff88'
    elif ratio < 0.8:
        ratio_str = f'{ratio:.2f}x'
        ratio_color = '#ff4444'
    else:
        ratio_str = f'{ratio:.2f}x'
        ratio_color = '#ffd700'

    conv_rate = row['conv_rate']
    cr_str = f'{conv_rate:.1f}%' if not np.isnan(conv_rate) else 'N/A'

    rows_html += f'''<tr>
        <td>{row["product"]}</td>
        <td>{row["total_impressions"]:,.0f}</td>
        <td>{row["total_clicks"]:,.0f}</td>
        <td>{row["click_share"]:.2f}%</td>
        <td>{row["total_purchases"]:,.0f}</td>
        <td>{row["conversion_share"]:.2f}%</td>
        <td>{cr_str}</td>
        <td style="color:{ratio_color};font-weight:bold">{ratio_str}</td>
        <td>${row["total_revenue"]:,.0f}</td>
    </tr>'''

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Product Clicks & Conversions Proportion</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0f0f23; color:#e0e0e0; font-family:'Segoe UI',system-ui,sans-serif; padding:30px; }}
h1 {{ font-size:2.2em; background:linear-gradient(135deg,#e94560,#00d2ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:8px; }}
.subtitle {{ color:#888; margin-bottom:30px; font-size:1.1em; }}
.metrics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:15px; margin:25px 0; }}
.metric {{ background:linear-gradient(135deg,#1a1a3e,#16213e); border:1px solid #333; border-radius:12px; padding:20px; text-align:center; }}
.metric .val {{ font-size:2em; font-weight:bold; }}
.metric .lbl {{ color:#888; font-size:0.85em; margin-top:4px; }}
.red {{ color:#e94560; }}
.green {{ color:#00ff88; }}
.blue {{ color:#00d2ff; }}
.gold {{ color:#ffd700; }}
.chart {{ background:#1a1a2e; border-radius:12px; padding:20px; margin:25px 0; border:1px solid #333; }}
.chart img {{ width:100%; border-radius:8px; }}
table {{ width:100%; border-collapse:collapse; margin:20px 0; }}
th {{ background:#16213e; color:#00d2ff; padding:12px; text-align:left; font-size:0.85em; position:sticky; top:0; }}
td {{ padding:10px 12px; border-bottom:1px solid #222; font-size:0.85em; }}
tr:hover {{ background:#1a1a3e; }}
.legend {{ display:flex; gap:20px; margin:15px 0; font-size:0.9em; }}
.legend span {{ display:inline-flex; align-items:center; gap:5px; }}
.dot {{ width:12px; height:12px; border-radius:50%; display:inline-block; }}
h2 {{ color:#e94560; font-size:1.5em; margin:35px 0 15px; padding-bottom:8px; border-bottom:2px solid #e94560; }}
</style>
</head>
<body>

<h1>Product Clicks & Conversions Proportion</h1>
<p class="subtitle">How each product shares total clicks and total conversions across all {df["query"].nunique()} queries over {df["date"].nunique()} days</p>

<div class="metrics">
    <div class="metric"><div class="val blue">{len(prod):,}</div><div class="lbl">Products</div></div>
    <div class="metric"><div class="val red">{total_clicks:,}</div><div class="lbl">Total Clicks</div></div>
    <div class="metric"><div class="val green">{total_purchases:,}</div><div class="lbl">Total Conversions</div></div>
    <div class="metric"><div class="val gold">{total_purchases/total_clicks*100:.2f}%</div><div class="lbl">Overall Conv Rate</div></div>
</div>

<h2>Click Share vs Conversion Share</h2>
<p>Does a product's share of conversions match its share of clicks? Green bars exceeding red bars = efficient converters.</p>
<div class="chart"><img src="product_clicks_conversions.png"></div>

<h2>Conversion Efficiency Ratio</h2>
<p>Ratio > 1.0 means the product converts more than its fair share of clicks. These are undervalued. Ratio < 1.0 = overvalued (gets clicks but doesn't convert proportionally).</p>
<div class="legend">
    <span><span class="dot" style="background:#00ff88"></span> Undervalued (ratio > 1.0) - deserves higher ranking</span>
    <span><span class="dot" style="background:#e94560"></span> Overvalued (ratio < 1.0) - wastes click share</span>
</div>
<div class="chart"><img src="product_conversion_efficiency.png"></div>

<h2>Full Product Breakdown</h2>
<table>
<tr>
    <th>Product</th><th>Impressions</th><th>Clicks</th><th>Click Share</th>
    <th>Purchases</th><th>Conv Share</th><th>Conv Rate</th><th>Efficiency</th><th>Revenue</th>
</tr>
{rows_html}
</table>

<div style="text-align:center;padding:30px 0;color:#555;">
Product Clicks & Conversions Analysis - {len(df):,} data points
</div>
</body>
</html>'''

with open('output/product_clicks_conversions.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Saved:')
print('  output/product_clicks_conversions.png')
print('  output/product_conversion_efficiency.png')
print('  output/product_clicks_conversions.html')
print()
print(f'Total clicks: {total_clicks:,}')
print(f'Total conversions: {total_purchases:,}')
print(f'Overall conversion rate: {total_purchases/total_clicks*100:.2f}%')
print()
print('Top 5 by click share:')
top5 = prod.sort_values('click_share', ascending=False).head(5)
for _, r in top5.iterrows():
    print(f'  {r["product"]}: {r["click_share"]:.2f}% clicks, {r["conversion_share"]:.2f}% conversions, efficiency {r["click_to_conv_ratio"]:.2f}x')
print()
print('Top 5 most efficient converters:')
eff5 = prod.sort_values('click_to_conv_ratio', ascending=False).head(5)
for _, r in eff5.iterrows():
    print(f'  {r["product"]}: {r["click_to_conv_ratio"]:.2f}x (gets {r["click_share"]:.2f}% clicks but {r["conversion_share"]:.2f}% conversions)')
