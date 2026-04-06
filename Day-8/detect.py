"""
VISION v1.0 — Real-Time Object Detection
Cinematic YOLOv8 webcam detection with glowing bounding boxes and HUD overlay.
"""

import cv2
import numpy as np
import csv
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

# ─── Config Constants ────────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.40
FRAME_WIDTH  = 1280
FRAME_HEIGHT = 720
MODEL_PATH   = "yolov8n.pt"

# ─── Color Palette (BGR) ─────────────────────────────────────────────────────
COLOR_HIGH   = (20, 255, 57)    # Neon green  ≥ 80%
COLOR_MID    = (255, 245, 0)    # Electric cyan 55–79%
COLOR_LOW    = (0, 179, 255)    # Amber < 55%
COLOR_HUD_BG = (13, 13, 13)
COLOR_ACCENT = (255, 245, 0)    # Cyan accent
COLOR_WHITE  = (255, 255, 255)


def get_box_color(confidence: float) -> tuple:
    """Return BGR color based on detection confidence level."""
    if confidence >= 0.80:
        return COLOR_HIGH
    elif confidence >= 0.55:
        return COLOR_MID
    else:
        return COLOR_LOW


def draw_glow_box(frame, x1: int, y1: int, x2: int, y2: int,
                  color: tuple, label: str, conf: float):
    """Draw glow effect + corner accents + confidence label on frame."""
    overlay = frame.copy()

    # Glow effect: 3 layers — thick+faint → thin+solid
    glow_layers = [
        (8, 0.15),
        (5, 0.30),
        (2, 0.70),
    ]
    for thickness, alpha in glow_layers:
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, thickness)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        overlay = frame.copy()

    # Corner accents (L-shaped lines at each corner)
    corner_len = 14
    corner_thick = 3

    corners = [
        # (start_h, end_h, start_v, end_v)
        ((x1, y1), (x1 + corner_len, y1), (x1, y1), (x1, y1 + corner_len)),          # top-left
        ((x2 - corner_len, y1), (x2, y1), (x2, y1), (x2, y1 + corner_len)),          # top-right
        ((x1, y2), (x1 + corner_len, y2), (x1, y2 - corner_len), (x1, y2)),          # bottom-left
        ((x2 - corner_len, y2), (x2, y2), (x2, y2 - corner_len), (x2, y2)),          # bottom-right
    ]
    for h_start, h_end, v_start, v_end in corners:
        cv2.line(frame, h_start, h_end, color, corner_thick)
        cv2.line(frame, v_start, v_end, color, corner_thick)

    # Label: "classname  94%"
    text = f"{label}  {int(conf * 100)}%"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    font_thick = 1
    (tw, th), baseline = cv2.getTextSize(text, font, font_scale, font_thick)

    # Semi-transparent label background
    pad = 4
    lx1, ly1 = x1, max(0, y1 - th - baseline - pad * 2)
    lx2, ly2 = x1 + tw + pad * 2, y1

    label_bg = frame.copy()
    cv2.rectangle(label_bg, (lx1, ly1), (lx2, ly2), (0, 0, 0), -1)
    cv2.addWeighted(label_bg, 0.75, frame, 0.25, 0, frame)

    cv2.putText(frame, text, (lx1 + pad, ly2 - baseline - 1),
                font, font_scale, COLOR_WHITE, font_thick, cv2.LINE_AA)


