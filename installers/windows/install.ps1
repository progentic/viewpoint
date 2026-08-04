param(
    [Parameter(Mandatory = $true)][string]$CatalogPath,
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")),
    [string]$PythonExecutable = "",
    [string]$AppDataRoot = (Join-Path $env:LOCALAPPDATA "WordResearcher"),
    [switch]$DryRun
)

. (Join-Path $PSScriptRoot "common.ps1")

if (-not $PythonExecutable) {
    $PythonExecutable = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
}
$plan = New-Phase1InstallPlan "Install" $ProjectRoot $PythonExecutable $AppDataRoot $CatalogPath

if ($DryRun) {
    Invoke-Phase1DryRun $plan
} else {
    Install-Phase1Spike $plan
}
