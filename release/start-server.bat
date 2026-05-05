@echo off
REM PieraCoin Server Startup Script
REM No dependencies required - just run!

title PieraCoin Node Server
echo.
echo ========================================
echo    PieraCoin Node Starting
echo ========================================
echo.

REM Set default port if not already set
if not defined PORT set PORT=8080

echo Starting server on port %PORT%...
echo.

cd /d "%~dp0"
pieracoin.exe

pause
