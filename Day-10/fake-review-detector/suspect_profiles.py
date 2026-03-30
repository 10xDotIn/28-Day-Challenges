import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import base64, warnings
warnings.filterwarnings("ignore")
from textblob import TextBlob

# ── Load & score (lightweight re-score) ───────────────────────────────────────
df = pd.read_csv("data/hotel_reviews.csv", low_memory=False)
df["rating"]    = pd.to_numeric(df["reviews.rating"], errors="coerce")
df["text"]      = df["reviews.text"].fillna("").astype(str)
df["hotel"]     = df["name"].fillna("Unknown").astype(str)
df["user"]      = df["reviews.username"].fillna("anonymous").astype(str)
df["date"]      = pd.to_datetime(df["reviews.date"], errors="coerce")
df["date_only"] = df["date"].dt.date
df["userCity"]  = df["reviews.userCity"].fillna("Unknown").astype(str)
df["userProv"]  = df["reviews.userProvince"].fillna("").astype(str)

VAGUE    = {"great","good","bad","nice","terrible","amazing","worst","best",
            "awesome","horrible","loved","hated","perfect","recommend"}
SPECIFIC = {"room","floor","lobby","parking","breakfast","pool","shower","bed",
            "wifi","staff","neighborhood","elevator","checkout"}

def wc(t): return len(t.split())
def vague_ratio(t):
    words = t.lower().split()
    v = sum(1 for w in words if w in VAGUE)
    s = sum(1 for w in words if w in SPECIFIC)
    return v / (s + 0.1)

df["wc"]   = df["text"].apply(wc)
df["vr"]   = df["text"].apply(vague_ratio)
df["exc"]  = df["text"].apply(lambda t: t.count("!"))
df["pol"]  = df["text"].apply(lambda t: TextBlob(t).sentiment.polarity)

# Quick suspicion score per review
def quick_score(row):
    s = 0
    if row["wc"] < 15 and row["rating"] in [1, 5]: s += 20
    if row["vr"] > 3: s += 15
    if abs(row["pol"]) > 0.8: s += 15
    if row["exc"] >= 3: s += 10
    return s

df["score"] = df.apply(quick_score, axis=1)

# Reviewer-level signals
user_ratings  = df.groupby("user")["rating"].nunique()
one_sided     = set(user_ratings[user_ratings == 1].index)

user_day_hotel = df.groupby(["user","date_only","hotel"]).size().reset_index(name="n")
multi_day      = set(user_day_hotel[user_day_hotel["n"] > 1]["user"])

for idx, row in df.iterrows():
    if row["user"] in one_sided:  df.at[idx,"score"] += 10
    if row["user"] in multi_day:  df.at[idx,"score"] += 15

df["score"] = df["score"].clip(0, 100)

# ── Aggregate by user ──────────────────────────────────────────────────────────
user_stats = (df.groupby("user")
              .apply(lambda g: pd.Series({
                  "total_reviews":    len(g),
                  "fake_reviews":     (g["score"] > 50).sum(),
                  "avg_score":        g["score"].mean(),
                  "max_score":        g["score"].max(),
                  "ratings_given":    sorted(g["rating"].dropna().unique().tolist()),
                  "hotels_reviewed":  g["hotel"].nunique(),
                  "user_city":        g["userCity"].mode()[0] if len(g) > 0 else "Unknown",
                  "user_province":    g["userProv"].mode()[0] if len(g) > 0 else "",
                  "date_range":       f"{g['date'].min().date()} → {g['date'].max().date()}"
                                      if g["date"].notna().any() else "Unknown",
                  "one_sided":        g["user"].iloc[0] in one_sided,
                  "multi_same_day":   g["user"].iloc[0] in multi_day,
              }))
              .reset_index())

# Only keep users with at least 1 fake review
suspects = user_stats[user_stats["fake_reviews"] >= 1].sort_values("avg_score", ascending=False)
print(f"Suspicious accounts found: {len(suspects)}")
print(suspects[["user","total_reviews","fake_reviews","avg_score","user_city"]].head(20).to_string())

top_suspects = suspects.head(30)

# ══════════════════════════════════════════════════════════════════════════════
# PNG — top suspect accounts bar chart
# ══════════════════════════════════════════════════════════════════════════════
top15 = suspects.head(15)
fig, ax = plt.subplots(figsize=(14, 9))
fig.patch.set_facecolor("#0a0a0a")
ax.set_facecolor("#111")

colors = ["#cc0000" if r else "#ff8800"
          for r in top15["one_sided"]]

bars = ax.barh(range(len(top15)), top15["avg_score"], color=colors, height=0.6)
ax.set_yticks(range(len(top15)))
ax.set_yticklabels([u[:35] for u in top15["user"]], color="white", fontsize=9)
ax.set_xlabel("Average Suspicion Score", color="white")
ax.set_title("Top 15 Most Suspicious Reviewer Accounts",
             color="white", fontsize=14, fontweight="bold", pad=14)
