@echo off
REM Run the mobile-optimized Wall Inspector app

echo Starting Wall Inspector (Mobile-Optimized)...
echo.
echo Opening at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

uv run streamlit run app_mobile_optimized.py
