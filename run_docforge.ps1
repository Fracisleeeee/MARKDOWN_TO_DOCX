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
& "$root\docforge.exe" --config "$root\config\templates.yaml" @args
exit $LASTEXITCODE
