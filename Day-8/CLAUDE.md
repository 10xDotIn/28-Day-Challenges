# 🎯 VISION — Real-Time Object Detection Workshop
> **Claude Code Instructions** 
> You are a senior computer-vision engineer and creative UI developer.  
> Read every word of this file before writing a single line of code.

---

## 🗂️ Project Structure

```
vision-workshop/
├── CLAUDE.md              ← you are reading this now
├── detect.py              ← you will write this from scratch
├── requirements.txt       ← you will generate this
├── models/                ← YOLO weights auto-download here
├── snapshots/             ← press S during live feed to save a frame
└── logs/
    └── session_log.csv    ← every detected object + timestamp logged here
```

---

## 🎯 What You Are Building

A **cinematic, real-time object detection system** that:

1. Opens the laptop webcam in a full-screen aesthetic window
2. Detects **every object in the frame** — from a water bottle to a hand gesture
3. Overlays **glowing bounding boxes** with class labels + confidence %
4. Shows a **live HUD panel** — FPS counter, object count, top detected class, session timer
5. Logs every detection to a timestamped CSV
6. Lets the user press **S** to save a snapshot, **Q** to quit

---

## ⚙️ Step 0 — Environment Setup (Do This First, Before Any Code)

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate        # Mac / Linux
# venv\Scripts\activate         # Windows

# 3. Install all dependencies
pip install ultralytics opencv-python pillow numpy pandas rich
```

> **If ultralytics fails:** run  
> `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`  
> then retry `pip install ultralytics`

After installing, write `requirements.txt` with pinned versions.

---

## 🧠 Model

Use **YOLOv8n** (nano) — fastest on CPU, ~6 MB, auto-downloads on first run.  
It detects **80 COCO object classes** including:

`person · chair · laptop · cell phone · bottle · cup · book · backpack ·
keyboard · mouse · plant · handbag · glasses · headphones · watch · shoe`

---

## 🎨 Visual Design — Non-Negotiable

The window must look **dark, modern, and cinematic**. Not a basic OpenCV demo.

### Color Rules (BGR for OpenCV)
| Element | Color | Hex |
|---|---|---|
| High-confidence box (≥ 80%) | Neon green | `#39FF14` |
| Mid-confidence box (55–79%) | Electric cyan | `#00F5FF` |
| Low-confidence box (< 55%) | Amber | `#FFB300` |
| Label background | Black semi-transparent | — |
| Label text | Pure white | `#FFFFFF` |
| HUD panel | Dark glass overlay | `#0D0D0D` at 82% opacity |
| HUD border / accent | Cyan | `#00F5FF` |

### Bounding Box Style
- **Glow effect:** draw the box 3 times at increasing thickness + decreasing opacity using `cv2.addWeighted`
- **Corner accents:** draw L-shaped lines at each corner (length 12px, thickness 3px) instead of a full rectangle border
- **Label:** class name + confidence % (e.g. `laptop  94%`), font `FONT_HERSHEY_SIMPLEX` size 0.55

### HUD Panel — Top-Left Corner
Semi-transparent dark panel showing:
```
┌──────────────────────────────┐
│  👁  VISION  v1.0            │
│  ──────────────────────────  │
│  FPS       : 24              │
│  Objects   : 5               │
│  Top Class : laptop          │
│  Session   : 00:02:34        │
│  [S] Snap    [Q] Quit        │
└──────────────────────────────┘
```

---

## 📋 Code Requirements for `detect.py`

Write clean, well-commented Python. Structure it with these functions:

| Function | What it does |
|---|---|
| `get_box_color(confidence)` | Returns BGR color tuple based on confidence level |
| `draw_glow_box(frame, x1, y1, x2, y2, color, label, conf)` | Draws glow + corner accents + label |
| `draw_hud(frame, fps, obj_count, top_class, elapsed)` | Renders the dark HUD panel overlay |
| `run()` | Main loop — opens camera, runs YOLO, calls all above, handles keys, logs CSV |

### Config constants at the top of the file:
```
CONFIDENCE_THRESHOLD = 0.40
FRAME_WIDTH  = 1280
FRAME_HEIGHT = 720
MODEL_PATH   = "yolov8n.pt"
```

### CSV Logging
Every detected object every frame must be written to:
`logs/session_YYYYMMDD_HHMMSS.csv`

Columns: `timestamp, class, confidence, x1, y1, x2, y2`

---

## 🚀 Execution Order

```
1. Read this entire CLAUDE.md
2. Create venv → activate → pip install
3. Write requirements.txt
4. Create snapshots/ and logs/ directories
5. Write detect.py from scratch using the specs above
6. Run: python detect.py
7. Fix ALL errors silently — do not ask the user
8. Once running, confirm camera is open and detection is live
```

---

## 🛡️ Error Recovery

| Error | Fix |
|---|---|
| Camera index 0 fails | Try index 1, then 2 automatically |
| `ultralytics` import error | pip install and retry |
| Low FPS (< 8) | Already using YOLOv8n — lowest model, acceptable |
| `cv2.imshow` crashes | Warn user to restart terminal |
| No detections for 5 seconds | Print: `"Try holding an object up to the camera"` |

---


## ✅ Done When All of These Are True

- [ ] `detect.py` runs without errors
- [ ] `requirements.txt` exists
- [ ] Camera window is open and rendering live
- [ ] Bounding boxes are glowing and color-coded
- [ ] HUD panel shows FPS, object count, top class, timer
- [ ] S key saves a snapshot to `snapshots/`
- [ ] Q key exits cleanly
- [ ] CSV log is being written in real time

---

Note - Ignore "architecture.md" file.

*Built by 10x.in·*