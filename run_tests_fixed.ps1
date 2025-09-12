# run_tests_fixed.ps1 - Clean PowerShell test runner
param(
  [ValidateSet("unit","integration","all","security","api","quick","lint","format","ci")]
  [string]$Mode = "quick",
  [switch]$Install,
  [switch]$Open
)

function Invoke-Step {
  param([string]$Title, [string[]]$Cmd)
  Write-Host "`n==============================" -ForegroundColor DarkCyan
  Write-Host $Title -ForegroundColor Cyan
  Write-Host "==============================" -ForegroundColor DarkCyan
  Write-Host "Command: $($Cmd -join ' ')"
  $exe = $Cmd[0]
  $args = @()
  if ($Cmd.Count -gt 1) { $args = $Cmd[1..($Cmd.Count-1)] }
  & $exe @args
  if ($LASTEXITCODE -eq 0) { Write-Host "SUCCESS" -ForegroundColor Green; return $true }
  else { Write-Host "FAIL ($LASTEXITCODE)" -ForegroundColor Red; return $false }
}

function Install-Dependencies {
  Invoke-Step "Install test dependencies" @("python","-m","pip","install","-r","requirements-test.txt")
}

function Run-Unit { Invoke-Step "Run unit tests" @("python","-m","pytest","tests/unit","-v","--tb=short","--cov=auth","--cov-report=term-missing") }
function Run-Integration { Invoke-Step "Run integration tests" @("python","-m","pytest","tests/integration","-v","--tb=short") }
function Run-All {
  Invoke-Step "Run all tests with coverage" @(
    "python","-m","pytest","tests","-v","--tb=short",
    "--cov=auth","--cov=app",
    "--cov-report=html:htmlcov","--cov-report=term-missing","--cov-report=xml",
    "--html=reports/report.html","--self-contained-html"
  )
}
function Run-Security { Invoke-Step "Run security tests" @("python","-m","pytest","-m","security","-v","--tb=short") }
function Run-API { Invoke-Step "Run API tests" @("python","-m","pytest","-m","api","-v","--tb=short") }
function Run-Quick { Invoke-Step "Run quick tests" @("python","-m","pytest","-m","not slow","-v","--tb=line","--cov=auth","--cov-report=term") }
function Run-Format { Invoke-Step "Run Black formatter" @("python","-m","black","auth/","app.py","tests/") }
function Run-Lint {
  $ok = $true
  $ok = (Invoke-Step "Check formatting (Black)" @("python","-m","black","--check","--diff","auth/","app.py","tests/")) -and $ok
  $ok = (Invoke-Step "Check imports (isort)" @("python","-m","isort","--check-only","--diff","auth/","app.py","tests/")) -and $ok
  $ok = (Invoke-Step "Run flake8" @("python","-m","flake8","auth/","app.py","tests/")) -and $ok
  return $ok
}

function Open-Reports {
  $cov = Join-Path (Get-Location) "htmlcov/index.html"
  $rep = Join-Path (Get-Location) "reports/report.html"
  if (Test-Path $cov) { Start-Process $cov }
  if (Test-Path $rep) { Start-Process $rep }
}

Write-Host "Test Runner (PowerShell)" -ForegroundColor Green
Write-Host "Mode: $Mode" -ForegroundColor Yellow
Write-Host "Location: $(Get-Location)" -ForegroundColor Yellow

if ($Install) { if (-not (Install-Dependencies)) { exit 1 } }

$success = $true
switch ($Mode) {
  "unit" { $success = Run-Unit }
  "integration" { $success = Run-Integration }
  "all" { $success = Run-All }
  "security" { $success = Run-Security }
  "api" { $success = Run-API }
  "quick" { $success = Run-Quick }
  "lint" { $success = Run-Lint }
  "format" { $success = Run-Format }
  "ci" {
    $success = $true
    $success = (Install-Dependencies) -and $success
    $success = (Run-Format) -and $success
    $success = (Run-Lint) -and $success
    $success = (Run-All) -and $success
  }
}

if ($Open -and $success) { Open-Reports }

if ($success) { Write-Host "Done" -ForegroundColor Green; exit 0 }
else { Write-Host "Failed" -ForegroundColor Red; exit 1 }
