$ErrorActionPreference = 'Stop'

param(
    [Parameter(Mandatory = $false)]
    [string]$SubjectName,
    [Parameter(Mandatory = $false)]
    [string]$ExePath,
    [Parameter(Mandatory = $false)]
    [string]$ScriptPath
)

if (-not $ExePath) {
    $ExePath = 'dist\DRYDefense.exe'
}

if (-not $ScriptPath) {
    $ScriptPath = 'install_dry_defense.ps1'
}

if (-not $SubjectName) {
    $SubjectName = $env:WINDOWS_SIGNING_CERT_SUBJECT
}

if (-not $SubjectName) {
    throw "Set WINDOWS_SIGNING_CERT_SUBJECT or pass -SubjectName with a valid code-signing certificate subject."
}

if (-not (Test-Path $ExePath)) {
    throw "Executable not found: $ExePath"
}

$signtool = Get-Command signtool.exe -ErrorAction SilentlyContinue
if (-not $signtool) {
    throw "signtool.exe is not available. Install the Windows SDK and retry."
}

& signtool.exe sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 /n $SubjectName /v $ExePath

if (Test-Path $ScriptPath) {
    $cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -match $SubjectName } | Select-Object -First 1
    if (-not $cert) {
        throw "No certificate matching subject '$SubjectName' was found in Cert:\CurrentUser\My."
    }

    Set-AuthenticodeSignature -FilePath $ScriptPath -Certificate $cert -TimestampServer 'http://timestamp.digicert.com' | Out-Null
}

Write-Host "Signed executable and installer script successfully."
