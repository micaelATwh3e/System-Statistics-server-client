@echo off
REM System Statistics Server Startup Script (Windows)
REM This script starts the Flask dashboard server

echo === System Statistics Server Startup ===
echo Starting Flask Dashboard Server...

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\requirements_installed.flag" (
    echo Installing requirements...
    pip install -r requirements.txt
    if not errorlevel 1 (
        echo. > venv\requirements_installed.flag
        echo Requirements installed successfully
    ) else (
        echo Error: Failed to install requirements
        pause
        exit /b 1
    )
) else (
    echo Requirements already installed
)

REM Display server information
echo.
echo ==================================
echo   SYSTEM STATISTICS SERVER
echo ==================================
echo Server will start on: http://localhost:8001
echo Default login:
echo   Username: admin
echo   Password: admin123
echo.
echo WARNING: Change default password after first login!
echo ==================================
echo.

REM Start the server
echo Starting server...
python server.py

pause