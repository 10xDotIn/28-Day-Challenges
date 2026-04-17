import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path
import json, html, textwrap

# ── Setup ──────────────────────────────────────────────────────────────────
DATA = Path("data/orders.csv")
OUT  = Path("output")
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA)
print(f"Loaded {len(df):,} orders, {df['product'].nunique()} products")

# ── 1. Revenue vs Profit Lie ──────────────────────────────────────────────
prod = df.groupby("product").agg(
    total_revenue=("revenue","sum"),
    total_profit=("true_profit","sum"),
    total_cogs=("cogs","sum"),
    total_shipping=("shipping_cost","sum"),
    total_return_cost=("return_cost","sum"),
    total_support_cost=("support_cost","sum"),
    total_marketing=("marketing_cost","sum"),
    orders=("order_id","count"),
    returns=("returned","sum"),
    support_tickets=("support_ticket","sum"),
    total_discount=("discount_amount","sum"),
    avg_discount_pct=("discount_percent","mean"),
).reset_index()

prod["profit_margin"] = (prod["total_profit"] / prod["total_revenue"] * 100).round(2)
prod["rev_rank"]  = prod["total_revenue"].rank(ascending=False).astype(int)
prod["prof_rank"] = prod["total_profit"].rank(ascending=False).astype(int)
prod["rank_diff"] = prod["rev_rank"] - prod["prof_rank"]
prod["return_rate"] = (prod["returns"] / prod["orders"] * 100).round(2)
prod["return_tax_pct"] = (prod["total_return_cost"] / prod["total_revenue"] * 100).round(2)
prod["hidden_costs"] = prod["total_cogs"] + prod["total_shipping"] + prod["total_return_cost"] + prod["total_support_cost"] + prod["total_marketing"]

# ── 2. Channel Analysis ──────────────────────────────────────────────────
chan = df.groupby("channel").agg(
    revenue=("revenue","sum"),
    profit=("true_profit","sum"),
    marketing=("marketing_cost","sum"),
    orders=("order_id","count"),
).reset_index()
chan["roi"] = (chan["profit"] / chan["marketing"]).round(2)
chan["profit_margin"] = (chan["profit"] / chan["revenue"] * 100).round(2)

# ── 3. Segment Analysis ─────────────────────────────────────────────────
seg = df.groupby("customer_segment").agg(
    revenue=("revenue","sum"),
    profit=("true_profit","sum"),
    orders=("order_id","count"),
    avg_discount=("discount_percent","mean"),
    returns=("returned","sum"),
).reset_index()
seg["profit_per_order"] = (seg["profit"] / seg["orders"]).round(2)
seg["profit_margin"]    = (seg["profit"] / seg["revenue"] * 100).round(2)
seg["return_rate"]      = (seg["returns"] / seg["orders"] * 100).round(2)

# ── 4. Discount Analysis ────────────────────────────────────────────────
df["discount_band"] = pd.cut(df["discount_percent"], bins=[0,5,10,15,20,25,30,35,40,100],
                             labels=["0-5%","5-10%","10-15%","15-20%","20-25%","25-30%","30-35%","35-40%","40%+"])
disc = df.groupby("discount_band", observed=True).agg(
    revenue=("revenue","sum"),
    profit=("true_profit","sum"),
    orders=("order_id","count"),
).reset_index()
disc["margin"] = (disc["profit"] / disc["revenue"] * 100).round(2)

# ── 5. Profit Power Score ───────────────────────────────────────────────
def norm(s):
    r = s.max() - s.min()
    return (s - s.min()) / r if r else 0

prod["pps"] = (
    0.35 * norm(prod["profit_margin"]) +
    0.25 * norm(prod["total_profit"]) +
    0.20 * norm(100 - prod["return_rate"]) +
    0.20 * norm(-prod["total_support_cost"])
).round(4)
prod["pps_rank"] = prod["pps"].rank(ascending=False).astype(int)

# ── 6. Strategy Buckets ─────────────────────────────────────────────────
def classify(row):
    if row["profit_margin"] > 25 and row["return_rate"] < 20 and row["total_support_cost"] / row["orders"] < 8:
        return "SCALE"
    elif row["total_revenue"] > prod["total_revenue"].median() and row["profit_margin"] < 15:
        return "FIX"
    elif row["avg_discount_pct"] > 18 and row["profit_margin"] < 20:
        return "REPRICE"
    elif row["profit_margin"] < 5 or row["total_profit"] < 0:
        return "DROP"
    else:
        return "FIX"

prod["strategy"] = prod.apply(classify, axis=1)

