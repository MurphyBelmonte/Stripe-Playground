#!/usr/bin/env sh
set -euo pipefail

echo "[entrypoint] Starting Financial Command Center container"
echo "[entrypoint] UID: $(id -u), GID: $(id -g)"

# Optional: auto-generate certs inside app container (usually handled by cert-manager service)
AUTO_GENERATE_CERTS=${AUTO_GENERATE_CERTS:-false}
CERT_DIR=${CERT_DIR:-/app/certs}

if [ "$AUTO_GENERATE_CERTS" = "true" ]; then
  if [ ! -f "$CERT_DIR/server.crt" ] || [ ! -f "$CERT_DIR/server.key" ]; then
    echo "[entrypoint] Generating certificates (AUTO_GENERATE_CERTS=true)"
    python cert_manager.py --generate || echo "[entrypoint] Certificate generation optional; continuing"
  fi
fi

# Print first-run setup hint
python - <<'PY'
import os
try:
  from setup_wizard import is_setup_required
  first_run = is_setup_required()
except Exception:
  first_run = False

if first_run and not os.getenv('STRIPE_API_KEY'):
  print('[entrypoint] First-time setup detected. The web wizard will be available at:')
  print('[entrypoint]   https://localhost/setup  (via reverse proxy)')
  print('[entrypoint]   or http://localhost:8000/setup (inside container/network)')
PY

echo "[entrypoint] Launching: $*"
exec "$@"

