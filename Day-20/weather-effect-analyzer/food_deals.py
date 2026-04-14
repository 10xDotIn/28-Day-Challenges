import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

df = pd.read_csv('data/weather_business.csv')

# Food businesses: Restaurant Dine-In, Food Delivery, Coffee Shop
food_types = ['Restaurant Dine-In', 'Food Delivery', 'Coffee Shop']
food = df[df['business_type'].isin(food_types)]

day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

# ── When do food businesses lose revenue? That's when deals appear ──
# Logic: low revenue + low customers + high cancellations = desperate for business = deals

print("=" * 70)
print("FOOD DEAL FINDER: When food businesses need YOUR money most")
print("=" * 70)

# 1. By weather condition
print("\n=== FOOD REVENUE BY WEATHER ===")
for biz in food_types:
    bdf = df[df['business_type'] == biz]
    avg = bdf['revenue'].mean()
    weather_rev = bdf.groupby('weather_condition').agg(
        revenue=('revenue','mean'),
        customers=('customer_count','mean'),
        cancel=('cancellation_rate','mean'),
        online=('online_order_pct','mean')
    ).sort_values('revenue')
    print(f"\n  {biz} (avg ${avg:,.0f}):")
    for w in weather_rev.index:
        r = weather_rev.loc[w]
        diff = r.revenue - avg
        print(f"    {w:20s}  ${r.revenue:>8,.0f} ({diff:+,.0f})  Cust: {r.customers:.0f}  Cancel: {r.cancel:.1f}%")

# 2. By day × weather combo for dine-in (most deal-sensitive)
dinein = df[df['business_type'] == 'Restaurant Dine-In']
dinein_avg = dinein['revenue'].mean()
combo = dinein.groupby(['day_of_week', 'weather_condition']).agg(
    revenue=('revenue','mean'),
    customers=('customer_count','mean'),
    cancel=('cancellation_rate','mean')
).reset_index()
combo['label'] = combo['day_of_week'] + ' + ' + combo['weather_condition']
combo['rev_drop'] = ((combo['revenue'] - dinein_avg) / dinein_avg * 100)
combo = combo.sort_values('revenue')

print("\n=== TOP 10 WORST DAYS FOR RESTAURANT DINE-IN (= BEST FOR DEALS) ===")
for _, r in combo.head(10).iterrows():
    print(f"  {r['label']:35s}  ${r.revenue:>8,.0f}  ({r.rev_drop:+.1f}%)  Cust: {r.customers:.0f}  Cancel: {r.cancel:.1f}%")

print("\n=== TOP 10 BEST DAYS FOR RESTAURANT DINE-IN (= fewest deals) ===")
for _, r in combo.tail(10).iloc[::-1].iterrows():
    print(f"  {r['label']:35s}  ${r.revenue:>8,.0f}  ({r.rev_drop:+.1f}%)  Cust: {r.customers:.0f}")

# 3. Coffee shop worst days
coffee = df[df['business_type'] == 'Coffee Shop']
coffee_avg = coffee['revenue'].mean()
coffee_combo = coffee.groupby(['day_of_week', 'weather_condition']).agg(
    revenue=('revenue','mean'), customers=('customer_count','mean')
).reset_index()
coffee_combo['label'] = coffee_combo['day_of_week'] + ' + ' + coffee_combo['weather_condition']
coffee_combo = coffee_combo.sort_values('revenue')

print("\n=== TOP 5 WORST DAYS FOR COFFEE SHOPS (= deal time) ===")
for _, r in coffee_combo.head(5).iterrows():
    diff = r.revenue - coffee_avg
    print(f"  {r['label']:35s}  ${r.revenue:>8,.0f}  ({diff:+,.0f})  Cust: {r.customers:.0f}")

# 4. Delivery deals — when demand is lowest (cheapest surge pricing)
delivery = df[df['business_type'] == 'Food Delivery']
del_avg = delivery['revenue'].mean()
del_combo = delivery.groupby(['day_of_week', 'weather_condition']).agg(
    revenue=('revenue','mean'), customers=('customer_count','mean'),
    online=('online_order_pct','mean')
).reset_index()
del_combo['label'] = del_combo['day_of_week'] + ' + ' + del_combo['weather_condition']
del_combo = del_combo.sort_values('revenue')

print("\n=== TOP 5 LOWEST DELIVERY DEMAND (= no surge, better deals) ===")
for _, r in del_combo.head(5).iterrows():
    diff = r.revenue - del_avg
    print(f"  {r['label']:35s}  ${r.revenue:>8,.0f}  ({diff:+,.0f})  Cust: {r.customers:.0f}")

# ── Deal score: combine low revenue + low customers + high cancellation ──
# For each day×weather, score across all food businesses
all_food_combo = food.groupby(['day_of_week', 'weather_condition']).agg(
    revenue=('revenue','mean'),
    customers=('customer_count','mean'),
    cancel=('cancellation_rate','mean')
).reset_index()
all_food_combo['label'] = all_food_combo['day_of_week'] + ' + ' + all_food_combo['weather_condition']

def inv_norm(s):
    return 1 - (s - s.min()) / (s.max() - s.min())

