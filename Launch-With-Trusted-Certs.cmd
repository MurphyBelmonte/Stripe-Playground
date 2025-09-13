@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Change to this script's directory
pushd "%~dp0"

echo.
echo ==============================================
echo   Financial Command Center AI - Secure Launch
echo ==============================================
echo.

REM Step 1: Ensure we have browser-trusted certificates
echo Step 1: Checking SSL certificates...
python cert_manager.py --health | find "Mkcert Available" | find "True" >nul
if errorlevel 1 (
    echo Warning: mkcert not available, using self-signed certificates
    goto :skip_mkcert
)

python cert_manager.py --health | find "Trust Installed" | find "True" >nul
if errorlevel 1 (
    echo Generating browser-trusted certificates...
    python cert_manager.py --mkcert
    if errorlevel 1 (
        echo Warning: Failed to generate trusted certificates, continuing anyway...
    ) else (
        echo ✅ Browser-trusted certificates ready!
    )
) else (
    echo ✅ Browser-trusted certificates already installed!
)

:skip_mkcert

REM Step 2: Find Python executable
echo.
echo Step 2: Starting application...
set "PY_EXE="
if exist ".venv\Scripts\pythonw.exe" set "PY_EXE=.venv\Scripts\pythonw.exe"
if not defined PY_EXE (
  for %%P in (pyw.exe pythonw.exe) do (
    where %%P >nul 2>&1 && set "PY_EXE=%%P" && goto :gotpy
  )
)
:gotpy
if not defined PY_EXE (
  echo pythonw.exe not found. Trying console python...
  for %%P in (py.exe python.exe) do (
    where %%P >nul 2>&1 && set "PY_EXE=%%P" && goto :gotpy2
  )
)
:gotpy2
if not defined PY_EXE (
  echo Could not find Python. Please install Python 3.8+ and try again.
  pause
  popd
  endlocal
  exit /b 1
)

REM Step 3: Pick the best entry point
set "APP=financial_launcher.py"
if not exist "%APP%" (
  if exist "app_with_setup_wizard.py" set "APP=app_with_setup_wizard.py"
)
if not exist "%APP%" (
  if exist "app.py" set "APP=app.py"
)

REM Step 4: Launch with no console window
echo Starting Financial Command Center with trusted certificates...
echo Opening browser to https://localhost:8000
echo.
start "" /B "%PY_EXE%" "%APP%"

echo Application is running in the background and system tray.
echo You can safely close this window.
echo.
echo To access the application later, use the system tray icon
echo or visit: https://localhost:8000
echo.
timeout /T 5 /NOBREAK >nul

popd
endlocal