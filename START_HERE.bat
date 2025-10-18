@echo off
title Wall Inspector - Quick Start Menu
color 0A

:menu
cls
echo ============================================
echo    WALL INSPECTOR - QUICK START MENU
echo ============================================
echo.
echo What would you like to do?
echo.
echo 1. Run Mobile-Optimized Version
echo 2. Run Desktop Version
echo 3. Kill Process on Port 8501
echo 4. Exit
echo.
echo ============================================
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto mobile
if "%choice%"=="2" goto desktop
if "%choice%"=="3" goto kill
if "%choice%"=="4" goto end
echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:mobile
cls
echo Starting Mobile-Optimized Version...
echo.
call run_mobile.bat
goto menu

:desktop
cls
echo Starting Desktop Version...
echo.
call run_desktop.bat
goto menu

:kill
cls
echo Killing processes on port 8501...
echo.
call kill_port_8501.bat
goto menu

:end
echo.
echo Goodbye!
timeout /t 2 >nul
exit
