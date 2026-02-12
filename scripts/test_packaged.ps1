[CmdletBinding()]
param(
  [string]$ExePath = ".\dist\docforge.exe",
  [switch]$RunBuildTest
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not (Test-Path $ExePath)) {
  throw "Executable not found: $ExePath"
}

Write-Host "[INFO] Running smoke test: --help"
& $ExePath --help | Out-Host

if ($LASTEXITCODE -ne 0) {
  throw "Smoke test failed with code $LASTEXITCODE"
}

if ($RunBuildTest) {
  Write-Host "[INFO] Running build test"
  & $ExePath --input .\examples\sample_compliance.md --output .\output\packaged_test.docx --type compliance --no-mermaid
  if ($LASTEXITCODE -ne 0) {
    throw "Build test failed with code $LASTEXITCODE"
  }
}

Write-Host "[OK] Packaged executable test passed"
