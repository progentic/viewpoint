param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")),
    [string]$PythonExecutable = (Get-Command python).Source,
    [string]$NodeExecutable = (Get-Command node).Source,
    [switch]$RunLifecycle
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Phase1WindowsTests {
    Test-PowerShellParsing
    Test-DryRunPlans
    if ($RunLifecycle) {
        Test-IsolatedLifecycle
    }
    Write-Output "windows-phase1-tests: PASS"
}

function Test-PowerShellParsing {
    $scripts = Get-ChildItem (Join-Path $ProjectRoot "installers\windows") -Filter "*.ps1" -Recurse
    foreach ($script in $scripts) {
        $tokens = $null
        $errors = $null
        [void][System.Management.Automation.Language.Parser]::ParseFile(
            $script.FullName,
            [ref]$tokens,
            [ref]$errors
        )
        Assert-Phase1 ($errors.Count -eq 0) "PowerShell parser failed: $($script.Name)"
    }
}

function Test-DryRunPlans {
    $testRoot = New-TestRoot
    try {
        $catalog = New-Item -ItemType Directory -Path (Join-Path $testRoot "catalog")
        $appData = Join-Path $testRoot "app-data"
        foreach ($operation in @("install", "repair")) {
            $result = & (Join-Path $ProjectRoot "installers\windows\$operation.ps1") `
                -CatalogPath $catalog.FullName -ProjectRoot $ProjectRoot `
                -PythonExecutable $PythonExecutable -AppDataRoot $appData -DryRun | ConvertFrom-Json
            Assert-DryRunResult $result $operation
        }
        $uninstall = & (Join-Path $ProjectRoot "installers\windows\uninstall.ps1") `
            -ProjectRoot $ProjectRoot -PythonExecutable $PythonExecutable `
            -AppDataRoot $appData -DryRun | ConvertFrom-Json
        Assert-DryRunResult $uninstall "uninstall"
        Assert-Phase1 (-not (Test-Path $appData)) "Dry-run mutated application data"
        Assert-Phase1 (-not (Test-Path (Join-Path $catalog "word-researcher.xml"))) `
            "Dry-run registered a manifest"
    } finally {
        Remove-Item $testRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Test-IsolatedLifecycle {
    $testRoot = New-TestRoot
    $catalog = New-Item -ItemType Directory -Path (Join-Path $testRoot "catalog")
    $appData = Join-Path $testRoot "app-data"
    $rootThumbprint = ""
    try {
        Invoke-Installer "install" $catalog.FullName $appData
        $rootThumbprint = Read-TrustedRootThumbprint $appData
        Assert-InstallationSecretExists
        Wait-ForCompanion
        Invoke-ProductionOriginTest $appData $testRoot
        $fingerprints = Read-TlsFingerprints $appData
        Invoke-Installer "repair" $catalog.FullName $appData
        Invoke-Installer "repair" $catalog.FullName $appData
        Assert-TlsFingerprints $appData $fingerprints
        Assert-RegistrationState $catalog.FullName $appData $rootThumbprint
        Assert-RuntimeState $appData
        Assert-InstallationSecretExists
    } finally {
        & (Join-Path $ProjectRoot "installers\windows\uninstall.ps1") `
            -ProjectRoot $ProjectRoot -PythonExecutable $PythonExecutable -AppDataRoot $appData
        Assert-UninstalledState $catalog.FullName $appData $rootThumbprint
        Assert-InstallationSecretRemoved
        Remove-Item $testRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Assert-RuntimeState {
    param([string]$AppDataRoot)
    $runtimeRoot = Join-Path $AppDataRoot "runtime"
    Assert-Phase1 (Test-Path (Join-Path $runtimeRoot "companion\src\researcher_companion\main.py")) `
        "Installed companion source is missing"
    Assert-Phase1 (Test-Path (Join-Path $runtimeRoot "companion\migrations\0001_phase1_runtime.sql")) `
        "Installed migration is missing"
    Assert-Phase1 (Test-Path (Join-Path $runtimeRoot "taskpane\dist\index.html")) `
        "Installed task pane is missing"
}

function Invoke-ProductionOriginTest {
    param([string]$AppDataRoot, [string]$TestRoot)
    & $PythonExecutable (Join-Path $ProjectRoot "scripts\run_installed_production_origin_test.py") `
        --node $NodeExecutable --app-data $AppDataRoot `
        --output (Join-Path $TestRoot "windows-production-origin.json")
    if ($LASTEXITCODE -ne 0) { throw "Windows production-origin test failed" }
}

function Invoke-Installer {
    param([string]$Operation, [string]$CatalogPath, [string]$AppDataRoot)
    & (Join-Path $ProjectRoot "installers\windows\$Operation.ps1") `
        -CatalogPath $CatalogPath -ProjectRoot $ProjectRoot `
        -PythonExecutable $PythonExecutable -AppDataRoot $AppDataRoot
}

function Wait-ForCompanion {
    foreach ($attempt in 1..60) {
        if (Test-NetConnection -ComputerName 127.0.0.1 -Port 4179 `
            -InformationLevel Quiet -WarningAction SilentlyContinue) {
            return
        }
        Start-Sleep -Milliseconds 250
    }
    throw "Scheduled companion did not start on loopback"
}

