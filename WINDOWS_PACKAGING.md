# Windows Packaging (Reserved Interface)

Current strategy: package CLI first, GUI later.

## Prepare Mermaid browser runtime (required for intranet bundle)

Run on an internet-connected Windows packaging machine:

```powershell
.\scripts\prepare_bundle_tools.ps1
```

This downloads Chromium revision `1108766` and prepares:

- `tools/chromium/chrome.exe`
- `tools/puppeteer/` (download cache/metadata)

## Build EXE (on Windows)

```powershell
.\scripts\package_windows.ps1 -Clean
```

## Expected output

- `dist/docforge.exe`

## Test packaged executable

```powershell
.\scripts\test_packaged.ps1
.\scripts\test_packaged.ps1 -RunBuildTest
```

`-RunBuildTest` requires `pandoc` available in `PATH`.

Mermaid runtime checks:

- `run_docforge.ps1` will prefer `tools/chromium/chrome.exe`
- If not found, it falls back to system Edge:
  - `C:\Program Files\Microsoft\Edge\Application\msedge.exe`
  - `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
- Puppeteer cache is forced to `tools/puppeteer-cache`

Template override (no config file change):

```powershell
.\dist\docforge.exe --input .\examples\sample_tech.md --output .\output\sample.docx --type gov --template-dir C:\DocForge\templates
```

## Notes

- `ToolRunner` abstraction already supports custom binary paths.
- Future GUI can call `BuildService.run(...)` directly.
- Mermaid failure semantics remain unchanged: if browser launch fails, process returns exit code `4`.
