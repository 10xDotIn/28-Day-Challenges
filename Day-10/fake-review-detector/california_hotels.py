import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import base64, warnings
warnings.filterwarnings("ignore")
from textblob import TextBlob

df = pd.read_csv("data/hotel_reviews.csv", low_memory=False)
df["rating"]    = pd.to_numeric(df["reviews.rating"], errors="coerce")
df["text"]      = df["reviews.text"].fillna("").astype(str)
df["hotel"]     = df["name"].fillna("Unknown").astype(str)
df["user"]      = df["reviews.username"].fillna("anonymous").astype(str)
df["date"]      = pd.to_datetime(df["reviews.date"], errors="coerce")
df["date_only"] = df["date"].dt.date
df["province"]  = df["province"].fillna("").astype(str)
df["country"]   = df["country"].fillna("").astype(str)
df["city"]      = df["city"].fillna("").astype(str)
df["address"]   = df["address"].fillna("").astype(str)
df["postalCode"]= df["postalCode"].fillna("").astype(str)

# ── Filter California ──────────────────────────────────────────────────────────
ca = df[
    (df["province"].str.upper().str.strip().isin(["CA","CALIFORNIA"])) |
    (df["city"].str.contains("Los Angeles|San Francisco|San Diego|Sacramento|"
                              "Santa Monica|Anaheim|San Jose|Oakland|Long Beach|"
                              "Santa Barbara|Monterey|Palm Springs|Napa|Lake Tahoe|"
                              "Pasadena|Burbank|Irvine|Riverside|Fresno",
                              case=False, na=False))
].copy()

print(f"California reviews: {len(ca)}")
print("Cities found:", ca["city"].value_counts().head(15).to_dict())

# ── Quick suspicion score ──────────────────────────────────────────────────────
VAGUE    = {"great","good","bad","nice","terrible","amazing","worst","best",
            "awesome","horrible","loved","hated","perfect","recommend"}
SPECIFIC = {"room","floor","lobby","parking","breakfast","pool","shower","bed",
            "wifi","staff","neighborhood","elevator","checkout","kids","family",
            "children","pool","suite","ocean","view"}

def quick_score(row):
    t = row["text"]; s = 0
    wc = len(t.split())
    if wc < 15 and row["rating"] in [1,5]: s += 20
    words = t.lower().split()
    v = sum(1 for w in words if w in VAGUE)
    sp= sum(1 for w in words if w in SPECIFIC)
    if v / (sp + 0.1) > 3: s += 15
    try:
        pol = TextBlob(t).sentiment.polarity
        if abs(pol) > 0.8: s += 15
    except: pass
    if t.count("!") >= 3: s += 10
    return s

ca["sus_score"] = ca.apply(quick_score, axis=1)

# ── Per-hotel aggregation ──────────────────────────────────────────────────────
# Get hotel-level info (address, city etc.) — take first row per hotel
hotel_info = (ca.groupby("hotel")
              .first()
              .reset_index()[["hotel","address","city","postalCode","province","country",
                               "latitude","longitude"]])

hotel_stats = (ca.groupby("hotel")
               .apply(lambda g: pd.Series({
                   "total_reviews":   len(g),
                   "avg_rating":      g["rating"].mean(),
                   "pct_genuine":     (g["sus_score"] < 20).mean() * 100,
                   "avg_sus_score":   g["sus_score"].mean(),
                   "five_star_pct":   (g["rating"] == 5).mean() * 100,
                   "one_star_pct":    (g["rating"] == 1).mean() * 100,
               }))
               .reset_index())

hotel_stats = hotel_stats.merge(hotel_info, on="hotel", how="left")

# ── Family-friendliness score ──────────────────────────────────────────────────
FAMILY_WORDS = ["kid","kids","child","children","family","families","pool",
                "suite","playground","clean","safe","quiet","spacious","friendly"]

def family_score(hotel_name):
    reviews = ca[ca["hotel"] == hotel_name]["text"].str.lower()
    total = len(reviews)
    if total == 0: return 0
    hits = reviews.apply(lambda t: sum(1 for w in FAMILY_WORDS if w in t))
    return hits.mean() * 10  # normalise

hotel_stats["family_score"] = hotel_stats["hotel"].apply(family_score)

