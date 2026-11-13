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
    $cands = @(
        (Join-Path $TemasDir "$temaId\$sub\preview\$fase\v3.png"),
        (Join-Path $Raiz "escenas\$temaId\$sub\preview\$fase\v3.png"),
        (Join-Path $TemasDir "$temaId\$sub\fondo.png"),
        (Join-Path $TemasDir "$temaId\fondo.png")
    )
    foreach ($p in $cands) {
        if ($p -and (Test-Path $p)) { return $p }
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
    [PzWallApp]::Apply($p1, $p2, [int]$numMonitores)
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
            $lista += @{ id = $id; anime = $anime; titulo = $titulo; m1 = $m1; m2 = $m2; m3 = $m3 }
        }
    }
    if ($lista.Count -eq 0) {
        return @(@{ id = 'fittoa'; anime = 'Mushoku Tensei'; titulo = 'Región de Fittoa'; m1 = 'Aldea de Buena'; m2 = 'Reino de Asura'; m3 = 'Santuario del Teletransporte' })
    }
    return $lista
}

$VersionActual = Obtener-Version
$temas = Cargar-Temas

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
        Width="1080" Height="710"
        MinWidth="980" MinHeight="650"
        WindowStartupLocation="CenterScreen"
        Background="#070A17" Foreground="#F3EAD6"
        FontFamily="Segoe UI">
  <Window.Resources>
    <Style x:Key="NavBtn" TargetType="Button">
      <Setter Property="Background" Value="Transparent"/>
      <Setter Property="Foreground" Value="#A8B8CF"/>
      <Setter Property="BorderThickness" Value="0"/>
      <Setter Property="HorizontalContentAlignment" Value="Left"/>
      <Setter Property="Padding" Value="14,11"/>
      <Setter Property="Margin" Value="0,0,0,6"/>
      <Setter Property="FontSize" Value="13"/>
      <Setter Property="FontWeight" Value="SemiBold"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="Bd" Background="{TemplateBinding Background}" CornerRadius="8" BorderBrush="{TemplateBinding BorderBrush}" BorderThickness="1" Padding="{TemplateBinding Padding}">
              <ContentPresenter HorizontalAlignment="{TemplateBinding HorizontalContentAlignment}" VerticalAlignment="Center"/>
            </Border>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
    <Style x:Key="PillBtn" TargetType="Button">
      <Setter Property="Background" Value="#101832"/>
      <Setter Property="Foreground" Value="#D6E0EE"/>
      <Setter Property="BorderBrush" Value="#2A3C64"/>
      <Setter Property="BorderThickness" Value="1"/>
      <Setter Property="Padding" Value="11,6"/>
      <Setter Property="FontSize" Value="12"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border Background="{TemplateBinding Background}" BorderBrush="{TemplateBinding BorderBrush}" BorderThickness="{TemplateBinding BorderThickness}" CornerRadius="6" Padding="{TemplateBinding Padding}">
              <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
            </Border>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
    <Style TargetType="CheckBox">
      <Setter Property="Foreground" Value="#F3EAD6"/>
      <Setter Property="FontSize" Value="13"/>
      <Setter Property="Margin" Value="0,5"/>
      <Setter Property="Cursor" Value="Hand"/>
    </Style>
    <Style TargetType="RadioButton">
      <Setter Property="Foreground" Value="#F3EAD6"/>
      <Setter Property="FontSize" Value="13"/>
      <Setter Property="Margin" Value="0,4"/>
      <Setter Property="Cursor" Value="Hand"/>
    </Style>
  </Window.Resources>

  <Grid Margin="16">
    <Grid.RowDefinitions>
      <RowDefinition Height="Auto"/>
      <RowDefinition Height="*"/>
      <RowDefinition Height="Auto"/>
    </Grid.RowDefinitions>

    <!-- Cabecera amigable -->
    <Border Grid.Row="0" Background="#0D142B" BorderBrush="#28395E" BorderThickness="1" CornerRadius="10" Padding="16,12" Margin="0,0,0,14">
      <DockPanel>
        <StackPanel>
          <StackPanel Orientation="Horizontal">
            <TextBlock Text="✦ PIXELZEN WORLDS" Foreground="#54DED4" FontSize="17" FontWeight="Bold"/>
            <Border Background="#182B3A" BorderBrush="#54DED4" BorderThickness="1" CornerRadius="4" Padding="7,1" Margin="10,2,0,2" VerticalAlignment="Center">
              <TextBlock Text="APP DE ESCRITORIO" Foreground="#54DED4" FontSize="10" FontWeight="Bold"/>
            </Border>
          </StackPanel>
          <TextBlock x:Name="TxtMonInfo" Text="" Foreground="#A8B8CF" FontSize="12" Margin="0,3,0,0"/>
        </StackPanel>
        <StackPanel Orientation="Horizontal" DockPanel.Dock="Right" HorizontalAlignment="Right" VerticalAlignment="Center">
          <Button x:Name="BtnMiniTray" Content="Minimizar junto al reloj" Style="{StaticResource PillBtn}" Margin="0,0,8,0"/>
          <Button x:Name="BtnSalirTotal" Content="Cerrar app" Style="{StaticResource PillBtn}" Foreground="#FFA0A8" BorderBrush="#5A2A36"/>
        </StackPanel>
      </DockPanel>
    </Border>

    <!-- Cuerpo en 3 columnas: Navegación + Contenido + Vista Previa -->
    <Grid Grid.Row="1">
      <Grid.ColumnDefinitions>
        <ColumnDefinition Width="196"/>
        <ColumnDefinition Width="14"/>
        <ColumnDefinition Width="420"/>
        <ColumnDefinition Width="14"/>
        <ColumnDefinition Width="*"/>
      </Grid.ColumnDefinitions>

      <!-- Navegación Lateral -->
      <Border Grid.Column="0" Background="#0B1124" BorderBrush="#233252" BorderThickness="1" CornerRadius="10" Padding="10">
        <DockPanel>
          <StackPanel DockPanel.Dock="Top">
            <TextBlock Text="MENÚ FÁCIL" Foreground="#6F82A6" FontSize="11" FontWeight="Bold" Margin="8,4,0,10"/>
            <Button x:Name="NavMundos" Content="1. Elegir Mundo" Style="{StaticResource NavBtn}"/>
            <Button x:Name="NavPantallas" Content="2. Pantallas y Luz" Style="{StaticResource NavBtn}"/>
            <Button x:Name="NavHud" Content="3. Cajitas del Fondo" Style="{StaticResource NavBtn}"/>
            <Button x:Name="NavSistema" Content="4. Ajustes e Inicio" Style="{StaticResource NavBtn}"/>
          </StackPanel>
          <Border DockPanel.Dock="Bottom" VerticalAlignment="Bottom" Background="#101833" BorderBrush="#25365A" BorderThickness="1" CornerRadius="8" Padding="10" Margin="0,12,0,0">
            <StackPanel>
              <TextBlock Text="RESUMEN ACTUAL" Foreground="#E6B45A" FontSize="10" FontWeight="Bold" Margin="0,0,0,4"/>
              <TextBlock x:Name="TxtResumen" Text="" Foreground="#B9C6DA" FontSize="11" TextWrapping="Wrap" LineHeight="16"/>
            </StackPanel>
          </Border>
        </DockPanel>
      </Border>

      <!-- Área Principal de Páginas -->
      <Border Grid.Column="2" Background="#0B1124" BorderBrush="#233252" BorderThickness="1" CornerRadius="10" Padding="14">
        <Grid>
          <!-- PÁGINA 1: ELEGIR MUNDO (Tarjetas visuales) -->
          <ScrollViewer x:Name="PageMundos" VerticalScrollBarVisibility="Auto">
            <StackPanel>
              <TextBlock Text="¿Qué mundo quieres ver en tu escritorio?" Foreground="#F3EAD6" FontSize="15" FontWeight="Bold"/>
              <TextBlock Text="Haz clic en cualquier tarjeta para previsualizar ambos monitores y luego pulsa Aplicar abajo." Foreground="#8FA2C2" FontSize="12" Margin="0,3,0,12" TextWrapping="Wrap"/>
              <StackPanel x:Name="ListaTarjetasMundos"/>
            </StackPanel>
          </ScrollViewer>

          <!-- PÁGINA 2: PANTALLAS Y LUZ -->
          <ScrollViewer x:Name="PagePantallas" VerticalScrollBarVisibility="Auto" Visibility="Collapsed">
            <StackPanel>
              <TextBlock Text="¿Cuántas pantallas quieres configurar?" Foreground="#F3EAD6" FontSize="15" FontWeight="Bold"/>
              <TextBlock Text="En modo 2 pantallas, tu monitor principal lleva la escena base y el segundo continúa la historia sin repetirse." Foreground="#8FA2C2" FontSize="12" Margin="0,3,0,10" TextWrapping="Wrap"/>

              <Border x:Name="CardMon1" Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12" Margin="0,0,0,8" Cursor="Hand">
                <StackPanel>
                  <RadioButton x:Name="RbMon1" GroupName="Mon" Content="Solo 1 Pantalla (Únicamente monitor principal)" FontWeight="SemiBold"/>
                  <TextBlock Text="Muestra el escenario principal del mundo elegido. Ideal para portátiles o si solo quieres decorar una pantalla." Foreground="#8FA2C2" FontSize="11" Margin="22,2,0,0" TextWrapping="Wrap"/>
                </StackPanel>
              </Border>

              <Border x:Name="CardMon2" Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12" Margin="0,0,0,14" Cursor="Hand">
                <StackPanel>
                  <RadioButton x:Name="RbMon2" GroupName="Mon" Content="2 Pantallas (Principal + Historia extendida)" FontWeight="SemiBold"/>
                  <TextBlock x:Name="TxtMon2Detalle" Text="Detectando pantallas..." Foreground="#54DED4" FontSize="11" Margin="22,2,0,0" TextWrapping="Wrap"/>
                </StackPanel>
              </Border>

              <TextBlock Text="¿Qué escena del grupo quieres en cada pantalla?" Foreground="#F3EAD6" FontSize="15" FontWeight="Bold" Margin="0,2,0,2"/>
              <TextBlock Text="Cada mundo incluye 3 escenas distintas (Principal, Secundaria y Bloqueo). Puedes combinarlas libremente." Foreground="#8FA2C2" FontSize="12" Margin="0,0,0,10" TextWrapping="Wrap"/>

              <Border Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12" Margin="0,0,0,16">
                <StackPanel>
                  <TextBlock Text="🖥️ Pantalla Principal" Foreground="#54DED4" FontSize="12" FontWeight="SemiBold" Margin="0,0,0,4"/>
                  <ComboBox x:Name="CmbFondoPrincipal" FontSize="12" Height="32" Padding="8,4" Margin="0,0,0,10">
                    <ComboBoxItem Content="Principal" Tag="principal"/>
                    <ComboBoxItem Content="Secundaria" Tag="secundaria"/>
                    <ComboBoxItem Content="Bloqueo" Tag="bloqueo"/>
                  </ComboBox>

                  <StackPanel x:Name="PanelComboSec">
                    <TextBlock Text="🖥️ Pantalla Secundaria" Foreground="#E6B45A" FontSize="12" FontWeight="SemiBold" Margin="0,0,0,4"/>
                    <ComboBox x:Name="CmbFondoSecundaria" FontSize="12" Height="32" Padding="8,4" Margin="0,0,0,10">
                      <ComboBoxItem Content="Principal" Tag="principal"/>
                      <ComboBoxItem Content="Secundaria" Tag="secundaria"/>
                      <ComboBoxItem Content="Bloqueo" Tag="bloqueo"/>
                    </ComboBox>
                  </StackPanel>

                  <CheckBox x:Name="ChkBloqueo" Content="🔒 Aplicar también fondo a la Pantalla de Bloqueo de Windows" FontWeight="SemiBold" Margin="0,2,0,6"/>
                  <StackPanel x:Name="PanelComboBloq">
                    <ComboBox x:Name="CmbFondoBloqueo" FontSize="12" Height="32" Padding="8,4" Margin="22,0,0,0">
                      <ComboBoxItem Content="Principal" Tag="principal"/>
                      <ComboBoxItem Content="Secundaria" Tag="secundaria"/>
                      <ComboBoxItem Content="Bloqueo" Tag="bloqueo"/>
                    </ComboBox>
                  </StackPanel>
                </StackPanel>
              </Border>

              <TextBlock Text="¿Cómo cambia la luz del cielo?" Foreground="#F3EAD6" FontSize="15" FontWeight="Bold" Margin="0,4,0,2"/>
              <TextBlock Text="Cada mundo tiene versión de Día, Atardecer Dorado y Noche con estrellas." Foreground="#8FA2C2" FontSize="12" Margin="0,0,0,10" TextWrapping="Wrap"/>

              <ComboBox x:Name="CmbModo" FontSize="13" Height="34" Padding="8,5" Margin="0,0,0,8">
                <ComboBoxItem Content="🌗 Ciclo suave — Día y noche cada 90 min (Recomendado)" Tag="90m"/>
                <ComboBoxItem Content="🕒 Hora real — Igual que el reloj de tu Windows" Tag="real"/>
                <ComboBoxItem Content="⚡ Paseo rápido — Cambia en 90 segundos para probar" Tag="demo"/>
                <ComboBoxItem Content="🔒 Momento fijo — Elige tú Día, Atardecer o Noche" Tag="fija"/>
              </ComboBox>

              <Border x:Name="PanelHora" Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12" Margin="0,4,0,0">
                <StackPanel>
                  <TextBlock Text="Elige el momento fijo que prefieras:" Foreground="#E6B45A" FontSize="12" FontWeight="SemiBold" Margin="0,0,0,8"/>
                  <StackPanel Orientation="Horizontal" Margin="0,0,0,10">
                    <Button x:Name="BtnFijarDia" Content="☀️ Día (13:00)" Style="{StaticResource PillBtn}" Margin="0,0,6,0"/>
                    <Button x:Name="BtnFijarDor" Content="🌅 Atardecer (18:30)" Style="{StaticResource PillBtn}" Margin="0,0,6,0"/>
                    <Button x:Name="BtnFijarNoc" Content="🌙 Noche (22:00)" Style="{StaticResource PillBtn}"/>
                  </StackPanel>
                  <DockPanel>
                    <TextBlock x:Name="TxtHoraVal" Text="21:30" Foreground="#54DED4" FontFamily="Consolas" FontSize="13" FontWeight="Bold" DockPanel.Dock="Right" Width="50" TextAlignment="Right"/>
                    <Slider x:Name="SldHora" Minimum="0" Maximum="23.75" TickFrequency="0.25" IsSnapToTickEnabled="True" Value="21.5"/>
                  </DockPanel>
                </StackPanel>
              </Border>
            </StackPanel>
          </ScrollViewer>

          <!-- PÁGINA 3: CAJITAS DEL ESCRITORIO (HUD) -->
          <ScrollViewer x:Name="PageHud" VerticalScrollBarVisibility="Auto" Visibility="Collapsed">
            <StackPanel>
              <DockPanel Margin="0,0,0,4">
                <TextBlock Text="Tarjetas flotantes del escritorio" Foreground="#F3EAD6" FontSize="15" FontWeight="Bold"/>
                <CheckBox x:Name="ChkHudMaster" Content="Activadas" DockPanel.Dock="Right" HorizontalAlignment="Right" FontWeight="Bold" Foreground="#54DED4" Margin="0"/>
              </DockPanel>
              <TextBlock Text="No bloquean el ratón: puedes hacer clic a través de ellas como si no estuvieran. Mira a la derecha cómo quedan." Foreground="#8FA2C2" FontSize="12" Margin="0,0,0,10" TextWrapping="Wrap"/>

              <StackPanel Orientation="Horizontal" Margin="0,0,0,12">
                <Button x:Name="BtnHudTodas" Content="Mostrar todas" Style="{StaticResource PillBtn}" Margin="0,0,6,0"/>
                <Button x:Name="BtnHudMinimo" Content="Modo limpio (Reloj + Frase)" Style="{StaticResource PillBtn}" Margin="0,0,6,0"/>
                <Button x:Name="BtnHudSoloReloj" Content="Solo Reloj" Style="{StaticResource PillBtn}"/>
              </StackPanel>

              <Border Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12" Margin="0,0,0,8">
                <StackPanel>
                  <CheckBox x:Name="ChkTiempo" Content="🕒 Reloj, fecha y nombre del mundo" FontWeight="SemiBold"/>
                  <TextBlock Text="Muestra la hora grande, la fecha en español y el mundo activo." Foreground="#8FA2C2" FontSize="11" Margin="22,0,0,0"/>
                </StackPanel>
              </Border>
              <Border Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12" Margin="0,0,0,8">
                <StackPanel>
                  <CheckBox x:Name="ChkSistema" Content="💻 Rendimiento del PC (CPU, RAM, Disco, Batería)" FontWeight="SemiBold"/>
                  <TextBlock Text="Barras visuales en vivo para vigilar si tu ordenador va cargado." Foreground="#8FA2C2" FontSize="11" Margin="22,0,0,0"/>
                </StackPanel>
              </Border>
              <Border Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12" Margin="0,0,0,8">
                <StackPanel>
                  <CheckBox x:Name="ChkRed" Content="🌐 Conexión e Internet (Wi-Fi / IP / Velocidad)" FontWeight="SemiBold"/>
                  <TextBlock Text="Muestra tu red, dirección IP local y tráfico de subida/bajada." Foreground="#8FA2C2" FontSize="11" Margin="22,0,0,0"/>
                </StackPanel>
              </Border>
              <Border Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12" Margin="0,0,0,8">
                <StackPanel>
                  <CheckBox x:Name="ChkDev" Content="🛠️ Información técnica / Programador" FontWeight="SemiBold"/>
                  <TextBlock Text="Nombre del equipo, rama Git actual y versiones instaladas." Foreground="#8FA2C2" FontSize="11" Margin="22,0,0,0"/>
                </StackPanel>
              </Border>
              <Border Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12">
                <StackPanel>
                  <CheckBox x:Name="ChkGrimorio" Content="📖 Frase del anime (Grimorio)" FontWeight="SemiBold"/>
                  <TextBlock Text="Citas famosas de los personajes que van rotando automáticamente." Foreground="#8FA2C2" FontSize="11" Margin="22,0,0,0"/>
                </StackPanel>
              </Border>
            </StackPanel>
          </ScrollViewer>

          <!-- PÁGINA 4: AJUSTES E INICIO -->
          <ScrollViewer x:Name="PageSistema" VerticalScrollBarVisibility="Auto" Visibility="Collapsed">
            <StackPanel>
              <TextBlock Text="Comodidad e inicio automático" Foreground="#F3EAD6" FontSize="15" FontWeight="Bold"/>
              <TextBlock Text="Deja PixelZen listo para no tener que abrir carpetas ni usar la consola nunca más." Foreground="#8FA2C2" FontSize="12" Margin="0,3,0,12" TextWrapping="Wrap"/>

              <Border Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12" Margin="0,0,0,10">
                <StackPanel>
                  <TextBlock Text="Acceso rápido desde el Escritorio" Foreground="#E6B45A" FontSize="13" FontWeight="SemiBold" Margin="0,0,0,4"/>
                  <TextBlock Text="Crea un icono directo en tu Escritorio para abrir este panel con un doble clic sin ventanas negras." Foreground="#8FA2C2" FontSize="11" Margin="0,0,0,10" TextWrapping="Wrap"/>
                  <Button x:Name="BtnAccesoDirecto" Content="📌 Crear acceso directo en mi Escritorio" Style="{StaticResource PillBtn}" HorizontalAlignment="Left" Foreground="#54DED4" BorderBrush="#54DED4"/>
                </StackPanel>
              </Border>

              <Border Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12" Margin="0,0,0,10">
                <StackPanel>
                  <CheckBox x:Name="ChkAutoInicio" Content="🚀 Aplicar fondo y abrir junto al reloj al encender Windows" FontWeight="SemiBold"/>
                  <TextBlock Text="Restaura automáticamente tus fondos y tarjetitas cada vez que inicies sesión." Foreground="#8FA2C2" FontSize="11" Margin="22,2,0,6" TextWrapping="Wrap"/>
                  <CheckBox x:Name="ChkTrayCerrar" Content="📌 Al pulsar la X, minimizar junto al reloj en lugar de salir" FontWeight="SemiBold"/>
                  <TextBlock Text="Así podrás cambiar de mundo o encender/apagar el HUD en un clic desde la bandeja." Foreground="#8FA2C2" FontSize="11" Margin="22,2,0,0" TextWrapping="Wrap"/>
                </StackPanel>
              </Border>

              <Border Background="#101832" BorderBrush="#2A3C64" BorderThickness="1" CornerRadius="8" Padding="12">
                <StackPanel>
                  <TextBlock Text="Estado y actualizaciones" Foreground="#E6B45A" FontSize="13" FontWeight="SemiBold" Margin="0,0,0,6"/>
                  <TextBlock x:Name="TxtDiag" Text="" Foreground="#B9C6DA" FontSize="12" TextWrapping="Wrap" LineHeight="19" Margin="0,0,0,10"/>
                  <StackPanel Orientation="Horizontal">
                    <Button x:Name="BtnBuscarUpdate" Content="🔄 Buscar actualización" Style="{StaticResource PillBtn}" Foreground="#54DED4" BorderBrush="#54DED4" Margin="0,0,8,0"/>
                    <Button x:Name="BtnRestaurar" Content="Restablecer ajustes recomendados" Style="{StaticResource PillBtn}"/>
                  </StackPanel>
                </StackPanel>
              </Border>
            </StackPanel>
          </ScrollViewer>
        </Grid>
      </Border>

      <!-- Vista Previa en Vivo (Columna Derecha Siempre Visible) -->
      <Border Grid.Column="4" Background="#0B1124" BorderBrush="#28395E" BorderThickness="1" CornerRadius="10" Padding="14">
        <ScrollViewer VerticalScrollBarVisibility="Auto">
          <StackPanel>
            <DockPanel Margin="0,0,0,10">
              <TextBlock Text="ASÍ SE VERÁ TU ESCRITORIO" Foreground="#54DED4" FontSize="13" FontWeight="Bold" VerticalAlignment="Center"/>
              <StackPanel Orientation="Horizontal" DockPanel.Dock="Right" HorizontalAlignment="Right">
                <Button x:Name="BtnPrevDia" Content="☀️ Día" Style="{StaticResource PillBtn}" Padding="8,4" FontSize="11" Margin="0,0,4,0"/>
                <Button x:Name="BtnPrevDor" Content="🌅 Dorado" Style="{StaticResource PillBtn}" Padding="8,4" FontSize="11" Margin="0,0,4,0"/>
                <Button x:Name="BtnPrevNoc" Content="🌙 Noche" Style="{StaticResource PillBtn}" Padding="8,4" FontSize="11"/>
              </StackPanel>
            </DockPanel>

            <TextBlock x:Name="TxtPrev1Title" Text="PANTALLA PRINCIPAL (Monitor 1)" Foreground="#E6B45A" FontSize="11" FontWeight="Bold" Margin="0,0,0,4"/>
            <Border BorderBrush="#54DED4" BorderThickness="1.5" CornerRadius="6" Background="#050812" Height="215" Margin="0,0,0,12" ClipToBounds="True">
              <Grid>
                <Image x:Name="ImgPrev1" Stretch="UniformToFill" RenderOptions.BitmapScalingMode="NearestNeighbor"/>
                <!-- Simulación en tiempo real del HUD superpuesto -->
                <StackPanel x:Name="MockHudPanel" HorizontalAlignment="Right" VerticalAlignment="Top" Margin="8" Width="108">
                  <Border x:Name="MockTiempo" Background="#D80B1020" BorderBrush="#7D6540" BorderThickness="1" Padding="5,3" Margin="0,0,0,3">
                    <StackPanel>
                      <TextBlock Text="21:34" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
                      <TextBlock x:Name="TxtMockMundo" Text="Fittoa" Foreground="#E6C06E" FontFamily="Consolas" FontSize="7.5" TextTrimming="CharacterEllipsis"/>
                    </StackPanel>
                  </Border>
                  <Border x:Name="MockSistema" Background="#D80B1020" BorderBrush="#7D6540" BorderThickness="1" Padding="5,3" Margin="0,0,0,3">
                    <StackPanel>
                      <TextBlock Text="CPU 12%  RAM 48%" Foreground="#72C48C" FontFamily="Consolas" FontSize="7.5"/>
                    </StackPanel>
                  </Border>
                  <Border x:Name="MockRed" Background="#D80B1020" BorderBrush="#7D6540" BorderThickness="1" Padding="5,3" Margin="0,0,0,3">
                    <TextBlock Text="WI-FI  ↓ 12K/s" Foreground="#54DED4" FontFamily="Consolas" FontSize="7.5"/>
                  </Border>
                  <Border x:Name="MockDev" Background="#D80B1020" BorderBrush="#7D6540" BorderThickness="1" Padding="5,3" Margin="0,0,0,3">
                    <TextBlock Text="DEV · main" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="7.5"/>
                  </Border>
                  <Border x:Name="MockGrimorio" Background="#D80B1020" BorderBrush="#7D6540" BorderThickness="1" Padding="5,3">
                    <TextBlock Text="«Frase del mundo...»" Foreground="#E6C06E" FontFamily="Consolas" FontSize="7.5" TextTrimming="CharacterEllipsis"/>
                  </Border>
                </StackPanel>
              </Grid>
            </Border>

            <StackPanel x:Name="PanelPrev2">
              <TextBlock x:Name="TxtPrev2Title" Text="PANTALLA 2 · CONTINUACIÓN DE LA HISTORIA" Foreground="#E6B45A" FontSize="11" FontWeight="Bold" Margin="0,0,0,4"/>
              <Border BorderBrush="#7D6540" BorderThickness="1.5" CornerRadius="6" Background="#050812" Height="175" ClipToBounds="True">
                <Image x:Name="ImgPrev2" Stretch="UniformToFill" RenderOptions.BitmapScalingMode="NearestNeighbor"/>
              </Border>
              <TextBlock x:Name="TxtM2Sub" Text="" Foreground="#A8B8CF" FontSize="11" Margin="0,4,0,8" TextWrapping="Wrap"/>
            </StackPanel>

            <StackPanel x:Name="PanelPrevBloqueo">
              <TextBlock x:Name="TxtPrevBloqTitle" Text="🔒 PANTALLA DE BLOQUEO" Foreground="#88C8FF" FontSize="11" FontWeight="Bold" Margin="0,2,0,4"/>
              <Border BorderBrush="#4C6FA8" BorderThickness="1.5" CornerRadius="6" Background="#050812" Height="115" ClipToBounds="True">
                <Grid>
                  <Image x:Name="ImgPrevBloqueo" Stretch="UniformToFill" RenderOptions.BitmapScalingMode="NearestNeighbor"/>
                  <StackPanel HorizontalAlignment="Center" VerticalAlignment="Top" Margin="0,12,0,0">
                    <TextBlock Text="21:34" Foreground="#F6F4EA" FontSize="20" FontWeight="Bold" HorizontalAlignment="Center"/>
                    <TextBlock Text="Windows Lock Screen" Foreground="#C8D6EA" FontSize="9" HorizontalAlignment="Center"/>
                  </StackPanel>
                </Grid>
              </Border>
              <TextBlock x:Name="TxtBloqSub" Text="" Foreground="#A8B8CF" FontSize="11" Margin="0,4,0,0" TextWrapping="Wrap"/>
            </StackPanel>

            <Border Background="#101833" BorderBrush="#263A60" BorderThickness="1" CornerRadius="6" Padding="10,8" Margin="0,12,0,0">
              <TextBlock x:Name="TxtEstado" Text="Elige lo que quieras a la izquierda y pulsa Aplicar a mi escritorio." Foreground="#72C48C" FontSize="12" TextWrapping="Wrap"/>
            </Border>
          </StackPanel>
        </ScrollViewer>
      </Border>
    </Grid>

    <!-- Barra inferior de acciones -->
    <Border Grid.Row="2" Background="#0D142B" BorderBrush="#28395E" BorderThickness="1" CornerRadius="10" Padding="12,10" Margin="0,14,0,0">
      <DockPanel>
        <StackPanel Orientation="Horizontal" DockPanel.Dock="Left">
          <Button x:Name="BtnWeb" Content="🎬 Abrir versión animada en navegador" Style="{StaticResource PillBtn}" Foreground="#54DED4" BorderBrush="#397D88" Margin="0,0,8,0"/>
          <Button x:Name="BtnToggleHudNow" Content="👁️ Ocultar cajitas ahora" Style="{StaticResource PillBtn}"/>
        </StackPanel>
        <StackPanel Orientation="Horizontal" DockPanel.Dock="Right" HorizontalAlignment="Right">
          <Button x:Name="BtnSoloGuardar" Content="💾 Solo guardar" Style="{StaticResource PillBtn}" Margin="0,0,8,0"/>
          <Button x:Name="BtnAplicar" Content="✦ APLICAR A MI ESCRITORIO" Padding="20,9" FontSize="13" FontWeight="Bold" Background="#17444E" Foreground="#7CF6EE" BorderBrush="#54DED4" BorderThickness="1.5" Cursor="Hand">
            <Button.Template>
              <ControlTemplate TargetType="Button">
                <Border Background="{TemplateBinding Background}" BorderBrush="{TemplateBinding BorderBrush}" BorderThickness="{TemplateBinding BorderThickness}" CornerRadius="8" Padding="{TemplateBinding Padding}">
                  <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
                </Border>
              </ControlTemplate>
            </Button.Template>
          </Button>
        </StackPanel>
      </DockPanel>
    </Border>
  </Grid>
