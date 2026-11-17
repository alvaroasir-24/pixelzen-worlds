#!/usr/bin/env python3
"""PixelZen HUD - motor de datos. Solo lectura, sin red, sin sudo.
  datos.py rapido  -> CPU, RAM, temperatura, bateria, red (cada ~2 s)
  datos.py lento   -> puertos, repos git, servicios, herramientas (cada ~20 s)
Salida: JSON por stdout."""
import glob, json, os, re, shutil, subprocess, sys, time

MODO = sys.argv[1] if len(sys.argv) > 1 else 'rapido'
ETQ = sys.argv[2] if len(sys.argv) > 2 else 'hud'
ESTADO = os.path.join(os.environ.get('XDG_RUNTIME_DIR', '/tmp'), f'pixelzen-{ETQ}-{MODO}.json')

def sh(cmd, t=2):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=t).stdout
    except Exception:
        return ''

def leer(p, d=''):
    try:
        return open(p).read().strip()
    except Exception:
        return d

def carga_estado():
    try: return json.load(open(ESTADO))
    except Exception: return {}

def guarda_estado(e):
    try: json.dump(e, open(ESTADO, 'w'))
    except Exception: pass

# ----------------------------------------------------------------- rapido
def cpu_pct(e):
    v = [int(x) for x in open('/proc/stat').readline().split()[1:9]]
    idle, total = v[3] + v[4], sum(v)
    ant = e.get('cpu')
    e['cpu'] = [idle, total]
    if not ant or total == ant[1]: return 0.0
    return round(100.0 * (1 - (idle - ant[0]) / (total - ant[1])), 1)

def memoria():
    m = {}
    for l in open('/proc/meminfo'):
        k, v = l.split(':'); m[k] = int(v.split()[0])
    tot, disp = m['MemTotal'], m['MemAvailable']
    sw = m.get('SwapTotal', 0)
    return dict(pct=round(100.0 * (tot - disp) / tot, 1), usado=round((tot - disp) / 1048576, 1), total=round(tot / 1048576, 1),
                swap=round(100.0 * (sw - m.get('SwapFree', 0)) / sw, 1) if sw else 0)

def temperatura():
    for h in glob.glob('/sys/class/hwmon/hwmon*'):
        if leer(h + '/name') in ('k10temp', 'coretemp', 'zenpower'):
            t = leer(h + '/temp1_input')
            if t: return round(int(t) / 1000.0, 1)
    for t in glob.glob('/sys/class/thermal/thermal_zone*/temp'):
        v = leer(t)
        if v: return round(int(v) / 1000.0, 1)
    return None

def bateria():
    for b in glob.glob('/sys/class/power_supply/BAT*'):
        cap = int(leer(b + '/capacity', '0')); est = leer(b + '/status')
        try:
            pw = int(leer(b + '/power_now', '0')); en = int(leer(b + '/energy_now', '0')); ef = int(leer(b + '/energy_full', '0'))
            if pw > 0:
                horas = (en / pw) if est == 'Discharging' else ((ef - en) / pw if est == 'Charging' else 0)
                minutos = int(horas * 60)
            else: minutos = 0
            watts = round(pw / 1e6, 1)
        except Exception: minutos, watts = 0, 0
        return dict(pct=cap, estado=est, min=minutos, w=watts)
    return None

_BIN_CACHE = {}


def _which(cmd):
    if cmd not in _BIN_CACHE:
        _BIN_CACHE[cmd] = shutil.which(cmd)
    return _BIN_CACHE[cmd]


def _default_route_proc():
    try:
        with open('/proc/net/route') as f:
            next(f, None)
            for line in f:
                cols = line.split()
                if len(cols) >= 3 and cols[1] == '00000000':
                    iface = cols[0]
                    gw_hex = cols[2]
                    gw = None
                    if len(gw_hex) == 8 and gw_hex != '00000000':
                        b = bytes.fromhex(gw_hex)
                        gw = f'{b[3]}.{b[2]}.{b[1]}.{b[0]}'
                    return iface, gw
    except Exception:
        pass
    return None, None


