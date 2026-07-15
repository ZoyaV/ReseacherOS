#!/usr/bin/env bash
# Local dev server for ResearchOS Hub.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
if [[ -f hub/.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source hub/.env
  set +a
fi
# Avoid broken system proxy for GitHub; github_http.py falls back if direct fails.
export HUB_GITHUB_NETWORK="${HUB_GITHUB_NETWORK:-direct}"
export PYTHONPATH="$ROOT"
export HUB_PUBLIC_URL="${HUB_PUBLIC_URL:-http://127.0.0.1:8020}"
export HUB_DATA_DIR="${HUB_DATA_DIR:-$ROOT/hub/.data}"
exec "$ROOT/.venv/bin/python" -m uvicorn hub.app.main:app --host 127.0.0.1 --port 8020 --reload
