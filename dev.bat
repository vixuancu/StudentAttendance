@echo off
REM ============================================================
REM StudentAttendance - Development Server (Windows)
REM Hot reload enabled
REM ============================================================

echo.
echo ============================================================
echo  Starting Development Server
echo ============================================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist "backend\.env" (
    echo WARNING: backend\.env not found!
    echo Please update it with your Supabase credentials before running
    echo.
)

REM Start development server
echo Starting Uvicorn with hot reload...
echo.
echo Server: http://localhost:8000
echo Docs:   http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo.

cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
