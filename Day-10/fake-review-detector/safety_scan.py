import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import base64, re, warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("data/hotel_reviews.csv", low_memory=False)
df["rating"]   = pd.to_numeric(df["reviews.rating"], errors="coerce")
df["text"]     = df["reviews.text"].fillna("").astype(str)
df["hotel"]    = df["name"].fillna("Unknown").astype(str)
df["user"]     = df["reviews.username"].fillna("anonymous").astype(str)
df["date"]     = pd.to_datetime(df["reviews.date"], errors="coerce")
df["province"] = df["province"].fillna("").astype(str)
df["city"]     = df["city"].fillna("").astype(str)
df["address"]  = df["address"].fillna("").astype(str)
df["postalCode"]= df["postalCode"].fillna("").astype(str)

# ── California hotels from filtered list ──────────────────────────────────────
CA_TOP10 = [
    "Anaheim Marriott Suites",
    "Best Western of Long Beach",
    "Holiday Inn Express San Clemente",
    "Hotel Valencia Santana Row",
    "Chelsea Inn",
    "Wine Valley Lodge",
    "Simpson House Inn",
    "Residence Inn By Marriott Irvine John Wayne Airport",
    "Best Western Plus San Marcos Inn",
    "Hotel Aura Sfo",
]

# ── Safety concern keyword categories ─────────────────────────────────────────
SAFETY_SIGNALS = {
    "Hidden Camera": [
        r"hidden camera", r"spy cam", r"camera in room", r"camera in bathroom",
        r"recording device", r"surveillance", r"watching us", r"being watched",
        r"peephole", r"two.way mirror", r"found a camera", r"hidden device",
        r"secret camera", r"privacy violation"
    ],
    "Theft / Robbery": [
        r"stolen", r"robbery", r"robbed", r"burglar", r"theft", r"missing money",
        r"items missing", r"valuables gone", r"broke into", r"break.in",
        r"pickpocket", r"stole my"
    ],
    "Drugs / Crime": [
        r"drug deal", r"drug activity", r"prostitut", r"suspicious activity",
        r"criminal", r"crime scene", r"police called", r"arrested",
        r"sketchy", r"shady people", r"dangerous area", r"gang"
    ],
    "Hygiene / Health": [
        r"bed bug", r"cockroach", r"roach", r"mold", r"mould", r"rat", r"mice",
        r"mouse", r"infest", r"dirty needle", r"biohazard", r"health department",
        r"unsanitary", r"feces", r"urine smell", r"vomit"
    ],
    "Physical Safety": [
        r"unsafe", r"broken lock", r"no lock", r"door won.t lock", r"felt unsafe",
        r"threatened", r"harassed", r"assault", r"attacked", r"stranger entered",
        r"someone in room", r"intruder", r"no security", r"dark parking"
    ],
    "Scam / Fraud": [
        r"scam", r"fraud", r"rip.?off", r"overcharged", r"fake receipt",
        r"double charge", r"unauthorized charge", r"credit card fraud",
        r"bait and switch", r"false advertising", r"misleading"
    ],
}

# ── Scan ALL reviews (not just CA top 10) then filter ─────────────────────────
def find_signals(text):
    t = text.lower()
    found = {}
    for category, patterns in SAFETY_SIGNALS.items():
        hits = []
        for pat in patterns:
            matches = re.findall(pat, t)
            if matches:
                hits.extend(matches)
        if hits:
            found[category] = list(set(hits))
    return found

print("Scanning all reviews for safety signals...")
df["safety_hits"] = df["text"].apply(find_signals)
df["safety_flags"] = df["safety_hits"].apply(lambda x: list(x.keys()))
df["safety_count"] = df["safety_flags"].apply(len)

flagged = df[df["safety_count"] > 0].copy()
print(f"Reviews with safety concerns: {len(flagged)}")
print(f"Signal breakdown:")
for cat in SAFETY_SIGNALS:
    n = flagged["safety_flags"].apply(lambda f: cat in f).sum()
    print(f"  {cat}: {n}")

# ── Filter to CA top-10 hotels ─────────────────────────────────────────────────
ca_flagged = flagged[flagged["hotel"].isin(CA_TOP10)].copy()
print(f"\nSafety-flagged reviews in CA top-10 hotels: {len(ca_flagged)}")
print(ca_flagged[["hotel","user","rating","safety_flags","text"]].head(20).to_string())

