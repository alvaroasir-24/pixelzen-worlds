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
    foreach ($fn in @('PixelZenMenu.ps1', 'PixelZenMotor.ps1', 'PixelZenHud.ps1', 'PixelZenCiclo.ps1', 'PixelZenApp.vbs', 'pixelzen_win.py', 'datos_win.py', 'pixelzen.ico')) {
        Copy-Item -Path (Join-Path $Raiz "windows\$fn") -Destination (Join-Path $AppStage $fn) -Force
    }
    Copy-Item -Path (Join-Path $Raiz 'src\worlds_meta.json') -Destination (Join-Path $AppStage 'worlds_meta.json') -Force
    Copy-Item -Path (Join-Path $Raiz 'windows\installer\Desinstalar.ps1') -Destination (Join-Path $AppStage 'Desinstalar.ps1') -Force

    $LivelyDst = Join-Path $AppStage 'lively'
    New-Item -Path $LivelyDst -ItemType Directory -Force | Out-Null
    foreach ($webItem in Get-ChildItem -Path (Join-Path $Raiz 'windows\lively') -File) {
        Copy-Item -Path $webItem.FullName -Destination (Join-Path $LivelyDst $webItem.Name) -Force
    }

    $TemasSrc = if (Test-Path (Join-Path $Raiz 'docs\temas')) {
        Join-Path $Raiz 'docs\temas'
    } else {
        Join-Path $Raiz 'windows\lively\temas'
    }
    $TemasDst = Join-Path $LivelyDst 'temas'
    Copy-Item -Path $TemasSrc -Destination $TemasDst -Recurse -Force

    # Copiar previews dia/dorado/noche (principal y secundario) dentro de cada tema instalado
    foreach ($temaDir in Get-ChildItem -Path $TemasDst -Directory) {
        $tid = $temaDir.Name
        foreach ($sub in @('', 'secundario', 'bloqueo')) {
            $prevSrc = if ($sub) { Join-Path $Raiz "escenas\$tid\$sub\preview" } else { Join-Path $Raiz "escenas\$tid\preview" }
            if (Test-Path $prevSrc) {
                $prevDst = if ($sub) { Join-Path $temaDir.FullName "$sub\preview" } else { Join-Path $temaDir.FullName 'preview' }
                Copy-Item -Path $prevSrc -Destination $prevDst -Recurse -Force
            }
        }
    }

    $PayloadZip = Join-Path $Stage 'PixelZenPayload.zip'
    Write-Host '==> Empaquetando payload.zip...'
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($AppStage, $PayloadZip, [System.IO.Compression.CompressionLevel]::Optimal, $false)

    $PkgZip = Join-Path $OutDir 'PixelZenWorlds-Windows.zip'
    if (Test-Path $PkgZip) { Remove-Item $PkgZip -Force }
    $ZipStage = Join-Path $Stage 'zip_dist'
    New-Item -Path $ZipStage -ItemType Directory -Force | Out-Null
    Copy-Item -Path $AppStage -Destination (Join-Path $ZipStage 'app') -Recurse -Force
    Copy-Item -Path (Join-Path $Raiz 'scripts\instalar.ps1') -Destination (Join-Path $ZipStage 'Instalar.ps1') -Force
    $BatTxt = "@echo off`r`npowershell.exe -NoProfile -ExecutionPolicy Bypass -File `"%~dp0Instalar.ps1`"`r`nif errorlevel 1 pause`r`n"
    Set-Content -Path (Join-Path $ZipStage 'Instalar.bat') -Value $BatTxt -Encoding ASCII
    [System.IO.Compression.ZipFile]::CreateFromDirectory($ZipStage, $PkgZip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
    $zipMb = [math]::Round((Get-Item $PkgZip).Length / 1MB, 2)
    Write-Host "✅ Paquete sin .exe generado: $PkgZip ($zipMb MB)"

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
