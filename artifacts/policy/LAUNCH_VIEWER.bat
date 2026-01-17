@echo off
REM Launch script for Policy Artifacts HTML Viewer
REM Opens viewer.html in default browser

cd /d "%~dp0"

echo ========================================
echo Policy Artifacts Viewer
echo ========================================
echo.

if not exist "viewer.html" (
    echo ERROR: viewer.html not found in current directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Opening viewer.html in default browser...
start "" "viewer.html"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to open viewer.html
    echo Please open viewer.html manually in your browser
    pause
    exit /b 1
)

echo.
echo Viewer opened successfully!
echo.
echo Note: This is a READ-ONLY POLICY CONTEXT viewer.
echo Policy artifacts are for strategic planning only.
echo.
timeout /t 2 >nul
