# Product Photo Analyzer

> You are a product photography analyst and computer vision expert.
> Analyze every product photo in `images/` folder and tell me which platform takes better photos.

## Setup
- Images are in `images/Amazon/` (11 photos) and `images/Ebay/` (7 photos)
- All images are .webp format — use Pillow to load them
- Save all results in `output/` folder
- Install any missing packages automatically: opencv-python pillow scikit-learn matplotlib pandas numpy

## What to Analyze on Every Image

Run ALL of these checks on every image:

**Sharpness** — Laplacian variance. Sharp (>80) / Soft (40-80) / Blurry (<40)

**Background** — Sample border pixels. White (>240) / Light (>200) / Colored (>150) / Busy

**Dominant Colors** — K-Means clustering (k=5). Return hex codes + percentages

**Color Temperature** — Warm / Cool / Neutral based on RGB balance

**Product Coverage** — GrabCut segmentation. What % of frame does product fill? Ideal: 40-80%

**Edge Detail** — Canny edge detection. High / Moderate / Low detail

**Exposure** — RGB histogram. Well-lit / Overexposed / Underexposed / Uneven

**Mood** — Combine brightness + contrast + saturation. Premium / Professional / Budget / Minimal / Energetic / Cluttered

**Complexity** — Score 1-10 based on edge density

**Text Overlay** — Detect text/graphics. None / Minimal / Moderate / Heavy

**Layout** — Product-only / Product-with-text / Studio-shot

**Thumbnail Simulation** — Resize to 150x150px. Re-check sharpness and contrast. Score: Good / Acceptable / Poor

**Fake Photo Detection (ELA)** — Error Level Analysis. Save at 95% JPEG, compare difference. Authentic / Edited / Heavily-composited

**Engagement Score** — Score 1-10:
- Sharp: +2, High contrast: +2, White bg: +1, Good coverage: +1, Well-lit: +1, No text overlay: +1, Colors pop: +1, High res: +1

## Output Files — IMPORTANT: Follow Exactly

### 1. `output/dashboard.html`
A self-contained interactive HTML dashboard. Must open in any browser. Include:
- A header: "Product Photo Quality Dashboard — Amazon vs eBay"
- For each image: show the image (use base64 embedded), engagement score, all CV signals, mood, thumbnail readability, ELA result
- Make the images filterable by platform (Amazon / eBay / All)
- A sortable table of all scores
- Color-coded scores: green (7+), yellow (5-6), red (<5)
- Platform comparison summary at the top with average scores
- Use modern CSS — dark theme, rounded cards, clean typography
- All in ONE html file — no external dependencies

### 2. `output/vision_maps.png`
For each image, show 3 versions side by side:
- Original photo
- Canny edge detection output (white edges on black — this is what the computer "sees")
- ELA heatmap (amplified error levels — shows editing/compression patterns)
Arrange as rows: one row per image, 3 columns (Original | Edges | ELA)
Add image filename and platform label on each row
This is the "what the computer sees" visualization

### 3. `output/radar_charts.png`
One radar/spider chart per image showing 6 axes:
- Sharpness (normalized 0-10)
- Background (white=10, light=7, colored=4, busy=1)
- Coverage (how close to ideal 60%, normalized 0-10)
- Exposure (well-lit=10, uneven=5, over/underexposed=2)
- Cleanliness (no text=10, minimal=7, moderate=4, heavy=1)
- Detail (edge density normalized 0-10)
Color: orange for Amazon, blue for eBay
Arrange in a grid — 4 per row
Each chart labeled with filename and engagement score

### 4. `output/platform_scorecard.png`
A single infographic-style comparison:
- Two columns: Amazon vs eBay
- Horizontal bar charts comparing:
  - Average engagement score
  - % with white backgrounds
  - % well-lit
  - % good thumbnails
  - % no text overlays
  - Average product coverage
  - % authentic (ELA)
- Color: orange bars for Amazon, blue bars for eBay
- Winner badge at the bottom
- Clean, professional look — like a consulting slide

### 5. `output/listings.md`
For the top 5 scoring images, write:
- Product title (under 80 chars)
- 3 bullet points describing the product
- Based ONLY on what is visible in the photo
- Format as a clean markdown document

## Rules
1. Read this file first
2. Install packages silently
3. Write and run analyzer.py — fix any errors yourself
4. Produce all 5 output files
5. End with: which platform wins, best photo, worst photo, one key recommendation
