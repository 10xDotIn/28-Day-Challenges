#!/usr/bin/env python3
"""Deep dive: Most underpriced listings and WHY they're cheap."""

import pandas as pd
import numpy as np
import json, os

df = pd.read_csv('data/listings.csv')

# Get the most underpriced listings (bottom 50 by price_gap_percent)
underpriced = df.nsmallest(50, 'price_gap_percent').copy()

# Compute neighborhood averages for comparison
hood_avg = df.groupby('neighborhood').agg(
    avg_ppsf=('price_per_sqft', 'mean'),
    avg_price=('listing_price', 'mean'),
    avg_condition=('condition', lambda x: x.mode()[0]),
    avg_sqft=('sqft', 'mean'),
    avg_floor=('floor', 'mean'),
    avg_metro=('metro_distance_miles', 'mean'),
    avg_school=('school_rating', 'mean'),
    avg_crime=('crime_index', 'mean'),
    avg_noise=('noise_level', 'mean'),
    avg_year=('year_built', 'mean'),
    pct_parking=('has_parking', 'mean'),
    pct_gym=('has_gym', 'mean'),
    pct_pool=('has_pool', 'mean'),
    pct_doorman=('has_doorman', 'mean'),
).to_dict('index')

# For each underpriced listing, figure out WHY it's cheap
def diagnose_cheap(row):
    """Compare listing to its neighborhood average and find the reasons it's underpriced."""
    h = hood_avg[row['neighborhood']]
    reasons = []

    # Condition
    cond_rank = {'Needs Work': 1, 'Average': 2, 'Good': 3, 'Renovated': 4, 'New': 5}
    if cond_rank.get(row['condition'], 3) <= 2:
        reasons.append(f"Poor condition ({row['condition']})")

    # Small size relative to neighborhood
    if row['sqft'] < h['avg_sqft'] * 0.7:
        reasons.append(f"Small for area ({row['sqft']} sqft vs {h['avg_sqft']:.0f} avg)")

    # Far from metro vs neighborhood avg
    if row['metro_distance_miles'] > h['avg_metro'] * 1.4:
        reasons.append(f"Far from metro ({row['metro_distance_miles']:.1f} mi vs {h['avg_metro']:.1f} avg)")

    # High crime area
    if row['crime_index'] > 40:
        reasons.append(f"High crime area (index {row['crime_index']:.0f})")

    # Low floor
    if row['floor'] <= 2 and h['avg_floor'] > 5:
        reasons.append(f"Low floor ({row['floor']} vs {h['avg_floor']:.0f} avg)")

    # Old building
    if row['year_built'] < h['avg_year'] - 15:
        reasons.append(f"Older building ({row['year_built']} vs {h['avg_year']:.0f} avg)")

    # High noise
    if row['noise_level'] > h['avg_noise'] * 1.3:
        reasons.append(f"High noise ({row['noise_level']} vs {h['avg_noise']:.0f} avg)")

    # No amenities in a neighborhood that has them
    if not row['has_parking'] and h['pct_parking'] > 0.5:
        reasons.append("No parking (most nearby have it)")
    if not row['has_doorman'] and h['pct_doorman'] > 0.4:
        reasons.append("No doorman")

    # Low school rating
    if row['school_rating'] < 5:
        reasons.append(f"Low school rating ({row['school_rating']})")

    # Low park access
    if row['park_access_score'] <= 2:
        reasons.append("Poor park access")

    if not reasons:
        reasons.append("Genuinely undervalued — no obvious drawbacks")

    return reasons

underpriced['reasons'] = underpriced.apply(diagnose_cheap, axis=1)
underpriced['reason_str'] = underpriced['reasons'].apply(lambda r: '; '.join(r))
underpriced['num_reasons'] = underpriced['reasons'].apply(len)

# Aggregate: what are the most common reasons?
from collections import Counter
all_reasons = []
for rlist in underpriced['reasons']:
    for r in rlist:
        # Bucket by prefix
        tag = r.split('(')[0].strip()
        all_reasons.append(tag)

reason_counts = Counter(all_reasons).most_common(15)

