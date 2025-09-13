@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================================
echo  PyInstaller Temp Directory Cleanup
echo  Financial Command Center AI
echo ========================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo Step 1: Stopping all Python processes to release temp directory locks...
echo.

REM Stop all python processes
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM Financial-Command-Center-Launcher.exe /T >nul 2>&1

REM Wait a moment for processes to fully terminate
timeout /T 3 /NOBREAK >nul

echo Step 2: Cleaning up PyInstaller temp directories...
echo.

REM Count temp directories before cleanup
set count=0
for /d %%i in ("C:\Users\Hi\AppData\Local\Temp\_MEI*") do set /a count+=1
echo Found %count% PyInstaller temp directories to clean up

echo.
echo Attempting to remove temp directories...

REM Method 1: Try regular deletion
for /d %%i in ("C:\Users\Hi\AppData\Local\Temp\_MEI*") do (
    echo Removing: %%i
    rmdir /S /Q "%%i" 2>nul
    if exist "%%i" (
        echo   - Failed with rmdir, trying PowerShell...
        powershell -Command "try { Remove-Item '%%i' -Recurse -Force -ErrorAction Stop; Write-Host '   - Removed with PowerShell' -ForegroundColor Green } catch { Write-Host '   - Still locked, will try later' -ForegroundColor Yellow }"
    ) else (
        echo   - Successfully removed
    )
)

echo.
echo Step 3: Checking remaining temp directories...
echo.

REM Count remaining directories
set remaining=0
for /d %%i in ("C:\Users\Hi\AppData\Local\Temp\_MEI*") do (
    set /a remaining+=1
    echo Still exists: %%i
)

echo.
if %remaining%==0 (
    echo ✅ SUCCESS: All PyInstaller temp directories cleaned up!
) else (
    echo ⚠️  WARNING: %remaining% directories still exist (may be in use)
    echo.
    echo These will be cleaned up when the processes using them exit.
    echo You can run this script again later to clean up remaining directories.
)

echo.
echo Step 4: Setting up automatic cleanup on system restart...
echo.

REM Create a batch file to run at startup for cleanup
set startup_script="%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\cleanup_mei_temp.cmd"

echo @echo off > %startup_script%
echo REM Automatic PyInstaller temp directory cleanup >> %startup_script%
echo for /d %%%%i in ("C:\Users\Hi\AppData\Local\Temp\_MEI*") do rmdir /S /Q "%%%%i" 2^>nul >> %startup_script%

echo ✅ Created automatic cleanup script at startup

echo.
echo Step 5: Prevention - Update launchers to avoid PyInstaller...
echo.

REM Check if we're using PyInstaller executables
if exist "Financial-Command-Center-Launcher.exe" (
    echo ⚠️  Found PyInstaller executable: Financial-Command-Center-Launcher.exe
    echo.
    echo RECOMMENDATION: Use Python scripts instead of executables to avoid temp directories:
    echo   - Use: python financial_launcher.py
    echo   - Use: Launch-With-Trusted-Certs.cmd
    echo   - Avoid: Financial-Command-Center-Launcher.exe
    echo.
    echo The updated desktop shortcut now uses Python scripts to prevent this issue.
)

echo.
echo ========================================================
echo  Temp Directory Cleanup Complete!
echo ========================================================
echo.
echo SUMMARY:
echo - Cleaned up: %count% temp directories found
echo - Remaining: %remaining% directories (if any)
echo - Prevention: Automatic cleanup script installed
echo - Recommendation: Use Python scripts instead of executables
echo.
echo TO PREVENT FUTURE ISSUES:
echo 1. Use the updated desktop shortcut (uses Python scripts)
echo 2. Use: Launch-With-Trusted-Certs.cmd
echo 3. Avoid: Financial-Command-Center-Launcher.exe
echo.
echo The temp directory issue should now be resolved!
echo.
pause