"""
Fraud Detective — Anomaly Hunter
Forensic analysis of 14K+ transactions to find 9 types of hidden anomalies.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# ── Setup ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0f0f0f', 'axes.facecolor': '#1a1a2e',
    'text.color': '#e0e0e0', 'axes.labelcolor': '#e0e0e0',
    'xtick.color': '#e0e0e0', 'ytick.color': '#e0e0e0',
    'axes.edgecolor': '#333', 'grid.color': '#333', 'grid.alpha': 0.3,
    'font.size': 10, 'figure.dpi': 150
})

os.makedirs('output', exist_ok=True)
df = pd.read_csv('data/transactions.csv', parse_dates=['timestamp'])
print(f"Loaded {len(df)} transactions")
print(f"Columns: {list(df.columns)}")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

# Initialize suspicion scores
df['suspicion_score'] = 0
df['flags'] = ''

def add_flag(mask, score, flag_name):
    df.loc[mask, 'suspicion_score'] += score
    df.loc[mask, 'flags'] = df.loc[mask, 'flags'].apply(lambda x: f"{x}|{flag_name}" if x else flag_name)

# ═══════════════════════════════════════════════════════════════════════════════
# HUNT 1: IMPOSSIBLE GEOGRAPHY — Stolen Cards
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🔍 HUNT 1: Impossible Geography...")

stolen_card_cases = []
cards_with_countries = df[df['card_last_4'].notna()].copy()
cards_with_countries = cards_with_countries.sort_values('timestamp')

for card, group in cards_with_countries.groupby('card_last_4'):
    if group['country'].nunique() < 2:
        continue
    group = group.sort_values('timestamp')
    for i in range(len(group)):
        for j in range(i+1, len(group)):
            r1, r2 = group.iloc[i], group.iloc[j]
            time_diff = (r2['timestamp'] - r1['timestamp']).total_seconds() / 3600
            if 0 < time_diff <= 2 and r1['country'] != r2['country']:
                stolen_card_cases.append({
                    'card': card, 'tx1': r1['transaction_id'], 'tx2': r2['transaction_id'],
                    'country1': r1['country'], 'city1': r1['city'],
                    'country2': r2['country'], 'city2': r2['city'],
                    'time1': r1['timestamp'], 'time2': r2['timestamp'],
                    'time_diff_min': round(time_diff * 60, 1),
                    'amount1': r1['amount'], 'amount2': r2['amount']
                })

stolen_df = pd.DataFrame(stolen_card_cases)
if len(stolen_df) > 0:
    stolen_cards = set(stolen_df['card'])
    mask = df['card_last_4'].isin(stolen_cards)
    add_flag(mask, 30, 'STOLEN_CARD')
    print(f"  Found {len(stolen_cards)} stolen cards with {len(stolen_df)} impossible travel cases")
else:
    stolen_cards = set()
    print("  No impossible geography cases found")

# ═══════════════════════════════════════════════════════════════════════════════
# HUNT 2: RAPID-FIRE / CARD TESTING
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🔍 HUNT 2: Rapid-Fire Card Testing...")

card_testing_ips = []
ip_groups = df[df['ip_address'].notna()].groupby('ip_address')
for ip, group in ip_groups:
    small_txns = group[group['amount'] < 5].sort_values('timestamp')
    if len(small_txns) < 10:
        continue
    # Check for bursts within 1 hour
    for i in range(len(small_txns)):
        window = small_txns[(small_txns['timestamp'] >= small_txns.iloc[i]['timestamp']) &
                           (small_txns['timestamp'] <= small_txns.iloc[i]['timestamp'] + timedelta(hours=1))]
        if len(window) >= 20:
            card_testing_ips.append({
                'ip': ip, 'count_in_hour': len(window),
                'avg_amount': round(window['amount'].mean(), 2),
                'start_time': window['timestamp'].min()
            })
            break

card_testing_ip_set = set(x['ip'] for x in card_testing_ips)
# Also flag IPs with high volume of small transactions even if < 20/hr
rapid_ips = df[df['ip_address'].notna()].groupby('ip_address').agg(
    count=('transaction_id', 'count'),
    avg_amount=('amount', 'mean'),
    min_amount=('amount', 'min')
).reset_index()
rapid_ips = rapid_ips[(rapid_ips['count'] >= 10) & (rapid_ips['avg_amount'] < 5)]
card_testing_ip_set.update(rapid_ips['ip_address'])

mask = df['ip_address'].isin(card_testing_ip_set)
add_flag(mask, 25, 'CARD_TESTING')
print(f"  Found {len(card_testing_ip_set)} IPs with card testing patterns")

# ═══════════════════════════════════════════════════════════════════════════════
# HUNT 3: EMPLOYEE ANOMALIES
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🔍 HUNT 3: Employee Anomalies...")

emp_stats = df.groupby('employee_id').agg(
    total_txns=('transaction_id', 'count'),
    refund_count=('is_refund', 'sum'),
    avg_discount=('discount_applied_pct', 'mean'),
    max_discount=('discount_applied_pct', 'max'),
    avg_amount=('amount', 'mean'),
    total_amount=('amount', 'sum')
).reset_index()
emp_stats['refund_rate'] = emp_stats['refund_count'] / emp_stats['total_txns']

avg_refund_rate = emp_stats['refund_rate'].mean()
std_refund_rate = emp_stats['refund_rate'].std()
avg_discount = emp_stats['avg_discount'].mean()
std_discount = emp_stats['avg_discount'].std()

emp_stats['refund_zscore'] = (emp_stats['refund_rate'] - avg_refund_rate) / std_refund_rate
emp_stats['discount_zscore'] = (emp_stats['avg_discount'] - avg_discount) / std_discount
emp_stats['suspicion'] = emp_stats['refund_zscore'].abs() + emp_stats['discount_zscore'].abs()

# Ghost refunds — refunds without valid original_transaction_id
refunds = df[df['is_refund'] == 1].copy()
valid_tx_ids = set(df['transaction_id'])
refunds['is_ghost'] = ~refunds['original_transaction_id'].isin(valid_tx_ids)
ghost_by_emp = refunds[refunds['is_ghost']].groupby('employee_id').size().reset_index(name='ghost_refunds')
emp_stats = emp_stats.merge(ghost_by_emp, on='employee_id', how='left')
emp_stats['ghost_refunds'] = emp_stats['ghost_refunds'].fillna(0)

suspicious_emps = emp_stats[(emp_stats['refund_zscore'] > 2) | (emp_stats['discount_zscore'] > 2) |
                            (emp_stats['refund_rate'] > avg_refund_rate * 3) | (emp_stats['ghost_refunds'] > 2)]

for _, emp in suspicious_emps.iterrows():
    mask = df['employee_id'] == emp['employee_id']
    flags = []
    if emp['refund_zscore'] > 2 or emp['refund_rate'] > avg_refund_rate * 3:
        flags.append('HIGH_REFUND_RATE')
    if emp['discount_zscore'] > 2:
        flags.append('HIGH_DISCOUNT')
    if emp['ghost_refunds'] > 2:
        flags.append('GHOST_REFUNDS')
    add_flag(mask, 20, '|'.join(flags))

# Flag ghost refund transactions specifically
ghost_mask = (df['is_refund'] == 1) & (~df['original_transaction_id'].isin(valid_tx_ids)) & (df['original_transaction_id'].notna())
add_flag(ghost_mask, 15, 'GHOST_REFUND')

print(f"  Found {len(suspicious_emps)} suspicious employees")
print(f"  Ghost refunds: {ghost_mask.sum()}")

# ═══════════════════════════════════════════════════════════════════════════════
# HUNT 4: BOT DETECTION
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🔍 HUNT 4: Bot Detection...")

# Bots have processing times < 1 second or very uniform times
bot_mask_fast = df['processing_time_seconds'] < 1.0
# IPs with very uniform processing times (low std)
ip_proc = df[df['ip_address'].notna()].groupby('ip_address').agg(
    proc_std=('processing_time_seconds', 'std'),
    proc_mean=('processing_time_seconds', 'mean'),
    count=('transaction_id', 'count')
).reset_index()
bot_ips = ip_proc[(ip_proc['proc_std'] < 0.1) & (ip_proc['count'] >= 5) & (ip_proc['proc_mean'] < 1.5)]
bot_ip_set = set(bot_ips['ip_address'])

bot_mask = bot_mask_fast | df['ip_address'].isin(bot_ip_set)
add_flag(bot_mask, 20, 'BOT_TRAFFIC')
print(f"  Bot-speed transactions (<1s): {bot_mask_fast.sum()}")
print(f"  Suspicious bot IPs: {len(bot_ip_set)}")

# ═══════════════════════════════════════════════════════════════════════════════
# HUNT 5: PRICE GLITCHES
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🔍 HUNT 5: Price Glitches...")

cat_stats = df[df['is_refund'] == 0].groupby('category').agg(
    mean_amount=('amount', 'mean'),
    std_amount=('amount', 'std'),
    median_amount=('amount', 'median'),
    p5=('amount', lambda x: x.quantile(0.05))
).reset_index()

price_glitch_mask = pd.Series(False, index=df.index)
for _, cat in cat_stats.iterrows():
    threshold = max(cat['mean_amount'] - 3 * cat['std_amount'], cat['mean_amount'] * 0.1)
    cat_mask = (df['category'] == cat['category']) & (df['amount'] < threshold) & (df['amount'] > 0) & (df['is_refund'] == 0)
    price_glitch_mask |= cat_mask

add_flag(price_glitch_mask, 20, 'PRICE_GLITCH')
glitch_revenue_lost = 0
if price_glitch_mask.sum() > 0:
    for _, cat in cat_stats.iterrows():
        cat_glitches = df[price_glitch_mask & (df['category'] == cat['category'])]
        glitch_revenue_lost += (cat['median_amount'] - cat_glitches['amount']).sum()
print(f"  Price glitches found: {price_glitch_mask.sum()}, est. revenue lost: ${glitch_revenue_lost:,.0f}")

# ═══════════════════════════════════════════════════════════════════════════════
# HUNT 6: DATA CORRUPTION
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🔍 HUNT 6: Data Corruption...")

neg_items = df['items_count'] < 0
extreme_amount = df['amount'] > df['amount'].quantile(0.9999)
future_ts = df['timestamp'] > pd.Timestamp.now()
corruption_mask = neg_items | extreme_amount | future_ts
add_flag(corruption_mask, 15, 'DATA_CORRUPTION')
print(f"  Negative item counts: {neg_items.sum()}")
print(f"  Extreme amounts: {extreme_amount.sum()}")
print(f"  Future timestamps: {future_ts.sum()}")

# ═══════════════════════════════════════════════════════════════════════════════
# HUNT 7: DISCOUNT ABUSE
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🔍 HUNT 7: Discount Abuse...")

high_discount = df['discount_applied_pct'] > 50
add_flag(high_discount, 20, 'DISCOUNT_ABUSE')
discount_loss = df[high_discount].apply(
    lambda r: r['amount'] * (r['discount_applied_pct'] / 100) / (1 - r['discount_applied_pct']/100) if r['discount_applied_pct'] < 100 else r['amount'],
    axis=1
).sum() if high_discount.sum() > 0 else 0
print(f"  Excessive discounts (>50%): {high_discount.sum()}, est. loss: ${discount_loss:,.0f}")

# ═══════════════════════════════════════════════════════════════════════════════
# HUNT 8: ACCOUNT TAKEOVER
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🔍 HUNT 8: Account Takeover...")

takeover_cases = []
cust_groups = df.sort_values('timestamp').groupby('customer_id')

for cust, group in cust_groups:
    if len(group) < 3:
        continue
    group = group.sort_values('timestamp')
    flags = []

    # Method 1: Many different cards in a short window (strong signal)
    unique_cards = group['card_last_4'].dropna().nunique()
    if unique_cards >= 5:
        flags.append('MULTI_NEW_CARDS')

    # Method 2: Spending spike - compare median to max burst
    if len(group) >= 4:
        split = max(1, int(len(group) * 0.3))
        early = group.iloc[:split]
        late = group.iloc[split:]
        if early['amount'].mean() > 0 and late['amount'].mean() / early['amount'].mean() > 5:
            flags.append('SPENDING_SPIKE')

    # Method 3: Device change
    devices = group['device_type'].dropna().unique()
    if len(devices) >= 2:
        # Check if device changed between early and late transactions
        early_dev = group.iloc[:max(1, len(group)//3)]['device_type'].mode()
        late_dev = group.iloc[len(group)//3:]['device_type'].mode()
        if len(early_dev) > 0 and len(late_dev) > 0 and early_dev.iloc[0] != late_dev.iloc[0]:
            flags.append('DEVICE_CHANGE')

    # Method 4: City change
    cities = group['city'].dropna().unique()
    if len(cities) >= 2:
        early_city = group.iloc[:max(1, len(group)//3)]['city'].mode()
        late_city = group.iloc[len(group)//3:]['city'].mode()
        if len(early_city) > 0 and len(late_city) > 0 and early_city.iloc[0] != late_city.iloc[0]:
            flags.append('NEW_CITY')

    # Method 5: Rapid burst of transactions (many in a short window)
    if len(group) >= 5:
        # Check for any 2-hour window with 5+ transactions
        for i in range(len(group)):
            window = group[(group['timestamp'] >= group.iloc[i]['timestamp']) &
                          (group['timestamp'] <= group.iloc[i]['timestamp'] + pd.Timedelta(hours=2))]
            if len(window) >= 5:
                flags.append('RAPID_BURST')
                break

    if len(flags) >= 2:
        takeover_cases.append({
            'customer_id': cust, 'flags': '|'.join(flags),
            'early_avg_spend': round(group.iloc[:max(1,len(group)//3)]['amount'].mean(), 2),
            'late_avg_spend': round(group.iloc[len(group)//3:]['amount'].mean(), 2),
            'transactions': len(group)
        })
        mask = df['customer_id'] == cust
        add_flag(mask, 25, 'ACCOUNT_TAKEOVER')

print(f"  Account takeover suspects: {len(takeover_cases)}")

# ═══════════════════════════════════════════════════════════════════════════════
# HUNT 9: PATTERN CLUSTERING
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🔍 HUNT 9: Pattern Clustering...")

df['hour'] = df['timestamp'].dt.hour
df['dow'] = df['timestamp'].dt.dayofweek
anomaly_df = df[df['suspicion_score'] > 0].copy()

hour_counts = anomaly_df.groupby('hour').size()
store_counts = anomaly_df.groupby('store_location').size().sort_values(ascending=False)
emp_counts = anomaly_df.groupby('employee_id').size().sort_values(ascending=False)

# Heatmap data
heatmap_data = anomaly_df.groupby(['hour', 'dow']).size().unstack(fill_value=0)
# Fill missing
for d in range(7):
    if d not in heatmap_data.columns:
        heatmap_data[d] = 0
for h in range(24):
    if h not in heatmap_data.index:
        heatmap_data.loc[h] = 0
heatmap_data = heatmap_data.sort_index()
heatmap_data = heatmap_data[sorted(heatmap_data.columns)]

print(f"  Peak anomaly hour: {hour_counts.idxmax()}:00 ({hour_counts.max()} anomalies)")
print(f"  Top anomaly store: {store_counts.index[0]} ({store_counts.iloc[0]})")

# ═══════════════════════════════════════════════════════════════════════════════
# HUNT 10: ROUND NUMBER FRAUD (bonus)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🔍 HUNT 10: Round Number Fraud...")
# Round number fraud: exact round amounts ($100, $250, $500, $1000) with items_count=1
# in categories like Electronics and Gift Card — looks like money laundering or gift card fraud
round_amounts = {100, 250, 500, 1000}
round_mask = (df['amount'].isin(round_amounts)) & (df['items_count'] == 1) & (df['category'].isin(['Electronics', 'Gift Card']))
add_flag(round_mask, 15, 'ROUND_NUMBER')
print(f"  Round number fraud candidates: {round_mask.sum()}")

# ═══════════════════════════════════════════════════════════════════════════════
# SCORING & RANKING
# ═══════════════════════════════════════════════════════════════════════════════
print("\n📊 Scoring & Ranking...")

# Normalize scores to 0-100
max_score = df['suspicion_score'].max()
if max_score > 0:
    df['suspicion_score_norm'] = (df['suspicion_score'] / max_score * 100).clip(0, 100).astype(int)
else:
    df['suspicion_score_norm'] = 0

top50 = df.nlargest(50, 'suspicion_score')[['transaction_id', 'timestamp', 'customer_id', 'employee_id',
    'store_location', 'category', 'amount', 'suspicion_score_norm', 'flags']].copy()
top50.rename(columns={'suspicion_score_norm': 'score'}, inplace=True)

total_anomalies = (df['suspicion_score'] > 0).sum()
financial_impact = df[df['suspicion_score'] > 0]['amount'].sum()
fraud_rate = total_anomalies / len(df) * 100

print(f"  Total anomalies flagged: {total_anomalies}")
print(f"  Financial impact: ${financial_impact:,.0f}")
print(f"  Fraud rate: {fraud_rate:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION vs hidden_anomaly_type
# ═══════════════════════════════════════════════════════════════════════════════
print("\n✅ Validation against ground truth...")

anomaly_types = df['hidden_anomaly_type'].unique()
anomaly_types = [t for t in anomaly_types if t != 'normal']

validation = {}
for atype in anomaly_types:
    actual = df['hidden_anomaly_type'] == atype
    detected = df['suspicion_score'] > 0
    tp = (actual & detected).sum()
    fn = (actual & ~detected).sum()
    fp_in_type = 0  # not meaningful per-type
    total_actual = actual.sum()
    recall = tp / total_actual if total_actual > 0 else 0
    validation[atype] = {'total': total_actual, 'detected': tp, 'missed': fn, 'recall': f"{recall:.0%}"}
    print(f"  {atype}: {tp}/{total_actual} detected ({recall:.0%})")

# Overall
actual_any = df['hidden_anomaly_type'] != 'normal'
detected_any = df['suspicion_score'] > 0
overall_tp = (actual_any & detected_any).sum()
overall_recall = overall_tp / actual_any.sum() if actual_any.sum() > 0 else 0
overall_precision = overall_tp / detected_any.sum() if detected_any.sum() > 0 else 0
print(f"\n  Overall: {overall_tp}/{actual_any.sum()} anomalies detected ({overall_recall:.0%} recall)")
print(f"  Precision: {overall_precision:.0%}")

# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION 1: Stolen Card Timeline
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🎨 Creating visualizations...")

fig, ax = plt.subplots(figsize=(14, 7))
if len(stolen_df) > 0:
    unique_cards = stolen_df['card'].unique()[:8]
    colors = plt.cm.Set1(np.linspace(0, 1, len(unique_cards)))
    for idx, card in enumerate(unique_cards):
        card_data = stolen_df[stolen_df['card'] == card].iloc[0]
        times = [card_data['time1'], card_data['time2']]
        cities = [f"{card_data['city1']}, {card_data['country1']}", f"{card_data['city2']}, {card_data['country2']}"]
        ax.plot(times, [idx, idx], 'o-', color=colors[idx], markersize=10, linewidth=2.5, label=f"Card ****{int(card)}")
        for t, c in zip(times, cities):
            ax.annotate(c, (t, idx), textcoords="offset points", xytext=(0, 12),
                       fontsize=8, color=colors[idx], ha='center')
        ax.annotate(f"{card_data['time_diff_min']}min", (times[0] + (times[1]-times[0])/2, idx),
                   textcoords="offset points", xytext=(0, -15), fontsize=7, color='#ff6b6b', ha='center')

    ax.set_yticks(range(len(unique_cards)))
    ax.set_yticklabels([f"Card ****{int(c)}" for c in unique_cards])
    ax.legend(loc='upper right', fontsize=8)
ax.set_title('IMPOSSIBLE GEOGRAPHY — Stolen Card Detection', fontsize=16, fontweight='bold', color='#ff4444')
ax.set_xlabel('Time')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
plt.tight_layout()
plt.savefig('output/stolen_card_timeline.png', bbox_inches='tight')
plt.close()

# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION 2: Employee Watchlist
# ═══════════════════════════════════════════════════════════════════════════════
emp_ranked = emp_stats.sort_values('suspicion', ascending=True).tail(15)
fig, axes = plt.subplots(1, 3, figsize=(18, 8))

# Refund rate
ax = axes[0]
colors = ['#ff4444' if x > avg_refund_rate * 3 else '#4ecdc4' for x in emp_ranked['refund_rate']]
ax.barh(emp_ranked['employee_id'], emp_ranked['refund_rate'] * 100, color=colors)
ax.axvline(x=avg_refund_rate * 100, color='#ff6b6b', linestyle='--', label=f'Avg ({avg_refund_rate*100:.1f}%)')
ax.set_title('Refund Rate %', fontweight='bold', color='#ff4444')
ax.legend()

# Avg discount
ax = axes[1]
colors = ['#ff4444' if x > avg_discount + 2*std_discount else '#4ecdc4' for x in emp_ranked['avg_discount']]
ax.barh(emp_ranked['employee_id'], emp_ranked['avg_discount'], color=colors)
ax.axvline(x=avg_discount, color='#ff6b6b', linestyle='--', label=f'Avg ({avg_discount:.1f}%)')
ax.set_title('Avg Discount %', fontweight='bold', color='#ff4444')
ax.legend()

# Ghost refunds
ax = axes[2]
colors = ['#ff4444' if x > 2 else '#4ecdc4' for x in emp_ranked['ghost_refunds']]
ax.barh(emp_ranked['employee_id'], emp_ranked['ghost_refunds'], color=colors)
ax.set_title('Ghost Refunds', fontweight='bold', color='#ff4444')

fig.suptitle('EMPLOYEE WATCHLIST — Suspicion Rankings', fontsize=16, fontweight='bold', color='#ff4444', y=1.02)
plt.tight_layout()
plt.savefig('output/employee_watchlist.png', bbox_inches='tight')
plt.close()

# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION 3: Bot vs Human
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 6))
human_times = df[df['processing_time_seconds'] >= 1.0]['processing_time_seconds']
bot_times = df[df['processing_time_seconds'] < 1.0]['processing_time_seconds']

ax.hist(human_times, bins=80, alpha=0.7, color='#4ecdc4', label=f'Human ({len(human_times)})', density=True)
if len(bot_times) > 0:
    ax.hist(bot_times, bins=30, alpha=0.8, color='#ff4444', label=f'Bot ({len(bot_times)})', density=True)
ax.axvline(x=1.0, color='#ffff00', linestyle='--', linewidth=2, label='Bot/Human threshold (1s)')
ax.set_xlabel('Processing Time (seconds)')
ax.set_ylabel('Density')
ax.set_title('BOT vs HUMAN — Processing Time Distribution', fontsize=16, fontweight='bold', color='#ff4444')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig('output/bot_vs_human.png', bbox_inches='tight')
plt.close()

# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION 4: Price Glitch Report
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 7))
categories = df['category'].unique()
cat_colors = plt.cm.Set2(np.linspace(0, 1, len(categories)))
for idx, cat in enumerate(categories):
    cat_data = df[(df['category'] == cat) & (df['is_refund'] == 0)]
    normal = cat_data[~price_glitch_mask.reindex(cat_data.index, fill_value=False)]
    glitch = cat_data[price_glitch_mask.reindex(cat_data.index, fill_value=False)]
    ax.scatter([cat]*len(normal), normal['amount'], alpha=0.2, s=10, color=cat_colors[idx])
    if len(glitch) > 0:
        ax.scatter([cat]*len(glitch), glitch['amount'], color='#ff4444', s=50, marker='x',
                  zorder=5, label='Glitch' if idx == 0 else '')
ax.set_ylabel('Amount ($)')
ax.set_title('PRICE GLITCH DETECTION — Outliers by Category', fontsize=16, fontweight='bold', color='#ff4444')
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('output/price_glitch_report.png', bbox_inches='tight')
plt.close()

# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION 5: Anomaly Hotspots Heatmap
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 8))
day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
sns.heatmap(heatmap_data, cmap='YlOrRd', ax=ax, linewidths=0.5, linecolor='#333',
            xticklabels=day_labels, cbar_kws={'label': 'Anomaly Count'})
ax.set_ylabel('Hour of Day')
ax.set_xlabel('Day of Week')
ax.set_title('ANOMALY HOTSPOTS — When Crimes Happen', fontsize=16, fontweight='bold', color='#ff4444')
plt.tight_layout()
plt.savefig('output/anomaly_hotspots.png', bbox_inches='tight')
plt.close()

# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION 6: Suspicion Ranking
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 8))
top20 = top50.head(20).sort_values('score')
colors = ['#ff4444' if s >= 80 else '#ff8c00' if s >= 60 else '#ffd700' for s in top20['score']]
bars = ax.barh(top20['transaction_id'], top20['score'], color=colors)
for bar, flags in zip(bars, top20['flags']):
    short_flags = flags[:40] + '...' if len(flags) > 40 else flags
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, short_flags,
           va='center', fontsize=7, color='#aaa')
ax.set_xlabel('Suspicion Score')
ax.set_title('TOP 20 MOST SUSPICIOUS TRANSACTIONS', fontsize=16, fontweight='bold', color='#ff4444')
ax.set_xlim(0, 120)
plt.tight_layout()
plt.savefig('output/suspicion_ranking.png', bbox_inches='tight')
plt.close()

print("  All PNG visualizations saved!")

# ═══════════════════════════════════════════════════════════════════════════════
# INVESTIGATION REPORT (Markdown)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n📝 Writing investigation report...")

# Find most dangerous type
type_impact = df[df['hidden_anomaly_type'] != 'normal'].groupby('hidden_anomaly_type')['amount'].sum().sort_values(ascending=False)
most_dangerous = type_impact.index[0] if len(type_impact) > 0 else 'N/A'

# Highest risk employee
highest_risk_emp = emp_stats.sort_values('suspicion', ascending=False).iloc[0]['employee_id'] if len(emp_stats) > 0 else 'N/A'

report = f"""# FRAUD DETECTIVE — Investigation Report

