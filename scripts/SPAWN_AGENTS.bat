@echo off
REM Batch wrapper for spawning agents
REM Quick command to spawn IDLE agents to generate reports

cd /d "%~dp0\.."
python scripts\execution__spawn_agents.py %*

pause
