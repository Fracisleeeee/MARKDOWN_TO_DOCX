from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import yaml

from docforge.adapters.tool_runner import SubprocessToolRunner, ToolRunner, ToolRunnerError
from docforge.core.models import (
    BuildError,
    BuildOptions,
    BuildResult,
    BuildWarning,
    EXIT_ARG_ERROR,
    EXIT_CONVERT_ERROR,
    EXIT_MERMAID_ERROR,
    EXIT_OK,
    EXIT_TEMPLATE_ERROR,
)

MERMAID_BLOCK_RE = re.compile(r"```mermaid[ \t]*\n(.*?)```", re.DOTALL)
META_SCHEMA_VERSION = "1.0"


class BuildService:
    def __init__(self, base_dir: Path, tool_runner: ToolRunner | None = None) -> None:
        self.base_dir = base_dir.resolve()
        self.tool_runner = tool_runner

    def run(self, options: BuildOptions) -> BuildResult:
        input_path = options.input_path.expanduser().resolve()
        output_path = options.output_path.expanduser().resolve()

        config_path = options.config_path
        if not config_path.is_absolute():
            config_path = (self.base_dir / config_path).resolve()

        if not input_path.exists():
            return self._fail(EXIT_ARG_ERROR, f"Input file not found: {input_path}")

        if not config_path.exists():
            return self._fail(EXIT_ARG_ERROR, f"Config not found: {config_path}")

        try:
            config = self._load_yaml(config_path)
        except Exception as exc:
            return self._fail(EXIT_ARG_ERROR, f"Invalid config YAML: {exc}")

        templates = config.get("templates", {})
        defaults = config.get("defaults", {})
        tools_cfg = config.get("tools", {})
        if not isinstance(templates, dict) or not templates:
            return self._fail(EXIT_ARG_ERROR, "templates config is empty or invalid")

        runner = self.tool_runner
        if runner is None:
            pandoc_path = tools_cfg.get("pandoc") if isinstance(tools_cfg, dict) else None
            mmdc_path = tools_cfg.get("mmdc") if isinstance(tools_cfg, dict) else None
            runner = SubprocessToolRunner(pandoc_path=pandoc_path, mmdc_path=mmdc_path)

        raw_markdown = input_path.read_text(encoding="utf-8")
        front_matter, markdown_body = self._parse_front_matter(raw_markdown)

        selected_type = options.template_type or front_matter.get("template") or defaults.get("type", "tech")
        if selected_type not in templates:
            available = ", ".join(sorted(templates.keys()))
            return self._fail(EXIT_TEMPLATE_ERROR, f"Unknown template type '{selected_type}'. Available: {available}")

        template_cfg = templates[selected_type]
        reference_doc = template_cfg.get("reference_doc")
        if not reference_doc:
            return self._fail(EXIT_TEMPLATE_ERROR, f"Missing reference_doc for template '{selected_type}'")

        reference_doc_path = Path(reference_doc)
        if not reference_doc_path.is_absolute():
            reference_doc_path = (self.base_dir / reference_doc_path).resolve()

        if not reference_doc_path.exists():
            return self._fail(EXIT_TEMPLATE_ERROR, f"Template file not found: {reference_doc_path}")

        toc_enabled = self._as_bool(front_matter.get("toc"), self._as_bool(defaults.get("toc"), True))
        mermaid_enabled = options.enable_mermaid and self._as_bool(
            front_matter.get("mermaid"), self._as_bool(defaults.get("mermaid"), True)
        )
        number_sections = self._as_bool(
            front_matter.get("number_sections"), self._as_bool(defaults.get("number_sections"), True)
        )
        page_break_h1 = self._as_bool(
            front_matter.get("page_break_h1"), self._as_bool(defaults.get("page_break_h1"), True)
        )

        logs_dir = (self.base_dir / "logs").resolve()
        cache_dir = (self.base_dir / ".cache" / "mermaid").resolve()
        logs_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        warnings = self._detect_table_warnings(markdown_body)

        mermaid_rendered = 0
        if mermaid_enabled:
            result = self._replace_mermaid_with_svg(markdown_body, cache_dir, runner)
            if isinstance(result, BuildError):
                return BuildResult(exit_code=result.code, error=result, warnings=warnings)
            markdown_body, mermaid_rendered = result
        elif MERMAID_BLOCK_RE.search(markdown_body):
            warnings.append(
                BuildWarning(
                    code="MERMAID_SKIPPED",
                    message="Mermaid blocks detected and kept as code blocks because Mermaid rendering is disabled.",
                )
            )

        cmd_args = self._pandoc_args(
            input_markdown="",
            output_path=output_path,
            reference_doc_path=reference_doc_path,
            selected_type=selected_type,
            toc_enabled=toc_enabled,
            number_sections=number_sections,
            page_break_h1=page_break_h1,
            front_matter=front_matter,
        )

        with NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tmp:
            tmp_path = Path(tmp.name)
            if front_matter:
                tmp.write("---\n")
                tmp.write(yaml.safe_dump(front_matter, sort_keys=False, allow_unicode=True))
                tmp.write("---\n\n")
            tmp.write(markdown_body)

        cmd_args[0] = str(tmp_path)

        try:
            pandoc_proc = runner.run_pandoc(cmd_args)
        except ToolRunnerError as exc:
            tmp_path.unlink(missing_ok=True)
            return self._fail(EXIT_CONVERT_ERROR, str(exc))

        tmp_path.unlink(missing_ok=True)

        if pandoc_proc.returncode != 0:
            details = {"stderr": pandoc_proc.stderr.strip(), "stdout": pandoc_proc.stdout.strip()}
            return BuildResult(
                exit_code=EXIT_CONVERT_ERROR,
                warnings=warnings,
                error=BuildError(EXIT_CONVERT_ERROR, "pandoc conversion failed", details),
            )

        output_sha = self._sha256_file(output_path)
        sha_file = logs_dir / "SHA256SUMS"
        with sha_file.open("a", encoding="utf-8") as fh:
            fh.write(f"{output_sha}  {output_path}\n")

        versions = runner.get_versions()

        build_meta = {
            "schema_version": META_SCHEMA_VERSION,
            "input": str(input_path),
            "output": str(output_path),
            "input_sha256": self._sha256_file(input_path),
            "output_sha256": output_sha,
            "template_type": selected_type,
            "reference_doc": str(reference_doc_path),
            "config": str(config_path),
            "options": {
                "toc": toc_enabled,
                "number_sections": number_sections,
                "page_break_h1": page_break_h1,
                "mermaid": mermaid_enabled,
                "verbose": options.verbose,
            },
            "front_matter": front_matter,
            "mermaid": {
                "blocks_detected": len(MERMAID_BLOCK_RE.findall(raw_markdown)),
                "blocks_rendered": mermaid_rendered,
                "cache_dir": str(cache_dir),
            },
            "warnings": [w.__dict__ for w in warnings],
            "tool_versions": versions,
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }

        meta_path = logs_dir / "build_meta.json"
        with meta_path.open("w", encoding="utf-8") as fh:
            json.dump(build_meta, fh, indent=2, ensure_ascii=False)

        return BuildResult(
            exit_code=EXIT_OK,
            output_path=output_path,
            warnings=warnings,
            meta_path=meta_path,
            sha_path=sha_file,
        )

    def _replace_mermaid_with_svg(
        self,
        markdown_text: str,
        cache_dir: Path,
        runner: ToolRunner,
    ) -> tuple[str, int] | BuildError:
        count = 0

        def _replace(match: re.Match[str]) -> str:
            nonlocal count
            count += 1
            source = match.group(1).strip() + "\n"
            digest = self._sha256_text(source)
            mmd_path = cache_dir / f"{digest}.mmd"
            svg_path = cache_dir / f"{digest}.svg"
            if not svg_path.exists():
                mmd_path.write_text(source, encoding="utf-8")
                try:
                    mermaid_proc = runner.run_mermaid(mmd_path, svg_path)
                except ToolRunnerError as exc:
                    raise RuntimeError(str(exc))
                if mermaid_proc.returncode != 0:
                    msg = (mermaid_proc.stderr or mermaid_proc.stdout).strip() or "Unknown Mermaid rendering error"
                    raise RuntimeError(f"Mermaid block #{count}: {msg}")
            return f"![Mermaid diagram {count}]({svg_path.resolve().as_posix()})\n"

        try:
            converted = MERMAID_BLOCK_RE.sub(_replace, markdown_text)
        except RuntimeError as exc:
            return BuildError(EXIT_MERMAID_ERROR, str(exc))

        return converted, count

    def _pandoc_args(
        self,
        input_markdown: str,
        output_path: Path,
        reference_doc_path: Path,
        selected_type: str,
        toc_enabled: bool,
        number_sections: bool,
        page_break_h1: bool,
        front_matter: dict[str, Any],
    ) -> list[str]:
        filters_dir = (self.base_dir / "filters").resolve()
        args = [
            input_markdown,
            "--from",
            "gfm+yaml_metadata_block",
            "--to",
            "docx",
            "--output",
            str(output_path),
            "--reference-doc",
            str(reference_doc_path),
            "--lua-filter",
            str(filters_dir / "toc.lua"),
            "--lua-filter",
            str(filters_dir / "pagination.lua"),
            "-M",
            f"template_type={selected_type}",
            "-M",
            f"page_break_h1={'true' if page_break_h1 else 'false'}",
            "-M",
            f"toc_enabled={'true' if toc_enabled else 'false'}",
        ]
        if toc_enabled:
            args.append("--toc")
        if number_sections:
            args.append("--number-sections")

        for k in ["title", "author", "date", "version"]:
            if k in front_matter and front_matter[k] is not None:
                args.extend(["-M", f"{k}={front_matter[k]}"])
        return args

    @staticmethod
    def _as_bool(value: Any, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            v = value.strip().lower()
            if v in {"1", "true", "yes", "on"}:
                return True
            if v in {"0", "false", "no", "off"}:
                return False
        if isinstance(value, int):
            return value != 0
        return default

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            raise ValueError("expected mapping")
        return data

    @staticmethod
    def _parse_front_matter(raw_text: str) -> tuple[dict[str, Any], str]:
        if not raw_text.startswith("---\n"):
            return {}, raw_text
        lines = raw_text.splitlines(keepends=True)
        end = None
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                end = idx
                break
        if end is None:
            return {}, raw_text
        meta_text = "".join(lines[1:end])
        body = "".join(lines[end + 1 :])
        metadata = yaml.safe_load(meta_text) or {}
        if not isinstance(metadata, dict):
            metadata = {}
        return metadata, body

    @staticmethod
    def _sha256_text(data: str) -> str:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def _sha256_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _detect_table_warnings(md_text: str) -> list[BuildWarning]:
        warnings: list[BuildWarning] = []
        if re.search(r"<(td|th)[^>]*(rowspan|colspan)=", md_text, flags=re.IGNORECASE):
            warnings.append(
                BuildWarning(
                    code="TABLE_UNSUPPORTED_SPAN",
                    message="Detected rowspan/colspan in HTML table; MVP does not support merged cells.",
                )
            )

        if re.search(r"<table", md_text, flags=re.IGNORECASE) and re.search(
            r"<table[\s\S]*<table", md_text, flags=re.IGNORECASE
        ):
            warnings.append(
                BuildWarning(
                    code="TABLE_UNSUPPORTED_NESTED",
                    message="Detected nested HTML table; MVP does not support nested tables.",
                )
            )

        for idx, line in enumerate(md_text.splitlines(), start=1):
            if "|" in line and len(line) > 160:
                warnings.append(
                    BuildWarning(
                        code="TABLE_POSSIBLY_WIDE",
                        message=f"Line {idx} looks like a wide table row (>160 chars); Word layout may wrap.",
                    )
                )
        return warnings

    @staticmethod
    def _fail(code: int, msg: str) -> BuildResult:
        return BuildResult(exit_code=code, error=BuildError(code, msg))
