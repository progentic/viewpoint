Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "policy.ps1")
. (Join-Path $PSScriptRoot "platform.ps1")

function Invoke-Phase1DryRun {
    param([pscustomobject]$Plan)
    Assert-Phase1PlanPolicy $Plan
    Assert-Phase1Prerequisites $Plan
    Write-Phase1DryRun $Plan
}

function Install-Phase1Spike {
    param([pscustomobject]$Plan)
    Assert-Phase1Prerequisites $Plan
    Install-PrivateMaterial $Plan
    Install-RuntimeAssets $Plan
    Install-TlsTrust $Plan
    Register-WordManifest $Plan
    $launcher = Write-CompanionLauncher $Plan
    Register-CompanionStartup $Plan $launcher
}

function Repair-Phase1Spike {
    param([pscustomobject]$Plan)
    Assert-Phase1Prerequisites $Plan
    Assert-PrivateMaterial $Plan
    Install-RuntimeAssets $Plan
    Install-TlsTrust $Plan
    Register-WordManifest $Plan
    $launcher = Write-CompanionLauncher $Plan
    Register-CompanionStartup $Plan $launcher
}

function Uninstall-Phase1Spike {
    param([pscustomobject]$Plan)
    Assert-Phase1Prerequisites $Plan
    $catalogPath = Read-RegisteredCatalogPath
    Remove-Phase1Registration $Plan
    Remove-Phase1Files $Plan $catalogPath
}