function Read-TlsFingerprints {
    param([string]$AppDataRoot)
    return @{
        Root = (Get-FileHash (Join-Path $AppDataRoot "tls\root-ca.pem") -Algorithm SHA256).Hash
        Leaf = (Get-FileHash (Join-Path $AppDataRoot "tls\server-cert.pem") -Algorithm SHA256).Hash
    }
}

function Assert-TlsFingerprints {
    param([string]$AppDataRoot, [hashtable]$Expected)
    $actual = Read-TlsFingerprints $AppDataRoot
    Assert-Phase1 ($actual.Root -eq $Expected.Root) "Repair rotated the root certificate"
    Assert-Phase1 ($actual.Leaf -eq $Expected.Leaf) "Repair rotated the server certificate"
}

function Assert-RegistrationState {
    param([string]$CatalogPath, [string]$AppDataRoot, [string]$RootThumbprint)
    Assert-Phase1 (Test-Path (Join-Path $CatalogPath "word-researcher.xml")) `
        "Manifest registration is missing"
    Assert-Phase1 (Test-Path (Join-Path $AppDataRoot "tls\trusted-root-thumbprint.txt")) `
        "Trusted-root record is missing"
    $task = Get-ScheduledTask -TaskName "Word Researcher Local Companion" -ErrorAction Stop
    Assert-Phase1 ($null -ne $task) "Scheduled Task registration is missing"
    $trustedRoots = @(Get-ChildItem Cert:\CurrentUser\Root | Where-Object Thumbprint -eq $RootThumbprint)
    Assert-Phase1 ($trustedRoots.Count -eq 1) "Repair produced duplicate trusted roots"
}

function Assert-UninstalledState {
    param([string]$CatalogPath, [string]$AppDataRoot, [string]$RootThumbprint)
    Assert-Phase1 (-not (Test-Path $AppDataRoot)) "Application data remains after uninstall"
    Assert-Phase1 (-not (Test-Path (Join-Path $CatalogPath "word-researcher.xml"))) `
        "Manifest remains after uninstall"
    $task = Get-ScheduledTask -TaskName "Word Researcher Local Companion" `
        -ErrorAction SilentlyContinue
    Assert-Phase1 ($null -eq $task) "Scheduled Task remains after uninstall"
    if ($RootThumbprint) {
        $trustedRoot = Get-Item "Cert:\CurrentUser\Root\$RootThumbprint" `
            -ErrorAction SilentlyContinue
        Assert-Phase1 ($null -eq $trustedRoot) "Trusted root remains after uninstall"
    }
}

function Read-TrustedRootThumbprint {
    param([string]$AppDataRoot)
    return (Get-Content (Join-Path $AppDataRoot "tls\trusted-root-thumbprint.txt") -Raw).Trim()
}

function Assert-InstallationSecretExists {
    $exitCode = Invoke-SecretCheck
    Assert-Phase1 ($exitCode -eq 0) "Installation credential is missing"
}

function Assert-InstallationSecretRemoved {
    $exitCode = Invoke-SecretCheck
    Assert-Phase1 ($exitCode -ne 0) "Installation credential remains after uninstall"
}

function Invoke-SecretCheck {
    $previousPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = Join-Path $ProjectRoot "companion\src"
        & $PythonExecutable -m researcher_companion.install_cli check-secret 2>$null
        return $LASTEXITCODE
    } finally {
        $env:PYTHONPATH = $previousPythonPath
    }
}

function Assert-DryRunResult {
    param([pscustomobject]$Result, [string]$Operation)
    Assert-Phase1 $Result.DryRun "Dry-run marker is missing"
    Assert-Phase1 ($Result.Plan.Operation -eq (Get-Culture).TextInfo.ToTitleCase($Operation)) `
        "Dry-run operation mismatch"
    Assert-Phase1 ($Result.Plan.StableOrigin -eq "https://localhost:4179") `
        "Dry-run stable origin mismatch"
    Assert-Phase1 ($Result.Plan.BindAddress -eq "127.0.0.1") `
        "Dry-run bind policy mismatch"
}

function New-TestRoot {
    $path = Join-Path ([System.IO.Path]::GetTempPath()) ("viewpoint-phase1-" + [guid]::NewGuid())
    return (New-Item -ItemType Directory -Path $path).FullName
}

function Assert-Phase1 {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

Invoke-Phase1WindowsTests