def red(e):
    ahora = time.time()
    iface, gw = _default_route_proc()
    if iface is None:
        r = sh(['ip', '-o', 'route', 'show', 'default'])
        m = re.search(r'dev (\S+)', r)
        iface = m.group(1) if m else None
        mg = re.search(r'via (\S+)', r)
        gw = mg.group(1) if mg else None

    meta = e.get('net_meta')
    if not meta or meta.get('iface') != iface or ahora - meta.get('t', 0) >= 20:
        ip = None
        ssid = None
        senal = None
        vpn = dict(on=False, iface=None, ip=None)
        if iface:
            a = sh(['ip', '-o', '-4', 'addr', 'show', iface])
            m = re.search(r'inet (\S+?)/', a)
            ip = m.group(1) if m else None
            if os.path.exists(f'/sys/class/net/{iface}/wireless'):
                if _which('iw'):
                    l = sh(['iw', 'dev', iface, 'link'])
                    m = re.search(r'SSID: (.+)', l)
                    ssid = m.group(1).strip() if m else None
                    m = re.search(r'signal: (-?\d+) dBm', l)
                    if m:
                        senal = max(0, min(100, 2 * (int(m.group(1)) + 100)))
                else:
                    for l in sh(['nmcli', '-t', '-f', 'IN-USE,SIGNAL,SSID', 'dev', 'wifi', 'list', 'ifname', iface, '--rescan', 'no']).splitlines():
                        if l.startswith('*:'):
                            _, sen, ss = l.split(':', 2)
                            ssid = ss.replace('\\:', ':') or None
                            senal = int(sen) if sen.isdigit() else None
                            break
        for v in sorted(os.listdir('/sys/class/net')):
            if re.match(r'(tailscale|tun|wg|proton|nordlynx|vpn)', v) and leer(f'/sys/class/net/{v}/operstate') != 'down':
                a = sh(['ip', '-o', '-4', 'addr', 'show', v])
                m = re.search(r'inet (\S+?)/', a)
                vpn = dict(on=True, iface=v, ip=m.group(1) if m else None)
                break
        meta = dict(t=ahora, iface=iface, ip=ip, ssid=ssid, senal=senal, vpn=vpn)
        e['net_meta'] = meta

    out = dict(iface=iface, ip=meta['ip'], ssid=meta['ssid'], senal=meta['senal'], rx=0, tx=0, gw=gw, vpn=meta['vpn'])
    if iface:
        try:
            rx = int(leer(f'/sys/class/net/{iface}/statistics/rx_bytes', '0'))
            tx = int(leer(f'/sys/class/net/{iface}/statistics/tx_bytes', '0'))
            ant = e.get('net')
            if ant and ant[0] == iface and ahora > ant[3]:
                dt = ahora - ant[3]
                out['rx'] = max(0, int((rx - ant[1]) / dt))
                out['tx'] = max(0, int((tx - ant[2]) / dt))
            e['net'] = [iface, rx, tx, ahora]
        except Exception:
            pass
    return out


def _nvidia_suspendida():
    for dev in glob.glob('/sys/bus/pci/devices/*'):
        if leer(dev + '/vendor') == '0x10de':
            cls = leer(dev + '/class')
            if cls.startswith('0x03'):
                if leer(dev + '/power/runtime_status') == 'suspended':
                    return True
    return False