</Window>
"@

$reader = [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($xaml))
$win = [System.Windows.Markup.XamlReader]::Load($reader)
if (Test-Path $IconPath) {
    try { $win.Icon = [System.Windows.Media.Imaging.BitmapFrame]::Create((New-Object Uri($IconPath))) } catch {}
}

$el = @{}
foreach ($n in 'TxtMonInfo','BtnMiniTray','BtnSalirTotal','NavMundos','NavPantallas','NavHud','NavSistema','TxtResumen','PageMundos','PagePantallas','PageHud','PageSistema','ListaTarjetasMundos','CardMon1','CardMon2','RbMon1','RbMon2','TxtMon2Detalle','CmbFondoPrincipal','PanelComboSec','CmbFondoSecundaria','ChkBloqueo','PanelComboBloq','CmbFondoBloqueo','CmbModo','PanelHora','BtnFijarDia','BtnFijarDor','BtnFijarNoc','TxtHoraVal','SldHora','ChkHudMaster','BtnHudTodas','BtnHudMinimo','BtnHudSoloReloj','ChkTiempo','ChkSistema','ChkRed','ChkDev','ChkGrimorio','BtnAccesoDirecto','ChkAutoInicio','ChkTrayCerrar','TxtDiag','BtnBuscarUpdate','BtnRestaurar','BtnPrevDia','BtnPrevDor','BtnPrevNoc','TxtPrev1Title','ImgPrev1','MockHudPanel','MockTiempo','TxtMockMundo','MockSistema','MockRed','MockDev','MockGrimorio','PanelPrev2','TxtPrev2Title','ImgPrev2','TxtM2Sub','PanelPrevBloqueo','TxtPrevBloqTitle','ImgPrevBloqueo','TxtBloqSub','TxtEstado','BtnWeb','BtnToggleHudNow','BtnSoloGuardar','BtnAplicar') {
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
$script:previewFase = Detectar-Fase $cfg.modo $cfg.horaFija
$script:worldCards = @{}
$script:worldBadges = @{}

# Construir tarjetas visuales de mundos
foreach ($t in $temas) {
    $tid = $t.id
    $bd = New-Object System.Windows.Controls.Border
    $bd.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#101832')
    $bd.BorderThickness = [System.Windows.Thickness]::new(1.5)
    $bd.CornerRadius = [System.Windows.CornerRadius]::new(8)
    $bd.Padding = [System.Windows.Thickness]::new(9)
    $bd.Margin = [System.Windows.Thickness]::new(0, 0, 0, 9)
    $bd.Cursor = [System.Windows.Input.Cursors]::Hand

    $g = New-Object System.Windows.Controls.Grid
    $c1 = New-Object System.Windows.Controls.ColumnDefinition; $c1.Width = [System.Windows.GridLength]::new(108)
    $c2 = New-Object System.Windows.Controls.ColumnDefinition; $c2.Width = [System.Windows.GridLength]::new(10)
    $c3 = New-Object System.Windows.Controls.ColumnDefinition; $c3.Width = [System.Windows.GridLength]::new(1, [System.Windows.GridUnitType]::Star)
    $null = $g.ColumnDefinitions.Add($c1); $null = $g.ColumnDefinitions.Add($c2); $null = $g.ColumnDefinitions.Add($c3)

    $imgWrap = New-Object System.Windows.Controls.Border
    $imgWrap.CornerRadius = [System.Windows.CornerRadius]::new(5)
    $imgWrap.Height = 68
    $imgWrap.ClipToBounds = $true
    $imgWrap.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#060916')
    $thumb = New-Object System.Windows.Controls.Image
    $thumb.Stretch = [System.Windows.Media.Stretch]::UniformToFill
    [System.Windows.Media.RenderOptions]::SetBitmapScalingMode($thumb, [System.Windows.Media.BitmapScalingMode]::NearestNeighbor)
    $thumbPath = Resolver-Preview $tid 'dorado' $false
    if (-not $thumbPath) { $thumbPath = Resolver-Preview $tid 'noche' $false }
    $thumb.Source = Cargar-Bitmap $thumbPath
    $imgWrap.Child = $thumb
    [System.Windows.Controls.Grid]::SetColumn($imgWrap, 0)
    $null = $g.Children.Add($imgWrap)

    $info = New-Object System.Windows.Controls.StackPanel
    $topRow = New-Object System.Windows.Controls.DockPanel
    $lblTitle = New-Object System.Windows.Controls.TextBlock
    $lblTitle.Text = "$($t.anime) · $($t.titulo)"
    $lblTitle.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#F3EAD6')
    $lblTitle.FontSize = 13
    $lblTitle.FontWeight = [System.Windows.FontWeights]::Bold
    $null = $topRow.Children.Add($lblTitle)

    $badge = New-Object System.Windows.Controls.Border
    $badge.Background = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#183E46')
    $badge.BorderBrush = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#54DED4')
    $badge.BorderThickness = [System.Windows.Thickness]::new(1)
    $badge.CornerRadius = [System.Windows.CornerRadius]::new(4)
    $badge.Padding = [System.Windows.Thickness]::new(5, 1, 5, 1)
    $badge.HorizontalAlignment = [System.Windows.HorizontalAlignment]::Right
    [System.Windows.Controls.DockPanel]::SetDock($badge, [System.Windows.Controls.Dock]::Right)
    $bTxt = New-Object System.Windows.Controls.TextBlock
    $bTxt.Text = 'ACTIVO'
    $bTxt.FontSize = 9
    $bTxt.FontWeight = [System.Windows.FontWeights]::Bold
    $bTxt.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#54DED4')
    $badge.Child = $bTxt
    $null = $topRow.Children.Add($badge)

    $lblM1 = New-Object System.Windows.Controls.TextBlock
    $lblM1.Text = "M1: $($t.m1)"
    $lblM1.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#9EB0CC')
    $lblM1.FontSize = 11
    $lblM1.Margin = [System.Windows.Thickness]::new(0, 3, 0, 1)
    $lblM1.TextTrimming = [System.Windows.TextTrimming]::CharacterEllipsis

    $lblM2 = New-Object System.Windows.Controls.TextBlock
    $lblM2.Text = "M2: $($t.m2)"
    $lblM2.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#E6B45A')
    $lblM2.FontSize = 11
    $lblM2.TextTrimming = [System.Windows.TextTrimming]::CharacterEllipsis

    $lblM3 = New-Object System.Windows.Controls.TextBlock
    $lblM3.Text = "🔒 $($t.m3)"
    $lblM3.Foreground = [System.Windows.Media.BrushConverter]::new().ConvertFromString('#88C8FF')
    $lblM3.FontSize = 10.5
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
        $script:selectedTema = $sender.Tag
        Actualiza-Vista
    })
    $script:worldCards[$tid] = $bd
    $script:worldBadges[$tid] = $badge
    $null = $el.ListaTarjetasMundos.Children.Add($bd)
}

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

