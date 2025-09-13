# Financial Command Center AI - Launcher Build Script (PowerShell)
# ================================================================

param(
    [switch]$Clean = $false,
    [switch]$SkipDeps = $false,
    [string]$OutputDir = "installer_package"
)

Write-Host "🚀 Building Financial Command Center AI Launcher" -ForegroundColor Green
Write-Host "=" * 60

# Check if Python is available
try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Python not found. Please install Python 3.8+ and add it to PATH." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ and add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if main script exists
if (-not (Test-Path "financial_launcher.py")) {
    Write-Host "❌ Main script not found: financial_launcher.py" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Yellow
    exit 1
}

# Clean previous builds if requested
if ($Clean) {
    Write-Host "🧹 Cleaning previous build artifacts..." -ForegroundColor Yellow
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "financial_launcher.spec") { Remove-Item -Force "financial_launcher.spec" }
    if (Test-Path $OutputDir) { Remove-Item -Recurse -Force $OutputDir }
    Write-Host "✅ Cleaned build directories" -ForegroundColor Green
}

# Install dependencies if not skipped
if (-not $SkipDeps) {
    Write-Host "📦 Installing build dependencies..." -ForegroundColor Yellow
    try {
        & python -m pip install --upgrade pip
        & python -m pip install -r launcher_requirements.txt
        Write-Host "✅ Build dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install dependencies: $_" -ForegroundColor Red
        exit 1
    }
}

# Run the Python build script
Write-Host "🔨 Running build process..." -ForegroundColor Yellow
try {
    & python build_launcher.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build process failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Build process failed: $_" -ForegroundColor Red
    exit 1
}

# Check if executable was created
$exePath = "dist\Financial-Command-Center-Launcher.exe"
if (Test-Path $exePath) {
    $size = (Get-Item $exePath).Length / 1MB
    Write-Host "✅ Executable created: $exePath ($($size.ToString('F1')) MB)" -ForegroundColor Green
} else {
    Write-Host "❌ Executable not found after build" -ForegroundColor Red
    exit 1
}

# Create installer package info
if (Test-Path $OutputDir) {
    Write-Host "📦 Installer package created in: $OutputDir" -ForegroundColor Green
    Write-Host "Package contents:" -ForegroundColor Cyan
    Get-ChildItem $OutputDir | ForEach-Object {
        $sizeKB = if ($_.PSIsContainer) { "DIR" } else { "$([math]::Round($_.Length / 1KB, 1)) KB" }
        Write-Host "  📄 $($_.Name) ($sizeKB)" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "🎉 Build completed successfully!" -ForegroundColor Green
Write-Host "🚀 Ready for distribution!" -ForegroundColor Cyan

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the executable: .\$exePath" -ForegroundColor White
Write-Host "2. Distribute the installer package in: $OutputDir" -ForegroundColor White
Write-Host "3. Users can run Financial-Command-Center-Launcher.exe to start" -ForegroundColor White

# Optional: Open the output directory
$choice = Read-Host "Open output directory? (y/n)"
if ($choice -eq "y" -or $choice -eq "Y") {
    if (Test-Path $OutputDir) {
        Invoke-Item $OutputDir
    }
}