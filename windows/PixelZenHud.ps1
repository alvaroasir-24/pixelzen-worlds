Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase, System.Windows.Forms

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
        MinWidth="290">
  <Window.Resources>
    <Style TargetType="Border" x:Key="CardStyle">
      <Setter Property="Background" Value="#D60B1020"/>
      <Setter Property="BorderBrush" Value="#7D6540"/>
      <Setter Property="BorderThickness" Value="1"/>
      <Setter Property="Padding" Value="10,8"/>
      <Setter Property="Margin" Value="0,0,0,7"/>
    </Style>
  </Window.Resources>
  <Grid x:Name="RootPanel" Margin="0">
    <Grid.ColumnDefinitions>
      <ColumnDefinition Width="Auto"/>
      <ColumnDefinition Width="Auto"/>
    </Grid.ColumnDefinitions>

    <StackPanel x:Name="ColExtra" Grid.Column="0" Width="268" Margin="0,0,8,0" VerticalAlignment="Top">
      <Border x:Name="CardClima" Style="{StaticResource CardStyle}">
        <StackPanel>
          <DockPanel Margin="0,0,0,5">
            <TextBlock Text="☀ ÓRBITA &amp; CLIMA" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
            <TextBlock x:Name="TxtClimaMeta" Text="DÍA" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,6"/>
          <DockPanel Margin="0,1">
            <TextBlock x:Name="TxtClimaElev" Text="SOL --°" Foreground="#E6C06E" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
            <TextBlock x:Name="TxtClimaAz" Text="AZ --°" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <ProgressBar x:Name="BarClima" Height="6" Minimum="0" Maximum="100" Value="50" Foreground="#E6B45A" Background="#1C2844" BorderBrush="#2F4266" Margin="0,5,0,4"/>
          <TextBlock x:Name="TxtClimaLuz" Text="CIELO DESPEJADO" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10"/>
        </StackPanel>
      </Border>

      <Border x:Name="CardGpu" Style="{StaticResource CardStyle}">
        <StackPanel>
          <DockPanel Margin="0,0,0,5">
            <TextBlock Text="▣ GPU &amp; MOTOR" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
            <TextBlock x:Name="TxtGpuMeta" Text="8 FPS" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,6"/>
          <TextBlock x:Name="TxtGpuNombre" Text="GPU" Foreground="#E6C06E" FontFamily="Consolas" FontSize="10.5" TextTrimming="CharacterEllipsis" Margin="0,0,0,4"/>
          <DockPanel Margin="0,1">
            <TextBlock Text="CARGA" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" Width="40"/>
            <TextBlock x:Name="TxtGpuUso" Text="--%" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="10.5" DockPanel.Dock="Right" Width="42" TextAlignment="Right"/>
            <ProgressBar x:Name="BarGpu" Height="6" Minimum="0" Maximum="100" Foreground="#66DCE0" Background="#1C2844" BorderBrush="#2F4266" Margin="4,0"/>
          </DockPanel>
          <TextBlock x:Name="TxtGpuRes" Text="640×400 PIXEL" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" Margin="0,4,0,0"/>
        </StackPanel>
      </Border>

      <Border x:Name="CardAudio" Style="{StaticResource CardStyle}">
        <StackPanel>
          <DockPanel Margin="0,0,0,5">
            <TextBlock Text="♪ BSO MUNDO" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
            <TextBlock x:Name="TxtAudioMeta" Text="AMBIENTE" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,6"/>
          <TextBlock x:Name="TxtAudioTrack" Text="--" Foreground="#E6C06E" FontFamily="Consolas" FontSize="11" TextTrimming="CharacterEllipsis"/>
          <TextBlock x:Name="TxtAudioBpm" Text="--" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" Margin="0,3,0,4"/>
          <ProgressBar x:Name="BarAudio" Height="6" Minimum="0" Maximum="100" Value="65" Foreground="#72C48C" Background="#1C2844" BorderBrush="#2F4266"/>
        </StackPanel>
      </Border>

      <Border x:Name="CardFoco" Style="{StaticResource CardStyle}">
        <StackPanel>
          <DockPanel Margin="0,0,0,5">
            <TextBlock Text="⧖ FOCO ZEN" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
            <TextBlock x:Name="TxtFocoMeta" Text="CICLO 1" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,6"/>
          <DockPanel Margin="0,0,0,4">
            <TextBlock x:Name="TxtFocoTimer" Text="25:00" Foreground="#E6C06E" FontFamily="Consolas" FontSize="16" FontWeight="Bold"/>
            <TextBlock x:Name="TxtFocoSesion" Text="0m 00s" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10.5" VerticalAlignment="Center" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <ProgressBar x:Name="BarFoco" Height="6" Minimum="0" Maximum="100" Value="10" Foreground="#54DED4" Background="#1C2844" BorderBrush="#2F4266"/>
        </StackPanel>
      </Border>
    </StackPanel>

    <StackPanel x:Name="ColMain" Grid.Column="1" Width="288" VerticalAlignment="Top">
      <Border x:Name="CardTiempo" Style="{StaticResource CardStyle}">
        <StackPanel>
          <DockPanel Margin="0,0,0,5">
            <TextBlock Text="✦ TIEMPO" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
            <TextBlock x:Name="TxtModo" Text="REAL" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,6"/>
          <StackPanel Orientation="Horizontal" VerticalAlignment="Bottom">
            <TextBlock x:Name="TxtHora" Text="--:--" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="32" FontWeight="Bold"/>
            <TextBlock x:Name="TxtSeg" Text="--" Foreground="#54DED4" FontFamily="Consolas" FontSize="14" FontWeight="Bold" Margin="6,0,0,5" VerticalAlignment="Bottom"/>
          </StackPanel>
          <TextBlock x:Name="TxtFecha" Text="" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="11" Margin="0,2,0,0"/>
          <TextBlock x:Name="TxtTema" Text="" Foreground="#E6C06E" FontFamily="Consolas" FontSize="11" FontWeight="Bold" Margin="0,3,0,0" TextWrapping="Wrap"/>
        </StackPanel>
      </Border>

      <Border x:Name="CardSistema" Style="{StaticResource CardStyle}">
        <StackPanel>
          <DockPanel Margin="0,0,0,5">
            <TextBlock Text="❖ SISTEMA" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
            <TextBlock x:Name="TxtUp" Text="WIN" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,6"/>
          <DockPanel Margin="0,1">
            <TextBlock Text="CPU" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="11" Width="36"/>
            <TextBlock x:Name="TxtCpu" Text="--%" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="11" DockPanel.Dock="Right" Width="48" TextAlignment="Right"/>
            <ProgressBar x:Name="BarCpu" Height="7" Minimum="0" Maximum="100" Foreground="#72C48C" Background="#1C2844" BorderBrush="#2F4266" Margin="4,0"/>
          </DockPanel>
          <DockPanel Margin="0,4,0,1">
            <TextBlock Text="RAM" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="11" Width="36"/>
            <TextBlock x:Name="TxtRam" Text="--" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="11" DockPanel.Dock="Right" Width="74" TextAlignment="Right"/>
            <ProgressBar x:Name="BarRam" Height="7" Minimum="0" Maximum="100" Foreground="#E6B45A" Background="#1C2844" BorderBrush="#2F4266" Margin="4,0"/>
          </DockPanel>
          <DockPanel Margin="0,5,0,0">
            <TextBlock x:Name="TxtDisco" Text="DISCO --" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="11"/>
            <TextBlock x:Name="TxtBat" Text="BAT --" Foreground="#72C48C" FontFamily="Consolas" FontSize="11" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
        </StackPanel>
      </Border>

      <Border x:Name="CardRed" Style="{StaticResource CardStyle}">
        <StackPanel>
          <DockPanel Margin="0,0,0,5">
            <TextBlock Text="◈ RED" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
            <TextBlock x:Name="TxtIface" Text="--" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,6"/>
          <DockPanel>
            <TextBlock Text="IP" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="11"/>
            <TextBlock x:Name="TxtIp" Text="--" Foreground="#F3EAD6" FontFamily="Consolas" FontSize="11" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <DockPanel Margin="0,4,0,0">
            <TextBlock x:Name="TxtRx" Text="↓ --" Foreground="#66DCE0" FontFamily="Consolas" FontSize="11"/>
            <TextBlock x:Name="TxtTx" Text="↑ --" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
        </StackPanel>
      </Border>

      <Border x:Name="CardDev" Style="{StaticResource CardStyle}">
        <StackPanel>
          <DockPanel Margin="0,0,0,5">
            <TextBlock Text="⚔ DEV" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
            <TextBlock x:Name="TxtHost" Text="" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,6"/>
          <TextBlock x:Name="TxtRepo" Text="--" Foreground="#E6C06E" FontFamily="Consolas" FontSize="11" TextTrimming="CharacterEllipsis"/>
          <TextBlock x:Name="TxtTc" Text="--" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" Margin="0,3,0,0" TextWrapping="Wrap"/>
        </StackPanel>
      </Border>

      <Border x:Name="CardGrimorio" Style="{StaticResource CardStyle}">
        <StackPanel>
          <DockPanel Margin="0,0,0,5">
            <TextBlock Text="✧ GRIMORIO" Foreground="#54DED4" FontFamily="Consolas" FontSize="11" FontWeight="Bold"/>
            <TextBlock x:Name="TxtAu" Text="" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="10" HorizontalAlignment="Right" DockPanel.Dock="Right"/>
          </DockPanel>
          <Border BorderBrush="#2F4266" BorderThickness="0,0,0,1" Margin="0,0,0,6"/>
          <TextBlock x:Name="TxtQSub" Text="" Foreground="#E6C06E" FontFamily="Consolas" FontSize="11"/>
          <TextBlock x:Name="TxtQTxt" Text="" Foreground="#A8B8CF" FontFamily="Consolas" FontSize="11" Margin="0,4,0,0" TextWrapping="Wrap"/>
        </StackPanel>
      </Border>
    </StackPanel>
  </Grid>
