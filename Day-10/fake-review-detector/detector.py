import subprocess, sys

def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

for pkg in ["textblob", "pandas", "matplotlib", "numpy", "scikit-learn", "pillow", "seaborn", "wordcloud"]:
    try:
        __import__(pkg.replace("-", "_"))
    except ImportError:
        install(pkg)

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud
from collections import defaultdict
from datetime import datetime
import re, base64, io, json, warnings
warnings.filterwarnings("ignore")

# ── Load data ──────────────────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv("data/hotel_reviews.csv", low_memory=False)
print(f"  Loaded {len(df):,} reviews")

# Normalise columns
df["rating"] = pd.to_numeric(df["reviews.rating"], errors="coerce")
df["text"]   = df["reviews.text"].fillna("").astype(str)
df["date"]   = pd.to_datetime(df["reviews.date"], errors="coerce")
df["hotel"]  = df["name"].fillna("Unknown Hotel").astype(str)
df["user"]   = df["reviews.username"].fillna("anonymous").astype(str)
df["date_only"] = df["date"].dt.date

# ── Signal helpers ─────────────────────────────────────────────────────────────
VAGUE     = {"great","good","bad","nice","terrible","amazing","worst","best",
             "awesome","horrible","loved","hated","perfect","recommend"}
SPECIFIC  = {"room","floor","lobby","parking","breakfast","pool","shower","bed",
             "wifi","staff","neighborhood","elevator","checkout"}

def word_count(text):
    return len(text.split())

def count_words_in_set(text, word_set):
    words = re.findall(r"\b\w+\b", text.lower())
    return sum(1 for w in words if w in word_set)

def exclamation_count(text):
    return text.count("!")

# ── Score each review ──────────────────────────────────────────────────────────
print("Scoring reviews...")

scores   = np.zeros(len(df), dtype=float)
signals  = [set() for _ in range(len(df))]

# Signal 1 — Review Length
wc = df["text"].apply(word_count)
mask_short_5 = (wc < 15) & (df["rating"] == 5)
mask_short_1 = (wc < 15) & (df["rating"] == 1)
for idx in df.index[mask_short_5]:
    scores[idx] += 20; signals[idx].add("Length")
for idx in df.index[mask_short_1]:
    scores[idx] += 20; signals[idx].add("Length")

# Signal 2 — Vague vs Specific
vague_cnt    = df["text"].apply(lambda t: count_words_in_set(t, VAGUE))
specific_cnt = df["text"].apply(lambda t: count_words_in_set(t, SPECIFIC))
ratio        = vague_cnt / (specific_cnt + 0.1)
mask_vague   = ratio > 3
for idx in df.index[mask_vague]:
    scores[idx] += 15; signals[idx].add("Vague")

# Signal 3 — Extreme Sentiment
print("  Computing sentiment (this may take a minute)...")
polarity = df["text"].apply(lambda t: TextBlob(t).sentiment.polarity)
mask_extreme = (polarity > 0.8) | (polarity < -0.8)
for idx in df.index[mask_extreme]:
    scores[idx] += 15; signals[idx].add("Extreme")

# Signal 4 — Duplicate / Similar Text
print("  Finding duplicates...")
sample_texts = df["text"].tolist()
tfidf = TfidfVectorizer(max_features=5000, stop_words="english")
tfidf_matrix = tfidf.fit_transform(sample_texts)

BATCH = 2000
dup_flags  = np.zeros(len(df), dtype=bool)
dup_cluster= [-1] * len(df)
cluster_id = 0
cluster_map = {}  # cluster_id -> list of indices

for start in range(0, len(df), BATCH):
    end  = min(start + BATCH, len(df))
    chunk = tfidf_matrix[start:end]
    sim   = cosine_similarity(chunk, tfidf_matrix)
    for i in range(end - start):
        global_i = start + i
        row = sim[i]
        row[global_i] = 0  # exclude self
        matches = np.where(row >= 0.80)[0]
        if len(matches) > 0:
            dup_flags[global_i] = True
            # assign cluster
            neighbors = [global_i] + list(matches)
            existing = None
            for n in neighbors:
                if dup_cluster[n] >= 0:
                    existing = dup_cluster[n]
                    break
            if existing is None:
                existing = cluster_id
                cluster_map[existing] = []
                cluster_id += 1
            for n in neighbors:
                dup_cluster[n] = existing
                if n not in cluster_map.get(existing, []):
                    cluster_map.setdefault(existing, []).append(n)

for idx in np.where(dup_flags)[0]:
    scores[idx] += 20; signals[idx].add("Duplicate")

