import cv2
import torch
import numpy as np
import time
from transformers import pipeline
from PIL import Image

device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

print("Loading Depth Anything V2 (small model)... first run downloads it, may take a minute.")
pipe = pipeline(
    task="depth-estimation",
    model="depth-anything/Depth-Anything-V2-Small-hf",
    device=device
)
print("Model loaded.")

cap = cv2.VideoCapture("http://192.168.0.165:5000/video")

if not cap.isOpened():
    print("Could not open webcam")
    exit()

print("Webcam opened. Press 'q' to quit.")

INFERENCE_SIZE = (256, 192)
FRAME_SKIP = 2
frame_count = 0
last_depth_colored = None

scan_y = 0
scan_speed = 6
prev_time = time.time()

def draw_corner_brackets(img, color=(0, 255, 200), length=30, thickness=2):
    h, w = img.shape[:2]
    m = 20
    cv2.line(img, (m, m), (m + length, m), color, thickness)
    cv2.line(img, (m, m), (m, m + length), color, thickness)
    cv2.line(img, (w - m, m), (w - m - length, m), color, thickness)
    cv2.line(img, (w - m, m), (w - m, m + length), color, thickness)
    cv2.line(img, (m, h - m), (m + length, h - m), color, thickness)
    cv2.line(img, (m, h - m), (m, h - m - length), color, thickness)
    cv2.line(img, (w - m, h - m), (w - m - length, h - m), color, thickness)
    cv2.line(img, (w - m, h - m), (w - m, h - m), color, thickness)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    frame_count += 1

    if frame_count % FRAME_SKIP == 0 or last_depth_colored is None:
        small_frame = cv2.resize(frame, INFERENCE_SIZE)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)

        result = pipe(pil_image)
        depth_np = np.array(result["depth"])

        depth_norm = cv2.normalize(depth_np, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        depth_colored = cv2.applyColorMap(depth_norm, cv2.COLORMAP_TURBO)
        last_depth_colored = cv2.resize(depth_colored, (w, h))

    blended = cv2.addWeighted(frame, 0.4, last_depth_colored, 0.6, 0)

    scan_y = (scan_y + scan_speed) % h
    cv2.line(blended, (0, scan_y), (w, scan_y), (0, 255, 200), 2)
    overlay = blended.copy()
    cv2.rectangle(overlay, (0, max(0, scan_y - 15)), (w, scan_y), (0, 255, 200), -1)
    blended = cv2.addWeighted(overlay, 0.15, blended, 0.85, 0)

    draw_corner_brackets(blended)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0
    prev_time = curr_time

    cv2.putText(blended, "DEPTH VISION ONLINE", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 200), 2)
    cv2.putText(blended, f"FPS: {fps:.1f}  DEVICE: {device.upper()}", (30, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 200), 1)

    cv2.imshow("Depth Vision HUD - press q to quit", blended)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

