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
        stats = [pscustomobject]@{ tiempo = $true; sistema = $true; red = $true; dev = $true; grimorio = $true }
    }
}

$cfg = Leer-Config
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
        SizeToContent="Height"
        Width="310"
        ResizeMode="NoResize">
  <Window.Resources>
    <Style TargetType="Border" x:Key="CardStyle">
      <Setter Property="Background" Value="#D60B1020"/>
      <Setter Property="BorderBrush" Value="#7D6540"/>
      <Setter Property="BorderThickness" Value="1"/>
      <Setter Property="Padding" Value="11,9"/>
      <Setter Property="Margin" Value="0,0,0,8"/>
    </Style>
  </Window.Resources>
  <StackPanel x:Name="RootPanel" Margin="0">
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
$win.Left = $primary.Right - $win.Width - 22
$win.Top = $primary.Top + 22

$el = @{}
foreach ($n in 'CardTiempo','CardSistema','CardRed','CardDev','CardGrimorio','TxtModo','TxtHora','TxtSeg','TxtFecha','TxtTema','TxtUp','TxtCpu','BarCpu','TxtRam','BarRam','TxtDisco','TxtBat','TxtIface','TxtIp','TxtRx','TxtTx','TxtHost','TxtRepo','TxtTc','TxtAu','TxtQSub','TxtQTxt') {
    $el[$n] = $win.FindName($n)
}

function Aplica-Visibilidad($c) {
    $st = $c.stats
    $el.CardTiempo.Visibility = if ($st.tiempo) { 'Visible' } else { 'Collapsed' }
    $el.CardSistema.Visibility = if ($st.sistema) { 'Visible' } else { 'Collapsed' }
    $el.CardRed.Visibility = if ($st.red) { 'Visible' } else { 'Collapsed' }
    $el.CardDev.Visibility = if ($st.dev) { 'Visible' } else { 'Collapsed' }
    $el.CardGrimorio.Visibility = if ($st.grimorio) { 'Visible' } else { 'Collapsed' }
}

$script:prevNet = $null
$script:lastConfigTick = 0
$script:cpuCounter = New-Object System.Diagnostics.PerformanceCounter("Processor", "% Processor Time", "_Total")
$null = $script:cpuCounter.NextValue()
$script:lastSlow = [datetime]::MinValue

function Formato-Tasa($bps) {
    if ($bps -ge 1048576) { return "{0:N1}M/s" -f ($bps / 1048576.0) }
    if ($bps -ge 1024) { return "{0}K/s" -f [math]::Round($bps / 1024.0) }
    return "{0}B/s" -f [int]$bps
}

function Refresca-Hud {
    $now = Get-Date
    if ((([int]$now.Second) % 3) -eq 0) {
        $script:cfg = Leer-Config
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

    if ($st.grimorio -and $script:temaData -and $script:temaData.citas.Count -gt 0) {
        $idx = [math]::Floor([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() / 45) % $script:temaData.citas.Count
        $cita = $script:temaData.citas[$idx]
        $el.TxtAu.Text = $cita.au
        $el.TxtQSub.Text = $cita.sub
        $el.TxtQTxt.Text = $cita.es
    }

    if (($now - $script:lastSlow).TotalSeconds -ge 2) {
        $script:lastSlow = $now
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
