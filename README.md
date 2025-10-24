# EduSense

EduSense — real-time student emotion & engagement monitor.


1. Create & activate venv: (Recommended to avoid clashes)
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1` 
2. Install:
   - `pip install -r requirements.txt`
3. Start backend:
   - `python -m uvicorn backend.app:app --reload`
4. Start frontend:
   - `streamlit run frontend/streamlit_app.py`