function Actualiza-Vista {
    $bc = [System.Windows.Media.BrushConverter]::new()
    $tid = $script:selectedTema
    $tmeta = $temas | Where-Object { $_.id -eq $tid } | Select-Object -First 1

    # Resaltar tarjeta elegida
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

    # Nombres de escenas del mundo en los selectores por pantalla
    $script:syncingCombos = $true
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
    $usarBloq = [bool]$el.ChkBloqueo.IsChecked
    $el.PanelComboBloq.Visibility = if ($usarBloq) { 'Visible' } else { 'Collapsed' }

    function Nombre-EscenaVariante([string]$tag) {
        switch ($tag) {
            'secundaria' { return $tmeta.m2 }
            'bloqueo'    { return $tmeta.m3 }
            default      { return $tmeta.m1 }
        }
    }

    # Imágenes de vista previa M1, M2 y Bloqueo
    $p1 = Resolver-Preview $tid $script:previewFase $fpTag
    $p2 = Resolver-Preview $tid $script:previewFase $fsTag
    $pb = Resolver-Preview $tid $script:previewFase $fbTag
    $el.ImgPrev1.Source = Cargar-Bitmap $p1
    $el.ImgPrev2.Source = Cargar-Bitmap $p2
    $el.ImgPrevBloqueo.Source = Cargar-Bitmap $pb
    $el.TxtPrev1Title.Text = "PANTALLA 1 · $(Nombre-EscenaVariante $fpTag)"
    $el.PanelPrev2.Visibility = if ($dosMon) { 'Visible' } else { 'Collapsed' }
    $el.TxtM2Sub.Text = "En tu 2.º monitor: $(Nombre-EscenaVariante $fsTag)"
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

    # Botones de vista previa fase
    foreach ($pair in @(@($el.BtnPrevDia,'dia'), @($el.BtnPrevDor,'dorado'), @($el.BtnPrevNoc,'noche'))) {
        $pair[0].BorderBrush = $bc.ConvertFromString($(if ($script:previewFase -eq $pair[1]) { '#54DED4' } else { '#2A3C64' }))
        $pair[0].Foreground = $bc.ConvertFromString($(if ($script:previewFase -eq $pair[1]) { '#54DED4' } else { '#D6E0EE' }))
    }

    # Resumen lateral
    $modoTxt = switch ($modo) { 'real' { 'Hora real' } 'demo' { 'Pase rápido 90s' } 'fija' { "Fija $($el.TxtHoraVal.Text)" } default { 'Suave 90m' } }
    $nStats = @($el.ChkTiempo, $el.ChkSistema, $el.ChkRed, $el.ChkDev, $el.ChkGrimorio | Where-Object { $_.IsChecked }).Count
    $hudTxt = if ($hudOn) { "$nStats cajitas activas" } else { 'HUD desactivado' }
    $bloqTxt = if ($usarBloq) { 'Activa' } else { 'Sin cambio' }
    $el.TxtResumen.Text = "Mundo: $($tmeta.titulo)`nPantallas: $(if ($dosMon) { '2 pantallas' } else { '1 pantalla' })`nBloqueo: $bloqTxt`nLuz: $modoTxt`nInfo: $hudTxt"
}

# Eventos de navegación y controles
$el.NavMundos.Add_Click({ Cambia-Pestana 'mundos' })
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
$el.ChkBloqueo.Add_Checked({ Actualiza-Vista })
$el.ChkBloqueo.Add_Unchecked({ Actualiza-Vista })
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
Actualiza-Vista

if ($Tray) {
    $c = Cargar-Config
    $null = Aplicar-Todo $c
    $win.WindowState = 'Minimized'
    $win.ShowInTaskbar = $false
    $win.Add_Loaded({ $win.Hide(); $win.ShowInTaskbar = $true })
}

$null = $win.ShowDialog()
