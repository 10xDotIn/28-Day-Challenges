import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import base64, warnings
warnings.filterwarnings("ignore")

from textblob import TextBlob

df = pd.read_csv("data/hotel_reviews.csv", low_memory=False)
df["rating"] = pd.to_numeric(df["reviews.rating"], errors="coerce")
df["text"]   = df["reviews.text"].fillna("").astype(str)
df["hotel"]  = df["name"].fillna("Unknown").astype(str)
df["polarity"] = df["text"].apply(lambda t: TextBlob(t).sentiment.polarity)

# Classify each review
df["sentiment"] = df["polarity"].apply(
    lambda p: "Positive" if p > 0.1 else ("Negative" if p < -0.1 else "Neutral")
)

# ── Per-hotel stats ────────────────────────────────────────────────────────────
hotel_stats = (df.groupby("hotel")
               .apply(lambda g: pd.Series({
                   "total":    len(g),
                   "positive": (g["sentiment"] == "Positive").sum(),
                   "negative": (g["sentiment"] == "Negative").sum(),
                   "neutral":  (g["sentiment"] == "Neutral").sum(),
                   "avg_rating": g["rating"].mean(),
               }))
               .reset_index()
               .sort_values("total", ascending=False))

hotel_stats["pct_pos"] = hotel_stats["positive"] / hotel_stats["total"] * 100
hotel_stats["pct_neg"] = hotel_stats["negative"] / hotel_stats["total"] * 100

top20 = hotel_stats.head(20).copy()
top20["short"] = top20["hotel"].apply(lambda x: x[:32])

print(f"Total hotels: {len(hotel_stats)}")
print(hotel_stats[["hotel","total","positive","negative","neutral","avg_rating"]].head(10).to_string())

# ══════════════════════════════════════════════════════════════════════════════
# PNG 1 — reviews_per_hotel.png  (top 20 stacked bar)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(16, 10))
fig.patch.set_facecolor("#0a0a0a")
ax.set_facecolor("#111")

y = np.arange(len(top20))
bars_pos = ax.barh(y, top20["positive"], color="#00cc66", label="Positive", height=0.6)
bars_neu = ax.barh(y, top20["neutral"],  left=top20["positive"],
                   color="#888888", label="Neutral",  height=0.6)
bars_neg = ax.barh(y, top20["negative"], left=top20["positive"]+top20["neutral"],
                   color="#ff4444", label="Negative", height=0.6)

ax.set_yticks(y)
ax.set_yticklabels(top20["short"], color="white", fontsize=9)
ax.set_xlabel("Number of Reviews", color="white", fontsize=11)
ax.set_title("Reviews per Hotel — Positive / Neutral / Negative Breakdown (Top 20)",
             color="white", fontsize=14, fontweight="bold", pad=14)
ax.tick_params(colors="white")
for spine in ax.spines.values():
    spine.set_edgecolor("#333")
ax.xaxis.label.set_color("white")

# total count labels
for _, row_data in top20.iterrows():
    idx = top20.index.get_loc(row_data.name)
    ax.text(row_data["total"] + 8, idx, f'{int(row_data["total"])}',
            va="center", color="#ccc", fontsize=8)

ax.legend(facecolor="#222", edgecolor="#444", labelcolor="white", fontsize=10,
          loc="lower right")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig("output/reviews_per_hotel.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0a0a")
plt.close()
print("Saved: reviews_per_hotel.png")

# ══════════════════════════════════════════════════════════════════════════════
# HTML — hotel_sentiment.html  (interactive table + sample quotes)
# ══════════════════════════════════════════════════════════════════════════════

# For each hotel in top 20, grab best positive and worst negative review
def best_review(hotel_name, sentiment):
    sub = df[(df["hotel"] == hotel_name) & (df["sentiment"] == sentiment)]
    if sub.empty:
        return "—"
    if sentiment == "Positive":
        r = sub.loc[sub["polarity"].idxmax()]
    else:
        r = sub.loc[sub["polarity"].idxmin()]
    return str(r["text"])[:280].replace("<","&lt;").replace(">","&gt;")