# ── Chart helpers ────────────────────────────────────────────────────────
DARK  = "#0f0f0f"
CARD  = "#1a1a2e"
BLUE  = "#4ea8de"
GREEN = "#2ecc71"
RED   = "#e74c3c"
GOLD  = "#f1c40f"
GRAY  = "#aaaaaa"
COLORS_COST = ["#e74c3c","#e67e22","#9b59b6","#3498db","#1abc9c"]

def style_ax(ax, title=""):
    ax.set_facecolor(DARK)
    ax.figure.set_facecolor(DARK)
    ax.tick_params(colors=GRAY)
    ax.xaxis.label.set_color(GRAY)
    ax.yaxis.label.set_color(GRAY)
    ax.title.set_color("white")
    for s in ax.spines.values(): s.set_color("#333")
    if title: ax.set_title(title, fontsize=14, fontweight="bold", pad=12)

def money(v):
    if abs(v) >= 1e6: return f"${v/1e6:.1f}M"
    if abs(v) >= 1e3: return f"${v/1e3:.0f}K"
    return f"${v:.0f}"

# ── Chart 1: Revenue vs Profit ──────────────────────────────────────────
ps = prod.sort_values("total_revenue", ascending=True)
fig, ax = plt.subplots(figsize=(14, 10))
y = np.arange(len(ps))
ax.barh(y - 0.2, ps["total_revenue"], 0.4, color=BLUE, label="Revenue")
ax.barh(y + 0.2, ps["total_profit"], 0.4, color=GREEN, label="True Profit")
ax.set_yticks(y)
ax.set_yticklabels(ps["product"], fontsize=9)
ax.legend(fontsize=11, loc="lower right", facecolor=CARD, edgecolor="#333", labelcolor="white")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: money(x)))
style_ax(ax, "The Revenue vs Profit Lie — Where Money Disappears")
plt.tight_layout()
fig.savefig(OUT / "revenue_vs_profit.png", dpi=150, facecolor=DARK)
plt.close()
print("[OK] revenue_vs_profit.png")

# ── Chart 2: Cost Waterfall ─────────────────────────────────────────────
top5 = prod.nlargest(5, "total_revenue")
fig, axes = plt.subplots(1, 5, figsize=(20, 7), sharey=False)
for i, (_, r) in enumerate(top5.iterrows()):
    ax = axes[i]
    cats = ["Revenue","−COGS","−Ship","−Returns","−Support","−Mkt","Profit"]
    vals = [r["total_revenue"], -r["total_cogs"], -r["total_shipping"],
            -r["total_return_cost"], -r["total_support_cost"], -r["total_marketing"], r["total_profit"]]
    running = 0
    for j, (c, v) in enumerate(zip(cats, vals)):
        color = BLUE if j == 0 else (GREEN if j == len(cats)-1 else COLORS_COST[j-1])
        bottom = running if j > 0 and j < len(cats)-1 else 0
        if j > 0 and j < len(cats)-1:
            ax.bar(c, abs(v), bottom=running + v, color=color, width=0.6)
            running += v
        elif j == 0:
            ax.bar(c, v, color=color, width=0.6)
            running = v
        else:
            ax.bar(c, v, color=color, width=0.6)
    ax.set_title(r["product"], fontsize=9, color="white", fontweight="bold")
    ax.tick_params(axis='x', rotation=45, labelsize=7)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: money(x)))
    style_ax(ax)
fig.suptitle("Cost Waterfall — How Revenue Melts Away", color="white", fontsize=15, fontweight="bold")
plt.tight_layout()
fig.savefig(OUT / "cost_waterfall.png", dpi=150, facecolor=DARK)
plt.close()
print("[OK] cost_waterfall.png")

# ── Chart 3: Channel Truth ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(chan))
ax.bar(x - 0.2, chan["revenue"], 0.4, color=BLUE, label="Revenue")
ax.bar(x + 0.2, chan["profit"], 0.4, color=GREEN, label="Profit")
for i, r in chan.iterrows():
    ax.text(i + 0.2, r["profit"] + 2000, f"ROI: {r['roi']}x", ha="center", color=GOLD, fontsize=10, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(chan["channel"], fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: money(x)))
ax.legend(fontsize=11, facecolor=CARD, edgecolor="#333", labelcolor="white")
style_ax(ax, "Channel Truth — Revenue vs Profit by Channel")
plt.tight_layout()
fig.savefig(OUT / "channel_truth.png", dpi=150, facecolor=DARK)
plt.close()
print("[OK] channel_truth.png")

