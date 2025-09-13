#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PROFILE="${1:-}"

echo "[docker-up] Bringing up stack (profile: ${PROFILE:-default})"
if [ -n "$PROFILE" ]; then
  docker compose --profile "$PROFILE" up -d --build
else
  docker compose up -d --build
fi

echo "[docker-up] Waiting for health..."
for i in {1..30}; do
  if curl -fsS -k https://localhost/health >/dev/null 2>&1; then
    echo "[docker-up] Service healthy. Opening setup wizard..."
    if command -v xdg-open >/dev/null 2>&1; then
      xdg-open https://localhost/setup || true
    elif command -v open >/dev/null 2>&1; then
      open https://localhost/setup || true
    else
      echo "Open https://localhost/setup in your browser to complete setup."
    fi
    exit 0
  fi
  sleep 2
done

echo "[docker-up] Health check timed out. Access https://localhost/setup manually."