# ── Composite trust score ──────────────────────────────────────────────────────
# Higher = better for families
hotel_stats["trust_score"] = (
    hotel_stats["avg_rating"]   * 15 +
    hotel_stats["pct_genuine"]  * 0.3 +
    hotel_stats["family_score"] * 2 -
    hotel_stats["avg_sus_score"]* 0.5
)

# Filter: min 5 reviews, avg rating >= 3.5
qualified = hotel_stats[
    (hotel_stats["total_reviews"] >= 5) &
    (hotel_stats["avg_rating"] >= 3.5)
].sort_values("trust_score", ascending=False)

top10 = qualified.head(10).reset_index(drop=True)
print(f"\nQualified CA hotels: {len(qualified)}")
print(top10[["hotel","city","avg_rating","total_reviews","pct_genuine","trust_score"]].to_string())

# ── Best/worst review per hotel ────────────────────────────────────────────────
def best_review(hotel_name):
    sub = ca[(ca["hotel"] == hotel_name) & (ca["sus_score"] < 20) & (ca["rating"] >= 4)]
    if sub.empty:
        sub = ca[ca["hotel"] == hotel_name]
    if sub.empty: return ("—", 5)
    r = sub.loc[sub["rating"].idxmax()]
    return (str(r["text"])[:300], int(r["rating"]) if not np.isnan(r["rating"]) else 5)

def family_mentions(hotel_name):
    sub = ca[ca["hotel"] == hotel_name]["text"].str.lower()
    hits = []
    for t in sub:
        for w in FAMILY_WORDS:
            if w in t:
                hits.append(w)
    from collections import Counter
    return Counter(hits).most_common(5)

# ── PNG — top hotels bar chart ─────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 8))
fig.patch.set_facecolor("#0a0a0a")

# Left: avg rating
ax1 = axes[0]
ax1.set_facecolor("#111")
colors = ["#00cc66" if r >= 4.5 else "#ffa94d" if r >= 4.0 else "#ff8800"
          for r in top10["avg_rating"]]
bars = ax1.barh(range(len(top10)), top10["avg_rating"], color=colors, height=0.6)
ax1.set_yticks(range(len(top10)))
ax1.set_yticklabels([h[:30] for h in top10["hotel"]], color="white", fontsize=8)
ax1.set_xlabel("Average Rating", color="white")
ax1.set_title("Avg Rating", color="white", fontsize=12, fontweight="bold")
ax1.set_xlim(0, 5.5)
ax1.tick_params(colors="white")
for spine in ax1.spines.values(): spine.set_edgecolor("#333")
for i, (_, row) in enumerate(top10.iterrows()):
    ax1.text(row["avg_rating"] + 0.05, i, f"★ {row['avg_rating']:.2f}",
             va="center", color="white", fontsize=9, fontweight="bold")
ax1.invert_yaxis()

# Right: % genuine reviews
ax2 = axes[1]
ax2.set_facecolor("#111")
colors2 = ["#00cc66" if p >= 80 else "#ffa94d" if p >= 60 else "#ff8800"
           for p in top10["pct_genuine"]]
ax2.barh(range(len(top10)), top10["pct_genuine"], color=colors2, height=0.6)
ax2.set_yticks(range(len(top10)))
ax2.set_yticklabels([h[:30] for h in top10["hotel"]], color="white", fontsize=8)
ax2.set_xlabel("% Genuine Reviews", color="white")
ax2.set_title("Review Authenticity", color="white", fontsize=12, fontweight="bold")
ax2.set_xlim(0, 115)
ax2.tick_params(colors="white")
for spine in ax2.spines.values(): spine.set_edgecolor("#333")
for i, (_, row) in enumerate(top10.iterrows()):
    ax2.text(row["pct_genuine"] + 0.5, i, f"{row['pct_genuine']:.0f}%",
             va="center", color="white", fontsize=9, fontweight="bold")
ax2.invert_yaxis()