</Window>
"@

$reader = [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($xaml))
$win = [System.Windows.Markup.XamlReader]::Load($reader)

# Hacer click-through (WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW) y colocar en monitor principal
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class PzWinStyle {
    [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll")] public static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
}
"@

$win.Add_SourceInitialized({
    $hwnd = (New-Object System.Windows.Interop.WindowInteropHelper($win)).Handle
    $ex = [PzWinStyle]::GetWindowLong($hwnd, -20)
    [PzWinStyle]::SetWindowLong($hwnd, -20, $ex -bor 0x20 -bor 0x80) | Out-Null
    [PzWinStyle]::SetWindowPos($hwnd, [IntPtr]::new(1), 0, 0, 0, 0, 0x0013) | Out-Null
})

# Posicionar arriba a la derecha del area de trabajo del monitor principal
$primary = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$win.Left = $primary.Right - 564 - 22
$win.Top = $primary.Top + 22

$el = @{}
foreach ($n in 'ColExtra','ColMain','CardTiempo','CardClima','CardSistema','CardGpu','CardRed','CardAudio','CardDev','CardFoco','CardGrimorio','TxtModo','TxtHora','TxtSeg','TxtFecha','TxtTema','TxtClimaMeta','TxtClimaElev','TxtClimaAz','BarClima','TxtClimaLuz','TxtUp','TxtCpu','BarCpu','TxtRam','BarRam','TxtDisco','TxtBat','TxtGpuMeta','TxtGpuNombre','TxtGpuUso','BarGpu','TxtGpuRes','TxtIface','TxtIp','TxtRx','TxtTx','TxtAudioMeta','TxtAudioTrack','TxtAudioBpm','BarAudio','TxtHost','TxtRepo','TxtTc','TxtFocoMeta','TxtFocoTimer','TxtFocoSesion','BarFoco','TxtAu','TxtQSub','TxtQTxt') {
    $el[$n] = $win.FindName($n)
}

function Aplica-Visibilidad($c) {
    $st = $c.stats
    $el.CardTiempo.Visibility   = if ($st.tiempo)   { 'Visible' } else { 'Collapsed' }
    $el.CardClima.Visibility    = if ($st.clima)    { 'Visible' } else { 'Collapsed' }
    $el.CardSistema.Visibility  = if ($st.sistema)  { 'Visible' } else { 'Collapsed' }
    $el.CardGpu.Visibility      = if ($st.gpu)      { 'Visible' } else { 'Collapsed' }
    $el.CardRed.Visibility      = if ($st.red)      { 'Visible' } else { 'Collapsed' }
    $el.CardAudio.Visibility    = if ($st.audio)    { 'Visible' } else { 'Collapsed' }
    $el.CardDev.Visibility      = if ($st.dev)      { 'Visible' } else { 'Collapsed' }
    $el.CardFoco.Visibility     = if ($st.foco)     { 'Visible' } else { 'Collapsed' }
    $el.CardGrimorio.Visibility = if ($st.grimorio) { 'Visible' } else { 'Collapsed' }

    $hayExtra = [bool]($st.clima -or $st.gpu -or $st.audio -or $st.foco)
    $hayMain  = [bool]($st.tiempo -or $st.sistema -or $st.red -or $st.dev -or $st.grimorio)
    $el.ColExtra.Visibility = if ($hayExtra) { 'Visible' } else { 'Collapsed' }
    $el.ColMain.Visibility  = if ($hayMain)  { 'Visible' } else { 'Collapsed' }
    $el.ColExtra.Margin = if ($hayExtra -and $hayMain) { [System.Windows.Thickness]::new(0,0,8,0) } else { [System.Windows.Thickness]::new(0) }
    $w = if ($hayExtra -and $hayMain) { 564 } elseif ($hayExtra) { 268 } else { 288 }
    $win.Left = $primary.Right - $w - 22
}

$script:prevNet = $null
$script:sessionStart = Get-Date
$script:gpuNombre = $null
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
}
$script:cpuCounter = New-Object System.Diagnostics.PerformanceCounter("Processor", "% Processor Time", "_Total")
$null = $script:cpuCounter.NextValue()
$script:lastSlow = [datetime]::MinValue

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

