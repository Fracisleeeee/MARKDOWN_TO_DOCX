#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

run_expect() {
  local expected="$1"
  shift
  set +e
  python3 "$ROOT_DIR/build.py" "$@"
  local rc=$?
  set -e
  if [[ "$rc" -ne "$expected" ]]; then
    echo "FAIL: expected rc=$expected, got rc=$rc for: $*" >&2
    exit 1
  fi
}

python3 "$ROOT_DIR/build.py" --help >/dev/null
python3 "$ROOT_DIR/docforge_cli.py" --help >/dev/null

# Invalid template should return 3.
run_expect 3 --input "$ROOT_DIR/examples/sample_tech.md" --output "$ROOT_DIR/output/t1.docx" --type bad

# Mermaid enabled without mmdc should return 4 in minimal environments.
if ! command -v mmdc >/dev/null 2>&1; then
  run_expect 4 --input "$ROOT_DIR/examples/sample_tech.md" --output "$ROOT_DIR/output/t2.docx" --type tech
fi

# Mermaid disabled without pandoc should return 2 in minimal environments.
if ! command -v pandoc >/dev/null 2>&1; then
  run_expect 2 --input "$ROOT_DIR/examples/sample_tech.md" --output "$ROOT_DIR/output/t3.docx" --type tech --no-mermaid
fi

echo "smoke tests completed"
