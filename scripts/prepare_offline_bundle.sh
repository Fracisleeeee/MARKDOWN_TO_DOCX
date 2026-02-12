#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_DIR="$ROOT_DIR/third_party/python"
NPM_DIR="$ROOT_DIR/third_party/npm"

mkdir -p "$PY_DIR" "$NPM_DIR"

if ! command -v pip >/dev/null 2>&1; then
  echo "pip not found" >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found" >&2
  exit 1
fi

pip download -r "$ROOT_DIR/requirements.txt" -d "$PY_DIR"

pushd "$NPM_DIR" >/dev/null
npm pack @mermaid-js/mermaid-cli@10.9.1
popd >/dev/null

echo "offline bundle prepared under third_party/"
