param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")),
    [string]$PythonExecutable = "",
    [string]$AppDataRoot = (Join-Path $env:LOCALAPPDATA "WordResearcher"),
    [switch]$DryRun
)

. (Join-Path $PSScriptRoot "common.ps1")

if (-not $PythonExecutable) {
    $PythonExecutable = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
}
$plan = New-Phase1InstallPlan "Uninstall" $ProjectRoot $PythonExecutable $AppDataRoot

if ($DryRun) {
    Invoke-Phase1DryRun $plan
} else {
    Uninstall-Phase1Spike $plan
}
