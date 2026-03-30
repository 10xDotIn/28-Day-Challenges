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
df["city"]      = df["city"].fillna("").astype(str)
df["address"]   = df["address"].fillna("").astype(str)
df["postalCode"]= df["postalCode"].fillna("").astype(str)
df["userCity"]  = df["reviews.userCity"].fillna("Unknown").astype(str)

# ── Filter California ──────────────────────────────────────────────────────────
ca = df[
    (df["province"].str.upper().str.strip().isin(["CA","CALIFORNIA"])) |
    (df["city"].str.contains("Los Angeles|San Francisco|San Diego|Sacramento|"
                              "Santa Monica|Anaheim|San Jose|Oakland|Long Beach|"
                              "Santa Barbara|Monterey|Palm Springs|Napa|Lake Tahoe|"
                              "Pasadena|Burbank|Irvine|Riverside|Fresno|Eureka|"
                              "Rohnert Park|Studio City|San Clemente|Marina|Livermore|"
                              "Garden Grove|Gardena|Sunnyvale|Garberville|Joshua Tree|"
                              "Rancho Mirage",
                              case=False, na=False))
].copy()

# ── Score every review ─────────────────────────────────────────────────────────
VAGUE    = {"great","good","bad","nice","terrible","amazing","worst","best",
            "awesome","horrible","loved","hated","perfect","recommend"}
SPECIFIC = {"room","floor","lobby","parking","breakfast","pool","shower","bed",
            "wifi","staff","neighborhood","elevator","checkout","kids","family",
            "children","suite","ocean","view"}

def score_review(row):
    t = row["text"]; s = 0
    wc = len(t.split())
    words = t.lower().split()
    if wc < 15 and row["rating"] in [1, 5]: s += 20
    v  = sum(1 for w in words if w in VAGUE)
    sp = sum(1 for w in words if w in SPECIFIC)
    if v / (sp + 0.1) > 3: s += 15
    try:
        pol = TextBlob(t).sentiment.polarity
        if abs(pol) > 0.8: s += 15
    except: pass
    if t.count("!") >= 3: s += 10
    return min(s, 100)

print("Scoring reviews...")
ca["rev_score"] = ca.apply(score_review, axis=1)

# Reviewer-level signals
user_ratings = ca.groupby("user")["rating"].nunique()
one_sided    = set(user_ratings[user_ratings == 1].index)

user_day = ca.groupby(["user","date_only","hotel"]).size().reset_index(name="n")
multi_day= set(user_day[user_day["n"] > 1]["user"])

for idx, row in ca.iterrows():
    if row["user"] in one_sided:  ca.at[idx,"rev_score"] = min(ca.at[idx,"rev_score"] + 10, 100)
    if row["user"] in multi_day:  ca.at[idx,"rev_score"] = min(ca.at[idx,"rev_score"] + 15, 100)

# ── Separate genuine vs suspicious reviews ─────────────────────────────────────
genuine    = ca[ca["rev_score"] <= 20].copy()
suspicious = ca[ca["rev_score"] >  20].copy()

print(f"CA total reviews:      {len(ca)}")
print(f"CA genuine reviews:    {len(genuine)} ({len(genuine)/len(ca)*100:.1f}%)")
print(f"CA suspicious reviews: {len(suspicious)} ({len(suspicious)/len(ca)*100:.1f}%)")

# ── Top 10 CA hotels using ONLY genuine reviews ────────────────────────────────
FAMILY_WORDS = ["kid","kids","child","children","family","families","pool",
                "suite","playground","clean","safe","quiet","spacious","friendly"]

def family_score(hotel_name, data):
    reviews = data[data["hotel"] == hotel_name]["text"].str.lower()
    if len(reviews) == 0: return 0
    hits = reviews.apply(lambda t: sum(1 for w in FAMILY_WORDS if w in t))
    return hits.mean() * 10

hotel_info = (ca.groupby("hotel").first().reset_index()
              [["hotel","address","city","postalCode","province"]])

# Stats from genuine reviews only
genuine_stats = (genuine.groupby("hotel")
                 .apply(lambda g: pd.Series({
                     "genuine_reviews": len(g),
                     "avg_rating":      g["rating"].mean(),
                     "five_star_pct":   (g["rating"] == 5).mean() * 100,
                 }))
                 .reset_index())

# Suspicious count per hotel
sus_count = (suspicious.groupby("hotel")
             .agg(suspicious_reviews=("rev_score","count"),
                  avg_sus_score=("rev_score","mean"))
             .reset_index())

