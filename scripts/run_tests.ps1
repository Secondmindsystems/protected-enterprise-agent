$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$python = if ($env:PEA_PYTHON) { $env:PEA_PYTHON } else { 'python' }
$env:PYTHONPATH = Join-Path $repo 'src'
& $python -m unittest discover -s (Join-Path $repo 'tests') -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