all_food_combo['deal_score'] = (
    inv_norm(all_food_combo['revenue']) * 0.4 +
    inv_norm(all_food_combo['customers']) * 0.35 +
    (all_food_combo['cancel'] - all_food_combo['cancel'].min()) /
    (all_food_combo['cancel'].max() - all_food_combo['cancel'].min()) * 0.25
)
all_food_combo = all_food_combo.sort_values('deal_score', ascending=False)

print("\n=== OVERALL FOOD DEAL SCORE (higher = better deals expected) ===")
print("  Top 10:")
for _, r in all_food_combo.head(10).iterrows():
    print(f"    {r['label']:35s}  Score: {r.deal_score:.3f}  Rev: ${r.revenue:,.0f}  Cust: {r.customers:.0f}  Cancel: {r.cancel:.1f}%")
print("  Bottom 5 (worst for deals):")
for _, r in all_food_combo.tail(5).iloc[::-1].iterrows():
    print(f"    {r['label']:35s}  Score: {r.deal_score:.3f}  Rev: ${r.revenue:,.0f}  Cust: {r.customers:.0f}")

best_deal = all_food_combo.iloc[0]
worst_deal = all_food_combo.iloc[-1]

# ── BUILD VISUAL ──
fig = plt.figure(figsize=(18, 12))
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

# Chart 1: Restaurant revenue by weather (low = deals likely)
dinein_weather = dinein.groupby('weather_condition')['revenue'].mean().sort_values()
colors1 = ['#2ecc71' if v < dinein_avg else '#e74c3c' for v in dinein_weather.values]
ax1.barh(dinein_weather.index, dinein_weather.values, color=colors1, edgecolor='none', height=0.6)
ax1.axvline(dinein_avg, color='#00d4ff', ls='--', lw=1.2, alpha=0.7)
ax1.text(dinein_avg, -0.7, f'Avg ${dinein_avg:,.0f}', color='#00d4ff', fontsize=8, ha='center')
for i, (w, v) in enumerate(zip(dinein_weather.index, dinein_weather.values)):
    diff = v - dinein_avg
    ax1.text(v + 50, i, f'${v:,.0f} ({diff:+,.0f})', va='center', fontsize=8, color='white')
ax1.set_title('Restaurant Dine-In Revenue by Weather\n(Green = Low Revenue = Deal Time)', color='white', fontsize=11, fontweight='bold')
ax1.set_xlabel('Avg Revenue ($)', color='white')

# Chart 2: Top 10 deal combos (bar chart)
top10 = all_food_combo.head(10).iloc[::-1]
colors2 = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, 10))
ax2.barh(range(10), top10['deal_score'], color=colors2, edgecolor='none', height=0.7)
ax2.set_yticks(range(10))
ax2.set_yticklabels(top10['label'], fontsize=9, color='#ccc')
for i, (_, r) in enumerate(top10.iterrows()):
    ax2.text(r.deal_score + 0.01, i, f'{r.deal_score:.2f}  |  ${r.revenue:,.0f}', va='center', fontsize=8, color='white')
ax2.set_title('Top 10 Day+Weather for Food Deals\n(Higher Score = Better Deals)', color='white', fontsize=11, fontweight='bold')
ax2.set_xlabel('Deal Score', color='white')

# Chart 3: Dine-in revenue by day (lowest day = best deals)
dinein_day = dinein.groupby('day_of_week')['revenue'].mean().reindex(day_order)
day_colors = ['#2ecc71' if v == dinein_day.min() else '#e74c3c' if v == dinein_day.max() else '#3498db' for v in dinein_day.values]
ax3.bar([d[:3] for d in day_order], dinein_day.values, color=day_colors, edgecolor='none')
ax3.set_ylabel('Avg Revenue ($)', color='white')
ax3.set_title('Restaurant Revenue by Day\n(Low Revenue Day = Deals)', color='white', fontsize=11, fontweight='bold')
ax3.grid(axis='y', color='#333', alpha=0.5)
for i, (d, v) in enumerate(zip(day_order, dinein_day.values)):
    ax3.text(i, v + 50, f'${v:,.0f}', ha='center', fontsize=8, color='white')

# Chart 4: Cancellation rate by weather (high cancel = desperate = deals)
dinein_cancel = dinein.groupby('weather_condition')['cancellation_rate'].mean().sort_values(ascending=False)
colors4 = ['#2ecc71' if v > dinein['cancellation_rate'].mean() else '#555' for v in dinein_cancel.values]
ax4.barh(dinein_cancel.index, dinein_cancel.values, color=colors4, edgecolor='none', height=0.6)
ax4.axvline(dinein['cancellation_rate'].mean(), color='#00d4ff', ls='--', lw=1, alpha=0.6)
for i, (w, v) in enumerate(zip(dinein_cancel.index, dinein_cancel.values)):
    ax4.text(v + 0.05, i, f'{v:.1f}%', va='center', fontsize=8, color='white')
ax4.set_title('Restaurant Cancellation Rate by Weather\n(High Cancel = Desperate = Deals)', color='white', fontsize=11, fontweight='bold')
ax4.set_xlabel('Cancellation Rate (%)', color='white')

fig.suptitle(f'Best Day + Weather for Food Deals:  {best_deal["label"]}',
             fontsize=16, fontweight='bold', color='#00d4ff', y=0.98)

plt.savefig('output/best_food_deals.png', dpi=150, facecolor='#1a1a2e', bbox_inches='tight')
plt.close()
print('\nSaved output/best_food_deals.png')
