Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase, System.Windows.Forms, System.Drawing

$ErrorActionPreference = 'SilentlyContinue'
$Aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$Raiz = Split-Path -Parent $Aqui
$EsInstalada = (Test-Path (Join-Path $Aqui 'lively\temas')) -or (Test-Path (Join-Path $Aqui 'temas'))
$TemasDir = if (Test-Path (Join-Path $Aqui 'lively\temas')) {
    Join-Path $Aqui 'lively\temas'
} elseif (Test-Path (Join-Path $Aqui 'temas')) {
    Join-Path $Aqui 'temas'
} else {
    Join-Path $Raiz 'windows\lively\temas'
}
$DataDir = if ($EsInstalada) { Join-Path $env:LOCALAPPDATA 'PixelZenWorlds' } else { $Aqui }
$ConfigPath = Join-Path $DataDir 'config.json'

# Cerrar instancias previas del HUD (guardando su PID)
$PidFile = Join-Path $env:TEMP 'pixelzen_hud.pid'
if (Test-Path $PidFile) {
    $oldPid = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($oldPid -and $oldPid -ne $PID) {
        Stop-Process -Id ([int]$oldPid) -Force -ErrorAction SilentlyContinue
    }
}
Set-Content -Path $PidFile -Value $PID -Encoding ASCII

function Leer-Config {
    if (Test-Path $ConfigPath) {
        try { return (Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json) } catch {}
    }
    return [pscustomobject]@{
        tema = 'fittoa'
        monitores = 2
        modo = '90m'
        hud = $true
        stats = [pscustomobject]@{
            tiempo = $true; clima = $true; sistema = $true; gpu = $true
            red = $true; audio = $true; dev = $true; foco = $true; grimorio = $true
        }
    }
}

function Normaliza-Config($c) {
    $defStats = [ordered]@{
        tiempo = $true; clima = $true; sistema = $true; gpu = $true
        red = $true; audio = $true; dev = $true; foco = $true; grimorio = $true
    }
    if ($null -eq $c.fps) {
        $c | Add-Member -NotePropertyName fps -NotePropertyValue 8 -Force
    }
    if ($null -eq $c.soloWidgets) {
        $c | Add-Member -NotePropertyName soloWidgets -NotePropertyValue $false -Force
    }
    if (-not $c.stats) {
        $c | Add-Member -NotePropertyName stats -NotePropertyValue ([pscustomobject]$defStats) -Force
    } else {
        foreach ($k in $defStats.Keys) {
            if ($null -eq $c.stats.$k) {
                $c.stats | Add-Member -NotePropertyName $k -NotePropertyValue $true -Force
            }
        }
    }
    return $c
}

$cfg = Normaliza-Config (Leer-Config)
if ($cfg.hud -eq $false) { exit 0 }

# Cargar datos del tema activo (nombre + citas)
$temaJsonPath = Join-Path $TemasDir "$($cfg.tema)\tema.json"
$temaData = $null
if (Test-Path $temaJsonPath) {
    try { $temaData = Get-Content $temaJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json } catch {}
}

$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="PixelZen HUD"
        WindowStyle="None"
        AllowsTransparency="True"
        Background="Transparent"
        ShowInTaskbar="False"
        Topmost="False"
        ResizeMode="NoResize"
        SizeToContent="WidthAndHeight"
        Width="298"
        MinWidth="292">
  <Window.Resources>
    <Style TargetType="Border" x:Key="CardStyle">
      <Setter Property="Background" Value="#D60B1020"/>
      <Setter Property="BorderBrush" Value="#7D6540"/>
      <Setter Property="BorderThickness" Value="1"/>
      <Setter Property="Padding" Value="10,6"/>
      <Setter Property="Margin" Value="0,0,0,5"/>
    </Style>
  </Window.Resources>
  <StackPanel x:Name="RootPanel" Width="292" HorizontalAlignment="Right" VerticalAlignment="Top" Margin="0">
    <Border x:Name="CardTiempo" Style="{StaticResource CardStyle}">
      <StackPanel>
        <DockPanel Margin="0,0,0,3">
          <TextBlock Text="✦ TIEMPO" Foreground="#54DED4" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold"/>
          <TextBlock x:Name="TxtModo" Text="REAL" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,4"/>
        <StackPanel Orientation="Horizontal" VerticalAlignment="Bottom">
          <TextBlock x:Name="TxtHora" Text="--:--" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="26" FontWeight="Bold"/>
          <TextBlock x:Name="TxtSeg" Text="--" Foreground="#54DED4" FontFamily="Consolas" FontSize="12" FontWeight="Bold" Margin="6,0,0,4" VerticalAlignment="Bottom"/>
        </StackPanel>
        <TextBlock x:Name="TxtFecha" Text="" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" Margin="0,1,0,0"/>
        <TextBlock x:Name="TxtTema" Text="" Foreground="#E6C06E" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold" Margin="0,2,0,0" TextTrimming="CharacterEllipsis"/>
      </StackPanel>
    </Border>

    <Border x:Name="CardClima" Style="{StaticResource CardStyle}">
      <StackPanel>
        <DockPanel Margin="0,0,0,3">
          <TextBlock Text="☀ CLIMA &amp; ÓRBITA" Foreground="#54DED4" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold" Margin="0,0,6,0"/>
          <TextBlock x:Name="TxtClimaMeta" Text="UBICACIÓN..." Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" HorizontalAlignment="Right" DockPanel.Dock="Right" TextTrimming="CharacterEllipsis"/>
        </DockPanel>
        <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,4"/>
        <DockPanel Margin="0,0,0,3">
          <TextBlock x:Name="TxtClimaElev" Text="--°C" Foreground="#E6C06E" FontFamily="Consolas" FontSize="10" FontWeight="Bold"/>
          <TextBlock x:Name="TxtClimaAz" Text="SOL --°" Foreground="#54DED4" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <ProgressBar x:Name="BarClima" Height="4" Minimum="0" Maximum="100" Value="50" Foreground="#E6B45A" Background="#1C2844" BorderBrush="#2F4266" Margin="0,1,0,3"/>
        <TextBlock x:Name="TxtClimaLuz" Text="OBTENIENDO CLIMA REAL..." Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" TextTrimming="CharacterEllipsis"/>
      </StackPanel>
    </Border>

    <Border x:Name="CardSistema" Style="{StaticResource CardStyle}">
      <StackPanel>
        <DockPanel Margin="0,0,0,3">
          <TextBlock Text="❖ SISTEMA" Foreground="#54DED4" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold"/>
          <TextBlock x:Name="TxtUp" Text="WIN" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,4"/>
        <DockPanel Margin="0,0,0,2">
          <TextBlock Text="CPU" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" Width="32"/>
          <TextBlock x:Name="TxtCpu" Text="--%" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="10" DockPanel.Dock="Right" Width="44" TextAlignment="Right"/>
          <ProgressBar x:Name="BarCpu" Height="5" Minimum="0" Maximum="100" Foreground="#72C48C" Background="#1C2844" BorderBrush="#2F4266" Margin="4,0"/>
        </DockPanel>
        <DockPanel Margin="0,2,0,2">
          <TextBlock Text="RAM" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" Width="32"/>
          <TextBlock x:Name="TxtRam" Text="--" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="10" DockPanel.Dock="Right" Width="68" TextAlignment="Right"/>
          <ProgressBar x:Name="BarRam" Height="5" Minimum="0" Maximum="100" Foreground="#E6B45A" Background="#1C2844" BorderBrush="#2F4266" Margin="4,0"/>
        </DockPanel>
        <DockPanel Margin="0,2,0,0">
          <TextBlock x:Name="TxtDisco" Text="DISCO --" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10"/>
          <TextBlock x:Name="TxtBat" Text="BAT --" Foreground="#72C48C" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
      </StackPanel>
    </Border>

    <Border x:Name="CardGpu" Style="{StaticResource CardStyle}">
      <StackPanel>
        <DockPanel Margin="0,0,0,3">
          <TextBlock Text="▣ GPU &amp; MOTOR" Foreground="#54DED4" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold"/>
          <TextBlock x:Name="TxtGpuMeta" Text="8 FPS" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,4"/>
        <TextBlock x:Name="TxtGpuNombre" Text="GPU" Foreground="#E6C06E" FontFamily="Consolas" FontSize="10" TextTrimming="CharacterEllipsis" Margin="0,0,0,3"/>
        <DockPanel Margin="0,0,0,2">
          <TextBlock Text="CARGA" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" Width="38"/>
          <TextBlock x:Name="TxtGpuUso" Text="--%" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="10" DockPanel.Dock="Right" Width="40" TextAlignment="Right"/>
          <ProgressBar x:Name="BarGpu" Height="4" Minimum="0" Maximum="100" Foreground="#66DCE0" Background="#1C2844" BorderBrush="#2F4266" Margin="4,0"/>
        </DockPanel>
        <TextBlock x:Name="TxtGpuRes" Text="2560×1440" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" Margin="0,1,0,0" TextTrimming="CharacterEllipsis"/>
      </StackPanel>
    </Border>

    <Border x:Name="CardRed" Style="{StaticResource CardStyle}">
      <StackPanel>
        <DockPanel Margin="0,0,0,3">
          <TextBlock Text="◈ RED ACTIVA" Foreground="#54DED4" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold"/>
          <TextBlock x:Name="TxtIface" Text="--" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,4"/>
        <DockPanel>
          <TextBlock Text="IP" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10"/>
          <TextBlock x:Name="TxtIp" Text="--" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="10" FontWeight="Bold" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <DockPanel Margin="0,2,0,0">
          <TextBlock x:Name="TxtRx" Text="↓ --" Foreground="#66DCE0" FontFamily="Consolas" FontSize="10"/>
          <TextBlock x:Name="TxtTx" Text="↑ --" Foreground="#54DED4" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
      </StackPanel>
    </Border>

    <Border x:Name="CardAudio" Style="{StaticResource CardStyle}">
      <StackPanel>
        <DockPanel Margin="0,0,0,3">
          <TextBlock Text="♪ MÚSICA &amp; SPOTIFY" Foreground="#54DED4" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold"/>
          <TextBlock x:Name="TxtAudioMeta" Text="AMBIENTE" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,4"/>
        <TextBlock x:Name="TxtAudioTrack" Text="--" Foreground="#E6C06E" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold" TextTrimming="CharacterEllipsis"/>
        <TextBlock x:Name="TxtAudioBpm" Text="--" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" Margin="0,1,0,4" TextTrimming="CharacterEllipsis"/>
        <DockPanel LastChildFill="True">
          <TextBlock x:Name="TxtAudioPos" Text="0:00" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9" VerticalAlignment="Center" DockPanel.Dock="Left" Margin="0,0,5,0"/>
          <TextBlock x:Name="TxtAudioDur" Text="0:00" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9" VerticalAlignment="Center" DockPanel.Dock="Right" Margin="5,0,0,0"/>
          <ProgressBar x:Name="BarAudio" Height="5" Minimum="0" Maximum="100" Value="0" Foreground="#72C48C" Background="#1C2844" BorderBrush="#2F4266" VerticalAlignment="Center"/>
        </DockPanel>
      </StackPanel>
    </Border>

    <Border x:Name="CardDev" Style="{StaticResource CardStyle}">
      <StackPanel>
        <DockPanel Margin="0,0,0,3">
          <TextBlock Text="⚔ DEV" Foreground="#54DED4" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold"/>
          <TextBlock x:Name="TxtHost" Text="" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,4"/>
        <TextBlock x:Name="TxtRepo" Text="--" Foreground="#E6C06E" FontFamily="Consolas" FontSize="10" TextTrimming="CharacterEllipsis"/>
        <TextBlock x:Name="TxtTc" Text="--" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" Margin="0,2,0,0" TextTrimming="CharacterEllipsis"/>
      </StackPanel>
    </Border>

    <Border x:Name="CardFoco" Style="{StaticResource CardStyle}">
      <StackPanel>
        <DockPanel Margin="0,0,0,3">
          <TextBlock Text="⧖ FOCO ZEN" Foreground="#54DED4" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold"/>
          <TextBlock x:Name="TxtFocoMeta" Text="CICLO 1" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,4"/>
        <DockPanel Margin="0,0,0,3">
          <TextBlock x:Name="TxtFocoTimer" Text="25:00" Foreground="#E6C06E" FontFamily="Consolas" FontSize="14" FontWeight="Bold"/>
          <TextBlock x:Name="TxtFocoSesion" Text="0m 00s" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" VerticalAlignment="Center" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <ProgressBar x:Name="BarFoco" Height="4" Minimum="0" Maximum="100" Value="10" Foreground="#54DED4" Background="#1C2844" BorderBrush="#2F4266"/>
      </StackPanel>
    </Border>

    <Border x:Name="CardGrimorio" Style="{StaticResource CardStyle}" Margin="0">
      <StackPanel>
        <DockPanel Margin="0,0,0,3">
          <TextBlock Text="✧ GRIMORIO" Foreground="#54DED4" FontFamily="Consolas" FontSize="10.5" FontWeight="Bold"/>
          <TextBlock x:Name="TxtAu" Text="" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="9.5" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
        </DockPanel>
        <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,4"/>
        <TextBlock x:Name="TxtQSub" Text="" Foreground="#E6C06E" FontFamily="Consolas" FontSize="10" TextTrimming="CharacterEllipsis"/>
        <TextBlock x:Name="TxtQTxt" Text="" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" Margin="0,2,0,0" TextWrapping="Wrap"/>
      </StackPanel>
    </Border>
  </StackPanel>
