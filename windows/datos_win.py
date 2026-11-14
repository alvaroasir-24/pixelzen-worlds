#!/usr/bin/env python3
"""Telemetría ligera para Windows (sin dependencias externas) usada por PixelZen HUD."""
import base64
import ctypes
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time

_PREV_CPU = None
_PREV_NET = None
_CACHE_SLOW = {'t': 0.0, 'data': None}
_CACHE_GPU = {'t': 0.0, 'nombre': None}
_CACHE_NV = {'t': 0.0, 'data': None}
_CACHE_IFACE = {'t': 0.0, 'ip': None, 'iface': 'RED'}
_CACHE_AUDIO = {'t': 0.0, 'data': {'estado': 'AMBIENTE BSO'}}
_AUDIO_NAMES = ('Spotify.exe', 'vlc.exe', 'Music.UI.exe', 'wmplayer.exe')

_PS_MEDIA_B64 = base64.b64encode(r'''
$ErrorActionPreference = 'SilentlyContinue'
[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media.Control, ContentType = WindowsRuntime] | Out-Null
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
            $out += [pscustomobject]@{
                App    = [string]$s.SourceAppUserModelId
                Status = [string]$pb.PlaybackStatus
                Title  = [string]$info.Title
                Artist = [string]$info.Artist
            }
        }
    }
    [Console]::OutputEncoding = [Text.Encoding]::UTF8
    $out | ConvertTo-Json -Compress
}
'''.strip().encode('utf-16le')).decode('ascii')


class _FILETIME(ctypes.Structure):
    _fields_ = [('dwLowDateTime', ctypes.c_uint32), ('dwHighDateTime', ctypes.c_uint32)]


class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ('dwLength', ctypes.c_uint32),
        ('dwMemoryLoad', ctypes.c_uint32),
        ('ullTotalPhys', ctypes.c_uint64),
        ('ullAvailPhys', ctypes.c_uint64),
        ('ullTotalPageFile', ctypes.c_uint64),
        ('ullAvailPageFile', ctypes.c_uint64),
        ('ullTotalVirtual', ctypes.c_uint64),
        ('ullAvailVirtual', ctypes.c_uint64),
        ('sullAvailExtendedVirtual', ctypes.c_uint64),
    ]


class _SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ('ACLineStatus', ctypes.c_uint8),
        ('BatteryFlag', ctypes.c_uint8),
        ('BatteryLifePercent', ctypes.c_uint8),
        ('SystemStatusFlag', ctypes.c_uint8),
        ('BatteryLifeTime', ctypes.c_uint32),
        ('BatteryFullLifeTime', ctypes.c_uint32),
    ]


def _ft_int(ft):
    return (ft.dwHighDateTime << 32) | ft.dwLowDateTime


def cpu_pct():
    global _PREV_CPU
    if sys.platform != 'win32':
        return 12
    idle, kern, user = _FILETIME(), _FILETIME(), _FILETIME()
    if not ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kern), ctypes.byref(user)):
        return 0
    cur = (_ft_int(idle), _ft_int(kern) + _ft_int(user))
    if _PREV_CPU is None:
        _PREV_CPU = cur
        return 8
    d_idle = cur[0] - _PREV_CPU[0]
    d_tot = cur[1] - _PREV_CPU[1]
    _PREV_CPU = cur
    if d_tot <= 0:
        return 0
    return max(0, min(100, round(100.0 * (1.0 - d_idle / d_tot))))


def memoria():
    if sys.platform != 'win32':
        return {'pct': 40, 'str': '6.4/16G'}
    ms = _MEMORYSTATUSEX()
    ms.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    tot_g = ms.ullTotalPhys / (1024 ** 3)
    used_g = (ms.ullTotalPhys - ms.ullAvailPhys) / (1024 ** 3)
    return {'pct': int(ms.dwMemoryLoad), 'str': f'{used_g:.1f}/{tot_g:.0f}G'}


def bateria():
    if sys.platform != 'win32':
        return 'AC'
    sps = _SYSTEM_POWER_STATUS()
    if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(sps)):
        return 'AC'
    if sps.BatteryFlag == 128 or sps.BatteryLifePercent > 100:
        return 'AC'
    pref = 'CAR ' if sps.ACLineStatus == 1 else ''
    return f'{pref}{sps.BatteryLifePercent}%'


def uptime_str():
    if sys.platform != 'win32':
        return 'UP --'
    ms = ctypes.windll.kernel32.GetTickCount64()
    s = ms // 1000
    h, m = s // 3600, (s % 3600) // 60
    return f'UP {h}h{m:02d}'


def _run_quiet(cmd, timeout=2):
    try:
        si = None
        if sys.platform == 'win32':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return subprocess.run(
            cmd,
            capture_output=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout,
            startupinfo=si,
        ).stdout.strip()
    except Exception:
        return ''


