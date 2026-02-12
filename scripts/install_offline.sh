#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_DIR="$ROOT_DIR/third_party/python"
NPM_DIR="$ROOT_DIR/third_party/npm"

if ! command -v pip >/dev/null 2>&1; then
  echo "pip not found" >&2
  exit 1
fi

pip install --no-index --find-links="$PY_DIR" -r "$ROOT_DIR/requirements.txt"

PKG="$(ls "$NPM_DIR"/mermaid-js-mermaid-cli-*.tgz 2>/dev/null | head -n 1 || true)"
if [[ -z "$PKG" ]]; then
  echo "mermaid package not found in $NPM_DIR" >&2
  exit 1
fi

npm install -g "$PKG"

echo "offline install completed"