</Window>
"@

$reader = [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($xaml))
$win = [System.Windows.Markup.XamlReader]::Load($reader)

# Hacer click-through (WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW) y colocar en monitor principal
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class PzWinStyle {
    [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll")] public static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll", CharSet = CharSet.Auto)] public static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);

    public static string FindSpotifyTitle() {
        var pids = new System.Collections.Generic.HashSet<uint>();
        foreach (var p in System.Diagnostics.Process.GetProcessesByName("Spotify")) {
            pids.Add((uint)p.Id);
        }
        if (pids.Count == 0) return "";
        string found = "";
        EnumWindows((hWnd, lParam) => {
            uint pid;
            GetWindowThreadProcessId(hWnd, out pid);
            if (!pids.Contains(pid)) return true;
            var cls = new StringBuilder(64);
            GetClassName(hWnd, cls, cls.Capacity);
            string c = cls.ToString();
            if (c != "Chrome_WidgetWin_0" && c != "Chrome_WidgetWin_1") return true;
            var sb = new StringBuilder(512);
            GetWindowText(hWnd, sb, sb.Capacity);
            string t = sb.ToString().Trim();
            if (!string.IsNullOrEmpty(t) && t != "Spotify" && t != "Spotify Free" && t != "Spotify Premium" && t != "AngleHiddenWindow") {
                found = t;
                return false;
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }
}
"@

$script:hudHwnd = [IntPtr]::Zero
$win.Add_SourceInitialized({
    $hwnd = (New-Object System.Windows.Interop.WindowInteropHelper($win)).Handle
    $script:hudHwnd = $hwnd
    $ex = [PzWinStyle]::GetWindowLong($hwnd, -20)
    [PzWinStyle]::SetWindowLong($hwnd, -20, ($ex -bor 0x20 -bor 0x80 -bor 0x08000000)) | Out-Null
    [PzWinStyle]::SetWindowPos($hwnd, [IntPtr]::new(1), 0, 0, 0, 0, (0x0013 -bor 0x0040)) | Out-Null
})

# Posicionar todas las tarjetas en una unica columna en la parte derecha del monitor principal
$primary = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$win.Width = 296
$win.Left = $primary.Right - 296 - 18
$win.Top = $primary.Top + 14

$el = @{}
foreach ($n in 'RootPanel','CardTiempo','CardClima','CardSistema','CardGpu','CardRed','CardAudio','CardDev','CardFoco','CardGrimorio','TxtModo','TxtHora','TxtSeg','TxtFecha','TxtTema','TxtClimaMeta','TxtClimaElev','TxtClimaAz','BarClima','TxtClimaLuz','TxtUp','TxtCpu','BarCpu','TxtRam','BarRam','TxtDisco','TxtBat','TxtGpuMeta','TxtGpuNombre','TxtGpuUso','BarGpu','TxtGpuRes','TxtIface','TxtIp','TxtRx','TxtTx','TxtAudioMeta','TxtAudioTrack','TxtAudioBpm','TxtAudioPos','TxtAudioDur','BarAudio','TxtHost','TxtRepo','TxtTc','TxtFocoMeta','TxtFocoTimer','TxtFocoSesion','BarFoco','TxtAu','TxtQSub','TxtQTxt') {
    $el[$n] = $win.FindName($n)
}

$script:extWallCache = $null
$script:lastExtWallPoll = [datetime]::MinValue

function Convert-HsvToHex([double]$h, [double]$s, [double]$v) {
    $h = (($h % 360.0) + 360.0) % 360.0
    $s = [Math]::Max(0.0, [Math]::Min(1.0, $s))
    $v = [Math]::Max(0.0, [Math]::Min(1.0, $v))
    $c = $v * $s
    $x = $c * (1.0 - [Math]::Abs((($h / 60.0) % 2.0) - 1.0))
    $m = $v - $c
    $rp = 0.0; $gp = 0.0; $bp = 0.0
    if ($h -lt 60) { $rp = $c; $gp = $x }
    elseif ($h -lt 120) { $rp = $x; $gp = $c }
    elseif ($h -lt 180) { $gp = $c; $bp = $x }
    elseif ($h -lt 240) { $gp = $x; $bp = $c }
    elseif ($h -lt 300) { $rp = $x; $bp = $c }
    else { $rp = $c; $bp = $x }
    $r = [int][Math]::Max(0, [Math]::Min(255, [Math]::Round(($rp + $m) * 255.0)))
    $g = [int][Math]::Max(0, [Math]::Min(255, [Math]::Round(($gp + $m) * 255.0)))
    $b = [int][Math]::Max(0, [Math]::Min(255, [Math]::Round(($bp + $m) * 255.0)))
    return ('#{0:X2}{1:X2}{2:X2}' -f $r, $g, $b)
}

function Extraer-PaletaImagen([string]$imgPath) {
    if (-not $imgPath -or -not (Test-Path -LiteralPath $imgPath)) { return $null }
    $bmp = $null
    try {
        $bmp = [System.Drawing.Bitmap]::new($imgPath)
        $w = $bmp.Width; $hPx = $bmp.Height
        if ($w -lt 2 -or $hPx -lt 2) { return $null }

        $bins = @()
        for ($i = 0; $i -lt 12; $i++) {
            $bins += [pscustomobject]@{ w = 0.0; cosSum = 0.0; sinSum = 0.0; satSum = 0.0 }
        }
        $totW = 0.0
        for ($gx = 0; $gx -lt 16; $gx++) {
            $px = [int][Math]::Floor(($gx + 0.5) / 16.0 * $w)
            if ($px -ge $w) { $px = $w - 1 }
            for ($gy = 0; $gy -lt 16; $gy++) {
                $py = [int][Math]::Floor(($gy + 0.5) / 16.0 * $hPx)
                if ($py -ge $hPx) { $py = $hPx - 1 }
                $col = $bmp.GetPixel($px, $py)
                $r = $col.R / 255.0; $g = $col.G / 255.0; $b = $col.B / 255.0
                $mx = [Math]::Max($r, [Math]::Max($g, $b))
                $mn = [Math]::Min($r, [Math]::Min($g, $b))
                $d = $mx - $mn
                if ($mx -lt 0.14) { continue }
                $sat = if ($mx -gt 0.001) { $d / $mx } else { 0.0 }
                if ($sat -lt 0.14 -or ($mx -gt 0.94 -and $sat -lt 0.22)) { continue }
                $hue = 0.0
                if ($d -gt 0.0001) {
                    if ($mx -eq $r) { $hue = 60.0 * ((($g - $b) / $d) % 6.0) }
                    elseif ($mx -eq $g) { $hue = 60.0 * ((($b - $r) / $d) + 2.0) }
                    else { $hue = 60.0 * ((($r - $g) / $d) + 4.0) }
                }
                if ($hue -lt 0.0) { $hue += 360.0 }
                $binIdx = [int][Math]::Floor($hue / 30.0) % 12
                $wt = ($sat * $sat + 0.15) * (0.4 + 0.6 * $mx)
                $rad = $hue * [Math]::PI / 180.0
                $bins[$binIdx].w += $wt
                $bins[$binIdx].cosSum += $wt * [Math]::Cos($rad)
                $bins[$binIdx].sinSum += $wt * [Math]::Sin($rad)
                $bins[$binIdx].satSum += $wt * $sat
                $totW += $wt
            }
        }
        if ($totW -le 0.001) { return @('#475569', '#94A3B8', '#CBD5E1') }

        $b1 = 0
        for ($i = 1; $i -lt 12; $i++) {
            if ($bins[$i].w -gt $bins[$b1].w) { $b1 = $i }
        }
        $h1 = ([Math]::Atan2($bins[$b1].sinSum, $bins[$b1].cosSum) * 180.0 / [Math]::PI + 360.0) % 360.0
        $s1 = $bins[$b1].satSum / $bins[$b1].w

        $b2 = -1
        for ($i = 0; $i -lt 12; $i++) {
            $dist = [Math]::Abs($i - $b1)
            if ($dist -gt 6) { $dist = 12 - $dist }
            if ($dist -ge 2) {
                if ($b2 -lt 0 -or $bins[$i].w -gt $bins[$b2].w) { $b2 = $i }
            }
        }
        if ($b2 -ge 0 -and $bins[$b2].w -ge ($bins[$b1].w * 0.18)) {
            $h2 = ([Math]::Atan2($bins[$b2].sinSum, $bins[$b2].cosSum) * 180.0 / [Math]::PI + 360.0) % 360.0
            $s2 = $bins[$b2].satSum / $bins[$b2].w
        } else {
            $h2 = ($h1 + 42.0) % 360.0
            $s2 = 0.68
        }

        $s1c = [Math]::Max(0.45, [Math]::Min(0.86, $s1))
        $s2c = [Math]::Max(0.50, [Math]::Min(0.85, $s2))
        $borderHex = Convert-HsvToHex $h1 ([Math]::Min(0.72, $s1c)) 0.56
        $acc1Hex   = Convert-HsvToHex $h1 $s1c 0.94
        $acc2Hex   = Convert-HsvToHex $h2 $s2c 0.90
        return @($borderHex, $acc1Hex, $acc2Hex)
    } catch {
        return $null
    } finally {
        if ($bmp) { try { $bmp.Dispose() } catch {} }
    }
}

function Obtener-FondoExterno {
    $ahoraUtc = [DateTime]::UtcNow
    if ($script:extWallCache -and ($ahoraUtc - $script:lastExtWallPoll).TotalSeconds -lt 4) {
        return $script:extWallCache
    }
    $script:lastExtWallPoll = $ahoraUtc
    $defPal = @('#3B5278', '#7CF6EE', '#94A3B8')

    $weProc = Get-Process wallpaper64, wallpaper32, webwallpaper32 -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($weProc) {
        $candCfgs = @()
        try {
            $pExe = $weProc.Path
            if ($pExe) {
                $d1 = Split-Path -Parent $pExe
                $candCfgs += (Join-Path $d1 'config.json')
                $d2 = Split-Path -Parent $d1
                if ($d2) { $candCfgs += (Join-Path $d2 'config.json') }
            }
        } catch {}
        $candCfgs += 'C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine\config.json'
        $candCfgs += 'C:\Program Files\Steam\steamapps\common\wallpaper_engine\config.json'
        $weCfg = $candCfgs | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1

        if ($weCfg) {
            try {
                $mtime = (Get-Item -LiteralPath $weCfg).LastWriteTimeUtc
                if ($script:extWallCache -and $script:extWallCache.cfgPath -eq $weCfg -and $script:extWallCache.mtime -eq $mtime) {
                    return $script:extWallCache
                }
                $weJson = Get-Content -LiteralPath $weCfg -Raw -Encoding UTF8 | ConvertFrom-Json
                $selFile = $null
                foreach ($uProp in $weJson.PSObject.Properties) {
                    $gen = $uProp.Value.general
                    if ($gen -and $gen.wallpaperconfig -and $gen.wallpaperconfig.selectedwallpapers) {
                        $sw = $gen.wallpaperconfig.selectedwallpapers
                        if ($sw.Monitor0 -and $sw.Monitor0.file) {
                            $selFile = [string]$sw.Monitor0.file
                        } else {
                            foreach ($mProp in $sw.PSObject.Properties) {
                                if ($mProp.Value -and $mProp.Value.file) {
                                    $selFile = [string]$mProp.Value.file
                                    break
                                }
                            }
                        }
                        if ($selFile) { break }
                    }
                }
                $title = ''
                $pal = $null
                if ($selFile) {
                    $normFile = ($selFile -replace '/', '\').Trim()
                    $projDir = Split-Path -Parent $normFile
                    $projJsonPath = if ($projDir) { Join-Path $projDir 'project.json' } else { $null }
                    if ($projJsonPath -and (Test-Path -LiteralPath $projJsonPath)) {
                        try {
                            $pj = Get-Content -LiteralPath $projJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
                            if ($pj.title) { $title = ([string]$pj.title).Trim() }
                            if ($pj.preview) {
                                $prevPath = Join-Path $projDir (([string]$pj.preview) -replace '/', '\')
                                $pal = Extraer-PaletaImagen $prevPath
                            }
                        } catch {}
                    }
                    if (-not $title) {
                        $baseNom = [System.IO.Path]::GetFileNameWithoutExtension($normFile)
                        if ($baseNom -and $baseNom -notin @('scene', 'wallpaper', 'index', 'project')) {
                            $title = $baseNom
                        }
                    }
                    if (-not $pal -and $normFile -match '\.(jpg|jpeg|png|bmp|gif)$') {
                        $pal = Extraer-PaletaImagen $normFile
                    }
                }
                if (-not $pal) {
                    $transPath = Join-Path $env:APPDATA 'Microsoft\Windows\Themes\TranscodedWallpaper'
                    $pal = Extraer-PaletaImagen $transPath
                }
                if (-not $pal) { $pal = $defPal }
                $script:extWallCache = @{
                    source  = 'W. ENGINE'
                    title   = $title
                    palette = $pal
                    cfgPath = $weCfg
                    mtime   = $mtime
                }
                return $script:extWallCache
            } catch {}
        }
        return @{
            source  = 'W. ENGINE'
            title   = ''
            palette = $defPal
            cfgPath = ''
            mtime   = [datetime]::MinValue
        }
    }

    $winPath = Join-Path $env:APPDATA 'Microsoft\Windows\Themes\TranscodedWallpaper'
    if (-not (Test-Path -LiteralPath $winPath)) {
        try {
            $regWp = (Get-ItemProperty 'HKCU:\Control Panel\Desktop' -Name WallPaper -ErrorAction SilentlyContinue).WallPaper
            if ($regWp -and (Test-Path -LiteralPath $regWp)) { $winPath = $regWp }
        } catch {}
    }
    if ($winPath -and (Test-Path -LiteralPath $winPath)) {
        try {
            $mtime = (Get-Item -LiteralPath $winPath).LastWriteTimeUtc
            if ($script:extWallCache -and $script:extWallCache.cfgPath -eq $winPath -and $script:extWallCache.mtime -eq $mtime) {
                return $script:extWallCache
            }
            $pal = Extraer-PaletaImagen $winPath
            if (-not $pal) { $pal = $defPal }
            $script:extWallCache = @{
                source  = 'ESCRITORIO'
                title   = ''
                palette = $pal
                cfgPath = $winPath
                mtime   = $mtime
            }
            return $script:extWallCache
        } catch {}
    }

    return @{
        source  = 'ESCRITORIO'
        title   = ''
        palette = $defPal
        cfgPath = ''
        mtime   = [datetime]::MinValue
    }
}

function Aplica-Visibilidad($c) {
    $st = $c.stats
    $soloW = [bool]$c.soloWidgets
    $el.CardTiempo.Visibility   = if ($st.tiempo)   { 'Visible' } else { 'Collapsed' }
    $el.CardClima.Visibility    = if ($st.clima)    { 'Visible' } else { 'Collapsed' }
    $el.CardSistema.Visibility  = if ($st.sistema)  { 'Visible' } else { 'Collapsed' }
    $el.CardGpu.Visibility      = if ($st.gpu)      { 'Visible' } else { 'Collapsed' }
    $el.CardRed.Visibility      = if ($st.red)      { 'Visible' } else { 'Collapsed' }
    $el.CardAudio.Visibility    = if ($st.audio)    { 'Visible' } else { 'Collapsed' }
    $el.CardDev.Visibility      = if ($st.dev)      { 'Visible' } else { 'Collapsed' }
    $el.CardFoco.Visibility     = if ($st.foco)     { 'Visible' } else { 'Collapsed' }
    $el.CardGrimorio.Visibility = if ($st.grimorio -and (-not $soloW)) { 'Visible' } else { 'Collapsed' }

    $win.Width = 296
    $win.Left = $primary.Right - 296 - 18
    if ($soloW) {
        $ext = Obtener-FondoExterno
        Apply-WorldTheme ("ext:" + ($ext.palette -join ',')) ([bool]$c.compactoHud) $ext.palette
    } else {
        Apply-WorldTheme $c.tema ([bool]$c.compactoHud) $null
    }
}

$script:bc = New-Object System.Windows.Media.BrushConverter
$script:lastThemeApplied = ''
$script:lastCompactApplied = $null
$script:worldThemes = @{
    'fittoa'                  = @('#7D6540', '#E6C06E', '#54DED4')
    'continente-demoniaco'    = @('#7F3F2B', '#FF7854', '#F4A261')
    'hunter-x-hunter'         = @('#3A6F4F', '#72C48C', '#F3C65F')
    'black-clover'            = @('#61448A', '#B888FF', '#EF4444')
    'spiderman-miles-morales' = @('#8B2240', '#F43F5E', '#38BDF8')
    'solo-leveling'           = @('#602C94', '#A855F7', '#38BDF8')
    'demon-slayer'            = @('#8A4A22', '#FB923C', '#22D3EE')
    'stranger-things'         = @('#8A2424', '#EF4444', '#A855F7')
    'harry-potter'            = @('#7B6020', '#EAB308', '#38BDF8')
    'naruto'                  = @('#8E5120', '#FF9B38', '#38BDF8')
    'jujutsu-kaisen'          = @('#881337', '#E11D48', '#C084FC')
    'attack-on-titan'         = @('#7C2D12', '#F97316', '#22C55E')
    'one-piece'               = @('#881337', '#F43F5E', '#FACC15')
    'dragon-ball-z'           = @('#075985', '#38BDF8', '#FACC15')
    'cyberpunk-edgerunners'   = @('#713F12', '#FACC15', '#22D3EE')
}

function Apply-WorldTheme([string]$temaId, [bool]$compacto, $customPal = $null) {
    if ($temaId -eq $script:lastThemeApplied -and $compacto -eq $script:lastCompactApplied) { return }
    $script:lastThemeApplied = $temaId
    $script:lastCompactApplied = $compacto
    $pal = if ($customPal -and $customPal.Count -ge 3) { $customPal } else { $script:worldThemes[$temaId] }
    if (-not $pal) { $pal = $script:worldThemes['fittoa'] }
    try {
        $bBorder = $script:bc.ConvertFromString($pal[0])
        $bAcc1 = $script:bc.ConvertFromString($pal[1])
        $bAcc2 = $script:bc.ConvertFromString($pal[2])
        $pad = if ($compacto) { [System.Windows.Thickness]::new(8, 3, 8, 3) } else { [System.Windows.Thickness]::new(10, 6, 10, 6) }
        $mgn = if ($compacto) { [System.Windows.Thickness]::new(0, 0, 0, 3) } else { [System.Windows.Thickness]::new(0, 0, 0, 5) }
        foreach ($cn in 'CardTiempo','CardClima','CardSistema','CardGpu','CardRed','CardAudio','CardDev','CardFoco','CardGrimorio') {
            $card = $el[$cn]
            if ($card) {
                $card.BorderBrush = $bBorder
                $card.Padding = $pad
                $card.Margin = $mgn
            }
        }
        if ($el.TxtTema) { $el.TxtTema.Foreground = $bAcc1 }
        if ($el.TxtSeg) { $el.TxtSeg.Foreground = $bAcc2 }
        if ($el.TxtFocoTimer) { $el.TxtFocoTimer.Foreground = $bAcc1 }
        if ($el.TxtClimaElev) { $el.TxtClimaElev.Foreground = $bAcc1 }
        if ($el.TxtClimaAz) { $el.TxtClimaAz.Foreground = $bAcc2 }
        if ($el.TxtGpuNombre) { $el.TxtGpuNombre.Foreground = $bAcc1 }
        if ($el.TxtAudioTrack) { $el.TxtAudioTrack.Foreground = $bAcc1 }
        if ($el.TxtRepo) { $el.TxtRepo.Foreground = $bAcc1 }
        if ($el.BarClima) { $el.BarClima.Foreground = $bAcc1 }
        if ($el.BarAudio) { $el.BarAudio.Foreground = $bAcc2 }
        if ($el.BarFoco) { $el.BarFoco.Foreground = $bAcc1 }
    } catch {}
}

$script:prevNet = $null
$script:sessionStart = Get-Date
$script:gpuNombre = $null
$script:gpuMetaCache = $null
$script:mediaRs = $null
$script:mediaCache = @{ t = [datetime]::MinValue; ok = $false; app = ''; playing = $false; title = ''; artist = ''; posSec = 0.0; durSec = 0.0; polledAt = [DateTimeOffset]::UtcNow }
$script:climaRealPath = Join-Path $DataDir 'clima_real.json'
$script:climaRealCache = $null
$script:lastClimaFetch = [datetime]::MinValue
$script:worldAudio = @{
    'fittoa'                  = @('Lullaby of Fittoa · OST', '84 BPM · ACOUSTIC LO-FI')
    'continente-demoniaco'    = @('Rikarisu Wasteland · OST', '92 BPM · SYNTH AMBIENT')
    'hunter-x-hunter'         = @('Departure! (Acoustic)', '96 BPM · GUITARRA LO-FI')
    'black-clover'            = @('Haruka Mirai (Piano)', '108 BPM · ORQUESTA')
    'spiderman-miles-morales' = @('Sunflower · Brooklyn Mix', '90 BPM · BOOM-BAP LO-FI')
    'solo-leveling'           = @('DARK ARIA <LV2> · Sawano', '116 BPM · SINFÓNICO')
    'demon-slayer'            = @('Kamado Tanjiro no Uta', '78 BPM · SHAKUHACHI')
    'stranger-things'         = @("Kids / Synthwave '83", '104 BPM · ANALÓGICO')
    'harry-potter'            = @("Hedwig's Theme · Celesta", '88 BPM · CELESTA')
    'naruto'                  = @('Silhouette · Baryon OST', '132 BPM · TAIKO & SHAMISEN')
    'jujutsu-kaisen'          = @('Kaikai Kitan · Domain OST', '128 BPM · CURSED SYNTH')
    'attack-on-titan'         = @('Atæk on Titan · Sawano OST', '138 BPM · CORO ÉPICO')
    'one-piece'               = @('Drums of Liberation · Nika', '126 BPM · TAMBORES')
    'dragon-ball-z'           = @('Ultimate Battle · UI OST', '145 BPM · ROCK SINFÓNICO')
    'cyberpunk-edgerunners'   = @('I Really Want to Stay · OST', '124 BPM · SYNTHWAVE')
}
$script:cpuCounter = New-Object System.Diagnostics.PerformanceCounter("Processor", "% Processor Time", "_Total")
$null = $script:cpuCounter.NextValue()
$script:lastSlow = [datetime]::MinValue

function Limpia-AppAudio($raw) {
    if (-not $raw) { return 'MEDIA' }
    if ($raw -match 'Spotify') { return 'SPOTIFY' }
    if ($raw -match 'Brave')   { return 'BRAVE' }
    if ($raw -match 'Chrome')  { return 'CHROME' }
    if ($raw -match 'msedge|Edge') { return 'EDGE' }
    if ($raw -match 'Firefox') { return 'FIREFOX' }
    if ($raw -match 'vlc')     { return 'VLC' }
    $clean = ($raw -replace '\.exe$','') -replace '.*!',''
    if ($clean.Length -gt 12) { $clean = $clean.Substring(0, 12) }
    return $clean.ToUpper()
}

function Traducir-WmoClima([int]$code) {
    switch ($code) {
        0  { return @{ desc = 'Despejado'; efecto = 'normal' } }
        1  { return @{ desc = 'Mayormente despejado'; efecto = 'normal' } }
        2  { return @{ desc = 'Parcialmente nublado'; efecto = 'normal' } }
        3  { return @{ desc = 'Nublado'; efecto = 'normal' } }
        45 { return @{ desc = 'Niebla'; efecto = 'niebla' } }
        48 { return @{ desc = 'Niebla densa'; efecto = 'niebla' } }
        { $_ -in 51,53,55,56,57 } { return @{ desc = 'Llovizna'; efecto = 'lluvia' } }
        { $_ -in 61,63,65,66,67,80,81,82 } { return @{ desc = 'Lluvia'; efecto = 'lluvia' } }
        { $_ -in 71,73,75,77,85,86 } { return @{ desc = 'Nieve'; efecto = 'nieve' } }
        { $_ -in 95,96,99 } { return @{ desc = 'Tormenta'; efecto = 'tormenta' } }
        default { return @{ desc = 'Despejado'; efecto = 'normal' } }
    }
}

function Obtener-ClimaReal {
    $ahoraUtc = [DateTime]::UtcNow
    if ($script:climaRealCache -and ($ahoraUtc - $script:lastClimaFetch).TotalMinutes -lt 10) {
        return $script:climaRealCache
    }
    if ((-not $script:climaRealCache) -and (Test-Path $script:climaRealPath)) {
        try {
            $disk = Get-Content $script:climaRealPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($disk -and $disk.ok -and $disk.updatedUtc) {
                $dt = [DateTime]::Parse([string]$disk.updatedUtc).ToUniversalTime()
                $script:climaRealCache = $disk
                $script:lastClimaFetch = $dt
                if (($ahoraUtc - $dt).TotalMinutes -lt 10) { return $disk }
            }
        } catch {}
    }
    if ($script:climaRealCache -and ($ahoraUtc - $script:lastClimaFetch).TotalMinutes -lt 10) {
        return $script:climaRealCache
    }

    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $lat = $null; $lon = $null; $city = ''; $country = ''
        if ($script:climaRealCache -and $null -ne $script:climaRealCache.lat -and $null -ne $script:climaRealCache.lon) {
            $lat = [double]$script:climaRealCache.lat
            $lon = [double]$script:climaRealCache.lon
            $city = [string]$script:climaRealCache.city
            $country = [string]$script:climaRealCache.country
        } else {
            try {
                $g1 = Invoke-RestMethod -Uri 'http://ip-api.com/json/?fields=status,country,regionName,city,lat,lon' -TimeoutSec 3
                if ($g1 -and $g1.status -eq 'success' -and $null -ne $g1.lat) {
                    $lat = [double]$g1.lat; $lon = [double]$g1.lon
                    $city = [string]$g1.city; $country = [string]$g1.country
                }
            } catch {}
            if ($null -eq $lat) {
                try {
                    $g2 = Invoke-RestMethod -Uri 'https://ipwho.is/' -TimeoutSec 3
                    if ($g2 -and $g2.success -and $null -ne $g2.latitude) {
                        $lat = [double]$g2.latitude; $lon = [double]$g2.longitude
                        $city = [string]$g2.city; $country = [string]$g2.country
                    }
                } catch {}
            }
            if ($null -eq $lat) {
                try {
                    $g3 = Invoke-RestMethod -Uri 'https://ipapi.co/json/' -Headers @{ 'User-Agent' = 'PixelZenWorlds' } -TimeoutSec 3
                    if ($g3 -and $null -ne $g3.latitude) {
                        $lat = [double]$g3.latitude; $lon = [double]$g3.longitude
                        $city = [string]$g3.city; $country = [string]$g3.country_name
                    }
                } catch {}
            }
        }
        if ($null -ne $lat -and $null -ne $lon) {
            $inv = [System.Globalization.CultureInfo]::InvariantCulture
            $latS = $lat.ToString('0.####', $inv)
            $lonS = $lon.ToString('0.####', $inv)
            $om = Invoke-RestMethod -Uri "https://api.open-meteo.com/v1/forecast?latitude=$latS&longitude=$lonS&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,is_day&timezone=auto" -TimeoutSec 3
            if ($om -and $om.current) {
                $cur = $om.current
                $wmo = Traducir-WmoClima ([int]$cur.weather_code)
                $resClima = [pscustomobject]@{
                    ok         = $true
                    city       = if ($city) { $city } else { 'Tu ubicación' }
                    country    = $country
                    lat        = $lat
                    lon        = $lon
                    temp       = [Math]::Round([double]$cur.temperature_2m, 1)
                    apparent   = [Math]::Round([double]$cur.apparent_temperature, 1)
                    hum        = [int][Math]::Round([double]$cur.relative_humidity_2m)
                    wind       = [Math]::Round([double]$cur.wind_speed_10m, 0)
                    code       = [int]$cur.weather_code
                    desc       = $wmo.desc
                    efecto     = $wmo.efecto
                    isDay      = [int]$cur.is_day
                    updatedUtc = $ahoraUtc.ToString('o')
                }
                $script:climaRealCache = $resClima
                $script:lastClimaFetch = $ahoraUtc
                if (-not (Test-Path $DataDir)) { New-Item -Path $DataDir -ItemType Directory -Force | Out-Null }
                ($resClima | ConvertTo-Json -Depth 3) | Set-Content -Path $script:climaRealPath -Encoding UTF8 -ErrorAction SilentlyContinue
                return $resClima
            }
        }
    } catch {}
    $script:lastClimaFetch = $ahoraUtc.AddMinutes(-8)
    return $script:climaRealCache
}

function Format-TiempoCancion([double]$sec) {
    $tot = [Math]::Max(0, [int][Math]::Floor($sec))
    if ($tot -ge 3600) {
        $h = [int][Math]::Floor($tot / 3600)
        $m = [int][Math]::Floor(($tot % 3600) / 60)
        $s = $tot % 60
        return ('{0}:{1:00}:{2:00}' -f $h, $m, $s)
    }
    $m = [int][Math]::Floor($tot / 60)
    $s = $tot % 60
    return ('{0}:{1:00}' -f $m, $s)
}

function Elige-MejorSesion($sessions) {
    $res = @{ ok = $false; app = ''; playing = $false; title = ''; artist = ''; posSec = 0.0; durSec = 0.0; polledAt = [DateTimeOffset]::UtcNow }
    if (-not $sessions) { return $res }
    $conTitulo = @($sessions | Where-Object { $_.Title -and $_.Title.Trim().Length -gt 0 })
    if ($conTitulo.Count -eq 0) { return $res }

    $pick = $conTitulo | Where-Object { $_.App -match 'Spotify' -and $_.Status -eq 'Playing' } | Select-Object -First 1
    if (-not $pick) { $pick = $conTitulo | Where-Object { $_.Status -eq 'Playing' } | Select-Object -First 1 }
    if (-not $pick) { $pick = $conTitulo | Where-Object { $_.App -match 'Spotify' } | Select-Object -First 1 }
    if (-not $pick) { $pick = $conTitulo | Select-Object -First 1 }

    if ($pick) {
        $res.ok = $true
        $res.app = Limpia-AppAudio $pick.App
        $res.playing = ($pick.Status -eq 'Playing')
        $res.title = $pick.Title.Trim()
        $res.artist = if ($pick.Artist) { $pick.Artist.Trim() } else { '' }
        $pSec = if ($null -ne $pick.PosSec) { [double]$pick.PosSec } else { 0.0 }
        $dSec = if ($null -ne $pick.DurSec) { [double]$pick.DurSec } else { 0.0 }
        if ($res.playing -and $pick.LastUpdUtc) {
            try {
                $lu = [DateTimeOffset]::Parse([string]$pick.LastUpdUtc)
                if ($lu.Year -gt 2000) {
                    $drift = ([DateTimeOffset]::UtcNow - $lu).TotalSeconds
                    if ($drift -gt 0 -and $drift -lt 1800) { $pSec += $drift }
                }
            } catch {}
        }
        if ($dSec -gt 0) { $pSec = [Math]::Min($dSec, [Math]::Max(0.0, $pSec)) }
        $res.posSec = $pSec
        $res.durSec = $dSec
        $res.polledAt = [DateTimeOffset]::UtcNow
    }
    return $res
}

function Obtener-MediaActual {
    $ahora = Get-Date
    if (($ahora - $script:mediaCache.t).TotalSeconds -lt 2.5) {
        return $script:mediaCache
    }
    $res = @{ t = $ahora; ok = $false; app = ''; playing = $false; title = ''; artist = ''; posSec = 0.0; durSec = 0.0; polledAt = [DateTimeOffset]::UtcNow }
    try {
        $sessions = @()
        if ($PSVersionTable.PSVersion.Major -eq 5) {
            if (-not $script:mediaRs) {
                $rs = [runspacefactory]::CreateRunspace()
                $rs.ApartmentState = 'MTA'
                $rs.ThreadOptions = 'ReuseThread'
                $rs.Open()
                $script:mediaRs = $rs
            }
            $ps = [powershell]::Create()
            $ps.Runspace = $script:mediaRs
            $null = $ps.AddScript({
                [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media.Control, ContentType = WindowsRuntime] | Out-Null
                [Windows.Foundation.IAsyncOperation`1, Windows.Foundation, ContentType = WindowsRuntime] | Out-Null
                Add-Type -AssemblyName System.Runtime.WindowsRuntime
                $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
                $opMgr = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()
                $tMgr = $asTaskGeneric.MakeGenericMethod([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]).Invoke($null, @($opMgr))
                if (-not $tMgr.Wait(900)) { return @() }
                $mgr = $tMgr.Result
                $out = @()
                foreach ($s in $mgr.GetSessions()) {
                    $opInfo = $s.TryGetMediaPropertiesAsync()
                    $tInfo = $asTaskGeneric.MakeGenericMethod([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties]).Invoke($null, @($opInfo))
                    if (-not $tInfo.Wait(700)) { continue }
                    $info = $tInfo.Result
                    $pb = $s.GetPlaybackInfo()
                    $posSec = 0.0; $durSec = 0.0; $lastUpdIso = ''
                    try {
                        $tl = $s.GetTimelineProperties()
                        if ($tl) {
                            $stOff = if ($tl.StartTime) { $tl.StartTime.TotalSeconds } else { 0.0 }
                            $durSec = [Math]::Max(0.0, ($tl.EndTime.TotalSeconds - $stOff))
                            $posSec = [Math]::Max(0.0, ($tl.Position.TotalSeconds - $stOff))
                            if ($tl.LastUpdatedTime -and $tl.LastUpdatedTime.Year -gt 2000) {
                                $lastUpdIso = $tl.LastUpdatedTime.ToUniversalTime().ToString('o')
                            }
                        }
                    } catch {}
                    $out += [pscustomobject]@{
                        App        = [string]$s.SourceAppUserModelId
                        Status     = [string]$pb.PlaybackStatus
                        Title      = [string]$info.Title
                        Artist     = [string]$info.Artist
                        PosSec     = $posSec
                        DurSec     = $durSec
                        LastUpdUtc = $lastUpdIso
                    }
                }
                return $out
            })
            $sessions = @($ps.Invoke())
            $ps.Dispose()
        } else {
            $helper = @'
[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media.Control, ContentType = WindowsRuntime] | Out-Null
[Windows.Foundation.IAsyncOperation`1, Windows.Foundation, ContentType = WindowsRuntime] | Out-Null
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
$opMgr = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()
$tMgr = $asTaskGeneric.MakeGenericMethod([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]).Invoke($null, @($opMgr))
if ($tMgr.Wait(900)) {
    $out = @()
    foreach ($s in $tMgr.Result.GetSessions()) {
        $opInfo = $s.TryGetMediaPropertiesAsync()
        $tInfo = $asTaskGeneric.MakeGenericMethod([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties]).Invoke($null, @($opInfo))
        if ($tInfo.Wait(700)) {
            $info = $tInfo.Result
            $pb = $s.GetPlaybackInfo()
            $posSec = 0.0; $durSec = 0.0; $lastUpdIso = ''
            try {
                $tl = $s.GetTimelineProperties()
                if ($tl) {
                    $stOff = if ($tl.StartTime) { $tl.StartTime.TotalSeconds } else { 0.0 }
                    $durSec = [Math]::Max(0.0, ($tl.EndTime.TotalSeconds - $stOff))
                    $posSec = [Math]::Max(0.0, ($tl.Position.TotalSeconds - $stOff))
                    if ($tl.LastUpdatedTime -and $tl.LastUpdatedTime.Year -gt 2000) {
                        $lastUpdIso = $tl.LastUpdatedTime.ToUniversalTime().ToString('o')
                    }
                }
            } catch {}
            $out += [pscustomobject]@{ App = [string]$s.SourceAppUserModelId; Status = [string]$pb.PlaybackStatus; Title = [string]$info.Title; Artist = [string]$info.Artist; PosSec = $posSec; DurSec = $durSec; LastUpdUtc = $lastUpdIso }
        }
    }
    $out | ConvertTo-Json -Compress
}
'@
            $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($helper))
            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = 'powershell.exe'
            $psi.Arguments = "-NoProfile -NonInteractive -WindowStyle Hidden -EncodedCommand $enc"
            $psi.UseShellExecute = $false
            $psi.CreateNoWindow = $true
            $psi.RedirectStandardOutput = $true
            $psi.StandardOutputEncoding = [Text.Encoding]::UTF8
            $proc = [System.Diagnostics.Process]::Start($psi)
            $jsonOut = $proc.StandardOutput.ReadToEnd()
            $null = $proc.WaitForExit(2000)
            if ($jsonOut -and $jsonOut.Trim().StartsWith('{') -or ($jsonOut -and $jsonOut.Trim().StartsWith('['))) {
                $parsed = $jsonOut | ConvertFrom-Json
                if ($parsed -is [array]) { $sessions = $parsed } elseif ($parsed) { $sessions = @($parsed) }
            }
        }

        $pick = Elige-MejorSesion $sessions
        if ($pick.ok) {
            $res.ok = $true
            $res.app = $pick.app
            $res.playing = $pick.playing
            $res.title = $pick.title
            $res.artist = $pick.artist
            $res.posSec = $pick.posSec
            $res.durSec = $pick.durSec
            $res.polledAt = $pick.polledAt
        }
    } catch {}

    if (-not $res.ok) {
        try {
            $spTitle = [PzWinStyle]::FindSpotifyTitle()
            if ($spTitle) {
                $res.ok = $true
                $res.app = 'SPOTIFY'
                $res.playing = $true
                if ($spTitle -match '^(.+?)\s+-\s+(.+)$') {
                    $res.artist = $Matches[1].Trim()
                    $res.title  = $Matches[2].Trim()
                } else {
                    $res.title = $spTitle
                }
            }
        } catch {}
    }

    $script:mediaCache = $res
    return $res
}

function Calc-Sol($fecha, $lat = 40.4, $lon = -3.7) {
    $rad = [math]::PI / 180.0
    $epoch = [datetime]::new(1970,1,1,0,0,0,[System.DateTimeKind]::Utc)
    $nn = ($fecha.ToUniversalTime() - $epoch).TotalDays + 2440587.5 - 2451545.0
    $L = (280.460 + 0.9856474 * $nn) % 360.0
    $g = ((357.528 + 0.9856003 * $nn) % 360.0) * $rad
    $lam = ($L + 1.915 * [math]::Sin($g) + 0.020 * [math]::Sin(2 * $g)) * $rad
    $eps = (23.439 - 0.0000004 * $nn) * $rad
    $ra = [math]::Atan2([math]::Cos($eps) * [math]::Sin($lam), [math]::Cos($lam))
    $dec = [math]::Asin([math]::Sin($eps) * [math]::Sin($lam))
    $gmst = (18.697374558 + 24.06570982441908 * $nn) % 24.0
    $Hh = ($gmst * 15.0 + $lon) * $rad - $ra
    $Hh = [math]::Atan2([math]::Sin($Hh), [math]::Cos($Hh))
    $phi = $lat * $rad
    $e = [math]::Asin([math]::Sin($phi) * [math]::Sin($dec) + [math]::Cos($phi) * [math]::Cos($dec) * [math]::Cos($Hh))
    $A = [math]::Atan2([math]::Sin($Hh), [math]::Cos($Hh) * [math]::Sin($phi) - [math]::Tan($dec) * [math]::Cos($phi)) + [math]::PI
    return @{ e = ($e / $rad); az = (($A / $rad) % 360.0) }
}

function Formato-Tasa($bps) {
    if ($bps -ge 1048576) { return "{0:N1}M/s" -f ($bps / 1048576.0) }
    if ($bps -ge 1024) { return "{0}K/s" -f [math]::Round($bps / 1024.0) }
    return "{0}B/s" -f [int]$bps
}

function Actualiza-BarraAudio($m) {
    if ($m -and $m.ok) {
        if ($m.durSec -gt 0) {
            $extra = 0.0
            if ($m.playing -and $m.polledAt) {
                $extra = [Math]::Max(0.0, ([DateTimeOffset]::UtcNow - $m.polledAt).TotalSeconds)
            }
            $posNow = [Math]::Min([double]$m.durSec, [Math]::Max(0.0, [double]$m.posSec + $extra))
            $el.TxtAudioPos.Text = Format-TiempoCancion $posNow
            $el.TxtAudioDur.Text = Format-TiempoCancion ([double]$m.durSec)
            $el.BarAudio.Value = [Math]::Round([Math]::Max(0.0, [Math]::Min(100.0, ($posNow / [double]$m.durSec) * 100.0)), 1)
        } else {
            $el.TxtAudioPos.Text = '0:00'
            $el.TxtAudioDur.Text = '--:--'
            $el.BarAudio.Value = if ($m.playing) { 100 } else { 0 }
        }
    } else {
        $el.TxtAudioPos.Text = '0:00'
        $el.TxtAudioDur.Text = '--:--'
        $el.BarAudio.Value = 0
    }
}

function Aplicar-AudioInactivo {
    if ($script:cfg.soloWidgets) {
        $el.TxtAudioMeta.Text = 'AUDIO SISTEMA'
        $el.TxtAudioTrack.Text = 'Sin música activa'
        $el.TxtAudioBpm.Text = 'Spotify · Navegador · Sistema'
    } else {
        $info = $script:worldAudio[$script:cfg.tema]
        if (-not $info) { $info = @('Ambient Pixel · OST', '90 BPM · STEREO') }
        $el.TxtAudioMeta.Text = 'AMBIENTE BSO'
        $el.TxtAudioTrack.Text = $info[0]
        $el.TxtAudioBpm.Text = $info[1]
    }
    Actualiza-BarraAudio $null
}

function Refresca-Hud {
    $now = Get-Date
    if ($win.WindowState -eq 'Minimized') { $win.WindowState = 'Normal' }
    if ((([int]$now.Second) % 3) -eq 0) {
        $script:cfg = Normaliza-Config (Leer-Config)
        if ($script:cfg.hud -eq $false) { $win.Close(); return }
        if (-not $script:cfg.soloWidgets) {
            $tp = Join-Path $TemasDir "$($script:cfg.tema)\tema.json"
            if (Test-Path $tp) {
                try { $script:temaData = Get-Content $tp -Raw -Encoding UTF8 | ConvertFrom-Json } catch {}
            }
        }
        if ($script:hudHwnd -and $script:hudHwnd -ne [IntPtr]::Zero) {
            [PzWinStyle]::SetWindowPos($script:hudHwnd, [IntPtr]::new(1), 0, 0, 0, 0, (0x0013 -bor 0x0040)) | Out-Null
        }
    }
    Aplica-Visibilidad $script:cfg
    $st = $script:cfg.stats

    if ($st.tiempo) {
        $el.TxtHora.Text = $now.ToString('HH:mm')
        $el.TxtSeg.Text = $now.ToString('ss')
        $el.TxtFecha.Text = $now.ToString('dddd d MMM yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('es-ES'))
        $modoMap = @{ 'real' = 'REAL'; '90m' = 'CICLO 90M'; 'demo' = 'DEMO 90S'; 'fija' = 'FIJA' }
        if ($script:cfg.soloWidgets) {
            $ext = Obtener-FondoExterno
            $el.TxtModo.Text = $ext.source
            if ($ext.title) {
                $el.TxtTema.Text = $ext.title
                $el.TxtTema.Visibility = 'Visible'
            } else {
                $el.TxtTema.Text = ''
                $el.TxtTema.Visibility = 'Collapsed'
            }
        } else {
            $nomTema = if ($script:temaData -and $script:temaData.nombre) { $script:temaData.nombre } else { $script:cfg.tema }
            $el.TxtModo.Text = if ($modoMap.ContainsKey($script:cfg.modo)) { $modoMap[$script:cfg.modo] } else { '90M' }
            $el.TxtTema.Text = $nomTema
            $el.TxtTema.Visibility = 'Visible'
        }
    }

    if ($st.foco) {
        $secTot = [math]::Max(0, [int](($now - $script:sessionStart).TotalSeconds))
        $cicloSec = 1500
        $rest = $cicloSec - ($secTot % $cicloSec)
        $cicloNum = [math]::Floor($secTot / $cicloSec) + 1
        $el.TxtFocoMeta.Text = "CICLO $cicloNum · ZEN"
        $el.TxtFocoTimer.Text = "{0:00}:{1:00}" -f [int][math]::Floor($rest / 60), [int]($rest % 60)
        $el.TxtFocoSesion.Text = "{0}m {1:00}s" -f [int][math]::Floor($secTot / 60), [int]($secTot % 60)
        $el.BarFoco.Value = [math]::Max(4, [math]::Min(100, (($cicloSec - $rest) / $cicloSec) * 100.0))
    }

    if ($st.clima) {
        $fSol = $now
        if ($script:cfg.modo -eq 'fija' -and $null -ne $script:cfg.horaFija) {
            $hf = [double]$script:cfg.horaFija
            $fSol = $now.Date.AddHours($hf)
        }
        $clReal = Obtener-ClimaReal
        $latU = if ($clReal -and $null -ne $clReal.lat) { [double]$clReal.lat } else { 40.4 }
        $lonU = if ($clReal -and $null -ne $clReal.lon) { [double]$clReal.lon } else { -3.7 }
        $s = Calc-Sol $fSol $latU $lonU
        $elev = $s.e
        $az = $s.az
        $faseTxt = if ($elev -lt -6) { 'NOCHE' } elseif ($elev -lt 4) { 'DORADA' } else { 'DÍA' }
        $clMode = if ($script:cfg.clima) { [string]$script:cfg.clima } else { 'normal' }
        $clTag = if (-not $script:cfg.soloWidgets -and $clMode -and $clMode -ne 'normal') { " · " + $clMode.ToUpper() } else { '' }
        if ($clReal -and $clReal.ok) {
            $ciudadUp = ([string]$clReal.city).ToUpper()
            $el.TxtClimaMeta.Text = "📍 $ciudadUp"
            $el.TxtClimaElev.Text = ("🌡 {0}°C · HUM {1}%" -f $clReal.temp, $clReal.hum)
            $el.TxtClimaAz.Text = ("💨 {0} km/h · SOL {1:+0;-0;0}°" -f $clReal.wind, [math]::Round($elev))
            $el.TxtClimaLuz.Text = ("{0} · {1}{2}" -f ([string]$clReal.desc).ToUpper(), $faseTxt, $clTag)
        } else {
            $luzTxt = (if ($elev -lt -6) { 'ESTRELLAS Y LUNA' } elseif ($elev -lt 4) { 'SOL RASANTE · DORADA' } else { 'CIELO DESPEJADO' }) + $clTag
            $el.TxtClimaMeta.Text = $faseTxt + $clTag
            $el.TxtClimaElev.Text = "SOL {0:+0.0;-0.0;0.0}°" -f $elev
            $el.TxtClimaAz.Text = "AZ {0}°" -f [math]::Round($az)
            $el.TxtClimaLuz.Text = $luzTxt
        }
        $el.BarClima.Value = [math]::Max(4, [math]::Min(100, (($elev + 18.0) / 68.0) * 100.0))
    }

    if ($st.audio -and $script:mediaCache.ok) {
        Actualiza-BarraAudio $script:mediaCache
    } elseif ($st.audio) {
        Aplicar-AudioInactivo
    }

    if ($st.grimorio -and (-not $script:cfg.soloWidgets) -and $script:temaData -and $script:temaData.citas.Count -gt 0) {
        $idx = [math]::Floor([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() / 45) % $script:temaData.citas.Count
        $cita = $script:temaData.citas[$idx]
        $el.TxtAu.Text = $cita.au
        $el.TxtQSub.Text = $cita.sub
        $el.TxtQTxt.Text = $cita.es
    }

    if (($now - $script:lastSlow).TotalSeconds -ge 2) {
        $script:lastSlow = $now
        if ($st.audio) {
            try {
                $media = Obtener-MediaActual
                if ($media.ok) {
                    $el.TxtAudioMeta.Text = if ($media.playing) { "$($media.app) · EN VIVO" } else { "$($media.app) · PAUSA" }
                    $el.TxtAudioTrack.Text = $media.title
                    $el.TxtAudioBpm.Text = if ($media.artist) { $media.artist } else { "$($media.app) · AUDIO ACTIVO" }
                    Actualiza-BarraAudio $media
                } else {
                    Aplicar-AudioInactivo
                }
            } catch {}
        }
        if ($st.gpu) {
            try {
                $sb = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                $nvOut = $null
                try { $nvOut = & nvidia-smi --query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>$null } catch {}
                if ($nvOut -and $nvOut.Trim()) {
                    $line = ($nvOut -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -First 1)
                    $p = $line.Split(',') | ForEach-Object { $_.Trim() }
                    if ($p.Count -ge 5) {
                        $script:gpuNombre = $p[0]
                        $gpuUso = [math]::Max(0, [math]::Min(100, [int]$p[1]))
                        $el.TxtGpuNombre.Text = $script:gpuNombre
                        $el.TxtGpuMeta.Text = "$($p[2])°C · $($script:cfg.fps) FPS"
                        $el.TxtGpuUso.Text = "$gpuUso%"
                        $el.BarGpu.Value = $gpuUso
                        $el.TxtGpuRes.Text = "$($sb.Width)×$($sb.Height) · VRAM $($p[3])/$($p[4]) MB"
                    }
                } else {
                    if (-not $script:gpuNombre) {
                        $vc = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notmatch 'Basic|spacedesk|Virtual|Parsec' } | Select-Object -First 1
                        $script:gpuNombre = if ($vc -and $vc.Name) { $vc.Name } else { 'MOTOR GDI+ WIN' }
                    }
                    $el.TxtGpuNombre.Text = $script:gpuNombre
                    $el.TxtGpuMeta.Text = "$($script:cfg.fps) FPS"
                    $el.TxtGpuRes.Text = "$($sb.Width)×$($sb.Height) · MOTOR C#"
                    $gpuSum = (Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'engtype_3D' } | Measure-Object -Property UtilizationPercentage -Sum).Sum
                    $gpuEst = if ($null -ne $gpuSum) { [math]::Max(0, [math]::Min(100, [int][math]::Round($gpuSum))) } else { [math]::Max(2, [math]::Min(95, [math]::Round($script:cpuCounter.NextValue() * 0.55 + 4))) }
                    $el.TxtGpuUso.Text = "$gpuEst%"
                    $el.BarGpu.Value = $gpuEst
                }
            } catch {}
        }
        if ($st.sistema) {
            try {
                $cpu = [math]::Round($script:cpuCounter.NextValue())
                $el.TxtCpu.Text = "$cpu%"
                $el.BarCpu.Value = [math]::Max(0, [math]::Min(100, $cpu))
                $os = Get-CimInstance Win32_OperatingSystem
                $totG = [math]::Round($os.TotalVisibleMemorySize / 1MB, 0)
                $usedG = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 1)
                $ramPct = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100)
                $el.TxtRam.Text = "$usedG/${totG}G"
                $el.BarRam.Value = $ramPct
                $drv = Get-PSDrive C
                $dPct = [math]::Round(($drv.Used / ($drv.Used + $drv.Free)) * 100)
                $el.TxtDisco.Text = "DISCO $dPct%"
                $bat = Get-CimInstance Win32_Battery | Select-Object -First 1
                $el.TxtBat.Text = if ($bat) { "BAT $($bat.EstimatedChargeRemaining)%" } else { "AC" }
                $up = $now - $os.LastBootUpTime
                $el.TxtUp.Text = "UP $([int]$up.TotalHours)h$($up.Minutes.ToString('00'))"
            } catch {}
        }
        if ($st.red) {
            try {
                $defRoute = Get-NetRoute -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Sort-Object { $_.RouteMetric + $_.InterfaceMetric } | Select-Object -First 1
                $nic = $null
                if ($defRoute) {
                    $nic = Get-NetIPAddress -InterfaceIndex $defRoute.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
                        Where-Object { $_.IPAddress -ne '127.0.0.1' -and $_.IPAddress -notlike '169.254.*' } | Select-Object -First 1
                }
                if (-not $nic) {
                    try {
                        $udp = New-Object System.Net.Sockets.UdpClient
                        $udp.Connect('8.8.8.8', 80)
                        $localIp = $udp.Client.LocalEndPoint.Address.ToString()
                        $udp.Close()
                        if ($localIp) {
                            $nic = Get-NetIPAddress -AddressFamily IPv4 -IPAddress $localIp -ErrorAction SilentlyContinue | Select-Object -First 1
                            if (-not $nic) { $nic = [pscustomobject]@{ InterfaceAlias = 'RED ACTIVA'; IPAddress = $localIp } }
                        }
                    } catch {}
                }
                if (-not $nic) {
                    $nic = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
                        Where-Object { $_.InterfaceAlias -notmatch 'Loopback|VirtualBox|vEthernet|VMware' -and $_.IPAddress -notlike '169.254.*' -and $_.IPAddress -ne '127.0.0.1' } |
                        Select-Object -First 1
                }
                $ifaceTxt = if ($nic -and $nic.InterfaceAlias) { $nic.InterfaceAlias.ToUpper() } else { 'RED' }
                if ($ifaceTxt -match 'WI-?FI|WLAN|WIRELESS') {
                    try {
                        $wlan = (netsh wlan show interfaces 2>$null | Select-String '^\s*SSID\s*:\s*(.+)$' | Select-Object -First 1)
                        if ($wlan -and $wlan.Matches[0].Groups[1].Value.Trim()) {
                            $ifaceTxt = "WIFI · $($wlan.Matches[0].Groups[1].Value.Trim())"
                        }
                    } catch {}
                }
                $el.TxtIface.Text = $ifaceTxt
                $el.TxtIp.Text = if ($nic) { $nic.IPAddress } else { '--' }
                $stats = if ($nic -and $nic.InterfaceAlias) {
                    Get-NetAdapterStatistics -Name $nic.InterfaceAlias -ErrorAction SilentlyContinue | Select-Object -First 1
                } else { $null }
                if (-not $stats) {
                    $stats = Get-NetAdapterStatistics -ErrorAction SilentlyContinue | Where-Object { $_.ReceivedBytes -gt 0 -and $_.Name -notmatch 'VirtualBox|Loopback' } | Sort-Object ReceivedBytes -Descending | Select-Object -First 1
                }
                if ($stats) {
                    $tNow = [DateTime]::UtcNow
                    if ($script:prevNet) {
                        $dt = ($tNow - $script:prevNet.t).TotalSeconds
                        if ($dt -gt 0.2) {
                            $el.TxtRx.Text = ([char]0x2193) + " " + (Formato-Tasa ([math]::Max(0, ($stats.ReceivedBytes - $script:prevNet.rx) / $dt)))
                            $el.TxtTx.Text = ([char]0x2191) + " " + (Formato-Tasa ([math]::Max(0, ($stats.SentBytes - $script:prevNet.tx) / $dt)))
                        }
                    }
                    $script:prevNet = @{ rx = $stats.ReceivedBytes; tx = $stats.SentBytes; t = $tNow }
                }
            } catch {}
        }
        if ($st.dev) {
            $el.TxtHost.Text = $env:COMPUTERNAME
            try {
                $br = (git -C $Raiz rev-parse --abbrev-ref HEAD 2>$null)
                $stGit = @(git -C $Raiz status --porcelain 2>$null).Count
                $el.TxtRepo.Text = if ($br) { "pixelzen-worlds · $br" + $(if ($stGit -gt 0) { " (~$stGit)" } else { "" }) } else { "pixelzen-worlds" }
            } catch {
                $el.TxtRepo.Text = "pixelzen-worlds"
            }
            $pyExe = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
            $pyOk = (Get-Command python -ErrorAction SilentlyContinue) -or (Test-Path $pyExe)
            $el.TxtTc.Text = "PS $($PSVersionTable.PSVersion.Major).$($PSVersionTable.PSVersion.Minor)" + $(if ($pyOk) { " · PY 3.12" } else { "" }) + " · MON $($script:cfg.monitores)"
        }
    }
}

Aplica-Visibilidad $cfg
Refresca-Hud

$timer = New-Object System.Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromSeconds(1)
$timer.Add_Tick({ Refresca-Hud })
$timer.Start()

$win.Add_Closed({
    try { $timer.Stop() } catch {}
    if ($script:mediaRs) {
        try { $script:mediaRs.Close(); $script:mediaRs.Dispose() } catch {}
    }
})

$null = $win.ShowDialog()
