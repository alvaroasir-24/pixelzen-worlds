param(
    [switch]$Tray,
    [switch]$SoloAplicar
)

Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase, System.Windows.Forms, System.Drawing

$ErrorActionPreference = 'SilentlyContinue'
$Aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$Raiz = Split-Path -Parent $Aqui
$LivelyLocalDir = if (Test-Path (Join-Path $Aqui 'lively\index.html')) { Join-Path $Aqui 'lively' } else { Join-Path $Raiz 'windows\lively' }
$TemasDir = if (Test-Path (Join-Path $Aqui 'lively\temas')) {
    Join-Path $Aqui 'lively\temas'
} elseif (Test-Path (Join-Path $Aqui 'temas')) {
    Join-Path $Aqui 'temas'
} else {
    Join-Path $Raiz 'windows\lively\temas'
}
$EsInstalada = (Test-Path (Join-Path $Aqui 'lively\temas')) -or (Test-Path (Join-Path $Aqui 'temas'))
$DataDir = if ($EsInstalada) { Join-Path $env:LOCALAPPDATA 'PixelZenWorlds' } else { $Aqui }
if (-not (Test-Path $DataDir)) { New-Item -Path $DataDir -ItemType Directory -Force | Out-Null }
$ConfigPath = Join-Path $DataDir 'config.json'
$IconPath = Join-Path $Aqui 'pixelzen.ico'
$VbsPath = Join-Path $Aqui 'PixelZenApp.vbs'
$AutoRegPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$AutoRegName = 'PixelZenWorlds'

function Resolver-Preview([string]$temaId, [string]$fase, [string]$variante = 'principal') {
    $sub = switch ($variante) {
        'secundaria' { 'secundario' }
        'True'       { 'secundario' }
        'bloqueo'    { 'bloqueo' }
        default      { '' }
    }
    $temaDirLocal = Join-Path $TemasDir $temaId
    $temaDirEsc = Join-Path $Raiz "escenas\$temaId"
    $baseLocal = if ($sub) { Join-Path $temaDirLocal $sub } else { $temaDirLocal }
    $baseEsc = if ($sub) { Join-Path $temaDirEsc $sub } else { $temaDirEsc }
    $cands = @(
        (Join-Path $baseLocal "preview\$fase\v3.png"),
        (Join-Path $baseEsc "preview\$fase\v3.png"),
        (Join-Path $baseLocal 'fondo.png'),
        (Join-Path $temaDirLocal 'fondo.png')
    )
    foreach ($p in $cands) {
        if ($p -and (Test-Path $p)) { return ([System.IO.Path]::GetFullPath($p)) }
    }
    return $null
}

function Resolver-Python {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notmatch 'WindowsApps\\python\.exe$') { return $cmd.Source }
    foreach ($cand in @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python311\python.exe'),
        'C:\Python312\python.exe'
    )) {
        if (Test-Path $cand) { return $cand }
    }
    return $null
}

function Cargar-Config {
    $def = [ordered]@{
        tema = 'fittoa'
        monitores = 2
        modo = '90m'
        horaFija = 21.5
        fps = 8
        hud = $true
        trayAlCerrar = $true
        usarBloqueo = $true
        fondoPrincipal = 'principal'
        fondoSecundario = 'secundaria'
        fondoBloqueo = 'bloqueo'
        stats = [ordered]@{
            tiempo = $true
            sistema = $true
            red = $true
            dev = $true
            grimorio = $true
        }
    }
    if (Test-Path $ConfigPath) {
        try {
            $raw = Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
            foreach ($k in 'tema','monitores','modo','horaFija','fps','hud','trayAlCerrar','usarBloqueo','fondoPrincipal','fondoSecundario','fondoBloqueo') {
                if ($null -ne $raw.$k) { $def[$k] = $raw.$k }
            }
            if ($raw.stats) {
                foreach ($sk in 'tiempo','sistema','red','dev','grimorio') {
                    if ($null -ne $raw.stats.$sk) { $def.stats[$sk] = [bool]$raw.stats.$sk }
                }
            }
        } catch {}
    }
    return $def
}

function Guardar-Config($cfg) {
    $cfg | ConvertTo-Json -Depth 4 | Set-Content -Path $ConfigPath -Encoding UTF8
}

function Detectar-Fase($modo, $horaFija) {
    $h = if ($modo -eq 'fija') { [double]$horaFija } else { (Get-Date).Hour + (Get-Date).Minute / 60.0 }
    if ($h -ge 8.0 -and $h -lt 17.5) { return 'dia' }
    if (($h -ge 6.0 -and $h -lt 8.0) -or ($h -ge 17.5 -and $h -lt 20.0)) { return 'dorado' }
    return 'noche'
}