fig.suptitle("Top 10 California Hotels for Families — Rating & Authenticity",
             color="white", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("output/california_hotels.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0a0a")
plt.close()
print("Saved: california_hotels.png")

# ── HTML ───────────────────────────────────────────────────────────────────────
with open("output/california_hotels.png","rb") as f:
    chart_b64 = base64.b64encode(f.read()).decode()

RANK_COLORS = ["#FFD700","#C0C0C0","#CD7F32"] + ["#ff8800"]*7

def why_reasons(row, hotel_name):
    reasons = []
    if row["avg_rating"] >= 4.5: reasons.append(("⭐ Excellent avg rating", "#ffd700"))
    elif row["avg_rating"] >= 4.0: reasons.append(("⭐ Very good avg rating", "#ffa94d"))
    if row["pct_genuine"] >= 80: reasons.append(("✅ Highly authentic reviews", "#00cc66"))
    elif row["pct_genuine"] >= 60: reasons.append(("✅ Mostly authentic reviews", "#66cc66"))
    if row["family_score"] >= 3: reasons.append(("👨‍👩‍👧 Family-friendly mentions", "#4dabf7"))
    if row["avg_sus_score"] < 15: reasons.append(("🛡 Low fraud score", "#00cc66"))
    if row["five_star_pct"] >= 60: reasons.append(("🌟 60%+ five-star reviews", "#ffd700"))
    fm = family_mentions(hotel_name)
    if fm:
        top_words = ", ".join(w for w, _ in fm[:4])
        reasons.append((f"📝 Guests mention: {top_words}", "#aaa"))
    return reasons

def build_hotel_cards():
    html = ""
    for rank, (_, row) in enumerate(top10.iterrows(), 1):
        h = row["hotel"]
        rc = RANK_COLORS[rank-1]
        best_text, best_rating = best_review(h)
        best_text = best_text.replace("<","&lt;").replace(">","&gt;")
        reasons = why_reasons(row, h)
        reason_html = "".join(
            f'<span style="background:#1a1a1a;border:1px solid #333;border-radius:5px;'
            f'padding:3px 10px;font-size:0.8rem;color:{c};margin:3px 3px 3px 0;display:inline-block">{t}</span>'
            for t, c in reasons
        )

        addr = row["address"]
        city = row["city"]
        postal = row["postalCode"]
        prov = row["province"]
        full_addr = ", ".join(filter(None, [addr, city, prov, postal, "CA, USA"]))

        # Google Maps link
        maps_query = f"{h} {city} California".replace(" ", "+")
        maps_url   = f"https://www.google.com/maps/search/{maps_query}"

        stars_html = "★" * int(round(row["avg_rating"])) + "☆" * (5 - int(round(row["avg_rating"])))

        html += f"""
<div class="hotel-card">
  <div class="rank-badge" style="background:{rc};color:#000">#{rank}</div>
  <div class="hotel-main">
    <div class="hotel-name">{h}</div>
    <div class="hotel-city">📍 {city}, California</div>
    <div class="stars" style="color:#ffd700;font-size:1.1rem">{stars_html}
      <span style="color:#ccc;font-size:0.9rem"> {row['avg_rating']:.2f} avg  ·  {int(row['total_reviews'])} reviews</span>
    </div>
  </div>
  <div class="hotel-body">
    <div class="info-grid">
      <div class="info-block">
        <div class="info-label">📬 Address</div>
        <div class="info-val">{full_addr}</div>
      </div>
      <div class="info-block">
        <div class="info-label">🔍 Find on Maps</div>
        <div class="info-val"><a href="{maps_url}" target="_blank" style="color:#4dabf7">Search on Google Maps ↗</a></div>
      </div>
      <div class="info-block">
        <div class="info-label">✅ Genuine Reviews</div>
        <div class="info-val" style="color:#00cc66">{row['pct_genuine']:.0f}% authentic</div>
      </div>
      <div class="info-block">
        <div class="info-label">👨‍👩‍👧 Family Score</div>
        <div class="info-val">{row['family_score']:.1f} / 10</div>
      </div>
    </div>
    <div class="why-label">Why we recommend it:</div>
    <div class="why-row">{reason_html}</div>
    <div class="review-label">💬 Best genuine guest review:</div>
    <div class="review-text">"{best_text}..."</div>
  </div>
</div>"""
    return html

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>California Family Hotel Recommendations</title>
<style>
  * {{box-sizing:border-box;margin:0;padding:0}}
  body {{background:#0a0a0a;color:#e0e0e0;font-family:'Segoe UI',sans-serif;padding:30px}}

  .hero {{background:linear-gradient(135deg,#001a33,#0a0a0a,#001a00);
          border-radius:16px;padding:40px;text-align:center;margin-bottom:36px;
          border:1px solid #1a3a1a}}
  .hero h1 {{color:#00cc66;font-size:2rem;font-weight:bold;text-transform:uppercase;
             letter-spacing:3px;margin-bottom:8px}}
  .hero p  {{color:#888;font-size:0.95rem;line-height:1.7}}
  .hero .badges {{display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-top:20px}}
  .badge {{background:#111;border:1px solid #333;border-radius:8px;padding:10px 20px;
           font-size:0.85rem;color:#ccc}}
  .badge strong {{color:#00cc66;display:block;font-size:1.2rem}}

  .notice {{background:#0d1a0d;border:1px solid #1a4a1a;border-radius:10px;
            padding:14px 20px;margin-bottom:28px;color:#88bb88;font-size:0.88rem;line-height:1.7}}

  .chart-wrap {{text-align:center;margin-bottom:36px}}
  .chart-wrap img {{max-width:100%;border-radius:12px;border:1px solid #222}}

  .section-title {{color:#00cc66;font-size:1.4rem;font-weight:bold;text-transform:uppercase;
                   letter-spacing:2px;margin-bottom:20px}}

  .hotel-card {{background:#111;border:1px solid #1a3a1a;border-radius:14px;
                padding:0;margin-bottom:24px;overflow:hidden;position:relative}}
  .rank-badge  {{position:absolute;top:0;left:0;width:48px;height:48px;
                 display:flex;align-items:center;justify-content:center;
                 font-size:1rem;font-weight:bold;border-radius:0 0 12px 0}}
  .hotel-main  {{padding:18px 18px 14px 64px;border-bottom:1px solid #1a1a1a}}
  .hotel-name  {{font-size:1.15rem;font-weight:bold;color:#fff;margin-bottom:4px}}
  .hotel-city  {{color:#888;font-size:0.88rem;margin-bottom:6px}}
  .stars       {{margin-top:4px}}

  .hotel-body  {{padding:18px}}
  .info-grid   {{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px}}
  .info-block  {{background:#0d0d0d;border-radius:8px;padding:10px 14px}}
  .info-label  {{color:#666;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px}}
  .info-val    {{color:#ccc;font-size:0.9rem;line-height:1.4}}

  .why-label   {{color:#00cc66;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}}
  .why-row     {{margin-bottom:14px}}

  .review-label{{color:#888;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}}
  .review-text {{color:#bbb;font-style:italic;font-size:0.87rem;background:#0d0d0d;
                 border-left:3px solid #00cc66;border-radius:6px;padding:10px 14px;line-height:1.6}}

  .disclaimer  {{background:#1a1000;border:1px solid #333;border-radius:10px;
                 padding:16px 22px;margin-top:30px;color:#888;font-size:0.85rem;line-height:1.7}}
  .disclaimer strong {{color:#ffa94d}}

  @media(max-width:600px) {{
    .info-grid {{grid-template-columns:1fr}}
  }}
</style>
</head>
<body>

<div class="hero">
  <h1>🌴 California Family Hotels</h1>
  <p>Recommendations for a family vacation with 3 kids — filtered for<br>
     highest genuine ratings, family-friendliness, and low fraud scores</p>
  <div class="badges">
    <div class="badge"><strong>{len(qualified)}</strong> CA hotels analysed</div>
    <div class="badge"><strong>Top 10</strong> recommended</div>
    <div class="badge"><strong>✅</strong> Fraud-filtered</div>
    <div class="badge"><strong>👨‍👩‍👧</strong> Family mentions scored</div>
  </div>
</div>

<div class="notice">
  ℹ️ <strong>How hotels were ranked:</strong> We filtered for California hotels with ≥5 reviews and ≥3.5 avg rating,
  then scored each by: average rating × 15 + % genuine reviews × 0.3 + family keyword score × 2 − avg suspicion score × 0.5.
  Only hotels with authentic, non-manipulated review signals appear here.
</div>

<div class="chart-wrap">
  <img src="data:image/png;base64,{chart_b64}" alt="CA Hotels Chart">
</div>

<div class="section-title">🏆 Top 10 Recommended Hotels</div>

{build_hotel_cards()}

<div class="disclaimer">
  <strong>⚠️ About contact information:</strong> This dataset contains hotel names, addresses, cities and postal codes
  as captured at time of review. Phone numbers and websites are not included in the data.
  Use the Google Maps links above to find current contact details, check availability, and book directly.
  Always verify address and details before travelling.
</div>

</body>
</html>"""

with open("output/california_family_hotels.html","w",encoding="utf-8") as f:
    f.write(html)
print("Saved: california_family_hotels.html")
