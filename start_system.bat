@echo off
REM System Statistics - Complete Startup Script (Windows)
REM This script can start both server and client

echo === System Statistics Startup Manager ===
echo.
echo What would you like to start?
echo 1) Server only (Flask Dashboard)
echo 2) Client only (Monitoring Agent)
echo 3) Both Server and Client
echo 4) Exit
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" (
    echo Starting Server...
    cd server
    call start_server.bat
) else if "%choice%"=="2" (
    echo Starting Client...
    cd client
    call start_client.bat  
) else if "%choice%"=="3" (
    echo Starting both Server and Client...
    echo The server will start first, then the client in a new window...
    
    REM Start server in new command prompt window
    start "System Statistics Server" cmd /c "cd server && start_server.bat"
    
    REM Wait a moment for server to start
    timeout /t 5 /nobreak >nul
    
    REM Start client in new command prompt window
    start "System Statistics Client" cmd /c "cd client && start_client.bat"
    
    echo.
    echo Both services are starting in separate windows...
    echo Check the new command prompt windows for status.
    
) else if "%choice%"=="4" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

pause