def draw_hud(frame, fps: float, obj_count: int, top_class: str, elapsed: float):
    """Render the dark glass HUD panel in the top-left corner."""
    h, w = frame.shape[:2]

    panel_x, panel_y = 18, 18
    panel_w, panel_h = 280, 178

    # Semi-transparent dark background
    overlay = frame.copy()
    cv2.rectangle(overlay, (panel_x, panel_y),
                  (panel_x + panel_w, panel_y + panel_h),
                  COLOR_HUD_BG, -1)
    cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)

    # Cyan border
    cv2.rectangle(frame, (panel_x, panel_y),
                  (panel_x + panel_w, panel_y + panel_h),
                  COLOR_ACCENT, 1)

    # Accent top bar
    cv2.rectangle(frame, (panel_x, panel_y),
                  (panel_x + panel_w, panel_y + 3),
                  COLOR_ACCENT, -1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    tx = panel_x + 14

    # Title
    cv2.putText(frame, "VISION  v1.0", (tx, panel_y + 26),
                font, 0.58, COLOR_ACCENT, 1, cv2.LINE_AA)

    # Divider
    cv2.line(frame, (panel_x + 10, panel_y + 34),
             (panel_x + panel_w - 10, panel_y + 34), COLOR_ACCENT, 1)

    # Stats
    elapsed_td = str(timedelta(seconds=int(elapsed)))
    top_display = top_class if top_class else "—"
    stats = [
        ("FPS      ", f"{fps:.1f}"),
        ("Objects  ", str(obj_count)),
        ("Top Class", top_display),
        ("Session  ", elapsed_td),
    ]
    for i, (key, val) in enumerate(stats):
        y = panel_y + 62 + i * 26
        cv2.putText(frame, f"{key}: {val}", (tx, y),
                    font, 0.50, COLOR_WHITE, 1, cv2.LINE_AA)

    # Hotkeys hint
    cv2.putText(frame, "[S] Snap    [Q] Quit",
                (tx, panel_y + panel_h - 14),
                font, 0.42, COLOR_ACCENT, 1, cv2.LINE_AA)


def run():
    """Main detection loop."""
    # Import here so error is clear if missing
    from ultralytics import YOLO

    # Load model (auto-downloads yolov8n.pt on first run)
    print("[VISION] Loading YOLOv8n model...")
    model = YOLO(MODEL_PATH)

    # Open camera — try indices 0, 1, 2
    cap = None
    for idx in range(3):
        candidate = cv2.VideoCapture(idx)
        if candidate.isOpened():
            cap = candidate
            print(f"[VISION] Camera opened at index {idx}")
            break
        candidate.release()

    if cap is None:
        print("[ERROR] Could not open any camera (tried 0, 1, 2).")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    # Prepare CSV log
    Path("logs").mkdir(exist_ok=True)
    Path("snapshots").mkdir(exist_ok=True)
    session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"logs/session_{session_ts}.csv"
    csv_file = open(csv_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["timestamp", "class", "confidence", "x1", "y1", "x2", "y2"])

    print(f"[VISION] Logging detections to {csv_path}")
    print("[VISION] Press S to snapshot, Q to quit.")

    start_time = time.time()
    fps = 0.0
    frame_count = 0
    fps_timer = time.time()
    last_detection_time = time.time()
    no_detection_warned = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Frame read failed.")
            break

        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        elapsed = time.time() - start_time

        # Run YOLO inference
        results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)[0]
        boxes = results.boxes

        obj_count = 0
        class_counts: dict[str, int] = {}
        now_str = datetime.now().isoformat(timespec="milliseconds")

        if boxes is not None and len(boxes) > 0:
            last_detection_time = time.time()
            no_detection_warned = False

            for box in boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                color = get_box_color(conf)
                draw_glow_box(frame, x1, y1, x2, y2, color, cls_name, conf)

                class_counts[cls_name] = class_counts.get(cls_name, 0) + 1
                obj_count += 1

                # Log to CSV
                csv_writer.writerow([now_str, cls_name, f"{conf:.4f}",
                                     x1, y1, x2, y2])

            csv_file.flush()

        # No detections for 5 seconds
        if time.time() - last_detection_time > 5 and not no_detection_warned:
            print("Try holding an object up to the camera")
            no_detection_warned = True

        top_class = max(class_counts, key=class_counts.get) if class_counts else ""

        # FPS calculation (rolling over 10 frames)
        frame_count += 1
        if frame_count % 10 == 0:
            fps = 10.0 / (time.time() - fps_timer)
            fps_timer = time.time()

        draw_hud(frame, fps, obj_count, top_class, elapsed)

        cv2.imshow("VISION v1.0 — Real-Time Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == ord("Q"):
            print("[VISION] Exiting.")
            break
        elif key == ord("s") or key == ord("S"):
            snap_path = f"snapshots/snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(snap_path, frame)
            print(f"[VISION] Snapshot saved → {snap_path}")

    cap.release()
    csv_file.close()
    cv2.destroyAllWindows()
    print("[VISION] Session ended. CSV log saved.")


if __name__ == "__main__":
    run()
