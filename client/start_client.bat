@echo off
REM System Statistics Client Startup Script (Windows)
REM This script starts the FastAPI monitoring client

echo === System Statistics Client Startup ===
echo Starting FastAPI Monitoring Client...

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

REM Get hostname and IP
for /f "tokens=*" %%i in ('hostname') do set HOSTNAME=%%i
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do set LOCAL_IP=%%i
set LOCAL_IP=%LOCAL_IP: =%

REM Display client information
echo.
echo ==================================
echo   SYSTEM STATISTICS CLIENT
echo ==================================
echo Computer: %HOSTNAME%
echo Client will start on port: 8000
echo Local access: http://localhost:8000
if defined LOCAL_IP (
    echo Network access: http://%LOCAL_IP%:8000
)
echo.
echo SETUP INSTRUCTIONS:
echo 1. Copy the token that will be displayed below
echo 2. Open your server dashboard at http://server-ip:8001
echo 3. Login and go to 'Manage Computers'
echo 4. Add this computer using:
echo    - Name: %HOSTNAME% ^(or custom name^)
if defined LOCAL_IP (
    echo    - URL: http://%LOCAL_IP%:8000
) else (
    echo    - URL: http://localhost:8000
)
echo    - Token: [copy from below]
echo ==================================
echo.

REM Start the client
echo Starting client...
python client.py

pause