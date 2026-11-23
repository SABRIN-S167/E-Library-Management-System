@echo off
title Project Launcher
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
if not exist ".venv\Scripts\python.exe" (
 echo Creating virtual environment...
 %PY% -m venv .venv
 if errorlevel 1 goto error
)
echo Installing packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Starting application...
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto error
pause
exit /b 0
:error
echo Setup failed. Check Python 3.10+ and internet connection.
pause