# Signal 5 — Reviewer Behavior
print("  Analysing reviewer behaviour...")
user_hotel_date = df.groupby(["user","hotel","date_only"]).size().reset_index(name="cnt")
multi_same_day  = set(
    zip(user_hotel_date[user_hotel_date["cnt"] > 1]["user"],
        user_hotel_date[user_hotel_date["cnt"] > 1]["hotel"])
)
user_ratings    = df.groupby("user")["rating"].nunique()
one_sided_users = set(user_ratings[user_ratings == 1].index)

for idx, row in df.iterrows():
    if (row["user"], row["hotel"]) in multi_same_day:
        scores[idx] += 15; signals[idx].add("Behavior")
    if row["user"] in one_sided_users:
        scores[idx] += 10; signals[idx].add("Behavior")

# Signal 6 — Rating Distribution Anomaly
hotel_rating_dist = df.groupby("hotel")["rating"].apply(
    lambda x: (x == 5).sum() / len(x) if len(x) > 0 else 0
)
manipulated_hotels = set(hotel_rating_dist[hotel_rating_dist >= 0.90].index)
for idx, row in df.iterrows():
    if row["hotel"] in manipulated_hotels:
        scores[idx] += 10; signals[idx].add("Rating")

# Signal 7 — Timing Bursts
hotel_day_counts = df.groupby(["hotel","date_only"]).size().reset_index(name="cnt")
burst_pairs = set(
    zip(hotel_day_counts[hotel_day_counts["cnt"] >= 5]["hotel"],
        hotel_day_counts[hotel_day_counts["cnt"] >= 5]["date_only"])
)
for idx, row in df.iterrows():
    if (row["hotel"], row["date_only"]) in burst_pairs:
        scores[idx] += 15; signals[idx].add("Timing")

# Signal 8 — Exclamation Overuse
exc = df["text"].apply(exclamation_count)
mask_exc = exc >= 3
for idx in df.index[mask_exc]:
    scores[idx] += 10; signals[idx].add("Exclamation")

# ── Clamp scores and label ──────────────────────────────────────────────────────
scores = np.clip(scores, 0, 100)

def label(s):
    if s <= 20:  return "Genuine"
    if s <= 40:  return "Low Suspicion"
    if s <= 60:  return "Moderate Suspicion"
    if s <= 80:  return "High Suspicion"
    return "Likely Fake"

df["suspicion_score"]  = scores
df["suspicion_label"]  = [label(s) for s in scores]
df["signals_triggered"]= [list(s) for s in signals]
df["polarity"]         = polarity.values

print(f"  Scoring done. Mean score: {scores.mean():.1f}")

# ── Summary stats ──────────────────────────────────────────────────────────────
total      = len(df)
genuine    = (scores <= 20).sum()
low_sus    = ((scores > 20) & (scores <= 40)).sum()
mod_sus    = ((scores > 40) & (scores <= 60)).sum()
high_sus   = ((scores > 60) & (scores <= 80)).sum()
likely_fake= (scores > 80).sum()
flagged    = (scores > 20).sum()

pct_genuine     = genuine / total * 100
pct_flagged     = flagged / total * 100
pct_likely_fake = likely_fake / total * 100

print(f"\n  Genuine:      {genuine:,} ({pct_genuine:.1f}%)")
print(f"  Flagged:      {flagged:,} ({pct_flagged:.1f}%)")
print(f"  Likely Fake:  {likely_fake:,} ({pct_likely_fake:.1f}%)")

# ── Signal counts ──────────────────────────────────────────────────────────────
signal_names = ["Length","Vague","Extreme","Duplicate","Behavior","Rating","Timing","Exclamation"]
signal_counts = {s: sum(1 for sig_set in signals if s in sig_set) for s in signal_names}
print("\n  Signal counts:", signal_counts)

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT 2 — suspicion_heatmap.png
# ══════════════════════════════════════════════════════════════════════════════
print("\nGenerating suspicion_heatmap.png...")
hotel_signal = defaultdict(lambda: defaultdict(int))
for idx, row in df.iterrows():
    for sig in signals[idx]:
        hotel_signal[row["hotel"]][sig] += 1

top20_hotels = (df.groupby("hotel")["suspicion_score"]
                  .mean().nlargest(20).index.tolist())
hm_data = pd.DataFrame(
    [[hotel_signal[h].get(s, 0) for s in signal_names] for h in top20_hotels],
    index=[h[:30] for h in top20_hotels],
    columns=signal_names
)

fig, ax = plt.subplots(figsize=(14, 9))
fig.patch.set_facecolor("#0d0d0d")
ax.set_facecolor("#0d0d0d")
sns.heatmap(hm_data, ax=ax, cmap="Reds", linewidths=0.5,
            linecolor="#333", annot=True, fmt="d",
            cbar_kws={"shrink": 0.8})