def gpu_info(e):
    """Detecta GPU (NVIDIA, AMD DRM o lspci) sin bloquear ni despertar GPU suspendida."""
    ahora = time.time()
    if _which('nvidia-smi') and not _nvidia_suspendida():
        nv_t = e.get('nv_t', 0)
        if e.get('nv_d') and ahora - nv_t < 8:
            return e['nv_d']
        out = sh(['nvidia-smi', '--query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'], 2)
        if out.strip():
            p = [x.strip() for x in out.splitlines()[0].split(',')]
            if len(p) >= 5:
                try:
                    nv_d = dict(nombre=p[0], uso=int(float(p[1])), temp=int(float(p[2])), vram_u=int(float(p[3])), vram_t=int(float(p[4])))
                    e['nv_t'] = ahora
                    e['nv_d'] = nv_d
                    return nv_d
                except Exception:
                    pass
    nombre = e.get('gpu_nombre')
    if not nombre and _which('lspci'):
        for l in sh(['lspci'], 2).splitlines():
            if any(k in l for k in ('VGA compatible controller', '3D controller', 'Display controller')):
                cand = (l.split(':', 2)[-1] if l.count(':') >= 2 else l).strip()
                cand = re.sub(r'\s*\(rev [^)]+\)$', '', cand)
                cand = re.sub(r'\[[^\]]+\]\s*', '', cand).strip()
                if cand:
                    nombre = cand[:36]
                    e['gpu_nombre'] = nombre
                    break
    uso = None
    temp = None
    vram_u = None
    vram_t = None
    for card in sorted(glob.glob('/sys/class/drm/card[0-9]/device')):
        busy = leer(card + '/gpu_busy_percent')
        if busy.isdigit():
            uso = int(busy)
        vu = leer(card + '/mem_info_vram_used')
        vt = leer(card + '/mem_info_vram_total')
        if vu.isdigit() and vt.isdigit() and int(vt) > 0:
            vram_u = int(int(vu) / 1048576)
            vram_t = int(int(vt) / 1048576)
        for hm in glob.glob(card + '/hwmon/hwmon*/temp1_input'):
            tv = leer(hm)
            if tv.isdigit():
                temp = round(int(tv) / 1000.0)
                break
        if uso is not None:
            break
    return dict(nombre=nombre or 'GPU LINUX', uso=uso, temp=temp, vram_u=vram_u, vram_t=vram_t)


def rapido(e=None, secciones=None):
    persist = e is None
    if persist:
        e = carga_estado()
    ahora = time.time()
    want_sis = not secciones or ('sistema' in secciones)
    want_gpu = not secciones or ('gpu' in secciones)
    want_red = not secciones or ('red' in secciones)

    top = e.get('top', [])
    if want_sis:
        if not e.get('top_t') or ahora - e['top_t'] >= 6:
            top = []
            for l in sh(['ps', '-eo', 'comm,%cpu', '--sort=-%cpu', '--no-headers'], 2).splitlines()[:6]:
                p = l.rsplit(None, 1)
                if len(p) == 2 and p[0] not in ('ps', 'python3') and len(top) < 3:
                    top.append([p[0], float(p[1])])
            e['top'] = top
            e['top_t'] = ahora
        du = shutil.disk_usage('/')
        cpu = cpu_pct(e)
        ram = memoria()
        temp = temperatura()
        bat = bateria()
        load = [float(x) for x in leer('/proc/loadavg').split()[:3]]
        up = int(float(leer('/proc/uptime', '0').split()[0]))
        disco = round(100.0 * du.used / du.total, 1)
        libre = round(du.free / 2 ** 30)
        nuc = os.cpu_count()
    else:
        cpu = 0.0
        ram = dict(pct=0, usado=0, total=0, swap=0)
        temp = None
        bat = None
        load = [0.0, 0.0, 0.0]
        up = 0
        disco = 0.0
        libre = 0
        nuc = os.cpu_count()

    if want_gpu:
        g = gpu_info(e)
        if g.get('uso') is None:
            if not want_sis:
                cpu = cpu_pct(e)
            g['uso'] = max(2, min(95, round(cpu * 0.55 + 4)))
    else:
        g = {}

    net_d = red(e) if want_red else dict(iface=None, ip=None, ssid=None, senal=None, rx=0, tx=0, gw=None, vpn=dict(on=False, iface=None, ip=None))

    d = dict(t=int(ahora), cpu=cpu, ram=ram, temp=temp, bat=bat, net=net_d, gpu=g,
             load=load, up=up, disco=disco, libre=libre, top=top, nuc=nuc)
    if persist:
        guarda_estado(e)
    return d

