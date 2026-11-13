param(
    [string]$OutDir = ''
)

$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not $OutDir) { $OutDir = Join-Path $Raiz 'dist' }

$Csc = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (-not (Test-Path $Csc)) {
    throw "No se encontró el compilador C# de .NET Framework en $Csc"
}

$Stage = Join-Path ([IO.Path]::GetTempPath()) ("pz_win_stage_" + [Guid]::NewGuid().ToString('N'))
$AppStage = Join-Path $Stage 'app'
New-Item -Path $AppStage -ItemType Directory -Force | Out-Null
New-Item -Path $OutDir -ItemType Directory -Force | Out-Null

try {
    $Ico = Join-Path $Raiz 'windows\pixelzen.ico'
    $VersionPath = Join-Path $Raiz 'VERSION'
    $VerStr = if (Test-Path $VersionPath) { (Get-Content $VersionPath -Raw).Trim() } else { '1.0.0' }
    Write-Host "==> Copiando archivos de runtime v$VerStr (sin carpetas de desarrollo)..."
    Set-Content -Path (Join-Path $AppStage 'VERSION') -Value $VerStr -Encoding ASCII
    foreach ($fn in @('PixelZenMenu.ps1', 'PixelZenHud.ps1', 'PixelZenCiclo.ps1', 'PixelZenApp.vbs', 'pixelzen_win.py', 'datos_win.py', 'pixelzen.ico')) {
        Copy-Item -Path (Join-Path $Raiz "windows\$fn") -Destination (Join-Path $AppStage $fn) -Force
    }
    Copy-Item -Path (Join-Path $Raiz 'windows\installer\Desinstalar.ps1') -Destination (Join-Path $AppStage 'Desinstalar.ps1') -Force

    $TemasSrc = Join-Path $Raiz 'windows\lively\temas'
    $TemasDst = Join-Path $AppStage 'temas'
    Copy-Item -Path $TemasSrc -Destination $TemasDst -Recurse -Force

    # Copiar previews dia/dorado/noche (principal y secundario) dentro de cada tema instalado
    foreach ($temaDir in Get-ChildItem -Path $TemasDst -Directory) {
        $tid = $temaDir.Name
        foreach ($sub in @('', 'secundario')) {
            $prevSrc = if ($sub) { Join-Path $Raiz "escenas\$tid\$sub\preview" } else { Join-Path $Raiz "escenas\$tid\preview" }
            if (Test-Path $prevSrc) {
                $prevDst = if ($sub) { Join-Path $temaDir.FullName "$sub\preview" } else { Join-Path $temaDir.FullName 'preview' }
                Copy-Item -Path $prevSrc -Destination $prevDst -Recurse -Force
            }
        }
    }

    # También copiar visor web ligero por si alguien pulsa "Ver animación en navegador" teniendo Python
    $LivelyDst = Join-Path $AppStage 'lively'
    New-Item -Path $LivelyDst -ItemType Directory -Force | Out-Null
    foreach ($webItem in Get-ChildItem -Path (Join-Path $Raiz 'windows\lively') -File) {
        Copy-Item -Path $webItem.FullName -Destination (Join-Path $LivelyDst $webItem.Name) -Force
    }

    $PayloadZip = Join-Path $Stage 'PixelZenPayload.zip'
    Write-Host '==> Empaquetando payload.zip...'
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($AppStage, $PayloadZip, [System.IO.Compression.CompressionLevel]::Optimal, $false)

    $SetupExe = Join-Path $OutDir 'PixelZenWorlds-Setup.exe'
    if (Test-Path $SetupExe) { Remove-Item $SetupExe -Force }

    Write-Host '==> Compilando instalador único PixelZenWorlds-Setup.exe...'
    & $Csc /nologo /target:winexe /optimize+ "/win32icon:$Ico" "/out:$SetupExe" `
        "/resource:$PayloadZip,PixelZenPayload.zip" `
        /r:System.Drawing.dll /r:System.Windows.Forms.dll /r:System.IO.Compression.dll /r:System.IO.Compression.FileSystem.dll `
        (Join-Path $Raiz 'windows\installer\PixelZenSetup.cs')
    if ($LASTEXITCODE -ne 0) { throw 'Error compilando PixelZenSetup.cs' }

    $mb = [math]::Round((Get-Item $SetupExe).Length / 1MB, 2)
    Write-Host "✅ Instalador generado: $SetupExe ($mb MB)"
} finally {
    if (Test-Path $Stage) { Remove-Item $Stage -Recurse -Force -ErrorAction SilentlyContinue }
}
