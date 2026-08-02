param(
    [Parameter(Mandatory = $true)][string]$CatalogPath,
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")),
    [string]$PythonExecutable = "",
    [string]$AppDataRoot = (Join-Path $env:LOCALAPPDATA "WordResearcher")
)

. (Join-Path $PSScriptRoot "common.ps1")

function Install-Phase1Spike {
    if (-not $PythonExecutable) { $script:PythonExecutable = Join-Path $ProjectRoot ".venv\Scripts\python.exe" }
    Assert-Phase1Prerequisites $ProjectRoot $PythonExecutable $CatalogPath
    New-Item -ItemType Directory -Path $AppDataRoot -Force | Out-Null
    Install-PrivateMaterial $ProjectRoot $PythonExecutable $AppDataRoot
    Install-TlsTrust $AppDataRoot
    Register-WordManifest $ProjectRoot $CatalogPath
    $launcher = Write-CompanionLauncher $ProjectRoot $PythonExecutable $AppDataRoot
    Register-CompanionStartup $launcher
}

Install-Phase1Spike