rows_html = ""
for _, row_data in top20.iterrows():
    h = row_data["hotel"]
    pos_q = best_review(h, "Positive")
    neg_q = best_review(h, "Negative")
    bar_pos = row_data["pct_pos"]
    bar_neg = row_data["pct_neg"]
    bar_neu = 100 - bar_pos - bar_neg
    stars   = f"{row_data['avg_rating']:.1f}" if not np.isnan(row_data["avg_rating"]) else "N/A"

    rows_html += f"""
<div class="hotel-block">
  <div class="hotel-title">
    <span class="hname">{h[:55]}</span>
    <span class="stat green">{int(row_data['positive'])} positive</span>
    <span class="stat red">{int(row_data['negative'])} negative</span>
    <span class="stat gray">{int(row_data['neutral'])} neutral</span>
    <span class="stat yellow">★ {stars}</span>
    <span class="stat total">{int(row_data['total'])} total</span>
  </div>
  <div class="sentiment-bar">
    <div style="width:{bar_pos:.1f}%;background:#00cc66" title="Positive {bar_pos:.1f}%"></div>
    <div style="width:{bar_neu:.1f}%;background:#555" title="Neutral {bar_neu:.1f}%"></div>
    <div style="width:{bar_neg:.1f}%;background:#ff4444" title="Negative {bar_neg:.1f}%"></div>
  </div>
  <div class="bar-labels">
    <span style="color:#00cc66">{bar_pos:.0f}% positive</span>
    <span style="color:#555">{bar_neu:.0f}% neutral</span>
    <span style="color:#ff4444">{bar_neg:.0f}% negative</span>
  </div>
  <div class="quotes-grid">
    <div class="quote-card pos">
      <div class="qlabel">✅ Best Positive Review</div>
      <div class="qtext">"{pos_q}..."</div>
    </div>
    <div class="quote-card neg">
      <div class="qlabel">❌ Worst Negative Review</div>
      <div class="qtext">"{neg_q}..."</div>
    </div>
  </div>
</div>"""

# Embed chart
with open("output/reviews_per_hotel.png","rb") as f:
    chart_b64 = base64.b64encode(f.read()).decode()

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hotel Review Sentiment Analysis</title>
<style>
  * {{box-sizing:border-box;margin:0;padding:0}}
  body {{background:#0a0a0a;color:#e0e0e0;font-family:'Segoe UI',sans-serif;padding:30px}}

  .page-title {{color:#ff4444;font-size:2rem;font-weight:bold;text-transform:uppercase;
               letter-spacing:3px;text-align:center;margin-bottom:6px}}
  .page-sub   {{color:#888;text-align:center;margin-bottom:30px;font-size:0.95rem}}

  .chart-wrap {{text-align:center;margin-bottom:40px}}
  .chart-wrap img {{max-width:100%;border-radius:12px;border:1px solid #222}}

  .hotel-block {{background:#111;border:1px solid #222;border-radius:12px;
                 padding:20px;margin-bottom:22px;border-left:3px solid #ff4444}}

  .hotel-title {{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:12px}}
  .hname {{font-weight:bold;color:#ff8888;font-size:1rem;flex:1;min-width:200px}}
  .stat  {{font-size:0.82rem;padding:3px 10px;border-radius:6px;background:#1a1a1a;border:1px solid #333}}
  .green {{color:#00cc66}} .red {{color:#ff4444}} .gray {{color:#888}}
  .yellow{{color:#ffd700}} .total{{color:#aaa}}

  .sentiment-bar {{display:flex;height:10px;border-radius:5px;overflow:hidden;margin-bottom:4px}}
  .sentiment-bar div {{transition:width .4s}}

  .bar-labels {{display:flex;gap:16px;font-size:0.8rem;margin-bottom:14px}}

  .quotes-grid {{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
  .quote-card {{background:#0d0d0d;border-radius:8px;padding:14px}}
  .quote-card.pos {{border-left:3px solid #00cc66}}
  .quote-card.neg {{border-left:3px solid #ff4444}}
  .qlabel {{font-size:0.8rem;font-weight:bold;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px}}
  .quote-card.pos .qlabel {{color:#00cc66}}
  .quote-card.neg .qlabel {{color:#ff4444}}
  .qtext  {{color:#bbb;font-size:0.85rem;font-style:italic;line-height:1.6}}

  @media(max-width:700px) {{
    .quotes-grid {{grid-template-columns:1fr}}
  }}
</style>
</head>
<body>

<div class="page-title">Hotel Sentiment Analysis</div>
<div class="page-sub">Top 20 hotels by review count — positive &amp; negative breakdown with real examples</div>

<div class="chart-wrap">
  <img src="data:image/png;base64,{chart_b64}" alt="Reviews per hotel chart">
</div>

{rows_html}

</body>
</html>"""

with open("output/hotel_sentiment.html","w",encoding="utf-8") as f:
    f.write(html)
print("Saved: hotel_sentiment.html")
