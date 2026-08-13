# Builds Stream Ligar.exe + Config.exe into dist\StreamLigar
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "==> Regenerating icon" -ForegroundColor Cyan
python scripts\make_icon.py

Write-Host "==> Cleaning previous build" -ForegroundColor Cyan
if (Test-Path "$root\build") { Remove-Item -Recurse -Force "$root\build" }
if (Test-Path "$root\dist")  { Remove-Item -Recurse -Force "$root\dist" }

Write-Host "==> Running PyInstaller" -ForegroundColor Cyan
python -m PyInstaller packaging\stream_ligar.spec --noconfirm

$out = Join-Path $root "dist\StreamLigar"
Write-Host ""
Write-Host "==> Done. Executables in: $out" -ForegroundColor Green
Get-ChildItem $out -Filter *.exe | Select-Object Name, Length | Format-Table -AutoSize
