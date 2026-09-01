@echo off
title MediCheck — Run Locally
color 0B

echo.
echo ================================================
echo   MediCheck — Local Run
echo ================================================
echo.

REM ── Find Python ────────────────────────────────
set PYTHON=C:\Users\lapzone\AppData\Local\Microsoft\WindowsApps\python.exe
set STREAMLIT=C:\Users\lapzone\AppData\Local\Python\pythoncore-3.14-64\Scripts\streamlit.exe

if not exist "%STREAMLIT%" (
    echo Installing dependencies...
    "%PYTHON%" -m pip install -r requirements.txt
)

echo Starting MediCheck...
echo Open your browser at: http://localhost:8501
echo.
"%STREAMLIT%" run app.py

pause