hotel_stats = genuine_stats.merge(sus_count, on="hotel", how="left").fillna(0)
hotel_stats = hotel_stats.merge(hotel_info, on="hotel", how="left")
hotel_stats["family_score"] = hotel_stats["hotel"].apply(
    lambda h: family_score(h, genuine))
hotel_stats["trust_score"]  = (
    hotel_stats["avg_rating"]       * 15 +
    hotel_stats["genuine_reviews"]  * 0.5 +
    hotel_stats["family_score"]     * 2   -
    hotel_stats["avg_sus_score"]    * 0.3
)

qualified = hotel_stats[
    (hotel_stats["genuine_reviews"] >= 3) &
    (hotel_stats["avg_rating"] >= 3.5)
].sort_values("trust_score", ascending=False)

top10 = qualified.head(10).reset_index(drop=True)
print(f"\nTop 10 (genuine-only):")
print(top10[["hotel","city","avg_rating","genuine_reviews","suspicious_reviews"]].to_string())

# ── Suspicious reviewers who targeted these hotels ─────────────────────────────
top10_hotels = set(top10["hotel"])
sus_in_top10 = suspicious[suspicious["hotel"].isin(top10_hotels)].copy()

sus_profiles = (sus_in_top10.groupby("user")
                .apply(lambda g: pd.Series({
                    "fake_reviews_here": len(g),
                    "hotels_targeted":   g["hotel"].unique().tolist(),
                    "ratings_used":      sorted(g["rating"].dropna().unique().tolist()),
                    "avg_sus_score":     g["rev_score"].mean(),
                    "max_sus_score":     g["rev_score"].max(),
                    "user_city":         g["userCity"].mode()[0] if len(g)>0 else "Unknown",
                    "sample_review":     str(g.iloc[0]["text"])[:200],
                    "sample_rating":     g.iloc[0]["rating"],
                }))
                .reset_index()
                .sort_values("avg_sus_score", ascending=False))

print(f"\nSuspicious reviewers in top-10 hotels: {len(sus_profiles)}")
print(sus_profiles[["user","fake_reviews_here","avg_sus_score","user_city"]].head(15).to_string())

# ── PNG ────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.patch.set_facecolor("#0a0a0a")

# Left — genuine vs suspicious per hotel
ax1 = axes[0]
ax1.set_facecolor("#111")
labels = [h[:28] for h in top10["hotel"]]
y = np.arange(len(top10))
ax1.barh(y, top10["genuine_reviews"],    color="#00cc66", height=0.55, label="Genuine")
ax1.barh(y, top10["suspicious_reviews"], left=top10["genuine_reviews"],
         color="#ff4444", height=0.55, label="Suspicious (filtered out)")
ax1.set_yticks(y); ax1.set_yticklabels(labels, color="white", fontsize=8)
ax1.set_xlabel("Review Count", color="white")
ax1.set_title("Genuine vs Suspicious Reviews\n(per recommended hotel)",
              color="white", fontsize=11, fontweight="bold")
ax1.tick_params(colors="white")
for spine in ax1.spines.values(): spine.set_edgecolor("#333")
ax1.legend(facecolor="#222", edgecolor="#444", labelcolor="white", fontsize=9)
ax1.invert_yaxis()

# Right — top suspicious reviewers bar
ax2 = axes[1]
ax2.set_facecolor("#111")
top_sus = sus_profiles.head(12)
colors  = ["#cc0000" if s >= 60 else "#ff8800" for s in top_sus["avg_sus_score"]]
ax2.barh(range(len(top_sus)), top_sus["avg_sus_score"], color=colors, height=0.6)
ax2.set_yticks(range(len(top_sus)))
ax2.set_yticklabels([u[:30] for u in top_sus["user"]], color="white", fontsize=8)
ax2.set_xlabel("Avg Suspicion Score", color="white")
ax2.set_title("Most Suspicious Reviewers\nTargeting These Hotels",
              color="white", fontsize=11, fontweight="bold")
ax2.set_xlim(0, 115)
ax2.tick_params(colors="white")
for spine in ax2.spines.values(): spine.set_edgecolor("#333")
for i, (_, r) in enumerate(top_sus.iterrows()):
    ax2.text(r["avg_sus_score"]+1, i,
             f"{r['fake_reviews_here']} review(s) | {r['user_city']}",
             va="center", color="#ccc", fontsize=7.5)
ax2.invert_yaxis()

