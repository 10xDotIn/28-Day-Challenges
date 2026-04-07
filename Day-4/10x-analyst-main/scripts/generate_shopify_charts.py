"""
Generate 6 Shopify e-commerce charts for the analysis report.
Output: output/shopify-data/charts/*.png
"""

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np
import os

# ── Style setup ─────────────────────────────────────────────────────────────
COLORS = ['#FF6B35', '#004E89', '#00A878', '#FFD166', '#EF476F', '#118AB2', '#073B4C']
POSITIVE = '#00A878'
NEGATIVE = '#EF476F'
PRIMARY  = '#FF6B35'
SECONDARY = '#004E89'

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette(COLORS)

plt.rcParams.update({
    'figure.figsize': (12, 6),
    'figure.dpi': 150,
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'legend.fontsize': 10,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#dddddd',
    'grid.color': '#eeeeee',
    'grid.linewidth': 0.8,
})

BASE = "C:/Users/p/Downloads/10x-analyst-main/10x-analyst-main"
CHARTS_DIR = os.path.join(BASE, "output/shopify-data/charts")
CLEANED_DIR = os.path.join(BASE, "output/shopify-data/cleaned-data")
os.makedirs(CHARTS_DIR, exist_ok=True)

saved = []


# ── Chart 1: Monthly Revenue Bar Chart ──────────────────────────────────────
def chart_monthly_revenue():
    months   = ['Dec 2025', 'Jan 2026', 'Feb 2026']
    revenues = [54267, 59086, 46459]

    # Month-over-month % changes (first bar has no prior month)
    mom = [None,
           (revenues[1] - revenues[0]) / revenues[0] * 100,
           (revenues[2] - revenues[1]) / revenues[1] * 100]

    fig, ax = plt.subplots(figsize=(12, 6))

    bar_colors = [SECONDARY, POSITIVE, NEGATIVE]   # dec=blue, jan=green(+), feb=red(-)
    bars = ax.bar(months, revenues, color=bar_colors, width=0.5, zorder=3, edgecolor='white', linewidth=1.2)

    # Value labels + MoM badge on each bar
    for i, (bar, rev, m) in enumerate(zip(bars, revenues, mom)):
        h = bar.get_height()
        # Revenue label just above bar
        ax.text(bar.get_x() + bar.get_width() / 2, h + 600,
                f'${rev:,.0f}', ha='center', va='bottom',
                fontsize=12, fontweight='bold', color='#073B4C')
        # MoM % label inside bar (skip first)
        if m is not None:
            arrow = '+' if m >= 0 else ''
            color = POSITIVE if m >= 0 else NEGATIVE
            ax.text(bar.get_x() + bar.get_width() / 2, h / 2,
                    f'{arrow}{m:.1f}% MoM', ha='center', va='center',
                    fontsize=11, fontweight='bold', color='white')

    ax.set_title('Jan 2026 Peaked at $59K; Feb Dipped 21% MoM — Seasonal Watch Needed',
                 pad=14)
    ax.set_xlabel('Month')
    ax.set_ylabel('Revenue (USD)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_ylim(0, max(revenues) * 1.18)
    ax.yaxis.grid(True, color='#eeeeee', linewidth=0.8)
    ax.xaxis.grid(False)
    ax.tick_params(axis='x', labelsize=12)

    fig.text(0.5, -0.02, 'Source: output/shopify-data/cleaned-data/orders.csv | 10x.in',
             ha='center', fontsize=9, color='#888888')

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'monthly_revenue.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    saved.append(path)
    print(f'  Saved: {path}')


# ── Chart 2: Revenue by Category Horizontal Bar ──────────────────────────────
def chart_revenue_by_category():
    categories = ['Brewing Equipment', 'Subscriptions', 'Coffee Beans', 'Accessories']
    revenues   = [45384, 34799, 33656, 26085]

    # Sort ascending for horizontal bar (largest on top)
    df = pd.DataFrame({'category': categories, 'revenue': revenues})
    df = df.sort_values('revenue', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 5))

    bars = ax.barh(df['category'], df['revenue'],
                   color=[COLORS[i % len(COLORS)] for i in range(len(df))],
                   height=0.55, edgecolor='white', linewidth=1.0, zorder=3)

    for bar, rev in zip(bars, df['revenue']):
        ax.text(bar.get_width() + 400, bar.get_y() + bar.get_height() / 2,
                f'${rev:,.0f}', va='center', ha='left',
                fontsize=11, fontweight='bold', color='#073B4C')

    ax.set_title('Brewing Equipment Leads Revenue at $45K — Nearly 2x Accessories',
                 pad=14)
    ax.set_xlabel('Revenue (USD)')
    ax.set_ylabel('Product Category')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_xlim(0, max(df['revenue']) * 1.18)
    ax.xaxis.grid(True, color='#eeeeee', linewidth=0.8)
    ax.yaxis.grid(False)
    ax.tick_params(axis='y', labelsize=12)

    fig.text(0.5, -0.04, 'Source: output/shopify-data/cleaned-data/order_items.csv | 10x.in',
             ha='center', fontsize=9, color='#888888')

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'revenue_by_category.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    saved.append(path)
    print(f'  Saved: {path}')


