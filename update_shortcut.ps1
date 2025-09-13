# Update Desktop Shortcut to Use Trusted Certificate Launcher
# Financial Command Center AI

Write-Host "Updating desktop shortcut to use trusted certificate launcher..." -ForegroundColor Green

# Get current directory
$currentDir = (Get-Location).Path
$newLauncher = Join-Path $currentDir "Launch-With-Trusted-Certs.cmd"

# Check if new launcher exists
if (-not (Test-Path $newLauncher)) {
    Write-Host "Error: Launch-With-Trusted-Certs.cmd not found in current directory" -ForegroundColor Red
    exit 1
}

# Desktop shortcut path
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Financial Command Center AI.lnk"

if (Test-Path $shortcutPath) {
    # Update existing shortcut
    Write-Host "Found existing shortcut: $shortcutPath" -ForegroundColor Yellow
    
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    
    # Update shortcut properties
    $shortcut.TargetPath = $newLauncher
    $shortcut.WorkingDirectory = $currentDir
    $shortcut.Arguments = ""
    $shortcut.Description = "Financial Command Center AI - Secure Launch with Browser-Trusted Certificates"
    $shortcut.WindowStyle = 1  # Normal window
    
    # Save the updated shortcut
    $shortcut.Save()
    
    Write-Host "✅ Desktop shortcut updated successfully!" -ForegroundColor Green
    Write-Host "   Target: $newLauncher" -ForegroundColor Cyan
    Write-Host "   The shortcut will now use browser-trusted certificates automatically." -ForegroundColor Cyan
} else {
    # Create new shortcut
    Write-Host "Creating new desktop shortcut..." -ForegroundColor Yellow
    
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    
    $shortcut.TargetPath = $newLauncher
    $shortcut.WorkingDirectory = $currentDir
    $shortcut.Arguments = ""
    $shortcut.Description = "Financial Command Center AI - Secure Launch with Browser-Trusted Certificates"
    $shortcut.WindowStyle = 1  # Normal window
    
    # Save the new shortcut
    $shortcut.Save()
    
    Write-Host "✅ New desktop shortcut created!" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔐 Your desktop shortcut now automatically ensures browser-trusted certificates!" -ForegroundColor Green
Write-Host "🌐 Double-click the shortcut to launch with secure HTTPS (no browser warnings)" -ForegroundColor Green

# Also update Start Menu shortcut if it exists
$startMenuPath = Join-Path ([Environment]::GetFolderPath("Programs")) "Financial Command Center AI\Financial Command Center AI.lnk"
if (Test-Path $startMenuPath) {
    Write-Host ""
    Write-Host "Updating Start Menu shortcut..." -ForegroundColor Yellow
    
    $startMenuShortcut = $shell.CreateShortcut($startMenuPath)
    $startMenuShortcut.TargetPath = $newLauncher
    $startMenuShortcut.WorkingDirectory = $currentDir
    $startMenuShortcut.Arguments = ""
    $startMenuShortcut.Description = "Financial Command Center AI - Secure Launch with Browser-Trusted Certificates"
    $startMenuShortcut.WindowStyle = 1
    $startMenuShortcut.Save()
    
    Write-Host "✅ Start Menu shortcut also updated!" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 You can now double-click the shortcut to launch with trusted certificates!" -ForegroundColor Magenta