# ── Hidden camera specifically (highest severity) ──────────────────────────────
hidden_cam = flagged[flagged["safety_flags"].apply(lambda f: "Hidden Camera" in f)]
print(f"\nHidden camera mentions (entire dataset): {len(hidden_cam)}")
if len(hidden_cam) > 0:
    print(hidden_cam[["hotel","city","text"]].to_string())

# ── Per hotel safety summary ───────────────────────────────────────────────────
hotel_safety = {}
for h in CA_TOP10:
    sub = flagged[flagged["hotel"] == h]
    all_flags = []
    for flags in sub["safety_flags"]:
        all_flags.extend(flags)
    hotel_safety[h] = {
        "flagged_reviews": len(sub),
        "total_reviews": len(df[df["hotel"] == h]),
        "categories": list(set(all_flags)),
        "reviews": sub[["user","rating","safety_flags","text","date"]].to_dict("records")
    }

# ── PNG ────────────────────────────────────────────────────────────────────────
CAT_COLORS = {
    "Hidden Camera":  "#cc0000",
    "Theft / Robbery":"#ff4444",
    "Drugs / Crime":  "#ff8800",
    "Physical Safety":"#ffa94d",
    "Scam / Fraud":   "#ffd700",
    "Hygiene / Health":"#cc00cc",
}

fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.patch.set_facecolor("#0a0a0a")

# Left — safety flag count per hotel
ax1 = axes[0]
ax1.set_facecolor("#111")
hotels_short = [h[:28] for h in CA_TOP10]
flag_counts  = [hotel_safety[h]["flagged_reviews"] for h in CA_TOP10]
colors_h     = ["#cc0000" if c > 5 else "#ff8800" if c > 2 else "#ffa94d" if c > 0 else "#00cc66"
                for c in flag_counts]
bars = ax1.barh(range(len(CA_TOP10)), flag_counts, color=colors_h, height=0.6)
ax1.set_yticks(range(len(CA_TOP10)))
ax1.set_yticklabels(hotels_short, color="white", fontsize=8)
ax1.set_xlabel("Safety-Flagged Reviews", color="white")
ax1.set_title("Safety Concerns per Hotel\n(CA Top 10)", color="white",
              fontsize=12, fontweight="bold")
ax1.tick_params(colors="white")
for spine in ax1.spines.values(): spine.set_edgecolor("#333")
for i, (h, c) in enumerate(zip(CA_TOP10, flag_counts)):
    cats = hotel_safety[h]["categories"]
    label = f"{c}  " + (", ".join(cats[:2]) if cats else "✅ Clean")
    ax1.text(c + 0.1, i, label, va="center", color="#ccc", fontsize=7.5)
ax1.invert_yaxis()

# Right — signal category breakdown across all flagged CA reviews
ax2 = axes[1]
ax2.set_facecolor("#111")
cat_totals = {}
for h in CA_TOP10:
    for r in hotel_safety[h]["reviews"]:
        for f in r["safety_flags"]:
            cat_totals[f] = cat_totals.get(f, 0) + 1

if cat_totals:
    cats_sorted = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
    cats_names  = [c[0] for c in cats_sorted]
    cats_vals   = [c[1] for c in cats_sorted]
    cats_colors = [CAT_COLORS.get(c, "#888") for c in cats_names]
    ax2.barh(range(len(cats_names)), cats_vals, color=cats_colors, height=0.5)
    ax2.set_yticks(range(len(cats_names)))
    ax2.set_yticklabels(cats_names, color="white", fontsize=10)
    ax2.set_xlabel("Occurrences", color="white")
    ax2.set_title("Safety Signal Categories\n(CA Top 10 Hotels)", color="white",
                  fontsize=12, fontweight="bold")
    ax2.tick_params(colors="white")
    for spine in ax2.spines.values(): spine.set_edgecolor("#333")
    for i, v in enumerate(cats_vals):
        ax2.text(v + 0.1, i, str(v), va="center", color="white", fontsize=9)
    ax2.invert_yaxis()
else:
    ax2.text(0.5, 0.5, "✅ No safety signals\nfound in CA top-10 hotels",
             color="#00cc66", fontsize=14, ha="center", va="center",
             transform=ax2.transAxes)
    ax2.tick_params(colors="white")
    for spine in ax2.spines.values(): spine.set_edgecolor("#333")

