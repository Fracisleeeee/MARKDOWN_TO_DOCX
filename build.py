#!/usr/bin/env python3
"""Compatibility entrypoint.

Legacy command remains:
  python build.py --input ... --output ...
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docforge.cli.main import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
