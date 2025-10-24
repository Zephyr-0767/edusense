# frontend/streamlit_app.py
import streamlit as st
import requests
import time
import pandas as pd
from collections import deque
from datetime import datetime

st.set_page_config(page_title="EduSense Dashboard", layout="centered")
st.title("🎓 EduSense — Emotion & Engagement Monitor")

BACKEND_URL = "http://127.0.0.1:8000/engagement"  # change if needed

# ---------- Controls (create once, give explicit keys) ----------
refresh_rate = st.sidebar.slider("Refresh rate (sec)", min_value=1, max_value=10, value=2, key="refresh_rate")
max_points = st.sidebar.slider("History length (points)", min_value=10, max_value=600, value=120, key="max_points")
# IMPORTANT: give a unique key
run_live = st.sidebar.checkbox("🔴 Live Mode", value=True, key="run_live")

if "history" not in st.session_state:
    st.session_state.history = deque(maxlen=max_points)

# allow user to clear graph
if st.sidebar.button("Clear Graph", key="clear_graph"):
    st.session_state.history.clear()

# placeholders
chart_placeholder = st.empty()
info_col = st.empty()

# a helper to fetch backend safely
def fetch_engagement():
    try:
        res = requests.get(BACKEND_URL, timeout=4)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# Main update loop (runs while checkbox is checked)
# Note: widget `run_live` is created only once above (unique key), so no duplicate-id errors.
while st.session_state.get("run_live", False):
    data = fetch_engagement()
    if "error" in data:
        st.warning(f"Fetch error: {data['error']}")
        time.sleep(max(1, st.session_state.get("refresh_rate", 2)))
        # continue trying
        continue

    engagement = float(data.get("engagement", 0.0))
    ts = data.get("timestamp") or datetime.now().strftime("%H:%M:%S")

    # push into session deque (ensures a rolling buffer)
    # update maxlen if user changed slider
    maxlen = st.session_state.get("max_points", 120)
    if st.session_state.history.maxlen != maxlen:
        # re-create deque with new maxlen, keeping old points
        old = list(st.session_state.history)
        st.session_state.history = deque(old[-maxlen:], maxlen=maxlen)

    st.session_state.history.append((ts, engagement))

    # build dataframe for plotting
    df = pd.DataFrame(list(st.session_state.history), columns=["timestamp", "engagement"])
    df = df.set_index("timestamp")

    # update chart in-place
    chart_placeholder.line_chart(df["engagement"], height=350)

    # update latest metric
    info_col.metric("Latest engagement", f"{engagement:.1f}%")

    # sleep for UI-controlled refresh
    time.sleep(max(0.2, st.session_state.get("refresh_rate", 2)))

# When user stops live mode, show final summary and controls remain on the page
st.info("Live stopped. Toggle the Live Mode checkbox in the sidebar to resume.")
if st.session_state.history:
    st.write("Recent data (most recent last):")
    st.dataframe(pd.DataFrame(list(st.session_state.history), columns=["timestamp", "engagement"]))