fig.suptitle("Safety Signal Scan — California Hotel Recommendations",
             color="white", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("output/ca_safety_scan.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0a0a")
plt.close()
print("Saved: ca_safety_scan.png")

# ── HTML ───────────────────────────────────────────────────────────────────────
with open("output/ca_safety_scan.png","rb") as f:
    chart_b64 = base64.b64encode(f.read()).decode()

SEVERITY = {
    "Hidden Camera":   ("🔴 CRITICAL",  "#cc0000"),
    "Theft / Robbery": ("🔴 HIGH",      "#ff4444"),
    "Drugs / Crime":   ("🟠 HIGH",      "#ff8800"),
    "Physical Safety": ("🟠 MEDIUM",    "#ffa94d"),
    "Scam / Fraud":    ("🟡 MEDIUM",    "#ffd700"),
    "Hygiene / Health":("🟣 MEDIUM",    "#cc00cc"),
}

def build_hotel_safety_cards():
    html = ""
    for h in CA_TOP10:
        info  = hotel_safety[h]
        total = info["total_reviews"]
        flagged_n = info["flagged_reviews"]
        cats  = info["categories"]
        reviews = info["reviews"]

        if flagged_n == 0:
            status_col = "#00cc66"
            status_txt = "✅ CLEAN — No safety concerns found in any review"
            border_col = "#1a3a1a"
        elif "Hidden Camera" in cats:
            status_col = "#cc0000"
            status_txt = "🚨 CRITICAL — Hidden camera / surveillance mentioned"
            border_col = "#cc0000"
        elif any(c in cats for c in ["Theft / Robbery","Drugs / Crime"]):
            status_col = "#ff4444"
            status_txt = "⚠️ HIGH ALERT — Serious safety concerns in reviews"
            border_col = "#ff4444"
        else:
            status_col = "#ff8800"
            status_txt = f"⚠️ CAUTION — {flagged_n} review(s) mention safety concerns"
            border_col = "#ff8800"

        cat_badges = "".join(
            f'<span style="background:{SEVERITY.get(c,("","#888"))[1]};color:#fff;'
            f'border-radius:5px;padding:3px 10px;font-size:0.78rem;font-weight:bold;'
            f'margin:3px 3px 3px 0;display:inline-block">'
            f'{SEVERITY.get(c,("⚪ LOW","#888"))[0]} {c}</span>'
            for c in cats
        ) or ""

        review_cards = ""
        for rev in reviews[:5]:
            t   = str(rev["text"])[:350].replace("<","&lt;").replace(">","&gt;")
            fl  = rev["safety_flags"]
            kw_html = "".join(
                f'<span style="background:{CAT_COLORS.get(f,"#888")};color:#fff;'
                f'border-radius:4px;padding:1px 7px;font-size:0.73rem;margin-right:4px">{f}</span>'
                for f in fl
            )
            dt = str(rev["date"])[:10] if rev["date"] else "Unknown"
            review_cards += f"""
<div style="background:#0d0d0d;border-radius:8px;padding:12px;margin-bottom:10px;
            border-left:3px solid {CAT_COLORS.get(fl[0],'#888') if fl else '#888'}">
  <div style="display:flex;gap:10px;align-items:center;margin-bottom:6px;flex-wrap:wrap">
    <span style="color:#ff8888;font-size:0.85rem;font-weight:bold">👤 {rev['user']}</span>
    <span style="color:#ffd700;font-size:0.82rem">★ {rev['rating']}</span>
    <span style="color:#666;font-size:0.78rem">📅 {dt}</span>
    {kw_html}
  </div>
  <div style="color:#bbb;font-size:0.84rem;font-style:italic;line-height:1.6">"{t}..."</div>
</div>"""

        if not review_cards:
            review_cards = '<div style="color:#00cc66;font-size:0.88rem;padding:10px">✅ No concerning reviews found.</div>'

        html += f"""
<div style="background:#111;border:1px solid {border_col};border-radius:14px;
            margin-bottom:28px;overflow:hidden">
  <div style="background:{status_col}22;border-bottom:1px solid {border_col};
              padding:16px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
    <div>
      <div style="font-size:1.05rem;font-weight:bold;color:#fff;margin-bottom:4px">{h}</div>
      <div style="font-size:0.88rem;color:{status_col};font-weight:bold">{status_txt}</div>
    </div>
    <div style="text-align:right">
      <div style="font-size:1.4rem;font-weight:bold;color:{status_col}">{flagged_n}</div>
      <div style="font-size:0.75rem;color:#888">of {total} reviews flagged</div>
    </div>
  </div>
  <div style="padding:18px">
    {'<div style="margin-bottom:14px">' + cat_badges + '</div>' if cat_badges else ''}
    <div style="color:#888;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;
                margin-bottom:10px">Flagged review excerpts:</div>
    {review_cards}
  </div>
</div>"""
    return html

# Hidden camera section (entire dataset)
def hidden_cam_section():
    hc = flagged[flagged["safety_flags"].apply(lambda f: "Hidden Camera" in f)]
    if len(hc) == 0:
        return """<div style="background:#0d1a0d;border:1px solid #1a4a1a;border-radius:10px;
                              padding:24px;text-align:center;color:#00cc66;font-size:1.1rem">
                    ✅ No hidden camera mentions found anywhere in the entire dataset of 35,912 reviews.
                  </div>"""
    rows = ""
    for _, r in hc.iterrows():
        t = str(r["text"])[:400].replace("<","&lt;").replace(">","&gt;")
        rows += f"""
<div style="background:#1a0000;border:1px solid #cc0000;border-radius:10px;padding:16px;margin-bottom:14px">
  <div style="display:flex;gap:12px;margin-bottom:8px;flex-wrap:wrap">
    <span style="color:#ff4444;font-weight:bold;font-size:1rem">🏨 {r['hotel']}</span>
    <span style="color:#888">{r['city']}</span>
    <span style="color:#ffd700">★ {r['rating']}</span>
    <span style="color:#888">👤 {r['user']}</span>
  </div>
  <div style="color:#ffcccc;font-style:italic;line-height:1.6">"{t}..."</div>
</div>"""
    return rows

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hotel Safety Scan — CA Recommendations</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0a0a0a;color:#e0e0e0;font-family:'Segoe UI',sans-serif;padding:30px;max-width:960px;margin:0 auto}}
  .page-title{{color:#ff4444;font-size:1.9rem;font-weight:bold;text-transform:uppercase;
               letter-spacing:3px;text-align:center;margin-bottom:6px}}
  .page-sub  {{color:#888;text-align:center;margin-bottom:28px;font-size:0.92rem}}
  .section-title{{color:#ff8800;font-size:1.1rem;font-weight:bold;text-transform:uppercase;
                  letter-spacing:2px;margin:30px 0 14px;padding-bottom:6px;
                  border-bottom:1px solid #222}}
  .chart-wrap{{text-align:center;margin-bottom:28px}}
  .chart-wrap img{{max-width:100%;border-radius:12px;border:1px solid #222}}
  .info-box{{background:#0d0d1a;border:1px solid #333;border-radius:10px;
             padding:16px 20px;margin-bottom:24px;color:#aaa;font-size:0.88rem;line-height:1.7}}
  .info-box strong{{color:#4dabf7}}
</style>
</head>
<body>

<div class="page-title">🔍 Hotel Safety Scan</div>
<div class="page-sub">Scanning all reviews for hidden cameras, theft, crime, hygiene & safety incidents</div>

<div class="info-box">
  <strong>How this works:</strong> Every review was scanned using 40+ keyword patterns across 6 safety categories.
  This does NOT replace official reporting — it surfaces what guests have written about their experiences.
  A flagged review means a guest <em>mentioned</em> the concern; it doesn't confirm an incident occurred.
  Use this as a starting point for your own research before booking.
</div>

<div class="chart-wrap">
  <img src="data:image/png;base64,{chart_b64}" alt="Safety scan chart">
</div>

<div class="section-title">📷 Hidden Camera Reports — Entire Dataset</div>
{hidden_cam_section()}

<div class="section-title">🏨 Safety Report — CA Top 10 Hotels</div>
{build_hotel_safety_cards()}

</body>
</html>"""

with open("output/ca_safety_report.html","w",encoding="utf-8") as f:
    f.write(html)
print("Saved: ca_safety_report.html")
