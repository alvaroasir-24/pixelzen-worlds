#!/usr/bin/env python3
"""Telemetría ligera para Windows (sin dependencias externas) usada por PixelZen HUD."""
import ctypes
import json
import os
import shutil
import socket
import subprocess
import sys
import time

_PREV_CPU = None
_PREV_NET = None
_CACHE_SLOW = {'t': 0.0, 'data': None}


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
        for l in wlan.splitlines():
            if 'SSID' in l and 'BSSID' not in l and ':' in l:
                ssid = l.split(':', 1)[1].strip()
                if ssid:
                    iface = ssid[:18]
                    break
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


def recolectar(repo_dir=None):
    if repo_dir is None:
        repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mem = memoria()
    du = shutil.disk_usage(os.path.splitdrive(repo_dir)[0] + os.sep if sys.platform == 'win32' else '/')
    disco = f'{round(100.0 * du.used / du.total)}%'
    return {
        'sistema': {
            'cpu': cpu_pct(),
            'ram': mem['str'],
            'ramPct': mem['pct'],
            'disco': disco,
            'bat': bateria(),
            'up': uptime_str(),
        },
        'red': red_rapida(),
        'dev': dev_lento(repo_dir),
    }


if __name__ == '__main__':
    print(json.dumps(recolectar(), ensure_ascii=False))