# ----------------------------------------------------------------- lento
PUERTOS = {22: 'ssh', 53: 'dns', 80: 'http', 443: 'https', 631: 'cups', 3000: 'dev', 3306: 'mysql', 5000: 'dev', 5173: 'vite', 5432: 'pg',
           6379: 'redis', 8000: 'dev', 8080: 'http', 8888: 'jupyter', 9090: 'prom', 27017: 'mongo', 1716: 'kdeconn', 5900: 'vnc'}
def puertos():
    vistos = {}
    for l in sh(['ss', '-tlnpH']).splitlines():
        c = l.split()
        if len(c) < 5: continue
        m = re.search(r':(\d+)$', c[3]);
        if not m: continue
        p = int(m.group(1)); host = c[3].rsplit(':', 1)[0]
        pr = re.search(r'\(\("([^"]+)"', l)
        loc = host in ('127.0.0.1', '[::1]', '127.0.0.53%lo', '127.0.0.54')
        if p not in vistos: vistos[p] = dict(p=p, n=(pr.group(1) if pr else PUERTOS.get(p, '')), local=loc)
        elif not loc: vistos[p]['local'] = False
    return sorted(vistos.values(), key=lambda x: x['p'])[:24]

def repos(e):
    ahora = time.time()
    if e.get('repos_t', 0) < ahora - 600:
        raices = [os.path.expanduser(p) for p in ('~/proyectos', '~/dev', '~/code', '~/src', '~/projects', '~/workspace', '~/git', '~/Documentos', '~/Obsidian', '~/Escritorio')]
        encontrados = []
        for r in raices:
            if not os.path.isdir(r): continue
            for dp, dn, _ in os.walk(r):
                if dp[len(r):].count(os.sep) >= 3: dn[:] = []; continue
                if '.git' in dn: encontrados.append(dp); dn[:] = []
                else: dn[:] = [x for x in dn if not x.startswith('.') and x not in ('node_modules', 'venv', '.venv', 'target')]
        e['repos_l'] = encontrados[:8]; e['repos_t'] = ahora
    out = []
    for r in e.get('repos_l', []):
        b = sh(['git', '-C', r, 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        if not b: continue
        st = sh(['git', '-C', r, 'status', '--porcelain']).splitlines()
        ab = sh(['git', '-C', r, 'rev-list', '--left-right', '--count', '@{u}...HEAD']).split()
        out.append(dict(n=os.path.basename(r), b=b, sucio=len(st), atras=int(ab[0]) if len(ab) == 2 else 0, adelante=int(ab[1]) if len(ab) == 2 else 0))
    return out[:3]

def version(cmd, args=('--version',)):
    if not shutil.which(cmd): return None
    o = sh([cmd, *args], 2).strip() or ''
    m = re.search(r'(\d+\.\d+(?:\.\d+)?)', o); return m.group(1) if m else '?'

def edad_pacman():
    """Horas desde la ultima sincronizacion de paquetes (pacman en Arch, apt en Debian/Ubuntu)."""
    for f in ('/var/lib/pacman/sync/core.db', '/var/lib/apt/periodic/update-success-stamp', '/var/lib/apt/lists'):
        try: return int((time.time() - os.path.getmtime(f)) / 3600)
        except Exception: pass
    return None

def lento(e=None, secciones=None):
    persist = e is None
    if persist:
        e = carga_estado()
    ahora = time.time()
    want_red = not secciones or ('red' in secciones)
    want_dev = not secciones or ('dev' in secciones)

    if want_dev:
        fallos = len([l for l in sh(['systemctl', '--failed', '--no-legend', '--plain'], 3).splitlines() if l.strip()])
        fallos += len([l for l in sh(['systemctl', '--user', '--failed', '--no-legend', '--plain'], 3).splitlines() if l.strip()])
        errores = len([l for l in sh(['journalctl', '-p', '3', '-S', '-1h', '--no-pager', '-q'], 4).splitlines() if l.strip()])
        if e.get('tc_t', 0) < ahora - 600:
            e['tc'] = dict(py=version('python3'), node=version('node'), go=version('go', ('version',)), rust=version('rustc'), docker=version('docker'))
            e['tools'] = {t: bool(_which(t)) for t in ('btop', 'fastfetch', 'nmap', 'wireshark', 'tcpdump', 'docker', 'podman', 'dig', 'mtr', 'ncat', 'git', 'ranger', 'yazi')}
            e['tc_t'] = ahora
        tc = e['tc']
        tools = e['tools']
        repos_l = repos(e)
        pac_h = edad_pacman()
    else:
        fallos, errores, tc, tools, repos_l, pac_h = 0, 0, {}, {}, [], None

    if want_red:
        pt = puertos()
        est = len(sh(['ss', '-tnH', 'state', 'established']).splitlines())
        vecinos = len([l for l in sh(['ip', 'neigh']).splitlines() if 'REACHABLE' in l or 'STALE' in l or 'DELAY' in l])
        dns = re.search(r'nameserver (\S+)', leer('/etc/resolv.conf'))
        dns_s = dns.group(1) if dns else None
    else:
        pt, est, vecinos, dns_s = [], 0, 0, None

    d = dict(puertos=pt, est=est, vecinos=vecinos, dns=dns_s, repos=repos_l, fallos=fallos, errores=errores,
             tc=tc, tools=tools, pacman_h=pac_h, kernel=os.uname().release.split('-')[0], host=os.uname().nodename)
    if persist:
        guarda_estado(e)
    return d

DEMO = os.path.exists(os.path.expanduser('~/.config/pixelzen/demo'))
def anonimiza(d, modo):
    """Con el fichero ~/.config/pixelzen/demo los datos personales se sustituyen por otros ficticios (para capturas)."""
    if modo == 'rapido':
        n = d['net']; n['ssid'] = 'MiWiFi' if n.get('ssid') else None; n['ip'] = '192.168.1.42' if n.get('ip') else None; n['gw'] = '192.168.1.1' if n.get('gw') else None
        if n['vpn'].get('on'): n['vpn']['ip'] = '100.64.0.7'
    else:
        d['host'] = 'pixelzen'; d['dns'] = '1.1.1.1'
        d['repos'] = [dict(n='pixelzen', b='main', sucio=2, atras=0, adelante=1), dict(n='blog', b='dev', sucio=0, atras=0, adelante=0)]
    return d


def _ejecuta_cmd(cmd_str, state):
    parts = cmd_str.strip().split(':', 1)
    modo = parts[0] or 'rapido'
    secc = set(parts[1].split(',')) if len(parts) > 1 and parts[1] else None
    r = lento(state, secc) if modo == 'lento' else rapido(state, secc)
    return json.dumps(anonimiza(r, modo) if DEMO else r, ensure_ascii=False)


if __name__ == '__main__':
    modo = sys.argv[1] if len(sys.argv) > 1 else 'rapido'
    if modo == 'worker':
        state = carga_estado()
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                sys.stdout.write(_ejecuta_cmd(line, state) + '\n')
                sys.stdout.flush()
            except Exception as exc:
                sys.stdout.write(json.dumps({'error': str(exc)}) + '\n')
                sys.stdout.flush()
        guarda_estado(state)
    else:
        secc = set(sys.argv[3].split(',')) if len(sys.argv) > 3 and sys.argv[3] else None
        r = lento(None, secc) if modo == 'lento' else rapido(None, secc)
        print(json.dumps(anonimiza(r, modo) if DEMO else r, ensure_ascii=False))