## Executive Summary

> **Detected {total_anomalies} anomalies** across {len(df)} transactions, representing an estimated **${financial_impact:,.0f} in financial impact**. Fraud rate: **{fraud_rate:.1f}%** of all transactions.

---

## Crime-by-Crime Breakdown

### 1. Stolen Cards (Impossible Geography)
- **{len(stolen_cards)} cards** used in multiple countries within 2-hour windows
- These represent physically impossible travel scenarios
"""
if len(stolen_df) > 0:
    for _, case in stolen_df.head(10).iterrows():
        report += f"- Card ****{int(case['card'])}: {case['city1']}, {case['country1']} -> {case['city2']}, {case['country2']} in {case['time_diff_min']} minutes\n"

report += f"""
### 2. Card Testing Fraud
- **{len(card_testing_ip_set)} IPs** identified with rapid-fire small transactions
- Pattern: many sub-$5 charges in quick succession = testing stolen card numbers
"""
for ct in card_testing_ips[:5]:
    report += f"- IP {ct['ip']}: {ct['count_in_hour']} transactions/hour, avg ${ct['avg_amount']}\n"

report += f"""
### 3. Employee Anomalies
- **{len(suspicious_emps)} suspicious employees** identified
- Average refund rate: {avg_refund_rate*100:.1f}% | Average discount: {avg_discount:.1f}%
- Ghost refunds (no valid original transaction): {ghost_mask.sum()}

