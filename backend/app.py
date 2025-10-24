# backend/app.py
import tensorflow as tf
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .emotion_engine import get_latest_data

# ✅ Pin to NVIDIA GPU if available
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.set_visible_devices(gpus[0], 'GPU')
        tf.config.experimental.set_memory_growth(gpus[0], True)
        print("✅ Using GPU:", gpus[0])
    except Exception as e:
        print("⚠️ Could not set GPU:", e)
else:
    print("⚠️ No GPU found, running on CPU.")

# ✅ FastAPI app
app = FastAPI(title="EduSense Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "message": "EduSense backend running"}

@app.get("/engagement")
def engagement():
    return get_latest_data()
