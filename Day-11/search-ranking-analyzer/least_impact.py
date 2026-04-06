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
    'font.size': 12,
    'figure.dpi': 150,
})

df = pd.read_csv('data/search_rankings.csv')
df['ctr'] = df['clicks'] / df['impressions']
df['conversion_rate'] = df['purchases'] / df['clicks'].replace(0, np.nan)

# Compute per-product stats
prod = df.groupby(['query', 'product']).agg(
    total_impressions=('impressions', 'sum'),
    total_clicks=('clicks', 'sum'),
    total_purchases=('purchases', 'sum'),
    total_revenue=('revenue', 'sum'),
    total_atc=('add_to_cart', 'sum'),
    avg_position=('position', 'mean'),
).reset_index()
prod['ctr'] = prod['total_clicks'] / prod['total_impressions']
prod['conv_rate'] = prod['total_purchases'] / prod['total_clicks'].replace(0, np.nan)
prod['rev_per_click'] = prod['total_revenue'] / prod['total_clicks'].replace(0, np.nan)

# Position bias
pos = df.groupby('position').agg(avg_ctr=('ctr', 'mean')).reset_index()
pos1_ctr = pos.loc[pos['position'] == 1, 'avg_ctr'].values[0]

# Revenue loss per product-query
losses = []
for _, row in prod.iterrows():
    curr_pos = round(row['avg_position'])
    curr_pos_ctr = pos.loc[pos['position'] == max(1, min(10, curr_pos)), 'avg_ctr'].values[0]
    rpc = row['rev_per_click']
    if curr_pos_ctr > 0 and not np.isnan(rpc):
        ctr_boost = pos1_ctr / curr_pos_ctr
        potential_rev = row['total_clicks'] * ctr_boost * rpc
        loss = potential_rev - row['total_revenue']
    else:
        loss = 0
    losses.append({
        'product': row['product'],
        'query': row['query'],
        'avg_position': row['avg_position'],
        'conv_rate': row['conv_rate'],
        'ctr': row['ctr'],
        'total_revenue': row['total_revenue'],
        'revenue_loss': max(loss, 0),
    })

loss_df = pd.DataFrame(losses)

# Least loss products and queries
least_loss = loss_df.sort_values('revenue_loss').head(15)
query_loss = loss_df.groupby('query')['revenue_loss'].sum().reset_index().sort_values('revenue_loss')

# Funnel drop-offs
funnel = {
    'Impressions > Clicks': (1 - df['clicks'].sum() / df['impressions'].sum()) * 100,
    'Clicks > Add to Cart': (1 - df['add_to_cart'].sum() / df['clicks'].sum()) * 100,
    'Add to Cart > Purchase': (1 - df['purchases'].sum() / df['add_to_cart'].sum()) * 100,
}

# ── Build visual ──
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('Least Negative Impact Analysis\nWhat Is Working Well vs What Is Hurting',
             fontsize=20, fontweight='bold', color='#00d2ff')

# Panel 1: Queries by revenue loss
ax = axes[0, 0]
med = query_loss['revenue_loss'].median()
colors = ['#00ff88' if v < med else '#e94560' for v in query_loss['revenue_loss']]
ax.barh(range(len(query_loss)), query_loss['revenue_loss'], color=colors)
ax.set_yticks(range(len(query_loss)))
ax.set_yticklabels(query_loss['query'], fontsize=9)
ax.set_xlabel('Revenue Loss ($)')
ax.set_title('Revenue Loss by Query (Least to Most)', fontweight='bold', color='#00d2ff')
ax.grid(True, alpha=0.3, axis='x')
ax.annotate(
    'LEAST IMPACT\n$' + f'{query_loss.iloc[0]["revenue_loss"]:,.0f}',
    xy=(query_loss.iloc[0]['revenue_loss'], 0),
    xytext=(query_loss['revenue_loss'].max() * 0.4, 1.5),
    arrowprops=dict(arrowstyle='->', color='#00ff88', lw=2),
    fontsize=12, color='#00ff88', fontweight='bold',
    bbox=dict(facecolor='#1a1a2e', edgecolor='#00ff88', boxstyle='round,pad=0.4'))

