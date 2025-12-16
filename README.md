# paltalk-uia-service (PoC)

Purpose
-------
Prototype UI Automation (UIA) service for extracting mic/speaker state from Paltalk windows and optionally posting messages into the Paltalk window. The service prefers UI Automation (pywinauto) for deterministic access and falls back to an OCR capture if needed.

Quickstart
----------
1. Run on a Windows machine with Python 3.8+.
2. Create and activate a virtualenv and install dependencies:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Run dev server (requires direct desktop access):
   ```powershell
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
4. Probe a Paltalk window (replace title substring):
   - GET http://127.0.0.1:8000/room/A%20Welcome%20Soap%20Box/status

Files
-----
- `app/probe.py` - UIA probe and helper to send messages to the window.
- `app/main.py` - FastAPI app exposing `/room/{name}/status` and `/room/{name}/message`.
- `tests/` - unit tests for the probe logic (non-UI tests with mocking).
- `.github/workflows/ci.yml` - Windows CI job to run tests.

Notes
-----
- This is an experimental PoC; production needs hardened error handling, logging, and more robust fallbacks.
- The service must run on Windows because UIA needs native access to window controls.