ax.tick_params(colors="white")
for spine in ax.spines.values():
    spine.set_edgecolor("#333")

for i, (_, row) in enumerate(top15.iterrows()):
    ax.text(row["avg_score"] + 0.5, i,
            f"{row['fake_reviews']} fake / {row['total_reviews']} total  |  {row['user_city']}",
            va="center", color="#ccc", fontsize=8)

red_patch    = mpatches.Patch(color="#cc0000", label="One-sided rater (only 1★ or 5★)")
orange_patch = mpatches.Patch(color="#ff8800", label="Multi-signal suspicious")
ax.legend(handles=[red_patch, orange_patch],
          facecolor="#222", edgecolor="#444", labelcolor="white")
ax.invert_yaxis()
ax.set_xlim(0, 110)
plt.tight_layout()
plt.savefig("output/suspect_accounts.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0a0a")
plt.close()
print("Saved: suspect_accounts.png")

# ══════════════════════════════════════════════════════════════════════════════
# HTML — suspect_profiles.html
# ══════════════════════════════════════════════════════════════════════════════
with open("output/suspect_accounts.png","rb") as f:
    chart_b64 = base64.b64encode(f.read()).decode()

def score_color(s):
    if s <= 20:  return "#00cc66"
    if s <= 40:  return "#cccc00"
    if s <= 60:  return "#ff8800"
    if s <= 80:  return "#ff4444"
    return "#cc0000"

