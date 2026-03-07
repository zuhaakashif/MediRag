@echo off
echo Starting MediRAG...
echo.

REM Start FastAPI
start "MediRAG API" cmd /k "uvicorn app.main:app --reload --port 8000"

REM Wait for API to start
timeout /t 2 /nobreak > nul

REM Start main chat UI
start "MediRAG UI" cmd /k "streamlit run frontend/ui.py --server.port 8501"

REM Start admin dashboard
start "MediRAG Admin" cmd /k "streamlit run dashboard/admin.py --server.port 8502"

echo.
echo MediRAG is starting up!
echo.
echo   Chat UI:    http://localhost:8501
echo   Admin:      http://localhost:8502
echo   API Docs:   http://localhost:8000/docs
echo.
pause
