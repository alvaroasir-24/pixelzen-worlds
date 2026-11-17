# Instalador limpio de PixelZen Worlds para Windows 10/11 (sin archivos .exe; compatible con Control inteligente de aplicaciones).
# Uso remoto (1 comando en PowerShell, sin Git ni carpetas visibles):
#   irm https://raw.githubusercontent.com/davidlpizano/pixelzen-worlds/main/scripts/instalar.ps1 | iex
param(
    [string]$Destino = $(Join-Path $env:LOCALAPPDATA 'PixelZenWorlds'),
    [switch]$AutoInicio,
    [switch]$NoLaunch
)

$ErrorActionPreference = 'Stop'
$Repo = 'davidlpizano/pixelzen-worlds'
$AppDir = Join-Path $Destino 'app'

function Stop-PixelZenProcesos {
    foreach ($pf in @('pixelzen_app.pid', 'pixelzen_motor.pid', 'pixelzen_hud.pid', 'pixelzen_win.pid', 'pixelzen_srv.pid')) {
        $p = Join-Path $env:TEMP $pf
        if (Test-Path $p) {
            $idTxt = (Get-Content $p -ErrorAction SilentlyContinue | Select-Object -First 1)
            $pidNum = 0
            if ($idTxt -and [int]::TryParse($idTxt.Trim(), [ref]$pidNum)) {
                Stop-Process -Id $pidNum -Force -ErrorAction SilentlyContinue
            }
            Remove-Item $p -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Milliseconds 250
}

function Copy-RuntimeDesdeRepo([string]$Raiz, [string]$DestApp) {
    $VerPath = Join-Path $Raiz 'VERSION'
    $VerStr = if (Test-Path $VerPath) { (Get-Content $VerPath -Raw).Trim() } else { '1.1.0' }
    New-Item -Path $DestApp -ItemType Directory -Force | Out-Null
    Set-Content -Path (Join-Path $DestApp 'VERSION') -Value $VerStr -Encoding ASCII

    foreach ($fn in @('PixelZenMenu.ps1', 'PixelZenMotor.ps1', 'PixelZenHud.ps1', 'PixelZenCiclo.ps1', 'PixelZenApp.vbs', 'pixelzen_win.py', 'datos_win.py', 'pixelzen.ico')) {
        Copy-Item -Path (Join-Path $Raiz "windows\$fn") -Destination (Join-Path $DestApp $fn) -Force
    }
    Copy-Item -Path (Join-Path $Raiz 'src\worlds_meta.json') -Destination (Join-Path $DestApp 'worlds_meta.json') -Force
    Copy-Item -Path (Join-Path $Raiz 'windows\installer\Desinstalar.ps1') -Destination (Join-Path $DestApp 'Desinstalar.ps1') -Force

    $LivelyDst = Join-Path $DestApp 'lively'
    New-Item -Path $LivelyDst -ItemType Directory -Force | Out-Null
    foreach ($webItem in Get-ChildItem -Path (Join-Path $Raiz 'windows\lively') -File) {
        Copy-Item -Path $webItem.FullName -Destination (Join-Path $LivelyDst $webItem.Name) -Force
    }

    $TemasDst = Join-Path $LivelyDst 'temas'
    if (Test-Path $TemasDst) { Remove-Item $TemasDst -Recurse -Force -ErrorAction SilentlyContinue }
    $TemasSrc = if (Test-Path (Join-Path $Raiz 'docs\temas')) {
        Join-Path $Raiz 'docs\temas'
    } else {
        Join-Path $Raiz 'windows\lively\temas'
    }
    Copy-Item -Path $TemasSrc -Destination $TemasDst -Recurse -Force

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
}

Write-Host ''
Write-Host '==> Instalando PixelZen Worlds (sin ejecutables .exe)...' -ForegroundColor Cyan
Stop-PixelZenProcesos

$StageTmp = $null
try {
    if (Test-Path $AppDir) { Remove-Item $AppDir -Recurse -Force -ErrorAction SilentlyContinue }
    New-Item -Path $Destino -ItemType Directory -Force | Out-Null

    $ScriptDir = if ($MyInvocation.MyCommand.Path) { Split-Path -Parent $MyInvocation.MyCommand.Path } else { $null }
    if ($ScriptDir -and (Test-Path (Join-Path $ScriptDir 'app\PixelZenMenu.ps1'))) {
        Write-Host '==> Copiando aplicación desde paquete local...'
        Copy-Item -Path (Join-Path $ScriptDir 'app') -Destination $AppDir -Recurse -Force
    } elseif ($ScriptDir -and (Test-Path (Join-Path $ScriptDir '..\windows\PixelZenMenu.ps1'))) {
        $RepoLocal = Split-Path -Parent $ScriptDir
        Write-Host "==> Instalando aplicación final desde repositorio local ($RepoLocal)..."
        Copy-RuntimeDesdeRepo $RepoLocal $AppDir
    } else {
        $StageTmp = Join-Path ([IO.Path]::GetTempPath()) ('pz_dl_' + [Guid]::NewGuid().ToString('N'))
        New-Item -Path $StageTmp -ItemType Directory -Force | Out-Null
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Add-Type -AssemblyName System.IO.Compression.FileSystem

        $ZipUrl = $null
        $EsRepoZip = $false
        try {
            $rel = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" -Headers @{ 'User-Agent' = 'PixelZenWorlds' } -TimeoutSec 12
            $asset = $rel.assets | Where-Object { $_.name -eq 'PixelZenWorlds-Windows.zip' } | Select-Object -First 1
            if ($asset) { $ZipUrl = $asset.browser_download_url }
        } catch { }

        if (-not $ZipUrl) {
            $ZipUrl = "https://github.com/$Repo/archive/refs/heads/main.zip"
            $EsRepoZip = $true
        }

        $ZipPath = Join-Path $StageTmp 'pixelzen.zip'
        Write-Host "==> Descargando PixelZen Worlds desde GitHub..."
        Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath -UseBasicParsing
        [System.IO.Compression.ZipFile]::ExtractToDirectory($ZipPath, $StageTmp)

        if ($EsRepoZip) {
            $RootExtracted = (Get-ChildItem -Path $StageTmp -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'windows\PixelZenMenu.ps1') } | Select-Object -First 1)
            if (-not $RootExtracted) { throw 'No se encontró windows\PixelZenMenu.ps1 en el paquete descargado.' }
            Copy-RuntimeDesdeRepo $RootExtracted.FullName $AppDir
        } else {
            $AppExtracted = Join-Path $StageTmp 'app'
            if (-not (Test-Path $AppExtracted)) { throw 'Paquete ZIP sin carpeta app.' }
            Copy-Item -Path $AppExtracted -Destination $AppDir -Recurse -Force
        }
    }

    $VerInst = if (Test-Path (Join-Path $AppDir 'VERSION')) { (Get-Content (Join-Path $AppDir 'VERSION') -Raw).Trim() } else { '1.1.0' }
    $Wscript = Join-Path $env:WINDIR 'System32\wscript.exe'
    $AppVbs = Join-Path $AppDir 'PixelZenApp.vbs'
    $AppIco = Join-Path $AppDir 'pixelzen.ico'
    $UninstPs = Join-Path $AppDir 'Desinstalar.ps1'

    $Shell = New-Object -ComObject WScript.Shell
    foreach ($lnkPath in @(
        (Join-Path ([Environment]::GetFolderPath('Desktop')) 'PixelZen Worlds.lnk'),
        (Join-Path ([Environment]::GetFolderPath('Programs')) 'PixelZen Worlds.lnk')
    )) {
        $lnk = $Shell.CreateShortcut($lnkPath)
        $lnk.TargetPath = $Wscript
        $lnk.Arguments = "`"$AppVbs`""
        $lnk.WorkingDirectory = $AppDir
        $lnk.Description = 'PixelZen Worlds - Fondos pixel art animados'
        if (Test-Path $AppIco) { $lnk.IconLocation = "$AppIco,0" }
        $lnk.Save()
    }

    $UninstReg = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\PixelZenWorlds'
    New-Item -Path $UninstReg -Force | Out-Null
    Set-ItemProperty -Path $UninstReg -Name 'DisplayName' -Value 'PixelZen Worlds'
    Set-ItemProperty -Path $UninstReg -Name 'DisplayVersion' -Value $VerInst
    Set-ItemProperty -Path $UninstReg -Name 'Publisher' -Value 'PixelZen Worlds'
    Set-ItemProperty -Path $UninstReg -Name 'InstallLocation' -Value $AppDir
    Set-ItemProperty -Path $UninstReg -Name 'NoModify' -Value 1 -Type DWord
    Set-ItemProperty -Path $UninstReg -Name 'NoRepair' -Value 1 -Type DWord
    if (Test-Path $AppIco) { Set-ItemProperty -Path $UninstReg -Name 'DisplayIcon' -Value $AppIco }
    $UninstCmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$UninstPs`""
    Set-ItemProperty -Path $UninstReg -Name 'UninstallString' -Value $UninstCmd

    if ($AutoInicio) {
        $RunReg = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
        New-Item -Path $RunReg -Force | Out-Null
        Set-ItemProperty -Path $RunReg -Name 'PixelZenWorlds' -Value "`"$Wscript`" `"$AppVbs`" --solo-aplicar"
    }

    Write-Host "✅ PixelZen Worlds v$VerInst instalado correctamente en: $AppDir" -ForegroundColor Green
    Write-Host '   Acceso directo creado en el Escritorio y Menú Inicio.'

    if (-not $NoLaunch) {
        Start-Process -FilePath $Wscript -ArgumentList "`"$AppVbs`"" -WorkingDirectory $AppDir
    }
} finally {
    if ($StageTmp -and (Test-Path $StageTmp)) {
        Remove-Item $StageTmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
