# Windows Packaging (Reserved Interface)

Current strategy: package CLI first, GUI later.

## Build EXE (on Windows)

```powershell
py -m pip install -r requirements.txt
py -m pip install pyinstaller==6.16.0
pyinstaller packaging/pyinstaller.spec
```

## Expected output

- `dist/docforge.exe`

## Notes

- `ToolRunner` abstraction already supports custom binary paths.
- Future GUI can call `BuildService.run(...)` directly.
