param(
  [string]$Profile
)

$ErrorActionPreference = 'Stop'

function Invoke-ComposeUp {
  param([string]$Profile)
  if ($Profile) {
    Write-Host "[docker-up] Bringing up stack (profile: $Profile)"
    docker compose --profile $Profile up -d --build
  }
  else {
    Write-Host "[docker-up] Bringing up stack"
    docker compose up -d --build
  }
}

Invoke-ComposeUp -Profile $Profile

Write-Host "[docker-up] Waiting for health..."
for ($i = 0; $i -lt 30; $i++) {
  try {
    $resp = Invoke-WebRequest -Uri "https://localhost/health" -UseBasicParsing -SkipCertificateCheck -TimeoutSec 3
    if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
      Write-Host "[docker-up] Service healthy. Launching setup wizard..."
      Start-Process "https://localhost/setup" | Out-Null
      exit 0
    }
  } catch {}
  Start-Sleep -Seconds 2
}

Write-Host "[docker-up] Health check timed out. Open https://localhost/setup in your browser."