| Employee | Refund Rate | Avg Discount | Ghost Refunds | Suspicion Score |
|----------|------------|-------------|---------------|-----------------|
"""
for _, emp in emp_stats.sort_values('suspicion', ascending=False).head(10).iterrows():
    report += f"| {emp['employee_id']} | {emp['refund_rate']*100:.1f}% | {emp['avg_discount']:.1f}% | {int(emp['ghost_refunds'])} | {emp['suspicion']:.1f} |\n"

report += f"""
### 4. Bot Traffic
- **{bot_mask_fast.sum()} transactions** with sub-1-second processing times
- **{len(bot_ip_set)} IPs** with suspiciously uniform processing patterns
- Human processing times cluster around 3-5 seconds; bots spike below 1 second

### 5. Price Glitches
- **{price_glitch_mask.sum()} transactions** priced far below category norms
- Estimated revenue lost: **${glitch_revenue_lost:,.0f}**

### 6. Data Corruption
- Negative item counts: {neg_items.sum()}
- Extreme outlier amounts: {extreme_amount.sum()}
- Future timestamps: {future_ts.sum()}

### 7. Discount Abuse
- **{high_discount.sum()} transactions** with discounts > 50%
- Estimated loss from unauthorized discounts: **${discount_loss:,.0f}**

