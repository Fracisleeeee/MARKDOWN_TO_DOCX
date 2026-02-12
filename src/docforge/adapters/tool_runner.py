from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


class ToolRunnerError(RuntimeError):
    pass


@dataclass
class CompletedProcessLike:
    returncode: int
    stdout: str
    stderr: str


class ToolRunner:
    def run_pandoc(self, args: list[str]) -> CompletedProcessLike:
        raise NotImplementedError

    def run_mermaid(self, input_mmd: Path, output_svg: Path) -> CompletedProcessLike:
        raise NotImplementedError

    def get_versions(self) -> dict[str, str]:
        raise NotImplementedError


class SubprocessToolRunner(ToolRunner):
    def __init__(
        self,
        pandoc_path: str | None = None,
        mmdc_path: str | None = None,
        mmdc_config_path: str | None = None,
    ) -> None:
        self._pandoc_path = self._resolve_executable(pandoc_path, "pandoc")
        self._mmdc_path = self._resolve_executable(mmdc_path, "mmdc")
        self._mmdc_config_path = mmdc_config_path

    @staticmethod
    def _resolve_executable(override: str | None, default_name: str) -> str | None:
        if override:
            p = Path(override)
            if p.exists():
                return str(p)
            if p.suffix.lower() != ".exe":
                exe_candidate = p.with_suffix(".exe")
                if exe_candidate.exists():
                    return str(exe_candidate)
            return override

        found = shutil.which(default_name)
        if found:
            return found
        if not default_name.endswith(".exe"):
            found_exe = shutil.which(default_name + ".exe")
            if found_exe:
                return found_exe
        return None

    @staticmethod
    def _run(command: list[str]) -> CompletedProcessLike:
        try:
            proc = subprocess.run(command, capture_output=True, text=True, check=False)
        except OSError as exc:
            raise ToolRunnerError(str(exc)) from exc
        return CompletedProcessLike(proc.returncode, proc.stdout or "", proc.stderr or "")

    def run_pandoc(self, args: list[str]) -> CompletedProcessLike:
        if not self._pandoc_path:
            raise ToolRunnerError("pandoc is not installed or not in PATH")
        return self._run([self._pandoc_path, *args])

    def run_mermaid(self, input_mmd: Path, output_svg: Path) -> CompletedProcessLike:
        if not self._mmdc_path:
            raise ToolRunnerError("mmdc is not installed or not in PATH")
        output_svg.parent.mkdir(parents=True, exist_ok=True)
        cmd = [self._mmdc_path, "-i", str(input_mmd), "-o", str(output_svg), "-b", "transparent"]
        if self._mmdc_config_path:
            cfg = Path(self._mmdc_config_path)
            if cfg.exists():
                cmd.extend(["-c", str(cfg)])
        return self._run(cmd)

    def get_versions(self) -> dict[str, str]:
        return {
            "pandoc": self._version_of(self._pandoc_path, "--version"),
            "mmdc": self._version_of(self._mmdc_path, "--version"),
        }

    def _version_of(self, executable: str | None, arg: str) -> str:
        if not executable:
            return "unavailable"
        cp = self._run([executable, arg])
        line = (cp.stdout or cp.stderr).strip().splitlines()
        return line[0] if line else "unknown"


class BundledToolRunner(SubprocessToolRunner):
    """Reserved runner for future Windows EXE-bundled binary paths."""

    def __init__(self, bundle_root: Path, pandoc_rel: str = "bin/pandoc", mmdc_rel: str = "bin/mmdc") -> None:
        pandoc_path = bundle_root / pandoc_rel
        mmdc_path = bundle_root / mmdc_rel
        super().__init__(str(pandoc_path), str(mmdc_path))
