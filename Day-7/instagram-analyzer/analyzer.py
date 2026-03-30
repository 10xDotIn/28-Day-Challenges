import subprocess, sys

def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

for pkg in ["opencv-python", "pillow", "scikit-learn", "matplotlib", "pandas", "numpy"]:
    try:
        if pkg == "opencv-python":
            import cv2
        elif pkg == "pillow":
            from PIL import Image
        elif pkg == "scikit-learn":
            from sklearn.cluster import KMeans
        elif pkg == "matplotlib":
            import matplotlib
        elif pkg == "pandas":
            import pandas
        elif pkg == "numpy":
            import numpy
    except ImportError:
        print(f"Installing {pkg}...")
        install(pkg)

import os, io, base64, warnings
warnings.filterwarnings("ignore")

import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from PIL import Image
from sklearn.cluster import KMeans

os.makedirs("output", exist_ok=True)

# ─── Load images ──────────────────────────────────────────────────────────────
def load_images():
    images = []
    for platform, folder in [("Amazon", "images/Amazon"), ("Ebay", "images/Ebay")]:
        for fname in sorted(os.listdir(folder)):
            if fname.endswith(".webp"):
                path = os.path.join(folder, fname)
                pil_img = Image.open(path).convert("RGB")
                cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                images.append({"platform": platform, "filename": fname, "path": path,
                                "pil": pil_img, "cv": cv_img})
    return images

# ─── CV Analysis Functions ────────────────────────────────────────────────────

def analyze_sharpness(cv_img):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if lap_var > 80:
        label = "Sharp"
    elif lap_var > 40:
        label = "Soft"
    else:
        label = "Blurry"
    return round(lap_var, 2), label

def analyze_background(cv_img):
    h, w = cv_img.shape[:2]
    border = 10
    top = cv_img[:border, :, :]
    bottom = cv_img[h-border:, :, :]
    left = cv_img[:, :border, :]
    right = cv_img[:, w-border:, :]
    border_pixels = np.concatenate([top.reshape(-1,3), bottom.reshape(-1,3),
                                     left.reshape(-1,3), right.reshape(-1,3)])
    mean_val = border_pixels.mean()
    if mean_val > 240:
        return "White"
    elif mean_val > 200:
        return "Light"
    elif mean_val > 150:
        return "Colored"
    else:
        return "Busy"

def analyze_dominant_colors(pil_img, k=5):
    img_small = pil_img.resize((100, 100))
    pixels = np.array(img_small).reshape(-1, 3).astype(float)
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(pixels)
    labels, counts = np.unique(km.labels_, return_counts=True)
    total = counts.sum()
    colors = []
    for i in np.argsort(-counts):
        rgb = km.cluster_centers_[labels[i]].astype(int)
        hex_code = "#{:02X}{:02X}{:02X}".format(*rgb)
        pct = round(counts[i] / total * 100, 1)
        colors.append({"hex": hex_code, "pct": pct, "rgb": rgb.tolist()})
    return colors

def analyze_color_temperature(pil_img):
    arr = np.array(pil_img).astype(float)
    r_mean = arr[:,:,0].mean()
    b_mean = arr[:,:,2].mean()
    diff = r_mean - b_mean
    if diff > 15:
        return "Warm"
    elif diff < -15:
        return "Cool"
    else:
        return "Neutral"

