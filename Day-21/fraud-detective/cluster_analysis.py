"""
Deep dive: When and where do anomalies cluster?
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'figure.facecolor': '#0f0f0f', 'axes.facecolor': '#1a1a2e',
    'text.color': '#e0e0e0', 'axes.labelcolor': '#e0e0e0',
    'xtick.color': '#e0e0e0', 'ytick.color': '#e0e0e0',
    'axes.edgecolor': '#333', 'grid.color': '#333', 'grid.alpha': 0.3,
    'font.size': 10, 'figure.dpi': 150
})

df = pd.read_csv('data/transactions.csv', parse_dates=['timestamp'])
anomalies = df[df['hidden_anomaly_type'] != 'normal'].copy()
anomalies['hour'] = anomalies['timestamp'].dt.hour
anomalies['dow'] = anomalies['timestamp'].dt.dayofweek
anomalies['dow_name'] = anomalies['timestamp'].dt.day_name()
normal = df[df['hidden_anomaly_type'] == 'normal'].copy()
normal['hour'] = normal['timestamp'].dt.hour

print(f"Total anomalies: {len(anomalies)}")
print(f"Anomaly types: {anomalies['hidden_anomaly_type'].nunique()}")

# ── Build the visualization ────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 28))
gs = gridspec.GridSpec(5, 2, hspace=0.35, wspace=0.3, height_ratios=[1, 1, 1.2, 1, 1])

# ── 1. Hour-of-Day: Anomalies vs Normal (normalized) ──────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
anom_hourly = anomalies.groupby('hour').size()
norm_hourly = normal.groupby('hour').size()
# Normalize to rates
total_by_hour = df.groupby(df['timestamp'].dt.hour).size()
anom_rate = (anom_hourly / total_by_hour * 100).reindex(range(24), fill_value=0)

bars = ax1.bar(range(24), anom_rate, color=['#ff4444' if r > anom_rate.mean() + anom_rate.std() else '#ff8c00' if r > anom_rate.mean() else '#4ecdc4' for r in anom_rate], edgecolor='none')
ax1.axhline(y=anom_rate.mean(), color='#ffff00', linestyle='--', linewidth=1.5, label=f'Avg ({anom_rate.mean():.1f}%)')
ax1.set_xlabel('Hour of Day')
ax1.set_ylabel('Anomaly Rate (%)')
ax1.set_title('ANOMALY RATE BY HOUR', fontweight='bold', fontsize=13, color='#ff4444')
ax1.set_xticks(range(0, 24, 2))
ax1.legend(fontsize=9)
# Annotate peak
peak_hour = anom_rate.idxmax()
ax1.annotate(f'Peak: {peak_hour}:00\n({anom_rate[peak_hour]:.1f}%)', xy=(peak_hour, anom_rate[peak_hour]),
            xytext=(peak_hour+2, anom_rate[peak_hour]+1), fontsize=9, color='#ff4444',
            arrowprops=dict(arrowstyle='->', color='#ff4444'))

# ── 2. Anomaly Count by Hour (stacked by type) ────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
type_hour = anomalies.groupby(['hour', 'hidden_anomaly_type']).size().unstack(fill_value=0)
type_colors = {'stolen_card': '#ff4444', 'card_testing_fraud': '#ff8c00', 'employee_refund_fraud': '#ffd700',
               'bot_traffic': '#4ecdc4', 'price_glitch': '#a855f7', 'data_entry_error': '#888',
               'discount_abuse': '#22d3ee', 'account_takeover': '#f472b6', 'round_number_fraud': '#84cc16'}
type_hour.plot(kind='bar', stacked=True, ax=ax2, color=[type_colors.get(c, '#666') for c in type_hour.columns],
               width=0.85, edgecolor='none')
ax2.set_xlabel('Hour of Day')
ax2.set_ylabel('Anomaly Count')
ax2.set_title('ANOMALIES BY HOUR & TYPE', fontweight='bold', fontsize=13, color='#ff4444')
ax2.legend(fontsize=7, loc='upper left', ncol=2)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0, fontsize=8)

# ── 3. Location Breakdown ─────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
loc_counts = anomalies.groupby('store_location').size().sort_values(ascending=True)
loc_total = df.groupby('store_location').size()
loc_rate = (anomalies.groupby('store_location').size() / loc_total * 100).sort_values(ascending=True)

colors = ['#ff4444' if r > loc_rate.mean() + loc_rate.std() else '#ff8c00' if r > loc_rate.mean() else '#4ecdc4' for r in loc_rate]
ax3.barh(loc_rate.index, loc_rate.values, color=colors, edgecolor='none')
ax3.axvline(x=loc_rate.mean(), color='#ffff00', linestyle='--', linewidth=1.5, label=f'Avg ({loc_rate.mean():.1f}%)')
ax3.set_xlabel('Anomaly Rate (%)')
ax3.set_title('ANOMALY RATE BY STORE LOCATION', fontweight='bold', fontsize=13, color='#ff4444')
ax3.legend(fontsize=9)
for i, (loc, rate) in enumerate(loc_rate.items()):
    count = loc_counts.get(loc, 0)
    ax3.text(rate + 0.3, i, f'{count} anomalies', va='center', fontsize=8, color='#aaa')

# ── 4. Location x Anomaly Type heatmap ────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
loc_type = anomalies.groupby(['store_location', 'hidden_anomaly_type']).size().unstack(fill_value=0)
sns.heatmap(loc_type, cmap='YlOrRd', ax=ax4, linewidths=0.5, linecolor='#333',
            cbar_kws={'label': 'Count'}, annot=True, fmt='d', annot_kws={'fontsize': 7})
ax4.set_title('CRIME TYPE BY LOCATION', fontweight='bold', fontsize=13, color='#ff4444')
ax4.set_ylabel('')
ax4.tick_params(axis='x', rotation=35)
ax4.tick_params(axis='y', rotation=0)

# ── 5. Hour x Day-of-Week heatmap per anomaly type (top 4) ────────────────────
top4_types = anomalies['hidden_anomaly_type'].value_counts().head(4).index
for idx, atype in enumerate(top4_types):
    ax = fig.add_subplot(gs[2, idx % 2]) if idx < 2 else fig.add_subplot(gs[3, idx % 2])
    type_data = anomalies[anomalies['hidden_anomaly_type'] == atype]
    hm = type_data.groupby(['hour', 'dow']).size().unstack(fill_value=0)
    for d in range(7):
        if d not in hm.columns:
            hm[d] = 0
    for h in range(24):
        if h not in hm.index:
            hm.loc[h] = 0
    hm = hm.sort_index()[sorted(hm.columns)]
    day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    sns.heatmap(hm, cmap='YlOrRd', ax=ax, linewidths=0.3, linecolor='#222',
                xticklabels=day_labels, cbar_kws={'label': 'Count'})
    ax.set_title(f'{atype.upper().replace("_"," ")}', fontweight='bold', fontsize=12, color=type_colors.get(atype, '#ff4444'))
    ax.set_ylabel('Hour' if idx % 2 == 0 else '')
    ax.set_xlabel('')

# ── 6. Country breakdown ──────────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[4, 0])
country_anom = anomalies.groupby('country').size().sort_values(ascending=True)
country_total = df.groupby('country').size()
country_rate = (country_anom / country_total.reindex(country_anom.index) * 100).sort_values(ascending=True)
colors = ['#ff4444' if r > country_rate.mean() + country_rate.std() else '#4ecdc4' for r in country_rate]
ax6.barh(country_rate.index, country_rate.values, color=colors, edgecolor='none')
ax6.axvline(x=country_rate.mean(), color='#ffff00', linestyle='--', linewidth=1.5, label=f'Avg ({country_rate.mean():.1f}%)')
ax6.set_xlabel('Anomaly Rate (%)')
ax6.set_title('ANOMALY RATE BY COUNTRY', fontweight='bold', fontsize=13, color='#ff4444')
ax6.legend(fontsize=9)

# ── 7. Time-of-day profile per crime type (radar-like bar chart) ───────────────
ax7 = fig.add_subplot(gs[4, 1])
# Show when each crime type peaks
type_peak = {}
for atype in anomalies['hidden_anomaly_type'].unique():
    hourly = anomalies[anomalies['hidden_anomaly_type'] == atype].groupby('hour').size()
    if len(hourly) > 0:
        peak = hourly.idxmax()
        type_peak[atype] = {'peak_hour': peak, 'count_at_peak': hourly[peak], 'total': len(anomalies[anomalies['hidden_anomaly_type'] == atype])}

peak_df = pd.DataFrame(type_peak).T.sort_values('peak_hour')
y_pos = range(len(peak_df))
ax7.barh(y_pos, peak_df['peak_hour'], color=[type_colors.get(t, '#666') for t in peak_df.index],
         height=0.6, edgecolor='none')
ax7.set_yticks(y_pos)
ax7.set_yticklabels([t.replace('_', ' ').title() for t in peak_df.index], fontsize=9)
ax7.set_xlabel('Peak Hour of Day')
ax7.set_title('PEAK ACTIVITY HOUR BY CRIME TYPE', fontweight='bold', fontsize=13, color='#ff4444')
ax7.set_xticks(range(0, 24, 3))
ax7.set_xticklabels([f'{h}:00' for h in range(0, 24, 3)])
for i, (atype, row) in enumerate(peak_df.iterrows()):
    ax7.text(row['peak_hour'] + 0.3, i, f"{int(row['peak_hour'])}:00 ({int(row['total'])} total)",
            va='center', fontsize=8, color='#aaa')

fig.suptitle('ANOMALY CLUSTERING DEEP DIVE\nWhen & Where Do Crimes Happen?',
            fontsize=20, fontweight='bold', color='#ff4444', y=0.995)

plt.savefig('output/anomaly_clustering_deepdive.png', bbox_inches='tight')
plt.close()
print("Saved: output/anomaly_clustering_deepdive.png")

# ── Print summary ──────────────────────────────────────────────────────────────
print("\n=== TIME CLUSTERING ===")
print(f"Peak anomaly hour: {peak_hour}:00 ({anom_rate[peak_hour]:.1f}% anomaly rate)")
danger_hours = anom_rate[anom_rate > anom_rate.mean() + anom_rate.std()].sort_values(ascending=False)
print(f"Danger hours (>{anom_rate.mean()+anom_rate.std():.1f}% rate): {', '.join(f'{h}:00' for h in danger_hours.index)}")

print("\n=== LOCATION CLUSTERING ===")
print(f"Highest anomaly rate store: {loc_rate.index[-1]} ({loc_rate.iloc[-1]:.1f}%)")
for loc in loc_rate.index[-3:]:
    top_type = anomalies[anomalies['store_location'] == loc]['hidden_anomaly_type'].value_counts().index[0]
    print(f"  {loc}: {loc_rate[loc]:.1f}% anomaly rate, top crime: {top_type}")

print("\n=== COUNTRY CLUSTERING ===")
for c in country_rate.index[-3:]:
    print(f"  {c}: {country_rate[c]:.1f}% anomaly rate ({country_anom[c]} anomalies)")
