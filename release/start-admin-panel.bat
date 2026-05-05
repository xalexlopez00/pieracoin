@echo off
REM PieraCoin Admin Panel Startup Script
REM No dependencies required - all bundled!

title PieraCoin Admin Panel
echo.
echo ========================================
echo    PieraCoin Admin Panel
echo ========================================
echo.

REM Set server URL if not already set
if not defined SERVER_URL set SERVER_URL=https://pieracoin.onrender.com

echo Connecting to server: %SERVER_URL%
echo.

cd /d "%~dp0"
start PieraCoin-Admin.exe

echo Admin panel launched in new window
echo.
pause
