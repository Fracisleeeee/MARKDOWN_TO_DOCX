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

## Notes

- `ToolRunner` abstraction already supports custom binary paths.
- Future GUI can call `BuildService.run(...)` directly.