function Refresca-Hud {
    $now = Get-Date
    if ((([int]$now.Second) % 3) -eq 0) {
        $script:cfg = Normaliza-Config (Leer-Config)
        if ($script:cfg.hud -eq $false) { $win.Close(); return }
        $tp = Join-Path $TemasDir "$($script:cfg.tema)\tema.json"
        if (Test-Path $tp) {
            try { $script:temaData = Get-Content $tp -Raw -Encoding UTF8 | ConvertFrom-Json } catch {}
        }
    }
    Aplica-Visibilidad $script:cfg
    $st = $script:cfg.stats

    if ($st.tiempo) {
        $el.TxtHora.Text = $now.ToString('HH:mm')
        $el.TxtSeg.Text = $now.ToString('ss')
        $el.TxtFecha.Text = $now.ToString('dddd d MMM yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('es-ES'))
        $modoMap = @{ 'real' = 'REAL'; '90m' = 'CICLO 90M'; 'demo' = 'DEMO 90S'; 'fija' = 'FIJA' }
        $el.TxtModo.Text = if ($modoMap.ContainsKey($script:cfg.modo)) { $modoMap[$script:cfg.modo] } else { '90M' }
        $el.TxtTema.Text = if ($script:temaData -and $script:temaData.nombre) { $script:temaData.nombre } else { $script:cfg.tema }
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
        $s = Calc-Sol $fSol
        $elev = $s.e
        $az = $s.az
        $faseTxt = if ($elev -lt -6) { 'NOCHE' } elseif ($elev -lt 4) { 'DORADA' } else { 'DÍA' }
        $luzTxt = if ($elev -lt -6) { 'ESTRELLAS Y LUNA ACTIVAS' } elseif ($elev -lt 4) { 'SOL RASANTE · HORA DORADA' } else { 'CIELO DESPEJADO · LUZ PLENA' }
        $el.TxtClimaMeta.Text = $faseTxt
        $el.TxtClimaElev.Text = "SOL {0:+0.0;-0.0;0.0}°" -f $elev
        $el.TxtClimaAz.Text = "AZ {0}°" -f [math]::Round($az)
        $el.TxtClimaLuz.Text = $luzTxt
        $el.BarClima.Value = [math]::Max(4, [math]::Min(100, (($elev + 18.0) / 68.0) * 100.0))
    }

    if ($st.audio) {
        $info = $script:worldAudio[$script:cfg.tema]
        if (-not $info) { $info = @('Ambient Pixel · OST', '90 BPM · STEREO') }
        $el.TxtAudioTrack.Text = $info[0]
        $el.TxtAudioBpm.Text = $info[1]
        $pulse = 52 + [math]::Round(36 * [math]::Abs([math]::Sin($now.Second * 0.45)))
        $el.BarAudio.Value = $pulse
    }

    if ($st.grimorio -and $script:temaData -and $script:temaData.citas.Count -gt 0) {
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
                $appAudio = Get-Process -Name 'Spotify','vlc','wmplayer','Music.UI' -ErrorAction SilentlyContinue | Select-Object -First 1
                $el.TxtAudioMeta.Text = if ($appAudio) { "$($appAudio.ProcessName.ToUpper()) ACTIVO" } else { 'AMBIENTE BSO' }
            } catch {}
        }
        if ($st.gpu) {
            try {
                if (-not $script:gpuNombre) {
                    $vc = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notmatch 'Basic' } | Select-Object -First 1
                    $script:gpuNombre = if ($vc -and $vc.Name) { $vc.Name } else { 'MOTOR GDI+ WIN' }
                }
                $el.TxtGpuNombre.Text = $script:gpuNombre
                $el.TxtGpuMeta.Text = "$($script:cfg.fps) FPS"
                $sb = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                $el.TxtGpuRes.Text = "$($sb.Width)×$($sb.Height) · MOTOR C#"
                $cpuCur = [math]::Round($script:cpuCounter.NextValue())
                $gpuEst = [math]::Max(4, [math]::Min(95, [math]::Round($cpuCur * 0.65 + 6)))
                $el.TxtGpuUso.Text = "$gpuEst%"
                $el.BarGpu.Value = $gpuEst
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
                $nic = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback' -and $_.IPAddress -ne '127.0.0.1' } | Select-Object -First 1
                $el.TxtIface.Text = if ($nic) { $nic.InterfaceAlias } else { 'RED' }
                $el.TxtIp.Text = if ($nic) { $nic.IPAddress } else { '--' }
                $stats = Get-NetAdapterStatistics | Where-Object { $_.ReceivedBytes -gt 0 } | Sort-Object ReceivedBytes -Descending | Select-Object -First 1
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

$null = $win.ShowDialog()
