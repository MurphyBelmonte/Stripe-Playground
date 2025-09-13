@echo off
setlocal enabledelayedexpansion

echo.
echo ================================================================
echo  ULTIMATE SSL CERTIFICATE FIX - Financial Command Center AI
echo ================================================================
echo.
echo This will fix "Not Secure" warnings in ALL browsers
echo.

REM Change to script directory
cd /d "%~dp0"

REM Kill any running python processes
echo Step 1: Stopping any running instances...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM Financial-Command-Center-Launcher.exe /T >nul 2>&1

REM Wait a moment
timeout /T 2 /NOBREAK >nul

echo Step 2: Installing mkcert CA to SYSTEM certificate store (requires admin)...
echo.

REM Try to install to Local Machine (requires admin rights)
powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList '-Command', 'try { Import-Certificate -FilePath ''C:\Users\Hi\AppData\Local\mkcert\rootCA.pem'' -CertStoreLocation ''Cert:\LocalMachine\Root'' -ErrorAction Stop; Write-Host ''SUCCESS: Certificate installed to Local Machine store'' -ForegroundColor Green } catch { Write-Host ''INFO: Could not install to Local Machine (needs admin rights)'' -ForegroundColor Yellow }' -Wait"

echo.
echo Step 3: Installing to Current User certificate store...
powershell -Command "try { Import-Certificate -FilePath 'C:\Users\Hi\AppData\Local\mkcert\rootCA.pem' -CertStoreLocation 'Cert:\CurrentUser\Root' -ErrorAction Stop; Write-Host 'SUCCESS: Certificate installed to Current User store' -ForegroundColor Green } catch { Write-Host 'WARNING: Could not install to Current User store' -ForegroundColor Red }"

echo.
echo Step 4: Generating new mkcert certificates...
python cert_manager.py --mkcert

echo.
echo Step 5: Testing certificate installation...
python cert_manager.py --health

echo.
echo Step 6: Manual browser certificate installation...
echo.

REM Create a temp certificate in an easy location
copy "C:\Users\Hi\AppData\Local\mkcert\rootCA.pem" "%USERPROFILE%\Desktop\mkcert-rootCA.crt" >nul 2>&1

echo A copy of the root certificate has been placed on your Desktop:
echo %USERPROFILE%\Desktop\mkcert-rootCA.crt
echo.
echo MANUAL BROWSER SETUP (if automatic installation didn't work):
echo.
echo FOR CHROME/EDGE:
echo 1. Open Chrome/Edge Settings
echo 2. Search for "certificates" 
echo 3. Click "Manage certificates"
echo 4. Go to "Trusted Root Certification Authorities" tab
echo 5. Click "Import" and select the certificate from your Desktop
echo 6. Restart browser
echo.
echo FOR FIREFOX:
echo 1. Open Firefox Settings
echo 2. Search for "certificates"
echo 3. Click "View Certificates"
echo 4. Go to "Authorities" tab  
echo 5. Click "Import" and select the certificate from your Desktop
echo 6. Check "Trust this CA to identify websites"
echo 7. Restart browser
echo.

echo Step 7: Starting Financial Command Center...
echo.
echo IMPORTANT: After the app starts:
echo 1. COMPLETELY close your browser (all windows)
echo 2. Wait 10 seconds
echo 3. Clear browser cache (Ctrl+Shift+Delete)
echo 4. Restart browser
echo 5. Visit https://localhost:8000
echo.

timeout /T 5 /NOBREAK >nul

REM Launch using Python script directly (not PyInstaller executable)
echo Starting with Python script to avoid PyInstaller issues...
python financial_launcher.py

echo.
echo ================================================================
echo  Certificate Fix Complete!
echo ================================================================
echo.
echo IF YOU STILL SEE "NOT SECURE":
echo.
echo 1. RESTART your browser completely
echo 2. CLEAR all browser data for localhost
echo 3. Try DIFFERENT browsers (Chrome, Firefox, Edge)
echo 4. Import the certificate manually using instructions above
echo.
echo Certificate location: %USERPROFILE%\Desktop\mkcert-rootCA.crt
echo.
pause