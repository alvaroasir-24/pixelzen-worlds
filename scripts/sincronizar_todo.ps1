# Sincroniza los mundos compilados en scratch -> repositorio, actualiza Desktop\pixelzen-web y sube a GitHub.
param(
    [string]$OutRoot = 'C:\Users\david\.gemini\antigravity-cli\brain\8747b389-799a-4632-897a-f7f55a4233c0\scratch\out_root',
    [string]$StageWeb = 'C:\Users\david\.gemini\antigravity-cli\brain\8747b389-799a-4632-897a-f7f55a4233c0\scratch\pixelzen-web',
    [string]$DesktopWeb = (Join-Path ([Environment]::GetFolderPath('Desktop')) 'pixelzen-web'),
    [string]$Mensaje = 'feat: enriquecer 27 escenas, ampliar HUD a 9 tarjetas, crear web pixelzen-web y actualizar README',
    [switch]$NoCommit,
    [switch]$NoPush
)

$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Sync-Tree([string]$Src, [string]$Dst) {
    if (-not (Test-Path $Src)) { throw "No existe carpeta origen: $Src" }
    New-Item -Path $Dst -ItemType Directory -Force | Out-Null
    $rc = & robocopy $Src $Dst /E /COPY:DAT /R:2 /W:1 /NFL /NDL /NJH /NJS /NP
    if ($LASTEXITCODE -ge 8) {
        throw "Error robocopy ($LASTEXITCODE) copiando $Src -> $Dst"
    }
}

Write-Host ''
Write-Host '==> 1/5 Verificando artefactos compilados...' -ForegroundColor Cyan
if (-not (Test-Path (Join-Path $OutRoot 'docs\temas'))) { throw "Falta OutRoot\docs\temas en $OutRoot" }
if (-not (Test-Path (Join-Path $StageWeb 'temas-bundle.js'))) { throw "Falta StageWeb\temas-bundle.js en $StageWeb" }

Write-Host '==> 2/5 Sincronizando packs y previews en docs/, windows/ y escenas/...' -ForegroundColor Cyan
Sync-Tree (Join-Path $OutRoot 'docs\temas') (Join-Path $Raiz 'docs\temas')
Sync-Tree (Join-Path $OutRoot 'docs\previews') (Join-Path $Raiz 'docs\previews')
Sync-Tree (Join-Path $OutRoot 'windows\lively\temas') (Join-Path $Raiz 'windows\lively\temas')
Sync-Tree (Join-Path $OutRoot 'escenas') (Join-Path $Raiz 'escenas')

Write-Host '==> 3/5 Sincronizando pixelzen-canvas.js, pixelzen-heroes.js y temas-bundle.js...' -ForegroundColor Cyan
$SrcCanvas = Join-Path $Raiz 'src\pixelzen-canvas.js'
foreach ($dst in @(
    (Join-Path $Raiz 'docs\pixelzen-canvas.js'),
    (Join-Path $Raiz 'windows\lively\pixelzen-canvas.js'),
    (Join-Path $StageWeb 'pixelzen-canvas.js')
)) {
    Copy-Item -Path $SrcCanvas -Destination $dst -Force
}
$SrcHeroes = Join-Path $Raiz 'src\pixelzen-heroes.js'
foreach ($dst in @(
    (Join-Path $Raiz 'docs\pixelzen-heroes.js'),
    (Join-Path $Raiz 'windows\lively\pixelzen-heroes.js'),
    (Join-Path $StageWeb 'pixelzen-heroes.js')
)) {
    Copy-Item -Path $SrcHeroes -Destination $dst -Force
}
Copy-Item -Path (Join-Path $StageWeb 'temas-bundle.js') -Destination (Join-Path $Raiz 'docs\temas-bundle.js') -Force

Write-Host "==> 4/5 Actualizando carpeta completa del Escritorio ($DesktopWeb)..." -ForegroundColor Cyan
Sync-Tree $StageWeb $DesktopWeb
foreach ($webFile in @('index.html', 'styles.css', 'app.js', 'pixelzen-heroes.js', 'pixelzen-canvas.js', 'Instalar-PixelZenWorlds.bat', 'Instalar-PixelZenWorlds.ps1')) {
    $srcF = Join-Path $Raiz "docs\$webFile"
    if (Test-Path $srcF) {
        Copy-Item -Path $srcF -Destination (Join-Path $DesktopWeb $webFile) -Force
    }
}

Write-Host '==> 5/5 Verificando paridad SHA-256 y estado de Git...' -ForegroundColor Cyan
$hSrc = (Get-FileHash $SrcCanvas -Algorithm SHA256).Hash
$hDoc = (Get-FileHash (Join-Path $Raiz 'docs\pixelzen-canvas.js') -Algorithm SHA256).Hash
$hLiv = (Get-FileHash (Join-Path $Raiz 'windows\lively\pixelzen-canvas.js') -Algorithm SHA256).Hash
$hDsk = (Get-FileHash (Join-Path $DesktopWeb 'pixelzen-canvas.js') -Algorithm SHA256).Hash
if ($hSrc -ne $hDoc -or $hSrc -ne $hLiv -or $hSrc -ne $hDsk) {
    throw "Mismatch SHA-256 en pixelzen-canvas.js"
}
Write-Host "    SHA-256 OK: $hSrc" -ForegroundColor Green

$nPrev = (Get-ChildItem (Join-Path $DesktopWeb 'previews') -Recurse -File -Filter '*.png').Count
$nPacks = (Get-ChildItem (Join-Path $DesktopWeb 'temas') -Recurse -File -Filter 'datos.json').Count
Write-Host "    Desktop\pixelzen-web listo: $nPacks packs, $nPrev previews." -ForegroundColor Green

if (-not $NoCommit) {
    Push-Location $Raiz
    try {
        git add -A
        $cambios = git status --porcelain
        if ($cambios) {
            git commit -m $Mensaje
            if (-not $NoPush) {
                git push origin main
                Write-Host '✅ Cambios subidos correctamente a origin/main.' -ForegroundColor Green
            } else {
                Write-Host 'ℹ️ Commit creado localmente (-NoPush activo).' -ForegroundColor Yellow
            }
        } else {
            Write-Host 'ℹ️ No habia cambios nuevos que confirmar.' -ForegroundColor Gray
        }
    } finally {
        Pop-Location
    }
}

Write-Host '✅ Sincronizacion completada.' -ForegroundColor Green
