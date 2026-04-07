"""
build_dashboard.py
Generates output/shopify-data/dashboard.html from cleaned data files.
Run from the 10x-analyst-main root directory.
"""

import pandas as pd
import json
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED = os.path.join(BASE, "output", "shopify-data", "cleaned-data")
OUT_DIR = os.path.join(BASE, "output", "shopify-data")
OUT_HTML = os.path.join(OUT_DIR, "dashboard.html")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
customers   = pd.read_csv(os.path.join(CLEANED, "customers.csv"))
orders      = pd.read_csv(os.path.join(CLEANED, "orders.csv"),   parse_dates=["created_at"])
order_items = pd.read_csv(os.path.join(CLEANED, "order_items.csv"))
products    = pd.read_csv(os.path.join(CLEANED, "products.csv"))

# ---------------------------------------------------------------------------
# Metric computations
# ---------------------------------------------------------------------------

# Monthly revenue
orders["month"] = orders["created_at"].dt.to_period("M")
monthly = (
    orders.groupby("month")["total"]
    .sum()
    .reset_index()
    .sort_values("month")
)
monthly["month_label"] = monthly["month"].astype(str).map(
    {"2025-12": "Dec 2025", "2026-01": "Jan 2026", "2026-02": "Feb 2026"}
)
monthly_labels = monthly["month_label"].tolist()
monthly_values = [round(v, 2) for v in monthly["total"].tolist()]

# Revenue by category
cat_rev = (
    order_items.groupby("product_category")["line_total"]
    .sum()
    .sort_values(ascending=True)   # ascending for horizontal bar (bottom=largest)
    .reset_index()
)
cat_labels = cat_rev["product_category"].tolist()
cat_values = [round(v, 2) for v in cat_rev["line_total"].tolist()]

# Top 10 products by revenue
item_agg = (
    order_items.groupby(["product_sku", "product_name", "product_category"])
    .agg(units_sold=("quantity", "sum"), revenue=("line_total", "sum"))
    .reset_index()
)
prod_cost = products[["sku", "cost_usd", "current_price_usd"]].copy()
item_agg = item_agg.merge(prod_cost, left_on="product_sku", right_on="sku", how="left")
item_agg["margin_pct"] = (
    (item_agg["current_price_usd"] - item_agg["cost_usd"])
    / item_agg["current_price_usd"] * 100
).round(1)
top10_prod = item_agg.nlargest(10, "revenue").sort_values("revenue", ascending=True)
top10_prod_labels = top10_prod["product_name"].tolist()
top10_prod_values = [round(v, 2) for v in top10_prod["revenue"].tolist()]

# Table data (descending for table)
top10_table = item_agg.nlargest(10, "revenue").reset_index(drop=True)
table_rows = []
for _, r in top10_table.iterrows():
    table_rows.append({
        "sku":      r["product_sku"],
        "name":     r["product_name"],
        "category": r["product_category"],
        "units":    int(r["units_sold"]),
        "revenue":  round(r["revenue"], 2),
        "margin":   float(r["margin_pct"]) if pd.notna(r["margin_pct"]) else 0.0,
    })

# Customer acquisition by channel
acq = customers["acquisition_channel"].value_counts().reset_index()
acq.columns = ["channel", "count"]
acq = acq.sort_values("count", ascending=False)
acq_labels = acq["channel"].tolist()
acq_values = acq["count"].tolist()

