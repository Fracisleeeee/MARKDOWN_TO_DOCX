# Offline Deployment Guide

## 1. On internet-connected machine

```bash
bash scripts/prepare_offline_bundle.sh
```

This fills:
- `third_party/python/`
- `third_party/npm/`

For Windows bundle Mermaid rendering, also run:

```powershell
.\scripts\prepare_bundle_tools.ps1
```

This prepares Chromium runtime at `tools/chromium/chrome.exe`.

## 2. Transfer bundle to intranet machine

Copy the entire `MARKDOWN_TO_DOCX` directory or at minimum:
- `requirements.txt`
- `third_party/python/`
- `third_party/npm/`
- `scripts/install_offline.sh`
- `tools/chromium/` (or ensure Edge exists on target machine)
- `run_docforge.ps1`
- `config/templates.yaml`

## 3. Install on intranet machine

```bash
bash scripts/install_offline.sh
```

## 4. Verify

```bash
python3 build.py --help
mmdc --version
pandoc --version
```

Windows bundle runtime checks:

- `run_docforge.ps1` injects `PUPPETEER_EXECUTABLE_PATH` (bundled Chromium first, Edge fallback).
- `run_docforge.ps1` injects `PUPPETEER_CACHE_DIR=tools/puppeteer-cache`.
