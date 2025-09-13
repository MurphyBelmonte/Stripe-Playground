param(
  [string]$ExePath = "dist/Financial-Command-Center-Launcher.exe",
  [string]$PfxPath = $env:SIGN_PFX_PATH,
  [string]$PfxPassword = $env:SIGN_PFX_PASSWORD,
  [string]$Subject = $env:SIGN_SUBJECT,
  [string]$TimestampUrl = $(if ($env:SIGN_TIMESTAMP_URL) { $env:SIGN_TIMESTAMP_URL } else { 'http://timestamp.digicert.com' })
)

Write-Host "Signing: $ExePath"

function Find-SignTool {
  $signtool = (Get-Command signtool -ErrorAction SilentlyContinue).Source
  if ($signtool) { return $signtool }
  $pf = ${env:ProgramFiles(x86)}
  $root = Join-Path $pf 'Windows Kits\10\bin'
  if (Test-Path $root) {
    $found = Get-ChildItem -Path $root -Recurse -Filter signtool.exe -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { return $found.FullName }
  }
  return $null
}

$st = Find-SignTool
if (-not $st) {
  Write-Warning "signtool.exe not found. Install Windows SDK or run in a Developer Command Prompt."
  exit 1
}

if (-not (Test-Path $ExePath)) { Write-Error "EXE not found: $ExePath"; exit 1 }

if (-not $PfxPath -and -not $Subject) {
  Write-Warning "No PFX or Subject provided. Use -PfxPath/-PfxPassword or -Subject, or set env SIGN_PFX_PATH/SIGN_PFX_PASSWORD or SIGN_SUBJECT."
  exit 1
}

if ($PfxPath) {
  if (-not (Test-Path $PfxPath)) { Write-Error "PFX not found: $PfxPath"; exit 1 }
  & $st sign /fd sha256 /td sha256 /tr $TimestampUrl /f $PfxPath @(
    $(if ($PfxPassword) { '/p', $PfxPassword } )
  ) $ExePath
} else {
  & $st sign /fd sha256 /td sha256 /tr $TimestampUrl /n $Subject $ExePath
}

if ($LASTEXITCODE -eq 0) { Write-Host "Signed successfully" -ForegroundColor Green } else { Write-Error "Signing failed ($LASTEXITCODE)" }

