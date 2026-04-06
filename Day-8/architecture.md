---

# ARCHITECTURE.md
## What We Are Building Today

---

## WHAT IS OBJECT DETECTION

```
Object detection teaches a computer to SEE and UNDERSTAND.

When you look at a room you instantly know:
  "that's a laptop"
  "that's a coffee cup"
  "that's a person"

Object detection makes a computer do the same thing.

It looks at a live camera frame and answers:
  WHAT is in this frame?
  WHERE exactly is it?
  HOW confident is the model?

All three questions. Every object. Every frame. In real time.
```

---

## THE MODEL — YOLOv8n

```
YOLO = You Only Look Once

Scans the entire frame in one single pass.
Finds everything. No second look. No slow scanning.

How did it learn?
  Trained on millions of labeled images.
  It learned shapes, edges, colors, textures.
  Now it recognizes 80 everyday object classes.
  Size: only 6MB. Runs on any laptop.
```

---

## CONFIDENCE SCORE

```
Every detection comes with a score.

  94%  →  very sure
  65%  →  fairly sure
  42%  →  unsure

WHY DOES IT GO LOW?
  Bad lighting
  Unusual angle
  Object partially hidden
  Small objects like pen or glasses

The model is being honest about what it knows.
```

---

## WHAT WE ARE BUILDING

```
CAMERA  →  YOLOv8n MODEL  →  DETECT.PY
                                  ↓
               ┌──────────────────────────────┐
               │  1. LIVE WINDOW              │
               │     glowing bounding boxes   │
               │     + HUD panel              │
               │                              │
               │  2. SESSION LOG CSV          │
               │     every object logged      │
               │     with timestamp           │
               │                              │
               │  3. SNAPSHOTS                │
               │     press S to save frame    │
               └──────────────────────────────┘
                                  ↓
               CLAUDE ANALYZES THE LOG
```

---

## BOX COLORS EXPLAINED

```
GREEN   =  80% and above   →  trust this
CYAN    =  55% to 79%      →  probably right
AMBER   =  below 55%       →  treat with caution
```

---

## HOW CLAUDE CODE BUILDS THIS

```
OLD WAY
  Learn OpenCV + PyTorch
  Write detection code
  Write visualization code
  Debug for hours
  TIME: days

TODAY
  Write CLAUDE.md in plain English
  Claude builds the entire system
  Camera opens and runs
  TIME: under 10 minutes
```

---

## THE ANALYSIS PROMPTS

```
PROMPT 1  →  Make Claude understand the data
PROMPT 2  →  What was detected most and why
PROMPT 3  →  How detections changed over time
PROMPT 4  →  Flag anomalies automatically
```

---

## WHERE THIS IS USED IN THE REAL WORLD

```
Retail        →  counting products on shelves
Security      →  detecting unusual objects
Healthcare    →  monitoring patient movement
Manufacturing →  spotting defects on lines
Smart Homes   →  understanding room usage
Sports        →  tracking players and equipment
```

---

*You just built the foundation of all of these.*

---