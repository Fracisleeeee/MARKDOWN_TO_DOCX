[CmdletBinding()]
param(
  [string]$Revision = "1108766",
  [string]$ToolsRoot = "tools"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

$PuppeteerRoot = Join-Path $ProjectRoot (Join-Path $ToolsRoot "puppeteer")
$ChromiumRoot = Join-Path $ProjectRoot (Join-Path $ToolsRoot "chromium")

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
  throw "npx not found in PATH. Install Node.js on the packaging machine first."
}

Write-Host "[INFO] Installing Chromium revision $Revision with @puppeteer/browsers"
& npx --yes @puppeteer/browsers install "chrome@$Revision" --path $PuppeteerRoot

if ($LASTEXITCODE -ne 0) {
  throw "Chromium installation failed with exit code $LASTEXITCODE"
}

$chromeExe = Get-ChildItem -Path $PuppeteerRoot -Filter "chrome.exe" -File -Recurse |
  Sort-Object FullName |
  Select-Object -First 1

if (-not $chromeExe) {
  throw "chrome.exe not found under $PuppeteerRoot after installation."
}

$chromeSourceDir = Split-Path -Parent $chromeExe.FullName

if (Test-Path $ChromiumRoot) {
  Remove-Item -Recurse -Force $ChromiumRoot
}

Write-Host "[INFO] Copying Chromium runtime to $ChromiumRoot"
New-Item -ItemType Directory -Path $ChromiumRoot -Force | Out-Null
Copy-Item -Path (Join-Path $chromeSourceDir "*") -Destination $ChromiumRoot -Recurse -Force

Write-Host "[OK] Chromium prepared: $(Join-Path $ChromiumRoot 'chrome.exe')"
