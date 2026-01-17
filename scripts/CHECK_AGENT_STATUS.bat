@echo off
REM Batch wrapper for agent status check
REM Quick command to check agent status without typing full Python path

cd /d "%~dp0\.."
python scripts\monitor__check_agent_status.py

pause