### 8. Account Takeovers
- **{len(takeover_cases)} customers** show signs of account compromise
"""
for case in takeover_cases[:5]:
    report += f"- {case['customer_id']}: {case['flags']} (spending ${case['early_avg_spend']} -> ${case['late_avg_spend']})\n"

report += f"""
---

## Hotspot Analysis

### Peak Anomaly Hours
"""
for hour in hour_counts.sort_values(ascending=False).head(5).index:
    report += f"- {hour}:00 — {hour_counts[hour]} anomalies\n"

report += f"""
### Top Anomaly Stores
"""
for store in store_counts.head(5).index:
    report += f"- {store}: {store_counts[store]} anomalies\n"

report += f"""
---

## Top 50 Most Suspicious Transactions

| Rank | Transaction ID | Amount | Score | Flags |
|------|---------------|--------|-------|-------|
"""
for rank, (_, row) in enumerate(top50.iterrows(), 1):
    report += f"| {rank} | {row['transaction_id']} | ${row['amount']:,.2f} | {row['score']} | {row['flags'][:50]} |\n"

report += f"""
---

## Detection Accuracy (vs Ground Truth)

| Anomaly Type | Total Planted | Detected | Missed | Recall |
|-------------|--------------|----------|--------|--------|
"""
for atype, v in sorted(validation.items(), key=lambda x: x[1]['total'], reverse=True):
    report += f"| {atype} | {v['total']} | {v['detected']} | {v['missed']} | {v['recall']} |\n"

report += f"""
| **OVERALL** | **{actual_any.sum()}** | **{overall_tp}** | **{(actual_any & ~detected_any).sum()}** | **{overall_recall:.0%}** |

