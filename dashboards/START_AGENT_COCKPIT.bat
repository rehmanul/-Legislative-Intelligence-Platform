@echo off
echo ============================================================
echo Agent Runner Cockpit Launcher
echo ============================================================
echo.

cd /d "%~dp0"

echo [INFO] Starting server on http://localhost:9000
echo [INFO] The HTML page will open automatically in your browser
echo [INFO] Keep this window open while using the cockpit
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Start the server (it will auto-open the browser)
python server.py

pause
