from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


EXIT_OK = 0
EXIT_ARG_ERROR = 1
EXIT_CONVERT_ERROR = 2
EXIT_TEMPLATE_ERROR = 3
EXIT_MERMAID_ERROR = 4


@dataclass
class BuildWarning:
    code: str
    message: str


@dataclass
class BuildError:
    code: int
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildOptions:
    input_path: Path
    output_path: Path
    template_type: str | None = None
    config_path: Path = Path("config/templates.yaml")
    enable_mermaid: bool = True
    verbose: bool = False


@dataclass
class BuildResult:
    exit_code: int
    output_path: Path | None = None
    warnings: list[BuildWarning] = field(default_factory=list)
    error: BuildError | None = None
    meta_path: Path | None = None
    sha_path: Path | None = None
