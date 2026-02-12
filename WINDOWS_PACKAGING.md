# Windows Packaging (Reserved Interface)

Current strategy: package CLI first, GUI later.

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

Template override (no config file change):

```powershell
.\dist\docforge.exe --input .\examples\sample_tech.md --output .\output\sample.docx --type gov --template-dir C:\DocForge\templates
```

## Notes

- `ToolRunner` abstraction already supports custom binary paths.
- Future GUI can call `BuildService.run(...)` directly.
