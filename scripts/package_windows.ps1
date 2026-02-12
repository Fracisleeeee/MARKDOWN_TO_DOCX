[CmdletBinding()]
param(
  [switch]$Clean,
  [switch]$SkipDeps,
  [string]$PythonExe = "py",
  [string]$VenvDir = ".venv"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

Write-Host "[INFO] Project root: $ProjectRoot"

if ($Clean) {
  Write-Host "[INFO] Cleaning build/dist directories"
  if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
  if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
}

if (-not (Test-Path $VenvDir)) {
  Write-Host "[INFO] Creating virtual environment at $VenvDir"
  & $PythonExe -m venv $VenvDir
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
  throw "Venv python not found: $VenvPython"
}

if (-not $SkipDeps) {
  Write-Host "[INFO] Installing packaging dependencies"
  & $VenvPython -m pip install --upgrade pip
  & $VenvPython -m pip install -r requirements.txt
  & $VenvPython -m pip install pyinstaller==6.16.0
}

if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
  Write-Warning "pandoc not found in PATH. Packaged EXE can be created but runtime conversion will fail until pandoc is installed."
}

if (-not (Get-Command mmdc -ErrorAction SilentlyContinue)) {
  Write-Warning "mmdc not found in PATH. Mermaid rendering will fail until mmdc is installed."
}

Write-Host "[INFO] Running PyInstaller"
& $VenvPython -m PyInstaller packaging/pyinstaller.spec --noconfirm

$ExePath = Join-Path $ProjectRoot "dist\docforge.exe"
if (-not (Test-Path $ExePath)) {
  throw "Packaging failed: $ExePath not found"
}

Write-Host "[OK] Packaged executable: $ExePath"