def _formato_tasa(bps):
    if bps >= 1048576:
        return f'{bps / 1048576:.1f}M/s'
    if bps >= 1024:
        return f'{round(bps / 1024)}K/s'
    return f'{int(bps)}B/s'


def red_rapida():
    global _PREV_NET
    ip = '127.0.0.1'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
    except Exception:
        pass

    rx_s, tx_s = '--', '--'
    iface = 'RED'
    out = _run_quiet(['netstat', '-e'], timeout=2)
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[1].isdigit() and parts[2].isdigit():
            rx, tx = int(parts[1]), int(parts[2])
            now = time.monotonic()
            if _PREV_NET and now > _PREV_NET[2]:
                dt = now - _PREV_NET[2]
                rx_s = _formato_tasa(max(0.0, (rx - _PREV_NET[0]) / dt))
                tx_s = _formato_tasa(max(0.0, (tx - _PREV_NET[1]) / dt))
            else:
                rx_s, tx_s = '0B/s', '0B/s'
            _PREV_NET = (rx, tx, now)
            break

    if sys.platform == 'win32':
        wlan = _run_quiet(['netsh', 'wlan', 'show', 'interfaces'], timeout=2)
        ssid_found = False
        for l in wlan.splitlines():
            if 'SSID' in l and 'BSSID' not in l and ':' in l:
                ssid = l.split(':', 1)[1].strip()
                if ssid:
                    iface = ssid[:18]
                    ssid_found = True
                    break
        if not ssid_found:
            now_if = time.monotonic()
            if _CACHE_IFACE['ip'] == ip and now_if - _CACHE_IFACE['t'] < 30:
                iface = _CACHE_IFACE['iface']
            else:
                addr_out = _run_quiet(['netsh', 'interface', 'ipv4', 'show', 'addresses'], timeout=2)
                cur_if = ''
                detected = 'ETHERNET'
                for line in addr_out.splitlines():
                    m = re.search(r'"([^"]+)"', line)
                    if m and ip not in line:
                        cur_if = m.group(1).strip()
                    elif ip and ip in line and cur_if:
                        detected = cur_if.upper()[:18]
                        break
                _CACHE_IFACE.update({'t': now_if, 'ip': ip, 'iface': detected})
                iface = detected
    return {'iface': iface, 'ip': ip, 'rx': rx_s, 'tx': tx_s}


def _ver(cmd):
    if not shutil.which(cmd):
        return None
    out = _run_quiet([cmd, '--version'], timeout=2)
    for tok in out.replace('v', '').split():
        if tok[0].isdigit() and '.' in tok:
            return tok.split(',')[0]
    return '?'


def dev_lento(repo_dir):
    now = time.monotonic()
    if _CACHE_SLOW['data'] and now - _CACHE_SLOW['t'] < 20:
        return _CACHE_SLOW['data']

    branch = _run_quiet(['git', '-C', repo_dir, 'rev-parse', '--abbrev-ref', 'HEAD'])
    dirty = len(_run_quiet(['git', '-C', repo_dir, 'status', '--porcelain']).splitlines()) if branch else 0
    repo_name = os.path.basename(repo_dir)
    repo_txt = f'{repo_name} · {branch}' + (f' (~{dirty})' if dirty else '') if branch else repo_name

    tools = []
    py_v = f'{sys.version_info.major}.{sys.version_info.minor}'
    tools.append(f'PY {py_v}')
    for label, cmd in (('NODE', 'node'), ('GO', 'go'), ('GIT', 'git')):
        v = _ver(cmd)
        if v:
            tools.append(f'{label} {v}')

    data = {'host': socket.gethostname(), 'repo': repo_txt, 'tc': ' · '.join(tools)}
    _CACHE_SLOW['t'] = now
    _CACHE_SLOW['data'] = data
    return data


def gpu_lento():
    now = time.monotonic()
    if _CACHE_GPU['nombre'] and now - _CACHE_GPU['t'] < 120:
        return _CACHE_GPU['nombre']
    nombre = 'WIN GDI+ / CANVAS'
    if sys.platform == 'win32':
        try:
            import winreg
            key_path = r'SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}'
            cands = []
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as k:
                i = 0
                while True:
                    try:
                        sub = winreg.EnumKey(k, i)
                        i += 1
                        if not sub.isdigit():
                            continue
                        with winreg.OpenKey(k, sub) as sk:
                            desc = str(winreg.QueryValueEx(sk, 'DriverDesc')[0]).strip()
                            if desc and 'basic' not in desc.lower():
                                cands.append(desc)
                    except OSError:
                        break
            real = [c for c in cands if not any(v in c.lower() for v in ('spacedesk', 'parsec', 'virtual', 'citrix'))]
            if real:
                nombre = real[0][:28]
            elif cands:
                nombre = cands[0][:28]
        except Exception:
            pass
    _CACHE_GPU['t'] = now
    _CACHE_GPU['nombre'] = nombre
    return nombre