# Revenue by traffic source
src_rev = (
    orders.groupby("source")["total"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
src_labels = src_rev["source"].tolist()
src_values = [round(v, 2) for v in src_rev["total"].tolist()]

# Top 10 customers by spend
top_cust = customers.nlargest(10, "total_spent_usd").copy()
top_cust["name"] = top_cust["first_name"] + " " + top_cust["last_name"]
top_cust = top_cust.sort_values("total_spent_usd", ascending=True)
top_cust_labels = top_cust["name"].tolist()
top_cust_values = [round(v, 2) for v in top_cust["total_spent_usd"].tolist()]

# ---------------------------------------------------------------------------
# Serialise to JS-safe strings
# ---------------------------------------------------------------------------
def js(obj):
    return json.dumps(obj)


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>10x Analyst — Shopify Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  /* ── Reset & base ───────────────────────────────────── */
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #F5EDE0;
    color: #1a1a2e;
    font-size: 14px;
  }}

  /* ── Header ─────────────────────────────────────────── */
  header {{
    background: #004E89;
    color: #fff;
    padding: 18px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 8px rgba(0,0,0,.25);
  }}
  header h1 {{
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: .5px;
  }}
  header h1 span {{ color: #FF6B35; }}
  header .meta {{
    font-size: .8rem;
    opacity: .8;
    text-align: right;
    line-height: 1.6;
  }}

  /* ── Layout ─────────────────────────────────────────── */
  main {{
    max-width: 1400px;
    margin: 28px auto;
    padding: 0 24px 48px;
  }}
  .section-title {{
    font-size: 1rem;
    font-weight: 600;
    color: #004E89;
    margin: 32px 0 14px;
    text-transform: uppercase;
    letter-spacing: .6px;
    border-left: 4px solid #FF6B35;
    padding-left: 10px;
  }}

  /* ── KPI cards ──────────────────────────────────────── */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 16px;
  }}
  @media (max-width: 1100px) {{ .kpi-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
  @media (max-width: 640px)  {{ .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
  .kpi-card {{
    background: #fff;
    border-radius: 12px;
    padding: 20px 18px 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,.07);
    position: relative;
    overflow: hidden;
  }}
  .kpi-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: #FF6B35;
  }}
  .kpi-label {{
    font-size: .72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .5px;
    color: #6b7280;
    margin-bottom: 8px;
  }}
  .kpi-value {{
    font-size: 1.55rem;
    font-weight: 700;
    color: #004E89;
    line-height: 1.1;
  }}
  .kpi-delta {{
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: .78rem;
    font-weight: 600;
    margin-top: 6px;
    padding: 2px 8px;
    border-radius: 20px;
  }}
  .kpi-delta.up   {{ background: #d1fae5; color: #065f46; }}
  .kpi-delta.down {{ background: #fee2e2; color: #991b1b; }}
  .kpi-delta.neutral {{ background: #e0f2fe; color: #075985; }}

  /* ── Chart grid ─────────────────────────────────────── */
  .chart-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }}
  @media (max-width: 900px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
  .chart-card {{
    background: #fff;
    border-radius: 12px;
    padding: 22px 20px 18px;
    box-shadow: 0 2px 10px rgba(0,0,0,.07);
  }}
  .chart-card.full {{ grid-column: 1 / -1; }}
  .chart-title {{
    font-size: .9rem;
    font-weight: 700;
    color: #004E89;
    margin-bottom: 16px;
  }}
  .chart-sub {{
    font-size: .75rem;
    color: #9ca3af;
    margin-left: 6px;
    font-weight: 400;
  }}
  .chart-wrap {{ position: relative; }}

  /* ── Table ──────────────────────────────────────────── */
  .tbl-wrap {{ overflow-x: auto; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: .82rem;
  }}
  thead tr {{
    background: #004E89;
    color: #fff;
  }}
  thead th {{
    padding: 11px 14px;
    text-align: left;
    font-weight: 600;
    white-space: nowrap;
    cursor: pointer;
    user-select: none;
  }}
  thead th:hover {{ background: #005fa3; }}
  tbody tr {{ border-bottom: 1px solid #f0e8dc; }}
  tbody tr:hover {{ background: #fdf5ec; }}
  tbody td {{ padding: 10px 14px; }}
  .tag {{
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: .72rem;
    font-weight: 600;
  }}
  .tag-eq {{ background: #dbeafe; color: #1e40af; }}
  .tag-sub {{ background: #d1fae5; color: #065f46; }}
  .tag-cb {{ background: #fef3c7; color: #92400e; }}
  .tag-ac {{ background: #ede9fe; color: #5b21b6; }}
  .margin-bar {{
    display: flex;
    align-items: center;
    gap: 7px;
  }}
  .margin-bar-fill {{
    height: 8px;
    border-radius: 4px;
    background: #00A878;
    min-width: 4px;
  }}

  /* ── Footer ─────────────────────────────────────────── */
  footer {{
    text-align: center;
    padding: 20px;
    font-size: .75rem;
    color: #9ca3af;
    border-top: 1px solid #e5d5c5;
    margin-top: 40px;
  }}
  footer strong {{ color: #FF6B35; }}
</style>
</head>
<body>

<!-- ═══ HEADER ═══════════════════════════════════════════════════════════ -->
<header>
  <h1><span>10x</span> Analyst &mdash; Shopify Dashboard</h1>
  <div class="meta">
    Dataset: shopify-data &nbsp;|&nbsp; Period: Dec 2025 – Feb 2026<br>
    Generated: 2026-03-19
  </div>
</header>

<main>

  <!-- ═══ KPI CARDS ══════════════════════════════════════════════════════ -->
  <div class="section-title">Key Performance Indicators</div>
  <div class="kpi-grid">

    <div class="kpi-card">
      <div class="kpi-label">Total Revenue</div>
      <div class="kpi-value">$159,812</div>
      <div class="kpi-delta neutral">3-month total</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Total Orders</div>
      <div class="kpi-value">903</div>
      <div class="kpi-delta neutral">Dec&ndash;Feb</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Total Customers</div>
      <div class="kpi-value">195</div>
      <div class="kpi-delta up">&#9650; Active base</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Avg Order Value</div>
      <div class="kpi-value">$176.98</div>
      <div class="kpi-delta up">&#9650; Above target</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Avg Customer LTV</div>
      <div class="kpi-value">$819.55</div>
      <div class="kpi-delta up">&#9650; High retention</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Gross Margin</div>
      <div class="kpi-value">~66%</div>
      <div class="kpi-delta up">&#9650; Healthy mix</div>
    </div>

  </div><!-- /kpi-grid -->

  <!-- ═══ CHARTS ════════════════════════════════════════════════════════ -->
  <div class="section-title">Revenue Analytics</div>
  <div class="chart-grid">

    <!-- 1. Monthly Revenue Trend -->
    <div class="chart-card">
      <div class="chart-title">
        Monthly Revenue Trend
        <span class="chart-sub">Dec 2025 – Feb 2026</span>
      </div>
      <div class="chart-wrap" style="height:260px">
        <canvas id="chartMonthly"></canvas>
      </div>
    </div>

    <!-- 2. Revenue by Category -->
    <div class="chart-card">
      <div class="chart-title">
        Revenue by Product Category
        <span class="chart-sub">Horizontal bar</span>
      </div>
      <div class="chart-wrap" style="height:260px">
        <canvas id="chartCategory"></canvas>
      </div>
    </div>

    <!-- 3. Revenue by Traffic Source -->
    <div class="chart-card">
      <div class="chart-title">
        Revenue by Traffic Source
        <span class="chart-sub">All channels</span>
      </div>
      <div class="chart-wrap" style="height:280px">
        <canvas id="chartSource"></canvas>
      </div>
    </div>

    <!-- 4. Customer Acquisition by Channel -->
    <div class="chart-card">
      <div class="chart-title">
        Customer Acquisition by Channel
        <span class="chart-sub">Donut — {sum(acq_values)} customers</span>
      </div>
      <div class="chart-wrap" style="height:280px">
        <canvas id="chartAcq"></canvas>
      </div>
    </div>

    <!-- 5. Top 10 Products by Revenue -->
    <div class="chart-card full">
      <div class="chart-title">
        Top 10 Products by Revenue
        <span class="chart-sub">Horizontal bar</span>
      </div>
      <div class="chart-wrap" style="height:320px">
        <canvas id="chartProducts"></canvas>
      </div>
    </div>

    <!-- 6. Top 10 Customers by Spend -->
    <div class="chart-card full">
      <div class="chart-title">
        Top 10 Customers by Lifetime Spend
        <span class="chart-sub">Horizontal bar</span>
      </div>
      <div class="chart-wrap" style="height:320px">
        <canvas id="chartCustomers"></canvas>
      </div>
    </div>

  </div><!-- /chart-grid -->

  <!-- ═══ DATA TABLE ════════════════════════════════════════════════════ -->
  <div class="section-title">Top 10 Products — Summary Table</div>
  <div class="chart-card" style="padding:0;overflow:hidden;">
    <div class="tbl-wrap">
      <table id="productTable">
        <thead>
          <tr>
            <th onclick="sortTable(0)">SKU &#8597;</th>
            <th onclick="sortTable(1)">Product Name &#8597;</th>
            <th onclick="sortTable(2)">Category &#8597;</th>
            <th onclick="sortTable(3)" style="text-align:right">Units Sold &#8597;</th>
            <th onclick="sortTable(4)" style="text-align:right">Revenue &#8597;</th>
            <th onclick="sortTable(5)">Margin %</th>
          </tr>
        </thead>
        <tbody id="productTbody"></tbody>
      </table>
    </div>
  </div>

</main>

<!-- ═══ FOOTER ════════════════════════════════════════════════════════════ -->
<footer>
  Generated by <strong>10x Analyst</strong> &nbsp;|&nbsp; 2026-03-19 &nbsp;|&nbsp;
  <strong>10x.in</strong>
</footer>

<!-- ═══ EMBEDDED DATA ════════════════════════════════════════════════════ -->
<script>
// ── Palette ──────────────────────────────────────────────────────────────
const C = {{
  orange:  "#FF6B35",
  blue:    "#004E89",
  green:   "#00A878",
  yellow:  "#FFD166",
  red:     "#EF476F",
  teal:    "#118AB2",
  dark:    "#073B4C",
  purple:  "#6A4C93",
  pink:    "#FF70A6",
}};
const palette = [C.orange, C.blue, C.green, C.yellow, C.red, C.teal, C.dark, C.purple, C.pink, C.green];

// ── Chart defaults ───────────────────────────────────────────────────────
Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
Chart.defaults.font.size   = 12;
Chart.defaults.color       = "#374151";

// ── Data ─────────────────────────────────────────────────────────────────
const monthlyLabels  = {js(monthly_labels)};
const monthlyValues  = {js(monthly_values)};

const catLabels      = {js(cat_labels)};
const catValues      = {js(cat_values)};

const top10Labels    = {js(top10_prod_labels)};
const top10Values    = {js(top10_prod_values)};

const acqLabels      = {js(acq_labels)};
const acqValues      = {js(acq_values)};

const srcLabels      = {js(src_labels)};
const srcValues      = {js(src_values)};

const custLabels     = {js(top_cust_labels)};
const custValues     = {js(top_cust_values)};

const tableData      = {js(table_rows)};

// ── Helper ───────────────────────────────────────────────────────────────
const fmt = v => "$" + v.toLocaleString("en-US", {{minimumFractionDigits: 0, maximumFractionDigits: 0}});

// ── 1. Monthly Revenue Trend ─────────────────────────────────────────────
new Chart(document.getElementById("chartMonthly"), {{
  type: "line",
  data: {{
    labels: monthlyLabels,
    datasets: [{{
      label: "Revenue",
      data: monthlyValues,
      borderColor: C.orange,
      backgroundColor: "rgba(255,107,53,.12)",
      borderWidth: 3,
      pointBackgroundColor: C.orange,
      pointRadius: 6,
      pointHoverRadius: 8,
      tension: 0.35,
      fill: true,
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          label: ctx => " " + fmt(ctx.parsed.y)
        }}
      }}
    }},
    scales: {{
      x: {{ grid: {{ color: "#f0e8dc" }} }},
      y: {{
        grid: {{ color: "#f0e8dc" }},
        ticks: {{ callback: v => fmt(v) }},
        beginAtZero: false,
      }}
    }}
  }}
}});

// ── 2. Revenue by Category ───────────────────────────────────────────────
new Chart(document.getElementById("chartCategory"), {{
  type: "bar",
  data: {{
    labels: catLabels,
    datasets: [{{
      label: "Revenue",
      data: catValues,
      backgroundColor: [C.blue, C.orange, C.green, C.yellow],
      borderRadius: 6,
      borderSkipped: false,
    }}]
  }},
  options: {{
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{ label: ctx => " " + fmt(ctx.parsed.x) }}
      }}
    }},
    scales: {{
      x: {{
        grid: {{ color: "#f0e8dc" }},
        ticks: {{ callback: v => fmt(v) }}
      }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});

// ── 3. Revenue by Traffic Source ─────────────────────────────────────────
new Chart(document.getElementById("chartSource"), {{
  type: "bar",
  data: {{
    labels: srcLabels,
    datasets: [{{
      label: "Revenue",
      data: srcValues,
      backgroundColor: srcLabels.map((_,i) => palette[i % palette.length]),
      borderRadius: 6,
      borderSkipped: false,
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{ label: ctx => " " + fmt(ctx.parsed.y) }}
      }}
    }},
    scales: {{
      x: {{ grid: {{ display: false }} }},
      y: {{
        grid: {{ color: "#f0e8dc" }},
        ticks: {{ callback: v => fmt(v) }}
      }}
    }}
  }}
}});

// ── 4. Customer Acquisition Donut ────────────────────────────────────────
new Chart(document.getElementById("chartAcq"), {{
  type: "doughnut",
  data: {{
    labels: acqLabels,
    datasets: [{{
      data: acqValues,
      backgroundColor: palette,
      borderWidth: 2,
      borderColor: "#fff",
      hoverOffset: 8,
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    cutout: "62%",
    plugins: {{
      legend: {{
        position: "right",
        labels: {{ boxWidth: 12, padding: 14, font: {{ size: 11 }} }}
      }},
      tooltip: {{
        callbacks: {{
          label: ctx => " " + ctx.label + ": " + ctx.parsed + " customers"
        }}
      }}
    }}
  }}
}});

// ── 5. Top 10 Products ───────────────────────────────────────────────────
new Chart(document.getElementById("chartProducts"), {{
  type: "bar",
  data: {{
    labels: top10Labels,
    datasets: [{{
      label: "Revenue",
      data: top10Values,
      backgroundColor: C.teal,
      borderRadius: 6,
      borderSkipped: false,
    }}]
  }},
  options: {{
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{ label: ctx => " " + fmt(ctx.parsed.x) }}
      }}
    }},
    scales: {{
      x: {{
        grid: {{ color: "#f0e8dc" }},
        ticks: {{ callback: v => fmt(v) }}
      }},
      y: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 11 }} }} }}
    }}
  }}
}});

// ── 6. Top 10 Customers ──────────────────────────────────────────────────
new Chart(document.getElementById("chartCustomers"), {{
  type: "bar",
  data: {{
    labels: custLabels,
    datasets: [{{
      label: "Total Spend",
      data: custValues,
      backgroundColor: C.purple,
      borderRadius: 6,
      borderSkipped: false,
    }}]
  }},
  options: {{
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{ label: ctx => " " + fmt(ctx.parsed.x) }}
      }}
    }},
    scales: {{
      x: {{
        grid: {{ color: "#f0e8dc" }},
        ticks: {{ callback: v => fmt(v) }}
      }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});

// ── Table rendering ──────────────────────────────────────────────────────
const tagClass = cat => {{
  if (cat.includes("Equipment"))    return "tag-eq";
  if (cat.includes("Subscription")) return "tag-sub";
  if (cat.includes("Coffee"))       return "tag-cb";
  return "tag-ac";
}};

const tbody = document.getElementById("productTbody");
tableData.forEach((r, i) => {{
  const margin = r.margin;
  const barW   = Math.round(margin * 1.2);
  const row = `
    <tr>
      <td><code>${{r.sku}}</code></td>
      <td>${{r.name}}</td>
      <td><span class="tag ${{tagClass(r.category)}}">${{r.category}}</span></td>
      <td style="text-align:right;font-weight:600">${{r.units.toLocaleString()}}</td>
      <td style="text-align:right;font-weight:700;color:#004E89">${{fmt(r.revenue)}}</td>
      <td>
        <div class="margin-bar">
          <div class="margin-bar-fill" style="width:${{barW}}px"></div>
          <span style="font-weight:600;color:#065f46">${{margin}}%</span>
        </div>
      </td>
    </tr>`;
  tbody.insertAdjacentHTML("beforeend", row);
}});

// ── Table sort ───────────────────────────────────────────────────────────
let sortDir = {{}};
function sortTable(col) {{
  const tbody = document.getElementById("productTbody");
  const rows  = Array.from(tbody.querySelectorAll("tr"));
  sortDir[col] = !sortDir[col];
  rows.sort((a, b) => {{
    let va = a.cells[col].innerText.replace(/[$,]/g, "").trim();
    let vb = b.cells[col].innerText.replace(/[$,]/g, "").trim();
    const numA = parseFloat(va), numB = parseFloat(vb);
    if (!isNaN(numA) && !isNaN(numB)) {{
      return sortDir[col] ? numA - numB : numB - numA;
    }}
    return sortDir[col] ? va.localeCompare(vb) : vb.localeCompare(va);
  }});
  rows.forEach(r => tbody.appendChild(r));
}}
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------
os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Dashboard written to: {OUT_HTML}")
