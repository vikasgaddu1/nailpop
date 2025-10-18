@echo off
REM Run the desktop version of Wall Inspector app

echo Starting Wall Inspector (Desktop Version)...
echo.
echo Opening at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

uv run streamlit run app.py
