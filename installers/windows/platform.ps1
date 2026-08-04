Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:Phase1CatalogRegistryPath = `
    "HKCU:\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\$($script:Phase1CatalogId)"

function Assert-Phase1Prerequisites {
    param([pscustomobject]$Plan)
    if (-not (Test-Path -PathType Leaf $Plan.PythonExecutable)) {
        throw "Missing locked Python environment"
    }
    if (-not (Test-Path -PathType Leaf (Join-Path $Plan.ProjectRoot "taskpane\dist\index.html"))) {
        throw "Missing task-pane build"
    }
    if (-not (Test-Path -PathType Leaf (Join-Path $Plan.ProjectRoot "manifest\word-researcher.xml"))) {
        throw "Missing Word manifest"
    }
    if ($Plan.Operation -ne "Uninstall" -and -not (Test-Path -PathType Container $Plan.CatalogPath)) {
        throw "The required Word test catalog share is unavailable: $($Plan.CatalogPath)"
    }
}

function Invoke-InstallCli {
    param([pscustomobject]$Plan, [string[]]$Arguments)
    $previousPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = Join-Path $Plan.ProjectRoot "companion\src"
        & $Plan.PythonExecutable -m researcher_companion.install_cli @Arguments
        if ($LASTEXITCODE -ne 0) { throw "Local installation material command failed" }
    } finally {
        $env:PYTHONPATH = $previousPythonPath
    }
}

function Install-PrivateMaterial {
    param([pscustomobject]$Plan)
    New-Item -ItemType Directory -Path $Plan.AppDataRoot -Force | Out-Null
    Invoke-InstallCli $Plan @("provision", "--tls-directory", $Plan.TlsDirectory)
    Protect-PrivateMaterial $Plan.TlsDirectory
}

function Install-RuntimeAssets {
    param([pscustomobject]$Plan)
    Remove-Item $Plan.RuntimeRoot -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path (Join-Path $Plan.RuntimeRoot "companion") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $Plan.RuntimeRoot "taskpane") -Force | Out-Null
    Copy-Item (Join-Path $Plan.ProjectRoot "companion\src") `
        (Join-Path $Plan.RuntimeRoot "companion\src") -Recurse -Force
    Copy-Item (Join-Path $Plan.ProjectRoot "companion\migrations") `
        (Join-Path $Plan.RuntimeRoot "companion\migrations") -Recurse -Force
    Copy-Item (Join-Path $Plan.ProjectRoot "taskpane\dist") `
        (Join-Path $Plan.RuntimeRoot "taskpane\dist") -Recurse -Force
    Remove-RuntimeCaches $Plan.RuntimeRoot
}

function Remove-RuntimeCaches {
    param([string]$RuntimeRoot)
    Get-ChildItem $RuntimeRoot -Recurse -Directory -Filter "__pycache__" |
        Remove-Item -Recurse -Force
    Get-ChildItem $RuntimeRoot -Recurse -File -Include "*.pyc", "*.pyo" |
        Remove-Item -Force
}

function Protect-PrivateMaterial {
    param([string]$TlsDirectory)
    & icacls.exe $TlsDirectory /inheritance:r /grant:r "$($env:USERNAME):(OI)(CI)F" /T | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Windows could not restrict TLS material ACLs" }
}

function Install-TlsTrust {
    param([pscustomobject]$Plan)
    $certificatePath = Join-Path $Plan.TlsDirectory "root-ca.pem"
    $certificate = Import-Certificate -FilePath $certificatePath `
        -CertStoreLocation "Cert:\CurrentUser\Root"
    Set-Content -Path (Join-Path $Plan.TlsDirectory "trusted-root-thumbprint.txt") `
        -Value $certificate.Thumbprint -Encoding ascii -NoNewline
}

function Register-WordManifest {
    param([pscustomobject]$Plan)
    Copy-Item (Join-Path $Plan.ProjectRoot "manifest\word-researcher.xml") `
        (Join-Path $Plan.CatalogPath "word-researcher.xml") -Force
    New-Item -Path $script:Phase1CatalogRegistryPath -Force | Out-Null
    New-ItemProperty -Path $script:Phase1CatalogRegistryPath -Name "Id" `
        -Value $Plan.CatalogId -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $script:Phase1CatalogRegistryPath -Name "Url" `
        -Value $Plan.CatalogPath -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $script:Phase1CatalogRegistryPath -Name "Flags" `
        -Value 1 -PropertyType DWord -Force | Out-Null
}

function Write-CompanionLauncher {
    param([pscustomobject]$Plan)
    $launcherPath = Join-Path $Plan.AppDataRoot "run-companion.ps1"
    $pythonPath = Join-Path $Plan.RuntimeRoot "companion\src"
    $content = @"
`$env:PYTHONPATH = '$($pythonPath.Replace("'", "''"))'
`$env:WORD_RESEARCHER_DATA = '$($Plan.AppDataRoot.Replace("'", "''"))'
Set-Location '$($Plan.RuntimeRoot.Replace("'", "''"))'
& '$($Plan.PythonExecutable.Replace("'", "''"))' -m researcher_companion.main
"@
    Set-Content -Path $launcherPath -Value $content -Encoding UTF8
    return $launcherPath
}

function Register-CompanionStartup {
    param([pscustomobject]$Plan, [string]$LauncherPath)
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$LauncherPath`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
    Register-ScheduledTask -TaskName $Plan.ScheduledTaskName -Action $action `
        -Trigger $trigger -Principal $principal -Force | Out-Null
    Start-ScheduledTask -TaskName $Plan.ScheduledTaskName
}

function Assert-PrivateMaterial {
    param([pscustomobject]$Plan)
    $required = @(
        "root-ca.pem", "root-ca-key.pem", "server-cert.pem", "server-key.pem", "tls-metadata.json"
    )
    foreach ($name in $required) {
        if (-not (Test-Path -PathType Leaf (Join-Path $Plan.TlsDirectory $name))) {
            throw "TLS repair requires reinstall: $name is missing"
        }
    }
    Invoke-InstallCli $Plan @("check-secret")
}

function Read-RegisteredCatalogPath {
    $registration = Get-ItemProperty $script:Phase1CatalogRegistryPath `
        -Name "Url" -ErrorAction SilentlyContinue
    if ($null -eq $registration) { return "" }
    return $registration.Url
}

function Remove-Phase1Registration {
    param([pscustomobject]$Plan)
    Unregister-ScheduledTask -TaskName $Plan.ScheduledTaskName `
        -Confirm:$false -ErrorAction SilentlyContinue
    Remove-TrustedRoot $Plan
    Invoke-InstallCli $Plan @("delete-secret")
    Remove-Item $script:Phase1CatalogRegistryPath -Recurse -Force -ErrorAction SilentlyContinue
}

function Remove-TrustedRoot {
    param([pscustomobject]$Plan)
    $thumbprintPath = Join-Path $Plan.TlsDirectory "trusted-root-thumbprint.txt"
    if (Test-Path -PathType Leaf $thumbprintPath) {
        $thumbprint = Get-Content $thumbprintPath -Raw
        Remove-Item "Cert:\CurrentUser\Root\$thumbprint" -Force -ErrorAction SilentlyContinue
    }
}

function Remove-Phase1Files {
    param([pscustomobject]$Plan, [string]$CatalogPath)
    if ($CatalogPath) {
        Remove-Item (Join-Path $CatalogPath "word-researcher.xml") `
            -Force -ErrorAction SilentlyContinue
    }
    Remove-Item $Plan.AppDataRoot -Recurse -Force -ErrorAction SilentlyContinue
}