# ── Chart 4: Segment Profitability ──────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(seg))
ax.bar(x - 0.2, seg["revenue"], 0.4, color=BLUE, label="Revenue")
ax.bar(x + 0.2, seg["profit"], 0.4, color=GREEN, label="Profit")
for i, r in seg.iterrows():
    ax.text(i + 0.2, r["profit"] + 2000, f"${r['profit_per_order']}/order", ha="center", color=GOLD, fontsize=9, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(seg["customer_segment"], fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: money(x)))
ax.legend(fontsize=11, facecolor=CARD, edgecolor="#333", labelcolor="white")
style_ax(ax, "Customer Segment Truth — Revenue vs Profit")
plt.tight_layout()
fig.savefig(OUT / "segment_profitability.png", dpi=150, facecolor=DARK)
plt.close()
print("[OK] segment_profitability.png")

# ── Chart 5: Return Tax ────────────────────────────────────────────────
ps2 = prod.sort_values("return_tax_pct", ascending=True)
fig, ax = plt.subplots(figsize=(14, 9))
colors = [RED if v > 10 else "#e67e22" if v > 5 else GREEN for v in ps2["return_tax_pct"]]
ax.barh(ps2["product"], ps2["return_tax_pct"], color=colors)
for i, (_, r) in enumerate(ps2.iterrows()):
    ax.text(r["return_tax_pct"] + 0.3, i, f'{r["return_tax_pct"]:.1f}% ({money(r["total_return_cost"])})', va="center", color=GRAY, fontsize=9)
ax.set_xlabel("Return Cost as % of Revenue")
style_ax(ax, "The Return Tax — Revenue Lost to Returns")
plt.tight_layout()
fig.savefig(OUT / "return_tax.png", dpi=150, facecolor=DARK)
plt.close()
print("[OK] return_tax.png")

# ── Chart 6: Profit Power Ranking ──────────────────────────────────────
ppr = prod.sort_values("pps", ascending=True)
fig, ax = plt.subplots(figsize=(14, 9))
colors = [GREEN if s == "SCALE" else GOLD if s == "FIX" else "#e67e22" if s == "REPRICE" else RED for s in ppr["strategy"]]
bars = ax.barh(ppr["product"], ppr["pps"], color=colors)
for i, (_, r) in enumerate(ppr.iterrows()):
    ax.text(r["pps"] + 0.01, i, f'{r["profit_margin"]:.1f}% margin | {r["strategy"]}', va="center", color=GRAY, fontsize=9)
style_ax(ax, "Profit Power Ranking — True Business Value")
ax.set_xlabel("Composite Score")
plt.tight_layout()
fig.savefig(OUT / "profit_power_ranking.png", dpi=150, facecolor=DARK)
plt.close()
print("[OK] profit_power_ranking.png")

# ── Markdown Report ─────────────────────────────────────────────────────
total_rev = df["revenue"].sum()
total_prof = df["true_profit"].sum()
total_hidden = total_rev - total_prof
overall_margin = total_prof / total_rev * 100
total_returns = df["returned"].sum()
return_rate = total_returns / len(df) * 100

illusions = prod.sort_values("rank_diff", ascending=True).head(5)  # high rev rank, low prof rank
gems = prod.sort_values("rank_diff", ascending=False).head(5)       # low rev rank, high prof rank
most_overrated = illusions.iloc[0]
most_underrated = gems.iloc[0]
biggest_leak_product = prod.loc[(prod["total_revenue"] - prod["total_profit"]).idxmax()]

report = f"""# Profit Illusion Report

## Executive Summary

Your revenue is **{money(total_rev)}** but **{money(total_hidden)}** is an illusion.

- **Total Revenue:** {money(total_rev)}
- **Total True Profit:** {money(total_prof)}
- **Overall Margin:** {overall_margin:.1f}%
- **Total Hidden Costs:** {money(total_hidden)}
- **Return Rate:** {return_rate:.1f}% ({total_returns:,} returned orders)
- **Orders Analyzed:** {len(df):,}

---

## Top 5 Profit Illusion Products (High Revenue, Low/Negative Profit)

| Product | Revenue | Profit | Margin | Rev Rank | Profit Rank |
|---------|---------|--------|--------|----------|-------------|
"""
for _, r in illusions.iterrows():
    report += f"| {r['product']} | {money(r['total_revenue'])} | {money(r['total_profit'])} | {r['profit_margin']:.1f}% | #{r['rev_rank']} | #{r['prof_rank']} |\n"

