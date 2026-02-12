from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docforge.adapters.tool_runner import CompletedProcessLike, ToolRunner
from docforge.core.models import BuildOptions, EXIT_TEMPLATE_ERROR
from docforge.core.service import BuildService


class FakeRunner(ToolRunner):
    def run_pandoc(self, args):
        return CompletedProcessLike(0, "", "")

    def run_mermaid(self, input_mmd, output_svg):
        output_svg.write_text("<svg></svg>", encoding="utf-8")
        return CompletedProcessLike(0, "", "")

    def get_versions(self):
        return {"pandoc": "fake", "mmdc": "fake"}


def main() -> int:
    svc = BuildService(base_dir=ROOT, tool_runner=FakeRunner())
    opts = BuildOptions(
        input_path=ROOT / "examples" / "sample_tech.md",
        output_path=ROOT / "output" / "unit.docx",
        template_type="does_not_exist",
        enable_mermaid=False,
    )
    res = svc.run(opts)
    assert res.exit_code == EXIT_TEMPLATE_ERROR
    assert res.error is not None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