function Aplicar-Fondos-Windows($tema, $numMonitores, $fase, $fondoPrincipal = 'principal', $fondoSecundario = 'secundaria') {
    $p1 = Resolver-Preview $tema $fase $fondoPrincipal
    $p2 = Resolver-Preview $tema $fase $fondoSecundario
    if (-not $p2) { $p2 = $p1 }

    Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Wallpapers' -Name 'BackgroundType' -Value 0 -Type DWord -ErrorAction SilentlyContinue
    $code = @'
using System;
using System.Runtime.InteropServices;

[StructLayout(LayoutKind.Sequential)]
public struct PZRECT { public int Left, Top, Right, Bottom; }

[ComImport, Guid("B92B56A9-8B55-4E14-9A89-0199BBB6F93B"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IPzDesktopWallpaper {
    void SetWallpaper([MarshalAs(UnmanagedType.LPWStr)] string monitorID, [MarshalAs(UnmanagedType.LPWStr)] string wallpaper);
    [return: MarshalAs(UnmanagedType.LPWStr)]
    string GetWallpaper([MarshalAs(UnmanagedType.LPWStr)] string monitorID);
    [return: MarshalAs(UnmanagedType.LPWStr)]
    string GetMonitorDevicePathAt(uint monitorIndex);
    uint GetMonitorDevicePathCount();
    PZRECT GetMonitorRECT([MarshalAs(UnmanagedType.LPWStr)] string monitorID);
}

[ComImport, Guid("C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD")]
public class PzDesktopWallpaperClass {}

public class PzWallApp {
    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    public static extern int SystemParametersInfoW(int uAction, int uParam, string lpvParam, int fuWinIni);

    public static void Apply(string p1, string p2, int numMon) {
        var dw = (IPzDesktopWallpaper)new PzDesktopWallpaperClass();
        uint count = dw.GetMonitorDevicePathCount();
        int primIdx = 0;
        for (uint i = 0; i < count; i++) {
            string id = dw.GetMonitorDevicePathAt(i);
            PZRECT r = dw.GetMonitorRECT(id);
            if (r.Left == 0 && r.Top == 0) { primIdx = (int)i; break; }
        }
        for (uint i = 0; i < count; i++) {
            string id = dw.GetMonitorDevicePathAt(i);
            if ((int)i == primIdx || numMon <= 1) {
                dw.SetWallpaper(id, p1);
            } else {
                dw.SetWallpaper(id, p2);
            }
        }
        if (count == 0) { SystemParametersInfoW(20, 0, p1, 3); }
    }
}
'@
    Add-Type -TypeDefinition $code -ErrorAction SilentlyContinue
    try {
        [PzWallApp]::Apply($p1, $p2, [int]$numMonitores)
    } catch {
        [PzWallApp]::SystemParametersInfoW(20, 0, $p1, 3) | Out-Null
    }
}

function Limpiar-RestosLively {
    $livelyWallRoot = Join-Path $env:LOCALAPPDATA 'Lively Wallpaper\Library\wallpapers'
    $habiaPrueba = $false
    foreach ($name in @('pixelzen-m1', 'pixelzen-m2')) {
        $dir = Join-Path $livelyWallRoot $name
        if (Test-Path $dir) {
            $habiaPrueba = $true
            $lnk = Join-Path $dir 'temas'
            if (Test-Path $lnk) { cmd /c rmdir "`"$lnk`"" 2>$null | Out-Null }
            Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    if ($habiaPrueba) {
        Stop-Process -Name 'Lively', 'Lively.UI.WinUI', 'Lively.WebView2' -Force -ErrorAction SilentlyContinue
    }
}

function Detener-CiclosPrevios {
    foreach ($pf in @('pixelzen_win.pid', 'pixelzen_hud.pid')) {
        $pfile = Join-Path $env:TEMP $pf
        if (Test-Path $pfile) {
            $oldPid = Get-Content $pfile -ErrorAction SilentlyContinue
            if ($oldPid) { Stop-Process -Id ([int]$oldPid) -Force -ErrorAction SilentlyContinue }
        }
    }
}

function Motor-NativoActivo {
    $motorPidFile = Join-Path $env:TEMP 'pixelzen_motor.pid'
    if (Test-Path $motorPidFile) {
        $oldPid = Get-Content $motorPidFile -ErrorAction SilentlyContinue
        if ($oldPid -and (Get-Process -Id ([int]$oldPid) -ErrorAction SilentlyContinue)) { return $true }
    }
    return $false
}

function Aplicar-Bloqueo-Windows($tema, $variante, $fase) {
    $src = Resolver-Preview $tema $fase $variante
    if (-not $src -or -not (Test-Path $src)) { return $false }
    $lockA = Join-Path $DataDir 'lockscreen_a.png'
    $lockB = Join-Path $DataDir 'lockscreen_b.png'
    $curImg = ''
    try {
        Add-Type -AssemblyName System.Runtime.WindowsRuntime
        $null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
        $null = [Windows.System.UserProfile.LockScreen, Windows.System.UserProfile, ContentType = WindowsRuntime]
        $curImg = [Windows.System.UserProfile.LockScreen]::OriginalImageFile.AbsolutePath
    } catch { return $false }
    $outPath = if ($curImg -and ($curImg -match 'lockscreen_a\.png$')) { $lockB } else { $lockA }

    try {
        $bmpIn = [System.Drawing.Bitmap]::new($src)
        try {
            $dstW = 1920; $dstH = 1080
            $bmpOut = [System.Drawing.Bitmap]::new($dstW, $dstH, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
            try {
                $g = [System.Drawing.Graphics]::FromImage($bmpOut)
                try {
                    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
                    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
                    $scale = [Math]::Max($dstW / [double]$bmpIn.Width, $dstH / [double]$bmpIn.Height)
                    $srcW = [float]($dstW / $scale)
                    $srcH = [float]($dstH / $scale)
                    $srcX = [float](($bmpIn.Width - $srcW) * 0.5)
                    $srcY = [float][Math]::Max(0, [Math]::Min($bmpIn.Height - $srcH, [Math]::Round(($bmpIn.Height - $srcH) * 0.55)))
                    $g.DrawImage($bmpIn, [System.Drawing.Rectangle]::new(0, 0, $dstW, $dstH), $srcX, $srcY, $srcW, $srcH, [System.Drawing.GraphicsUnit]::Pixel)
                } finally { $g.Dispose() }
                $bmpOut.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
            } finally { $bmpOut.Dispose() }
        } finally { $bmpIn.Dispose() }

        $null = [Windows.Foundation.IAsyncAction, Windows.Foundation, ContentType = WindowsRuntime]
        $asTaskGen = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
            $_.Name -eq 'AsTask' -and $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -like 'IAsyncOperation*'
        }) | Select-Object -First 1
        $asTaskAct = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
            $_.Name -eq 'AsTask' -and (-not $_.IsGenericMethodDefinition) -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction'
        }) | Select-Object -First 1
        $opFile = [Windows.Storage.StorageFile]::GetFileFromPathAsync($outPath)
        $tFile = $asTaskGen.MakeGenericMethod([Windows.Storage.StorageFile]).Invoke($null, @($opFile))
        $null = $tFile.Wait(-1)
        $sf = $tFile.Result
        $act = [Windows.System.UserProfile.LockScreen]::SetImageFileAsync($sf)
        $tSet = $asTaskAct.Invoke($null, @($act))
        $null = $tSet.Wait(-1)
        return $true
    } catch {
        return $false
    }
}

$script:modoMotor = 'nativo'
$script:bloqueoOk = $false

function Aplicar-Todo($c) {
    Guardar-Config $c
    Limpiar-RestosLively
    $fase = Detectar-Fase $c.modo $c.horaFija
    $fp = if ($c.fondoPrincipal) { $c.fondoPrincipal } else { 'principal' }
    $fs = if ($c.fondoSecundario) { $c.fondoSecundario } else { 'secundaria' }
    $fb = if ($c.fondoBloqueo) { $c.fondoBloqueo } else { 'bloqueo' }
    Aplicar-Fondos-Windows $c.tema $c.monitores $fase $fp $fs
    if ($c.usarBloqueo) {
        $script:bloqueoOk = Aplicar-Bloqueo-Windows $c.tema $fb $fase
    } else {
        $script:bloqueoOk = $false
    }
    Detener-CiclosPrevios

    $motorPath = Join-Path $Aqui 'PixelZenMotor.ps1'
    if (Test-Path $motorPath) {
        $script:modoMotor = 'nativo'
        $motorPidFile = Join-Path $env:TEMP 'pixelzen_motor.pid'
        if (Test-Path $motorPidFile) {
            $oldM = Get-Content $motorPidFile -ErrorAction SilentlyContinue
            if ($oldM) { Stop-Process -Id ([int]$oldM) -Force -ErrorAction SilentlyContinue }
        }
        $proc = Start-Process -FilePath 'powershell.exe' -ArgumentList "-NoProfile -ExecutionPolicy Bypass -STA -WindowStyle Hidden -File `"$motorPath`" -Tema $($c.tema) -Monitores $($c.monitores) -Modo $($c.modo) -Hora $($c.horaFija) -Fps 8 -FondoPrincipal $fp -FondoSecundario $fs" -WindowStyle Hidden -PassThru
        if ($proc) { Set-Content -Path $motorPidFile -Value $proc.Id -Encoding ASCII }
    } else {
        $script:modoMotor = 'estatico'
        $pyPidFile = Join-Path $env:TEMP 'pixelzen_win.pid'
        $py = Resolver-Python
        $pyConPillow = $false
        if ($py) {
            try {
                & $py -c "import PIL" 2>$null
                $pyConPillow = ($LASTEXITCODE -eq 0)
            } catch { $pyConPillow = $false }
        }
        if ($pyConPillow -and $c.modo -ne 'fija') {
            $flag = if ($c.modo -eq 'demo') { '--demo' } elseif ($c.modo -eq 'real') { '--real' } else { '--90m' }
            $proc = Start-Process -FilePath $py -ArgumentList "`"$(Join-Path $Aqui 'pixelzen_win.py')`" --tema $($c.tema) --monitores $($c.monitores) $flag" -WindowStyle Hidden -PassThru
            if ($proc) { Set-Content -Path $pyPidFile -Value $proc.Id -Encoding ASCII }
        } elseif ($c.modo -ne 'fija' -and (Test-Path (Join-Path $Aqui 'PixelZenCiclo.ps1'))) {
            $proc = Start-Process -FilePath 'powershell.exe' -ArgumentList "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$(Join-Path $Aqui 'PixelZenCiclo.ps1')`" -Tema $($c.tema) -Monitores $($c.monitores) -Modo $($c.modo) -Hora $($c.horaFija) -FondoPrincipal $fp -FondoSecundario $fs" -WindowStyle Hidden -PassThru
            if ($proc) { Set-Content -Path $pyPidFile -Value $proc.Id -Encoding ASCII }
        }
    }

    if ($c.hud) {
        Start-Process -FilePath 'powershell.exe' -ArgumentList "-NoProfile -ExecutionPolicy Bypass -STA -WindowStyle Hidden -File `"$(Join-Path $Aqui 'PixelZenHud.ps1')`"" -WindowStyle Hidden
    }
    return $fase
}

function Detener-Hud {
    $hudPidFile = Join-Path $env:TEMP 'pixelzen_hud.pid'
    if (Test-Path $hudPidFile) {
        $oldHud = Get-Content $hudPidFile -ErrorAction SilentlyContinue
        if ($oldHud) { Stop-Process -Id ([int]$oldHud) -Force -ErrorAction SilentlyContinue }
    }
}

function Hay-HudActivo {
    $hudPidFile = Join-Path $env:TEMP 'pixelzen_hud.pid'
    if (Test-Path $hudPidFile) {
        $pidVal = Get-Content $hudPidFile -ErrorAction SilentlyContinue
        if ($pidVal -and (Get-Process -Id ([int]$pidVal) -ErrorAction SilentlyContinue)) { return $true }
    }
    return $false
}

function AutoInicio-Activo {
    $val = (Get-ItemProperty -Path $AutoRegPath -Name $AutoRegName -ErrorAction SilentlyContinue).$AutoRegName
    return [bool]$val
}

function Set-AutoInicio($activar) {
    if ($activar) {
        if (-not (Test-Path $AutoRegPath)) { New-Item -Path $AutoRegPath -Force | Out-Null }
        $cmd = "wscript.exe `"$VbsPath`" --tray"
        Set-ItemProperty -Path $AutoRegPath -Name $AutoRegName -Value $cmd
    } else {
        Remove-ItemProperty -Path $AutoRegPath -Name $AutoRegName -ErrorAction SilentlyContinue
    }
}

function Crear-AccesoDirecto {
    $desk = [Environment]::GetFolderPath('Desktop')
    $lnkPath = Join-Path $desk 'PixelZen Worlds.lnk'
    $ws = New-Object -ComObject WScript.Shell
    $sc = $ws.CreateShortcut($lnkPath)
    $sc.TargetPath = 'wscript.exe'
    $sc.Arguments = "`"$VbsPath`""
    $sc.WorkingDirectory = $Aqui
    $sc.Description = 'Abrir PixelZen Worlds (Fondos animados, multimonitor y HUD)'
    if (Test-Path $IconPath) { $sc.IconLocation = $IconPath }
    $sc.Save()
    return $lnkPath
}

if ($SoloAplicar) {
    $c = Cargar-Config
    $null = Aplicar-Todo $c
    exit 0
}

# Evitar dos ventanas abiertas: si ya hay PID activo y no es modo bandeja, avisar o cerrar instancia previa
$appPidFile = Join-Path $env:TEMP 'pixelzen_app.pid'
if (Test-Path $appPidFile) {
    $prevPid = Get-Content $appPidFile -ErrorAction SilentlyContinue
    if ($prevPid -and $prevPid -ne $PID) {
        Stop-Process -Id ([int]$prevPid) -Force -ErrorAction SilentlyContinue
    }
}
Set-Content -Path $appPidFile -Value $PID -Encoding ASCII

function Obtener-Version {
    foreach ($vp in @((Join-Path $Aqui 'VERSION'), (Join-Path $Raiz 'VERSION'))) {
        if (Test-Path $vp) {
            $txt = (Get-Content $vp -Raw -ErrorAction SilentlyContinue).Trim()
            if ($txt) { return $txt }
        }
    }
    return '1.1.0'
}

function Cargar-Temas {
    $mapaSerie = @{
        'fittoa'                  = @{ serie = 'Mushoku Tensei'; titulo = 'Región de Fittoa' }
        'continente-demoniaco'    = @{ serie = 'Mushoku Tensei'; titulo = 'Continente Demoníaco' }
        'black-clover'            = @{ serie = 'Black Clover'; titulo = 'Aldea de Hage' }
        'hunter-x-hunter'         = @{ serie = 'Hunter × Hunter'; titulo = 'Isla Ballena' }
        'spiderman-miles-morales' = @{ serie = 'Spider-Man: Miles Morales'; titulo = 'Brooklyn y Manhattan' }
        'solo-leveling'           = @{ serie = 'Solo Leveling'; titulo = 'Castillo del Monarca' }
        'demon-slayer'            = @{ serie = 'Demon Slayer'; titulo = 'Tren Infinito' }
        'stranger-things'         = @{ serie = 'Stranger Things'; titulo = 'Hawkins y el Revés' }
        'harry-potter'            = @{ serie = 'Harry Potter'; titulo = 'Castillo de Hogwarts' }
    }
    $lista = @()
    if (Test-Path $TemasDir) {
        foreach ($d in (Get-ChildItem -Path $TemasDir -Directory | Sort-Object Name)) {
            $id = $d.Name
            if ($id.StartsWith('_')) { continue }
            $tj = Join-Path $d.FullName 'tema.json'
            if (-not (Test-Path $tj)) { continue }
            $anime = 'PixelZen'
            $titulo = $id
            $m1 = 'Escena principal'
            $m2 = 'Continuación de la historia'
            try {
                $raw = Get-Content $tj -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($raw.nombre) {
                    $titulo = [string]$raw.nombre
                    if ($titulo -match '^([^·]+)·\s*(.+)$') {
                        $anime = $Matches[1].Trim()
                        $titulo = $Matches[2].Trim()
                    }
                }
                if ($raw.anime) { $anime = [string]$raw.anime }
                if ($raw.subtitulo) { $m1 = [string]$raw.subtitulo }
                elseif ($raw.descripcion) { $m1 = [string]$raw.descripcion }
            } catch {}

            $serie = if ($raw -and $raw.serie) { [string]$raw.serie } elseif ($mapaSerie.ContainsKey($id)) { $mapaSerie[$id].serie } else { $anime }
            if ($mapaSerie.ContainsKey($id)) { $titulo = $mapaSerie[$id].titulo }

            $sj = Join-Path $d.FullName 'secundario\tema.json'
            if (Test-Path $sj) {
                try {
                    $sraw = Get-Content $sj -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($sraw.nombre) { $m2 = [string]$sraw.nombre }
                    elseif ($sraw.subtitulo) { $m2 = [string]$sraw.subtitulo }
                } catch {}
            }
            $m3 = 'Pantalla de bloqueo'
            $bj = Join-Path $d.FullName 'bloqueo\tema.json'
            if (Test-Path $bj) {
                try {
                    $braw = Get-Content $bj -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($braw.nombre) { $m3 = [string]$braw.nombre }
                    elseif ($braw.subtitulo) { $m3 = [string]$braw.subtitulo }
                } catch {}
            }
            $lista += @{ id = $id; serie = $serie; anime = $serie; titulo = $titulo; m1 = $m1; m2 = $m2; m3 = $m3 }
        }
    }
    if ($lista.Count -eq 0) {
        return @(@{ id = 'fittoa'; serie = 'Mushoku Tensei'; anime = 'Mushoku Tensei'; titulo = 'Región de Fittoa'; m1 = 'Aldea de Buena'; m2 = 'Reino de Asura'; m3 = 'Santuario del Teletransporte' })
    }
    return $lista
}

$VersionActual = Obtener-Version
$temas = Cargar-Temas
$seriesList = @()
$seriesByName = [ordered]@{}
foreach ($t in $temas) {
    if (-not $seriesByName.Contains($t.serie)) {
        $seriesByName[$t.serie] = @()
        $seriesList += $t.serie
    }
    $seriesByName[$t.serie] += $t
}

$screens = [System.Windows.Forms.Screen]::AllScreens
$monSummary = ($screens | ForEach-Object -Begin { $i = 1 } -Process {
    $tag = if ($_.Primary) { 'Principal' } else { 'Secundario' }
    "Pantalla ${i}: $tag ($($_.Bounds.Width)×$($_.Bounds.Height))"
    $i++
}) -join '   ·   '

$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="PixelZen Worlds · Tu Escritorio Animado"
        Width="1230" Height="796"
        MinWidth="1040" MinHeight="680"
        WindowStartupLocation="CenterScreen"
        Background="#060913" Foreground="#F3EAD6"
        FontFamily="Segoe UI">
  <Window.Resources>
    <!-- Scrollbar fino y oscuro -->
    <Style TargetType="ScrollBar">
      <Setter Property="Width" Value="7"/>
      <Setter Property="MinWidth" Value="7"/>
      <Setter Property="Background" Value="Transparent"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="ScrollBar">
            <Grid Background="Transparent" Margin="2,2,0,2">
              <Track x:Name="PART_Track" IsDirectionReversed="True">
                <Track.Thumb>
                  <Thumb Cursor="Hand">
                    <Thumb.Template>
                      <ControlTemplate TargetType="Thumb">
                        <Border x:Name="ThBd" Background="#253860" CornerRadius="3.5"/>
                        <ControlTemplate.Triggers>
                          <Trigger Property="IsMouseOver" Value="True">
                            <Setter TargetName="ThBd" Property="Background" Value="#3D5C96"/>
                          </Trigger>
                        </ControlTemplate.Triggers>
                      </ControlTemplate>
                    </Thumb.Template>
                  </Thumb>
                </Track.Thumb>
              </Track>
            </Grid>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>

    <!-- Navegación lateral con hover -->
    <Style x:Key="NavBtn" TargetType="Button">
      <Setter Property="Background" Value="Transparent"/>
      <Setter Property="Foreground" Value="#A3B4CE"/>
      <Setter Property="BorderBrush" Value="Transparent"/>
      <Setter Property="BorderThickness" Value="1"/>
      <Setter Property="HorizontalContentAlignment" Value="Left"/>
      <Setter Property="Padding" Value="14,11"/>
      <Setter Property="Margin" Value="0,0,0,6"/>
      <Setter Property="FontSize" Value="13"/>
      <Setter Property="FontWeight" Value="SemiBold"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="Bd" Background="{TemplateBinding Background}" CornerRadius="9" BorderBrush="{TemplateBinding BorderBrush}" BorderThickness="{TemplateBinding BorderThickness}" Padding="{TemplateBinding Padding}">
              <ContentPresenter HorizontalAlignment="{TemplateBinding HorizontalContentAlignment}" VerticalAlignment="Center"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsMouseOver" Value="True">
                <Setter TargetName="Bd" Property="Background" Value="#121F3E"/>
                <Setter Property="Foreground" Value="#E6EEF9"/>
              </Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>

    <!-- Botones secundarios tipo píldora -->
    <Style x:Key="PillBtn" TargetType="Button">
      <Setter Property="Background" Value="#0F1832"/>
      <Setter Property="Foreground" Value="#DCE6F5"/>
      <Setter Property="BorderBrush" Value="#283C66"/>
      <Setter Property="BorderThickness" Value="1"/>
      <Setter Property="Padding" Value="12,6"/>
      <Setter Property="FontSize" Value="12"/>
      <Setter Property="FontWeight" Value="SemiBold"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="Bd" Background="{TemplateBinding Background}" BorderBrush="{TemplateBinding BorderBrush}" BorderThickness="{TemplateBinding BorderThickness}" CornerRadius="7" Padding="{TemplateBinding Padding}">
              <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsMouseOver" Value="True">
                <Setter TargetName="Bd" Property="Background" Value="#18274E"/>
                <Setter TargetName="Bd" Property="BorderBrush" Value="#4669A8"/>
              </Trigger>
              <Trigger Property="IsPressed" Value="True">
                <Setter TargetName="Bd" Property="Background" Value="#101B38"/>
              </Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>

    <!-- Interruptor moderno (Toggle Switch) para CheckBox -->
    <Style TargetType="CheckBox">
      <Setter Property="Foreground" Value="#F3EAD6"/>
      <Setter Property="FontSize" Value="13"/>
      <Setter Property="Margin" Value="0,4"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="CheckBox">
            <StackPanel Orientation="Horizontal" VerticalAlignment="Center" Background="Transparent">
              <Border x:Name="Track" Width="36" Height="20" CornerRadius="10" Background="#1A2644" BorderBrush="#2D416E" BorderThickness="1" VerticalAlignment="Center" Margin="0,0,10,0">
                <Border x:Name="Knob" Width="14" Height="14" CornerRadius="7" Background="#8FA4C6" HorizontalAlignment="Left" Margin="2,0,0,0" VerticalAlignment="Center"/>
              </Border>
              <ContentPresenter VerticalAlignment="Center" RecognizesAccessKey="True"/>
            </StackPanel>
            <ControlTemplate.Triggers>
              <Trigger Property="IsChecked" Value="True">
                <Setter TargetName="Track" Property="Background" Value="#164E5B"/>
                <Setter TargetName="Track" Property="BorderBrush" Value="#54DED4"/>
                <Setter TargetName="Knob" Property="HorizontalAlignment" Value="Right"/>
                <Setter TargetName="Knob" Property="Margin" Value="0,0,2,0"/>
                <Setter TargetName="Knob" Property="Background" Value="#7CF6EE"/>
              </Trigger>
              <Trigger Property="IsMouseOver" Value="True">
                <Setter TargetName="Track" Property="BorderBrush" Value="#54DED4"/>
              </Trigger>
              <Trigger Property="IsEnabled" Value="False">
                <Setter Property="Opacity" Value="0.45"/>
              </Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>

    <!-- RadioButton elegante -->
    <Style TargetType="RadioButton">
      <Setter Property="Foreground" Value="#F3EAD6"/>
      <Setter Property="FontSize" Value="13"/>
      <Setter Property="Margin" Value="0,3"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="RadioButton">
            <StackPanel Orientation="Horizontal" VerticalAlignment="Center" Background="Transparent">
              <Border x:Name="Ring" Width="18" Height="18" CornerRadius="9" Background="#0D152C" BorderBrush="#354C7C" BorderThickness="1.5" VerticalAlignment="Center" Margin="0,0,10,0">
                <Border x:Name="Dot" Width="8" Height="8" CornerRadius="4" Background="#54DED4" Visibility="Collapsed" HorizontalAlignment="Center" VerticalAlignment="Center"/>
              </Border>
              <ContentPresenter VerticalAlignment="Center"/>
            </StackPanel>
            <ControlTemplate.Triggers>
              <Trigger Property="IsChecked" Value="True">
                <Setter TargetName="Ring" Property="BorderBrush" Value="#54DED4"/>
                <Setter TargetName="Ring" Property="Background" Value="#143648"/>
                <Setter TargetName="Dot" Property="Visibility" Value="Visible"/>
              </Trigger>
              <Trigger Property="IsMouseOver" Value="True">
                <Setter TargetName="Ring" Property="BorderBrush" Value="#54DED4"/>
              </Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>

    <!-- ComboBox oscuro estilizado -->
    <Style TargetType="ComboBoxItem">
      <Setter Property="Foreground" Value="#DCE6F5"/>
      <Setter Property="Background" Value="Transparent"/>
      <Setter Property="Padding" Value="10,7"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="ComboBoxItem">
            <Border x:Name="Bd" Background="{TemplateBinding Background}" CornerRadius="5" Padding="{TemplateBinding Padding}" Margin="3,1">
              <ContentPresenter VerticalAlignment="Center"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsHighlighted" Value="True">
                <Setter TargetName="Bd" Property="Background" Value="#182D58"/>
                <Setter Property="Foreground" Value="#7CF6EE"/>
              </Trigger>
              <Trigger Property="IsSelected" Value="True">
                <Setter TargetName="Bd" Property="Background" Value="#153B4E"/>
                <Setter Property="Foreground" Value="#54DED4"/>
              </Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>

    <Style TargetType="ComboBox">
      <Setter Property="Foreground" Value="#F3EAD6"/>
      <Setter Property="Background" Value="#0C1429"/>
      <Setter Property="BorderBrush" Value="#2A3F6C"/>
      <Setter Property="BorderThickness" Value="1"/>
      <Setter Property="SnapsToDevicePixels" Value="True"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="ComboBox">
            <Grid>
              <ToggleButton x:Name="ToggleBtn" Focusable="False" IsChecked="{Binding IsDropDownOpen, Mode=TwoWay, RelativeSource={RelativeSource TemplatedParent}}" ClickMode="Press" Cursor="Hand">
                <ToggleButton.Template>
                  <ControlTemplate TargetType="ToggleButton">
                    <Border x:Name="Bd" Background="#0C1429" BorderBrush="#2A3F6C" BorderThickness="1" CornerRadius="7">
                      <Grid>
                        <Grid.ColumnDefinitions>
                          <ColumnDefinition Width="*"/>
                          <ColumnDefinition Width="28"/>
                        </Grid.ColumnDefinitions>
                        <TextBlock Grid.Column="1" Text="▾" Foreground="#54DED4" FontSize="12" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                      </Grid>
                    </Border>
                    <ControlTemplate.Triggers>
                      <Trigger Property="IsMouseOver" Value="True">
                        <Setter TargetName="Bd" Property="BorderBrush" Value="#54DED4"/>
                        <Setter TargetName="Bd" Property="Background" Value="#111C38"/>
                      </Trigger>
                      <Trigger Property="IsChecked" Value="True">
                        <Setter TargetName="Bd" Property="BorderBrush" Value="#54DED4"/>
                      </Trigger>
                    </ControlTemplate.Triggers>
                  </ControlTemplate>
                </ToggleButton.Template>
              </ToggleButton>
              <ContentPresenter x:Name="ContentSite" IsHitTestVisible="False" Content="{TemplateBinding SelectionBoxItem}" ContentTemplate="{TemplateBinding SelectionBoxItemTemplate}" ContentTemplateSelector="{TemplateBinding ItemTemplateSelector}" Margin="10,4,28,4" VerticalAlignment="Center" HorizontalAlignment="Left"/>
              <Popup x:Name="Popup" Placement="Bottom" IsOpen="{TemplateBinding IsDropDownOpen}" AllowsTransparency="True" Focusable="False" PopupAnimation="Slide">
                <Grid x:Name="DropDown" SnapsToDevicePixels="True" MinWidth="{TemplateBinding ActualWidth}" MaxHeight="260">
                  <Border x:Name="DropDownBorder" Background="#0A1124" BorderBrush="#355288" BorderThickness="1" CornerRadius="8" Margin="0,4,0,0" Padding="2">
                    <ScrollViewer VerticalScrollBarVisibility="Auto">
                      <StackPanel IsItemsHost="True" KeyboardNavigation.DirectionalNavigation="Contained"/>
                    </ScrollViewer>
                  </Border>
                </Grid>
              </Popup>
            </Grid>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>

    <!-- Slider limpio estilo estudio -->
    <Style TargetType="Slider">
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Slider">
            <Grid VerticalAlignment="Center" Height="22">
              <Border Height="5" CornerRadius="2.5" Background="#1A2748" BorderBrush="#283C66" BorderThickness="1" VerticalAlignment="Center"/>
              <Track x:Name="PART_Track">
                <Track.Thumb>
                  <Thumb>
                    <Thumb.Template>
                      <ControlTemplate TargetType="Thumb">
                        <Border x:Name="Knob" Width="16" Height="16" CornerRadius="8" Background="#54DED4" BorderBrush="#B4FFF8" BorderThickness="1.5"/>
                        <ControlTemplate.Triggers>
                          <Trigger Property="IsMouseOver" Value="True">
                            <Setter TargetName="Knob" Property="Background" Value="#7CF6EE"/>
                          </Trigger>
                        </ControlTemplate.Triggers>
                      </ControlTemplate>
                    </Thumb.Template>
                  </Thumb>
                </Track.Thumb>
              </Track>
            </Grid>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
  </Window.Resources>

  <Grid>
    <Grid.Background>
      <LinearGradientBrush StartPoint="0,0" EndPoint="1,1">
        <GradientStop Color="#060913" Offset="0"/>
        <GradientStop Color="#090F22" Offset="0.6"/>
        <GradientStop Color="#060A16" Offset="1"/>
      </LinearGradientBrush>
    </Grid.Background>

    <Grid Margin="16">
      <Grid.RowDefinitions>
        <RowDefinition Height="Auto"/>
        <RowDefinition Height="*"/>
        <RowDefinition Height="Auto"/>
      </Grid.RowDefinitions>

      <!-- Cabecera Studio -->
      <Border Grid.Row="0" BorderBrush="#223359" BorderThickness="1" CornerRadius="12" Padding="18,12" Margin="0,0,0,14">
        <Border.Background>
          <LinearGradientBrush StartPoint="0,0" EndPoint="1,0">
            <GradientStop Color="#0D1630" Offset="0"/>
            <GradientStop Color="#101B3B" Offset="0.5"/>
            <GradientStop Color="#0C142B" Offset="1"/>
          </LinearGradientBrush>
        </Border.Background>
        <DockPanel>
          <StackPanel>
            <StackPanel Orientation="Horizontal">
              <TextBlock Text="✦ PIXELZEN WORLDS" Foreground="#54DED4" FontSize="17.5" FontWeight="Bold"/>
              <Border Background="#12303D" BorderBrush="#3C9BA4" BorderThickness="1" CornerRadius="5" Padding="8,2" Margin="10,1,0,1" VerticalAlignment="Center">
                <TextBlock Text="DESKTOP STUDIO" Foreground="#7CF6EE" FontSize="9.5" FontWeight="Bold"/>
              </Border>
              <Border x:Name="BadgeMotor" Background="#102924" BorderBrush="#2E8B6B" BorderThickness="1" CornerRadius="5" Padding="8,2" Margin="6,1,0,1" VerticalAlignment="Center">
                <TextBlock x:Name="TxtMotorBadge" Text="● MOTOR NATIVO" Foreground="#72E6AE" FontSize="9.5" FontWeight="Bold"/>
              </Border>
            </StackPanel>
            <TextBlock x:Name="TxtMonInfo" Text="" Foreground="#9AB0CE" FontSize="12" Margin="0,4,0,0"/>
          </StackPanel>
          <StackPanel Orientation="Horizontal" DockPanel.Dock="Right" HorizontalAlignment="Right" VerticalAlignment="Center">
            <Button x:Name="BtnMiniTray" Content="▾ Minimizar al reloj" Style="{StaticResource PillBtn}" Margin="0,0,8,0"/>
            <Button x:Name="BtnSalirTotal" Content="✕ Cerrar app" Style="{StaticResource PillBtn}" Foreground="#FFA8B0" BorderBrush="#5C2B39"/>
          </StackPanel>
        </DockPanel>
      </Border>

      <!-- Cuerpo principal: Navegación | Configurador | Estudio en Vivo -->
      <Grid Grid.Row="1">
        <Grid.ColumnDefinitions>
          <ColumnDefinition Width="212"/>
          <ColumnDefinition Width="14"/>
          <ColumnDefinition Width="*"/>
          <ColumnDefinition Width="14"/>
          <ColumnDefinition Width="430"/>
        </Grid.ColumnDefinitions>

        <!-- Navegación Lateral -->
        <Border Grid.Column="0" Background="#0A1022" BorderBrush="#1F2F52" BorderThickness="1" CornerRadius="12" Padding="12">
          <DockPanel>
            <StackPanel DockPanel.Dock="Top">
              <TextBlock Text="CONFIGURADOR" Foreground="#64799E" FontSize="10.5" FontWeight="Bold" Margin="8,4,0,10"/>
              <Button x:Name="NavMundos" Content="1 · Elegir Mundo" Style="{StaticResource NavBtn}"/>
              <Button x:Name="NavPantallas" Content="2 · Pantallas y Luz" Style="{StaticResource NavBtn}"/>
              <Button x:Name="NavHud" Content="3 · Cajitas del Fondo" Style="{StaticResource NavBtn}"/>
              <Button x:Name="NavSistema" Content="4 · Ajustes e Inicio" Style="{StaticResource NavBtn}"/>
            </StackPanel>
            <Border DockPanel.Dock="Bottom" VerticalAlignment="Bottom" Background="#0E1730" BorderBrush="#23365E" BorderThickness="1" CornerRadius="10" Padding="12" Margin="0,12,0,0">
              <StackPanel>
                <TextBlock Text="✦ CONFIGURACIÓN ACTIVA" Foreground="#E6B45A" FontSize="10" FontWeight="Bold" Margin="0,0,0,6"/>
                <TextBlock x:Name="TxtResumen" Text="" Foreground="#C4D2E6" FontSize="11.5" TextWrapping="Wrap" LineHeight="18"/>
              </StackPanel>
            </Border>
          </DockPanel>
        </Border>

        <!-- Área Principal de Páginas -->
        <Border Grid.Column="2" Background="#0A1022" BorderBrush="#1F2F52" BorderThickness="1" CornerRadius="12" Padding="18">
          <Grid>
            <!-- PÁGINA 1: SERIES -> TEMAS -> IMÁGENES POR PANTALLA -->
            <ScrollViewer x:Name="PageMundos" VerticalScrollBarVisibility="Auto">
              <StackPanel Margin="0,0,6,0">
                <!-- Paso 1: Elegir Serie -->
                <StackPanel x:Name="PanelSeries">
                  <TextBlock Text="Elige tu Serie o Universo" Foreground="#F3EAD6" FontSize="17" FontWeight="Bold"/>
                  <TextBlock Text="Selecciona un anime o universo. Si incluye varios escenarios podrás elegir mundo; si solo tiene uno pasarás directo a asignar escenas." Foreground="#8EA3C4" FontSize="12" Margin="0,4,0,14" TextWrapping="Wrap" LineHeight="17"/>
                  <StackPanel x:Name="ListaSeries"/>
                </StackPanel>

                <!-- Paso 2: Elegir Tema dentro de la Serie -->
                <StackPanel x:Name="PanelTemasSerie" Visibility="Collapsed">
                  <DockPanel Margin="0,0,0,12">
                    <Button x:Name="BtnVolverASeries" Content="← Series" Style="{StaticResource PillBtn}" DockPanel.Dock="Left" Margin="0,0,12,0"/>
                    <TextBlock x:Name="TxtSerieTitulo" Text="Mushoku Tensei" Foreground="#F3EAD6" FontSize="17" FontWeight="Bold" VerticalAlignment="Center"/>
                  </DockPanel>
                  <TextBlock Text="Esta serie cuenta con varios escenarios pixel art. Pulsa el que quieras personalizar:" Foreground="#8EA3C4" FontSize="12" Margin="0,0,0,14" TextWrapping="Wrap"/>
                  <StackPanel x:Name="ListaTarjetasMundos"/>
                </StackPanel>

                <!-- Paso 3: Elegir qué imagen va en cada monitor y en Pantalla de Bloqueo -->
                <StackPanel x:Name="PanelImagenesTema" Visibility="Collapsed">
                  <DockPanel Margin="0,0,0,10">
                    <Button x:Name="BtnVolverDeImagenes" Content="← Volver" Style="{StaticResource PillBtn}" DockPanel.Dock="Left" Margin="0,0,12,0"/>
                    <TextBlock x:Name="TxtTemaImagenesTitulo" Text="Región de Fittoa" Foreground="#F3EAD6" FontSize="16.5" FontWeight="Bold" VerticalAlignment="Center" TextTrimming="CharacterEllipsis"/>
                  </DockPanel>
                  <TextBlock Text="Asigna libremente cualquiera de las 3 escenas a cada monitor y a la pantalla de bloqueo:" Foreground="#8EA3C4" FontSize="12" Margin="0,0,0,10" TextWrapping="Wrap"/>

                  <WrapPanel Margin="0,0,0,12">
                    <Button x:Name="BtnPresetClasico" Content="✦ Clásica (1·2·3)" Style="{StaticResource PillBtn}" Foreground="#7CF6EE" BorderBrush="#397D88" Margin="0,0,6,6" FontSize="11"/>
                    <Button x:Name="BtnRepetirPrincipal" Content="✨ Usar Escena 1 en todas" Style="{StaticResource PillBtn}" Margin="0,0,6,6" FontSize="11"/>
                    <Button x:Name="BtnRepetirSecundaria" Content="✨ Usar Escena 2 en todas" Style="{StaticResource PillBtn}" Margin="0,0,6,6" FontSize="11"/>
                    <Button x:Name="BtnRepetirBloqueo" Content="✨ Usar Escena 3 en todas" Style="{StaticResource PillBtn}" Margin="0,0,0,6" FontSize="11"/>
                  </WrapPanel>

                  <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="12" Margin="0,0,0,10">
                    <StackPanel>
                      <TextBlock Text="🖥️ MONITOR PRINCIPAL" Foreground="#54DED4" FontSize="11.5" FontWeight="Bold" Margin="0,0,0,8"/>
                      <UniformGrid x:Name="GridPickerM1" Columns="3"/>
                    </StackPanel>
                  </Border>

                  <Border x:Name="PanelPickerM2" Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="12" Margin="0,0,0,10">
                    <StackPanel>
                      <TextBlock Text="🖥️ MONITOR SECUNDARIO" Foreground="#E6B45A" FontSize="11.5" FontWeight="Bold" Margin="0,0,0,8"/>
                      <UniformGrid x:Name="GridPickerM2" Columns="3"/>
                    </StackPanel>
                  </Border>

                  <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="12" Margin="0,0,0,12">
                    <StackPanel>
                      <DockPanel Margin="0,0,0,8">
                        <CheckBox x:Name="ChkBloqueoMenu" Content="🔒 PANTALLA DE BLOQUEO DE WINDOWS" FontSize="11.5" FontWeight="Bold" Foreground="#88C8FF" Margin="0"/>
                      </DockPanel>
                      <UniformGrid x:Name="GridPickerBloq" Columns="3"/>
                    </StackPanel>
                  </Border>

                  <Button x:Name="BtnIrAPantallasLuz" Content="⚙️ Ajustar monitores y ciclo horario de luz →" Style="{StaticResource PillBtn}" HorizontalAlignment="Left" Margin="0,2,0,4"/>
                </StackPanel>
              </StackPanel>
            </ScrollViewer>

            <!-- PÁGINA 2: PANTALLAS Y LUZ -->
            <ScrollViewer x:Name="PagePantallas" VerticalScrollBarVisibility="Auto" Visibility="Collapsed">
              <StackPanel Margin="0,0,6,0">
                <TextBlock Text="Disposición de Pantallas" Foreground="#F3EAD6" FontSize="17" FontWeight="Bold"/>
                <TextBlock Text="En modo 2 pantallas, tu monitor principal muestra la escena base y el segundo continúa la historia sin repetirse." Foreground="#8EA3C4" FontSize="12" Margin="0,4,0,12" TextWrapping="Wrap"/>

                <Border x:Name="CardMon1" Background="#0E1730" BorderBrush="#263860" BorderThickness="1.5" CornerRadius="10" Padding="14" Margin="0,0,0,8" Cursor="Hand">
                  <StackPanel>
                    <RadioButton x:Name="RbMon1" GroupName="Mon" Content="Solo 1 Pantalla (Únicamente monitor principal)" FontWeight="SemiBold"/>
                    <TextBlock Text="Ideal para portátiles o si prefieres animar un único escritorio." Foreground="#8EA3C4" FontSize="11.5" Margin="28,3,0,0" TextWrapping="Wrap"/>
                  </StackPanel>
                </Border>

                <Border x:Name="CardMon2" Background="#0E1730" BorderBrush="#263860" BorderThickness="1.5" CornerRadius="10" Padding="14" Margin="0,0,0,16" Cursor="Hand">
                  <StackPanel>
                    <RadioButton x:Name="RbMon2" GroupName="Mon" Content="2 Pantallas (Principal + Continuación extendida)" FontWeight="SemiBold"/>
                    <TextBlock x:Name="TxtMon2Detalle" Text="Detectando pantallas..." Foreground="#54DED4" FontSize="11.5" Margin="28,3,0,0" TextWrapping="Wrap"/>
                  </StackPanel>
                </Border>

                <TextBlock Text="Escena por Pantalla y Bloqueo" Foreground="#F3EAD6" FontSize="16" FontWeight="Bold" Margin="0,2,0,4"/>
                <TextBlock Text="Cada mundo tiene 3 escenas independientes (Principal, Secundaria y Bloqueo)." Foreground="#8EA3C4" FontSize="12" Margin="0,0,0,10" TextWrapping="Wrap"/>

                <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="14" Margin="0,0,0,16">
                  <StackPanel>
                    <TextBlock Text="🖥️ Pantalla Principal" Foreground="#54DED4" FontSize="12" FontWeight="Bold" Margin="0,0,0,5"/>
                    <ComboBox x:Name="CmbFondoPrincipal" FontSize="12" Height="34" Margin="0,0,0,12">
                      <ComboBoxItem Content="Principal" Tag="principal"/>
                      <ComboBoxItem Content="Secundaria" Tag="secundaria"/>
                      <ComboBoxItem Content="Bloqueo" Tag="bloqueo"/>
                    </ComboBox>

                    <StackPanel x:Name="PanelComboSec">
                      <TextBlock Text="🖥️ Pantalla Secundaria" Foreground="#E6B45A" FontSize="12" FontWeight="Bold" Margin="0,0,0,5"/>
                      <ComboBox x:Name="CmbFondoSecundaria" FontSize="12" Height="34" Margin="0,0,0,12">
                        <ComboBoxItem Content="Principal" Tag="principal"/>
                        <ComboBoxItem Content="Secundaria" Tag="secundaria"/>
                        <ComboBoxItem Content="Bloqueo" Tag="bloqueo"/>
                      </ComboBox>
                    </StackPanel>

                    <CheckBox x:Name="ChkBloqueo" Content="🔒 Aplicar también fondo a la Pantalla de Bloqueo de Windows" FontWeight="SemiBold" Margin="0,2,0,8"/>
                    <StackPanel x:Name="PanelComboBloq">
                      <ComboBox x:Name="CmbFondoBloqueo" FontSize="12" Height="34" Margin="0,0,0,0">
                        <ComboBoxItem Content="Principal" Tag="principal"/>
                        <ComboBoxItem Content="Secundaria" Tag="secundaria"/>
                        <ComboBoxItem Content="Bloqueo" Tag="bloqueo"/>
                      </ComboBox>
                    </StackPanel>
                  </StackPanel>
                </Border>

                <TextBlock Text="Ciclo de Luz del Cielo" Foreground="#F3EAD6" FontSize="16" FontWeight="Bold" Margin="0,2,0,4"/>
                <TextBlock Text="Controla cómo evoluciona la escena entre Día, Atardecer Dorado y Noche estrellada." Foreground="#8EA3C4" FontSize="12" Margin="0,0,0,10" TextWrapping="Wrap"/>

                <ComboBox x:Name="CmbModo" FontSize="12.5" Height="36" Margin="0,0,0,10">
                  <ComboBoxItem Content="🌗 Ciclo suave — Día y noche cada 90 min (Recomendado)" Tag="90m"/>
                  <ComboBoxItem Content="🕒 Hora real — Igual que el reloj de tu Windows" Tag="real"/>
                  <ComboBoxItem Content="⚡ Paseo rápido — Cambia en 90 segundos para probar" Tag="demo"/>
                  <ComboBoxItem Content="🔒 Momento fijo — Elige tú Día, Atardecer o Noche" Tag="fija"/>
                </ComboBox>

                <Border x:Name="PanelHora" Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="14" Margin="0,2,0,0">
                  <StackPanel>
                    <TextBlock Text="Elige el momento fijo que prefieras:" Foreground="#E6B45A" FontSize="12" FontWeight="Bold" Margin="0,0,0,10"/>
                    <StackPanel Orientation="Horizontal" Margin="0,0,0,12">
                      <Button x:Name="BtnFijarDia" Content="☀️ Día (13:00)" Style="{StaticResource PillBtn}" Margin="0,0,6,0"/>
                      <Button x:Name="BtnFijarDor" Content="🌅 Atardecer (18:30)" Style="{StaticResource PillBtn}" Margin="0,0,6,0"/>
                      <Button x:Name="BtnFijarNoc" Content="🌙 Noche (22:00)" Style="{StaticResource PillBtn}"/>
                    </StackPanel>
                    <DockPanel>
                      <TextBlock x:Name="TxtHoraVal" Text="21:30" Foreground="#54DED4" FontFamily="Consolas" FontSize="14" FontWeight="Bold" DockPanel.Dock="Right" Width="56" TextAlignment="Right" VerticalAlignment="Center"/>
                      <Slider x:Name="SldHora" Minimum="0" Maximum="23.75" TickFrequency="0.25" IsSnapToTickEnabled="True" Value="21.5"/>
                    </DockPanel>
                  </StackPanel>
                </Border>
              </StackPanel>
            </ScrollViewer>

            <!-- PÁGINA 3: CAJITAS DEL ESCRITORIO (HUD) -->
            <ScrollViewer x:Name="PageHud" VerticalScrollBarVisibility="Auto" Visibility="Collapsed">
              <StackPanel Margin="0,0,6,0">
                <DockPanel Margin="0,0,0,4">
                  <TextBlock Text="Tarjetas Flotantes (HUD)" Foreground="#F3EAD6" FontSize="17" FontWeight="Bold" VerticalAlignment="Center"/>
                  <CheckBox x:Name="ChkHudMaster" Content="Activadas" DockPanel.Dock="Right" HorizontalAlignment="Right" FontWeight="Bold" Foreground="#54DED4" Margin="0"/>
                </DockPanel>
                <TextBlock Text="Transparentes al ratón: puedes hacer clic a través de ellas en tu escritorio. Mira su distribución en el estudio a la derecha." Foreground="#8EA3C4" FontSize="12" Margin="0,2,0,12" TextWrapping="Wrap"/>

                <WrapPanel Margin="0,0,0,14">
                  <Button x:Name="BtnHudTodas" Content="✦ Mostrar todas" Style="{StaticResource PillBtn}" Margin="0,0,6,6"/>
                  <Button x:Name="BtnHudMinimo" Content="Modo limpio (Reloj + Frase)" Style="{StaticResource PillBtn}" Margin="0,0,6,6"/>
                  <Button x:Name="BtnHudSoloReloj" Content="Solo Reloj" Style="{StaticResource PillBtn}" Margin="0,0,0,6"/>
                </WrapPanel>

                <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="13" Margin="0,0,0,9">
                  <StackPanel>
                    <CheckBox x:Name="ChkTiempo" Content="🕒 Reloj, fecha y nombre del mundo" FontWeight="SemiBold"/>
                    <TextBlock Text="Muestra la hora grande, la fecha en español y el escenario activo." Foreground="#8EA3C4" FontSize="11.5" Margin="46,0,0,0"/>
                  </StackPanel>
                </Border>
                <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="13" Margin="0,0,0,9">
                  <StackPanel>
                    <CheckBox x:Name="ChkSistema" Content="💻 Rendimiento del PC (CPU, RAM, Disco, Batería)" FontWeight="SemiBold"/>
                    <TextBlock Text="Barras visuales en tiempo real para controlar la carga del equipo." Foreground="#8EA3C4" FontSize="11.5" Margin="46,0,0,0"/>
                  </StackPanel>
                </Border>
                <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="13" Margin="0,0,0,9">
                  <StackPanel>
                    <CheckBox x:Name="ChkRed" Content="🌐 Conexión e Internet (Wi-Fi / IP / Velocidad)" FontWeight="SemiBold"/>
                    <TextBlock Text="Muestra tu red activa, IP local y tráfico de subida/bajada." Foreground="#8EA3C4" FontSize="11.5" Margin="46,0,0,0"/>
                  </StackPanel>
                </Border>
                <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="13" Margin="0,0,0,9">
                  <StackPanel>
                    <CheckBox x:Name="ChkDev" Content="🛠️ Información técnica / Programador" FontWeight="SemiBold"/>
                    <TextBlock Text="Nombre del equipo, rama Git actual y entorno detectado." Foreground="#8EA3C4" FontSize="11.5" Margin="46,0,0,0"/>
                  </StackPanel>
                </Border>
                <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="13">
                  <StackPanel>
                    <CheckBox x:Name="ChkGrimorio" Content="📖 Frase del universo (Grimorio)" FontWeight="SemiBold"/>
                    <TextBlock Text="Citas icónicas de la serie que rotan automáticamente." Foreground="#8EA3C4" FontSize="11.5" Margin="46,0,0,0"/>
                  </StackPanel>
                </Border>
              </StackPanel>
            </ScrollViewer>

            <!-- PÁGINA 4: AJUSTES E INICIO -->
            <ScrollViewer x:Name="PageSistema" VerticalScrollBarVisibility="Auto" Visibility="Collapsed">
              <StackPanel Margin="0,0,6,0">
                <TextBlock Text="Comodidad e Inicio Automático" Foreground="#F3EAD6" FontSize="17" FontWeight="Bold"/>
                <TextBlock Text="Deja PixelZen listo para iniciarse sin consolas al encender Windows." Foreground="#8EA3C4" FontSize="12" Margin="0,4,0,14" TextWrapping="Wrap"/>

                <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="14" Margin="0,0,0,10">
                  <StackPanel>
                    <TextBlock Text="Acceso directo en el Escritorio" Foreground="#E6B45A" FontSize="13.5" FontWeight="Bold" Margin="0,0,0,4"/>
                    <TextBlock Text="Crea un icono en tu Escritorio para abrir este estudio con un doble clic." Foreground="#8EA3C4" FontSize="11.5" Margin="0,0,0,10" TextWrapping="Wrap"/>
                    <Button x:Name="BtnAccesoDirecto" Content="📌 Crear acceso directo en mi Escritorio" Style="{StaticResource PillBtn}" HorizontalAlignment="Left" Foreground="#54DED4" BorderBrush="#3C8D96"/>
                  </StackPanel>
                </Border>

                <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="14" Margin="0,0,0,10">
                  <StackPanel>
                    <CheckBox x:Name="ChkAutoInicio" Content="🚀 Aplicar fondos e iniciar en bandeja al encender Windows" FontWeight="SemiBold"/>
                    <TextBlock Text="Restaura automáticamente tus fondos animados y tarjetas al iniciar sesión." Foreground="#8EA3C4" FontSize="11.5" Margin="46,0,0,10" TextWrapping="Wrap"/>
                    <CheckBox x:Name="ChkTrayCerrar" Content="📌 Al pulsar cerrar (X), minimizar junto al reloj en vez de salir" FontWeight="SemiBold"/>
                    <TextBlock Text="Permite cambiar de mundo o activar el HUD en un clic desde la bandeja." Foreground="#8EA3C4" FontSize="11.5" Margin="46,0,0,0" TextWrapping="Wrap"/>
                  </StackPanel>
                </Border>

                <Border Background="#0E1730" BorderBrush="#23355B" BorderThickness="1" CornerRadius="10" Padding="14">
                  <StackPanel>
                    <TextBlock Text="Estado del sistema y actualizaciones" Foreground="#E6B45A" FontSize="13.5" FontWeight="Bold" Margin="0,0,0,8"/>
                    <TextBlock x:Name="TxtDiag" Text="" Foreground="#C4D2E6" FontSize="12" TextWrapping="Wrap" LineHeight="20" Margin="0,0,0,12"/>
                    <StackPanel Orientation="Horizontal">
                      <Button x:Name="BtnBuscarUpdate" Content="🔄 Buscar actualización" Style="{StaticResource PillBtn}" Foreground="#54DED4" BorderBrush="#3C8D96" Margin="0,0,8,0"/>
                      <Button x:Name="BtnRestaurar" Content="Restablecer recomendados" Style="{StaticResource PillBtn}"/>
                    </StackPanel>
                  </StackPanel>
                </Border>
              </StackPanel>
            </ScrollViewer>
          </Grid>
        </Border>

        <!-- Estudio de Vista Previa en Vivo (Columna Derecha) -->
        <Border Grid.Column="4" Background="#0A1022" BorderBrush="#22345B" BorderThickness="1" CornerRadius="12" Padding="15">
          <DockPanel>
            <DockPanel DockPanel.Dock="Top" Margin="0,0,0,10">
              <TextBlock Text="ESCRITORIO EN VIVO" Foreground="#54DED4" FontSize="12" FontWeight="Bold" VerticalAlignment="Center"/>
              <Border DockPanel.Dock="Right" HorizontalAlignment="Right" Background="#060A16" BorderBrush="#223358" BorderThickness="1" CornerRadius="8" Padding="3">
                <StackPanel Orientation="Horizontal">
                  <Button x:Name="BtnPrevDia" Content="☀️ Día" Style="{StaticResource PillBtn}" Padding="7,3" FontSize="10.5" Margin="0,0,2,0"/>
                  <Button x:Name="BtnPrevDor" Content="🌅 Dorado" Style="{StaticResource PillBtn}" Padding="7,3" FontSize="10.5" Margin="0,0,2,0"/>
                  <Button x:Name="BtnPrevNoc" Content="🌙 Noche" Style="{StaticResource PillBtn}" Padding="7,3" FontSize="10.5"/>
                </StackPanel>
              </Border>
            </DockPanel>

            <Border DockPanel.Dock="Bottom" Background="#0E1730" BorderBrush="#263B66" BorderThickness="1" CornerRadius="8" Padding="10,8" Margin="0,8,0,0">
              <TextBlock x:Name="TxtEstado" Text="Elige una escena a la izquierda y pulsa Aplicar a mi escritorio." Foreground="#72E6AE" FontSize="11.5" TextWrapping="Wrap"/>
            </Border>

            <ScrollViewer VerticalScrollBarVisibility="Auto">
              <StackPanel Margin="0,0,2,0">
                <DockPanel Margin="0,0,0,4">
                  <TextBlock x:Name="TxtPrev1Title" Text="PANTALLA 1" Foreground="#E6B45A" FontSize="11" FontWeight="Bold" VerticalAlignment="Center" TextTrimming="CharacterEllipsis"/>
                  <Border DockPanel.Dock="Right" HorizontalAlignment="Right" Background="#12303D" CornerRadius="4" Padding="6,1" Margin="6,0,0,0">
                    <TextBlock Text="PRINCIPAL" Foreground="#54DED4" FontSize="9" FontWeight="Bold"/>
                  </Border>
                </DockPanel>
                <Border BorderBrush="#49C8C0" BorderThickness="1.5" CornerRadius="8" Background="#040711" Height="150" Margin="0,0,0,7" ClipToBounds="True">
                  <Grid>
                    <Image x:Name="ImgPrev1" Stretch="UniformToFill" RenderOptions.BitmapScalingMode="NearestNeighbor"/>
                    <!-- Simulación de cajitas HUD superpuestas -->
                    <StackPanel x:Name="MockHudPanel" HorizontalAlignment="Right" VerticalAlignment="Top" Margin="6,6,6,0" Width="106">
                      <Border x:Name="MockTiempo" Background="#D8090F20" BorderBrush="#8A6E44" BorderThickness="1" CornerRadius="4" Padding="5,3" Margin="0,0,0,2">
                        <StackPanel>
                          <TextBlock Text="21:34" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold"/>
                          <TextBlock x:Name="TxtMockMundo" Text="Fittoa" Foreground="#E6C06E" FontFamily="Consolas" FontSize="7" TextTrimming="CharacterEllipsis"/>
                        </StackPanel>
                      </Border>
                      <Border x:Name="MockSistema" Background="#D8090F20" BorderBrush="#8A6E44" BorderThickness="1" CornerRadius="4" Padding="5,2.5" Margin="0,0,0,2">
                        <TextBlock Text="CPU 12%  RAM 48%" Foreground="#72C48C" FontFamily="Consolas" FontSize="7"/>
                      </Border>
                      <Border x:Name="MockRed" Background="#D8090F20" BorderBrush="#8A6E44" BorderThickness="1" CornerRadius="4" Padding="5,2.5" Margin="0,0,0,2">
                        <TextBlock Text="WI-FI  ↓ 12K/s" Foreground="#54DED4" FontFamily="Consolas" FontSize="7"/>
                      </Border>
                      <Border x:Name="MockDev" Background="#D8090F20" BorderBrush="#8A6E44" BorderThickness="1" CornerRadius="4" Padding="5,2.5" Margin="0,0,0,2">
                        <TextBlock Text="DEV · main" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="7"/>
                      </Border>
                      <Border x:Name="MockGrimorio" Background="#D8090F20" BorderBrush="#8A6E44" BorderThickness="1" CornerRadius="4" Padding="5,2.5">
                        <TextBlock Text="«Frase del mundo...»" Foreground="#E6C06E" FontFamily="Consolas" FontSize="7" TextTrimming="CharacterEllipsis"/>
                      </Border>
                    </StackPanel>
                    <!-- Sutil simulación barra de tareas Windows -->
                    <Border VerticalAlignment="Bottom" Height="6" Background="#90070B16">
                      <StackPanel Orientation="Horizontal" HorizontalAlignment="Center" VerticalAlignment="Center">
                        <Border Width="4" Height="2.5" Background="#54DED4" Margin="2,0"/>
                        <Border Width="4" Height="2.5" Background="#A8B8CF" Margin="2,0"/>
                        <Border Width="4" Height="2.5" Background="#E6B45A" Margin="2,0"/>
                      </StackPanel>
                    </Border>
                  </Grid>
                </Border>

                <StackPanel x:Name="PanelPrev2" Margin="0,0,0,7">
                  <DockPanel Margin="0,0,0,4">
                    <TextBlock x:Name="TxtPrev2Title" Text="PANTALLA 2 · HISTORIA EXTENDIDA" Foreground="#E6B45A" FontSize="11" FontWeight="Bold" VerticalAlignment="Center" TextTrimming="CharacterEllipsis"/>
                    <Border DockPanel.Dock="Right" HorizontalAlignment="Right" Background="#2B2112" CornerRadius="4" Padding="6,1" Margin="6,0,0,0">
                      <TextBlock Text="MONITOR 2" Foreground="#E6B45A" FontSize="9" FontWeight="Bold"/>
                    </Border>
                  </DockPanel>
                  <Border BorderBrush="#8A6E44" BorderThickness="1.5" CornerRadius="8" Background="#040711" Height="114" ClipToBounds="True">
                    <Image x:Name="ImgPrev2" Stretch="UniformToFill" RenderOptions.BitmapScalingMode="NearestNeighbor"/>
                  </Border>
                  <TextBlock x:Name="TxtM2Sub" Visibility="Collapsed" Text=""/>
                </StackPanel>

                <StackPanel x:Name="PanelPrevBloqueo">
                  <DockPanel Margin="0,0,0,4">
                    <TextBlock x:Name="TxtPrevBloqTitle" Text="🔒 PANTALLA DE BLOQUEO" Foreground="#88C8FF" FontSize="11" FontWeight="Bold" VerticalAlignment="Center" TextTrimming="CharacterEllipsis"/>
                    <Border DockPanel.Dock="Right" HorizontalAlignment="Right" Background="#132440" CornerRadius="4" Padding="6,1" Margin="6,0,0,0">
                      <TextBlock Text="WINDOWS LOCK" Foreground="#88C8FF" FontSize="9" FontWeight="Bold"/>
                    </Border>
                  </DockPanel>
                  <Border BorderBrush="#4C6FA8" BorderThickness="1.5" CornerRadius="8" Background="#040711" Height="92" ClipToBounds="True">
                    <Grid>
                      <Image x:Name="ImgPrevBloqueo" Stretch="UniformToFill" RenderOptions.BitmapScalingMode="NearestNeighbor"/>
                      <Border Background="#38040814"/>
                      <StackPanel HorizontalAlignment="Center" VerticalAlignment="Top" Margin="0,8,0,0">
                        <TextBlock Text="21:34" Foreground="#F6F4EA" FontSize="19" FontWeight="Bold" HorizontalAlignment="Center"/>
                        <TextBlock Text="Pantalla de bloqueo de Windows" Foreground="#D4E2F6" FontSize="9" HorizontalAlignment="Center"/>
                      </StackPanel>
                    </Grid>
                  </Border>
                  <TextBlock x:Name="TxtBloqSub" Visibility="Collapsed" Text=""/>
                </StackPanel>
              </StackPanel>
            </ScrollViewer>
          </DockPanel>
        </Border>
      </Grid>

      <!-- Barra inferior de acciones -->
      <Border Grid.Row="2" Background="#0B1227" BorderBrush="#223359" BorderThickness="1" CornerRadius="12" Padding="14,11" Margin="0,14,0,0">
        <DockPanel>
          <StackPanel Orientation="Horizontal" DockPanel.Dock="Left">
            <Button x:Name="BtnWeb" Content="🎬 Visor animado en navegador" Style="{StaticResource PillBtn}" Foreground="#54DED4" BorderBrush="#397D88" Margin="0,0,8,0"/>
            <Button x:Name="BtnToggleHudNow" Content="👁️ Ocultar cajitas ahora" Style="{StaticResource PillBtn}"/>
          </StackPanel>
          <StackPanel Orientation="Horizontal" DockPanel.Dock="Right" HorizontalAlignment="Right">
            <Button x:Name="BtnSoloGuardar" Content="💾 Guardar sin aplicar" Style="{StaticResource PillBtn}" Margin="0,0,10,0"/>
            <Button x:Name="BtnAplicar" Content="✦ APLICAR A MI ESCRITORIO" Padding="24,10" FontSize="13.5" FontWeight="Bold" Foreground="#061217" BorderBrush="#7CF6EE" BorderThickness="1" Cursor="Hand">
              <Button.Template>
                <ControlTemplate TargetType="Button">
                  <Border x:Name="CtaBd" CornerRadius="9" BorderBrush="{TemplateBinding BorderBrush}" BorderThickness="{TemplateBinding BorderThickness}" Padding="{TemplateBinding Padding}">
                    <Border.Background>
                      <LinearGradientBrush StartPoint="0,0" EndPoint="1,0">
                        <GradientStop Color="#4CE0D6" Offset="0"/>
                        <GradientStop Color="#6EF7EE" Offset="1"/>
                      </LinearGradientBrush>
                    </Border.Background>
                    <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
                  </Border>
                  <ControlTemplate.Triggers>
                    <Trigger Property="IsMouseOver" Value="True">
                      <Setter TargetName="CtaBd" Property="Background">
                        <Setter.Value>
                          <LinearGradientBrush StartPoint="0,0" EndPoint="1,0">
                            <GradientStop Color="#6CF2E8" Offset="0"/>
                            <GradientStop Color="#9EFFF8" Offset="1"/>
                          </LinearGradientBrush>
                        </Setter.Value>
                      </Setter>
                    </Trigger>
                    <Trigger Property="IsPressed" Value="True">
                      <Setter TargetName="CtaBd" Property="Opacity" Value="0.88"/>
                    </Trigger>
                  </ControlTemplate.Triggers>
                </ControlTemplate>
              </Button.Template>
            </Button>
          </StackPanel>
        </DockPanel>
      </Border>
    </Grid>
  </Grid>
</Window>
"@

$reader = [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($xaml))
$win = [System.Windows.Markup.XamlReader]::Load($reader)
if (Test-Path $IconPath) {
    try { $win.Icon = [System.Windows.Media.Imaging.BitmapFrame]::Create((New-Object Uri($IconPath))) } catch {}
}

# Barra de título oscura nativa en Windows 11/10
$dwmCode = @'
using System;
using System.Runtime.InteropServices;
public static class PzWinTheme {
    [DllImport("dwmapi.dll")]
    public static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int attrValue, int attrSize);
    public static void ApplyDarkTitlebar(IntPtr hwnd) {
        if (hwnd == IntPtr.Zero) return;
        int dark = 1;
        DwmSetWindowAttribute(hwnd, 20, ref dark, 4);
        int captionColor = 0x00130906; // BGR de #060913
        DwmSetWindowAttribute(hwnd, 35, ref captionColor, 4);
        int textColor = 0x00D6EAF3; // BGR de #F3EAD6
        DwmSetWindowAttribute(hwnd, 36, ref textColor, 4);
    }
}
'@
Add-Type -TypeDefinition $dwmCode -ErrorAction SilentlyContinue
$win.Add_SourceInitialized({
    try {
        $hwnd = (New-Object System.Windows.Interop.WindowInteropHelper($win)).Handle
        [PzWinTheme]::ApplyDarkTitlebar($hwnd)
    } catch {}
})

$el = @{}
foreach ($n in 'TxtMonInfo','BadgeMotor','TxtMotorBadge','BtnMiniTray','BtnSalirTotal','NavMundos','NavPantallas','NavHud','NavSistema','TxtResumen','PageMundos','PagePantallas','PageHud','PageSistema','PanelSeries','ListaSeries','PanelTemasSerie','BtnVolverASeries','TxtSerieTitulo','PanelImagenesTema','BtnVolverDeImagenes','TxtTemaImagenesTitulo','BtnPresetClasico','BtnRepetirPrincipal','BtnRepetirSecundaria','BtnRepetirBloqueo','GridPickerM1','PanelPickerM2','GridPickerM2','ChkBloqueoMenu','GridPickerBloq','BtnIrAPantallasLuz','ListaTarjetasMundos','CardMon1','CardMon2','RbMon1','RbMon2','TxtMon2Detalle','CmbFondoPrincipal','PanelComboSec','CmbFondoSecundaria','ChkBloqueo','PanelComboBloq','CmbFondoBloqueo','CmbModo','PanelHora','BtnFijarDia','BtnFijarDor','BtnFijarNoc','TxtHoraVal','SldHora','ChkHudMaster','BtnHudTodas','BtnHudMinimo','BtnHudSoloReloj','ChkTiempo','ChkSistema','ChkRed','ChkDev','ChkGrimorio','BtnAccesoDirecto','ChkAutoInicio','ChkTrayCerrar','TxtDiag','BtnBuscarUpdate','BtnRestaurar','BtnPrevDia','BtnPrevDor','BtnPrevNoc','TxtPrev1Title','ImgPrev1','MockHudPanel','MockTiempo','TxtMockMundo','MockSistema','MockRed','MockDev','MockGrimorio','PanelPrev2','TxtPrev2Title','ImgPrev2','TxtM2Sub','PanelPrevBloqueo','TxtPrevBloqTitle','ImgPrevBloqueo','TxtBloqSub','TxtEstado','BtnWeb','BtnToggleHudNow','BtnSoloGuardar','BtnAplicar') {
    $el[$n] = $win.FindName($n)
}

$el.TxtMonInfo.Text = $monSummary
if ($screens.Count -ge 2) {
    $el.TxtMon2Detalle.Text = "¡Genial! Hemos detectado $($screens.Count) pantallas listas para la historia doble."
} else {
    $el.TxtMon2Detalle.Text = "Ahora solo hay 1 pantalla conectada, pero si conectas una segunda se activará la continuación."
}

function Cargar-Bitmap($ruta) {
    if (-not (Test-Path $ruta)) { return $null }
    $bmp = New-Object System.Windows.Media.Imaging.BitmapImage
    $bmp.BeginInit()
    $bmp.CacheOption = [System.Windows.Media.Imaging.BitmapCacheOption]::OnLoad
    $bmp.UriSource = New-Object Uri($ruta)
    $bmp.EndInit()
    return $bmp
}

$cfg = Cargar-Config
$script:selectedTema = if ($cfg.tema) { $cfg.tema } else { 'fittoa' }
$initTemaObj = $temas | Where-Object { $_.id -eq $script:selectedTema } | Select-Object -First 1
$script:selectedSerie = if ($initTemaObj) { $initTemaObj.serie } else { $seriesList[0] }
$script:previewFase = Detectar-Fase $cfg.modo $cfg.horaFija
$script:mundoVista = 'series'
$script:syncingCombos = $false
$script:seriesCards = @{}
$script:seriesBadges = @{}
$script:worldCards = @{}
$script:worldBadges = @{}
$script:worldSeries = @{}
$script:pickerItems = @()

function New-CardBadge {
    $bc = [System.Windows.Media.BrushConverter]::new()
    $badge = New-Object System.Windows.Controls.Border
    $badge.Background = $bc.ConvertFromString('#183E46')
    $badge.BorderBrush = $bc.ConvertFromString('#54DED4')
    $badge.BorderThickness = [System.Windows.Thickness]::new(1)
    $badge.CornerRadius = [System.Windows.CornerRadius]::new(4)
    $badge.Padding = [System.Windows.Thickness]::new(5, 1, 5, 1)
    $badge.HorizontalAlignment = [System.Windows.HorizontalAlignment]::Right
    [System.Windows.Controls.DockPanel]::SetDock($badge, [System.Windows.Controls.Dock]::Right)
    $bTxt = New-Object System.Windows.Controls.TextBlock
    $bTxt.Text = 'ACTIVO'
    $bTxt.FontSize = 9
    $bTxt.FontWeight = [System.Windows.FontWeights]::Bold
    $bTxt.Foreground = $bc.ConvertFromString('#54DED4')
    $badge.Child = $bTxt
    return $badge
}

function New-CardThumb([string]$thumbPath, [int]$width = 108, [int]$height = 68) {
    $imgWrap = New-Object System.Windows.Controls.Border
    $imgWrap.CornerRadius = [System.Windows.CornerRadius]::new(5)
    $imgWrap.Height = $height
    if ($width -gt 0) { $imgWrap.Width = $width }
    $imgWrap.ClipToBounds = $true
    $imgWrap.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#060916')
    $thumb = New-Object System.Windows.Controls.Image
    $thumb.Stretch = [System.Windows.Media.Stretch]::UniformToFill
    [System.Windows.Media.RenderOptions]::SetBitmapScalingMode($thumb, [System.Windows.Media.BitmapScalingMode]::NearestNeighbor)
    if ($thumbPath) { $thumb.Source = Cargar-Bitmap $thumbPath }
    $imgWrap.Child = $thumb
    return $imgWrap
}

function Attach-CardHover($bd) {
    $bd.Add_MouseEnter({
        param($s, $e)
        if (-not $s.IsHitTestVisible) { return }
        $bc = [System.Windows.Media.BrushConverter]::new()
        $s.Opacity = 1.0
        $s.BorderBrush = $bc.ConvertFromString('#7CF6EE')
    })
    $bd.Add_MouseLeave({
        param($s, $e)
        Actualiza-Vista
    })
}

# Paso 1: Construir tarjetas visuales por Serie
foreach ($sName in $seriesList) {
    $sTemas = $seriesByName[$sName]
    $repTema = $sTemas | Where-Object { $_.id -eq $script:selectedTema } | Select-Object -First 1
    if (-not $repTema) { $repTema = $sTemas[0] }

    $bdS = New-Object System.Windows.Controls.Border
    $bdS.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#0E1730')
    $bdS.BorderThickness = [System.Windows.Thickness]::new(1.5)
    $bdS.CornerRadius = [System.Windows.CornerRadius]::new(10)
    $bdS.Padding = [System.Windows.Thickness]::new(11)
    $bdS.Margin = [System.Windows.Thickness]::new(0, 0, 0, 10)
    $bdS.Cursor = [System.Windows.Input.Cursors]::Hand

    $gS = New-Object System.Windows.Controls.Grid
    $c1 = New-Object System.Windows.Controls.ColumnDefinition; $c1.Width = [System.Windows.GridLength]::new(142)
    $c2 = New-Object System.Windows.Controls.ColumnDefinition; $c2.Width = [System.Windows.GridLength]::new(12)
    $c3 = New-Object System.Windows.Controls.ColumnDefinition; $c3.Width = [System.Windows.GridLength]::new(1, [System.Windows.GridUnitType]::Star)
    $null = $gS.ColumnDefinitions.Add($c1); $null = $gS.ColumnDefinitions.Add($c2); $null = $gS.ColumnDefinitions.Add($c3)

    $thumbPath = Resolver-Preview $repTema.id 'dorado' 'principal'
    if (-not $thumbPath) { $thumbPath = Resolver-Preview $repTema.id 'noche' 'principal' }
    $imgWrap = New-CardThumb $thumbPath 142 88
    [System.Windows.Controls.Grid]::SetColumn($imgWrap, 0)
    $null = $gS.Children.Add($imgWrap)

    $info = New-Object System.Windows.Controls.StackPanel
    $info.VerticalAlignment = [System.Windows.VerticalAlignment]::Center
    $topRow = New-Object System.Windows.Controls.DockPanel
    $lblTitle = New-Object System.Windows.Controls.TextBlock
    $lblTitle.Text = $sName
    $lblTitle.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#F3EAD6')
    $lblTitle.FontSize = 15
    $lblTitle.FontWeight = [System.Windows.FontWeights]::Bold
    $null = $topRow.Children.Add($lblTitle)

    $badgeS = New-CardBadge
    $null = $topRow.Children.Add($badgeS)

    $lblSub = New-Object System.Windows.Controls.TextBlock
    if ($sTemas.Count -gt 1) {
        $titulos = ($sTemas | ForEach-Object { $_.titulo }) -join ' · '
        $lblSub.Text = "$($sTemas.Count) escenarios: $titulos"
    } else {
        $lblSub.Text = "Escenario único: $($sTemas[0].titulo)"
    }
    $lblSub.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#A6B9D6')
    $lblSub.FontSize = 12
    $lblSub.Margin = [System.Windows.Thickness]::new(0, 5, 0, 4)
    $lblSub.TextTrimming = [System.Windows.TextTrimming]::CharacterEllipsis

    $lblHint = New-Object System.Windows.Controls.TextBlock
    $lblHint.Text = if ($sTemas.Count -gt 1) { 'Explorar los mundos de esta serie →' } else { 'Elegir escenas de pantallas y bloqueo →' }
    $lblHint.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#E6B45A')
    $lblHint.FontSize = 11
    $lblHint.FontWeight = [System.Windows.FontWeights]::SemiBold

    $null = $info.Children.Add($topRow)
    $null = $info.Children.Add($lblSub)
    $null = $info.Children.Add($lblHint)
    [System.Windows.Controls.Grid]::SetColumn($info, 2)
    $null = $gS.Children.Add($info)

    $bdS.Child = $gS
    $bdS.Tag = $sName
    $bdS.Add_MouseLeftButtonUp({
        param($sender, $e)
        $sNameClick = [string]$sender.Tag
        $script:selectedSerie = $sNameClick
        $listaS = $seriesByName[$sNameClick]
        if ($listaS.Count -gt 1) {
            if (-not ($listaS | Where-Object { $_.id -eq $script:selectedTema })) {
                $script:selectedTema = $listaS[0].id
            }
            Cambia-VistaMundo 'temas'
        } else {
            $script:selectedTema = $listaS[0].id
            Cambia-VistaMundo 'imagenes'
        }
        Actualiza-Vista
    })
    Attach-CardHover $bdS
    $script:seriesCards[$sName] = $bdS
    $script:seriesBadges[$sName] = $badgeS
    $null = $el.ListaSeries.Children.Add($bdS)
}

# Paso 2: Construir tarjetas visuales de mundos (filtradas por Serie)
foreach ($t in $temas) {
    $tid = $t.id
    $bd = New-Object System.Windows.Controls.Border
    $bd.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#0E1730')
    $bd.BorderThickness = [System.Windows.Thickness]::new(1.5)
    $bd.CornerRadius = [System.Windows.CornerRadius]::new(10)
    $bd.Padding = [System.Windows.Thickness]::new(11)
    $bd.Margin = [System.Windows.Thickness]::new(0, 0, 0, 10)
    $bd.Cursor = [System.Windows.Input.Cursors]::Hand

    $g = New-Object System.Windows.Controls.Grid
    $c1 = New-Object System.Windows.Controls.ColumnDefinition; $c1.Width = [System.Windows.GridLength]::new(142)
    $c2 = New-Object System.Windows.Controls.ColumnDefinition; $c2.Width = [System.Windows.GridLength]::new(12)
    $c3 = New-Object System.Windows.Controls.ColumnDefinition; $c3.Width = [System.Windows.GridLength]::new(1, [System.Windows.GridUnitType]::Star)
    $null = $g.ColumnDefinitions.Add($c1); $null = $g.ColumnDefinitions.Add($c2); $null = $g.ColumnDefinitions.Add($c3)

    $thumbPath = Resolver-Preview $tid 'dorado' 'principal'
    if (-not $thumbPath) { $thumbPath = Resolver-Preview $tid 'noche' 'principal' }
    $imgWrap = New-CardThumb $thumbPath 142 88
    [System.Windows.Controls.Grid]::SetColumn($imgWrap, 0)
    $null = $g.Children.Add($imgWrap)

    $info = New-Object System.Windows.Controls.StackPanel
    $info.VerticalAlignment = [System.Windows.VerticalAlignment]::Center
    $topRow = New-Object System.Windows.Controls.DockPanel
    $lblTitle = New-Object System.Windows.Controls.TextBlock
    $lblTitle.Text = $t.titulo
    $lblTitle.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#F3EAD6')
    $lblTitle.FontSize = 14.5
    $lblTitle.FontWeight = [System.Windows.FontWeights]::Bold
    $null = $topRow.Children.Add($lblTitle)

    $badge = New-CardBadge
    $null = $topRow.Children.Add($badge)

    $lblM1 = New-Object System.Windows.Controls.TextBlock
    $lblM1.Text = "1 · $($t.m1)"
    $lblM1.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#A6B9D6')
    $lblM1.FontSize = 11.5
    $lblM1.Margin = [System.Windows.Thickness]::new(0, 4, 0, 2)
    $lblM1.TextTrimming = [System.Windows.TextTrimming]::CharacterEllipsis

    $lblM2 = New-Object System.Windows.Controls.TextBlock
    $lblM2.Text = "2 · $($t.m2)"
    $lblM2.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#E6B45A')
    $lblM2.FontSize = 11.5
    $lblM2.Margin = [System.Windows.Thickness]::new(0, 0, 0, 2)
    $lblM2.TextTrimming = [System.Windows.TextTrimming]::CharacterEllipsis

    $lblM3 = New-Object System.Windows.Controls.TextBlock
    $lblM3.Text = "3 · Bloqueo: $($t.m3)"
    $lblM3.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#88C8FF')
    $lblM3.FontSize = 11
    $lblM3.TextTrimming = [System.Windows.TextTrimming]::CharacterEllipsis

    $null = $info.Children.Add($topRow)
    $null = $info.Children.Add($lblM1)
    $null = $info.Children.Add($lblM2)
    $null = $info.Children.Add($lblM3)
    [System.Windows.Controls.Grid]::SetColumn($info, 2)
    $null = $g.Children.Add($info)

    $bd.Child = $g
    $bd.Tag = $tid
    $bd.Add_MouseLeftButtonUp({
        param($sender, $e)
        $tidClick = [string]$sender.Tag
        $script:selectedTema = $tidClick
        $script:selectedSerie = $script:worldSeries[$tidClick]
        Cambia-VistaMundo 'imagenes'
        Actualiza-Vista
    })
    Attach-CardHover $bd
    $script:worldCards[$tid] = $bd
    $script:worldBadges[$tid] = $badge
    $script:worldSeries[$tid] = $t.serie
    $null = $el.ListaTarjetasMundos.Children.Add($bd)
}

# Paso 3: Construir selector visual de las 3 imágenes para Monitor Principal, Secundario y Bloqueo
function Build-PickerRow($grid, [string]$rol) {
    $bc = [System.Windows.Media.BrushConverter]::new()
    foreach ($esc in @('principal', 'secundaria', 'bloqueo')) {
        $card = New-Object System.Windows.Controls.Border
        $card.Background = $bc.ConvertFromString('#091024')
        $card.BorderBrush = $bc.ConvertFromString('#24365C')
        $card.BorderThickness = [System.Windows.Thickness]::new(1.5)
        $card.CornerRadius = [System.Windows.CornerRadius]::new(8)
        $card.Padding = [System.Windows.Thickness]::new(5)
        $card.Margin = [System.Windows.Thickness]::new(4)
        $card.Cursor = [System.Windows.Input.Cursors]::Hand

        $sp = New-Object System.Windows.Controls.StackPanel
        $imgWrap = New-Object System.Windows.Controls.Border
        $imgWrap.CornerRadius = [System.Windows.CornerRadius]::new(5)
        $imgWrap.Height = 68
        $imgWrap.ClipToBounds = $true
        $imgWrap.Background = $bc.ConvertFromString('#050814')

        $imgGrid = New-Object System.Windows.Controls.Grid
        $img = New-Object System.Windows.Controls.Image
        $img.Stretch = [System.Windows.Media.Stretch]::UniformToFill
        [System.Windows.Media.RenderOptions]::SetBitmapScalingMode($img, [System.Windows.Media.BitmapScalingMode]::NearestNeighbor)
        $null = $imgGrid.Children.Add($img)

        $checkBadge = New-Object System.Windows.Controls.Border
        $checkBadge.Background = $bc.ConvertFromString('#54DED4')
        $checkBadge.CornerRadius = [System.Windows.CornerRadius]::new(9)
        $checkBadge.Width = 18
        $checkBadge.Height = 18
        $checkBadge.HorizontalAlignment = [System.Windows.HorizontalAlignment]::Right
        $checkBadge.VerticalAlignment = [System.Windows.VerticalAlignment]::Top
        $checkBadge.Margin = [System.Windows.Thickness]::new(0, 4, 4, 0)
        $checkBadge.Visibility = 'Collapsed'
        $chkTxt = New-Object System.Windows.Controls.TextBlock
        $chkTxt.Text = '✓'
        $chkTxt.Foreground = $bc.ConvertFromString('#061217')
        $chkTxt.FontSize = 10
        $chkTxt.FontWeight = [System.Windows.FontWeights]::Bold
        $chkTxt.HorizontalAlignment = [System.Windows.HorizontalAlignment]::Center
        $chkTxt.VerticalAlignment = [System.Windows.VerticalAlignment]::Center
        $checkBadge.Child = $chkTxt
        $null = $imgGrid.Children.Add($checkBadge)

        $imgWrap.Child = $imgGrid

        $lbl = New-Object System.Windows.Controls.TextBlock
        $lbl.Foreground = $bc.ConvertFromString('#DCE6F5')
        $lbl.FontSize = 11
        $lbl.FontWeight = [System.Windows.FontWeights]::SemiBold
        $lbl.Margin = [System.Windows.Thickness]::new(2, 5, 2, 1)
        $lbl.TextTrimming = [System.Windows.TextTrimming]::CharacterEllipsis
        $lbl.TextAlignment = [System.Windows.TextAlignment]::Center

        $null = $sp.Children.Add($imgWrap)
        $null = $sp.Children.Add($lbl)
        $card.Child = $sp
        $card.Tag = @{ rol = $rol; escena = $esc }
        $card.Add_MouseLeftButtonUp({
            param($sender, $e)
            $info = $sender.Tag
            if ($info.rol -eq 'bloqueo') { $el.ChkBloqueo.IsChecked = $true }
            $cmbMap = @{
                'principal'  = $el.CmbFondoPrincipal
                'secundaria' = $el.CmbFondoSecundaria
                'bloqueo'    = $el.CmbFondoBloqueo
            }
            Set-ComboByTag $cmbMap[$info.rol] $info.escena 0
            Actualiza-Vista
        })
        Attach-CardHover $card
        $null = $grid.Children.Add($card)
        $script:pickerItems += @{ rol = $rol; escena = $esc; card = $card; img = $img; lbl = $lbl; chk = $checkBadge }
    }
}

Build-PickerRow $el.GridPickerM1 'principal'
Build-PickerRow $el.GridPickerM2 'secundaria'
Build-PickerRow $el.GridPickerBloq 'bloqueo'

# Inicializar valores desde config.json
$el.RbMon1.IsChecked = ($cfg.monitores -le 1)
$el.RbMon2.IsChecked = ($cfg.monitores -ge 2)
$el.ChkHudMaster.IsChecked = [bool]$cfg.hud
$el.ChkTiempo.IsChecked = [bool]$cfg.stats.tiempo
$el.ChkSistema.IsChecked = [bool]$cfg.stats.sistema
$el.ChkRed.IsChecked = [bool]$cfg.stats.red
$el.ChkDev.IsChecked = [bool]$cfg.stats.dev
$el.ChkGrimorio.IsChecked = [bool]$cfg.stats.grimorio
$el.SldHora.Value = [double]$cfg.horaFija
$el.ChkTrayCerrar.IsChecked = [bool]$cfg.trayAlCerrar
$el.ChkAutoInicio.IsChecked = AutoInicio-Activo

for ($i = 0; $i -lt $el.CmbModo.Items.Count; $i++) {
    if ($el.CmbModo.Items[$i].Tag -eq $cfg.modo) { $el.CmbModo.SelectedIndex = $i; break }
}
if ($el.CmbModo.SelectedIndex -lt 0) { $el.CmbModo.SelectedIndex = 0 }

function Set-ComboByTag($cmb, [string]$tag, [int]$defIdx = 0) {
    $found = -1
    for ($i = 0; $i -lt $cmb.Items.Count; $i++) {
        if ($cmb.Items[$i].Tag -eq $tag) { $found = $i; break }
    }
    $cmb.SelectedIndex = if ($found -ge 0) { $found } else { $defIdx }
}

$el.ChkBloqueo.IsChecked = [bool]$cfg.usarBloqueo
$el.ChkBloqueoMenu.IsChecked = [bool]$cfg.usarBloqueo
Set-ComboByTag $el.CmbFondoPrincipal ([string]$cfg.fondoPrincipal) 0
Set-ComboByTag $el.CmbFondoSecundaria ([string]$cfg.fondoSecundario) 1
Set-ComboByTag $el.CmbFondoBloqueo ([string]$cfg.fondoBloqueo) 2

# Diagnóstico sencillo
$pyPath = Resolver-Python
$pyMsg = if ($pyPath) { "✅ Animación solar automática y vista web listas (Python detectado)." } else { "✅ Animación solar nativa activa (no requiere Python)." }
$deskLnk = Join-Path ([Environment]::GetFolderPath('Desktop')) 'PixelZen Worlds.lnk'
$lnkMsg = if (Test-Path $deskLnk) { "✅ Acceso directo ya creado en tu Escritorio." } else { "ℹ️ Aún no tienes acceso directo en el Escritorio (puedes crearlo arriba)." }
$el.TxtDiag.Text = "ℹ️ Versión instalada: v$VersionActual`n✅ $($screens.Count) pantalla(s) detectadas.`n✅ $($temas.Count) mundos con continuación de historia listos.`n$pyMsg`n$lnkMsg"

function Lee-FormConfig {
    $fp = if ($el.CmbFondoPrincipal.SelectedItem) { [string]$el.CmbFondoPrincipal.SelectedItem.Tag } else { 'principal' }
    $fs = if ($el.CmbFondoSecundaria.SelectedItem) { [string]$el.CmbFondoSecundaria.SelectedItem.Tag } else { 'secundaria' }
    $fb = if ($el.CmbFondoBloqueo.SelectedItem) { [string]$el.CmbFondoBloqueo.SelectedItem.Tag } else { 'bloqueo' }
    return [ordered]@{
        tema = $script:selectedTema
        monitores = if ($el.RbMon2.IsChecked) { 2 } else { 1 }
        modo = $el.CmbModo.SelectedItem.Tag
        horaFija = [double]$el.SldHora.Value
        fps = 8
        hud = [bool]$el.ChkHudMaster.IsChecked
        trayAlCerrar = [bool]$el.ChkTrayCerrar.IsChecked
        usarBloqueo = [bool]$el.ChkBloqueo.IsChecked
        fondoPrincipal = $fp
        fondoSecundario = $fs
        fondoBloqueo = $fb
        stats = [ordered]@{
            tiempo = [bool]$el.ChkTiempo.IsChecked
            sistema = [bool]$el.ChkSistema.IsChecked
            red = [bool]$el.ChkRed.IsChecked
            dev = [bool]$el.ChkDev.IsChecked
            grimorio = [bool]$el.ChkGrimorio.IsChecked
        }
    }
}

function Cambia-VistaMundo([string]$vista) {
    $script:mundoVista = $vista
    $el.PanelSeries.Visibility       = if ($vista -eq 'series')   { 'Visible' } else { 'Collapsed' }
    $el.PanelTemasSerie.Visibility   = if ($vista -eq 'temas')    { 'Visible' } else { 'Collapsed' }
    $el.PanelImagenesTema.Visibility = if ($vista -eq 'imagenes') { 'Visible' } else { 'Collapsed' }

    if ($vista -eq 'temas') {
        $el.TxtSerieTitulo.Text = $script:selectedSerie
        foreach ($k in $script:worldCards.Keys) {
            $script:worldCards[$k].Visibility = if ($script:worldSeries[$k] -eq $script:selectedSerie) { 'Visible' } else { 'Collapsed' }
        }
    } elseif ($vista -eq 'imagenes') {
        $tmeta = $temas | Where-Object { $_.id -eq $script:selectedTema } | Select-Object -First 1
        if ($tmeta) { $el.TxtTemaImagenesTitulo.Text = "$($tmeta.serie) · $($tmeta.titulo)" }
    }
    $el.PageMundos.ScrollToHome()
}

function Cambia-Pestana($cual) {
    $pages = @{ 'mundos' = $el.PageMundos; 'pantallas' = $el.PagePantallas; 'hud' = $el.PageHud; 'sistema' = $el.PageSistema }
    $navs = @{ 'mundos' = $el.NavMundos; 'pantallas' = $el.NavPantallas; 'hud' = $el.NavHud; 'sistema' = $el.NavSistema }
    $bc = [System.Windows.Media.BrushConverter]::new()
    foreach ($k in $pages.Keys) {
        if ($k -eq $cual) {
            $pages[$k].Visibility = 'Visible'
            $navs[$k].Background = $bc.ConvertFromString('#152244')
            $navs[$k].BorderBrush = $bc.ConvertFromString('#54DED4')
            $navs[$k].Foreground = $bc.ConvertFromString('#54DED4')
        } else {
            $pages[$k].Visibility = 'Collapsed'
            $navs[$k].Background = [System.Windows.Media.Brushes]::Transparent
            $navs[$k].BorderBrush = [System.Windows.Media.Brushes]::Transparent
            $navs[$k].Foreground = $bc.ConvertFromString('#A8B8CF')
        }
    }
}

function Aplicar-EscenaTodas([string]$escena) {
    $script:syncingCombos = $true
    $el.ChkBloqueo.IsChecked = $true
    $el.ChkBloqueoMenu.IsChecked = $true
    Set-ComboByTag $el.CmbFondoPrincipal $escena 0
    Set-ComboByTag $el.CmbFondoSecundaria $escena 0
    Set-ComboByTag $el.CmbFondoBloqueo $escena 0
    $script:syncingCombos = $false
    Actualiza-Vista
}

function Actualiza-Vista {
    $bc = [System.Windows.Media.BrushConverter]::new()
    $tid = $script:selectedTema
    $tmeta = $temas | Where-Object { $_.id -eq $tid } | Select-Object -First 1
    $activeSerie = if ($tmeta) { $tmeta.serie } else { $script:selectedSerie }

    # Resaltar serie activa
    foreach ($sK in $script:seriesCards.Keys) {
        if ($sK -eq $activeSerie) {
            $script:seriesCards[$sK].BorderBrush = $bc.ConvertFromString('#54DED4')
            $script:seriesCards[$sK].Background = $bc.ConvertFromString('#152346')
            $script:seriesBadges[$sK].Visibility = 'Visible'
        } else {
            $script:seriesCards[$sK].BorderBrush = $bc.ConvertFromString('#263759')
            $script:seriesCards[$sK].Background = $bc.ConvertFromString('#101832')
            $script:seriesBadges[$sK].Visibility = 'Collapsed'
        }
    }

    # Resaltar tarjeta de mundo elegida
    foreach ($k in $script:worldCards.Keys) {
        if ($k -eq $tid) {
            $script:worldCards[$k].BorderBrush = $bc.ConvertFromString('#54DED4')
            $script:worldCards[$k].Background = $bc.ConvertFromString('#152346')
            $script:worldBadges[$k].Visibility = 'Visible'
        } else {
            $script:worldCards[$k].BorderBrush = $bc.ConvertFromString('#263759')
            $script:worldCards[$k].Background = $bc.ConvertFromString('#101832')
            $script:worldBadges[$k].Visibility = 'Collapsed'
        }
    }

    # Resaltar tarjetas de 1 o 2 monitores
    $dosMon = [bool]$el.RbMon2.IsChecked
    $el.CardMon1.BorderBrush = $bc.ConvertFromString($(if (-not $dosMon) { '#54DED4' } else { '#2A3C64' }))
    $el.CardMon2.BorderBrush = $bc.ConvertFromString($(if ($dosMon) { '#54DED4' } else { '#2A3C64' }))

    $usarBloq = [bool]$el.ChkBloqueo.IsChecked
    # Nombres de escenas del mundo en los selectores por pantalla
    $script:syncingCombos = $true
    $el.ChkBloqueoMenu.IsChecked = $usarBloq
    foreach ($cmb in @($el.CmbFondoPrincipal, $el.CmbFondoSecundaria, $el.CmbFondoBloqueo)) {
        foreach ($item in $cmb.Items) {
            switch ([string]$item.Tag) {
                'principal'  { $item.Content = "Principal · $($tmeta.m1)" }
                'secundaria' { $item.Content = "Secundaria · $($tmeta.m2)" }
                'bloqueo'    { $item.Content = "Bloqueo · $($tmeta.m3)" }
            }
        }
    }
    $script:syncingCombos = $false

    $fpTag = if ($el.CmbFondoPrincipal.SelectedItem) { [string]$el.CmbFondoPrincipal.SelectedItem.Tag } else { 'principal' }
    $fsTag = if ($el.CmbFondoSecundaria.SelectedItem) { [string]$el.CmbFondoSecundaria.SelectedItem.Tag } else { 'secundaria' }
    $fbTag = if ($el.CmbFondoBloqueo.SelectedItem) { [string]$el.CmbFondoBloqueo.SelectedItem.Tag } else { 'bloqueo' }
    $el.PanelComboSec.Visibility = if ($dosMon) { 'Visible' } else { 'Collapsed' }
    $el.PanelPickerM2.Visibility = if ($dosMon) { 'Visible' } else { 'Collapsed' }
    $el.PanelComboBloq.Visibility = if ($usarBloq) { 'Visible' } else { 'Collapsed' }
    $el.GridPickerBloq.Opacity = if ($usarBloq) { 1.0 } else { 0.45 }

    function Cortar-SeriePrefijo([string]$txt) {
        if (-not $txt) { return '' }
        if ($txt -match '^[^·]+·\s*(.+)$') { return $Matches[1].Trim() }
        return $txt.Trim()
    }
    function Nombre-EscenaVariante([string]$tag) {
        switch ($tag) {
            'secundaria' { return (Cortar-SeriePrefijo $tmeta.m2) }
            'bloqueo'    { return (Cortar-SeriePrefijo $tmeta.m3) }
            default      { return (Cortar-SeriePrefijo $tmeta.m1) }
        }
    }

    # Actualizar encabezados e imágenes del Paso 3 (Selector visual por pantalla)
    $el.TxtTemaImagenesTitulo.Text = "$($tmeta.serie) · $($tmeta.titulo)"
    $el.BtnRepetirPrincipal.Content  = "✨ Todas: $(Nombre-EscenaVariante 'principal')"
    $el.BtnRepetirSecundaria.Content = "✨ Todas: $(Nombre-EscenaVariante 'secundaria')"
    $el.BtnRepetirBloqueo.Content    = "✨ Todas: $(Nombre-EscenaVariante 'bloqueo')"

    $prevCache = @{
        'principal'  = Cargar-Bitmap (Resolver-Preview $tid $script:previewFase 'principal')
        'secundaria' = Cargar-Bitmap (Resolver-Preview $tid $script:previewFase 'secundaria')
        'bloqueo'    = Cargar-Bitmap (Resolver-Preview $tid $script:previewFase 'bloqueo')
    }
    $selMap = @{ 'principal' = $fpTag; 'secundaria' = $fsTag; 'bloqueo' = $fbTag }
    foreach ($pi in $script:pickerItems) {
        $pi.img.Source = $prevCache[$pi.escena]
        $pi.lbl.Text = Nombre-EscenaVariante $pi.escena
        $esSel = ($selMap[$pi.rol] -eq $pi.escena) -and ($pi.rol -ne 'bloqueo' -or $usarBloq)
        if ($esSel) {
            $pi.card.BorderBrush = $bc.ConvertFromString('#54DED4')
            $pi.card.Background  = $bc.ConvertFromString('#15284F')
            $pi.lbl.Foreground   = $bc.ConvertFromString('#7CF6EE')
            $pi.chk.Visibility   = 'Visible'
        } else {
            $pi.card.BorderBrush = $bc.ConvertFromString('#24365C')
            $pi.card.Background  = $bc.ConvertFromString('#091024')
            $pi.lbl.Foreground   = $bc.ConvertFromString('#DCE6F5')
            $pi.chk.Visibility   = 'Collapsed'
        }
    }

    # Imágenes de vista previa M1, M2 y Bloqueo
    $el.ImgPrev1.Source = $prevCache[$fpTag]
    $el.ImgPrev2.Source = $prevCache[$fsTag]
    $el.ImgPrevBloqueo.Source = $prevCache[$fbTag]
    $el.TxtPrev1Title.Text = "PANTALLA 1 · $(Nombre-EscenaVariante $fpTag)"
    $el.TxtPrev2Title.Text = "PANTALLA 2 · $(Nombre-EscenaVariante $fsTag)"
    $el.PanelPrev2.Visibility = if ($dosMon) { 'Visible' } else { 'Collapsed' }
    $el.TxtM2Sub.Text = "En tu 2.º monitor: $(Nombre-EscenaVariante $fsTag)"
    $el.TxtPrevBloqTitle.Text = "🔒 BLOQUEO · $(Nombre-EscenaVariante $fbTag)"
    $el.PanelPrevBloqueo.Visibility = if ($usarBloq) { 'Visible' } else { 'Collapsed' }
    $el.TxtBloqSub.Text = "Bloqueo de Windows: $(Nombre-EscenaVariante $fbTag)"

    # Modo horario
    $modo = $el.CmbModo.SelectedItem.Tag
    $el.PanelHora.Visibility = if ($modo -eq 'fija') { 'Visible' } else { 'Collapsed' }
    $hv = [double]$el.SldHora.Value
    $hh = [math]::Floor($hv); $mm = [math]::Round(($hv - $hh) * 60)
    $el.TxtHoraVal.Text = "{0:00}:{1:00}" -f [int]$hh, [int]$mm

    # Simulación en vivo de cajitas HUD sobre Monitor 1
    $hudOn = [bool]$el.ChkHudMaster.IsChecked
    $el.MockHudPanel.Visibility = if ($hudOn) { 'Visible' } else { 'Collapsed' }
    $el.TxtMockMundo.Text = $tmeta.titulo
    $el.MockTiempo.Visibility = if ($el.ChkTiempo.IsChecked) { 'Visible' } else { 'Collapsed' }
    $el.MockSistema.Visibility = if ($el.ChkSistema.IsChecked) { 'Visible' } else { 'Collapsed' }
    $el.MockRed.Visibility = if ($el.ChkRed.IsChecked) { 'Visible' } else { 'Collapsed' }
    $el.MockDev.Visibility = if ($el.ChkDev.IsChecked) { 'Visible' } else { 'Collapsed' }
    $el.MockGrimorio.Visibility = if ($el.ChkGrimorio.IsChecked) { 'Visible' } else { 'Collapsed' }

    # Habilitar/atenuar checkboxes individuales según interruptor maestro
    foreach ($cb in $el.ChkTiempo, $el.ChkSistema, $el.ChkRed, $el.ChkDev, $el.ChkGrimorio) {
        $cb.IsEnabled = $hudOn
    }

    # Botón toggle HUD actual
    $el.BtnToggleHudNow.Content = if (Hay-HudActivo) { '👁️ Ocultar cajitas ahora' } else { '👁️ Mostrar cajitas ahora' }

    # Estado motor nativo en cabecera
    if (Motor-NativoActivo) {
        $el.BadgeMotor.Background = $bc.ConvertFromString('#102924')
        $el.BadgeMotor.BorderBrush = $bc.ConvertFromString('#2E8B6B')
        $el.TxtMotorBadge.Text = '● MOTOR NATIVO ACTIVO'
        $el.TxtMotorBadge.Foreground = $bc.ConvertFromString('#72E6AE')
    } else {
        $el.BadgeMotor.Background = $bc.ConvertFromString('#261E12')
        $el.BadgeMotor.BorderBrush = $bc.ConvertFromString('#7D6230')
        $el.TxtMotorBadge.Text = '● EN ESPERA'
        $el.TxtMotorBadge.Foreground = $bc.ConvertFromString('#E6B45A')
    }

    # Botones de vista previa fase (segmentados)
    foreach ($pair in @(@($el.BtnPrevDia,'dia'), @($el.BtnPrevDor,'dorado'), @($el.BtnPrevNoc,'noche'))) {
        $activoF = ($script:previewFase -eq $pair[1])
        $pair[0].Background  = $bc.ConvertFromString($(if ($activoF) { '#163549' } else { 'Transparent' }))
        $pair[0].BorderBrush = $bc.ConvertFromString($(if ($activoF) { '#54DED4' } else { 'Transparent' }))
        $pair[0].Foreground  = $bc.ConvertFromString($(if ($activoF) { '#7CF6EE' } else { '#9AB0CE' }))
    }

    # Resumen lateral estructurado
    $modoTxt = switch ($modo) { 'real' { 'Hora real' } 'demo' { 'Pase rápido 90s' } 'fija' { "Fija $($el.TxtHoraVal.Text)" } default { 'Suave 90m' } }
    $nStats = @($el.ChkTiempo, $el.ChkSistema, $el.ChkRed, $el.ChkDev, $el.ChkGrimorio | Where-Object { $_.IsChecked }).Count
    $hudTxt = if ($hudOn) { "$nStats activas" } else { 'Desactivado' }
    $bloqTxt = if ($usarBloq) { Nombre-EscenaVariante $fbTag } else { 'Desactivado' }
    $el.TxtResumen.Text = "Serie: $($tmeta.serie)`nMundo: $($tmeta.titulo)`nMonitores: $(if ($dosMon) { '2 pantallas' } else { '1 pantalla' })`nBloqueo: $bloqTxt`nLuz: $modoTxt`nCajitas HUD: $hudTxt"
}

# Eventos de navegación y controles
$el.NavMundos.Add_Click({ Cambia-Pestana 'mundos'; Cambia-VistaMundo 'series' })
$el.BtnVolverASeries.Add_Click({ Cambia-VistaMundo 'series' })
$el.BtnVolverDeImagenes.Add_Click({
    $listaS = $seriesByName[$script:selectedSerie]
    if ($listaS -and $listaS.Count -gt 1) { Cambia-VistaMundo 'temas' } else { Cambia-VistaMundo 'series' }
})
$el.BtnPresetClasico.Add_Click({
    $script:syncingCombos = $true
    $el.ChkBloqueo.IsChecked = $true
    $el.ChkBloqueoMenu.IsChecked = $true
    Set-ComboByTag $el.CmbFondoPrincipal 'principal' 0
    Set-ComboByTag $el.CmbFondoSecundaria 'secundaria' 1
    Set-ComboByTag $el.CmbFondoBloqueo 'bloqueo' 2
    $script:syncingCombos = $false
    Actualiza-Vista
})
$el.BtnRepetirPrincipal.Add_Click({ Aplicar-EscenaTodas 'principal' })
$el.BtnRepetirSecundaria.Add_Click({ Aplicar-EscenaTodas 'secundaria' })
$el.BtnRepetirBloqueo.Add_Click({ Aplicar-EscenaTodas 'bloqueo' })
$el.BtnIrAPantallasLuz.Add_Click({ Cambia-Pestana 'pantallas' })

$el.NavPantallas.Add_Click({ Cambia-Pestana 'pantallas' })
$el.NavHud.Add_Click({ Cambia-Pestana 'hud' })
$el.NavSistema.Add_Click({ Cambia-Pestana 'sistema' })

$el.CardMon1.Add_MouseLeftButtonUp({ $el.RbMon1.IsChecked = $true; Actualiza-Vista })
$el.CardMon2.Add_MouseLeftButtonUp({ $el.RbMon2.IsChecked = $true; Actualiza-Vista })
$el.RbMon1.Add_Checked({ Actualiza-Vista })
$el.RbMon2.Add_Checked({ Actualiza-Vista })
foreach ($cmbV in $el.CmbFondoPrincipal, $el.CmbFondoSecundaria, $el.CmbFondoBloqueo) {
    $cmbV.Add_SelectionChanged({ if (-not $script:syncingCombos) { Actualiza-Vista } })
}
$el.ChkBloqueo.Add_Checked({ if (-not $script:syncingCombos) { Actualiza-Vista } })
$el.ChkBloqueo.Add_Unchecked({ if (-not $script:syncingCombos) { Actualiza-Vista } })
$el.ChkBloqueoMenu.Add_Checked({
    if (-not $script:syncingCombos) {
        $script:syncingCombos = $true; $el.ChkBloqueo.IsChecked = $true; $script:syncingCombos = $false
        Actualiza-Vista
    }
})
$el.ChkBloqueoMenu.Add_Unchecked({
    if (-not $script:syncingCombos) {
        $script:syncingCombos = $true; $el.ChkBloqueo.IsChecked = $false; $script:syncingCombos = $false
        Actualiza-Vista
    }
})
$el.CmbModo.Add_SelectionChanged({
    if ($el.CmbModo.SelectedItem.Tag -eq 'fija') {
        $script:previewFase = Detectar-Fase 'fija' $el.SldHora.Value
    }
    Actualiza-Vista
})
$el.SldHora.Add_ValueChanged({
    $script:previewFase = Detectar-Fase 'fija' $el.SldHora.Value
    Actualiza-Vista
})
$el.BtnFijarDia.Add_Click({ $el.SldHora.Value = 13.0; $script:previewFase = 'dia'; Actualiza-Vista })
$el.BtnFijarDor.Add_Click({ $el.SldHora.Value = 18.5; $script:previewFase = 'dorado'; Actualiza-Vista })
$el.BtnFijarNoc.Add_Click({ $el.SldHora.Value = 22.0; $script:previewFase = 'noche'; Actualiza-Vista })

$el.BtnPrevDia.Add_Click({ $script:previewFase = 'dia'; Actualiza-Vista })
$el.BtnPrevDor.Add_Click({ $script:previewFase = 'dorado'; Actualiza-Vista })
$el.BtnPrevNoc.Add_Click({ $script:previewFase = 'noche'; Actualiza-Vista })

foreach ($cb in $el.ChkHudMaster, $el.ChkTiempo, $el.ChkSistema, $el.ChkRed, $el.ChkDev, $el.ChkGrimorio) {
    $cb.Add_Checked({ Actualiza-Vista })
    $cb.Add_Unchecked({ Actualiza-Vista })
}
$el.BtnHudTodas.Add_Click({
    $el.ChkHudMaster.IsChecked = $true
    foreach ($cb in $el.ChkTiempo, $el.ChkSistema, $el.ChkRed, $el.ChkDev, $el.ChkGrimorio) { $cb.IsChecked = $true }
    Actualiza-Vista
})
$el.BtnHudMinimo.Add_Click({
    $el.ChkHudMaster.IsChecked = $true
    $el.ChkTiempo.IsChecked = $true; $el.ChkGrimorio.IsChecked = $true
    $el.ChkSistema.IsChecked = $false; $el.ChkRed.IsChecked = $false; $el.ChkDev.IsChecked = $false
    Actualiza-Vista
})
$el.BtnHudSoloReloj.Add_Click({
    $el.ChkHudMaster.IsChecked = $true
    $el.ChkTiempo.IsChecked = $true
    $el.ChkSistema.IsChecked = $false; $el.ChkRed.IsChecked = $false; $el.ChkDev.IsChecked = $false; $el.ChkGrimorio.IsChecked = $false
    Actualiza-Vista
})

$el.BtnAccesoDirecto.Add_Click({
    $rutaLnk = Crear-AccesoDirecto
    $el.TxtEstado.Text = "✅ Acceso directo creado en tu Escritorio: PixelZen Worlds.lnk"
})
$el.ChkAutoInicio.Add_Checked({ Set-AutoInicio $true; $el.TxtEstado.Text = "✅ PixelZen se aplicará automáticamente al iniciar Windows." })
$el.ChkAutoInicio.Add_Unchecked({ Set-AutoInicio $false; $el.TxtEstado.Text = "Auto-inicio con Windows desactivado." })
$el.BtnBuscarUpdate.Add_Click({
    $el.TxtEstado.Text = "🔄 Buscando actualizaciones en GitHub Releases..."
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/davidlpizano/pixelzen-worlds/releases/latest' -Headers @{ 'User-Agent' = 'PixelZenWorlds' } -TimeoutSec 10
        $remTag = ([string]$rel.tag_name).TrimStart('v', 'V')
        if ([version]$remTag -le [version]$VersionActual) {
            $el.TxtEstado.Text = "✅ Ya tienes la última versión (v$VersionActual)."
            return
        }
        $assetZip = $rel.assets | Where-Object { $_.name -eq 'PixelZenWorlds-Windows.zip' } | Select-Object -First 1
        $assetExe = $rel.assets | Where-Object { $_.name -eq 'PixelZenWorlds-Setup.exe' } | Select-Object -First 1
        $asset = if ($assetZip) { $assetZip } else { $assetExe }
        if (-not $asset) {
            $el.TxtEstado.Text = "✨ Nueva versión v$remTag disponible en GitHub Releases."
            Start-Process ([string]$rel.html_url)
            return
        }
        $resp = [System.Windows.MessageBox]::Show(
            "Hay una versión nueva disponible (v$remTag, actual v$VersionActual).`n¿Quieres descargarla e instalarla ahora? Tus ajustes se conservarán.",
            "Actualización · PixelZen Worlds",
            [System.Windows.MessageBoxButton]::YesNo,
            [System.Windows.MessageBoxImage]::Question
        )
        if ($resp -ne [System.Windows.MessageBoxResult]::Yes) {
            $el.TxtEstado.Text = "Actualización pospuesta (disponible v$remTag)."
            return
        }
        if ($assetZip) {
            $updDir = Join-Path $env:TEMP ('pz_upd_' + [Guid]::NewGuid().ToString('N'))
            New-Item -Path $updDir -ItemType Directory -Force | Out-Null
            $tmpZip = Join-Path $updDir 'PixelZenWorlds-Windows.zip'
            Invoke-WebRequest -Uri $assetZip.browser_download_url -OutFile $tmpZip -UseBasicParsing
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [System.IO.Compression.ZipFile]::ExtractToDirectory($tmpZip, $updDir)
            $instPs = Join-Path $updDir 'Instalar.ps1'
            Start-Process -FilePath 'powershell.exe' -ArgumentList "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$instPs`""
        } else {
            $tmpSetup = Join-Path $env:TEMP 'PixelZenWorlds-Setup.exe'
            Invoke-WebRequest -Uri $assetExe.browser_download_url -OutFile $tmpSetup -UseBasicParsing
            Start-Process -FilePath $tmpSetup
        }
        $script:realClose = $true
        $win.Close()
    } catch {
        $el.TxtEstado.Text = "⚠️ No se pudo consultar GitHub automáticamente. Abriendo página de Releases..."
        Start-Process 'https://github.com/davidlpizano/pixelzen-worlds/releases'
    }
})

$el.BtnRestaurar.Add_Click({
    $script:selectedTema = 'fittoa'
    $script:selectedSerie = 'Mushoku Tensei'
    $el.RbMon2.IsChecked = $true
    $el.ChkBloqueo.IsChecked = $true
    Set-ComboByTag $el.CmbFondoPrincipal 'principal' 0
    Set-ComboByTag $el.CmbFondoSecundaria 'secundaria' 1
    Set-ComboByTag $el.CmbFondoBloqueo 'bloqueo' 2
    $el.CmbModo.SelectedIndex = 0
    $el.ChkHudMaster.IsChecked = $true
    foreach ($cb in $el.ChkTiempo, $el.ChkSistema, $el.ChkRed, $el.ChkDev, $el.ChkGrimorio) { $cb.IsChecked = $true }
    Actualiza-Vista
    $el.TxtEstado.Text = "Valores recomendados cargados. Pulsa Aplicar a mi escritorio si quieres guardarlos."
})

$el.BtnToggleHudNow.Add_Click({
    if (Hay-HudActivo) {
        Detener-Hud
        $el.ChkHudMaster.IsChecked = $false
        $c = Lee-FormConfig; Guardar-Config $c
        $el.TxtEstado.Text = "Cajitas ocultadas del escritorio."
    } else {
        $el.ChkHudMaster.IsChecked = $true
        $c = Lee-FormConfig; Guardar-Config $c
        Start-Process -FilePath 'powershell.exe' -ArgumentList "-NoProfile -ExecutionPolicy Bypass -STA -WindowStyle Hidden -File `"$(Join-Path $Aqui 'PixelZenHud.ps1')`"" -WindowStyle Hidden
        Start-Sleep -Milliseconds 350
        $el.TxtEstado.Text = "✅ Cajitas mostradas en tu pantalla principal."
    }
    Actualiza-Vista
})

$el.BtnSoloGuardar.Add_Click({
    $c = Lee-FormConfig
    Guardar-Config $c
    $el.TxtEstado.Text = "💾 Opciones guardadas en configuración."
})

$el.BtnAplicar.Add_Click({
    $c = Lee-FormConfig
    $fase = Aplicar-Todo $c
    $script:previewFase = $fase
    Start-Sleep -Milliseconds 250
    Actualiza-Vista
    $tmeta = $temas | Where-Object { $_.id -eq $c.tema } | Select-Object -First 1
    $bloqSuf = if ($c.usarBloqueo -and $script:bloqueoOk) { ' + bloqueo' } else { '' }
    if ($script:modoMotor -eq 'nativo') {
        $el.TxtEstado.Text = "✨ ¡Listo! '$($tmeta.titulo)' animado en vivo de forma nativa ($($c.monitores) pantalla(s)$bloqSuf)."
    } else {
        $el.TxtEstado.Text = "✅ ¡Listo! Aplicado '$($tmeta.titulo)' en $($c.monitores) pantalla(s)$bloqSuf (fase $fase)."
    }
})

$el.BtnWeb.Add_Click({
    $c = Lee-FormConfig
    Guardar-Config $c
    $py = Resolver-Python
    if (-not $py) {
        $el.TxtEstado.Text = "⚠️ Se necesita Python instalado para abrir el visor animado del navegador."
        return
    }
    $srvPidFile = Join-Path $env:TEMP 'pixelzen_srv.pid'
    $yaCorre = $false
    if (Test-Path $srvPidFile) {
        $sp = Get-Content $srvPidFile -ErrorAction SilentlyContinue
        if ($sp -and (Get-Process -Id ([int]$sp) -ErrorAction SilentlyContinue)) { $yaCorre = $true }
    }
    if (-not $yaCorre) {
        $proc = Start-Process -FilePath $py -ArgumentList "`"$(Join-Path $Aqui 'pixelzen_win.py')`" --servidor --puerto 8765" -WindowStyle Hidden -PassThru
        if ($proc) { Set-Content -Path $srvPidFile -Value $proc.Id -Encoding ASCII }
        Start-Sleep -Milliseconds 600
    }
    $activas = @($c.stats.Keys | Where-Object { $c.stats[$_] }) -join ','
    $hudFlag = if ($c.hud) { '1' } else { '0' }
    Start-Process "http://127.0.0.1:8765/?tema=$($c.tema)&pantalla=principal&modo=$($c.modo)&hora=$($c.horaFija)&hud=$hudFlag&stats=$activas"
    if ($c.monitores -ge 2) {
        Start-Process "http://127.0.0.1:8765/?tema=$($c.tema)&pantalla=secundaria&modo=$($c.modo)&hora=$($c.horaFija)&hud=0"
    }
    $el.TxtEstado.Text = "🎬 Vista animada abierta en tu navegador."
})

# Bandeja del sistema (NotifyIcon junto al reloj)
$script:realClose = $false
$trayIcon = New-Object System.Windows.Forms.NotifyIcon
if (Test-Path $IconPath) { $trayIcon.Icon = New-Object System.Drawing.Icon($IconPath) }
else { $trayIcon.Icon = [System.Drawing.SystemIcons]::Application }
$trayIcon.Text = 'PixelZen Worlds'
$trayIcon.Visible = $true

$ctxMenu = New-Object System.Windows.Forms.ContextMenuStrip
$miAbrir = $ctxMenu.Items.Add('Abrir PixelZen Worlds')
$miAbrir.Add_Click({
    $win.Show()
    $win.WindowState = 'Normal'
    $null = $win.Activate()
})

$miMundos = New-Object System.Windows.Forms.ToolStripMenuItem('Cambiar mundo rápido')
foreach ($t in $temas) {
    $sub = New-Object System.Windows.Forms.ToolStripMenuItem("$($t.anime) · $($t.titulo)")
    $sub.Tag = $t.id
    $sub.Add_Click({
        param($s, $e)
        $script:selectedTema = $s.Tag
        $script:selectedSerie = $script:worldSeries[$s.Tag]
        $c = Lee-FormConfig
        $c.tema = $s.Tag
        $fase = Aplicar-Todo $c
        $script:previewFase = $fase
        Actualiza-Vista
        $el.TxtEstado.Text = "✅ Mundo cambiado desde la bandeja."
    })
    $null = $miMundos.DropDownItems.Add($sub)
}
$null = $ctxMenu.Items.Add($miMundos)

$miHud = $ctxMenu.Items.Add('Mostrar / Ocultar cajitas HUD')
$miHud.Add_Click({ $el.BtnToggleHudNow.RaiseEvent((New-Object System.Windows.RoutedEventArgs([System.Windows.Controls.Primitives.ButtonBase]::ClickEvent))) })

$null = $ctxMenu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator))
$miSalir = $ctxMenu.Items.Add('Cerrar por completo')
$miSalir.Add_Click({
    $script:realClose = $true
    $win.Close()
})

$trayIcon.ContextMenuStrip = $ctxMenu
$trayIcon.Add_DoubleClick({
    $win.Show()
    $win.WindowState = 'Normal'
    $null = $win.Activate()
})

$el.BtnMiniTray.Add_Click({
    $win.Hide()
    $trayIcon.ShowBalloonTip(2500, 'PixelZen Worlds', 'Seguimos activos junto al reloj. Haz doble clic aquí para volver.', [System.Windows.Forms.ToolTipIcon]::Info)
})
$el.BtnSalirTotal.Add_Click({
    $script:realClose = $true
    $win.Close()
})

$win.Add_Closing({
    param($sender, $e)
    if (-not $script:realClose -and $el.ChkTrayCerrar.IsChecked) {
        $e.Cancel = $true
        $win.Hide()
    } else {
        $trayIcon.Visible = $false
        $trayIcon.Dispose()
    }
})

Cambia-Pestana 'mundos'
Cambia-VistaMundo 'series'
Actualiza-Vista

if ($Tray) {
    $c = Cargar-Config
    $null = Aplicar-Todo $c
    $win.WindowState = 'Minimized'
    $win.ShowInTaskbar = $false
    $win.Add_Loaded({ $win.Hide(); $win.ShowInTaskbar = $true })
}

$null = $win.ShowDialog()