# ── Chart 3: Top 10 Products by Revenue ─────────────────────────────────────
def chart_top10_products():
    products = [
        'Quarterly Discovery Box (6 bags + surprise)',
        'Electric Gooseneck Kettle (1.2L)',
        'Manual Ceramic Burr Grinder',
        'AeroPress Original Kit',
        'Monthly Bean Box (2 bags)',
        'Ceramic Pour-Over Dripper',
        'Limited Edition Guatemala Antigua',
        'Ethiopian Yirgacheffe Single Origin',
        'Stainless Steel French Press (34oz)',
        'Precision Coffee Scale with Timer',
    ]
    revenues = [21957.56, 11618.34, 8633.43, 8357.91, 7983.58,
                6822.35, 5672.73, 5374.17, 5193.55, 4948.35]

    # Truncate long names for readability
    short_names = [
        'Quarterly Discovery Box',
        'Electric Gooseneck Kettle',
        'Manual Ceramic Burr Grinder',
        'AeroPress Original Kit',
        'Monthly Bean Box',
        'Ceramic Pour-Over Dripper',
        'Guatemala Antigua (Limited Ed.)',
        'Ethiopian Yirgacheffe',
        'Stainless Steel French Press',
        'Precision Coffee Scale',
    ]

    df = pd.DataFrame({'product': short_names, 'revenue': revenues})
    df = df.sort_values('revenue', ascending=True)

    fig, ax = plt.subplots(figsize=(13, 7))

    bar_colors = [PRIMARY if i == len(df) - 1 else SECONDARY for i in range(len(df))]
    bars = ax.barh(df['product'], df['revenue'],
                   color=bar_colors, height=0.6,
                   edgecolor='white', linewidth=1.0, zorder=3)

    for bar, rev in zip(bars, df['revenue']):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
                f'${rev:,.0f}', va='center', ha='left',
                fontsize=10, fontweight='bold', color='#073B4C')

    ax.set_title('Quarterly Discovery Box Alone Drives 19% of Total Revenue',
                 pad=14)
    ax.set_xlabel('Revenue (USD)')
    ax.set_ylabel('Product')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_xlim(0, max(df['revenue']) * 1.20)
    ax.xaxis.grid(True, color='#eeeeee', linewidth=0.8)
    ax.yaxis.grid(False)
    ax.tick_params(axis='y', labelsize=10)

    fig.text(0.5, -0.02, 'Source: output/shopify-data/cleaned-data/order_items.csv | 10x.in',
             ha='center', fontsize=9, color='#888888')

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'top10_products_revenue.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    saved.append(path)
    print(f'  Saved: {path}')


# ── Chart 4: Customer Acquisition Channel Pie Chart ─────────────────────────
def chart_acquisition_channel():
    channels = ['Organic Search', 'Instagram Ads', 'Referral', 'Google Ads',
                'Email Campaign', 'TikTok Ads', 'Direct', 'Facebook Ads']
    counts   = [42, 38, 32, 26, 17, 14, 14, 12]

    fig, ax = plt.subplots(figsize=(9, 8))

    wedge_props = dict(width=0.62, edgecolor='white', linewidth=2)

    wedges, texts, autotexts = ax.pie(
        counts,
        labels=None,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.72,
        colors=COLORS[:len(channels)],
        wedgeprops=wedge_props,
    )

    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')
        autotext.set_color('white')

    # Legend with counts
    legend_labels = [f'{ch}  ({cnt})' for ch, cnt in zip(channels, counts)]
    ax.legend(wedges, legend_labels, loc='lower center',
              bbox_to_anchor=(0.5, -0.12), ncol=2,
              fontsize=10, frameon=False)

    ax.set_title('Organic Search (21%) & Instagram Ads (19%) Drive Most New Customers',
                 pad=18)

    fig.text(0.5, -0.06, 'Source: output/shopify-data/cleaned-data/customers.csv | 10x.in',
             ha='center', fontsize=9, color='#888888')

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'acquisition_channel.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    saved.append(path)
    print(f'  Saved: {path}')