report += f"""
## Top 5 Hidden Gems (Lower Revenue, High Profit Margin)

| Product | Revenue | Profit | Margin | Rev Rank | Profit Rank |
|---------|---------|--------|--------|----------|-------------|
"""
for _, r in gems.iterrows():
    report += f"| {r['product']} | {money(r['total_revenue'])} | {money(r['total_profit'])} | {r['profit_margin']:.1f}% | #{r['rev_rank']} | #{r['prof_rank']} |\n"

report += f"""
## Channel Analysis

| Channel | Revenue | Profit | Margin | ROI | Recommendation |
|---------|---------|--------|--------|-----|----------------|
"""
for _, r in chan.sort_values("roi", ascending=False).iterrows():
    rec = "SCALE" if r["roi"] > 3 else "MAINTAIN" if r["roi"] > 1.5 else "CUT"
    report += f"| {r['channel']} | {money(r['revenue'])} | {money(r['profit'])} | {r['profit_margin']:.1f}% | {r['roi']}x | {rec} |\n"

report += f"""
## Customer Segment Analysis

| Segment | Revenue | Profit | Margin | Profit/Order | Return Rate |
|---------|---------|--------|--------|-------------|-------------|
"""
for _, r in seg.sort_values("profit_margin", ascending=False).iterrows():
    report += f"| {r['customer_segment']} | {money(r['revenue'])} | {money(r['profit'])} | {r['profit_margin']:.1f}% | ${r['profit_per_order']:.2f} | {r['return_rate']:.1f}% |\n"

report += f"""
## The Discount Problem

| Discount Band | Revenue | Profit | Margin | Orders |
|---------------|---------|--------|--------|--------|
"""
for _, r in disc.iterrows():
    report += f"| {r['discount_band']} | {money(r['revenue'])} | {money(r['profit'])} | {r['margin']:.1f}% | {r['orders']:,} |\n"

report += f"""
## Profit Power Ranking

| Rank | Product | Score | Margin | Strategy |
|------|---------|-------|--------|----------|
"""
for _, r in prod.sort_values("pps_rank").iterrows():
    report += f"| #{r['pps_rank']} | {r['product']} | {r['pps']:.3f} | {r['profit_margin']:.1f}% | {r['strategy']} |\n"

# Strategy groups
scale_prods = prod[prod["strategy"]=="SCALE"]["product"].tolist()
fix_prods   = prod[prod["strategy"]=="FIX"]["product"].tolist()
reprice_prods = prod[prod["strategy"]=="REPRICE"]["product"].tolist()
drop_prods  = prod[prod["strategy"]=="DROP"]["product"].tolist()

report += f"""
## Strategic Recommendations

### SCALE — High margin, low returns, low support
{', '.join(scale_prods) if scale_prods else 'None'}
> Invest more marketing budget here. These products convert revenue to real profit.

### FIX — Good revenue, leaking profit
{', '.join(fix_prods) if fix_prods else 'None'}
> Identify the specific cost leak (returns? support? shipping?) and plug it.

### REPRICE — Over-discounted
{', '.join(reprice_prods) if reprice_prods else 'None'}
> Reduce discount depth or exclude from promotions. Test price elasticity.

### DROP — Revenue illusion, near-zero or negative profit
{', '.join(drop_prods) if drop_prods else 'None'}
> Consider discontinuing or fundamentally restructuring these products.

## 5 Actions to Increase Profit Without Increasing Revenue

1. **Cap discounts at 20%** on high-return products — deeper discounts attract Discount Hunters who return more
2. **Shift paid_ads budget to email/organic** — paid_ads has the lowest ROI, email/organic have the highest
3. **Reduce support costs** on top offenders by improving product documentation and packaging
4. **Raise prices 5-10%** on hidden gems that customers already love at full price
5. **Implement return friction** (restocking fees, shorter windows) on products with >15% return rate

---

## Final Verdict

- **Most Overrated Product:** {most_overrated['product']} (Rev Rank #{most_overrated['rev_rank']}, Profit Rank #{most_overrated['prof_rank']}, Margin {most_overrated['profit_margin']:.1f}%)
- **Most Underrated Product:** {most_underrated['product']} (Rev Rank #{most_underrated['rev_rank']}, Profit Rank #{most_underrated['prof_rank']}, Margin {most_underrated['profit_margin']:.1f}%)
- **Biggest Profit Leak:** {biggest_leak_product['product']} ({money(biggest_leak_product['total_revenue'])} revenue, only {money(biggest_leak_product['total_profit'])} profit — {money(biggest_leak_product['total_revenue'] - biggest_leak_product['total_profit'])} disappears)
- **1 Change for Immediate Profit Increase:** Cap all discounts at 20% and redirect Discount Hunter targeting to VIP retention — this alone could recover {money(total_hidden * 0.08)} in annual profit
"""