def analyze_product_coverage(cv_img):
    h, w = cv_img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    rect = (int(w*0.05), int(h*0.05), int(w*0.9), int(h*0.9))
    try:
        cv2.grabCut(cv_img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        fg_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
        coverage = fg_mask.sum() / (h * w) * 100
    except Exception:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        coverage = (thresh > 0).sum() / (h * w) * 100
    return round(coverage, 1)

def analyze_edges(cv_img):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    density = edges.sum() / 255 / (gray.shape[0] * gray.shape[1]) * 100
    if density > 5:
        label = "High"
    elif density > 2:
        label = "Moderate"
    else:
        label = "Low"
    return edges, round(density, 2), label

def analyze_exposure(cv_img):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    mean_val = gray.mean()
    std_val = gray.std()
    if mean_val > 220:
        return "Overexposed"
    elif mean_val < 60:
        return "Underexposed"
    elif std_val < 30:
        return "Uneven"
    else:
        return "Well-lit"

def analyze_mood(cv_img):
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    brightness = hsv[:,:,2].mean()
    saturation = hsv[:,:,1].mean()
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    contrast = gray.std()
    if brightness > 200 and contrast > 50 and saturation < 80:
        return "Premium"
    elif brightness > 150 and contrast > 40:
        return "Professional"
    elif saturation > 100 and contrast > 50:
        return "Energetic"
    elif brightness < 80:
        return "Budget"
    elif contrast < 25:
        return "Minimal"
    else:
        return "Professional"

def analyze_complexity(edge_density):
    score = min(10, max(1, int(edge_density * 2)))
    return score

def analyze_text_overlay(cv_img):
    # Approximate: look for high-contrast rectangular regions
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = gray.shape
    text_area = 0
    for c in contours:
        x, y, cw, ch = cv2.boundingRect(c)
        ar = cw / (ch + 1e-5)
        if 2 < ar < 20 and cw > 30 and ch > 8:
            text_area += cw * ch
    pct = text_area / (h * w) * 100
    if pct < 1:
        return "None"
    elif pct < 5:
        return "Minimal"
    elif pct < 15:
        return "Moderate"
    else:
        return "Heavy"

def analyze_layout(cv_img, text_overlay, background):
    if text_overlay in ("Moderate", "Heavy"):
        return "Product-with-text"
    elif background == "White":
        return "Studio-shot"
    else:
        return "Product-only"

def analyze_thumbnail(cv_img):
    thumb = cv2.resize(cv_img, (150, 150))
    gray = cv2.cvtColor(thumb, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    contrast = gray.std()
    if lap_var > 60 and contrast > 40:
        return "Good"
    elif lap_var > 30 or contrast > 25:
        return "Acceptable"
    else:
        return "Poor"

def analyze_ela(pil_img, path):
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    recompressed = Image.open(buf).convert("RGB")
    orig_arr = np.array(pil_img).astype(float)
    recomp_arr = np.array(recompressed).astype(float)
    diff = np.abs(orig_arr - recomp_arr)
    ela_map = (diff * 10).clip(0, 255).astype(np.uint8)
    max_diff = diff.max()
    mean_diff = diff.mean()
    if mean_diff < 2:
        result = "Authentic"
    elif mean_diff < 8:
        result = "Edited"
    else:
        result = "Heavily-composited"
    return ela_map, result, round(mean_diff, 2)

def analyze_shadow(cv_img):
    """Detect cast shadows on the background behind the product.
    Shadows on white/light backgrounds appear as neutral-gray regions
    significantly darker than the surrounding background."""
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    h, w = cv_img.shape[:2]

    # Rough background mask: areas bright enough to be background (not the dark product)
    bg_mask = (gray > 160).astype(np.uint8)
    bg_pixels = gray[bg_mask == 1]
    if len(bg_pixels) == 0:
        return "None", 0.0

    bg_mean = float(bg_pixels.mean())

    # Shadow pixels sit well below the background mean but aren't product-dark
    shadow_thresh = bg_mean - 30
    if shadow_thresh < 80:
        return "None", 0.0

    # Shadows are chromatically neutral (gray), not colored
    bgr = cv_img.astype(float)
    r, g, b_ch = bgr[:, :, 2], bgr[:, :, 1], bgr[:, :, 0]
    chroma = np.abs(r - g) + np.abs(g - b_ch) + np.abs(r - b_ch)
    neutral_mask = (chroma < 40).astype(np.uint8)

    shadow_mask = (
        (gray < shadow_thresh) &
        (gray > 60) &
        (bg_mask == 1) &
        (neutral_mask == 1)
    ).astype(np.uint8)

    shadow_pct = shadow_mask.sum() / (h * w) * 100

    if shadow_pct < 1.0:
        label = "None"
    elif shadow_pct < 4.0:
        label = "Soft"
    else:
        label = "Hard"

    return label, round(shadow_pct, 2)


def compute_engagement(sharpness_label, exposure, background, coverage, text_overlay, colors, cv_img, shadow="None"):
    score = 0
    if sharpness_label == "Sharp":
        score += 2
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    if gray.std() > 50:
        score += 2
    if background == "White":
        score += 1
    if 40 <= coverage <= 80:
        score += 1
    if exposure == "Well-lit":
        score += 1
    if text_overlay == "None":
        score += 1
    # Colors pop: check saturation variance
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    if hsv[:,:,1].mean() > 60:
        score += 1
    h, w = cv_img.shape[:2]
    if h >= 500 and w >= 500:
        score += 1
    if shadow == "Hard":
        score -= 2
    elif shadow == "Soft":
        score -= 1
    return max(0, min(10, score))

# ─── Run all analysis ─────────────────────────────────────────────────────────

print("Loading images...")
images = load_images()
print(f"Found {len(images)} images ({sum(1 for i in images if i['platform']=='Amazon')} Amazon, {sum(1 for i in images if i['platform']=='Ebay')} eBay)")

results = []
for idx, img_data in enumerate(images):
    fname = img_data["filename"]
    platform = img_data["platform"]
    print(f"  Analyzing [{idx+1}/{len(images)}] {platform}/{fname}...")

    cv_img = img_data["cv"]
    pil_img = img_data["pil"]

    lap_var, sharpness_label = analyze_sharpness(cv_img)
    background = analyze_background(cv_img)
    dom_colors = analyze_dominant_colors(pil_img)
    color_temp = analyze_color_temperature(pil_img)
    coverage = analyze_product_coverage(cv_img)
    edges, edge_density, edge_label = analyze_edges(cv_img)
    exposure = analyze_exposure(cv_img)
    mood = analyze_mood(cv_img)
    complexity = analyze_complexity(edge_density)
    text_overlay = analyze_text_overlay(cv_img)
    layout = analyze_layout(cv_img, text_overlay, background)
    thumbnail = analyze_thumbnail(cv_img)
    ela_map, ela_result, ela_diff = analyze_ela(pil_img, img_data["path"])
    shadow_label, shadow_pct = analyze_shadow(cv_img)
    engagement = compute_engagement(sharpness_label, exposure, background, coverage, text_overlay, dom_colors, cv_img, shadow=shadow_label)

    results.append({
        "platform": platform,
        "filename": fname,
        "path": img_data["path"],
        "pil": pil_img,
        "cv": cv_img,
        "edges": edges,
        "ela_map": ela_map,
        "lap_var": lap_var,
        "sharpness": sharpness_label,
        "background": background,
        "dom_colors": dom_colors,
        "color_temp": color_temp,
        "coverage": coverage,
        "edge_density": edge_density,
        "edge_label": edge_label,
        "exposure": exposure,
        "mood": mood,
        "complexity": complexity,
        "text_overlay": text_overlay,
        "layout": layout,
        "thumbnail": thumbnail,
        "ela_result": ela_result,
        "ela_diff": ela_diff,
        "shadow": shadow_label,
        "shadow_pct": shadow_pct,
        "engagement": engagement,
    })

print("Analysis complete!\n")

# ─── OUTPUT 1: dashboard.html ─────────────────────────────────────────────────
print("Generating dashboard.html...")

def img_to_base64(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()

def score_color(score):
    if score >= 7: return "#4ade80"
    elif score >= 5: return "#facc15"
    else: return "#f87171"

amazon_results = [r for r in results if r["platform"] == "Amazon"]
ebay_results = [r for r in results if r["platform"] == "Ebay"]

def avg(lst, key):
    vals = [r[key] for r in lst]
    return round(sum(vals) / len(vals), 2) if vals else 0

amz_avg = avg(amazon_results, "engagement")
ebay_avg = avg(ebay_results, "engagement")
winner = "Amazon" if amz_avg >= ebay_avg else "eBay"

cards_html = ""
for r in results:
    b64 = img_to_base64(r["pil"])
    colors_html = "".join(
        f'<span style="display:inline-block;width:20px;height:20px;background:{c["hex"]};border-radius:3px;margin:2px;title:{c["hex"]} {c["pct"]}%"></span>'
        for c in r["dom_colors"]
    )
    sc = score_color(r["engagement"])
    cards_html += f"""
    <div class="card" data-platform="{r['platform']}">
      <div class="card-img-wrap">
        <img src="data:image/jpeg;base64,{b64}" alt="{r['filename']}"/>
        <span class="platform-badge {'amz' if r['platform']=='Amazon' else 'ebay'}">{r['platform']}</span>
      </div>
      <div class="card-body">
        <div class="card-title">{r['filename']}</div>
        <div class="engagement-score" style="color:{sc}">&#9733; {r['engagement']}/10</div>
        <table class="signals">
          <tr><td>Sharpness</td><td>{r['sharpness']} ({r['lap_var']})</td></tr>
          <tr><td>Background</td><td>{r['background']}</td></tr>
          <tr><td>Color Temp</td><td>{r['color_temp']}</td></tr>
          <tr><td>Coverage</td><td>{r['coverage']}%</td></tr>
          <tr><td>Edges</td><td>{r['edge_label']} ({r['edge_density']})</td></tr>
          <tr><td>Exposure</td><td>{r['exposure']}</td></tr>
          <tr><td>Mood</td><td>{r['mood']}</td></tr>
          <tr><td>Complexity</td><td>{r['complexity']}/10</td></tr>
          <tr><td>Text Overlay</td><td>{r['text_overlay']}</td></tr>
          <tr><td>Layout</td><td>{r['layout']}</td></tr>
          <tr><td>Thumbnail</td><td>{r['thumbnail']}</td></tr>
          <tr><td>ELA</td><td>{r['ela_result']}</td></tr>
          <tr><td>Shadow</td><td>{r['shadow']} ({r['shadow_pct']}%)</td></tr>
        </table>
        <div class="colors-label">Dominant Colors:</div>
        <div class="colors-row">{colors_html}</div>
      </div>
    </div>"""

rows_html = ""
for r in sorted(results, key=lambda x: -x["engagement"]):
    sc = score_color(r["engagement"])
    rows_html += f"""<tr>
      <td>{r['platform']}</td><td>{r['filename']}</td>
      <td style="color:{sc};font-weight:bold">{r['engagement']}</td>
      <td>{r['sharpness']}</td><td>{r['background']}</td>
      <td>{r['coverage']}%</td><td>{r['exposure']}</td>
      <td>{r['mood']}</td><td>{r['thumbnail']}</td><td>{r['ela_result']}</td>
      <td>{r['shadow']}</td>
    </tr>"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Product Photo Quality Dashboard</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0f0f1a; color: #e2e8f0; font-family: 'Segoe UI', system-ui, sans-serif; }}
  h1 {{ text-align:center; padding: 32px 16px 8px; font-size: 1.8rem; color: #f8fafc; letter-spacing:-0.5px; }}
  h2 {{ font-size: 1.1rem; color: #94a3b8; text-align:center; margin-bottom:24px; }}
  .summary {{ display:flex; gap:20px; justify-content:center; flex-wrap:wrap; margin: 24px auto; max-width:900px; }}
  .sum-card {{ background:#1e1e2e; border-radius:14px; padding:20px 32px; text-align:center; min-width:180px; }}
  .sum-card .label {{ color:#94a3b8; font-size:0.85rem; margin-bottom:6px; }}
  .sum-card .value {{ font-size:2rem; font-weight:700; }}
  .amz-color {{ color:#fb923c; }}
  .ebay-color {{ color:#60a5fa; }}
  .winner-badge {{ background: linear-gradient(135deg,#7c3aed,#4f46e5); border-radius:14px; padding:20px 32px; text-align:center; }}
  .winner-badge .label {{ color:#c4b5fd; font-size:0.85rem; }}
  .winner-badge .value {{ font-size:1.5rem; font-weight:800; color:#fff; }}
  .filter-bar {{ display:flex; justify-content:center; gap:12px; margin:20px; }}
  .filter-btn {{ padding:8px 22px; border-radius:20px; border:2px solid #334155; background:transparent; color:#94a3b8; cursor:pointer; font-size:0.9rem; transition:all 0.2s; }}
  .filter-btn.active, .filter-btn:hover {{ border-color:#6366f1; color:#fff; background:#6366f1; }}
  .grid {{ display:flex; flex-wrap:wrap; gap:20px; justify-content:center; padding:20px; max-width:1400px; margin:auto; }}
  .card {{ background:#1e1e2e; border-radius:16px; overflow:hidden; width:280px; transition:transform 0.2s,box-shadow 0.2s; }}
  .card:hover {{ transform:translateY(-4px); box-shadow:0 8px 32px #0008; }}
  .card-img-wrap {{ position:relative; }}
  .card-img-wrap img {{ width:100%; height:200px; object-fit:cover; display:block; }}
  .platform-badge {{ position:absolute; top:8px; right:8px; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; }}
  .amz {{ background:#fb923c; color:#fff; }}
  .ebay {{ background:#60a5fa; color:#fff; }}
  .card-body {{ padding:14px; }}
  .card-title {{ font-size:0.85rem; color:#94a3b8; margin-bottom:6px; }}
  .engagement-score {{ font-size:1.4rem; font-weight:800; margin-bottom:10px; }}
  .signals {{ width:100%; border-collapse:collapse; font-size:0.78rem; margin-bottom:10px; }}
  .signals td {{ padding:2px 4px; }}
  .signals td:first-child {{ color:#64748b; width:45%; }}
  .signals td:last-child {{ color:#e2e8f0; font-weight:500; }}
  .colors-label {{ font-size:0.75rem; color:#64748b; margin-bottom:4px; }}
  .colors-row {{ display:flex; flex-wrap:wrap; }}
  .table-wrap {{ max-width:1100px; margin:40px auto; padding:0 20px 40px; overflow-x:auto; }}
  .table-wrap h3 {{ color:#94a3b8; margin-bottom:12px; font-size:1rem; }}
  table.scores {{ width:100%; border-collapse:collapse; font-size:0.85rem; background:#1e1e2e; border-radius:12px; overflow:hidden; }}
  table.scores th {{ background:#2d2d44; color:#94a3b8; padding:10px 12px; text-align:left; cursor:pointer; }}
  table.scores td {{ padding:9px 12px; border-bottom:1px solid #2d2d44; }}
  table.scores tr:last-child td {{ border-bottom:none; }}
  table.scores tr:hover td {{ background:#252538; }}
</style>
</head>
<body>
<h1>Product Photo Quality Dashboard</h1>
<h2>Amazon vs eBay — Computer Vision Analysis</h2>

<div class="summary">
  <div class="sum-card">
    <div class="label">Amazon Avg Score</div>
    <div class="value amz-color">{amz_avg}</div>
  </div>
  <div class="sum-card">
    <div class="label">eBay Avg Score</div>
    <div class="value ebay-color">{ebay_avg}</div>
  </div>
  <div class="sum-card">
    <div class="label">Images Analyzed</div>
    <div class="value" style="color:#a78bfa">{len(results)}</div>
  </div>
  <div class="winner-badge">
    <div class="label">Winner</div>
    <div class="value">{'🏆 ' + winner}</div>
  </div>
</div>

<div class="filter-bar">
  <button class="filter-btn active" onclick="filterCards('All')">All</button>
  <button class="filter-btn" onclick="filterCards('Amazon')">Amazon</button>
  <button class="filter-btn" onclick="filterCards('Ebay')">eBay</button>
</div>

<div class="grid" id="grid">
{cards_html}
</div>

<div class="table-wrap">
  <h3>All Images — Sortable Table</h3>
  <table class="scores" id="scoreTable">
    <thead>
      <tr>
        <th onclick="sortTable(0)">Platform</th>
        <th onclick="sortTable(1)">File</th>
        <th onclick="sortTable(2)">Score</th>
        <th onclick="sortTable(3)">Sharpness</th>
        <th onclick="sortTable(4)">Background</th>
        <th onclick="sortTable(5)">Coverage</th>
        <th onclick="sortTable(6)">Exposure</th>
        <th onclick="sortTable(7)">Mood</th>
        <th onclick="sortTable(8)">Thumbnail</th>
        <th onclick="sortTable(9)">ELA</th>
        <th onclick="sortTable(10)">Shadow</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>

<script>
function filterCards(platform) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('.card').forEach(c => {{
    c.style.display = (platform === 'All' || c.dataset.platform === platform) ? '' : 'none';
  }});
}}
function sortTable(col) {{
  const tb = document.getElementById('scoreTable').tBodies[0];
  const rows = Array.from(tb.rows);
  const asc = tb.dataset.sortCol == col && tb.dataset.sortDir === 'asc';
  rows.sort((a, b) => {{
    let av = a.cells[col].textContent.trim();
    let bv = b.cells[col].textContent.trim();
    return isNaN(parseFloat(av)) ? (asc?1:-1)*av.localeCompare(bv) : (asc?1:-1)*(parseFloat(av)-parseFloat(bv));
  }});
  rows.forEach(r => tb.appendChild(r));
  tb.dataset.sortCol = col; tb.dataset.sortDir = asc ? 'desc' : 'asc';
}}
</script>
</body>
</html>"""

with open("output/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("  -> output/dashboard.html done")

# ─── OUTPUT 2: vision_maps.png ────────────────────────────────────────────────
print("Generating vision_maps.png...")

n = len(results)
fig, axes = plt.subplots(n, 3, figsize=(15, n * 4))
fig.patch.set_facecolor("#0f0f1a")

for i, r in enumerate(results):
    row = axes[i] if n > 1 else axes
    # Original
    row[0].imshow(r["pil"])
    row[0].set_title(f"{r['platform']}/{r['filename']}", color="#e2e8f0", fontsize=8, pad=4)
    row[0].set_xlabel("Original", color="#94a3b8", fontsize=7)
    row[0].set_facecolor("#1e1e2e")
    # Canny edges
    row[1].imshow(r["edges"], cmap="gray")
    row[1].set_title("Canny Edges", color="#94a3b8", fontsize=8, pad=4)
    row[1].set_xlabel(f"Edge density: {r['edge_density']}%", color="#94a3b8", fontsize=7)
    row[1].set_facecolor("#0f0f1a")
    # ELA heatmap
    row[2].imshow(r["ela_map"])
    row[2].set_title("ELA Heatmap", color="#94a3b8", fontsize=8, pad=4)
    row[2].set_xlabel(f"Result: {r['ela_result']}", color="#94a3b8", fontsize=7)
    row[2].set_facecolor("#0f0f1a")
    for ax in row:
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor("#334155")

plt.suptitle("Vision Maps: What the Computer Sees", color="#f8fafc", fontsize=14, y=1.002)
plt.tight_layout(pad=0.5)
plt.savefig("output/vision_maps.png", dpi=100, bbox_inches="tight", facecolor="#0f0f1a")
plt.close()
print("  -> output/vision_maps.png done")

# ─── OUTPUT 3: radar_charts.png ──────────────────────────────────────────────
print("Generating radar_charts.png...")

def radar_values(r):
    sharpness_norm = min(10, r["lap_var"] / 20)
    bg_map = {"White": 10, "Light": 7, "Colored": 4, "Busy": 1}
    background_norm = bg_map.get(r["background"], 4)
    ideal = 60
    cov_norm = max(0, 10 - abs(r["coverage"] - ideal) / ideal * 10)
    exp_map = {"Well-lit": 10, "Uneven": 5, "Overexposed": 2, "Underexposed": 2}
    exposure_norm = exp_map.get(r["exposure"], 5)
    text_map = {"None": 10, "Minimal": 7, "Moderate": 4, "Heavy": 1}
    cleanliness = text_map.get(r["text_overlay"], 5)
    detail_norm = min(10, r["edge_density"] * 2)
    return [sharpness_norm, background_norm, cov_norm, exposure_norm, cleanliness, detail_norm]

categories = ["Sharpness", "Background", "Coverage", "Exposure", "Cleanliness", "Detail"]
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

cols = 4
rows_count = (len(results) + cols - 1) // cols
fig, axes = plt.subplots(rows_count, cols, subplot_kw=dict(polar=True),
                          figsize=(cols * 3.5, rows_count * 3.5))
fig.patch.set_facecolor("#0f0f1a")
axes_flat = axes.flatten() if rows_count > 1 else (axes if cols > 1 else [axes])

for i, r in enumerate(results):
    ax = axes_flat[i]
    ax.set_facecolor("#1e1e2e")
    vals = radar_values(r)
    vals_plot = vals + vals[:1]
    color = "#fb923c" if r["platform"] == "Amazon" else "#60a5fa"
    ax.plot(angles, vals_plot, color=color, linewidth=2)
    ax.fill(angles, vals_plot, color=color, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=6, color="#94a3b8")
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2","4","6","8","10"], size=5, color="#475569")
    ax.set_ylim(0, 10)
    ax.tick_params(colors="#475569")
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")
    ax.grid(color="#334155", linewidth=0.5)
    sc_color = score_color(r["engagement"])
    ax.set_title(f"{r['filename']}\nScore: {r['engagement']}/10", size=7,
                  color=sc_color, pad=10, fontweight="bold")

for j in range(i + 1, len(axes_flat)):
    axes_flat[j].set_visible(False)

amz_patch = mpatches.Patch(color="#fb923c", label="Amazon")
ebay_patch = mpatches.Patch(color="#60a5fa", label="eBay")
fig.legend(handles=[amz_patch, ebay_patch], loc="lower right", fontsize=9,
           facecolor="#1e1e2e", edgecolor="#334155", labelcolor="#e2e8f0")
plt.suptitle("Radar Charts — CV Signal Analysis per Image", color="#f8fafc", fontsize=13, y=1.01)
plt.tight_layout(pad=1.0)
plt.savefig("output/radar_charts.png", dpi=100, bbox_inches="tight", facecolor="#0f0f1a")
plt.close()
print("  -> output/radar_charts.png done")

# ─── OUTPUT 4: platform_scorecard.png ────────────────────────────────────────
print("Generating platform_scorecard.png...")

def pct(lst, condition):
    return round(sum(1 for r in lst if condition(r)) / len(lst) * 100, 1) if lst else 0

metrics = [
    ("Avg Engagement Score", amz_avg, ebay_avg),
    ("% White Background",
     pct(amazon_results, lambda r: r["background"]=="White"),
     pct(ebay_results, lambda r: r["background"]=="White")),
    ("% Well-lit",
     pct(amazon_results, lambda r: r["exposure"]=="Well-lit"),
     pct(ebay_results, lambda r: r["exposure"]=="Well-lit")),
    ("% Good Thumbnails",
     pct(amazon_results, lambda r: r["thumbnail"]=="Good"),
     pct(ebay_results, lambda r: r["thumbnail"]=="Good")),
    ("% No Text Overlay",
     pct(amazon_results, lambda r: r["text_overlay"]=="None"),
     pct(ebay_results, lambda r: r["text_overlay"]=="None")),
    ("Avg Product Coverage %",
     avg(amazon_results, "coverage"),
     avg(ebay_results, "coverage")),
    ("% Authentic (ELA)",
     pct(amazon_results, lambda r: r["ela_result"]=="Authentic"),
     pct(ebay_results, lambda r: r["ela_result"]=="Authentic")),
]

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor("#0f0f1a")
ax.set_facecolor("#0f0f1a")

y_pos = np.arange(len(metrics))
bar_h = 0.35
amz_vals = [m[1] for m in metrics]
ebay_vals = [m[2] for m in metrics]
max_val = max(max(amz_vals), max(ebay_vals), 10) * 1.15

bars1 = ax.barh(y_pos + bar_h/2, amz_vals, bar_h, color="#fb923c", label="Amazon", alpha=0.9)
bars2 = ax.barh(y_pos - bar_h/2, ebay_vals, bar_h, color="#60a5fa", label="eBay", alpha=0.9)

for bar, val in zip(bars1, amz_vals):
    ax.text(bar.get_width() + max_val*0.01, bar.get_y() + bar.get_height()/2,
            f"{val}", va="center", ha="left", color="#fb923c", fontsize=9, fontweight="bold")
for bar, val in zip(bars2, ebay_vals):
    ax.text(bar.get_width() + max_val*0.01, bar.get_y() + bar.get_height()/2,
            f"{val}", va="center", ha="left", color="#60a5fa", fontsize=9, fontweight="bold")

ax.set_yticks(y_pos)
ax.set_yticklabels([m[0] for m in metrics], color="#e2e8f0", fontsize=10)
ax.set_xlim(0, max_val)
ax.set_xlabel("Score / Percentage", color="#94a3b8", fontsize=9)
ax.tick_params(colors="#475569")
for spine in ax.spines.values():
    spine.set_edgecolor("#334155")
ax.grid(axis="x", color="#2d2d44", linewidth=0.5, alpha=0.7)
ax.legend(facecolor="#1e1e2e", edgecolor="#334155", labelcolor="#e2e8f0", fontsize=10)

winner_color = "#fb923c" if winner == "Amazon" else "#60a5fa"
ax.text(max_val/2, -1.2, f"Winner: {winner} 🏆",
        ha="center", va="center", fontsize=16, fontweight="bold",
        color=winner_color,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#1e1e2e", edgecolor=winner_color, linewidth=2))

plt.title("Platform Scorecard: Amazon vs eBay", color="#f8fafc", fontsize=14, pad=20)
plt.tight_layout(pad=2.0)
plt.savefig("output/platform_scorecard.png", dpi=100, bbox_inches="tight", facecolor="#0f0f1a")
plt.close()
print("  -> output/platform_scorecard.png done")

# ─── OUTPUT 5: listings.md ────────────────────────────────────────────────────
print("Generating listings.md...")

top5 = sorted(results, key=lambda x: -x["engagement"])[:5]

def describe_product(r):
    pil = r["pil"]
    arr = np.array(pil)
    h, w = arr.shape[:2]
    bg = r["background"]
    mood = r["mood"]
    colors = r["dom_colors"][:2]
    color_desc = f"{colors[0]['hex']} ({colors[0]['pct']}%)" if colors else "N/A"
    coverage = r["coverage"]
    exposure = r["exposure"]

    # Generate title
    platform = r["platform"]
    idx = r["filename"].replace(".webp","").split("_")[-1]
    title = f"{platform} Product #{idx} — {mood} Style, {bg} Background"
    if len(title) > 80:
        title = title[:77] + "..."

    bullets = [
        f"Dominant color scheme: {color_desc} — creates a {r['color_temp'].lower()} visual tone",
        f"Product fills approximately {coverage}% of frame with a {bg.lower()} background — {exposure.lower()} lighting conditions",
        f"Image exhibits {r['edge_label'].lower()} edge detail and a {mood.lower()} aesthetic mood, suitable for {platform} listings",
    ]
    return title, bullets

md_lines = ["# Top 5 Product Listings\n",
            f"*Generated by Product Photo Analyzer — {len(results)} images analyzed*\n",
            "---\n"]

for rank, r in enumerate(top5, 1):
    title, bullets = describe_product(r)
    md_lines.append(f"## {rank}. {title}\n")
    md_lines.append(f"**Platform:** {r['platform']} | **File:** `{r['filename']}` | **Engagement Score:** {r['engagement']}/10\n")
    for b in bullets:
        md_lines.append(f"- {b}")
    md_lines.append("")
    md_lines.append("")

with open("output/listings.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))
print("  -> output/listings.md done")

# ─── Final Summary ────────────────────────────────────────────────────────────
best = max(results, key=lambda r: r["engagement"])
worst = min(results, key=lambda r: r["engagement"])

print("\n" + "="*60)
print("FINAL VERDICT")
print("="*60)
print(f"  Winner:     {winner}")
print(f"  Best photo: {best['platform']}/{best['filename']} (score {best['engagement']}/10)")
print(f"  Worst photo:{worst['platform']}/{worst['filename']} (score {worst['engagement']}/10)")
print(f"  Amazon avg: {amz_avg}/10  |  eBay avg: {ebay_avg}/10")
print()
print("Key Recommendation:")
if winner == "Amazon":
    print("  Amazon photos are consistently sharper, better lit, and use cleaner")
    print("  white backgrounds — optimized for e-commerce conversion. eBay listings")
    print("  should adopt white/neutral backgrounds and remove text overlays.")
else:
    print("  eBay photos outperform Amazon in this dataset. Amazon should improve")
    print("  product coverage (aim for 40-80% of frame) and reduce visual clutter.")
print("="*60)
print("\nAll outputs saved to output/")
