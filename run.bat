@echo off
cd /d "%~dp0"

echo ========================================
echo    Eventuri_CB Launcher
echo ========================================
echo.

:: Check if venv exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Start Eventuri_CB using venv Python
echo [*] Starting Eventuri_CB...
echo.

:: Use venv Python directly
venv\Scripts\python.exe main.py

:: Pause if error occurred
if errorlevel 1 (
    echo.
    echo [ERROR] Program exited with error
    pause
)

