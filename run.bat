@echo off
REM Wall Inspector - Quick Launcher
REM Mobile-first AI wall damage detection

title Wall Inspector

echo ============================================
echo         WALL INSPECTOR
echo    AI Wall Damage Detection
echo ============================================
echo.
echo Starting Wall Inspector...
echo.
echo Local URL:   http://localhost:8501
echo Mobile URL:  http://192.168.1.215:8501
echo              (Access from phone on same WiFi)
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================
echo.

uv run streamlit run app.py

pause

