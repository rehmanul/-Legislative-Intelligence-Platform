@echo off
REM Change to script directory
cd /d "%~dp0"

echo ========================================
echo Starting Agent Health Dashboard...
echo ========================================
echo.

REM Get workspace root (two levels up from monitoring folder)
set "SCRIPT_DIR=%~dp0"
set "WORKSPACE_ROOT=%SCRIPT_DIR%..\.."
REM Remove trailing backslash
set "WORKSPACE_ROOT=%WORKSPACE_ROOT:~0,-1%"

REM Try to use .venv Python if it exists
set "VENV_PYTHON=%WORKSPACE_ROOT%\.venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    echo Using virtual environment Python...
    "%VENV_PYTHON%" "%~dp0dashboard-terminal.py"
) else (
    echo Using system Python...
    python "%~dp0dashboard-terminal.py"
)

if errorlevel 1 (
    echo.
    echo ERROR: Dashboard failed to start
    echo Press any key to exit...
    pause >nul
)