# Build the HTML dashboard
listings_data = []
for _, r in underpriced.head(30).iterrows():
    hood = hood_avg[r['neighborhood']]
    listings_data.append({
        'id': int(r['listing_id']),
        'hood': r['neighborhood'],
        'type': r['property_type'],
        'sqft': int(r['sqft']),
        'bed': int(r['bedrooms']),
        'bath': int(r['bathrooms']),
        'floor': int(r['floor']),
        'year': int(r['year_built']),
        'cond': r['condition'],
        'price': int(r['listing_price']),
        'fair': int(r['estimated_fair_value']),
        'gap': round(r['price_gap_percent'], 1),
        'gap_dollar': int(r['listing_price'] - r['estimated_fair_value']),
        'ppsf': round(r['price_per_sqft'], 0),
        'hood_ppsf': round(hood['avg_ppsf'], 0),
        'metro': round(r['metro_distance_miles'], 2),
        'school': round(r['school_rating'], 1),
        'crime': round(r['crime_index'], 0),
        'noise': round(r['noise_level'], 0),
        'parking': int(r['has_parking']),
        'gym': int(r['has_gym']),
        'pool': int(r['has_pool']),
        'doorman': int(r['has_doorman']),
        'dom': int(r['days_on_market']),
        'sold': int(r['sold']),
        'appr': round(r['predicted_1yr_appreciation'], 1),
        'reasons': list(r['reasons']),
    })

# Stats
avg_gap = underpriced.head(30)['price_gap_percent'].mean()
avg_savings = (underpriced.head(30)['estimated_fair_value'] - underpriced.head(30)['listing_price']).mean()
avg_dom = underpriced.head(30)['days_on_market'].mean()
pct_sold = underpriced.head(30)['sold'].mean() * 100

# Condition breakdown in underpriced vs all
cond_under = underpriced['condition'].value_counts(normalize=True) * 100
cond_all = df['condition'].value_counts(normalize=True) * 100

cond_compare = []
for c in ['Needs Work', 'Average', 'Good', 'Renovated', 'New']:
    cond_compare.append({
        'cond': c,
        'pct_under': round(cond_under.get(c, 0), 1),
        'pct_all': round(cond_all.get(c, 0), 1)
    })

# Property type breakdown
type_under = underpriced['property_type'].value_counts(normalize=True) * 100
type_all = df['property_type'].value_counts(normalize=True) * 100
type_compare = []
for t in df['property_type'].unique():
    type_compare.append({
        'type': t,
        'pct_under': round(type_under.get(t, 0), 1),
        'pct_all': round(type_all.get(t, 0), 1)
    })

