# Computer Vision with Claude Code
### 10x.in Live Workshop

---

## What is Computer Vision?

Teaching a computer to extract meaning from pixels.

**Old way:**
- Months of data collection
- Custom neural network training
- Deep ML knowledge required
- Expensive GPU servers

**Today:**
- A folder of images
- A clear CLAUDE.md
- Plain English prompts
- 90 minutes

---

## What We Are Building

**Product Image Quality Analyzer**

### Layer 1 — Quality Checks
- Blur detection
- Resolution check
- Aspect ratio validation
- White background check

### Layer 2 — Computer Vision
- K-Means color clustering → dominant colors
- Canny edge detection → product complexity
- GrabCut segmentation → product coverage in frame
- Histogram analysis → exposure check
- Claude Vision API → watermarks, centering, presentation

---

## Project Structure
```
product-qa/
├── CLAUDE.md        ← Claude Code's brain
├── images/          ← your product images
└── output/          ← results appear here
```

---

## What Makes a Good CLAUDE.md

| Element | What it does |
|---|---|
| Role | Tells Claude Code what it IS |
| Tasks | Tells Claude Code what to DO |
| Output format | Tells Claude Code what to PRODUCE |
| Rules | Tells Claude Code how to BEHAVE |

> The clearer your CLAUDE.md,
> the better Claude Code executes.

---

## The CV Checks — How They Work

### Blur Detection
Uses **Laplacian variance** — measures how sharp the edges are.
- High score = sharp image ✓
- Low score = blurry image ✗
- Threshold: score must be above 80

### Color Analysis
Uses **K-Means clustering** — groups all pixels by color similarity.
- Finds the 5 most dominant colors
- Returns hex codes + percentage of image
- Detects warm / cool / neutral tone

### Edge Detection
Uses **Canny algorithm** — traces boundaries between regions.
- More edges = more product detail
- Fewer edges = simple or blurry product
- Output is the white-lines-on-black image you'll see

### Product Coverage
Uses **GrabCut segmentation** — separates product from background.
- Measures what % of frame the product fills
- Below 30% = product too small, flag it

### Exposure Check
Uses **RGB histogram** — counts pixels by brightness.
- Too many bright pixels = overexposed
- Too many dark pixels = underexposed

---

## The 10 Prompts

---

**01 — Kickoff**
```
Read CLAUDE.md and run the full analysis on all images in 
images/ folder. Build the analyzer, run it, fix any errors, 
and show me the results.
```
One sentence. Entire pipeline. Watch what happens.

---

**02 — Visual Explanation**
```
Show me the summary_grid.png you created. Explain what the 
edge maps are telling us about each product.
```
The white lines are what the computer sees.

---

**03 — Color Intelligence**
```
Which product has the most unique color profile? Which two 
products are most visually similar based on their dominant 
colors?
```
K-Means clustering turned into business insight.

---

**04 — Product Coverage**
```
Which images have bad product coverage — where the product 
is too small in the frame? What should the photographer 
do differently?
```
Segmentation data → photography feedback.

---

**05 — The Ranking**
```
Based on all the CV analysis, rank every image from most 
e-commerce ready to least. Give me reasons for each ranking.
```
From data → to judgment → to decision.

---

**06 — Extend the Pipeline**
```
Add one more analysis — detect if the product casts a shadow. 
Update the analyzer, rerun on all images, update the CSV.
```
New feature. One sentence. Watch the script rewrite itself.

---

**07 — Business Translation**
```
Translate the report.csv into a plain English memo I could 
send to a product photography team. Tell them exactly what 
to fix and why it matters for sales.
```
CV data → human communication → team action.

---

**08 — Brief the Photographer**
```
Which single image needs the most work? Give me a detailed 
fix list — step by step — like you're briefing a 
photographer before a reshoot.
```
Domain reasoning on top of analysis.

---

**09 — Pattern Recognition**
```
Are there any patterns in the images that passed vs failed? 
What do the passing images have in common that the failing 
ones don't?
```
10 results → 1 pattern → your quality standard.

---

**10 — Make It Live**
```
Rewrite the analyzer so it watches the images/ folder for 
new files and automatically checks each new image the moment 
it's dropped in. Show me a pass/fail result in the terminal 
in real time.
```
A script becomes a product.

---

## What You Built Today

| Before this workshop | After this workshop |
|---|---|
| CV felt like a PhD topic | CV is a prompt away |
| Needed to write Python | Directed Claude Code in English |
| Static script | Live monitoring system |
| Raw CSV data | Business-ready insights |

---

## The Real Skill

> It is not the code.
> It is the clarity of your thinking.
>
> The better you describe what you want,
> the better Claude Code executes.
>
> That skill — you already have it.

---

*10x.in*