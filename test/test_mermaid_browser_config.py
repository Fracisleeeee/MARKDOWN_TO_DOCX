from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docforge.adapters.tool_runner import SubprocessToolRunner
from docforge.core.service import BuildService


def _test_resolve_tool_path_relative() -> None:
    svc = BuildService(base_dir=ROOT)
    resolved = svc._resolve_tool_path({"browser_executable": "tools/chromium/chrome.exe"}, "browser_executable")
    assert resolved == str((ROOT / "tools/chromium/chrome.exe").resolve())


def _test_mermaid_env_injects_browser_and_cache() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        browser = root / "chrome.exe"
        browser.write_text("fake", encoding="utf-8")
        cache_dir = root / "puppeteer-cache"

        runner = SubprocessToolRunner(
            pandoc_path=None,
            mmdc_path=None,
            browser_executable_path=str(browser),
            puppeteer_cache_dir=str(cache_dir),
        )
        env = runner._mermaid_env()
        assert env.get("PUPPETEER_EXECUTABLE_PATH") == str(browser)
        assert env.get("PUPPETEER_CACHE_DIR") == str(cache_dir)
        assert cache_dir.exists()


def _test_detect_windows_edge_path() -> None:
    detected = BuildService._detect_windows_edge_path()
    allowed = {
        None,
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    }
    assert detected in allowed


def main() -> int:
    _test_resolve_tool_path_relative()
    _test_mermaid_env_injects_browser_and_cache()
    _test_detect_windows_edge_path()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