ax.set_title("Fraud Signal Heatmap — Top 20 Suspicious Hotels",
             color="white", fontsize=15, pad=15)
ax.tick_params(colors="white")
plt.setp(ax.get_xticklabels(), color="white", rotation=30, ha="right")
plt.setp(ax.get_yticklabels(), color="white", rotation=0)
ax.figure.axes[-1].tick_params(colors="white")
plt.tight_layout()
plt.savefig("output/suspicion_heatmap.png", dpi=150, bbox_inches="tight",
            facecolor="#0d0d0d")
plt.close()
print("  Saved.")

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT 3 — genuine_vs_fake_wordcloud.png
# ══════════════════════════════════════════════════════════════════════════════
print("Generating genuine_vs_fake_wordcloud.png...")
genuine_text    = " ".join(df[df["suspicion_score"] < 20]["text"].tolist())
suspicious_text = " ".join(df[df["suspicion_score"] > 50]["text"].tolist())

wc_genuine = WordCloud(width=800, height=600, background_color="black",
                       colormap="Greens", max_words=200).generate(genuine_text or "genuine")
wc_fake    = WordCloud(width=800, height=600, background_color="black",
                       colormap="Reds",   max_words=200).generate(suspicious_text or "fake")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
fig.patch.set_facecolor("#0d0d0d")
for ax in (ax1, ax2):
    ax.set_facecolor("#0d0d0d")
    ax.axis("off")

ax1.imshow(wc_genuine, interpolation="bilinear")
ax1.set_title("GENUINE REVIEWS  (score < 20)", color="#00ff88",
              fontsize=14, fontweight="bold", pad=12)
ax2.imshow(wc_fake, interpolation="bilinear")
ax2.set_title("SUSPICIOUS REVIEWS  (score > 50)", color="#ff4444",
              fontsize=14, fontweight="bold", pad=12)

# divider line
fig.add_artist(plt.Line2D([0.5, 0.5], [0.05, 0.95],
               transform=fig.transFigure, color="#555", linewidth=2))
plt.tight_layout()
plt.savefig("output/genuine_vs_fake_wordcloud.png", dpi=150,
            bbox_inches="tight", facecolor="#0d0d0d")
plt.close()
print("  Saved.")

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT 4 — signal_radar.png
# ══════════════════════════════════════════════════════════════════════════════
print("Generating signal_radar.png...")
vals = [signal_counts[s] for s in signal_names]
N    = len(signal_names)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]
vals_plot = vals + vals[:1]

fig = plt.figure(figsize=(9, 9), facecolor="#0d0d0d")
ax  = fig.add_subplot(111, polar=True)
ax.set_facecolor("#0d0d0d")
ax.plot(angles, vals_plot, "o-", color="#ff4444", linewidth=2)
ax.fill(angles, vals_plot, alpha=0.35, color="#ff4444")
ax.set_xticks(angles[:-1])
ax.set_xticklabels(signal_names, color="white", fontsize=12)
ax.tick_params(colors="white")
ax.yaxis.label.set_color("white")
ax.spines["polar"].set_color("#444")
ax.grid(color="#333", linewidth=0.7)
plt.setp(ax.get_yticklabels(), color="#888")
ax.set_title("Fraud Signal Radar", color="white", fontsize=16,
             fontweight="bold", pad=25)
plt.tight_layout()
plt.savefig("output/signal_radar.png", dpi=150, bbox_inches="tight",
            facecolor="#0d0d0d")
plt.close()
print("  Saved.")

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT 5 — rating_comparison.png
# ══════════════════════════════════════════════════════════════════════════════
print("Generating rating_comparison.png...")
genuine_ratings    = df[df["suspicion_score"] < 20]["rating"].dropna()
suspicious_ratings = df[df["suspicion_score"] > 50]["rating"].dropna()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor("#0d0d0d")
for ax in (ax1, ax2):
    ax.set_facecolor("#111")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#333")

bins = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
ax1.hist(genuine_ratings, bins=bins, color="#00cc66", edgecolor="#0d0d0d", rwidth=0.8)
ax1.set_title("Genuine Reviews\n(score < 20)", fontsize=13)
ax1.set_xlabel("Rating"); ax1.set_ylabel("Count")
ax1.set_xticks([1,2,3,4,5])

ax2.hist(suspicious_ratings, bins=bins, color="#ff4444", edgecolor="#0d0d0d", rwidth=0.8)
ax2.set_title("Suspicious Reviews\n(score > 50)", fontsize=13)
ax2.set_xlabel("Rating"); ax2.set_ylabel("Count")
ax2.set_xticks([1,2,3,4,5])

