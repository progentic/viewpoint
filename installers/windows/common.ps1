Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$CatalogId = "{8F663F3F-80AF-4F20-A32F-4A226F7671F5}"
$CatalogRegistryPath = "HKCU:\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\$CatalogId"
$ScheduledTaskName = "Word Researcher Local Companion"

function Assert-Phase1Prerequisites {
    param([string]$ProjectRoot, [string]$PythonExecutable, [string]$CatalogPath)
    if (-not (Test-Path -PathType Leaf $PythonExecutable)) {
        throw "Missing locked Python environment"
    }
    if (-not (Test-Path -PathType Leaf (Join-Path $ProjectRoot "taskpane\dist\index.html"))) {
        throw "Missing task-pane build"
    }
    if (-not (Test-Path -PathType Container $CatalogPath)) {
        throw "The required Word test catalog share is unavailable: $CatalogPath"
    }
}

function Invoke-InstallCli {
    param([string]$ProjectRoot, [string]$PythonExecutable, [string[]]$Arguments)
    $previousPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = Join-Path $ProjectRoot "companion\src"
        & $PythonExecutable -m researcher_companion.install_cli @Arguments
        if ($LASTEXITCODE -ne 0) { throw "Local installation material command failed" }
    } finally {
        $env:PYTHONPATH = $previousPythonPath
    }
}

function Install-PrivateMaterial {
    param([string]$ProjectRoot, [string]$PythonExecutable, [string]$AppDataRoot)
    Invoke-InstallCli $ProjectRoot $PythonExecutable @(
        "provision", "--tls-directory", (Join-Path $AppDataRoot "tls")
    )
    Protect-PrivateMaterial (Join-Path $AppDataRoot "tls")
}

function Protect-PrivateMaterial {
    param([string]$TlsDirectory)
    & icacls.exe $TlsDirectory /inheritance:r /grant:r "$($env:USERNAME):(OI)(CI)F" /T | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Windows could not restrict TLS material ACLs" }
}

function Install-TlsTrust {
    param([string]$AppDataRoot)
    $certificatePath = Join-Path $AppDataRoot "tls\root-ca.pem"
    $certificate = Import-Certificate -FilePath $certificatePath -CertStoreLocation "Cert:\CurrentUser\Root"
    Set-Content -Path (Join-Path $AppDataRoot "tls\trusted-root-thumbprint.txt") `
        -Value $certificate.Thumbprint -Encoding ascii -NoNewline
}

function Register-WordManifest {
    param([string]$ProjectRoot, [string]$CatalogPath)
    Copy-Item (Join-Path $ProjectRoot "manifest\word-researcher.xml") `
        (Join-Path $CatalogPath "word-researcher.xml") -Force
    New-Item -Path $CatalogRegistryPath -Force | Out-Null
    New-ItemProperty -Path $CatalogRegistryPath -Name "Id" -Value $CatalogId `
        -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $CatalogRegistryPath -Name "Url" -Value $CatalogPath `
        -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $CatalogRegistryPath -Name "Flags" -Value 1 `
        -PropertyType DWord -Force | Out-Null
}

function Write-CompanionLauncher {
    param([string]$ProjectRoot, [string]$PythonExecutable, [string]$AppDataRoot)
    $launcherPath = Join-Path $AppDataRoot "run-companion.ps1"
    $pythonPath = Join-Path $ProjectRoot "companion\src"
    $content = @"
`$env:PYTHONPATH = '$($pythonPath.Replace("'", "''"))'
`$env:WORD_RESEARCHER_DATA = '$($AppDataRoot.Replace("'", "''"))'
& '$($PythonExecutable.Replace("'", "''"))' -m researcher_companion.main
"@
    Set-Content -Path $launcherPath -Value $content -Encoding utf8NoBOM
    return $launcherPath
}

function Register-CompanionStartup {
    param([string]$LauncherPath)
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$LauncherPath`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
    Register-ScheduledTask -TaskName $ScheduledTaskName -Action $action -Trigger $trigger `
        -Principal $principal -Force | Out-Null
    Start-ScheduledTask -TaskName $ScheduledTaskName
}

function Assert-PrivateMaterial {
    param([string]$ProjectRoot, [string]$PythonExecutable, [string]$AppDataRoot)
    $required = @("root-ca.pem", "root-ca-key.pem", "server-cert.pem", "server-key.pem", "tls-metadata.json")
    foreach ($name in $required) {
        if (-not (Test-Path -PathType Leaf (Join-Path $AppDataRoot "tls\$name"))) {
            throw "TLS repair requires reinstall: $name is missing"
        }
    }
    Invoke-InstallCli $ProjectRoot $PythonExecutable @("check-secret")
}

function Remove-Phase1Registration {
    param([string]$ProjectRoot, [string]$PythonExecutable, [string]$AppDataRoot)
    Unregister-ScheduledTask -TaskName $ScheduledTaskName -Confirm:$false -ErrorAction SilentlyContinue
    Remove-TrustedRoot $AppDataRoot
    Invoke-InstallCli $ProjectRoot $PythonExecutable @("delete-secret")
    Remove-Item $CatalogRegistryPath -Recurse -Force -ErrorAction SilentlyContinue
}

function Remove-TrustedRoot {
    param([string]$AppDataRoot)
    $thumbprintPath = Join-Path $AppDataRoot "tls\trusted-root-thumbprint.txt"
    if (Test-Path -PathType Leaf $thumbprintPath) {
        $thumbprint = Get-Content $thumbprintPath -Raw
        Remove-Item "Cert:\CurrentUser\Root\$thumbprint" -Force -ErrorAction SilentlyContinue
    }
}
