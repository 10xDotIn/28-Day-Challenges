"""
NYC Airbnb Market Dashboard Generator
Generates a self-contained interactive HTML dashboard using Plotly.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# ── Load and prepare data ────────────────────────────────────────────────────
df = pd.read_csv("C:/Users/Anit/Downloads/28-Day-Challenges/Day 2/airbnb_cleaned.csv")

# Cap prices at $1000 for visualizations
df_viz = df.copy()
df_viz["Price"] = df_viz["Price"].clip(upper=1000)

# Parse date columns
df_viz["First Review"] = pd.to_datetime(df_viz["First Review"], errors="coerce")
df_viz["Last Review"] = pd.to_datetime(df_viz["Last Review"], errors="coerce")

# ── Color palette (muted) ────────────────────────────────────────────────────
COLORS = {
    "primary": "#5B8DBE",
    "secondary": "#F2A154",
    "tertiary": "#7BC8A4",
    "quaternary": "#D4726A",
    "quinary": "#9B8EC5",
    "bg": "#FAFAFA",
}
DISTRICT_COLORS = {
    "Brooklyn": "#5B8DBE",
    "Manhattan": "#F2A154",
    "Queens": "#7BC8A4",
    "Bronx": "#D4726A",
    "Staten Island": "#9B8EC5",
}
ROOM_COLORS = {
    "Entire place": "#5B8DBE",
    "Private room": "#F2A154",
    "Shared room": "#7BC8A4",
}
TEMPLATE = "plotly_white"
CHART_HEIGHT = 500

# ── Helper ────────────────────────────────────────────────────────────────────
def styled_layout(title, **kwargs):
    """Return common layout kwargs."""
    base = dict(
        template=TEMPLATE,
        title=dict(text=title, font=dict(size=18, color="#333")),
        height=CHART_HEIGHT,
        margin=dict(l=60, r=30, t=60, b=50),
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color="#555"),
    )
    base.update(kwargs)
    return base


figures = []  # list of (section, fig) tuples

# ══════════════════════════════════════════════════════════════════════════════
#  PRICING ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

# 1 ── Price Distribution Histogram ───────────────────────────────────────────
fig1 = go.Figure()
fig1.add_trace(go.Histogram(
    x=df_viz["Price"], nbinsx=80,
    marker_color=COLORS["primary"], opacity=0.85,
    hovertemplate="Price: $%{x}<br>Count: %{y}<extra></extra>",
))
fig1.update_layout(**styled_layout(
    "Price Distribution (capped at $1,000)",
    xaxis_title="Price ($)", yaxis_title="Number of Listings",
))
figures.append(("Pricing Analysis", fig1))

# 2 ── Price by District (Box) ────────────────────────────────────────────────
district_order = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
fig2 = go.Figure()
for d in district_order:
    subset = df_viz[df_viz["District"] == d]
    fig2.add_trace(go.Box(
        y=subset["Price"], name=d,
        marker_color=DISTRICT_COLORS[d],
        boxmean="sd",
    ))
fig2.update_layout(**styled_layout(
    "Price by District",
    yaxis_title="Price ($)", showlegend=False,
))
figures.append(("Pricing Analysis", fig2))

# 3 ── Price by Room Type (Violin) ────────────────────────────────────────────
fig3 = go.Figure()
for rt in ["Entire place", "Private room", "Shared room"]:
    subset = df_viz[df_viz["Room Type"] == rt]
    fig3.add_trace(go.Violin(
        y=subset["Price"], name=rt,
        marker_color=ROOM_COLORS[rt],
        box_visible=True, meanline_visible=True,
    ))
fig3.update_layout(**styled_layout(
    "Price by Room Type",
    yaxis_title="Price ($)", showlegend=False,
))
figures.append(("Pricing Analysis", fig3))

# 4 ── Avg Price by Neighborhood — Top 15 & Bottom 15 ─────────────────────────
nbr_avg = df_viz.groupby("Neighborhood")["Price"].mean().sort_values()
bottom15 = nbr_avg.head(15)
top15 = nbr_avg.tail(15)
combined = pd.concat([bottom15, top15])

fig4 = go.Figure()
colors4 = [COLORS["tertiary"]] * len(bottom15) + [COLORS["quaternary"]] * len(top15)
fig4.add_trace(go.Bar(
    y=combined.index, x=combined.values, orientation="h",
    marker_color=colors4,
    hovertemplate="%{y}: $%{x:.0f}<extra></extra>",
))
fig4.update_layout(**styled_layout(
    "Avg Price by Neighborhood — Bottom 15 (green) & Top 15 (red)",
    xaxis_title="Average Price ($)", yaxis_title="",
    height=600, margin=dict(l=180, r=30, t=60, b=50),
))
figures.append(("Pricing Analysis", fig4))

# 5 ── Price vs Accommodates (Scatter) ────────────────────────────────────────
fig5 = px.scatter(
    df_viz, x="Accommodates", y="Price", color="Room Type",
    color_discrete_map=ROOM_COLORS, opacity=0.4,
    template=TEMPLATE, title="Price vs Accommodates",
    hover_data=["District"],
)
fig5.update_layout(**styled_layout(
    "Price vs Accommodates",
    xaxis_title="Accommodates (guests)", yaxis_title="Price ($)",
))
figures.append(("Pricing Analysis", fig5))

# 6 ── Price vs Rating (Scatter) ──────────────────────────────────────────────
fig6 = px.scatter(
    df_viz.dropna(subset=["Rating"]),
    x="Rating", y="Price", color="District",
    color_discrete_map=DISTRICT_COLORS, opacity=0.35,
    template=TEMPLATE,
)
fig6.update_layout(**styled_layout(
    "Price vs Rating",
    xaxis_title="Rating", yaxis_title="Price ($)",
))
figures.append(("Pricing Analysis", fig6))

# 7 ── Price Heatmap: District x Room Type ────────────────────────────────────
pivot = df_viz.pivot_table(values="Price", index="District", columns="Room Type", aggfunc="mean")
pivot = pivot.reindex(index=district_order)
fig7 = go.Figure(go.Heatmap(
    z=pivot.values,
    x=pivot.columns.tolist(),
    y=pivot.index.tolist(),
    colorscale="Blues",
    text=np.round(pivot.values, 0),
    texttemplate="$%{text:.0f}",
    hovertemplate="District: %{y}<br>Room Type: %{x}<br>Avg Price: $%{z:.0f}<extra></extra>",
))
fig7.update_layout(**styled_layout(
    "Average Price Heatmap: District × Room Type",
    xaxis_title="Room Type", yaxis_title="District",
))
figures.append(("Pricing Analysis", fig7))

# 8 ── Instant Book vs Non-Instant Book Pricing ──────────────────────────────
fig8 = go.Figure()
for val, label, color in [(True, "Instant Book", COLORS["primary"]),
                           (False, "No Instant Book", COLORS["secondary"])]:
    subset = df_viz[df_viz["Instant Book"] == val]
    fig8.add_trace(go.Box(y=subset["Price"], name=label, marker_color=color, boxmean="sd"))
fig8.update_layout(**styled_layout(
    "Instant Book vs Non-Instant Book Pricing",
    yaxis_title="Price ($)", showlegend=False,
))
figures.append(("Pricing Analysis", fig8))

# 9 ── Superhost vs Non-Superhost Pricing ─────────────────────────────────────
fig9 = go.Figure()
for val, label, color in [(True, "Superhost", COLORS["tertiary"]),
                           (False, "Not Superhost", COLORS["quaternary"])]:
    subset = df_viz[df_viz["Superhost"] == val]
    fig9.add_trace(go.Box(y=subset["Price"], name=label, marker_color=color, boxmean="sd"))
fig9.update_layout(**styled_layout(
    "Superhost vs Non-Superhost Pricing",
    yaxis_title="Price ($)", showlegend=False,
))
figures.append(("Pricing Analysis", fig9))

# ══════════════════════════════════════════════════════════════════════════════
#  REVIEWS & RATINGS
# ══════════════════════════════════════════════════════════════════════════════

# 10 ── Rating Distribution Histogram ─────────────────────────────────────────
fig10 = go.Figure()
fig10.add_trace(go.Histogram(
    x=df_viz["Rating"].dropna(), nbinsx=50,
    marker_color=COLORS["secondary"], opacity=0.85,
    hovertemplate="Rating: %{x}<br>Count: %{y}<extra></extra>",
))
fig10.update_layout(**styled_layout(
    "Rating Distribution",
    xaxis_title="Rating", yaxis_title="Number of Listings",
))
figures.append(("Reviews & Ratings", fig10))

# 11 ── Rating by District (Box) ──────────────────────────────────────────────
fig11 = go.Figure()
for d in district_order:
    subset = df_viz[df_viz["District"] == d].dropna(subset=["Rating"])
    fig11.add_trace(go.Box(
        y=subset["Rating"], name=d,
        marker_color=DISTRICT_COLORS[d], boxmean="sd",
    ))
fig11.update_layout(**styled_layout(
    "Rating by District",
    yaxis_title="Rating", showlegend=False,
))
figures.append(("Reviews & Ratings", fig11))

# 12 ── Rating by Room Type (Box) ─────────────────────────────────────────────
fig12 = go.Figure()
for rt in ["Entire place", "Private room", "Shared room"]:
    subset = df_viz[df_viz["Room Type"] == rt].dropna(subset=["Rating"])
    fig12.add_trace(go.Box(
        y=subset["Rating"], name=rt,
        marker_color=ROOM_COLORS[rt], boxmean="sd",
    ))
fig12.update_layout(**styled_layout(
    "Rating by Room Type",
    yaxis_title="Rating", showlegend=False,
))
figures.append(("Reviews & Ratings", fig12))

# 13 ── Review Volume Over Time (Monthly Trend) ──────────────────────────────
reviews_time = df_viz.dropna(subset=["First Review"]).copy()
reviews_time["Month"] = reviews_time["First Review"].dt.to_period("M").dt.to_timestamp()
monthly = reviews_time.groupby("Month").size().reset_index(name="New Listings")
fig13 = go.Figure()
fig13.add_trace(go.Scatter(
    x=monthly["Month"], y=monthly["New Listings"],
    mode="lines", line=dict(color=COLORS["primary"], width=2),
    fill="tozeroy", fillcolor="rgba(91,141,190,0.15)",
    hovertemplate="%{x|%b %Y}: %{y} listings<extra></extra>",
))
fig13.update_layout(**styled_layout(
    "New Listings Over Time (by First Review Month)",
    xaxis_title="Date", yaxis_title="Number of New Listings",
))
figures.append(("Reviews & Ratings", fig13))

# 14 ── Num_Reviews vs Rating (Scatter) ───────────────────────────────────────
fig14 = px.scatter(
    df_viz.dropna(subset=["Rating"]),
    x="Num_Reviews", y="Rating", color="District",
    color_discrete_map=DISTRICT_COLORS, opacity=0.35,
    template=TEMPLATE,
)
fig14.update_layout(**styled_layout(
    "Number of Reviews vs Rating",
    xaxis_title="Number of Reviews", yaxis_title="Rating",
))
figures.append(("Reviews & Ratings", fig14))

# 15 ── Top 20 Most Reviewed Listings (Horizontal Bar) ────────────────────────
top20 = df_viz.nlargest(20, "Num_Reviews")[["Place Name", "Num_Reviews", "District"]].copy()
top20 = top20.sort_values("Num_Reviews")
colors15 = [DISTRICT_COLORS.get(d, COLORS["primary"]) for d in top20["District"]]
fig15 = go.Figure()
fig15.add_trace(go.Bar(
    y=top20["Place Name"], x=top20["Num_Reviews"], orientation="h",
    marker_color=colors15,
    hovertemplate="%{y}<br>Reviews: %{x}<extra></extra>",
))
fig15.update_layout(**styled_layout(
    "Top 20 Most Reviewed Listings",
    xaxis_title="Number of Reviews", yaxis_title="",
    height=600, margin=dict(l=250, r=30, t=60, b=50),
))
figures.append(("Reviews & Ratings", fig15))

# 16 ── Days Since Last Review Distribution ───────────────────────────────────
fig16 = go.Figure()
fig16.add_trace(go.Histogram(
    x=df_viz["Days Since Last Review"].dropna(), nbinsx=60,
    marker_color=COLORS["quinary"], opacity=0.85,
    hovertemplate="Days: %{x}<br>Count: %{y}<extra></extra>",
))
fig16.update_layout(**styled_layout(
    "Days Since Last Review — Distribution",
    xaxis_title="Days Since Last Review", yaxis_title="Number of Listings",
))
figures.append(("Reviews & Ratings", fig16))

# 17 ── Listing Age vs Num_Reviews (Scatter) ──────────────────────────────────
fig17 = px.scatter(
    df_viz.dropna(subset=["Listing Age (days)"]),
    x="Listing Age (days)", y="Num_Reviews", color="Room Type",
    color_discrete_map=ROOM_COLORS, opacity=0.35,
    template=TEMPLATE,
)
fig17.update_layout(**styled_layout(
    "Listing Age vs Number of Reviews",
    xaxis_title="Listing Age (days)", yaxis_title="Number of Reviews",
))
figures.append(("Reviews & Ratings", fig17))

# 18 ── Rating vs Response Time (Bar) ─────────────────────────────────────────
rt_rating = (
    df_viz.dropna(subset=["Response Time", "Rating"])
    .groupby("Response Time")["Rating"]
    .mean()
    .sort_values(ascending=True)
    .reset_index()
)
fig18 = go.Figure()
fig18.add_trace(go.Bar(
    y=rt_rating["Response Time"], x=rt_rating["Rating"], orientation="h",
    marker_color=COLORS["primary"],
    hovertemplate="%{y}: %{x:.2f}<extra></extra>",
))
fig18.update_layout(**styled_layout(
    "Average Rating by Host Response Time",
    xaxis_title="Average Rating", yaxis_title="",
    height=400, margin=dict(l=200, r=30, t=60, b=50),
))
figures.append(("Reviews & Ratings", fig18))

# ══════════════════════════════════════════════════════════════════════════════
#  BUILD HTML
# ══════════════════════════════════════════════════════════════════════════════

html_parts = []

# HTML head
html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NYC Airbnb Market Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background: #f5f6fa;
    color: #333;
  }
  .header {
    background: linear-gradient(135deg, #2c3e6b 0%, #5B8DBE 100%);
    color: white;
    text-align: center;
    padding: 40px 20px 30px;
  }
  .header h1 { font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px; }
  .header p { font-size: 1rem; opacity: 0.85; margin-top: 8px; }
  .container { max-width: 1100px; margin: 0 auto; padding: 30px 20px 60px; }
  .section-title {
    font-size: 1.5rem; font-weight: 600; color: #2c3e6b;
    border-bottom: 3px solid #5B8DBE; padding-bottom: 8px;
    margin: 40px 0 20px;
  }
  .chart-card {
    background: white;
    border-radius: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    margin-bottom: 28px;
    padding: 10px;
    overflow: hidden;
  }
  .footer {
    text-align: center; color: #999; font-size: 0.85rem;
    padding: 20px; border-top: 1px solid #e0e0e0;
    margin-top: 40px;
  }
</style>
</head>
<body>
<div class="header">
  <h1>NYC Airbnb Market Dashboard</h1>
  <p>Interactive analysis of 5,999 listings across New York City &mdash; Prices capped at $1,000</p>
</div>
<div class="container">
""")

current_section = None
for section, fig in figures:
    if section != current_section:
        current_section = section
        html_parts.append(f'<h2 class="section-title">{section}</h2>\n')
    chart_html = fig.to_html(full_html=False, include_plotlyjs=False)
    html_parts.append(f'<div class="chart-card">{chart_html}</div>\n')

html_parts.append("""
<div class="footer">NYC Airbnb Market Dashboard &mdash; Generated with Plotly</div>
</div>
</body>
</html>
""")

output_path = "C:/Users/Anit/Downloads/28-Day-Challenges/Day 2/airbnb_dashboard.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("".join(html_parts))

print(f"Dashboard saved to {output_path}")
print(f"Total charts: {len(figures)}")
