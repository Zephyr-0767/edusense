# backend/emotion_engine.py
import threading
import time
import cv2
import numpy as np
from fer import FER

# Configuration
CAM_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
ANALYZE_EVERY_N = 2   # run emotion detection every N frames

# state
_lock = threading.Lock()
_last_frame_jpeg = None      # bytes
_last_results = []           # FER results list
_last_engagement = {"faces": 0, "engagement": 0.0, "dominant": None, "timestamp": None}

# initialize detector (this will import tensorflow; ensure TF is configured in app.py before uvicorn runs)
detector = FER(mtcnn=False)

# camera thread
def _camera_loop():
    global _last_frame_jpeg, _last_results, _last_engagement
    cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        # mirror for nicer preview (optional)
        frame = cv2.flip(frame, 1)

        frame_count += 1
        if frame_count % ANALYZE_EVERY_N == 0:
            # run FER on a resized copy (avoid modifying original)
            small = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            try:
                results = detector.detect_emotions(small)
            except Exception:
                results = []

            # compute engagement (simple average of weights)
            weights_map = {
                "happy": 1.0, "surprise": 0.9, "neutral": 0.7,
                "sad": 0.35, "angry": 0.3, "disgust": 0.2, "fear": 0.25
            }
            emotions = []
            for r in results:
                em = r.get("emotions", {})
                if em:
                    top = max(em.items(), key=lambda it: it[1])[0]
                    emotions.append(top)

            if emotions:
                w = [weights_map.get(e, 0.5) for e in emotions]
                engagement = float(np.mean(w) * 100.0)
                dominant = emotions[0]
            else:
                engagement = 0.0
                dominant = None

            with _lock:
                _last_results = results
                _last_engagement = {
                    "timestamp": time.strftime("%H:%M:%S"),
                    "faces": len(results),
                    "emotions": emotions,
                    "engagement": round(engagement, 2),
                    "dominant": dominant,
                }

        # encode frame as JPEG to serve quickly
        ret2, buf = cv2.imencode('.jpg', frame)
        if ret2:
            jpg_bytes = buf.tobytes()
            with _lock:
                _last_frame_jpeg = jpg_bytes

        # tiny sleep to avoid using 100% CPU
        time.sleep(0.01)

# start camera thread once on import
_thread = threading.Thread(target=_camera_loop, daemon=True)
_thread.start()

# accessors
def get_latest_snapshot():
    """Return bytes of latest JPEG frame (or None)."""
    with _lock:
        return _last_frame_jpeg

def get_latest_data():
    """Return latest engagement dict."""
    with _lock:
        return dict(_last_engagement)
