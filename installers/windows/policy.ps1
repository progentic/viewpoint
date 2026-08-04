Set-StrictMode -Version Latest

$script:Phase1CatalogId = "{8F663F3F-80AF-4F20-A32F-4A226F7671F5}"
$script:Phase1ScheduledTaskName = "Word Researcher Local Companion"
$script:Phase1StableHostname = "localhost"
$script:Phase1StablePort = 4179

function New-Phase1InstallPlan {
    param(
        [ValidateSet("Install", "Repair", "Uninstall")][string]$Operation,
        [string]$ProjectRoot,
        [string]$PythonExecutable,
        [string]$AppDataRoot,
        [string]$CatalogPath = ""
    )
    $plan = [ordered]@{
        SchemaVersion = 1
        Operation = $Operation
        StableHostname = $script:Phase1StableHostname
        StablePort = $script:Phase1StablePort
        StableOrigin = "https://$($script:Phase1StableHostname):$($script:Phase1StablePort)"
        BindAddress = "127.0.0.1"
        ProjectRoot = $ProjectRoot
        PythonExecutable = $PythonExecutable
        AppDataRoot = $AppDataRoot
        RuntimeRoot = (Join-Path $AppDataRoot "runtime")
        TlsDirectory = (Join-Path $AppDataRoot "tls")
        CatalogPath = $CatalogPath
        CatalogId = $script:Phase1CatalogId
        ScheduledTaskName = $script:Phase1ScheduledTaskName
        IntendedOperations = (Get-Phase1IntendedOperations $Operation)
    }
    $result = [pscustomobject]$plan
    Assert-Phase1PlanPolicy $result
    return $result
}

function Assert-Phase1PlanPolicy {
    param([pscustomobject]$Plan)
    if ($Plan.StableHostname -ne "localhost") {
        throw "Stable hostname policy mismatch"
    }
    if ($Plan.StablePort -ne 4179 -or $Plan.BindAddress -ne "127.0.0.1") {
        throw "Stable loopback policy mismatch"
    }
    foreach ($property in @("ProjectRoot", "PythonExecutable", "AppDataRoot")) {
        if ([string]::IsNullOrWhiteSpace($Plan.$property)) {
            throw "Installation plan is missing $property"
        }
    }
    if ($Plan.Operation -ne "Uninstall" -and [string]::IsNullOrWhiteSpace($Plan.CatalogPath)) {
        throw "Install and repair require a Word testing catalog path"
    }
}

function Write-Phase1DryRun {
    param([pscustomobject]$Plan)
    [ordered]@{
        DryRun = $true
        Plan = $Plan
    } | ConvertTo-Json -Depth 5
}

function Get-Phase1IntendedOperations {
    param([string]$Operation)
    switch ($Operation) {
        "Install" { return @("validate", "provision", "trust", "manifest", "startup") }
        "Repair" { return @("validate", "retain-private-material", "trust", "manifest", "startup") }
        "Uninstall" { return @("startup", "trust", "credential", "manifest", "files") }
    }
}
