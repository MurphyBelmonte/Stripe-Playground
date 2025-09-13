@echo off
echo.
echo ============================================
echo  Financial Command Center AI - Quick Launch
echo  With Browser-Trusted Certificates
echo ============================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo [1/3] Regenerating browser-trusted certificates...
python cert_manager.py --mkcert
if errorlevel 1 (
    echo Error: Failed to generate trusted certificates
    pause
    exit /b 1
)

echo.
echo [2/3] Starting Financial Command Center...
echo.

REM Run the launcher
python financial_launcher.py

echo.
echo [3/3] Application is running in system tray
echo You can close this window - the app will continue running
echo.
pause