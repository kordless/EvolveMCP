@echo off
echo Claude Process Cleanup Utility
echo ============================
echo.

python claude_cleanup.py --force
echo.
echo Press any key to exit...
pause > nul
