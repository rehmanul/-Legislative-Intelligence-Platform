@echo off
REM Launch Diagram Viewer - Local HTTP Server
REM This script starts a local HTTP server and opens the diagram viewer in your browser

echo ========================================
echo Agent Orchestrator - Diagram Viewer
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.x or use VS Code Live Server instead
    pause
    exit /b 1
)

REM Get the directory where this script is located
cd /d "%~dp0"
cd ..

REM Check if port 9000 is available, if not try 9001, 9002, etc.
set PORT=9000
:CHECK_PORT
netstat -an | findstr ":%PORT%" >nul 2>&1
if %errorlevel% equ 0 (
    echo Port %PORT% is in use, trying next port...
    set /a PORT+=1
    if %PORT% gtr 9010 (
        echo ERROR: Could not find available port (9000-9010)
        echo Please close other servers or manually specify a port
        pause
        exit /b 1
    )
    goto CHECK_PORT
)

echo.
echo Starting HTTP server on port %PORT%...
echo.
echo ========================================
echo Diagram Viewer URL:
echo   http://localhost:%PORT%/dashboards/diagram_viewer.html
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Wait a moment, then open browser
timeout /t 2 /nobreak >nul
start http://localhost:%PORT%/dashboards/diagram_viewer.html

REM Start Python HTTP server
python -m http.server %PORT%

pause
