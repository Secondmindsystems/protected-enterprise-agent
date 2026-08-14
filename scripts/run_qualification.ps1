param([switch]$RequireVendor)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$python = if ($env:PEA_PYTHON) { $env:PEA_PYTHON } else { 'python' }
$env:PYTHONPATH = Join-Path $repo 'src'
$argsList = @('-m', 'protected_enterprise_agent.cli', '--root', $repo)
if ($RequireVendor) { $argsList += '--require-vendor' }
& $python @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
