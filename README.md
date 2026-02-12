# MARKDOWN_TO_DOCX (DocForge)

Markdown -> DOCX build pipeline with multi-template routing, Mermaid rendering, Lua filters, and traceable build metadata.

## Architecture

- `src/docforge/core/`: build domain logic (`BuildOptions`, `BuildResult`, `BuildService`)
- `src/docforge/adapters/`: external tool adapters (`ToolRunner`)
- `src/docforge/cli/`: CLI entry
- `build.py`: compatibility entrypoint
- `docforge_cli.py`: module/packaging entrypoint

## Quick Start

```bash
python3 build.py \
  --input examples/sample_tech.md \
  --output output/sample_tech.docx \
  --type tech \
  --config config/templates.yaml
```

Equivalent module launch from repo root:

```bash
python3 docforge_cli.py --input examples/sample_tech.md --output output/sample_tech.docx --type tech
```

## CLI Options

- `--input` required
- `--output` required
- `--type` optional
- `--config` optional (default `config/templates.yaml`)
- `--template-dir` optional (override directory for template `.docx`)
- `--no-mermaid` optional
- `--verbose` optional

Template override example (without editing config):

```bash
python3 build.py \
  --input examples/sample_tech.md \
  --output output/sample_tech.docx \
  --type gov \
  --template-dir /opt/docforge/templates
```

## Exit Codes

- `0` success
- `1` argument/config error
- `2` pandoc conversion error
- `3` template configuration error
- `4` Mermaid rendering error

## Windows/Offline

- Offline bundle: see `OFFLINE_DEPLOY.md`
- Windows EXE packaging: see `WINDOWS_PACKAGING.md`
- Windows scripts: `scripts/package_windows.ps1`, `scripts/test_packaged.ps1`
