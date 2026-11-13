# Descarga e instalación automática de PixelZen Worlds para Windows 10/11.
# Uso remoto:
#   irm https://raw.githubusercontent.com/davidlpizano/pixelzen-worlds/main/scripts/instalar.ps1 | iex
param(
    [string]$Destino = $(if ($env:PIXELZEN_DIR) { $env:PIXELZEN_DIR } else { "$env:USERPROFILE\pixelzen-worlds" }),
    [string]$Tema = $(if ($env:PIXELZEN_TEMA) { $env:PIXELZEN_TEMA } else { "spiderman-miles-morales" })
)

$ErrorActionPreference = "Stop"
$Repo = "davidlpizano/pixelzen-worlds"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Se requiere Git para Windows. Instálalo con: winget install Git.Git"
}

if (Test-Path (Join-Path $Destino ".git")) {
    Write-Host "==> Actualizando repositorio en $Destino" -ForegroundColor Cyan
    git -C $Destino pull --ff-only
} elseif ((Get-Command gh -ErrorAction SilentlyContinue) -and (& gh auth status 2>$null)) {
    Write-Host "==> Clonando $Repo con GitHub CLI en $Destino" -ForegroundColor Cyan
    gh repo clone $Repo $Destino
} else {
    Write-Host "==> Clonando $Repo en $Destino" -ForegroundColor Cyan
    git clone "https://github.com/$Repo.git" $Destino
}

$WinDir = Join-Path $Destino "windows"
$LivelyHtml = Join-Path $WinDir "lively\index.html"

Write-Host ""
Write-Host "Descarga completada en: $Destino" -ForegroundColor Green
Write-Host "  - Lively Wallpaper: añade '$LivelyHtml' en Lively y elige tema '$Tema' en Personalizar."
Write-Host "  - Standalone Python: python `"$WinDir\pixelzen_win.py`" --tema $Tema --90m"
Write-Host ""

if (Test-Path $WinDir) {
    Start-Process explorer.exe $WinDir
}
