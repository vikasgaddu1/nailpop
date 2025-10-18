@echo off
REM Kill process using port 8501 (Streamlit default port)

echo Checking for processes using port 8501...
netstat -ano | findstr :8501

echo.
echo Killing process on port 8501...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501 ^| findstr LISTENING') do (
    echo Killing PID: %%a
    taskkill /PID %%a /F
)

echo.
echo Done! Port 8501 is now free.
pause
