import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
import re, base64, warnings
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
df["lat"]       = pd.to_numeric(df["latitude"],  errors="coerce")
df["lon"]       = pd.to_numeric(df["longitude"], errors="coerce")

# ── California filter ──────────────────────────────────────────────────────────
ca = df[
    (df["province"].str.upper().str.strip().isin(["CA","CALIFORNIA"])) |
    (df["city"].str.contains(
        "Long Beach|Garden Grove|San Jose|Santa Barbara|Rohnert Park|Studio City|"
        "San Clemente|Marina|Livermore|Anaheim|Monterey|Napa|San Francisco|Gardena|"
        "Sunnyvale|Garberville|Joshua Tree|Rancho Mirage|San Bruno|Irvine|Eureka|"
        "San Diego|Morro Bay|Palm Springs",
        case=False, na=False))
].copy()

# ── Suspicion score ────────────────────────────────────────────────────────────
VAGUE    = {"great","good","bad","nice","terrible","amazing","worst","best",
            "awesome","horrible","loved","hated","perfect","recommend"}
SPECIFIC = {"room","floor","lobby","parking","breakfast","pool","shower","bed",
            "wifi","staff","neighborhood","elevator","checkout","kids","family"}

def score_review(row):
    t = row["text"]; s = 0
    wc = len(t.split())
    words = t.lower().split()
    if wc < 15 and row["rating"] in [1,5]: s += 20
    v  = sum(1 for w in words if w in VAGUE)
    sp = sum(1 for w in words if w in SPECIFIC)
    if v / (sp + 0.1) > 3: s += 15
    try:
        pol = TextBlob(t).sentiment.polarity
        if abs(pol) > 0.8: s += 15
    except: pass
    if t.count("!") >= 3: s += 10
    return min(s, 100)

print("Scoring CA reviews...")
ca["sus_score"] = ca.apply(score_review, axis=1)

user_ratings = ca.groupby("user")["rating"].nunique()
one_sided    = set(user_ratings[user_ratings == 1].index)
user_day     = ca.groupby(["user","date_only","hotel"]).size().reset_index(name="n")
multi_day    = set(user_day[user_day["n"] > 1]["user"])
for idx, row in ca.iterrows():
    if row["user"] in one_sided:  ca.at[idx,"sus_score"] = min(ca.at[idx,"sus_score"]+10,100)
    if row["user"] in multi_day:  ca.at[idx,"sus_score"] = min(ca.at[idx,"sus_score"]+15,100)

# Genuine reviews only
genuine = ca[ca["sus_score"] <= 20].copy()
print(f"CA genuine reviews: {len(genuine)}")

# ── Hotel-level data from genuine reviews ─────────────────────────────────────
hotel_master = (ca.groupby("hotel")
                .agg(
                    total_reviews   =("text","count"),
                    genuine_reviews =("sus_score", lambda x: (x<=20).sum()),
                    avg_rating      =("rating","mean"),
                    min_rating      =("rating","min"),
                    max_rating      =("rating","max"),
                    rating_variance =("rating","var"),
                    address         =("address",  lambda x: x.mode()[0] if len(x)>0 else ""),
                    city            =("city",      lambda x: x.mode()[0] if len(x)>0 else ""),
                    postalCode      =("postalCode",lambda x: x.mode()[0] if len(x)>0 else ""),
                    province        =("province",  lambda x: x.mode()[0] if len(x)>0 else ""),
                    lat             =("lat","mean"),
                    lon             =("lon","mean"),
                    first_review    =("date","min"),
                    last_review     =("date","max"),
                )
                .reset_index())

hotel_master["genuine_pct"] = hotel_master["genuine_reviews"] / hotel_master["total_reviews"] * 100
hotel_master = hotel_master[hotel_master["genuine_reviews"] >= 3].sort_values("genuine_reviews", ascending=False)

print(f"Hotels with >=3 genuine reviews: {len(hotel_master)}")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 1 — Duplicate / Similar Hotel Names
# ══════════════════════════════════════════════════════════════════════════════
print("\nChecking for similar hotel names...")
hotel_names = hotel_master["hotel"].tolist()

