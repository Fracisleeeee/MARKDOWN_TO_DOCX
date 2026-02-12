# Offline Deployment Guide

## 1. On internet-connected machine

```bash
bash scripts/prepare_offline_bundle.sh
```

This fills:
- `third_party/python/`
- `third_party/npm/`

## 2. Transfer bundle to intranet machine

Copy the entire `MARKDOWN_TO_DOCX` directory or at minimum:
- `requirements.txt`
- `third_party/python/`
- `third_party/npm/`
- `scripts/install_offline.sh`

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