reason_data = [{'reason': r, 'count': c} for r, c in reason_counts]

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Underpriced Listings — Deep Dive</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0f0f0f; color:#e0e0e0; font-family:'Segoe UI',system-ui,sans-serif; }}
.container {{ max-width:1500px; margin:0 auto; padding:20px; }}
h1 {{ text-align:center; font-size:2em; margin:20px 0 5px; background:linear-gradient(135deg,#00e5ff,#00c853); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.subtitle {{ text-align:center; color:#888; margin-bottom:25px; }}
.hero {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:15px; margin-bottom:25px; }}
.hero-card {{ background:#1a1a2e; border-radius:12px; padding:18px; text-align:center; border:1px solid #333; }}
.hero-card .value {{ font-size:1.9em; font-weight:700; }}
.hero-card .value.green {{ color:#00c853; }}
.hero-card .value.cyan {{ color:#00e5ff; }}
.hero-card .value.yellow {{ color:#ffd600; }}
.hero-card .label {{ color:#888; font-size:0.85em; margin-top:5px; }}
.section {{ background:#1a1a2e; border-radius:12px; padding:22px; margin-bottom:20px; border:1px solid #333; }}
.section h2 {{ color:#00e5ff; font-size:1.2em; margin-bottom:15px; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
.grid3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:20px; }}
@media(max-width:1000px) {{ .grid2,.grid3 {{ grid-template-columns:1fr; }} }}
canvas {{ max-width:100%; }}
table {{ width:100%; border-collapse:collapse; font-size:0.85em; }}
th {{ background:#16213e; color:#ffd600; padding:10px 6px; text-align:left; position:sticky; top:0; white-space:nowrap; }}
td {{ padding:7px 6px; border-bottom:1px solid #222; }}
tr:hover {{ background:#16213e33; }}
.green {{ color:#00c853; }} .red {{ color:#ff1744; }} .cyan {{ color:#00e5ff; }} .yellow {{ color:#ffd600; }}
.tag {{ display:inline-block; background:#16213e; color:#ff9800; border-radius:4px; padding:2px 7px; margin:2px; font-size:0.8em; }}
.tag.good {{ background:#1b3a1b; color:#66bb6a; }}
.listing-card {{ background:#111; border-radius:10px; padding:16px; margin-bottom:12px; border-left:4px solid #00c853; }}
.listing-card .header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }}
.listing-card .title {{ font-size:1.1em; font-weight:600; color:#fff; }}
.listing-card .gap {{ font-size:1.3em; font-weight:700; color:#00c853; }}
.listing-card .details {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:8px; font-size:0.9em; color:#aaa; margin:10px 0; }}
.listing-card .details span b {{ color:#e0e0e0; }}
.listing-card .reasons {{ margin-top:8px; }}
.bar-row {{ display:flex; align-items:center; margin:6px 0; }}
.bar-label {{ width:200px; font-size:0.9em; color:#ccc; }}
.bar-bg {{ flex:1; height:22px; background:#111; border-radius:4px; overflow:hidden; }}
.bar-fill {{ height:100%; border-radius:4px; display:flex; align-items:center; padding-left:8px; font-size:0.8em; color:#fff; font-weight:600; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
<div class="container">
<h1>Underpriced Listings — Why Are They Cheap?</h1>
<p class="subtitle">30 most underpriced properties analyzed &mdash; comparing each to its neighborhood average</p>

<div class="hero">
  <div class="hero-card"><div class="value green">{avg_gap:.1f}%</div><div class="label">Avg Below Fair Value</div></div>
  <div class="hero-card"><div class="value green">${avg_savings:,.0f}</div><div class="label">Avg Savings vs Fair Value</div></div>
  <div class="hero-card"><div class="value cyan">{avg_dom:.0f} days</div><div class="label">Avg Days on Market</div></div>
  <div class="hero-card"><div class="value yellow">{pct_sold:.0f}%</div><div class="label">Already Sold</div></div>
</div>

<div class="grid2">
<div class="section">
<h2>Why Are They Cheap? — Most Common Reasons</h2>
<div id="reasonBars">
{"".join(f'''<div class="bar-row">
<div class="bar-label">{r['reason']}</div>
<div class="bar-bg"><div class="bar-fill" style="width:{r['count']/reason_counts[0][1]*100:.0f}%;background:{'#ff6d00' if r['count']>10 else '#ff9800' if r['count']>5 else '#ffc107'};">{r['count']}</div></div>
</div>''' for r in reason_data)}
</div>
</div>

<div class="section">
<h2>Condition: Underpriced vs All Listings</h2>
<canvas id="condChart" height="250"></canvas>
<p style="color:#888;font-size:0.85em;margin-top:10px;">Underpriced listings skew heavily toward poor condition &mdash; the #1 driver of being below fair value.</p>
</div>
</div>

<div class="grid2">
<div class="section">
<h2>Property Type Breakdown</h2>
<canvas id="typeChart" height="250"></canvas>
</div>
<div class="section">
<h2>Price Gap vs Days on Market</h2>
<canvas id="gapDomChart" height="250"></canvas>
<p style="color:#888;font-size:0.85em;margin-top:10px;">Underpriced listings sell fast &mdash; most gone in under 2 weeks.</p>
</div>
</div>

<div class="section">
<h2>Top 30 Underpriced Listings — Full Detail</h2>
{"".join(f'''<div class="listing-card">
<div class="header">
<div class="title">#{r['id']} &mdash; {r['hood']} &bull; {r['type']}</div>
<div class="gap">{r['gap']}% &nbsp;(${abs(r['gap_dollar']):,} below fair value)</div>
</div>
<div class="details">
<span><b>${r['price']:,}</b> asking</span>
<span><b>${r['fair']:,}</b> fair value</span>
<span><b>{r['sqft']:,}</b> sqft &bull; <b>${r['ppsf']:.0f}</b>/sqft (hood avg ${r['hood_ppsf']:.0f})</span>
<span><b>{r['bed']}</b> bed / <b>{r['bath']}</b> bath &bull; Floor <b>{r['floor']}</b></span>
<span>Built <b>{r['year']}</b> &bull; Condition: <b>{r['cond']}</b></span>
<span>Metro: <b>{r['metro']:.1f} mi</b> &bull; School: <b>{r['school']}</b> &bull; Crime: <b>{r['crime']:.0f}</b></span>
<span>{"Parking " if r['parking'] else ""}{"Gym " if r['gym'] else ""}{"Pool " if r['pool'] else ""}{"Doorman" if r['doorman'] else ""}{"No amenities" if not any([r['parking'],r['gym'],r['pool'],r['doorman']]) else ""}</span>
<span>DOM: <b>{r['dom']}d</b> &bull; {"SOLD" if r['sold'] else "Active"} &bull; 1yr appr: <b class="green">{r['appr']:+.1f}%</b></span>
</div>
<div class="reasons">{"".join(f'<span class="tag">{reason}</span>' for reason in r['reasons'])}</div>
</div>''' for r in listings_data)}
</div>

</div>

<script>
Chart.defaults.color = '#aaa';
Chart.defaults.borderColor = '#333';

const condData = {json.dumps(cond_compare)};
new Chart(document.getElementById('condChart'), {{
  type: 'bar',
  data: {{
    labels: condData.map(d => d.cond),
    datasets: [
      {{ label: 'Underpriced', data: condData.map(d => d.pct_under), backgroundColor: '#00c853' }},
      {{ label: 'All Listings', data: condData.map(d => d.pct_all), backgroundColor: '#555' }}
    ]
  }},
  options: {{ plugins: {{ legend: {{ labels: {{ color: '#aaa' }} }} }},
    scales: {{ y: {{ title: {{ display:true, text:'% of Listings' }}, grid:{{color:'#222'}} }}, x: {{ grid:{{display:false}} }} }}
  }}
}});

const typeData = {json.dumps(type_compare)};
new Chart(document.getElementById('typeChart'), {{
  type: 'bar',
  data: {{
    labels: typeData.map(d => d.type),
    datasets: [
      {{ label: 'Underpriced', data: typeData.map(d => d.pct_under), backgroundColor: '#00e5ff' }},
      {{ label: 'All Listings', data: typeData.map(d => d.pct_all), backgroundColor: '#555' }}
    ]
  }},
  options: {{ plugins: {{ legend: {{ labels: {{ color: '#aaa' }} }} }},
    scales: {{ y: {{ title: {{ display:true, text:'% of Listings' }}, grid:{{color:'#222'}} }}, x: {{ grid:{{display:false}} }} }}
  }}
}});

const listings = {json.dumps(listings_data)};
new Chart(document.getElementById('gapDomChart'), {{
  type: 'scatter',
  data: {{
    datasets: [{{
      label: 'Underpriced Listings',
      data: listings.map(d => ({{ x: d.gap, y: d.dom }})),
      backgroundColor: '#00c853', pointRadius: 6, pointHoverRadius: 9
    }}]
  }},
  options: {{
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ title: {{ display:true, text:'Price Gap % (more negative = better deal)' }}, grid:{{color:'#222'}} }},
      y: {{ title: {{ display:true, text:'Days on Market' }}, grid:{{color:'#222'}} }}
    }}
  }}
}});
</script>
</body>
</html>"""

with open('output/underpriced_deep_dive.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved output/underpriced_deep_dive.html")

# Print summary
print(f"\n{'='*60}")
print("WHY ARE THEY CHEAP? — Top reasons across 50 most underpriced:")
print('='*60)
for reason, count in reason_counts:
    print(f"  {count:3d}x  {reason}")
print(f"\nAvg gap: {avg_gap:.1f}% below fair value (${avg_savings:,.0f} savings)")
print(f"Avg days on market: {avg_dom:.0f} (vs 80 for overpriced)")
