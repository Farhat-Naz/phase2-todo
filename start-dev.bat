@echo off
REM Development startup script for Windows
echo ========================================
echo Starting phaseII-todo Development Servers
echo ========================================
echo.

REM Check if we're in the correct directory
if not exist "backend" (
    echo ERROR: Run this script from the project root directory!
    pause
    exit /b 1
)

REM Start backend in a new window
echo Starting backend server on http://localhost:8000
start "Backend - FastAPI" cmd /k "cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in a new window
echo Starting frontend server on http://localhost:3000
start "Frontend - Next.js" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to exit (servers will keep running)
pause
