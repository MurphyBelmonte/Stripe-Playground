@echo off
echo.
echo Updating desktop shortcut to use trusted certificate launcher...
echo.

powershell -Command "try { $currentDir = (Get-Location).Path; $newLauncher = Join-Path $currentDir 'Launch-With-Trusted-Certs.cmd'; $desktopPath = [Environment]::GetFolderPath('Desktop'); $shortcutPath = Join-Path $desktopPath 'Financial Command Center AI.lnk'; $shell = New-Object -ComObject WScript.Shell; $shortcut = $shell.CreateShortcut($shortcutPath); $shortcut.TargetPath = $newLauncher; $shortcut.WorkingDirectory = $currentDir; $shortcut.Arguments = ''; $shortcut.Description = 'Financial Command Center AI - Secure Launch'; $shortcut.WindowStyle = 1; $shortcut.Save(); Write-Host 'Success: Desktop shortcut updated!' } catch { Write-Host 'Error:' $_.Exception.Message }"

echo.
echo ✅ Your desktop shortcut has been updated!
echo 🔐 It will now automatically ensure browser-trusted certificates.
echo 🌐 Double-click the shortcut to launch with secure HTTPS.
echo.
pause