# ── Chart 5: Revenue by Traffic Source Bar Chart ────────────────────────────
def chart_revenue_by_source():
    sources  = ['Referral', 'Instagram Ads', 'Organic Search', 'Google Ads',
                'Direct', 'Email', 'TikTok', 'Facebook']
    revenues = [35660, 34530, 31928, 18356, 12226, 11695, 9489, 5928]

    fig, ax = plt.subplots(figsize=(13, 6))

    bar_colors = [COLORS[i % len(COLORS)] for i in range(len(sources))]
    bars = ax.bar(sources, revenues, color=bar_colors, width=0.6,
                  edgecolor='white', linewidth=1.2, zorder=3)

    for bar, rev in zip(bars, revenues):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 400,
                f'${rev:,.0f}', ha='center', va='bottom',
                fontsize=9.5, fontweight='bold', color='#073B4C')

    ax.set_title('Referral & Instagram Ads Together Deliver 46% of Revenue by Traffic Source',
                 pad=14)
    ax.set_xlabel('Traffic Source')
    ax.set_ylabel('Revenue (USD)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_ylim(0, max(revenues) * 1.18)
    ax.yaxis.grid(True, color='#eeeeee', linewidth=0.8)
    ax.xaxis.grid(False)
    ax.tick_params(axis='x', labelsize=10, rotation=20)

    fig.text(0.5, -0.04, 'Source: output/shopify-data/cleaned-data/orders.csv | 10x.in',
             ha='center', fontsize=9, color='#888888')

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'revenue_by_source.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    saved.append(path)
    print(f'  Saved: {path}')


# ── Chart 6: Top 10 Customers by Total Spend ────────────────────────────────
def chart_top_customers():
    names  = ['Peter Williams', 'Paige Lewis', 'Rohit Walker', 'Megha Thakur',
              'Tushar Thomas', 'Kavya Agarwal', 'William Taylor', 'Meera White',
              'Peter Wright', 'Charlie Wright']
    spend  = [3085.95, 3004.43, 2879.40, 2545.68, 2483.80,
              2343.14, 2110.74, 2021.87, 1939.26, 1890.96]

    df = pd.DataFrame({'customer': names, 'spend': spend})
    df = df.sort_values('spend', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 6))

    bar_colors = [PRIMARY if i == len(df) - 1 else SECONDARY for i in range(len(df))]
    bars = ax.barh(df['customer'], df['spend'],
                   color=bar_colors, height=0.6,
                   edgecolor='white', linewidth=1.0, zorder=3)

    for bar, sp in zip(bars, df['spend']):
        ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height() / 2,
                f'${sp:,.2f}', va='center', ha='left',
                fontsize=10, fontweight='bold', color='#073B4C')

    ax.set_title('Top 10 VIP Customers — Peter Williams Leads at $3,086 Lifetime Spend',
                 pad=14)
    ax.set_xlabel('Total Spend (USD)')
    ax.set_ylabel('Customer')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_xlim(0, max(df['spend']) * 1.22)
    ax.xaxis.grid(True, color='#eeeeee', linewidth=0.8)
    ax.yaxis.grid(False)
    ax.tick_params(axis='y', labelsize=10)

    fig.text(0.5, -0.04, 'Source: output/shopify-data/cleaned-data/customers.csv | 10x.in',
             ha='center', fontsize=9, color='#888888')

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'top_customers.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    saved.append(path)
    print(f'  Saved: {path}')


# ── Run all charts ───────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('Generating Shopify charts...')
    chart_monthly_revenue()
    chart_revenue_by_category()
    chart_top10_products()
    chart_acquisition_channel()
    chart_revenue_by_source()
    chart_top_customers()
    print(f'\nDone. {len(saved)} charts saved to {CHARTS_DIR}')
    for p in saved:
        print(f'  {p}')