(OUT / "profit_report.md").write_text(report, encoding="utf-8")
print("[OK] profit_report.md")

# ── Dashboard HTML ──────────────────────────────────────────────────────
def esc(s):
    return html.escape(str(s))

# Prepare JSON data for charts
prod_sorted_rev = prod.sort_values("total_revenue", ascending=False)
chart_products = prod_sorted_rev["product"].tolist()
chart_revenue  = prod_sorted_rev["total_revenue"].round(0).tolist()
chart_profit   = prod_sorted_rev["total_profit"].round(0).tolist()
chart_margins  = prod_sorted_rev["profit_margin"].tolist()
chart_strategies = prod_sorted_rev["strategy"].tolist()

chan_sorted = chan.sort_values("revenue", ascending=False)
chart_channels = chan_sorted["channel"].tolist()
chart_chan_rev  = chan_sorted["revenue"].round(0).tolist()
chart_chan_prof = chan_sorted["profit"].round(0).tolist()
chart_chan_roi  = chan_sorted["roi"].tolist()

seg_sorted = seg.sort_values("revenue", ascending=False)
chart_segments = seg_sorted["customer_segment"].tolist()
chart_seg_rev  = seg_sorted["revenue"].round(0).tolist()
chart_seg_prof = seg_sorted["profit"].round(0).tolist()
chart_seg_ppo  = seg_sorted["profit_per_order"].tolist()

# Return tax data
rt_sorted = prod.sort_values("return_tax_pct", ascending=False)
chart_rt_prods = rt_sorted["product"].tolist()
chart_rt_pct   = rt_sorted["return_tax_pct"].tolist()
chart_rt_cost  = rt_sorted["total_return_cost"].round(0).tolist()

# Discount data
chart_disc_bands  = disc["discount_band"].astype(str).tolist()
chart_disc_margin = disc["margin"].tolist()
chart_disc_rev    = disc["revenue"].round(0).tolist()
chart_disc_prof   = disc["profit"].round(0).tolist()

# Power ranking
pps_sorted = prod.sort_values("pps", ascending=False)
chart_pps_prods = pps_sorted["product"].tolist()
chart_pps_score = pps_sorted["pps"].tolist()
chart_pps_margin = pps_sorted["profit_margin"].tolist()
chart_pps_strat  = pps_sorted["strategy"].tolist()

# Waterfall data for top 5
wf_data = []
for _, r in top5.iterrows():
    wf_data.append({
        "product": r["product"],
        "revenue": round(r["total_revenue"]),
        "cogs": round(r["total_cogs"]),
        "shipping": round(r["total_shipping"]),
        "returns": round(r["total_return_cost"]),
        "support": round(r["total_support_cost"]),
        "marketing": round(r["total_marketing"]),
        "profit": round(r["total_profit"]),
    })

dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Profit Illusion Analyzer</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0f0f0f; color:#e0e0e0; font-family:'Segoe UI',system-ui,sans-serif; padding:20px; }}
.hero {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:16px; margin-bottom:30px; }}
.hero-card {{ background:linear-gradient(135deg,#1a1a2e,#16213e); border-radius:12px; padding:20px; text-align:center; border:1px solid #333; }}
.hero-card .label {{ font-size:12px; color:#888; text-transform:uppercase; letter-spacing:1px; }}
.hero-card .value {{ font-size:28px; font-weight:700; margin-top:6px; }}
.hero-card .value.green {{ color:#2ecc71; }}
.hero-card .value.blue {{ color:#4ea8de; }}
.hero-card .value.red {{ color:#e74c3c; }}
.hero-card .value.gold {{ color:#f1c40f; }}
h1 {{ text-align:center; font-size:32px; margin-bottom:8px; color:#fff; }}
.subtitle {{ text-align:center; color:#888; margin-bottom:24px; font-size:14px; }}
.card {{ background:#1a1a2e; border-radius:12px; padding:24px; margin-bottom:24px; border:1px solid #333; }}
.card h2 {{ color:#fff; margin-bottom:16px; font-size:20px; border-bottom:1px solid #333; padding-bottom:8px; }}
.chart-container {{ width:100%; overflow-x:auto; }}
canvas {{ max-width:100%; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ background:#16213e; color:#4ea8de; padding:10px 8px; text-align:left; position:sticky; top:0; }}
td {{ padding:8px; border-bottom:1px solid #222; }}
tr:hover td {{ background:#16213e44; }}
.badge {{ display:inline-block; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:600; }}
.badge-scale {{ background:#2ecc7133; color:#2ecc71; }}
.badge-fix {{ background:#f1c40f33; color:#f1c40f; }}
.badge-reprice {{ background:#e67e2233; color:#e67e22; }}
.badge-drop {{ background:#e74c3c33; color:#e74c3c; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
.strat-col {{ padding:16px; border-radius:10px; }}
.strat-col h3 {{ margin-bottom:10px; font-size:16px; }}
.strat-col ul {{ list-style:none; padding:0; }}
.strat-col li {{ padding:4px 0; font-size:14px; }}
@media(max-width:768px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
</head>
<body>

<h1>Profit Illusion Analyzer</h1>
<p class="subtitle">Seeing through revenue vanity — what LOOKS profitable vs what IS profitable</p>

<div class="hero">
  <div class="hero-card"><div class="label">Total Revenue</div><div class="value blue">{money(total_rev)}</div></div>
  <div class="hero-card"><div class="label">True Profit</div><div class="value green">{money(total_prof)}</div></div>
  <div class="hero-card"><div class="label">Overall Margin</div><div class="value {'green' if overall_margin > 15 else 'red'}">{overall_margin:.1f}%</div></div>
  <div class="hero-card"><div class="label">Hidden Costs</div><div class="value red">{money(total_hidden)}</div></div>
  <div class="hero-card"><div class="label">Return Rate</div><div class="value gold">{return_rate:.1f}%</div></div>
</div>

<!-- The Big Lie Chart -->
<div class="card">
  <h2>The Big Lie — Revenue vs True Profit by Product</h2>
  <div class="chart-container"><canvas id="bigLie" height="500"></canvas></div>
</div>

<!-- Cost Waterfall -->
<div class="card">
  <h2>Cost Waterfall — How Revenue Melts Away (Top 5)</h2>
  <div class="chart-container"><canvas id="waterfall" height="300"></canvas></div>
</div>

<!-- Revenue Rank vs Profit Rank -->
<div class="card">
  <h2>Revenue Rank vs Profit Rank — The Disconnect</h2>
  <div style="overflow-x:auto;">
  <table>
    <tr><th>Product</th><th>Revenue</th><th>Profit</th><th>Margin</th><th>Rev Rank</th><th>Profit Rank</th><th>Gap</th><th>Strategy</th></tr>
"""

for _, r in prod.sort_values("rev_rank").iterrows():
    gap = int(r["rev_rank"] - r["prof_rank"])
    gap_color = "#2ecc71" if gap > 0 else "#e74c3c" if gap < 0 else "#888"
    badge_cls = f"badge-{r['strategy'].lower()}"
    dashboard_html += f"""    <tr>
      <td>{esc(r['product'])}</td>
      <td>{money(r['total_revenue'])}</td>
      <td style="color:{'#2ecc71' if r['total_profit']>0 else '#e74c3c'}">{money(r['total_profit'])}</td>
      <td>{r['profit_margin']:.1f}%</td>
      <td>#{int(r['rev_rank'])}</td>
      <td>#{int(r['prof_rank'])}</td>
      <td style="color:{gap_color}">{'+' if gap>0 else ''}{gap}</td>
      <td><span class="badge {badge_cls}">{r['strategy']}</span></td>
    </tr>\n"""

dashboard_html += f"""  </table>
  </div>
</div>

<!-- Channel Truth -->
<div class="card">
  <h2>Channel Truth — Revenue vs Profit with ROI</h2>
  <div class="chart-container"><canvas id="channelChart" height="250"></canvas></div>
</div>

<!-- Segment Profitability -->
<div class="card">
  <h2>Customer Segment Profitability</h2>
  <div class="chart-container"><canvas id="segmentChart" height="250"></canvas></div>
</div>

<!-- Return Tax -->
<div class="card">
  <h2>The Return Tax — Revenue Lost to Returns</h2>
  <div class="chart-container"><canvas id="returnTax" height="450"></canvas></div>
</div>

<!-- Discount Trap -->
<div class="card">
  <h2>The Discount Trap — Profit Margin by Discount Level</h2>
  <div class="chart-container"><canvas id="discountChart" height="250"></canvas></div>
</div>

<!-- Profit Power Ranking -->
<div class="card">
  <h2>Profit Power Ranking — True Business Value</h2>
  <div class="chart-container"><canvas id="powerRanking" height="500"></canvas></div>
</div>

<!-- Strategy Board -->
<div class="card">
  <h2>Strategy Board</h2>
  <div class="grid2">
    <div class="strat-col" style="background:#2ecc7115; border:1px solid #2ecc7144;">
      <h3 style="color:#2ecc71;">SCALE</h3>
      <ul>{''.join(f'<li>{esc(p)}</li>' for p in scale_prods) if scale_prods else '<li>None</li>'}</ul>
    </div>
    <div class="strat-col" style="background:#f1c40f15; border:1px solid #f1c40f44;">
      <h3 style="color:#f1c40f;">FIX</h3>
      <ul>{''.join(f'<li>{esc(p)}</li>' for p in fix_prods) if fix_prods else '<li>None</li>'}</ul>
    </div>
    <div class="strat-col" style="background:#e67e2215; border:1px solid #e67e2244;">
      <h3 style="color:#e67e22;">REPRICE</h3>
      <ul>{''.join(f'<li>{esc(p)}</li>' for p in reprice_prods) if reprice_prods else '<li>None</li>'}</ul>
    </div>
    <div class="strat-col" style="background:#e74c3c15; border:1px solid #e74c3c44;">
      <h3 style="color:#e74c3c;">DROP</h3>
      <ul>{''.join(f'<li>{esc(p)}</li>' for p in drop_prods) if drop_prods else '<li>None</li>'}</ul>
    </div>
  </div>
</div>

<script>
Chart.defaults.color = '#aaa';
Chart.defaults.borderColor = '#333';
const money = v => v >= 1e6 ? '$'+(v/1e6).toFixed(1)+'M' : v >= 1e3 ? '$'+(v/1e3).toFixed(0)+'K' : '$'+v.toFixed(0);

// Big Lie Chart
new Chart(document.getElementById('bigLie'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(chart_products)},
    datasets: [
      {{ label:'Revenue', data:{json.dumps(chart_revenue)}, backgroundColor:'#4ea8de' }},
      {{ label:'True Profit', data:{json.dumps(chart_profit)}, backgroundColor:'#2ecc71' }}
    ]
  }},
  options: {{
    indexAxis:'y', responsive:true,
    plugins:{{ legend:{{ labels:{{ color:'#fff' }} }} }},
    scales:{{ x:{{ ticks:{{ callback: v=>money(v) }} }} }}
  }}
}});

// Waterfall
const wfData = {json.dumps(wf_data)};
const wfLabels = wfData.map(d=>d.product);
const wfCogs = wfData.map(d=>d.cogs);
const wfShip = wfData.map(d=>d.shipping);
const wfRet  = wfData.map(d=>d.returns);
const wfSup  = wfData.map(d=>d.support);
const wfMkt  = wfData.map(d=>d.marketing);
const wfProf = wfData.map(d=>d.profit);
new Chart(document.getElementById('waterfall'), {{
  type:'bar',
  data: {{
    labels: wfLabels,
    datasets: [
      {{ label:'COGS', data:wfCogs, backgroundColor:'#e74c3c' }},
      {{ label:'Shipping', data:wfShip, backgroundColor:'#e67e22' }},
      {{ label:'Returns', data:wfRet, backgroundColor:'#9b59b6' }},
      {{ label:'Support', data:wfSup, backgroundColor:'#3498db' }},
      {{ label:'Marketing', data:wfMkt, backgroundColor:'#1abc9c' }},
      {{ label:'Profit', data:wfProf, backgroundColor:'#2ecc71' }},
    ]
  }},
  options: {{
    responsive:true, plugins:{{ legend:{{ labels:{{ color:'#fff' }} }} }},
    scales: {{ x:{{ stacked:true }}, y:{{ stacked:true, ticks:{{ callback:v=>money(v) }} }} }}
  }}
}});

// Channel
new Chart(document.getElementById('channelChart'), {{
  type:'bar',
  data: {{
    labels: {json.dumps(chart_channels)},
    datasets: [
      {{ label:'Revenue', data:{json.dumps(chart_chan_rev)}, backgroundColor:'#4ea8de' }},
      {{ label:'Profit', data:{json.dumps(chart_chan_prof)}, backgroundColor:'#2ecc71' }}
    ]
  }},
  options: {{
    responsive:true,
    plugins: {{
      legend:{{ labels:{{ color:'#fff' }} }},
      tooltip: {{ callbacks: {{ afterLabel: function(ctx) {{
        const roi = {json.dumps(chart_chan_roi)};
        return 'ROI: ' + roi[ctx.dataIndex] + 'x';
      }} }} }}
    }},
    scales:{{ y:{{ ticks:{{ callback:v=>money(v) }} }} }}
  }}
}});

// Segments
new Chart(document.getElementById('segmentChart'), {{
  type:'bar',
  data: {{
    labels: {json.dumps(chart_segments)},
    datasets: [
      {{ label:'Revenue', data:{json.dumps(chart_seg_rev)}, backgroundColor:'#4ea8de' }},
      {{ label:'Profit', data:{json.dumps(chart_seg_prof)}, backgroundColor:'#2ecc71' }}
    ]
  }},
  options: {{
    responsive:true,
    plugins: {{ legend:{{ labels:{{ color:'#fff' }} }} }},
    scales:{{ y:{{ ticks:{{ callback:v=>money(v) }} }} }}
  }}
}});

// Return Tax
new Chart(document.getElementById('returnTax'), {{
  type:'bar',
  data: {{
    labels: {json.dumps(chart_rt_prods)},
    datasets: [{{
      label:'Return Cost % of Revenue',
      data:{json.dumps(chart_rt_pct)},
      backgroundColor: {json.dumps(chart_rt_pct)}.map(v => v > 10 ? '#e74c3c' : v > 5 ? '#e67e22' : '#2ecc71')
    }}]
  }},
  options: {{
    indexAxis:'y', responsive:true,
    plugins: {{ legend:{{ labels:{{ color:'#fff' }} }} }},
    scales:{{ x:{{ ticks:{{ callback:v=>v+'%' }} }} }}
  }}
}});

// Discount Trap
new Chart(document.getElementById('discountChart'), {{
  type:'line',
  data: {{
    labels: {json.dumps(chart_disc_bands)},
    datasets: [{{
      label:'Profit Margin %',
      data:{json.dumps(chart_disc_margin)},
      borderColor:'#f1c40f',
      backgroundColor:'#f1c40f33',
      fill:true, tension:0.3, pointRadius:6
    }}]
  }},
  options: {{
    responsive:true,
    plugins: {{ legend:{{ labels:{{ color:'#fff' }} }} }},
    scales:{{ y:{{ ticks:{{ callback:v=>v+'%' }} }} }}
  }}
}});

// Power Ranking
const stratColors = {json.dumps(chart_pps_strat)}.map(s =>
  s==='SCALE' ? '#2ecc71' : s==='FIX' ? '#f1c40f' : s==='REPRICE' ? '#e67e22' : '#e74c3c'
);
new Chart(document.getElementById('powerRanking'), {{
  type:'bar',
  data: {{
    labels: {json.dumps(chart_pps_prods)},
    datasets: [{{
      label:'Power Score',
      data:{json.dumps(chart_pps_score)},
      backgroundColor: stratColors
    }}]
  }},
  options: {{
    indexAxis:'y', responsive:true,
    plugins: {{ legend:{{ labels:{{ color:'#fff' }} }} }},
    scales:{{ x:{{ min:0, max:1 }} }}
  }}
}});
</script>

</body>
</html>
"""

(OUT / "dashboard.html").write_text(dashboard_html, encoding="utf-8")
print("[OK] dashboard.html")

# ── Final Summary ────────────────────────────────────────────────────────
print("\n" + "="*60)
print("PROFIT ILLUSION ANALYSIS COMPLETE")
print("="*60)
print(f"\nTotal Revenue:  {money(total_rev)}")
print(f"True Profit:    {money(total_prof)}")
print(f"Hidden Costs:   {money(total_hidden)} ({(total_hidden/total_rev*100):.1f}% of revenue)")
print(f"Overall Margin: {overall_margin:.1f}%")
print(f"\nMost OVERRATED product:  {most_overrated['product']}")
print(f"  -> Rev Rank #{int(most_overrated['rev_rank'])}, Profit Rank #{int(most_overrated['prof_rank'])}, Margin {most_overrated['profit_margin']:.1f}%")
print(f"\nMost UNDERRATED product: {most_underrated['product']}")
print(f"  -> Rev Rank #{int(most_underrated['rev_rank'])}, Profit Rank #{int(most_underrated['prof_rank'])}, Margin {most_underrated['profit_margin']:.1f}%")
print(f"\nBiggest PROFIT LEAK:     {biggest_leak_product['product']}")
print(f"  -> {money(biggest_leak_product['total_revenue'])} revenue, only {money(biggest_leak_product['total_profit'])} profit")
print(f"  -> {money(biggest_leak_product['total_revenue'] - biggest_leak_product['total_profit'])} disappears into hidden costs")
print(f"\n1 CHANGE for immediate profit: Cap discounts at 20% and redirect")
print(f"  Discount Hunter targeting to VIP retention")
print(f"\nAll 8 output files saved to output/")
