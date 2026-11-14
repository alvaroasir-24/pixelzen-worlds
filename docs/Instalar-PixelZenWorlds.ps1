# Instalador web oficial de PixelZen Worlds (Windows 10/11, sin ejecutables .exe)
# Compatible con Control inteligente de aplicaciones.
$ErrorActionPreference = 'Stop'
$Repo = 'davidlpizano/pixelzen-worlds'
$ApiUrl = "https://api.github.com/repos/$Repo/releases/latest"
$RawInstaller = "https://raw.githubusercontent.com/$Repo/main/scripts/instalar.ps1"

Write-Host ''
Write-Host '==> PixelZen Worlds · Preparando instalacion limpia (sin .exe)...' -ForegroundColor Cyan

$Aqui = if ($MyInvocation.MyCommand.Path) { Split-Path -Parent $MyInvocation.MyCommand.Path } else { $null }
$RepoLocalScript = $null
if ($Aqui) {
    foreach ($cand in @(
        (Join-Path (Split-Path -Parent $Aqui) 'scripts\instalar.ps1'),
        (Join-Path $env:USERPROFILE 'Proyectos\pixelzen-worlds\scripts\instalar.ps1')
    )) {
        if (Test-Path $cand) { $RepoLocalScript = $cand; break }
    }
}

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Write-Host '==> Descargando instalador oficial desde GitHub main...' -ForegroundColor Gray
    $codigo = Invoke-RestMethod -Uri $RawInstaller -Headers @{ 'User-Agent' = 'PixelZenWorlds' } -TimeoutSec 15
    Invoke-Expression $codigo
} catch {
    if ($RepoLocalScript -and (Test-Path $RepoLocalScript)) {
        Write-Host "==> Sin conexion a GitHub; usando instalador local: $RepoLocalScript" -ForegroundColor Yellow
        & $RepoLocalScript
    } else {
        Write-Host "No se pudo descargar desde GitHub ni encontrar copia local: $($_.Exception.Message)" -ForegroundColor Red
        Read-Host 'Pulsa Enter para cerrar'
        exit 1
    }
}
