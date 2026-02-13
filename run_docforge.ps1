$ErrorActionPreference = "Stop"
# $root = Split-Path -Parent $MyInvocation.MyCommand.Path

# # Ensure bundled tools are preferred
# $env:Path = "$root\tools\pandoc;$root\tools\node;$env:Path"

# # quick check
# & "$root\tools\pandoc\pandoc.exe" --version | Out-Null
# & "$root\tools\mmdc\mmdc.cmd" --version | Out-Null

# # delegate to packaged app
# & "$root\docforge.exe" @args
# exit $LASTEXITCODE

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:Path = "$root\tools\mmdc;$root\tools\node;$root\tools\pandoc;$env:Path"
$bundledChrome = Join-Path $root "tools\chromium\chrome.exe"
$edge64 = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
$edge86 = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if (Test-Path $bundledChrome) {
  $env:PUPPETEER_EXECUTABLE_PATH = $bundledChrome
} elseif (Test-Path $edge64) {
  $env:PUPPETEER_EXECUTABLE_PATH = $edge64
} elseif (Test-Path $edge86) {
  $env:PUPPETEER_EXECUTABLE_PATH = $edge86
}

$puppeteerCache = Join-Path $root "tools\puppeteer-cache"
if (-not (Test-Path $puppeteerCache)) {
  New-Item -ItemType Directory -Force -Path $puppeteerCache | Out-Null
}
$env:PUPPETEER_CACHE_DIR = $puppeteerCache

& "$root\docforge.exe" --config "$root\config\templates.yaml" @args
exit $LASTEXITCODE