Precision: **{overall_precision:.0%}** (of flagged transactions, how many were actual anomalies)

---

## 5 Immediate Actions

1. **Block stolen cards** — Immediately flag cards ****{', ****'.join(str(int(c)) for c in list(stolen_cards)[:3])} and investigate recent charges
2. **Investigate {highest_risk_emp}** — This employee has the highest anomaly suspicion score; review their transaction history and refund authorization
3. **Rate-limit card testing IPs** — Implement velocity checks: block IPs with >10 sub-$5 transactions per hour
4. **Fix price glitch vulnerability** — {price_glitch_mask.sum()} transactions exploited pricing errors; audit product price validation
5. **Add bot detection** — {bot_mask_fast.sum()} transactions processed in <1 second; add CAPTCHA or processing time floor

---

## Summary

| Metric | Value |
|--------|-------|
| Total Transactions | {len(df):,} |
| Anomalies Detected | {total_anomalies:,} |
| Financial Impact | ${financial_impact:,.0f} |
| Fraud Rate | {fraud_rate:.1f}% |
| Most Dangerous Type | {most_dangerous} |
| Highest Risk Employee | {highest_risk_emp} |
| Detection Recall | {overall_recall:.0%} |
| Detection Precision | {overall_precision:.0%} |
"""

with open('output/investigation_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD (HTML)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🖥️  Building dashboard...")

# Prepare data for charts
crime_type_counts = df[df['hidden_anomaly_type'] != 'normal']['hidden_anomaly_type'].value_counts()
top3_crimes = crime_type_counts.head(3)

store_anomaly_data = anomaly_df.groupby(['store_location', 'hour']).size().reset_index(name='count')

emp_chart_data = emp_stats.sort_values('suspicion', ascending=False).head(10)

top50_html_rows = ""
for _, row in top50.iterrows():
    score_color = '#ff4444' if row['score'] >= 80 else '#ff8c00' if row['score'] >= 60 else '#ffd700'
    top50_html_rows += f"""<tr>
        <td>{row['transaction_id']}</td>
        <td>{row['timestamp']}</td>
        <td>{row['employee_id']}</td>
        <td>${row['amount']:,.2f}</td>
        <td style="color:{score_color};font-weight:bold">{row['score']}</td>
        <td style="font-size:11px">{row['flags'][:60]}</td>
    </tr>"""

# Stolen card timeline HTML
stolen_timeline_html = ""
if len(stolen_df) > 0:
    for _, case in stolen_df.head(10).iterrows():
        stolen_timeline_html += f"""<div class="card-case">
            <span class="card-num">****{int(case['card'])}</span>
            <span class="route">{case['city1']}, {case['country1']} &rarr; {case['city2']}, {case['country2']}</span>
            <span class="time-badge">{case['time_diff_min']} min</span>
            <span class="amounts">${case['amount1']:.0f} &rarr; ${case['amount2']:.0f}</span>
        </div>"""

# Account takeover HTML
takeover_html = ""
for case in takeover_cases[:10]:
    takeover_html += f"""<div class="takeover-case">
        <span class="cust-id">{case['customer_id']}</span>
        <span class="flags-badge">{case['flags']}</span>
        <span class="spend-change">${case['early_avg_spend']} &rarr; ${case['late_avg_spend']}</span>
    </div>"""

# Validation table HTML
val_rows = ""
for atype, v in sorted(validation.items(), key=lambda x: x[1]['total'], reverse=True):
    recall_val = int(v['recall'].replace('%',''))
    recall_color = '#4ecdc4' if recall_val >= 70 else '#ff8c00' if recall_val >= 40 else '#ff4444'
    val_rows += f"""<tr>
        <td>{atype}</td><td>{v['total']}</td><td>{v['detected']}</td><td>{v['missed']}</td>
        <td style="color:{recall_color};font-weight:bold">{v['recall']}</td>
    </tr>"""

# Employee watchlist HTML
emp_rows = ""
for _, emp in emp_stats.sort_values('suspicion', ascending=False).head(10).iterrows():
    risk_color = '#ff4444' if emp['suspicion'] > 5 else '#ff8c00' if emp['suspicion'] > 3 else '#4ecdc4'
    emp_rows += f"""<tr>
        <td style="color:{risk_color};font-weight:bold">{emp['employee_id']}</td>
        <td>{emp['refund_rate']*100:.1f}%</td>
        <td>{emp['avg_discount']:.1f}%</td>
        <td>{int(emp['ghost_refunds'])}</td>
        <td>{emp['total_txns']}</td>
        <td style="color:{risk_color};font-weight:bold">{emp['suspicion']:.1f}</td>
    </tr>"""

# Heatmap data as JSON
heatmap_json = []
for h in range(24):
    row_data = []
    for d in range(7):
        val = heatmap_data.loc[h, d] if h in heatmap_data.index and d in heatmap_data.columns else 0
        row_data.append(int(val))
    heatmap_json.append(row_data)

# Bot data
bot_count = bot_mask.sum()
human_count = len(df) - bot_count

# Price glitch table
glitch_by_cat = df[price_glitch_mask].groupby('category').agg(
    count=('transaction_id', 'count'),
    avg_price=('amount', 'mean'),
).reset_index() if price_glitch_mask.sum() > 0 else pd.DataFrame()

glitch_rows = ""
for _, g in glitch_by_cat.iterrows() if len(glitch_by_cat) > 0 else []:
    cat_median = cat_stats[cat_stats['category'] == g['category']]['median_amount'].values[0]
    glitch_rows += f"""<tr>
        <td>{g['category']}</td><td>{g['count']}</td>
        <td>${g['avg_price']:.2f}</td><td>${cat_median:.2f}</td>
        <td style="color:#ff4444">${(cat_median - g['avg_price']) * g['count']:,.0f}</td>
    </tr>"""

dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fraud Detective — Investigation Dashboard</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0f0f0f; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}

/* Header */
.header {{ text-align: center; padding: 30px 0; border-bottom: 2px solid #ff4444; margin-bottom: 30px; }}
.header h1 {{ font-size: 2.5em; color: #ff4444; text-shadow: 0 0 20px rgba(255,68,68,0.3); letter-spacing: 3px; }}
.header .subtitle {{ color: #888; font-size: 1.1em; margin-top: 5px; }}

/* Alert Board */
.alert-board {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
.alert-card {{ background: #1a1a2e; border: 1px solid #333; border-radius: 10px; padding: 20px; text-align: center; }}
.alert-card.danger {{ border-color: #ff4444; box-shadow: 0 0 15px rgba(255,68,68,0.15); }}
.alert-card .value {{ font-size: 2.2em; font-weight: bold; margin: 8px 0; }}
.alert-card .label {{ color: #888; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; }}
.red {{ color: #ff4444; }} .green {{ color: #4ecdc4; }} .orange {{ color: #ff8c00; }} .yellow {{ color: #ffd700; }}

/* Sections */
.section {{ background: #1a1a2e; border: 1px solid #333; border-radius: 10px; padding: 25px; margin-bottom: 25px; }}
.section h2 {{ color: #ff4444; font-size: 1.4em; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #333; }}
.section h2 .icon {{ margin-right: 8px; }}

/* Tables */
table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
th {{ background: #16213e; color: #4ecdc4; padding: 10px 8px; text-align: left; position: sticky; top: 0; }}
td {{ padding: 8px; border-bottom: 1px solid #222; }}
tr:hover {{ background: rgba(78, 205, 196, 0.05); }}
.table-scroll {{ max-height: 400px; overflow-y: auto; }}

/* Cards */
.card-case, .takeover-case {{ display: flex; align-items: center; gap: 12px; padding: 10px; border-bottom: 1px solid #222;
    flex-wrap: wrap; }}
.card-num {{ background: #ff4444; color: white; padding: 3px 10px; border-radius: 4px; font-weight: bold; font-family: monospace; }}
.route {{ color: #4ecdc4; }}
.time-badge {{ background: #ff8c00; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.85em; }}
.amounts {{ color: #888; font-family: monospace; }}
.cust-id {{ background: #16213e; padding: 3px 10px; border-radius: 4px; font-family: monospace; color: #4ecdc4; }}
.flags-badge {{ background: #2a1a3e; color: #ff8c00; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }}
.spend-change {{ color: #ff4444; font-family: monospace; }}

/* Heatmap */
.heatmap {{ display: grid; grid-template-columns: 60px repeat(7, 1fr); gap: 2px; margin-top: 10px; }}
.heatmap-cell {{ padding: 8px 4px; text-align: center; font-size: 0.8em; border-radius: 3px; }}
.heatmap-header {{ color: #4ecdc4; font-weight: bold; padding: 5px; text-align: center; }}
.heatmap-label {{ color: #888; padding: 8px 4px; text-align: right; font-size: 0.8em; }}

/* Grid */
.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
@media (max-width: 900px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

/* Bot meter */
.meter {{ height: 30px; background: #111; border-radius: 15px; overflow: hidden; margin: 10px 0; }}
.meter-fill {{ height: 100%; border-radius: 15px; display: flex; align-items: center; justify-content: center;
    font-weight: bold; font-size: 0.85em; }}

/* Crime type bars */
.crime-bar {{ display: flex; align-items: center; gap: 10px; margin: 8px 0; }}
.crime-bar .bar {{ height: 25px; border-radius: 4px; display: flex; align-items: center; padding-left: 8px;
    font-size: 0.85em; font-weight: bold; min-width: 40px; }}
.crime-bar .name {{ width: 180px; text-align: right; font-size: 0.9em; color: #aaa; }}
</style>
</head>
<body>
<div class="container">

<div class="header">
    <h1>FRAUD DETECTIVE</h1>
    <div class="subtitle">Forensic Transaction Analysis — {len(df):,} Transactions Investigated</div>
</div>

<!-- Alert Board -->
<div class="alert-board">
    <div class="alert-card">
        <div class="label">Total Transactions</div>
        <div class="value green">{len(df):,}</div>
    </div>
    <div class="alert-card danger">
        <div class="label">Anomalies Detected</div>
        <div class="value red">{total_anomalies:,}</div>
    </div>
    <div class="alert-card danger">
        <div class="label">Financial Impact</div>
        <div class="value red">${financial_impact:,.0f}</div>
    </div>
    <div class="alert-card">
        <div class="label">Fraud Rate</div>
        <div class="value orange">{fraud_rate:.1f}%</div>
    </div>
    <div class="alert-card">
        <div class="label">Detection Recall</div>
        <div class="value yellow">{overall_recall:.0%}</div>
    </div>
    <div class="alert-card">
        <div class="label">Precision</div>
        <div class="value green">{overall_precision:.0%}</div>
    </div>
</div>

<!-- Top 3 Crime Types -->
<div class="section">
    <h2>Top Crime Types</h2>
    {"".join(f'<div class="crime-bar"><span class="name">{name}</span><div class="bar" style="width:{int(count/crime_type_counts.max()*100)}%;background:{"#ff4444" if i==0 else "#ff8c00" if i==1 else "#ffd700"}">{count}</div></div>' for i,(name,count) in enumerate(crime_type_counts.head(6).items()))}
</div>

<!-- Impossible Geography -->
<div class="section">
    <h2>Impossible Geography — Stolen Card Timeline</h2>
    <p style="color:#888;margin-bottom:15px">Cards used in multiple countries within 2-hour windows — physically impossible travel</p>
    {stolen_timeline_html if stolen_timeline_html else '<p style="color:#666">No impossible geography cases detected</p>'}
</div>

<!-- Employee Watchlist & Bot Detection -->
<div class="grid-2">
    <div class="section">
        <h2>Employee Watchlist</h2>
        <div class="table-scroll">
        <table>
            <tr><th>Employee</th><th>Refund Rate</th><th>Avg Discount</th><th>Ghost Refunds</th><th>Txns</th><th>Risk Score</th></tr>
            {emp_rows}
        </table>
        </div>
    </div>
    <div class="section">
        <h2>Bot Traffic Detection</h2>
        <p style="margin-bottom:10px">Processing Time Analysis</p>
        <div style="display:flex;gap:20px;margin-bottom:15px">
            <div><span class="green" style="font-size:2em;font-weight:bold">{human_count:,}</span><br><span style="color:#888">Human</span></div>
            <div><span class="red" style="font-size:2em;font-weight:bold">{bot_count:,}</span><br><span style="color:#888">Bot</span></div>
        </div>
        <div class="meter">
            <div class="meter-fill" style="width:{bot_count/len(df)*100:.1f}%;background:linear-gradient(90deg,#ff4444,#ff8c00)">
                {bot_count/len(df)*100:.1f}% Bot Traffic
            </div>
        </div>
        <p style="color:#888;font-size:0.85em;margin-top:10px">Humans: 2-8 sec processing | Bots: &lt;1 sec processing</p>
        <p style="color:#888;font-size:0.85em">{len(bot_ip_set)} IPs with suspiciously uniform timing</p>
    </div>
</div>

<!-- Price Glitch & Discount Abuse -->
<div class="grid-2">
    <div class="section">
        <h2>Price Glitch Report</h2>
        <p style="color:#ff4444;font-size:1.2em;margin-bottom:10px">Est. Revenue Lost: ${glitch_revenue_lost:,.0f}</p>
        <table>
            <tr><th>Category</th><th>Glitches</th><th>Avg Glitch Price</th><th>Normal Median</th><th>Loss</th></tr>
            {glitch_rows}
        </table>
    </div>
    <div class="section">
        <h2>Discount Abuse</h2>
        <p style="color:#ff8c00;font-size:1.2em;margin-bottom:10px">{high_discount.sum()} transactions with &gt;50% discount</p>
        <p style="color:#ff4444;font-size:1.2em">Est. Loss: ${discount_loss:,.0f}</p>
    </div>
</div>

<!-- Account Takeover -->
<div class="section">
    <h2>Account Takeover Detection</h2>
    <p style="color:#888;margin-bottom:15px">{len(takeover_cases)} customers with dramatic behavioral shifts</p>
    {takeover_html if takeover_html else '<p style="color:#666">No account takeover cases detected</p>'}
</div>

<!-- Anomaly Hotspot Heatmap -->
<div class="section">
    <h2>Anomaly Hotspot Heatmap — When Crimes Happen</h2>
    <div class="heatmap">
        <div class="heatmap-header"></div>
        {"".join(f'<div class="heatmap-header">{d}</div>' for d in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])}
        {"".join(
            f'<div class="heatmap-label">{h}:00</div>' +
            "".join(f'<div class="heatmap-cell" style="background:rgba(255,68,68,{min(heatmap_json[h][d]/max(max(r) for r in heatmap_json) if max(max(r) for r in heatmap_json)>0 else 1, 1):.2f})">{heatmap_json[h][d] if heatmap_json[h][d]>0 else ""}</div>'
                for d in range(7))
            for h in range(24)
        )}
    </div>
</div>

<!-- Top 50 Suspicious Transactions -->
<div class="section">
    <h2>Top 50 Most Suspicious Transactions</h2>
    <div class="table-scroll">
    <table>
        <tr><th>Transaction ID</th><th>Timestamp</th><th>Employee</th><th>Amount</th><th>Score</th><th>Flags</th></tr>
        {top50_html_rows}
    </table>
    </div>
</div>

<!-- Detection Accuracy -->
<div class="section">
    <h2>Detection Accuracy vs Ground Truth</h2>
    <table>
        <tr><th>Anomaly Type</th><th>Planted</th><th>Detected</th><th>Missed</th><th>Recall</th></tr>
        {val_rows}
        <tr style="border-top:2px solid #4ecdc4;font-weight:bold">
            <td>OVERALL</td><td>{actual_any.sum()}</td><td>{overall_tp}</td>
            <td>{(actual_any & ~detected_any).sum()}</td>
            <td style="color:{'#4ecdc4' if overall_recall>=0.7 else '#ff8c00'}">{overall_recall:.0%}</td>
        </tr>
    </table>
</div>

</div>
</body>
</html>"""

with open('output/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dashboard_html)

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("INVESTIGATION COMPLETE")
print("="*70)
print(f"\n  Total financial impact:   ${financial_impact:,.0f}")
print(f"  Most dangerous type:     {most_dangerous}")
print(f"  Highest-risk employee:   {highest_risk_emp}")
print(f"  Detection recall:        {overall_recall:.0%}")
print(f"  Detection precision:     {overall_precision:.0%}")
print(f"\n  ACTION FOR TOMORROW: Implement velocity-based card testing detection")
print(f"  — block IPs with >10 sub-$5 transactions per hour to stop fraud at the gate.\n")
print("  Output files:")
for f_name in ['dashboard.html', 'stolen_card_timeline.png', 'employee_watchlist.png',
               'bot_vs_human.png', 'price_glitch_report.png', 'anomaly_hotspots.png',
               'suspicion_ranking.png', 'investigation_report.md']:
    exists = os.path.exists(f'output/{f_name}')
    print(f"    {'[OK]' if exists else '[!!]'} output/{f_name}")
