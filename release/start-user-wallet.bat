@echo off
REM PieraCoin User Wallet Startup Script
REM No dependencies required - all bundled!

title PieraCoin Miner & Wallet
echo.
echo ========================================
echo    PieraCoin Miner & Wallet
echo ========================================
echo.

REM Set server URL if not already set
if not defined SERVER_URL set SERVER_URL=https://pieracoin.onrender.com

echo Connecting to server: %SERVER_URL%
echo.

cd /d "%~dp0"
start PieraCoin-Wallet.exe

echo Wallet app launched in new window
echo.
pause