fig.suptitle("Rating Distribution: Genuine vs Suspicious", color="white",
             fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("output/rating_comparison.png", dpi=150, bbox_inches="tight",
            facecolor="#0d0d0d")
plt.close()
print("  Saved.")

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT 6 — timeline_bursts.png
# ══════════════════════════════════════════════════════════════════════════════
print("Generating timeline_bursts.png...")
daily = df.groupby(["hotel","date_only"]).size().reset_index(name="count")
daily["date_only"] = pd.to_datetime(daily["date_only"])
bursts  = daily[daily["count"] >= 5]
normal  = daily[daily["count"] < 5]

fig, ax = plt.subplots(figsize=(16, 7))
fig.patch.set_facecolor("#0d0d0d")
ax.set_facecolor("#111")
ax.scatter(normal["date_only"], normal["count"], color="#555", alpha=0.4, s=15, label="Normal")
ax.scatter(bursts["date_only"], bursts["count"], color="#ff4444", s=60,
           alpha=0.85, zorder=5, label="Burst (5+)")

for _, row in bursts.nlargest(12, "count").iterrows():
    ax.annotate(row["hotel"][:20], (row["date_only"], row["count"]),
                textcoords="offset points", xytext=(0, 6),
                fontsize=7, color="#ffaa44", ha="center")

ax.set_title("Review Burst Timeline", color="white", fontsize=14, fontweight="bold")
ax.set_xlabel("Date", color="white"); ax.set_ylabel("Reviews / Day / Hotel", color="white")
ax.tick_params(colors="white")
for spine in ax.spines.values():
    spine.set_edgecolor("#333")
ax.legend(facecolor="#222", edgecolor="#444", labelcolor="white")
plt.tight_layout()
plt.savefig("output/timeline_bursts.png", dpi=150, bbox_inches="tight",
            facecolor="#0d0d0d")
plt.close()
print("  Saved.")

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT 7 — top_suspects.png
# ══════════════════════════════════════════════════════════════════════════════
print("Generating top_suspects.png...")
top5 = df.nlargest(5, "suspicion_score").reset_index(drop=True)

fig, axes = plt.subplots(5, 1, figsize=(14, 18))
fig.patch.set_facecolor("#0d0d0d")
fig.suptitle("★  MOST WANTED  —  TOP 5 SUSPICIOUS REVIEWS  ★",
             color="#ff4444", fontsize=17, fontweight="bold", y=0.98)

COLORS = {
    "Length":"#ff6b6b","Vague":"#ffa94d","Extreme":"#ff4444",
    "Duplicate":"#cc00cc","Behavior":"#4dabf7","Rating":"#ffd43b",
    "Timing":"#ff8787","Exclamation":"#69db7c"
}

for i, (ax, (_, row)) in enumerate(zip(axes, top5.iterrows())):
    ax.set_facecolor("#1a1a1a")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    score = row["suspicion_score"]
    bar_w = score / 100
    ax.add_patch(FancyBboxPatch((0.01, 0.05), 0.98, 0.9,
                                boxstyle="round,pad=0.01",
                                facecolor="#1a1a1a", edgecolor="#ff4444",
                                linewidth=1.5))
    ax.add_patch(plt.Rectangle((0.03, 0.08), bar_w * 0.6, 0.12,
                                color=("#ff4444" if score > 60 else "#ffa94d")))
    ax.text(0.03 + bar_w * 0.6 + 0.01, 0.14,
            f"{score:.0f}/100", color="white", fontsize=10, va="center")
    hotel = str(row["hotel"])[:40]
    rating = row["rating"]
    ax.text(0.03, 0.85, f"#{i+1}  {hotel}  ★{rating}", color="#ff8888",
            fontsize=11, fontweight="bold", va="top")
    snippet = str(row["text"])[:200].replace("\n", " ")
    ax.text(0.03, 0.68, f'"{snippet}..."', color="#cccccc",
            fontsize=8.5, va="top", wrap=True,
            bbox=dict(facecolor="none", edgecolor="none"))
    x_badge = 0.03
    for sig in row["signals_triggered"]:
        c = COLORS.get(sig, "#888")
        ax.add_patch(FancyBboxPatch((x_badge, 0.08), 0.07, 0.14,
                                    boxstyle="round,pad=0.005",
                                    facecolor=c, edgecolor="none", alpha=0.8,
                                    zorder=5))
        ax.text(x_badge + 0.035, 0.15, sig, color="black",
                fontsize=6.5, ha="center", va="center",
                fontweight="bold", zorder=6)
        x_badge += 0.09

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig("output/top_suspects.png", dpi=150, bbox_inches="tight",
            facecolor="#0d0d0d")
plt.close()
print("  Saved.")

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT 8 — fraud_report.md
# ══════════════════════════════════════════════════════════════════════════════
print("Generating fraud_report.md...")

top10_reviews = df.nlargest(10, "suspicion_score")[
    ["hotel","rating","suspicion_score","signals_triggered","text"]
].reset_index(drop=True)

hotel_flag = (df.groupby("hotel")
              .apply(lambda g: pd.Series({
                  "total": len(g),
                  "flagged": (g["suspicion_score"] > 20).sum(),
                  "pct_flagged": (g["suspicion_score"] > 20).mean() * 100,
                  "mean_score": g["suspicion_score"].mean()
              }))
              .sort_values("pct_flagged", ascending=False)
              .head(10))

dup_clusters = {cid: idxs for cid, idxs in cluster_map.items() if len(idxs) >= 2}

burst_info = hotel_day_counts[hotel_day_counts["cnt"] >= 5].sort_values("cnt", ascending=False).head(10)

top_signal = max(signal_counts, key=signal_counts.get)

report = f"""# Fake Review Investigation Report

**Date:** 2026-03-27
**Dataset:** data/hotel_reviews.csv

---

## Executive Summary

A total of **{total:,} hotel reviews** were analysed across multiple properties.
Automated fraud signals reveal significant manipulation activity, with
**{flagged:,} reviews ({pct_flagged:.1f}%)** showing at least one suspicious
characteristic and **{likely_fake:,} reviews ({pct_likely_fake:.1f}%)** classified
as *Likely Fake*.

The dominant fraud pattern is **{top_signal}**, suggesting systematic review
manipulation via {top_signal.lower()}-based tactics.

---

## Totals

| Category | Count | % |
|---|---|---|
| Total Analysed | {total:,} | 100% |
| Genuine (0–20) | {genuine:,} | {genuine/total*100:.1f}% |
| Low Suspicion (21–40) | {low_sus:,} | {low_sus/total*100:.1f}% |
| Moderate Suspicion (41–60) | {mod_sus:,} | {mod_sus/total*100:.1f}% |
| High Suspicion (61–80) | {high_sus:,} | {high_sus/total*100:.1f}% |
| Likely Fake (81–100) | {likely_fake:,} | {likely_fake/total*100:.1f}% |

---

## Top 10 Most Suspicious Reviews

"""
for i, row in top10_reviews.iterrows():
    report += f"""### #{i+1} — Score: {row['suspicion_score']:.0f}/100
**Hotel:** {row['hotel']}  **Rating:** {row['rating']}
**Signals:** {', '.join(row['signals_triggered'])}
**Text:** _{str(row['text'])[:400]}_

"""

report += "---\n\n## Most Suspicious Hotels\n\n"
report += "| Hotel | Total Reviews | Flagged | % Flagged | Mean Score |\n"
report += "|---|---|---|---|---|\n"
for h, row in hotel_flag.iterrows():
    report += f"| {h[:40]} | {int(row['total'])} | {int(row['flagged'])} | {row['pct_flagged']:.1f}% | {row['mean_score']:.1f} |\n"

report += "\n---\n\n## Duplicate Clusters Found\n\n"
for cid, idxs in list(dup_clusters.items())[:10]:
    sample_text = df.iloc[idxs[0]]["text"][:200] if idxs else ""
    report += f"**Cluster {cid}** ({len(idxs)} reviews):\n> _{sample_text}..._\n\n"

report += "\n---\n\n## Timing Bursts Detected\n\n"
report += "| Hotel | Date | Reviews in Day |\n|---|---|---|\n"
for _, row in burst_info.iterrows():
    report += f"| {str(row['hotel'])[:40]} | {row['date_only']} | {row['cnt']} |\n"

report += f"""
---

## Genuine vs Suspicious Language

**Genuine reviews** tend to use specific, contextual language — mentioning
exact amenities, locations, and staff interactions with moderate sentiment.

**Suspicious reviews** are characterised by vague superlatives (*amazing*,
*perfect*, *worst ever*), extreme polarity, and repetitive phrasing — often
recycled across multiple properties by the same user.

---

## Recommendations

1. **Rate-limit reviews per user per day** — cap at 3 to prevent burst campaigns.
2. **Flag vague-only reviews for manual moderation** before publishing.
3. **Cluster near-duplicate text** across the platform and auto-suppress repeats.
4. **Track reviewer rating entropy** — one-sided reviewers should be shadow-flagged.
5. **Introduce verified stay confirmation** before allowing 5-star reviews.

---

## Verdict

The dataset shows **widespread manipulation**. The {top_signal} signal alone
accounts for {signal_counts[top_signal]:,} flagged reviews. Hotels with suspiciously
high five-star concentrations represent coordinated rating inflation.
Platform trust requires immediate algorithmic intervention.

---
*Generated by detector.py — Fake Review Detector*
"""

with open("output/fraud_report.md", "w", encoding="utf-8") as f:
    f.write(report)
print("  Saved.")

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT 1 — dashboard.html (last, needs all data)
# ══════════════════════════════════════════════════════════════════════════════
print("Generating dashboard.html...")

def img_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

imgs = {k: img_to_b64(f"output/{k}") for k in [
    "suspicion_heatmap.png",
    "genuine_vs_fake_wordcloud.png",
    "signal_radar.png",
    "rating_comparison.png",
    "timeline_bursts.png",
    "top_suspects.png",
]}

# Top 15 suspicious reviews for case cards
top15 = df.nlargest(15, "suspicion_score").reset_index(drop=True)

SCORE_COLOR = {
    "Genuine":"#00cc66",
    "Low Suspicion":"#cccc00",
    "Moderate Suspicion":"#ff8800",
    "High Suspicion":"#ff4444",
    "Likely Fake":"#cc0000"
}

def score_color(s):
    if s <= 20:  return "#00cc66"
    if s <= 40:  return "#cccc00"
    if s <= 60:  return "#ff8800"
    if s <= 80:  return "#ff4444"
    return "#cc0000"

def build_case_cards():
    html = ""
    for _, row in top15.iterrows():
        sc = row["suspicion_score"]
        col = score_color(sc)
        badge_html = "".join(
            f'<span class="sig-badge" style="background:{COLORS.get(s,"#888")}">{s}</span>'
            for s in row["signals_triggered"]
        )
        snippet = str(row["text"])[:300].replace("<","&lt;").replace(">","&gt;")
        html += f"""
<div class="case-card">
  <div class="case-header">
    <span class="hotel-name">{str(row['hotel'])[:45]}</span>
    <span class="rating-badge">★ {row['rating']}</span>
    <span class="score-badge" style="background:{col}">{sc:.0f}/100</span>
  </div>
  <div class="case-text">"{snippet}..."</div>
  <div class="meter-wrap">
    <div class="meter-bar" style="width:{sc}%;background:{col}"></div>
  </div>
  <div class="sig-row">{badge_html}</div>
</div>"""
    return html

# Genuine / Fake example quotes
genuine_samples = df[df["suspicion_score"] < 20].dropna(subset=["text"]).head(5).reset_index()
fake_samples    = df[df["suspicion_score"] > 70].dropna(subset=["text"]).head(5).reset_index()

def quote_list(rows, col, color):
    out = ""
    for _, r in rows.iterrows():
        t = str(r[col])[:200].replace("<","&lt;").replace(">","&gt;")
        out += f'<div class="quote" style="border-left:3px solid {color};padding-left:10px;margin-bottom:12px;color:#ccc">"{t}..."</div>'
    return out

# Duplicate cluster cards
def dup_cards():
    out = ""
    for cid, idxs in list(dup_clusters.items())[:6]:
        if not idxs: continue
        sample = str(df.iloc[idxs[0]]["text"])[:250].replace("<","&lt;").replace(">","&gt;")
        out += f"""
<div class="dup-card">
  <div style="color:#ff8800;font-weight:bold;margin-bottom:6px">
    {len(idxs)} near-identical reviews
  </div>
  <div style="color:#bbb;font-size:13px">"{sample}..."</div>
</div>"""
    return out or "<p style='color:#888'>No significant duplicate clusters found.</p>"

# Suspicious hotels table
hotel_sus_top10 = hotel_flag.head(10)
def hotel_rows():
    out = ""
    for h, row in hotel_sus_top10.iterrows():
        sc = row["mean_score"]
        col = score_color(sc)
        lbl = label(sc)
        out += f"""
<div class="hotel-card">
  <div class="hotel-name-big">{h[:45]}</div>
  <div class="hotel-stats">
    <span>{int(row['total'])} reviews</span>
    <span style="color:#ff8800">{int(row['flagged'])} flagged</span>
    <span style="color:#ff4444">{row['pct_flagged']:.1f}% flagged</span>
    <span class="hotel-badge" style="background:{col}">{lbl}</span>
  </div>
</div>"""
    return out

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fake Review Detector — Dashboard</title>
<style>
  * {{box-sizing:border-box;margin:0;padding:0}}
  body {{background:#0a0a0a;color:#e0e0e0;font-family:'Segoe UI',sans-serif;line-height:1.5}}
  h2   {{color:#ff4444;font-size:1.5rem;margin-bottom:18px;text-transform:uppercase;letter-spacing:2px}}
  h3   {{color:#ff8888;margin-bottom:10px}}

  /* Hero */
  .hero {{background:linear-gradient(135deg,#1a0000 0%,#0a0a0a 60%,#001a00 100%);
          padding:60px 40px;text-align:center;border-bottom:2px solid #ff4444}}
  .hero h1 {{font-size:2.8rem;color:#ff4444;text-transform:uppercase;letter-spacing:4px;margin-bottom:6px}}
  .hero sub {{color:#888;font-size:1rem;letter-spacing:2px}}
  .hero-grid {{display:flex;justify-content:center;gap:40px;margin-top:40px;flex-wrap:wrap}}
  .hero-stat {{background:#111;border:1px solid #333;border-radius:12px;padding:24px 36px;min-width:160px}}
  .hero-stat .big {{font-size:2.8rem;font-weight:bold}}
  .hero-stat .lbl {{color:#888;font-size:0.85rem;text-transform:uppercase;letter-spacing:1px}}
  .green {{color:#00cc66}}  .red {{color:#ff4444}}  .orange {{color:#ff8800}}  .yellow {{color:#cccc00}}

  /* Sections */
  .section {{padding:50px 40px;border-bottom:1px solid #1a1a1a;max-width:1400px;margin:0 auto}}

  /* Case cards */
  .cards-grid {{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}}
  .case-card {{background:#111;border:1px solid #2a2a2a;border-radius:10px;padding:18px;
               border-left:3px solid #ff4444}}
  .case-header {{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}}
  .hotel-name {{font-weight:bold;color:#ff8888;flex:1;font-size:0.95rem}}
  .rating-badge {{background:#222;border:1px solid #555;border-radius:6px;
                  padding:3px 10px;color:#ffd700;font-size:0.9rem}}
  .score-badge {{border-radius:6px;padding:3px 12px;font-weight:bold;font-size:0.9rem;color:#fff}}
  .case-text {{color:#aaa;font-size:0.85rem;margin:8px 0;font-style:italic;
               max-height:70px;overflow:hidden}}
  .meter-wrap {{background:#222;border-radius:4px;height:6px;margin:10px 0}}
  .meter-bar {{height:6px;border-radius:4px;transition:width .3s}}
  .sig-row {{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}}
  .sig-badge {{border-radius:4px;padding:2px 8px;font-size:0.75rem;color:#000;font-weight:bold}}

  /* Hotels */
  .hotel-card {{background:#111;border:1px solid #2a2a2a;border-radius:10px;
                padding:16px 20px;margin-bottom:12px}}
  .hotel-name-big {{font-weight:bold;color:#ff8888;font-size:1rem;margin-bottom:8px}}
  .hotel-stats {{display:flex;gap:16px;flex-wrap:wrap;font-size:0.9rem;color:#bbb}}
  .hotel-badge {{border-radius:6px;padding:2px 10px;font-size:0.8rem;color:#fff}}

  /* Charts */
  .chart-img {{width:100%;border-radius:10px;border:1px solid #222;margin-top:10px}}

  /* Language comparison */
  .lang-grid {{display:grid;grid-template-columns:1fr 1fr;gap:24px}}
  .lang-card {{background:#111;border-radius:10px;padding:20px;border:1px solid #2a2a2a}}

  /* Dup cards */
  .dup-card {{background:#111;border:1px solid #333;border-left:3px solid #ff8800;
              border-radius:8px;padding:16px;margin-bottom:14px}}

  /* Verdict */
  .verdict {{background:linear-gradient(135deg,#1a0000,#0a0a0a);border:2px solid #ff4444;
             border-radius:16px;padding:40px;text-align:center;margin-top:20px}}
  .verdict .big-find {{font-size:1.8rem;color:#ff4444;font-weight:bold;margin:20px 0}}
  .verdict ul {{list-style:none;text-align:left;display:inline-block;margin-top:16px}}
  .verdict ul li {{padding:6px 0;color:#ccc}}
  .verdict ul li::before {{content:"▶ ";color:#ff4444}}
</style>
</head>
<body>

<!-- ── Hero ── -->
<div class="hero">
  <h1>🔍 Fake Review Detector</h1>
  <div><sub>Hotel Review Fraud Intelligence Dashboard</sub></div>
  <div class="hero-grid">
    <div class="hero-stat">
      <div class="big">{total:,}</div>
      <div class="lbl">Total Reviews</div>
    </div>
    <div class="hero-stat">
      <div class="big green">{pct_genuine:.1f}%</div>
      <div class="lbl">Genuine</div>
    </div>
    <div class="hero-stat">
      <div class="big orange">{pct_flagged:.1f}%</div>
      <div class="lbl">Suspicious</div>
    </div>
    <div class="hero-stat">
      <div class="big red">{pct_likely_fake:.1f}%</div>
      <div class="lbl">Likely Fake</div>
    </div>
    <div class="hero-stat">
      <div class="big yellow">{likely_fake:,}</div>
      <div class="lbl">Flagged Reviews</div>
    </div>
  </div>
</div>

<!-- ── Investigation Board ── -->
<div class="section">
  <h2>🚨 Investigation Board — Top 15 Suspects</h2>
  <div class="cards-grid">
    {build_case_cards()}
  </div>
</div>

<!-- ── Signal Radar ── -->
<div class="section">
  <h2>📡 Signal Radar</h2>
  <img class="chart-img" src="data:image/png;base64,{imgs['signal_radar.png']}"
       alt="Signal Radar">
</div>

<!-- ── Suspicious Hotels ── -->
<div class="section">
  <h2>🏨 Most Suspicious Hotels</h2>
  {hotel_rows()}
</div>

<!-- ── Genuine vs Fake Language ── -->
<div class="section">
  <h2>💬 Genuine vs Suspicious Language</h2>
  <div class="lang-grid">
    <div class="lang-card" style="border-left:3px solid #00cc66">
      <h3 style="color:#00cc66">What Genuine Reviews Sound Like</h3>
      {quote_list(genuine_samples, "text", "#00cc66")}
    </div>
    <div class="lang-card" style="border-left:3px solid #ff4444">
      <h3 style="color:#ff4444">What Suspicious Reviews Sound Like</h3>
      {quote_list(fake_samples, "text", "#ff4444")}
    </div>
  </div>
  <img class="chart-img" src="data:image/png;base64,{imgs['genuine_vs_fake_wordcloud.png']}"
       alt="Word Cloud">
</div>

<!-- ── Duplicate Evidence ── -->
<div class="section">
  <h2>🔁 Duplicate Evidence</h2>
  {dup_cards()}
</div>

<!-- ── Heatmap ── -->
<div class="section">
  <h2>🗺 Suspicion Heatmap</h2>
  <img class="chart-img" src="data:image/png;base64,{imgs['suspicion_heatmap.png']}"
       alt="Heatmap">
</div>

<!-- ── Rating Comparison ── -->
<div class="section">
  <h2>⭐ Rating Distribution</h2>
  <img class="chart-img" src="data:image/png;base64,{imgs['rating_comparison.png']}"
       alt="Rating Comparison">
</div>

<!-- ── Timing Bursts ── -->
<div class="section">
  <h2>📅 Timing Burst Timeline</h2>
  <img class="chart-img" src="data:image/png;base64,{imgs['timeline_bursts.png']}"
       alt="Timeline Bursts">
</div>

<!-- ── Top Suspects poster ── -->
<div class="section">
  <h2>🎯 Most Wanted Poster</h2>
  <img class="chart-img" src="data:image/png;base64,{imgs['top_suspects.png']}"
       alt="Top Suspects">
</div>

<!-- ── Verdict ── -->
<div class="section">
  <h2>⚖️ The Verdict</h2>
  <div class="verdict">
    <div>Overall trustworthiness assessment:</div>
    <div class="big-find">
      {pct_likely_fake:.1f}% of reviews show strong fraud indicators
    </div>
    <div style="color:#888">Dominant pattern: <strong style="color:#ff8800">{top_signal}</strong>
      ({signal_counts[top_signal]:,} reviews affected)</div>
    <ul>
      <li>Implement per-user daily review limits to prevent burst campaigns</li>
      <li>Auto-cluster near-duplicate text to catch copy-paste fraud rings</li>
      <li>Require verified stay confirmation before publishing 5-star reviews</li>
    </ul>
  </div>
</div>

</body>
</html>"""

with open("output/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("  Saved.")

# ── Final summary ──────────────────────────────────────────────────────────────
print("\n" + "="*60)
print(f"DONE — All 8 output files created in output/")
print(f"  Total flagged:          {flagged:,} ({pct_flagged:.1f}%)")
most_sus_hotel = hotel_flag["mean_score"].idxmax()
print(f"  Most suspicious hotel:  {most_sus_hotel}")
print(f"  #1 fraud pattern:       {top_signal} ({signal_counts[top_signal]:,} reviews)")
print("="*60)
