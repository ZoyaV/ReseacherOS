#!/usr/bin/env bash
# Install / migrate a project into tree/<repo>/koi-structure + <repo>/ code layout.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec python -m koi.projects.install_cli "$@"