# Panel 2: Funnel drop-offs
ax = axes[0, 1]
stages = sorted(funnel.items(), key=lambda x: x[1])
stage_names = [s[0] for s in stages]
stage_vals = [s[1] for s in stages]
colors_f = ['#00ff88', '#ffd700', '#e94560']
bars = ax.barh(range(len(stages)), stage_vals, color=colors_f, height=0.5)
ax.set_yticks(range(len(stages)))
ax.set_yticklabels(stage_names, fontsize=11)
ax.set_xlabel('Drop-off Rate (%)')
ax.set_title('Funnel Drop-offs (Least to Most Damaging)', fontweight='bold', color='#00d2ff')
for i, (bar, val) in enumerate(zip(bars, stage_vals)):
    ax.text(val + 0.5, i, f'{val:.1f}%', va='center', fontweight='bold', color=colors_f[i], fontsize=13)
ax.grid(True, alpha=0.3, axis='x')
ax.annotate('LEAST DAMAGING', xy=(stage_vals[0], 0),
            xytext=(stage_vals[0] + 15, 0.3),
            arrowprops=dict(arrowstyle='->', color='#00ff88', lw=2),
            fontsize=11, color='#00ff88', fontweight='bold')

# Panel 3: Products with least revenue loss
ax = axes[1, 0]
labels = [f"{r['product'][:22]}\n({r['query'][:18]})" for _, r in least_loss.iterrows()]
ax.barh(range(len(least_loss)), least_loss['revenue_loss'], color='#00ff88', alpha=0.8)
ax.set_yticks(range(len(least_loss)))
ax.set_yticklabels(labels, fontsize=7)
ax.set_xlabel('Revenue Loss ($)')
ax.set_title('Products with Least Revenue Loss (Best Positioned)', fontweight='bold', color='#00d2ff')
ax.grid(True, alpha=0.3, axis='x')

# Panel 4: Summary
ax = axes[1, 1]
ax.axis('off')

least_q = query_loss.iloc[0]
lines = [
    'LEAST NEGATIVE IMPACT SUMMARY',
    '',
    'BEST QUERY:',
    f'  "{least_q["query"]}"',
    f'  Only ${least_q["revenue_loss"]:,.0f} revenue loss',
    f'  Products are well-matched to their positions.',
    '',
    'HEALTHIEST FUNNEL STAGE:',
    f'  "{stage_names[0]}"',
    f'  Only {stage_vals[0]:.1f}% drop-off',
    f'  Customers who add to cart mostly buy.',
    '',
    'MOST DAMAGING STAGE:',
    f'  "{stage_names[-1]}"',
    f'  {stage_vals[-1]:.1f}% drop-off',
    '',
    'BOTTOM LINE:',
    '  The purchase funnel (cart to buy) is healthy.',
    '  The real problem is getting users to CLICK.',
    f'  {stage_vals[-1]:.1f}% of impressions get zero clicks.',
]

ax.text(0.05, 0.95, '\n'.join(lines), transform=ax.transAxes, fontsize=12,
        verticalalignment='top', fontfamily='monospace', color='#eee',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#16213e',
                  edgecolor='#00d2ff', linewidth=2))

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('output/least_negative_impact.png', bbox_inches='tight')
plt.close()

print('Saved: output/least_negative_impact.png')
print(f'Least impacted query: {least_q["query"]} (${least_q["revenue_loss"]:,.0f} loss)')
print(f'Least damaging funnel stage: {stage_names[0]} ({stage_vals[0]:.1f}% drop)')
print(f'Most damaging funnel stage: {stage_names[-1]} ({stage_vals[-1]:.1f}% drop)')