def build_cards():
    html = ""
    for _, row in top_suspects.iterrows():
        sc = row["avg_score"]
        col = score_color(sc)
        flags = []
        if row["one_sided"]:       flags.append(("ONE-SIDED RATER","#ff4444"))
        if row["multi_same_day"]:  flags.append(("SAME-DAY MULTI","#ff8800"))
        if row["fake_reviews"] >= 3: flags.append(("REPEAT OFFENDER","#cc00cc"))
        badge_html = "".join(
            f'<span style="background:{c};color:#fff;padding:2px 8px;border-radius:4px;'
            f'font-size:0.72rem;font-weight:bold;margin-right:5px">{t}</span>'
            for t, c in flags
        )
        ratings_str = ", ".join(str(int(r)) for r in row["ratings_given"] if not (isinstance(r, float) and np.isnan(r)))

        # Sample fake review text from this user
        sample = df[(df["user"] == row["user"]) & (df["score"] > 50)]
        if not sample.empty:
            sample_text = str(sample.iloc[0]["text"])[:220].replace("<","&lt;").replace(">","&gt;")
            sample_hotel = str(sample.iloc[0]["hotel"])[:50]
        else:
            sample_text = "—"
            sample_hotel = "—"

        location = row["user_city"]
        if row["user_province"] and row["user_province"] != "nan":
            location += f", {row['user_province']}"

        html += f"""
<div class="profile-card">
  <div class="card-header" style="border-left:4px solid {col}">
    <div>
      <div class="username">👤 {row['user']}</div>
      <div class="location">📍 {location}</div>
    </div>
    <div class="score-circle" style="background:{col}">{sc:.0f}<br><small>score</small></div>
  </div>
  <div class="flags">{badge_html}</div>
  <div class="stats-row">
    <div class="stat-box"><div class="sval">{int(row['total_reviews'])}</div><div class="slbl">Total Reviews</div></div>
    <div class="stat-box"><div class="sval" style="color:#ff4444">{int(row['fake_reviews'])}</div><div class="slbl">Fake Reviews</div></div>
    <div class="stat-box"><div class="sval">{int(row['hotels_reviewed'])}</div><div class="slbl">Hotels</div></div>
    <div class="stat-box"><div class="sval">{ratings_str or 'N/A'}</div><div class="slbl">Ratings Given</div></div>
  </div>
  <div class="date-range">📅 Active: {row['date_range']}</div>
  <div class="sample-label">Sample suspicious review — {sample_hotel}</div>
  <div class="sample-text">"{sample_text}..."</div>

  <div class="data-box">
    <div class="data-title">📋 Available Data Fields</div>
    <div class="data-grid">
      <div class="data-item avail">✅ Username: <strong>{row['user']}</strong></div>
      <div class="data-item avail">✅ Location: <strong>{location}</strong></div>
      <div class="data-item avail">✅ Activity: <strong>{row['date_range']}</strong></div>
      <div class="data-item avail">✅ Hotels reviewed: <strong>{int(row['hotels_reviewed'])}</strong></div>
      <div class="data-item avail">✅ Ratings pattern: <strong>{ratings_str or 'N/A'}</strong></div>
      <div class="data-item missing">❌ Email address: <strong>Not in dataset</strong></div>
      <div class="data-item missing">❌ Phone number: <strong>Not in dataset</strong></div>
      <div class="data-item missing">❌ Real name: <strong>Not in dataset</strong></div>
      <div class="data-item missing">❌ IP address: <strong>Not in dataset</strong></div>
      <div class="data-item missing">❌ Account ID: <strong>Not in dataset</strong></div>
    </div>
  </div>
</div>"""
    return html

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Suspect Reviewer Profiles</title>
<style>
  * {{box-sizing:border-box;margin:0;padding:0}}
  body {{background:#0a0a0a;color:#e0e0e0;font-family:'Segoe UI',sans-serif;padding:30px}}

  .page-title {{color:#ff4444;font-size:2rem;font-weight:bold;text-transform:uppercase;
               letter-spacing:3px;text-align:center;margin-bottom:6px}}
  .page-sub   {{color:#888;text-align:center;margin-bottom:10px;font-size:0.95rem}}

  .limit-box {{background:#1a1000;border:1px solid #ff8800;border-radius:10px;
               padding:18px 24px;margin:0 auto 30px;max-width:860px;color:#ffa94d;font-size:0.93rem;line-height:1.7}}
  .limit-box strong {{color:#ffd700}}
  .limit-box h3 {{color:#ff8800;margin-bottom:8px;font-size:1rem}}

  .chart-wrap {{text-align:center;margin-bottom:36px}}
  .chart-wrap img {{max-width:100%;border-radius:12px;border:1px solid #222}}

  .profile-card {{background:#111;border:1px solid #222;border-radius:12px;
                  padding:20px;margin-bottom:24px;max-width:900px;margin-left:auto;margin-right:auto}}

  .card-header {{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px}}
  .username    {{font-size:1.1rem;font-weight:bold;color:#ff8888;margin-bottom:4px}}
  .location    {{color:#888;font-size:0.88rem}}
  .score-circle{{width:58px;height:58px;border-radius:50%;display:flex;flex-direction:column;
                 align-items:center;justify-content:center;font-size:1.1rem;font-weight:bold;
                 color:#fff;flex-shrink:0;text-align:center;line-height:1.2}}
  .score-circle small {{font-size:0.62rem;font-weight:normal;opacity:0.8}}

  .flags {{margin-bottom:12px}}

  .stats-row  {{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px}}
  .stat-box   {{background:#0d0d0d;border:1px solid #222;border-radius:8px;
                padding:10px 16px;text-align:center;flex:1;min-width:90px}}
  .sval {{font-size:1.25rem;font-weight:bold;color:#fff}}
  .slbl {{font-size:0.72rem;color:#888;text-transform:uppercase;letter-spacing:0.5px;margin-top:2px}}

  .date-range  {{color:#888;font-size:0.83rem;margin-bottom:10px}}
  .sample-label{{color:#ff8800;font-size:0.8rem;font-weight:bold;text-transform:uppercase;
                 letter-spacing:1px;margin-bottom:5px}}
  .sample-text {{color:#bbb;font-size:0.85rem;font-style:italic;background:#0d0d0d;
                 border-radius:6px;padding:10px;margin-bottom:14px;border-left:3px solid #ff4444}}

  .data-box   {{background:#0a0a0a;border:1px solid #333;border-radius:8px;padding:14px}}
  .data-title {{color:#888;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px}}
  .data-grid  {{display:grid;grid-template-columns:1fr 1fr;gap:6px}}
  .data-item  {{font-size:0.83rem;padding:4px 0}}
  .data-item.avail  {{color:#00cc66}}
  .data-item.missing{{color:#666}}
  .data-item strong {{color:inherit;opacity:0.9}}
</style>
</head>
<body>

<div class="page-title">🕵️ Suspect Reviewer Profiles</div>
<div class="page-sub">Top 30 most suspicious accounts — based on behavioral fraud signals</div>

<div class="limit-box">
  <h3>⚠️ What this dataset can and cannot tell us</h3>
  <strong>Available in the data:</strong> Username, self-reported city/province, review dates, hotels reviewed, ratings pattern, review text.<br>
  <strong>NOT available:</strong> Email address, phone number, real name, IP address, account ID, payment info.<br><br>
  To get contact information, the <strong>review platform itself</strong> (TripAdvisor, Booking.com, etc.) would need to be involved —
  they hold account registration data. Law enforcement can subpoena that data if fraud is confirmed.
  What we can do: <strong>build a strong evidence dossier</strong> for each account so the platform or authorities have grounds to act.
</div>

<div class="chart-wrap">
  <img src="data:image/png;base64,{chart_b64}" alt="Suspect accounts chart">
</div>

{build_cards()}

</body>
</html>"""

with open("output/suspect_profiles.html","w",encoding="utf-8") as f:
    f.write(html)
print("Saved: suspect_profiles.html")
print(f"\nTop suspect: {suspects.iloc[0]['user']} — avg score {suspects.iloc[0]['avg_score']:.1f}, "
      f"{int(suspects.iloc[0]['fake_reviews'])} fake reviews")