fig.suptitle("California Hotels — Filtered: Suspicious Reviews Removed",
             color="white", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("output/ca_filtered_chart.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0a0a")
plt.close()
print("Saved: ca_filtered_chart.png")

# ── HTML ───────────────────────────────────────────────────────────────────────
with open("output/ca_filtered_chart.png","rb") as f:
    chart_b64 = base64.b64encode(f.read()).decode()

def score_color(s):
    if s <= 20:  return "#00cc66"
    if s <= 40:  return "#cccc00"
    if s <= 60:  return "#ff8800"
    if s <= 80:  return "#ff4444"
    return "#cc0000"

def best_genuine_review(hotel_name):
    sub = genuine[(genuine["hotel"] == hotel_name) & (genuine["rating"] >= 4)]
    if sub.empty: sub = genuine[genuine["hotel"] == hotel_name]
    if sub.empty: return ("—", 0)
    r = sub.loc[sub["rating"].idxmax()]
    return (str(r["text"])[:300].replace("<","&lt;").replace(">","&gt;"),
            int(r["rating"]) if not np.isnan(r["rating"]) else 0)

RANK_COLORS = ["#FFD700","#C0C0C0","#CD7F32"] + ["#ff8800"]*7

def build_hotel_cards():
    html = ""
    for rank, (_, row) in enumerate(top10.iterrows(), 1):
        h      = row["hotel"]
        rc     = RANK_COLORS[rank-1]
        bt, br = best_genuine_review(h)
        sus_ct = int(row["suspicious_reviews"])
        gen_ct = int(row["genuine_reviews"])
        total  = gen_ct + sus_ct
        pct_clean = gen_ct / total * 100 if total else 0

        maps_q   = f"{h} {row['city']} California".replace(" ","+")
        maps_url = f"https://www.google.com/maps/search/{maps_q}"
        full_addr= ", ".join(filter(None,[row["address"], row["city"],
                                          row["province"], row["postalCode"], "CA"]))
        stars    = "★" * int(round(row["avg_rating"])) + "☆" * (5 - int(round(row["avg_rating"])))

        # Suspicious reviewers for this hotel
        sus_here = sus_profiles[sus_profiles["hotels_targeted"].apply(lambda hl: h in hl)]
        sus_rows = ""
        for _, sr in sus_here.head(5).iterrows():
            sc2 = sr["avg_sus_score"]
            col = score_color(sc2)
            txt = str(sr["sample_review"])[:150].replace("<","&lt;").replace(">","&gt;")
            ratings_str = ", ".join(str(int(r)) for r in sr["ratings_used"]
                                    if not (isinstance(r, float) and np.isnan(r)))
            sus_rows += f"""
<div class="sus-row">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
    <span style="color:#ff8888;font-weight:bold">👤 {sr['user']}</span>
    <span style="background:{col};color:#fff;border-radius:4px;padding:1px 8px;font-size:0.75rem;font-weight:bold">{sc2:.0f}/100</span>
    <span style="color:#888;font-size:0.78rem">📍 {sr['user_city']}  ·  gave ★{ratings_str}</span>
  </div>
  <div style="color:#777;font-size:0.82rem;font-style:italic">"{txt}..."</div>
</div>"""

        if not sus_rows:
            sus_rows = '<div style="color:#00cc66;font-size:0.85rem">✅ No suspicious reviewers found for this hotel.</div>'

        html += f"""
<div class="hotel-card">
  <div class="rank-badge" style="background:{rc};color:#000">#{rank}</div>
  <div class="hotel-main">
    <div class="hotel-name">{h}</div>
    <div class="hotel-city">📍 {row['city']}, California</div>
    <div class="stars" style="color:#ffd700">{stars}
      <span style="color:#ccc;font-size:0.88rem"> {row['avg_rating']:.2f} avg (from genuine reviews only)</span>
    </div>
  </div>
  <div class="hotel-body">
    <div class="info-grid">
      <div class="info-block">
        <div class="info-label">📬 Address</div>
        <div class="info-val">{full_addr}</div>
      </div>
      <div class="info-block">
        <div class="info-label">🗺 Maps</div>
        <div class="info-val"><a href="{maps_url}" target="_blank" style="color:#4dabf7">Search on Google Maps ↗</a></div>
      </div>
      <div class="info-block">
        <div class="info-label">✅ Genuine Reviews</div>
        <div class="info-val" style="color:#00cc66">{gen_ct} genuine  ({pct_clean:.0f}% of total)</div>
      </div>
      <div class="info-block">
        <div class="info-label">🚫 Filtered Out</div>
        <div class="info-val" style="color:#ff4444">{sus_ct} suspicious reviews removed</div>
      </div>
    </div>

    <div class="review-label">💬 Best genuine guest review:</div>
    <div class="review-text">"{bt}..."</div>

    <div class="sus-label">🚨 Suspicious reviewers caught here ({len(sus_here)}):</div>
    <div class="sus-block">{sus_rows}</div>
  </div>
</div>"""
    return html

# Summary stats for hero
total_sus_removed = int(suspicious[suspicious["hotel"].isin(top10_hotels)].shape[0])
total_gen_kept    = int(genuine[genuine["hotel"].isin(top10_hotels)].shape[0])
unique_sus_users  = len(sus_profiles)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CA Hotels — Suspicious Reviews Filtered</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0a0a0a;color:#e0e0e0;font-family:'Segoe UI',sans-serif;padding:30px}}

  .hero{{background:linear-gradient(135deg,#001a00,#0a0a0a,#1a0000);border-radius:16px;
         padding:40px;text-align:center;margin-bottom:30px;border:1px solid #1a3a1a}}
  .hero h1{{color:#00cc66;font-size:2rem;font-weight:bold;text-transform:uppercase;
            letter-spacing:3px;margin-bottom:8px}}
  .hero p{{color:#888;font-size:0.92rem}}
  .badges{{display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-top:20px}}
  .badge{{background:#111;border:1px solid #333;border-radius:8px;padding:10px 20px;font-size:0.85rem;color:#ccc}}
  .badge strong{{display:block;font-size:1.3rem}}
  .green{{color:#00cc66}} .red{{color:#ff4444}} .orange{{color:#ff8800}}

  .chart-wrap{{text-align:center;margin-bottom:30px}}
  .chart-wrap img{{max-width:100%;border-radius:12px;border:1px solid #222}}

  .section-title{{color:#00cc66;font-size:1.3rem;font-weight:bold;text-transform:uppercase;
                  letter-spacing:2px;margin-bottom:18px}}

  .hotel-card{{background:#111;border:1px solid #1a3a1a;border-radius:14px;
               margin-bottom:24px;overflow:hidden;position:relative}}
  .rank-badge{{position:absolute;top:0;left:0;width:46px;height:46px;
               display:flex;align-items:center;justify-content:center;
               font-size:0.95rem;font-weight:bold;border-radius:0 0 10px 0}}
  .hotel-main{{padding:16px 16px 12px 58px;border-bottom:1px solid #1a1a1a}}
  .hotel-name{{font-size:1.1rem;font-weight:bold;color:#fff;margin-bottom:3px}}
  .hotel-city{{color:#888;font-size:0.85rem;margin-bottom:5px}}
  .stars{{margin-top:3px}}

  .hotel-body{{padding:16px}}
  .info-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px}}
  .info-block{{background:#0d0d0d;border-radius:8px;padding:10px 12px}}
  .info-label{{color:#555;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:3px}}
  .info-val{{color:#ccc;font-size:0.88rem;line-height:1.4}}

  .review-label{{color:#00cc66;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:5px}}
  .review-text{{color:#bbb;font-style:italic;font-size:0.86rem;background:#0d0d0d;
                border-left:3px solid #00cc66;border-radius:6px;padding:10px;margin-bottom:14px;line-height:1.6}}

  .sus-label{{color:#ff4444;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}}
  .sus-block{{background:#0d0d0d;border-radius:8px;padding:12px;border-left:3px solid #ff4444}}
  .sus-row{{border-bottom:1px solid #1a1a1a;padding-bottom:10px;margin-bottom:10px}}
  .sus-row:last-child{{border-bottom:none;margin-bottom:0;padding-bottom:0}}

  @media(max-width:600px){{.info-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>

<div class="hero">
  <h1>🔍 Filtered California Hotels</h1>
  <p>Suspicious reviews have been removed — rankings based on <strong>genuine reviews only</strong></p>
  <div class="badges">
    <div class="badge"><strong class="green">{total_gen_kept}</strong>Genuine reviews kept</div>
    <div class="badge"><strong class="red">{total_sus_removed}</strong>Suspicious removed</div>
    <div class="badge"><strong class="orange">{unique_sus_users}</strong>Suspect accounts caught</div>
    <div class="badge"><strong class="green">Top 10</strong>Trusted hotels</div>
  </div>
</div>

<div class="chart-wrap">
  <img src="data:image/png;base64,{chart_b64}" alt="Filtered chart">
</div>

<div class="section-title">🏆 Top 10 — Suspicious Reviews Stripped Out</div>

{build_hotel_cards()}

</body>
</html>"""

with open("output/ca_hotels_filtered.html","w",encoding="utf-8") as f:
    f.write(html)
print("Saved: ca_hotels_filtered.html")
