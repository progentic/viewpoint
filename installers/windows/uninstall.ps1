param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")),
    [string]$PythonExecutable = "",
    [string]$AppDataRoot = (Join-Path $env:LOCALAPPDATA "WordResearcher")
)

. (Join-Path $PSScriptRoot "common.ps1")

function Uninstall-Phase1Spike {
    if (-not $PythonExecutable) { $script:PythonExecutable = Join-Path $ProjectRoot ".venv\Scripts\python.exe" }
    $catalogPath = (Get-ItemProperty $CatalogRegistryPath -Name "Url" -ErrorAction SilentlyContinue).Url
    Remove-Phase1Registration $ProjectRoot $PythonExecutable $AppDataRoot
    if ($catalogPath) { Remove-Item (Join-Path $catalogPath "word-researcher.xml") -Force -ErrorAction SilentlyContinue }
    Remove-Item (Join-Path $AppDataRoot "run-companion.ps1") -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $AppDataRoot "state\companion.sqlite3") -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $AppDataRoot "tls") -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $AppDataRoot "content") -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item $AppDataRoot -Force -ErrorAction SilentlyContinue
}

Uninstall-Phase1Spike
