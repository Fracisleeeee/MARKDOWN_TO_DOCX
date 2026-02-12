#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "usage: render_mermaid.sh <input.mmd> <output.svg>" >&2
  exit 2
fi

if ! command -v mmdc >/dev/null 2>&1; then
  echo "mmdc is not installed or not in PATH" >&2
  exit 127
fi

input="$1"
output="$2"
out_dir="$(dirname "$output")"
mkdir -p "$out_dir"

mmdc -i "$input" -o "$output" -b transparent
