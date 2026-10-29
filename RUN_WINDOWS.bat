@echo off
title Awaaz Adhikar - Django Server
cd /d "%~dp0"
echo =========================================
echo        AWAAZ ADHIKAR - START SERVER
echo =========================================
echo.
if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -m venv .venv
    if errorlevel 1 (
        echo Python launcher failed. Try installing Python or use VS Code terminal.
        pause
        exit /b 1
    )
)
call ".venv\Scripts\activate.bat"
echo Installing Django dependencies (first run may take a few minutes)...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed. Check internet and Python installation.
    pause
    exit /b 1
)
echo Preparing SQLite database...
python manage.py migrate
if errorlevel 1 (
    echo Database migration failed.
    pause
    exit /b 1
)
echo.
echo Open this in your browser: http://127.0.0.1:8000/
echo Press Ctrl+C to stop the server.
echo.
python manage.py runserver
pause
