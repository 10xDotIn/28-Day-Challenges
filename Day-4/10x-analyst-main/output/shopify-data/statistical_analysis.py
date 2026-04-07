"""
Comprehensive Statistical Analysis — shopify-data
Statistician Agent, 10x-Analyst Swarm
"""
import json
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

BASE = "C:/Users/p/Downloads/10x-analyst-main/10x-analyst-main/output/shopify-data"
CLEANED = f"{BASE}/cleaned-data"

# ── Load data ──────────────────────────────────────────────────────────────
customers   = pd.read_csv(f"{CLEANED}/customers.csv",   parse_dates=["signup_date"])
orders      = pd.read_csv(f"{CLEANED}/orders.csv",      parse_dates=["created_at"])
order_items = pd.read_csv(f"{CLEANED}/order_items.csv")
products    = pd.read_csv(f"{CLEANED}/products.csv")

print("=" * 70)
print("SHOPIFY-DATA — COMPREHENSIVE STATISTICAL ANALYSIS")
print("=" * 70)

# ══════════════════════════════════════════════════════════════════════════
# 1. REVENUE & ORDERS
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("1. REVENUE & ORDERS")
print("=" * 70)

total_revenue = orders["total"].sum()
total_orders  = len(orders)
aov           = orders["total"].mean()

print(f"  Total Revenue         : ${total_revenue:,.2f}")
print(f"  Total Orders          : {total_orders:,}")
print(f"  Average Order Value   : ${aov:.2f}")

# Monthly revenue trend
orders["month_year"] = orders["created_at"].dt.to_period("M")
monthly_rev = (
    orders.groupby("month_year")["total"]
    .agg(revenue="sum", order_count="count")
    .reset_index()
)
monthly_rev["month_str"] = monthly_rev["month_year"].astype(str)
monthly_rev["mom_pct"] = monthly_rev["revenue"].pct_change() * 100

print("\n  Monthly Revenue Trend:")
print(f"  {'Month':<12} {'Revenue':>12} {'Orders':>8} {'MoM %':>10}")
print(f"  {'-'*12} {'-'*12} {'-'*8} {'-'*10}")
for _, row in monthly_rev.iterrows():
    mom = f"{row['mom_pct']:+.1f}%" if pd.notna(row["mom_pct"]) else "—"
    print(f"  {row['month_str']:<12} ${row['revenue']:>11,.2f} {int(row['order_count']):>8,} {mom:>10}")

# Revenue by fulfillment_status
print("\n  Revenue by Fulfillment Status:")
rev_fulfill = (
    orders.groupby("fulfillment_status")["total"]
    .agg(revenue="sum", order_count="count")
    .sort_values("revenue", ascending=False)
)
for status, row in rev_fulfill.iterrows():
    print(f"    {status:<20} ${row['revenue']:>11,.2f}  ({int(row['order_count'])} orders)")

# Revenue by financial_status
print("\n  Revenue by Financial Status:")
rev_fin = (
    orders.groupby("financial_status")["total"]
    .agg(revenue="sum", order_count="count")
    .sort_values("revenue", ascending=False)
)
for status, row in rev_fin.iterrows():
    print(f"    {status:<20} ${row['revenue']:>11,.2f}  ({int(row['order_count'])} orders)")

# ══════════════════════════════════════════════════════════════════════════
# 2. CUSTOMER ANALYSIS
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("2. CUSTOMER ANALYSIS")
print("=" * 70)

total_customers = len(customers)
avg_clv         = customers["total_spent_usd"].mean()
median_clv      = customers["total_spent_usd"].median()
pct_marketing   = (customers["accepts_marketing"] == "yes").sum() / total_customers * 100

print(f"  Total Customers          : {total_customers:,}")
print(f"  Average CLV (total_spent): ${avg_clv:,.2f}")
print(f"  Median CLV               : ${median_clv:,.2f}")
print(f"  Accepts Marketing        : {pct_marketing:.1f}% ({(customers['accepts_marketing']=='yes').sum()} / {total_customers})")

# New customers per month by signup_date
customers["signup_month"] = customers["signup_date"].dt.to_period("M")
new_per_month = customers.groupby("signup_month").size().reset_index(name="new_customers")
new_per_month["month_str"] = new_per_month["signup_month"].astype(str)
print("\n  New Customers per Month (by signup_date):")
for _, row in new_per_month.iterrows():
    print(f"    {row['month_str']:<12} {int(row['new_customers']):>4} new customers")

