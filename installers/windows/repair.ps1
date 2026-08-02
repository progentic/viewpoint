param(
    [Parameter(Mandatory = $true)][string]$CatalogPath,
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")),
    [string]$PythonExecutable = "",
    [string]$AppDataRoot = (Join-Path $env:LOCALAPPDATA "WordResearcher")
)

. (Join-Path $PSScriptRoot "common.ps1")

function Repair-Phase1Spike {
    if (-not $PythonExecutable) { $script:PythonExecutable = Join-Path $ProjectRoot ".venv\Scripts\python.exe" }
    Assert-Phase1Prerequisites $ProjectRoot $PythonExecutable $CatalogPath
    Assert-PrivateMaterial $ProjectRoot $PythonExecutable $AppDataRoot
    Install-TlsTrust $AppDataRoot
    Register-WordManifest $ProjectRoot $CatalogPath
    $launcher = Write-CompanionLauncher $ProjectRoot $PythonExecutable $AppDataRoot
    Register-CompanionStartup $launcher
}

Repair-Phase1Spike
