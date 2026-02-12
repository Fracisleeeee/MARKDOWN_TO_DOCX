from __future__ import annotations

import argparse
import sys
from pathlib import Path

from docforge.core.models import BuildOptions
from docforge.core.service import BuildService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Multi-template Markdown to DOCX builder")
    parser.add_argument("--input", required=True, help="Input markdown file")
    parser.add_argument("--output", required=True, help="Output docx path")
    parser.add_argument("--type", dest="doc_type", help="Template type (gov|tech|compliance|audit)")
    parser.add_argument(
        "--config",
        default="config/templates.yaml",
        help="Path to template config YAML (default: config/templates.yaml)",
    )
    parser.add_argument("--no-mermaid", action="store_true", help="Disable Mermaid rendering")
    parser.add_argument("--verbose", action="store_true", help="Verbose logs")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_dir = Path(__file__).resolve().parents[3]
    service = BuildService(base_dir=base_dir)

    options = BuildOptions(
        input_path=Path(args.input),
        output_path=Path(args.output),
        template_type=args.doc_type,
        config_path=Path(args.config),
        enable_mermaid=not args.no_mermaid,
        verbose=args.verbose,
    )

    result = service.run(options)

    for warning in result.warnings:
        print(f"[WARN] {warning.code}: {warning.message}")

    if result.exit_code != 0:
        if result.error:
            print(f"[ERROR] {result.error.message}", file=sys.stderr)
            stderr = result.error.details.get("stderr") if result.error.details else None
            if stderr:
                print(stderr, file=sys.stderr)
        return result.exit_code

    if result.output_path:
        print(f"[OK] Generated DOCX: {result.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
