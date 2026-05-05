@echo off
REM Build script for PieraCoin client applications
REM Requires PyInstaller to be installed: pip install pyinstaller

echo.
echo ========================================
echo PieraCoin Client Applications Builder
echo ========================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller not installed!
    echo Run: pip install pyinstaller
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install -q -r requirements.txt

echo [2/3] Building Admin Panel...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
pyinstaller ^
  --onefile ^
  --name "PieraCoin-Admin" ^
  --console ^
  --add-data ".:." ^
  admin_panel.py

if errorlevel 1 (
    echo ERROR: Failed to build Admin Panel
    pause
    exit /b 1
)

echo.
echo [3/3] Building User Wallet...
if exist "build" rmdir /s /q build
pyinstaller ^
  --onefile ^
  --name "PieraCoin-Wallet" ^
  --console ^
  --add-data ".:." ^
  user_wallet.py

if errorlevel 1 (
    echo ERROR: Failed to build User Wallet
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Files created in 'dist' folder:
echo   - PieraCoin-Admin.exe
echo   - PieraCoin-Wallet.exe
echo.
echo Before running Admin panel, set environment variable:
echo   set ADMIN_KEY=your-secret-key-here
echo.
echo Before running User wallet, set environment variable:
echo   set SERVER_URL=http://localhost:8080
echo.
pause
