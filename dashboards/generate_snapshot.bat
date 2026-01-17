@echo off
REM Generate State Snapshot for Cockpit Dashboard
REM This script generates cockpit_state.out.json from system state files

echo ========================================
echo Agent Orchestrator - State Snapshot Generator
echo ========================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"
cd ..

REM Try py launcher first (Windows Python launcher)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using Python launcher (py)...
    echo.
    py scripts\cockpit__generate__state_snapshot.py
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo Snapshot generated successfully!
        echo ========================================
        echo.
        echo Output: dashboards\cockpit_state.out.json
        echo.
        echo You can now:
        echo   1. Open dashboards\cockpit_template.html
        echo   2. Click "Load State File"
        echo   3. Select cockpit_state.out.json
        echo.
        pause
        exit /b 0
    ) else (
        echo.
        echo ERROR: Snapshot generation failed
        pause
        exit /b 1
    )
)

REM Fallback: Try python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using python command...
    echo.
    python scripts\cockpit__generate__state_snapshot.py
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo Snapshot generated successfully!
        echo ========================================
        echo.
        echo Output: dashboards\cockpit_state.out.json
        echo.
        pause
        exit /b 0
    ) else (
        echo.
        echo ERROR: Snapshot generation failed
        pause
        exit /b 1
    )
)

REM Fallback: Try venv Python directly
if exist ".venv\Scripts\python.exe" (
    echo Using virtual environment Python...
    echo.
    .venv\Scripts\python.exe scripts\cockpit__generate__state_snapshot.py
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo Snapshot generated successfully!
        echo ========================================
        echo.
        echo Output: dashboards\cockpit_state.out.json
        echo.
        pause
        exit /b 0
    ) else (
        echo.
        echo ERROR: Snapshot generation failed
        pause
        exit /b 1
    )
)

REM If we get here, no Python found
echo.
echo ERROR: Python not found
echo.
echo Please ensure Python 3.x is installed and available via:
echo   - py command (Windows Python launcher - recommended)
echo   - python command
echo   - .venv\Scripts\python.exe (virtual environment)
echo.
pause
exit /b 1
