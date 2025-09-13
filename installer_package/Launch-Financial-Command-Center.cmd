@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Change to this script's directory
pushd "%~dp0"

REM Prefer pythonw to avoid console window
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

REM Pick the best entry: launcher -> setup wizard -> app
set "APP=financial_launcher.py"
if not exist "%APP%" (
  if exist "app_with_setup_wizard.py" set "APP=app_with_setup_wizard.py"
)
if not exist "%APP%" (
  if exist "app.py" set "APP=app.py"
)

REM Check if app file exists
if not exist "%APP%" (
  echo Could not find application file: %APP%
  echo Please ensure the installation is complete.
  pause
  popd
  endlocal
  exit /b 1
)

echo Starting Financial Command Center AI...
echo Using: %APP%

REM Launch detached (minimized window if python.exe is used)
start "Financial Command Center AI" /B "%PY_EXE%" "%APP%"

REM Clean exit
popd
endlocal
