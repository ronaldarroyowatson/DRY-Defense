$ErrorActionPreference = 'Stop'

$installRoot = Join-Path $env:LOCALAPPDATA 'DRYDefense'
$shortcutPath = Join-Path $env:USERPROFILE 'Desktop\DRY Defense.lnk'
$exeSource = Join-Path $PSScriptRoot 'DRYDefense.exe'

if (-not (Test-Path $exeSource)) {
    throw "Expected executable not found in the same folder as this installer: $exeSource"
}

New-Item -ItemType Directory -Force -Path $installRoot | Out-Null
Copy-Item $exeSource (Join-Path $installRoot 'DRYDefense.exe') -Force

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = (Join-Path $installRoot 'DRYDefense.exe')
$Shortcut.WorkingDirectory = $installRoot
$Shortcut.Description = 'DRY Defense - FACTS and Planbook CSV converter'
$Shortcut.Save()

Write-Host "DRY Defense installed successfully."
Write-Host "Shortcut created at: $shortcutPath"
