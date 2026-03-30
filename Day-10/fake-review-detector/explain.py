import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings("ignore")

# ── Rebuild signal counts from detector output ─────────────────────────────────
signal_names  = ["Length","Vague","Extreme","Duplicate","Behavior","Rating","Timing","Exclamation"]
signal_counts = {'Length': 3283, 'Vague': 5466, 'Extreme': 1014,
                 'Duplicate': 5539, 'Behavior': 20867, 'Rating': 420,
                 'Timing': 450, 'Exclamation': 1540}

signal_colors = {
    "Length":      "#ff6b6b",
    "Vague":       "#ffa94d",
    "Extreme":     "#ff4444",
    "Duplicate":   "#cc00cc",
    "Behavior":    "#4dabf7",
    "Rating":      "#ffd43b",
    "Timing":      "#ff8787",
    "Exclamation": "#69db7c",
}

# Plain-English explanation per signal
signal_explain = {
    "Behavior":    ("Reviewer Behavior",
                    "20,867 reviews",
                    "Same user posts ONLY 5★ or ONLY 1★ across\nevery review they've ever written.\nReal reviewers give mixed ratings.",
                    "🕵️"),
    "Duplicate":   ("Copy-Paste Text",
                    "5,539 reviews",
                    "80%+ of the words match another review\nelsewhere in the dataset. Fake farms\nrecycle the same text across hotels.",
                    "🔁"),
    "Vague":       ("Vague Language",
                    "5,466 reviews",
                    "Words like 'amazing', 'perfect', 'worst'\nwith zero specific details — no mention\nof room, staff, breakfast, or location.",
                    "💬"),
    "Length":      ("Suspiciously Short",
                    "3,283 reviews",
                    "Under 15 words + extreme rating (1★ or 5★).\n'Perfect hotel!!!' or 'Terrible place.'\nReal guests write more.",
                    "📏"),
    "Exclamation": ("Exclamation Overuse",
                    "1,540 reviews",
                    "3+ exclamation marks in one review.\nAuthentic writers rarely write\n'Amazing!!! Best stay ever!!! Loved it!!!'",
                    "❗"),
    "Extreme":     ("Extreme Sentiment",
                    "1,014 reviews",
                    "TextBlob polarity > 0.8 or < -0.8.\nStatistically, real reviews cluster\naround neutral — not perfect or furious.",
                    "📊"),
    "Timing":      ("Review Burst",
                    "450 reviews",
                    "5+ reviews for one hotel posted\nin a single day. Coordinated campaigns\nleave this timing fingerprint.",
                    "📅"),
    "Rating":      ("Rating Inflation",
                    "420 reviews",
                    "Hotel has 90%+ five-star reviews.\nStatistically impossible for real hotels —\npoints to coordinated boosting.",
                    "⭐"),
}

# ── Figure ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 22), facecolor="#0a0a0a")
fig.suptitle("WHY ARE THESE REVIEWS SUSPICIOUS?",
             color="#ff4444", fontsize=22, fontweight="bold", y=0.99)
fig.text(0.5, 0.975, "8 fraud signals — what each one means and how many reviews it caught",
         color="#888", fontsize=12, ha="center")

gs = GridSpec(5, 2, figure=fig, hspace=0.55, wspace=0.35,
              top=0.96, bottom=0.02, left=0.05, right=0.95)

order = ["Behavior","Duplicate","Vague","Length","Exclamation","Extreme","Timing","Rating"]

for i, sig in enumerate(order):
    row, col = divmod(i, 2)
    ax = fig.add_subplot(gs[row, col])
    ax.set_facecolor("#111")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    title, count_str, explain, emoji = signal_explain[sig]
    bar_color = signal_colors[sig]
    bar_w = signal_counts[sig] / max(signal_counts.values())

    # Card border
    rect = mpatches.FancyBboxPatch((0, 0), 1, 1,
                                   boxstyle="round,pad=0.02",
                                   facecolor="#111",
                                   edgecolor=bar_color, linewidth=2,
                                   transform=ax.transAxes, clip_on=False)
    ax.add_patch(rect)

    # Coloured top strip
    ax.add_patch(plt.Rectangle((0, 0.85), 1, 0.15,
                                color=bar_color, alpha=0.25, zorder=1))

    # Emoji + title
    ax.text(0.04, 0.915, f"{emoji}  {title}", color="white",
            fontsize=13, fontweight="bold", va="center", zorder=2)

    # Count badge
    ax.text(0.96, 0.915, count_str, color=bar_color,
            fontsize=11, fontweight="bold", va="center", ha="right", zorder=2)

    # Explanation text
    ax.text(0.05, 0.70, explain, color="#cccccc",
            fontsize=10.5, va="top", linespacing=1.6)

    # Progress bar background
    ax.add_patch(plt.Rectangle((0.05, 0.10), 0.90, 0.10,
                                color="#222", zorder=2))
    # Progress bar fill
    ax.add_patch(plt.Rectangle((0.05, 0.10), 0.90 * bar_w, 0.10,
                                color=bar_color, alpha=0.85, zorder=3))

    pct = signal_counts[sig] / 35912 * 100
    ax.text(0.5, 0.155, f"{pct:.1f}% of all reviews",
            color="white", fontsize=9, ha="center", va="center", zorder=4,
            fontweight="bold")

# ── Bottom summary row ─────────────────────────────────────────────────────────
ax_sum = fig.add_subplot(gs[4, :])
ax_sum.set_facecolor("#111")
ax_sum.set_xlim(0, 1); ax_sum.set_ylim(0, 1); ax_sum.axis("off")

ax_sum.add_patch(mpatches.FancyBboxPatch((0, 0), 1, 1,
                                         boxstyle="round,pad=0.02",
                                         facecolor="#111",
                                         edgecolor="#ff4444", linewidth=2,
                                         transform=ax_sum.transAxes, clip_on=False))

ax_sum.text(0.5, 0.82, "THE BOTTOM LINE", color="#ff4444",
            fontsize=14, fontweight="bold", ha="center")

summary = (
    "No single signal makes a review fake — but when multiple signals fire together, "
    "the probability skyrockets.\n"
    "A review that is SHORT + VAGUE + EXTREME SENTIMENT + posted in a BURST is almost "
    "certainly not written by a real guest.\n"
    "The #1 signal in this dataset is REVIEWER BEHAVIOR: users who give nothing but "
    "5-stars or nothing but 1-stars — a telltale sign of bot accounts or paid review farms."
)
ax_sum.text(0.5, 0.42, summary, color="#cccccc", fontsize=11,
            ha="center", va="center", linespacing=1.8, wrap=True)

plt.savefig("output/why_suspicious.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0a0a")
plt.close()
print("Saved: output/why_suspicious.png")