def _nvidia_smi():
    now = time.monotonic()
    if now - _CACHE_NV['t'] < 2.5:
        return _CACHE_NV['data']
    info = None
    if sys.platform == 'win32' and shutil.which('nvidia-smi'):
        out = _run_quiet([
            'nvidia-smi',
            '--query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total',
            '--format=csv,noheader,nounits',
        ], timeout=2)
        if out:
            first = out.splitlines()[0].split(',')
            if len(first) >= 5:
                try:
                    info = {
                        'nombre': first[0].strip()[:28],
                        'uso': max(0, min(100, int(first[1].strip()))),
                        'temp': f'{first[2].strip()}°C',
                        'res': f'VRAM {first[3].strip()}/{first[4].strip()} MB',
                    }
                except ValueError:
                    info = None
    _CACHE_NV['t'] = now
    _CACHE_NV['data'] = info
    return info


def _limpia_app_audio(raw):
    r = raw or ''
    if 'Spotify' in r:
        return 'SPOTIFY'
    if 'Brave' in r:
        return 'BRAVE'
    if 'Chrome' in r:
        return 'CHROME'
    if 'Edge' in r or 'msedge' in r.lower():
        return 'EDGE'
    if 'Firefox' in r:
        return 'FIREFOX'
    if 'vlc' in r.lower():
        return 'VLC'
    clean = r.split('!')[-1].replace('.exe', '').strip()
    return (clean[:12] or 'MEDIA').upper()


def audio_rapido():
    if sys.platform != 'win32':
        return {'estado': 'AMBIENTE BSO'}
    now = time.monotonic()
    if _CACHE_AUDIO['data'] and now - _CACHE_AUDIO['t'] < 3.0:
        return _CACHE_AUDIO['data']

    res = None
    ps_out = _run_quiet(
        ['powershell.exe', '-NoProfile', '-NonInteractive', '-WindowStyle', 'Hidden', '-EncodedCommand', _PS_MEDIA_B64],
        timeout=3,
    )
    if ps_out and (ps_out.startswith('{') or ps_out.startswith('[')):
        try:
            parsed = json.loads(ps_out)
            sessions = parsed if isinstance(parsed, list) else [parsed]
            con_titulo = [s for s in sessions if isinstance(s, dict) and str(s.get('Title', '')).strip()]
            pick = next((s for s in con_titulo if 'Spotify' in str(s.get('App', '')) and s.get('Status') == 'Playing'), None)
            if not pick:
                pick = next((s for s in con_titulo if s.get('Status') == 'Playing'), None)
            if not pick:
                pick = next((s for s in con_titulo if 'Spotify' in str(s.get('App', ''))), None)
            if not pick and con_titulo:
                pick = con_titulo[0]
            if pick:
                app = _limpia_app_audio(pick.get('App', ''))
                playing = pick.get('Status') == 'Playing'
                title = str(pick.get('Title', '')).strip()
                artist = str(pick.get('Artist', '')).strip()
                res = {
                    'estado': f'{app} · EN VIVO' if playing else f'{app} · PAUSA',
                    'pista': title,
                    'detalle': artist or f'{app} · AUDIO',
                    'vol': 'LIVE' if playing else 'PAUSA',
                    'nivel': 76 if playing else 18,
                }
        except Exception:
            res = None

    if res is None:
        out = _run_quiet(['tasklist', '/NH', '/FO', 'CSV'], timeout=2)
        low = out.lower()
        for exe in _AUDIO_NAMES:
            if exe.lower() in low:
                res = {'estado': f'{exe.split(".")[0].upper()} ACTIVO'}
                break
        if res is None:
            res = {'estado': 'AMBIENTE BSO'}

    _CACHE_AUDIO['t'] = now
    _CACHE_AUDIO['data'] = res
    return res


def recolectar(repo_dir=None):
    if repo_dir is None:
        repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mem = memoria()
    cpu = cpu_pct()
    du = shutil.disk_usage(os.path.splitdrive(repo_dir)[0] + os.sep if sys.platform == 'win32' else '/')
    disco = f'{round(100.0 * du.used / du.total)}%'
    nv = _nvidia_smi()
    gpu_data = nv if nv else {
        'nombre': gpu_lento(),
        'uso': max(6, min(95, round(cpu * 0.65 + 6))),
    }
    return {
        'sistema': {
            'cpu': cpu,
            'ram': mem['str'],
            'ramPct': mem['pct'],
            'disco': disco,
            'bat': bateria(),
            'up': uptime_str(),
        },
        'gpu': gpu_data,
        'audio': audio_rapido(),
        'red': red_rapida(),
        'dev': dev_lento(repo_dir),
    }


if __name__ == '__main__':
    print(json.dumps(recolectar(), ensure_ascii=False))
