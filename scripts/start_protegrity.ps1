param(
    [string]$VendorRoot = $env:PROTEGRITY_DEV_EDITION_ROOT
)
$ErrorActionPreference = 'Stop'
if (-not $VendorRoot) { throw 'Set PROTEGRITY_DEV_EDITION_ROOT to the pinned official repository clone.' }
$vendorSha = git -C $VendorRoot rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $vendorSha.Trim() -ne '15c113c10ba71b272e0e7515b04e2f81b8b6afe7') {
    throw 'Vendor checkout is not at the required pinned commit.'
}
$composeVersion = docker compose version --short
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose is unavailable.' }
$parsedComposeVersion = [version](($composeVersion.Trim()).TrimStart('v').Split('-')[0])
if ($parsedComposeVersion -lt [version]'2.30.0') { throw 'Docker Compose 2.30 or newer is required.' }
$dockerOs = docker info --format '{{.OSType}}'
if ($LASTEXITCODE -ne 0 -or $dockerOs.Trim() -ne 'linux') { throw 'Docker must be running Linux containers.' }
docker compose -f (Join-Path $VendorRoot 'data-discovery\docker-compose.yml') up -d
docker compose -f (Join-Path $VendorRoot 'semantic-guardrail\docker-compose.yml') up -d