def name_similarity(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

# Find pairs with >70% name similarity but different addresses
similar_pairs = []
for i in range(len(hotel_names)):
    for j in range(i+1, len(hotel_names)):
        sim = name_similarity(hotel_names[i], hotel_names[j])
        if sim >= 0.70:
            row_i = hotel_master[hotel_master["hotel"]==hotel_names[i]].iloc[0]
            row_j = hotel_master[hotel_master["hotel"]==hotel_names[j]].iloc[0]
            addr_sim = name_similarity(str(row_i["address"]), str(row_j["address"]))
            similar_pairs.append({
                "hotel_a":    hotel_names[i],
                "hotel_b":    hotel_names[j],
                "name_sim":   round(sim*100,1),
                "addr_a":     row_i["address"],
                "addr_b":     row_j["address"],
                "city_a":     row_i["city"],
                "city_b":     row_j["city"],
                "addr_sim":   round(addr_sim*100,1),
                "rating_a":   round(row_i["avg_rating"],2),
                "rating_b":   round(row_j["avg_rating"],2),
                "genuine_a":  int(row_i["genuine_reviews"]),
                "genuine_b":  int(row_j["genuine_reviews"]),
            })

similar_pairs_df = pd.DataFrame(similar_pairs).sort_values("name_sim", ascending=False)
print(f"Similar name pairs found: {len(similar_pairs_df)}")
print(similar_pairs_df[["hotel_a","hotel_b","name_sim","city_a","city_b","addr_sim"]].head(20).to_string())

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 2 — Same address / different name (potential duplicates)
# ══════════════════════════════════════════════════════════════════════════════
print("\nChecking for same-address duplicates...")
addr_groups = hotel_master[hotel_master["address"] != ""].groupby("address")["hotel"].apply(list).reset_index()
addr_dupes  = addr_groups[addr_groups["hotel"].apply(len) > 1]
print(f"Same-address groups: {len(addr_dupes)}")
for _, r in addr_dupes.iterrows():
    print(f"  {r['address']}: {r['hotel']}")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 3 — Rating consistency check
# ══════════════════════════════════════════════════════════════════════════════
print("\nRating consistency flags...")
# Hotels where avg genuine rating differs a lot from overall avg
hotel_master["overall_avg"] = hotel_master.apply(
    lambda r: ca[ca["hotel"]==r["hotel"]]["rating"].mean(), axis=1)
hotel_master["rating_drift"] = (hotel_master["avg_rating"] - hotel_master["overall_avg"]).abs()

drifters = hotel_master[hotel_master["rating_drift"] > 0.5].sort_values("rating_drift", ascending=False)
print(f"Hotels with rating drift > 0.5 after removing suspicious reviews: {len(drifters)}")
print(drifters[["hotel","avg_rating","overall_avg","rating_drift","genuine_reviews","total_reviews"]].head(10).to_string())

# ══════════════════════════════════════════════════════════════════════════════
# PNG — 4-panel integrity dashboard
# ══════════════════════════════════════════════════════════════════════════════
top20 = hotel_master.head(20).copy()
top20["short"] = top20["hotel"].apply(lambda x: x[:30])

fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.patch.set_facecolor("#0a0a0a")
fig.suptitle("CA Hotels — Data Integrity & Duplication Check (Genuine Reviews Only)",
             color="white", fontsize=14, fontweight="bold", y=0.98)

# ── Panel A: Genuine vs Total reviews ─────────────────────────────────────────
ax = axes[0][0]; ax.set_facecolor("#111")
y = np.arange(len(top20))
ax.barh(y, top20["total_reviews"],   color="#333",    height=0.6, label="Suspicious")
ax.barh(y, top20["genuine_reviews"], color="#00cc66", height=0.6, label="Genuine")
ax.set_yticks(y); ax.set_yticklabels(top20["short"], color="white", fontsize=7)
ax.set_title("Genuine vs Total Reviews", color="white", fontsize=11, fontweight="bold")
ax.set_xlabel("Reviews", color="white"); ax.tick_params(colors="white")
for spine in ax.spines.values(): spine.set_edgecolor("#333")
ax.legend(facecolor="#222", edgecolor="#444", labelcolor="white", fontsize=8)
ax.invert_yaxis()

# ── Panel B: Avg rating (genuine only) ────────────────────────────────────────
ax = axes[0][1]; ax.set_facecolor("#111")
colors_r = ["#00cc66" if r>=4.5 else "#ffa94d" if r>=4.0 else "#ff8800" if r>=3.5 else "#ff4444"
            for r in top20["avg_rating"]]
ax.barh(y, top20["avg_rating"], color=colors_r, height=0.6)
ax.set_yticks(y); ax.set_yticklabels(top20["short"], color="white", fontsize=7)
ax.set_title("Avg Rating (Genuine Reviews Only)", color="white", fontsize=11, fontweight="bold")
ax.set_xlabel("Average Rating", color="white"); ax.set_xlim(0, 6)
ax.tick_params(colors="white")
for spine in ax.spines.values(): spine.set_edgecolor("#333")
for i, (_, r) in enumerate(top20.iterrows()):
    ax.text(r["avg_rating"]+0.05, i, f"★{r['avg_rating']:.2f}", va="center",
            color="white", fontsize=8)
ax.invert_yaxis()

# ── Panel C: Rating variance (consistency) ────────────────────────────────────
ax = axes[1][0]; ax.set_facecolor("#111")
var_vals   = top20["rating_variance"].fillna(0)
colors_v   = ["#ff4444" if v>2 else "#ffa94d" if v>1 else "#00cc66" for v in var_vals]
ax.barh(y, var_vals, color=colors_v, height=0.6)
ax.set_yticks(y); ax.set_yticklabels(top20["short"], color="white", fontsize=7)
ax.set_title("Rating Variance (Low=Consistent, High=Polarised)", color="white", fontsize=11, fontweight="bold")
ax.set_xlabel("Variance", color="white"); ax.tick_params(colors="white")
for spine in ax.spines.values(): spine.set_edgecolor("#333")
green_p = mpatches.Patch(color="#00cc66", label="Consistent (var<1)")
orange_p= mpatches.Patch(color="#ffa94d", label="Moderate (1-2)")
red_p   = mpatches.Patch(color="#ff4444", label="Polarised (>2)")
ax.legend(handles=[green_p,orange_p,red_p], facecolor="#222", edgecolor="#444",
          labelcolor="white", fontsize=8)
ax.invert_yaxis()

# ── Panel D: Name similarity heatmap (top 15) ─────────────────────────────────
ax = axes[1][1]; ax.set_facecolor("#111")
top15_names = hotel_names[:15]
sim_matrix  = np.zeros((len(top15_names), len(top15_names)))
for i, a in enumerate(top15_names):
    for j, b in enumerate(top15_names):
        sim_matrix[i][j] = name_similarity(a, b)
np.fill_diagonal(sim_matrix, 0)  # zero out self

import seaborn as sns
short15 = [n[:22] for n in top15_names]
sns.heatmap(sim_matrix, ax=ax, cmap="Reds", vmin=0, vmax=1,
            xticklabels=short15, yticklabels=short15,
            linewidths=0.3, linecolor="#222", annot=True, fmt=".2f",
            annot_kws={"size":6}, cbar_kws={"shrink":0.7})
ax.set_title("Hotel Name Similarity Matrix\n(red = possible duplicate)", color="white",
             fontsize=11, fontweight="bold")
plt.setp(ax.get_xticklabels(), color="white", rotation=45, ha="right", fontsize=7)
plt.setp(ax.get_yticklabels(), color="white", rotation=0, fontsize=7)
ax.figure.axes[-1].tick_params(colors="white")

plt.tight_layout(rect=[0,0,1,0.97])
plt.savefig("output/data_integrity.png", dpi=150, bbox_inches="tight", facecolor="#0a0a0a")
plt.close()
print("Saved: data_integrity.png")

# ══════════════════════════════════════════════════════════════════════════════
# HTML
# ══════════════════════════════════════════════════════════════════════════════
with open("output/data_integrity.png","rb") as f:
    chart_b64 = base64.b64encode(f.read()).decode()

def flag_color(val, thresholds, colors):
    for t, c in zip(thresholds, colors):
        if val >= t: return c
    return colors[-1]

def build_hotel_table():
    rows = ""
    for _, r in hotel_master.head(25).iterrows():
        drift    = r["rating_drift"]
        variance = r["rating_variance"] if not np.isnan(r["rating_variance"]) else 0
        drift_col   = "#ff4444" if drift > 0.5 else "#ffa94d" if drift > 0.2 else "#00cc66"
        var_col     = "#ff4444" if variance > 2 else "#ffa94d" if variance > 1 else "#00cc66"
        rating_col  = "#00cc66" if r["avg_rating"]>=4.5 else "#ffa94d" if r["avg_rating"]>=3.5 else "#ff4444"
        gen_pct_col = "#00cc66" if r["genuine_pct"]>=80 else "#ffa94d" if r["genuine_pct"]>=60 else "#ff4444"

        addr  = r["address"][:45] if r["address"] else "—"
        city  = r["city"] if r["city"] else "—"
        postal= r["postalCode"] if r["postalCode"] else "—"
        coord = f"{r['lat']:.4f}, {r['lon']:.4f}" if not np.isnan(r["lat"]) else "—"

        # Duplicate name warnings
        dup_warn = ""
        matches = similar_pairs_df[
            ((similar_pairs_df["hotel_a"]==r["hotel"]) | (similar_pairs_df["hotel_b"]==r["hotel"])) &
            (similar_pairs_df["name_sim"] >= 75)
        ]
        if len(matches) > 0:
            for _, m in matches.iterrows():
                other = m["hotel_b"] if m["hotel_a"]==r["hotel"] else m["hotel_a"]
                dup_warn += f'<div style="color:#ffd700;font-size:0.75rem;margin-top:4px">⚠️ Similar name: <em>{other[:40]}</em> ({m["name_sim"]}% match)</div>'

        addr_dup = ""
        same_addr = addr_groups[addr_groups["hotel"].apply(lambda hl: r["hotel"] in hl and len(hl)>1)]
        if len(same_addr) > 0:
            addr_dup = '<div style="color:#ff4444;font-size:0.75rem;margin-top:4px">🚨 Address shared with another hotel listing</div>'

        rows += f"""
<tr>
  <td class="hotel-cell">
    <div style="font-weight:bold;color:#fff;margin-bottom:3px">{r['hotel'][:45]}</div>
    <div style="color:#888;font-size:0.78rem">{addr} · {city} {postal}</div>
    <div style="color:#666;font-size:0.75rem">📍 {coord}</div>
    {dup_warn}{addr_dup}
  </td>
  <td style="text-align:center;color:{rating_col};font-weight:bold">★ {r['avg_rating']:.2f}</td>
  <td style="text-align:center;color:#ccc">{int(r['min_rating'])} – {int(r['max_rating'])}</td>
  <td style="text-align:center;color:{var_col};font-weight:bold">{variance:.2f}</td>
  <td style="text-align:center;color:#00cc66">{int(r['genuine_reviews'])}</td>
  <td style="text-align:center;color:#888">{int(r['total_reviews'])}</td>
  <td style="text-align:center;color:{gen_pct_col};font-weight:bold">{r['genuine_pct']:.0f}%</td>
  <td style="text-align:center;color:{drift_col};font-weight:bold">
    {"↑" if r["avg_rating"]>r["overall_avg"] else "↓"} {drift:.2f}
  </td>
</tr>"""
    return rows

def build_dupe_section():
    if len(similar_pairs_df) == 0:
        return '<div style="color:#00cc66;padding:16px">✅ No duplicate hotel names found.</div>'
    rows = ""
    for _, p in similar_pairs_df[similar_pairs_df["name_sim"] >= 70].head(20).iterrows():
        same_city = "✅ Same city" if p["city_a"].lower()==p["city_b"].lower() else "⚠️ Different city"
        verdict = "🔴 Likely same hotel, different listing" if p["name_sim"]>=90 and p["addr_sim"]>=70 \
             else "🟡 Possibly same chain / brand" if p["name_sim"]>=80 \
             else "⚪ Similar name only"
        rows += f"""
<tr>
  <td style="color:#ff8888">{p['hotel_a'][:40]}</td>
  <td style="color:#ff8888">{p['hotel_b'][:40]}</td>
  <td style="text-align:center;color:#ffd700;font-weight:bold">{p['name_sim']}%</td>
  <td style="text-align:center;color:#aaa">{p['addr_sim']}%</td>
  <td style="color:#888;font-size:0.82rem">{p['city_a']} / {p['city_b']}<br><small>{same_city}</small></td>
  <td style="text-align:center;color:#ffd700">★{p['rating_a']} / ★{p['rating_b']}</td>
  <td style="font-size:0.8rem">{verdict}</td>
</tr>"""
    return rows

def build_addr_dupes():
    if len(addr_dupes) == 0:
        return '<div style="color:#00cc66;padding:16px">✅ No shared-address conflicts found.</div>'
    rows = ""
    for _, r in addr_dupes.iterrows():
        hotels_str = " · ".join(r["hotel"][:2])
        rows += f'<div style="background:#1a1000;border:1px solid #ff8800;border-radius:8px;padding:12px;margin-bottom:10px"><div style="color:#ffd700;font-weight:bold;margin-bottom:4px">📍 {r["address"]}</div><div style="color:#ccc">{hotels_str}</div></div>'
    return rows

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CA Hotels — Data Integrity Report</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0a0a0a;color:#e0e0e0;font-family:'Segoe UI',sans-serif;padding:30px}}
  .page-title{{color:#4dabf7;font-size:1.9rem;font-weight:bold;text-transform:uppercase;
               letter-spacing:3px;text-align:center;margin-bottom:6px}}
  .page-sub  {{color:#888;text-align:center;margin-bottom:28px;font-size:0.92rem}}
  .section-title{{color:#4dabf7;font-size:1.1rem;font-weight:bold;text-transform:uppercase;
                  letter-spacing:2px;margin:30px 0 14px;border-bottom:1px solid #222;padding-bottom:8px}}
  .chart-wrap{{text-align:center;margin-bottom:30px}}
  .chart-wrap img{{max-width:100%;border-radius:12px;border:1px solid #222}}
  .stats-row{{display:flex;gap:16px;flex-wrap:wrap;justify-content:center;margin-bottom:28px}}
  .stat-box{{background:#111;border:1px solid #333;border-radius:10px;
             padding:16px 24px;text-align:center;min-width:130px}}
  .stat-box .val{{font-size:1.8rem;font-weight:bold}}
  .stat-box .lbl{{color:#888;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.5px;margin-top:4px}}
  table{{width:100%;border-collapse:collapse;font-size:0.83rem}}
  th{{background:#1a1a2a;color:#4dabf7;padding:10px 10px;text-align:left;
      font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;border-bottom:2px solid #333}}
  td{{padding:10px 10px;border-bottom:1px solid #1a1a1a;vertical-align:top}}
  tr:hover td{{background:#141414}}
  .hotel-cell{{min-width:240px}}
  .legend{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:14px;font-size:0.8rem}}
  .leg-item{{display:flex;align-items:center;gap:6px;color:#aaa}}
  .leg-dot{{width:10px;height:10px;border-radius:50%}}
  .table-wrap{{overflow-x:auto;background:#111;border:1px solid #222;border-radius:10px;padding:4px}}
</style>
</head>
<body>

<div class="page-title">📋 Data Integrity Report</div>
<div class="page-sub">Non-suspicious reviews only — cross-checking names, addresses, locations & ratings</div>

<div class="stats-row">
  <div class="stat-box"><div class="val" style="color:#00cc66">{len(genuine):,}</div><div class="lbl">Genuine Reviews</div></div>
  <div class="stat-box"><div class="val" style="color:#4dabf7">{len(hotel_master)}</div><div class="lbl">Verified Hotels</div></div>
  <div class="stat-box"><div class="val" style="color:#ffd700">{len(similar_pairs_df[similar_pairs_df['name_sim']>=70])}</div><div class="lbl">Similar Names</div></div>
  <div class="stat-box"><div class="val" style="color:#ff8800">{len(addr_dupes)}</div><div class="lbl">Shared Addresses</div></div>
  <div class="stat-box"><div class="val" style="color:#ff4444">{len(drifters)}</div><div class="lbl">Rating Drift Hotels</div></div>
</div>

<div class="chart-wrap">
  <img src="data:image/png;base64,{chart_b64}" alt="Integrity charts">
</div>

<div class="section-title">🏨 Hotel Master Table — Verified Data</div>
<div class="legend">
  <div class="leg-item"><div class="leg-dot" style="background:#00cc66"></div>Good</div>
  <div class="leg-item"><div class="leg-dot" style="background:#ffa94d"></div>Moderate</div>
  <div class="leg-item"><div class="leg-dot" style="background:#ff4444"></div>Concern</div>
  <div class="leg-item" style="color:#888">Variance: how spread out ratings are (low=consistent, high=polarised)</div>
  <div class="leg-item" style="color:#888">Drift: how much avg rating changed after removing suspicious reviews</div>
</div>
<div class="table-wrap">
<table>
  <thead><tr>
    <th>Hotel · Address · Coordinates</th>
    <th>Avg Rating</th>
    <th>Range</th>
    <th>Variance</th>
    <th>Genuine</th>
    <th>Total</th>
    <th>% Genuine</th>
    <th>Rating Drift ↕</th>
  </tr></thead>
  <tbody>{build_hotel_table()}</tbody>
</table>
</div>

<div class="section-title">🔁 Similar Hotel Name Check</div>
<div class="table-wrap">
<table>
  <thead><tr>
    <th>Hotel A</th><th>Hotel B</th>
    <th>Name Match</th><th>Address Match</th>
    <th>City</th><th>Ratings</th><th>Verdict</th>
  </tr></thead>
  <tbody>{build_dupe_sections() if False else build_dupe_section()}</tbody>
</table>
</div>

<div class="section-title">📍 Shared Address Conflicts</div>
{build_addr_dupes()}

</body>
</html>"""

# Fix typo in function call
html = html.replace("build_dupe_sections() if False else build_dupe_section()", "build_dupe_section()")

with open("output/data_integrity.html","w",encoding="utf-8") as f:
    f.write(html)
print("Saved: data_integrity.html")