# Top 10 customers by total_spent_usd
print("\n  Top 10 Customers by total_spent_usd:")
top10_customers = customers.nlargest(10, "total_spent_usd")[
    ["customer_id", "first_name", "last_name", "total_spent_usd", "total_orders"]
]
for i, (_, row) in enumerate(top10_customers.iterrows(), 1):
    print(f"    {i:>2}. {row['customer_id']}  {row['first_name']} {row['last_name']:<20} "
          f"${row['total_spent_usd']:>8,.2f}  ({int(row['total_orders'])} orders)")

# Acquisition channel
print("\n  Customer Acquisition by Channel:")
acq = customers["acquisition_channel"].value_counts()
for ch, cnt in acq.items():
    pct = cnt / total_customers * 100
    print(f"    {ch:<25} {cnt:>4}  ({pct:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════
# 3. PRODUCT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. PRODUCT ANALYSIS")
print("=" * 70)

# Join order_items with products for cost
items_prod = order_items.merge(
    products[["sku", "cost_usd", "category"]],
    left_on="product_sku", right_on="sku", how="left"
)

# Top 10 by revenue
print("\n  Top 10 Products by Revenue:")
rev_by_product = (
    items_prod.groupby(["product_sku", "product_name"])
    .agg(revenue=("line_total", "sum"), qty_sold=("quantity", "sum"))
    .sort_values("revenue", ascending=False)
    .head(10)
    .reset_index()
)
for i, row in rev_by_product.iterrows():
    print(f"    {i+1:>2}. {row['product_sku']:<10} {row['product_name']:<45} "
          f"${row['revenue']:>9,.2f}  (qty: {int(row['qty_sold']):,})")

# Top 10 by quantity sold
print("\n  Top 10 Products by Quantity Sold:")
qty_by_product = (
    items_prod.groupby(["product_sku", "product_name"])
    .agg(qty_sold=("quantity", "sum"), revenue=("line_total", "sum"))
    .sort_values("qty_sold", ascending=False)
    .head(10)
    .reset_index()
)
for i, row in qty_by_product.iterrows():
    print(f"    {i+1:>2}. {row['product_sku']:<10} {row['product_name']:<45} "
          f"qty: {int(row['qty_sold']):>5,}  (${row['revenue']:>9,.2f})")

# Revenue by product category
print("\n  Revenue by Product Category:")
rev_by_cat = (
    items_prod.groupby("product_category")
    .agg(revenue=("line_total", "sum"), qty_sold=("quantity", "sum"), orders=("order_id", "nunique"))
    .sort_values("revenue", ascending=False)
)
total_cat_rev = rev_by_cat["revenue"].sum()
for cat, row in rev_by_cat.iterrows():
    pct = row["revenue"] / total_cat_rev * 100
    print(f"    {cat:<25} ${row['revenue']:>11,.2f}  ({pct:.1f}%)  qty: {int(row['qty_sold']):,}")

# Gross margin by product
print("\n  Gross Margin by Product (Top 10 by absolute margin):")
items_prod["cogs"] = items_prod["cost_usd"] * items_prod["quantity"]
items_prod["gross_profit"] = items_prod["line_total"] - items_prod["cogs"]

margin_by_product = (
    items_prod.groupby(["product_sku", "product_name"])
    .agg(
        revenue=("line_total", "sum"),
        cogs=("cogs", "sum"),
        gross_profit=("gross_profit", "sum")
    )
    .reset_index()
)
margin_by_product["margin_pct"] = margin_by_product["gross_profit"] / margin_by_product["revenue"] * 100
margin_by_product = margin_by_product.sort_values("gross_profit", ascending=False).head(10)

print(f"    {'SKU':<10} {'Product':<45} {'Revenue':>10} {'COGS':>9} {'GP':>9} {'Margin%':>8}")
print(f"    {'-'*10} {'-'*45} {'-'*10} {'-'*9} {'-'*9} {'-'*8}")
for _, row in margin_by_product.iterrows():
    print(f"    {row['product_sku']:<10} {row['product_name']:<45} "
          f"${row['revenue']:>9,.2f} ${row['cogs']:>8,.2f} ${row['gross_profit']:>8,.2f} "
          f"{row['margin_pct']:>7.1f}%")

# ══════════════════════════════════════════════════════════════════════════
# 4. ORDER BEHAVIOR
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. ORDER BEHAVIOR")
print("=" * 70)

# Average items per order
items_per_order = order_items.groupby("order_id")["quantity"].sum()
avg_items_per_order = items_per_order.mean()
avg_line_items      = order_items.groupby("order_id").size().mean()

print(f"  Avg Items (qty) per Order        : {avg_items_per_order:.2f}")
print(f"  Avg Line Items per Order         : {avg_line_items:.2f}")

# Discount usage
orders_with_discount = orders[orders["discount_code"].notna() & (orders["discount_code"] != "")]
discount_usage_rate  = len(orders_with_discount) / total_orders * 100
avg_discount_amount  = orders_with_discount["discount_amount"].mean()
total_discount_value = orders_with_discount["discount_amount"].sum()

print(f"\n  Discount Usage Rate              : {discount_usage_rate:.1f}% ({len(orders_with_discount)} of {total_orders} orders)")
print(f"  Avg Discount Amount (w/ code)    : ${avg_discount_amount:.2f}")
print(f"  Total Discount Value Given       : ${total_discount_value:,.2f}")

print("\n  Discount Code Breakdown:")
disc_breakdown = orders_with_discount.groupby("discount_code").agg(
    order_count=("order_id", "count"),
    total_discount=("discount_amount", "sum"),
    avg_discount=("discount_amount", "mean")
).sort_values("order_count", ascending=False)
for code, row in disc_breakdown.iterrows():
    print(f"    {code:<15} {int(row['order_count']):>4} orders  "
          f"total: ${row['total_discount']:>8,.2f}  avg: ${row['avg_discount']:>6.2f}")

# Revenue by payment_method
print("\n  Revenue by Payment Method:")
rev_payment = (
    orders.groupby("payment_method")["total"]
    .agg(revenue="sum", order_count="count")
    .sort_values("revenue", ascending=False)
)
for method, row in rev_payment.iterrows():
    pct = row["revenue"] / total_revenue * 100
    print(f"    {method:<20} ${row['revenue']:>11,.2f}  ({pct:.1f}%  |  {int(row['order_count'])} orders)")

# Revenue by source
print("\n  Revenue by Source:")
rev_source = (
    orders.groupby("source")["total"]
    .agg(revenue="sum", order_count="count")
    .sort_values("revenue", ascending=False)
)
for src, row in rev_source.iterrows():
    pct = row["revenue"] / total_revenue * 100
    print(f"    {src:<25} ${row['revenue']:>11,.2f}  ({pct:.1f}%  |  {int(row['order_count'])} orders)")

# ══════════════════════════════════════════════════════════════════════════
# 5. GEOGRAPHIC
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. GEOGRAPHIC ANALYSIS")
print("=" * 70)

# Top 5 countries
print("\n  Top 5 Countries by Order Count & Revenue:")
geo_country = (
    orders.groupby("billing_country")
    .agg(order_count=("order_id", "count"), revenue=("total", "sum"))
    .sort_values("order_count", ascending=False)
    .head(5)
)
print(f"  {'Country':<10} {'Orders':>8} {'Revenue':>12}")
print(f"  {'-'*10} {'-'*8} {'-'*12}")
for country, row in geo_country.iterrows():
    print(f"  {country:<10} {int(row['order_count']):>8,} ${row['revenue']:>11,.2f}")

# Top 5 provinces
print("\n  Top 5 Provinces by Order Count & Revenue:")
geo_province = (
    orders.groupby("billing_province")
    .agg(order_count=("order_id", "count"), revenue=("total", "sum"))
    .sort_values("order_count", ascending=False)
    .head(5)
)
print(f"  {'Province':<20} {'Orders':>8} {'Revenue':>12}")
print(f"  {'-'*20} {'-'*8} {'-'*12}")
for prov, row in geo_province.iterrows():
    print(f"  {prov:<20} {int(row['order_count']):>8,} ${row['revenue']:>11,.2f}")

# ══════════════════════════════════════════════════════════════════════════
# BUILD insights.json
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("BUILDING insights.json")
print("=" * 70)

# Monthly data as plain dicts
monthly_rows = []
for _, row in monthly_rev.iterrows():
    monthly_rows.append({
        "month": row["month_str"],
        "revenue": round(float(row["revenue"]), 2),
        "order_count": int(row["order_count"]),
        "mom_pct": round(float(row["mom_pct"]), 2) if pd.notna(row["mom_pct"]) else None
    })

# Top 10 products by revenue
top10_rev_prod = []
for _, row in rev_by_product.iterrows():
    top10_rev_prod.append({
        "sku": row["product_sku"],
        "product_name": row["product_name"],
        "revenue": round(float(row["revenue"]), 2),
        "qty_sold": int(row["qty_sold"])
    })

# Top 10 products by qty
top10_qty_prod = []
for _, row in qty_by_product.iterrows():
    top10_qty_prod.append({
        "sku": row["product_sku"],
        "product_name": row["product_name"],
        "qty_sold": int(row["qty_sold"]),
        "revenue": round(float(row["revenue"]), 2)
    })

# Category revenue
cat_rev_dict = {}
for cat, row in rev_by_cat.iterrows():
    cat_rev_dict[cat] = {
        "revenue": round(float(row["revenue"]), 2),
        "qty_sold": int(row["qty_sold"]),
        "pct_of_total": round(float(row["revenue"] / total_cat_rev * 100), 2)
    }

# Gross margin full table
margin_full = (
    items_prod.groupby(["product_sku", "product_name"])
    .agg(revenue=("line_total", "sum"), cogs=("cogs", "sum"), gross_profit=("gross_profit", "sum"))
    .reset_index()
)
margin_full["margin_pct"] = (margin_full["gross_profit"] / margin_full["revenue"] * 100).round(2)
margin_full = margin_full.sort_values("gross_profit", ascending=False)
margin_list = []
for _, row in margin_full.iterrows():
    margin_list.append({
        "sku": row["product_sku"],
        "product_name": row["product_name"],
        "revenue": round(float(row["revenue"]), 2),
        "cogs": round(float(row["cogs"]), 2),
        "gross_profit": round(float(row["gross_profit"]), 2),
        "margin_pct": float(row["margin_pct"])
    })

# Top 10 customers
top10_cust_list = []
for _, row in top10_customers.iterrows():
    top10_cust_list.append({
        "customer_id": row["customer_id"],
        "name": f"{row['first_name']} {row['last_name']}",
        "total_spent_usd": round(float(row["total_spent_usd"]), 2),
        "total_orders": int(row["total_orders"])
    })

# Acquisition channel
acq_dict = {ch: int(cnt) for ch, cnt in acq.items()}

# New customers per month
new_cust_month = {row["month_str"]: int(row["new_customers"]) for _, row in new_per_month.iterrows()}

# Payment method revenue
pay_dict = {}
for method, row in rev_payment.iterrows():
    pay_dict[method] = {"revenue": round(float(row["revenue"]), 2), "order_count": int(row["order_count"])}

# Source revenue
src_dict = {}
for src, row in rev_source.iterrows():
    src_dict[src] = {"revenue": round(float(row["revenue"]), 2), "order_count": int(row["order_count"])}

# Geo top 5 countries
geo_country_list = []
for country, row in geo_country.iterrows():
    geo_country_list.append({"country": country, "order_count": int(row["order_count"]),
                              "revenue": round(float(row["revenue"]), 2)})

# Geo top 5 provinces
geo_province_list = []
for prov, row in geo_province.iterrows():
    geo_province_list.append({"province": prov, "order_count": int(row["order_count"]),
                               "revenue": round(float(row["revenue"]), 2)})

# Discount code breakdown
disc_code_list = []
for code, row in disc_breakdown.iterrows():
    disc_code_list.append({
        "code": code,
        "order_count": int(row["order_count"]),
        "total_discount": round(float(row["total_discount"]), 2),
        "avg_discount": round(float(row["avg_discount"]), 2)
    })

# Fulfillment status revenue
fulfill_dict = {}
for status, row in rev_fulfill.iterrows():
    fulfill_dict[status] = {"revenue": round(float(row["revenue"]), 2), "order_count": int(row["order_count"])}

# Overall total gross profit
total_gross_profit = items_prod["gross_profit"].sum()
overall_margin_pct = total_gross_profit / items_prod["line_total"].sum() * 100

insights = {
    "generated_at": "2026-03-19",
    "dataset": "shopify-data",

    "summary_kpis": {
        "total_revenue_usd": round(total_revenue, 2),
        "total_orders": total_orders,
        "average_order_value_usd": round(aov, 2),
        "total_customers": total_customers,
        "average_clv_usd": round(avg_clv, 2),
        "median_clv_usd": round(median_clv, 2),
        "pct_accepts_marketing": round(pct_marketing, 2),
        "avg_items_per_order": round(avg_items_per_order, 2),
        "avg_line_items_per_order": round(avg_line_items, 2),
        "discount_usage_rate_pct": round(discount_usage_rate, 2),
        "avg_discount_amount_usd": round(avg_discount_amount, 2),
        "total_discount_given_usd": round(total_discount_value, 2),
        "total_gross_profit_usd": round(total_gross_profit, 2),
        "overall_gross_margin_pct": round(overall_margin_pct, 2)
    },

    "revenue_orders": {
        "monthly_trend": monthly_rows,
        "by_fulfillment_status": fulfill_dict,
        "by_financial_status": {
            status: {"revenue": round(float(row["revenue"]), 2), "order_count": int(row["order_count"])}
            for status, row in rev_fin.iterrows()
        }
    },

    "customer_analysis": {
        "new_customers_per_month": new_cust_month,
        "acquisition_by_channel": acq_dict,
        "top_10_by_total_spent": top10_cust_list
    },

    "product_analysis": {
        "top_10_by_revenue": top10_rev_prod,
        "top_10_by_qty_sold": top10_qty_prod,
        "revenue_by_category": cat_rev_dict,
        "gross_margin_all_products": margin_list
    },

    "order_behavior": {
        "discount_by_code": disc_code_list,
        "revenue_by_payment_method": pay_dict,
        "revenue_by_source": src_dict
    },

    "geographic": {
        "top_5_countries": geo_country_list,
        "top_5_provinces": geo_province_list
    },

    "structured_insights": [
        {
            "id": "insight-001",
            "headline": f"Total revenue of ${total_revenue:,.2f} across {total_orders} orders with AOV ${aov:.2f}",
            "category": "revenue",
            "severity": "high",
            "metric": "total_revenue",
            "value": round(total_revenue, 2),
            "business_implication": "Baseline performance benchmark across 3-month operating window",
            "confidence": 1.0
        },
        {
            "id": "insight-002",
            "headline": f"MoM revenue change: {monthly_rows[1]['mom_pct']:+.1f}% (Dec→Jan), {monthly_rows[2]['mom_pct']:+.1f}% (Jan→Feb)",
            "category": "revenue_trend",
            "severity": "high",
            "metric": "monthly_revenue",
            "supporting_data": {r["month"]: r["revenue"] for r in monthly_rows},
            "business_implication": "Month-over-month growth trajectory indicates demand momentum",
            "confidence": 1.0
        },
        {
            "id": "insight-003",
            "headline": f"Discount usage at {discount_usage_rate:.1f}% — ${total_discount_value:,.2f} total discounts given",
            "category": "promotions",
            "severity": "medium",
            "metric": "discount_usage_rate",
            "value": round(discount_usage_rate, 2),
            "business_implication": "One-third of orders use discount codes; review margin impact vs. acquisition value",
            "confidence": 1.0
        },
        {
            "id": "insight-004",
            "headline": f"{pct_marketing:.1f}% of customers accept marketing — strong CRM list",
            "category": "customer",
            "severity": "medium",
            "metric": "marketing_opt_in_rate",
            "value": round(pct_marketing, 2),
            "business_implication": "High opt-in rate enables direct email campaigns to majority of customer base",
            "confidence": 1.0
        },
        {
            "id": "insight-005",
            "headline": f"Overall gross margin at {overall_margin_pct:.1f}% — total GP ${total_gross_profit:,.2f}",
            "category": "profitability",
            "severity": "high",
            "metric": "gross_margin_pct",
            "value": round(overall_margin_pct, 2),
            "business_implication": "Profitability health check — category and product-level margin varies significantly",
            "confidence": 1.0
        }
    ]
}

out_path = f"{BASE}/insights.json"
with open(out_path, "w") as f:
    json.dump(insights, f, indent=2)

print(f"\n  insights.json saved to: {out_path}")
print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
