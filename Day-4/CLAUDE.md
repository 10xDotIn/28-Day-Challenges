# Product Image QA + Computer Vision Analyzer

You are a computer vision analyst. For every image in the `images/` folder,
you will run BOTH a quality check AND deep computer vision analysis using
OpenCV. The computer should be doing real visual analysis — not just
reading metadata.

## Part 1 — Image Quality Checks (same as before)
- Blur detection using Laplacian variance (flag if score < 80)
- White background check using edge pixel scan
- Resolution check (min 800px short side)
- Aspect ratio check (1:1 or 4:3)
- Watermark / text / centering via Claude Vision API

## Part 2 — Real Computer Vision Analysis (this is the new part)
Use OpenCV to actually analyze the visual content of each image:

### Color Analysis
- Extract dominant colors using K-Means clustering (k=5)
- Show the top 3 dominant colors as hex codes and their percentage
- Detect color temperature (warm / cool / neutral)

### Edge & Shape Analysis
- Run Canny edge detection
- Count edges — high edge count = complex/detailed product
- Detect if product has sharp corners or curved shape (using contours)

### Product Segmentation
- Use GrabCut or thresholding to separate product from background
- Calculate what percentage of the frame the product occupies
- Flag if product takes up less than 30% of frame (too small)

### Texture & Detail Analysis
- Use Gabor filters or LBP (Local Binary Patterns) to measure texture richness
- Score the surface detail level: Low / Medium / High

### Histogram Analysis
- Plot RGB histogram for each image
- Flag if image is overexposed (too many pixels > 240) or underexposed (too many < 20)
- Save histogram as a PNG next to the report

## What to build:
1. Install all required packages (opencv-python, pillow, scikit-learn, 
   matplotlib, anthropic, pandas, numpy)
2. Write `analyzer.py` with all CV functions above
3. Run it on every image in `images/`
4. Save results to `output/report.csv`
5. Save a visual summary image `output/summary_grid.png` showing 
   each image with its dominant colors and edge map side by side
6. Give me a final plain English analysis of what you found

## Output CSV columns:
filename, qa_status, blur_score, dominant_color_1, dominant_color_2,
dominant_color_3, product_coverage_pct, edge_complexity, texture_level,
exposure, shape_type, watermark_detected, overall_grade (A/B/C/F)

## Rules:
- Actually run every analysis — don't skip steps
- Fix errors yourself before reporting back
- The summary_grid.png is important — create it
- Give me insights, not just numbers. Tell me what the analysis MEANS
  for each product image

Note : Ignore the "architecture.md" file.
