param(
    [string]$VendorRoot = $env:PROTEGRITY_DEV_EDITION_ROOT
)
$ErrorActionPreference = 'Stop'
if (-not $VendorRoot) { throw 'Set PROTEGRITY_DEV_EDITION_ROOT to the pinned official repository clone.' }
docker compose -f (Join-Path $VendorRoot 'data-discovery\docker-compose.yml') up -d
docker compose -f (Join-Path $VendorRoot 'semantic-guardrail\docker-compose.yml') up -d

