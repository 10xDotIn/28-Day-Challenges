import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

df = pd.read_csv('data/weather_business.csv')

ride = df[df['business_type'] == 'Ride-Hailing']
food = df[df['business_type'] == 'Food Delivery']

day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

ride_day = ride.groupby('day_of_week').agg(
    customers=('customer_count','mean'),
    cancel=('cancellation_rate','mean'),
    revenue=('revenue','mean')
).reindex(day_order)

food_day = food.groupby('day_of_week').agg(
    customers=('customer_count','mean'),
    cancel=('cancellation_rate','mean'),
    revenue=('revenue','mean'),
    online_pct=('online_order_pct','mean')
).reindex(day_order)

print('=== RIDE-HAILING BY DAY (lower demand = less wait) ===')
for day in day_order:
    r = ride_day.loc[day]
    print(f'  {day:10s}  Customers: {r.customers:5.0f}  Cancel: {r.cancel:.1f}%  Revenue: ${r.revenue:,.0f}')

print()
print('=== FOOD DELIVERY BY DAY (lower demand = faster delivery) ===')
for day in day_order:
    f = food_day.loc[day]
    print(f'  {day:10s}  Customers: {f.customers:5.0f}  Cancel: {f.cancel:.1f}%  Online: {f.online_pct:.0f}%  Revenue: ${f.revenue:,.0f}')

# Composite score: lower customer count = less wait, lower cancellation = smoother
def score(series):
    return 1 - (series - series.min()) / (series.max() - series.min())

ride_cust_score = score(ride_day['customers'])
ride_cancel_score = score(ride_day['cancel'])
food_cust_score = score(food_day['customers'])
food_cancel_score = score(food_day['cancel'])

combined = (ride_cust_score * 0.3 + ride_cancel_score * 0.2 +
            food_cust_score * 0.3 + food_cancel_score * 0.2)

print()
print('=== BEST DAY COMPOSITE SCORE (higher = less wait) ===')
for day in combined.sort_values(ascending=False).index:
    rc = ride_day.loc[day, 'customers']
    fc = food_day.loc[day, 'customers']
    print(f'  {day:10s}  Score: {combined[day]:.3f}  |  Ride demand: {rc:.0f}, Food demand: {fc:.0f}')

best_day = combined.idxmax()
worst_day = combined.idxmin()
print(f'\nBEST DAY: {best_day}')
print(f'WORST DAY: {worst_day}')

# Weather impact on wait
ride_weather = ride.groupby('weather_condition').agg(
    customers=('customer_count','mean'), cancel=('cancellation_rate','mean')
)
food_weather = food.groupby('weather_condition').agg(
    customers=('customer_count','mean'), cancel=('cancellation_rate','mean')
)

print()
print('=== BEST WEATHER FOR LOW RIDE WAIT ===')
for w in ride_weather.sort_values('customers').index:
    r = ride_weather.loc[w]
    print(f'  {w:20s}  Demand: {r.customers:5.0f}  Cancel: {r.cancel:.1f}%')

print()
print('=== BEST WEATHER FOR FAST FOOD DELIVERY ===')
for w in food_weather.sort_values('customers').index:
    f = food_weather.loc[w]
    print(f'  {w:20s}  Demand: {f.customers:5.0f}  Cancel: {f.cancel:.1f}%')

# ── BUILD VISUAL ──
fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('#1a1a2e')
gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.3)

axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]
for ax in axes:
    ax.set_facecolor('#16213e')
    ax.tick_params(colors='#aaa')
    for sp in ['top','right']:
        ax.spines[sp].set_visible(False)
    for sp in ['bottom','left']:
        ax.spines[sp].set_color('#555')

ax1, ax2, ax3, ax4 = axes

# Chart 1: Customer demand by day
x = np.arange(len(day_order))
w = 0.35
ax1.bar(x - w/2, ride_day['customers'], w, label='Ride-Hailing', color='#3498db', edgecolor='none')
ax1.bar(x + w/2, food_day['customers'], w, label='Food Delivery', color='#e67e22', edgecolor='none')
ax1.set_xticks(x)
ax1.set_xticklabels([d[:3] for d in day_order], fontsize=9, color='#ccc')
ax1.set_ylabel('Avg Customers', color='white')
ax1.set_title('Customer Demand by Day\n(Lower = Less Wait)', color='white', fontsize=11, fontweight='bold')
ax1.legend(fontsize=8, loc='upper left')
ax1.grid(axis='y', color='#333', alpha=0.5)
best_idx = day_order.index(best_day)
ax1.axvspan(best_idx-0.45, best_idx+0.45, alpha=0.15, color='#2ecc71')
ax1.text(best_idx, ax1.get_ylim()[1]*0.95, 'BEST', ha='center', color='#2ecc71', fontweight='bold', fontsize=10)

# Chart 2: Cancellation rate by day
ax2.plot([d[:3] for d in day_order], ride_day['cancel'], 'o-', color='#3498db', label='Ride-Hailing', lw=2, markersize=6)
ax2.plot([d[:3] for d in day_order], food_day['cancel'], 's-', color='#e67e22', label='Food Delivery', lw=2, markersize=6)
ax2.set_ylabel('Cancellation Rate (%)', color='white')
ax2.set_title('Cancellation Rate by Day\n(Lower = Smoother)', color='white', fontsize=11, fontweight='bold')
ax2.legend(fontsize=8)
ax2.grid(axis='y', color='#333', alpha=0.5)

# Chart 3: Composite score
bar_colors = ['#2ecc71' if d == best_day else '#e74c3c' if d == worst_day else '#3498db' for d in day_order]
ax3.bar([d[:3] for d in day_order], [combined[d] for d in day_order], color=bar_colors, edgecolor='none')
ax3.set_ylabel('Composite Score', color='white')
ax3.set_title('Best Day Score\n(Higher = Less Wait for Both)', color='white', fontsize=11, fontweight='bold')
ax3.grid(axis='y', color='#333', alpha=0.5)
for i, d in enumerate(day_order):
    ax3.text(i, combined[d]+0.01, f'{combined[d]:.2f}', ha='center', fontsize=8, color='white')

# Chart 4: Best weather for low ride wait
ride_w_sorted = ride_weather.sort_values('customers')
med = ride_weather['customers'].median()
colors_w = ['#2ecc71' if c < med else '#e74c3c' for c in ride_w_sorted['customers']]
ax4.barh(ride_w_sorted.index, ride_w_sorted['customers'], color=colors_w, edgecolor='none', height=0.6)
ax4.set_xlabel('Avg Customers (Ride-Hailing)', color='white')
ax4.set_title('Weather: Ride Demand\n(Green = Less Competition)', color='white', fontsize=11, fontweight='bold')
ax4.grid(axis='x', color='#333', alpha=0.5)
for i, (idx, c) in enumerate(zip(ride_w_sorted.index, ride_w_sorted['customers'])):
    ax4.text(c+3, i, f'{c:.0f}', va='center', fontsize=8, color='white')

fig.suptitle(f'Best Day to Travel + Order Takeout:  {best_day}', fontsize=16,
             fontweight='bold', color='#00d4ff', y=0.98)

plt.savefig('output/best_travel_takeout_day.png', dpi=150, facecolor='#1a1a2e', bbox_inches='tight')
plt.close()
print('\nSaved output/best_travel_takeout_day.png')
