# EduSense

EduSense — real-time student emotion & engagement monitor.

## Run locally
1. Create & activate venv:
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1` (PowerShell)
2. Install:
   - `pip install -r requirements.txt`
3. Start backend:
   - `python -m uvicorn backend.app:app --reload`
4. Start frontend:
   - `streamlit run frontend/streamlit_app.py`
