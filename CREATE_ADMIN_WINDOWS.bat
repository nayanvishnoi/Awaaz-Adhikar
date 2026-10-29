@echo off
title Awaaz Adhikar - Create Admin
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run RUN_WINDOWS.bat once before creating an admin.
    pause
    exit /b 1
)
call ".venv\Scripts\activate.bat"
python manage.py createsuperuser
pause
