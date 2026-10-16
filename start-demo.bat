@echo off
set ROOT=%~dp0
start "InsureFlow FastAPI" cmd /k "cd /d %ROOT%backend && py -m venv .venv 2>nul && call .venv\Scripts\activate && pip install -r requirements.txt && uvicorn main:app --reload --port 8000"
start "InsureFlow Frontend" cmd /k "cd /d %ROOT%frontend && npm install && npm run dev"
echo InsureFlow is starting. Open http://localhost:5173 after the frontend starts.
pause
