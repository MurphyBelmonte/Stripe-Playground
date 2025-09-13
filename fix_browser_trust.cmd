@echo off
echo.
echo ============================================================
echo  Financial Command Center AI - Browser Trust Fix
echo ============================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo Step 1: Installing mkcert CA certificate to Windows trust store...
echo.

REM Install mkcert CA certificate to current user root store
powershell -Command "try { Import-Certificate -FilePath 'C:\Users\Hi\AppData\Local\mkcert\rootCA.pem' -CertStoreLocation 'Cert:\CurrentUser\Root' -ErrorAction Stop; Write-Host 'Success: mkcert CA installed to user certificate store' -ForegroundColor Green } catch { Write-Host 'Info: Certificate may already be installed' -ForegroundColor Yellow }"

echo.
echo Step 2: Generating fresh mkcert certificates...
echo.

python cert_manager.py --mkcert

echo.
echo Step 3: Checking certificate health...
echo.

python cert_manager.py --health

echo.
echo Step 4: Testing the fix...
echo.

echo Starting Financial Command Center to test browser trust...
echo Your browser will open automatically.
echo.
echo ✅ SUCCESS INDICATORS:
echo    - Green lock icon in browser address bar  
echo    - "Secure" or "https://" without warnings
echo    - No "Not Secure" text
echo.
echo ❌ IF STILL NOT WORKING:
echo    - Close browser completely (all windows)
echo    - Wait 10 seconds  
echo    - Restart browser
echo    - Clear browser cache (Ctrl+Shift+Delete)
echo    - Try visiting https://localhost:8000 again
echo.

timeout /T 3 /NOBREAK >nul

REM Launch the application
python financial_launcher.py

echo.
echo ============================================================
echo  Browser Trust Fix Complete!
echo ============================================================
echo.
echo If you still see "Not Secure" warnings:
echo 1. Completely close and restart your browser
echo 2. Clear browser cache and cookies for localhost
echo 3. Try visiting https://localhost:8000 again
echo.
echo For manual troubleshooting:
echo - Run: python cert_manager.py --health
echo - Run: python test_ssl_trust.py
echo - Check: BROWSER_TRUST_GUIDE.md
echo.
pause