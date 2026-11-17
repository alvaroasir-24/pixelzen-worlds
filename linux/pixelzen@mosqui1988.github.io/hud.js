// PixelZen para GNOME - panel de datos (HUD) con 9 tarjetas, paleta por mundo y 2 columnas adaptativas.
import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import St from 'gi://St';
import Pango from 'gi://Pango';
import PangoCairo from 'gi://PangoCairo';

const COL_W = 300;
const COL_GAP = 8;
const PAL_BASE = {
    bg: '#0b1020', bg2: '#121a30', track: '#1c2844', line: '#2f4266', border: '#7d6540',
    text: '#f3ead6', dim: '#a8b8cf', faint: '#687a96', red: '#d6a34a', hot: '#e0584e',
    rosa: '#54ded4', flor: '#e6c06e', amber: '#e6b45a', green: '#72c48c', cyan: '#66dce0',
};
const WORLD_THEMES = {
    'fittoa': ['#7D6540', '#E6C06E', '#54DED4'],
    'continente-demoniaco': ['#7F3F2B', '#FF7854', '#F4A261'],
    'hunter-x-hunter': ['#3A6F4F', '#72C48C', '#F3C65F'],
    'black-clover': ['#61448A', '#B888FF', '#EF4444'],
    'spiderman-miles-morales': ['#8B2240', '#F43F5E', '#38BDF8'],
    'solo-leveling': ['#602C94', '#A855F7', '#38BDF8'],
    'demon-slayer': ['#8A4A22', '#FB923C', '#22D3EE'],
    'stranger-things': ['#8A2424', '#EF4444', '#A855F7'],
    'harry-potter': ['#7B6020', '#EAB308', '#38BDF8'],
    'naruto': ['#8E5120', '#FF9B38', '#38BDF8'],
    'jujutsu-kaisen': ['#881337', '#E11D48', '#C084FC'],
    'attack-on-titan': ['#7C2D12', '#F97316', '#22C55E'],
    'one-piece': ['#881337', '#F43F5E', '#FACC15'],
    'dragon-ball-z': ['#075985', '#38BDF8', '#FACC15'],
    'cyberpunk-edgerunners': ['#713F12', '#FACC15', '#22D3EE'],
};
const WORLD_AUDIO = {
    'fittoa': ['Lullaby of Fittoa · OST', '84 BPM · ACOUSTIC LO-FI'],
    'continente-demoniaco': ['Rikarisu Wasteland · OST', '92 BPM · SYNTH AMBIENT'],
    'hunter-x-hunter': ['Departure! (Acoustic)', '96 BPM · GUITARRA LO-FI'],
    'black-clover': ['Haruka Mirai (Piano)', '108 BPM · ORQUESTA'],
    'spiderman-miles-morales': ['Sunflower · Brooklyn Mix', '90 BPM · BOOM-BAP LO-FI'],
    'solo-leveling': ['DARK ARIA <LV2> · Sawano', '116 BPM · SINFÓNICO'],
    'demon-slayer': ['Kamado Tanjiro no Uta', '78 BPM · SHAKUHACHI'],
    'stranger-things': ["Kids / Synthwave '83", '104 BPM · ANALÓGICO'],
    'harry-potter': ["Hedwig's Theme · Celesta", '88 BPM · CELESTA'],
    'naruto': ['Silhouette · Baryon OST', '132 BPM · TAIKO & SHAMISEN'],
    'jujutsu-kaisen': ['Kaikai Kitan · Domain OST', '128 BPM · CURSED SYNTH'],
    'attack-on-titan': ['Atæk on Titan · Sawano OST', '138 BPM · CORO ÉPICO'],
    'one-piece': ['Drums of Liberation · Nika', '126 BPM · TAMBORES'],
    'dragon-ball-z': ['Ultimate Battle · UI OST', '145 BPM · ROCK SINFÓNICO'],
    'cyberpunk-edgerunners': ['I Really Want to Stay · OST', '124 BPM · SYNTHWAVE'],
};
const MONO = 'Departure Mono';
const DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
const CITAS_DEFECTO = [
    {sub: 'K407 · Aldea de Buena', es: '«Daré todo de mí en este mundo, sin arrepentimientos.»', au: 'Rudeus'},
];

const p2 = n => (n < 10 ? '0' : '') + n;
const tasa = b => b >= 1048576 ? (b / 1048576).toFixed(1) + 'M' : b >= 1024 ? Math.round(b / 1024) + 'K' : b + 'B';
const horas = m => m > 0 ? Math.floor(m / 60) + 'h' + p2(m % 60) : '--';
const fmtSeg = s => {
    const t = Math.max(0, Math.floor(s || 0));
    const m = Math.floor(t / 60), r = t % 60;
    return `${m}:${p2(r)}`;
};
function durac(s) {
    const dd = Math.floor(s / 86400), hh = Math.floor(s % 86400 / 3600), mm = Math.floor(s % 3600 / 60);
    return dd > 0 ? dd + 'd' + hh + 'h' : hh + 'h' + p2(mm);
}
function luna() {
    const syn = 29.530588853, ref = Date.UTC(2000, 0, 6, 18, 14) / 86400000;
    const age = (((Date.now() / 86400000 - ref) % syn) + syn) % syn;
    return {age, p: age / syn};
}
function calcSol(fecha, lat = 40.4, lon = -3.7) {
    const rad = Math.PI / 180;
    const n = fecha.getTime() / 86400000 + 2440587.5 - 2451545.0;
    const L = (280.460 + 0.9856474 * n) % 360;
    const g = ((357.528 + 0.9856003 * n) % 360) * rad;
    const lam = (L + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g)) * rad;
    const eps = (23.439 - 0.0000004 * n) * rad;
    const ra = Math.atan2(Math.cos(eps) * Math.sin(lam), Math.cos(lam));
    const dec = Math.asin(Math.sin(eps) * Math.sin(lam));
    const gmst = (18.697374558 + 24.06570982441908 * n) % 24;
    let Hh = (gmst * 15 + lon) * rad - ra;
    Hh = Math.atan2(Math.sin(Hh), Math.cos(Hh));
    const phi = lat * rad;
    const e = Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(Hh));
    const A = Math.atan2(Math.sin(Hh), Math.cos(Hh) * Math.sin(phi) - Math.tan(dec) * Math.cos(phi)) + Math.PI;
    return {e: e / rad, az: ((A / rad) % 360 + 360) % 360};
}
function rgb(hex) {
    const h = hex.replace('#', '');
    return [parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255];
}

export class Hud {
    constructor(dir, settings = null) {
        this._dir = dir;
        this._settings = settings;
        this._script = `${dir}/code/datos.py`;
        this._climaScript = `${dir}/code/clima.py`;
        this.d = {cpu: 0, ram: {pct: 0, usado: 0, total: 0}, temp: 0, bat: null, net: {vpn: {}}, gpu: {}, load: [0, 0, 0], up: 0, disco: 0, top: [], nuc: 0};
        this.s = {puertos: [], repos: [], tc: {}, tools: {}, fallos: 0, errores: 0, est: 0, vecinos: 0};
        this.clima = null;
        this.media = {ok: false, app: '', playing: false, title: '', artist: '', posSec: 0, durSec: 0, polledAt: Date.now()};
        this.lat = 40.4;
        this.lon = -3.7;
        this.monW = 1920;
        this.monH = 1080;
        this.sessionStart = Date.now();
        this.cpuH = [];
        this.rxH = [];
        this.citas = CITAS_DEFECTO;
        this.eraSub = 'Era del Dragón Acorazado';
        this.recargaTema();
        this.hk = Math.floor(Date.now() / 90000) % this.citas.length;
        this.hkOp = 1;
        this._ocupado = {};
        this._timers = [];
        this._cancel = new Gio.Cancellable();
        this._fuentes = new Map();
        this._rgbCache = new Map();
        this._lastArea = null;
        this._lastAltoDisp = 900;
        this._pausa = false;
        this._workerProc = null;
        this._workerOut = null;
        this._workerIn = null;
        this._workerQueue = [];
        this._workerBusy = false;
        this._moonKey = -1;
        this._moonCells = null;

        this.actor = new St.DrawingArea({reactive: false});
        this.actor.connect('repaint', a => this._pinta(a));

        this._iniciaTimers();
        this._lanza('rapido'); this._lanza('lento');
        this._lanzaClima();
        this._lanzaMedia();
    }

    _ver(k) {
        if (!this._settings) return true;
        try { return this._settings.get_boolean(k); } catch (_e) { return true; }
    }

    _seccionesRapido() {
        const s = [];
        if (this._ver('hud-sistema')) s.push('sistema');
        if (this._ver('hud-gpu')) s.push('gpu');
        if (this._ver('hud-red')) s.push('red');
        return s;
    }

    _seccionesLento() {
        const s = [];
        if (this._ver('hud-red')) s.push('red');
        if (this._ver('hud-dev')) s.push('dev');
        return s;
    }

    _necesitaTick1s() {
        if (this._ver('hud-tiempo') || this._ver('hud-foco')) return true;
        return Boolean(this._ver('hud-audio') && this.media?.ok && this.media.playing && this.media.durSec > 0);
    }

    _iniciaTimers() {
        this._paraTimers();
        if (this._pausa) return;
        let secCnt = 0;
        this._cada(3000, () => this._lanza('rapido'));
        this._cada(4000, () => this._lanzaMedia());
        this._cada(30000, () => this._lanza('lento'));
        this._cada(900000, () => this._lanzaClima());
        this._cada(1000, () => {
            secCnt++;
            if (this._necesitaTick1s() || secCnt % 60 === 0) {
                this.actor.queue_repaint();
            }
        });
        this._cada(90000, () => {
            if (this._ver('hud-grimorio') && !this._ver('solo-widgets')) this._cambiaHaiku();
        });
    }

    _paraTimers() {
        for (const t of this._timers) GLib.source_remove(t);
        this._timers = [];
    }

    pausa(p) {
        const np = !!p;
        if (np === this._pausa) return;
        this._pausa = np;
        if (np) {
            this._paraTimers();
        } else {
            this._iniciaTimers();
            this._lanza('rapido');
            this._lanzaMedia();
            this.actor?.queue_repaint();
        }
    }

    ajustesCambiados() {
        if (!this._pausa) {
            this._lanza('rapido');
            this._lanza('lento');
            this._lanzaMedia();
        }
    }

    ponUbicacion(lat, lon) {
        if (typeof lat === 'number' && typeof lon === 'number') {
            this.lat = lat;
            this.lon = lon;
        }
    }

    recargaTema() {
        try {
            const id = this._settings?.get_string('tema') || 'fittoa';
            const sub = id ? `${this._dir}/temas/${id}/tema.json` : '';
            const ruta = (sub && GLib.file_test(sub, GLib.FileTest.EXISTS)) ? sub : `${this._dir}/tema.json`;
            const raw = JSON.parse(new TextDecoder().decode(GLib.file_get_contents(ruta)[1]));
            this.citas = (raw.citas && raw.citas.length) ? raw.citas : CITAS_DEFECTO;
            this.eraSub = raw.nombre ?? 'Era del Dragón Acorazado';
            this.hk = this.hk % this.citas.length;
        } catch (_e) {
            this.citas = CITAS_DEFECTO;
        }
        if (this._lastArea) this.coloca(this._lastArea);
        else this.actor?.queue_repaint();
    }

    _paleta() {
        const s = this._settings;
        const soloW = s ? s.get_boolean('solo-widgets') : false;
        if (soloW) {
            return {...PAL_BASE, border: '#3B5278', flor: '#7CF6EE', rosa: '#54DED4'};
        }
        const tid = s?.get_string('tema') || 'fittoa';
        const wt = WORLD_THEMES[tid] || WORLD_THEMES.fittoa;
        return {...PAL_BASE, border: wt[0], flor: wt[1], rosa: wt[2]};
    }

    _tarjetasActivas() {
        const s = this._settings;
        const ver = k => {
            if (!s) return true;
            try { return s.get_boolean(k); } catch (_e) { return true; }
        };
        const soloW = ver('solo-widgets');
        const comp = ver('hud-compacto');
        const gap = comp ? 6 : 9;
        const repos = this.s?.repos ?? [];
        const hDev = (comp ? 86 : 98) + Math.max(0, repos.length - 1) * 16;
        const hasBat = Boolean(this.d?.bat);
        const hSistema = hasBat ? (comp ? 152 : 158) : (comp ? 135 : 140);
        const maxCita = Math.max(0, ...(this.citas ?? []).map(c => (c.es ?? '').length));
        const hGrimorio = maxCita > 110
            ? (comp ? 114 : 120)
            : maxCita > 74
                ? (comp ? 100 : 106)
                : (comp ? 88 : 94);

        const defs = [
            {id: 'tiempo', on: ver('hud-tiempo'), h: comp ? 104 : 114},
            {id: 'clima', on: ver('hud-clima'), h: comp ? 76 : 84},
            {id: 'sistema', on: ver('hud-sistema'), h: hSistema},
            {id: 'gpu', on: ver('hud-gpu'), h: comp ? 90 : 96},
            {id: 'red', on: ver('hud-red'), h: comp ? 172 : 188},
            {id: 'audio', on: ver('hud-audio'), h: comp ? 90 : 96},
            {id: 'dev', on: ver('hud-dev'), h: hDev},
            {id: 'foco', on: ver('hud-foco'), h: comp ? 74 : 82},
            {id: 'grimorio', on: ver('hud-grimorio') && !soloW, h: hGrimorio},
        ];
        const activas = defs.filter(c => c.on);
        return {activas, gap, comp};
    }

    _layoutColumnas(altoDisp = this._lastAltoDisp || 900) {
        const {activas, gap} = this._tarjetasActivas();
        if (!activas.length) {
            return {cols: [[{id: 'tiempo', h: 114}]], totalW: COL_W, totalH: 120, gap};
        }
        const totalH1 = activas.reduce((acc, c, idx) => acc + c.h + (idx > 0 ? gap : 0), 0);
        // Mantener 1 columna en el lateral derecho mientras quepa con escala legible (>= 0.72)
        if (activas.length <= 5 || altoDisp / totalH1 >= 0.72) {
            return {cols: [activas], totalW: COL_W, totalH: totalH1, gap};
        }
        // Solo usar 2 columnas si la altura útil es demasiado baja para una sola columna
        const col1 = [], col2 = [];
        let h1 = 0, h2 = 0;
        for (const c of activas) {
            if (h1 <= h2) {
                col1.push(c);
                h1 += c.h + (col1.length > 1 ? gap : 0);
            } else {
                col2.push(c);
                h2 += c.h + (col2.length > 1 ? gap : 0);
            }
        }
        return {cols: [col1, col2], totalW: COL_W * 2 + COL_GAP, totalH: Math.max(h1, h2), gap};
    }

    coloca(area, mon = null) {
        this._lastArea = area;
        if (mon) {
            this.monW = mon.width || this.monW;
            this.monH = mon.height || this.monH;
        }
        const margen = 20;
        const altoDisp = Math.max(200, area.height - 2 * margen);
        this._lastAltoDisp = altoDisp;
        const lay = this._layoutColumnas(altoDisp);
        // Limitar el ancho del HUD al lateral derecho de la pantalla (máx. 26% del ancho útil)
        const anchoMax = Math.max(240, Math.min(area.width - 2 * margen, Math.round(area.width * 0.26)));
        this.k = Math.max(0.55, Math.min(1.0, Math.min(altoDisp / lay.totalH, anchoMax / lay.totalW)));
        const w = Math.round(lay.totalW * this.k);
        const h = Math.round(lay.totalH * this.k);
        this.actor.set_size(w, h);
        this.actor.set_position(area.x + area.width - w - margen, area.y + margen);
        this.actor.queue_repaint();
    }

    _cada(ms, fn) {
        this._timers.push(GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => { fn(); return GLib.SOURCE_CONTINUE; }));
    }

    _aseguraWorker() {
        if (this._workerProc) return true;
        try {
            const proc = Gio.Subprocess.new(
                ['python3', '-I', this._script, 'worker', 'gnome'],
                Gio.SubprocessFlags.STDIN_PIPE | Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE
            );
            this._workerProc = proc;
            this._workerIn = new Gio.DataOutputStream({base_stream: proc.get_stdin_pipe()});
            this._workerOut = new Gio.DataInputStream({base_stream: proc.get_stdout_pipe()});
            this._workerBusy = false;
            proc.wait_async(this._cancel, () => {
                if (this._workerProc === proc) {
                    this._workerProc = null;
                    this._workerIn = null;
                    this._workerOut = null;
                    this._workerBusy = false;
                    this._workerQueue = [];
                    this._ocupado.rapido = false;
                    this._ocupado.lento = false;
                }
            });
            return true;
        } catch (_e) {
            this._workerProc = null;
            return false;
        }
    }

    _bombeaWorker() {
        if (this._workerBusy || !this._workerQueue.length) return;
        if (!this._aseguraWorker()) {
            while (this._workerQueue.length) {
                const it = this._workerQueue.shift();
                this._ocupado[it.modo] = false;
            }
            return;
        }
        const item = this._workerQueue.shift();
        this._workerBusy = true;
        try {
            const cmd = item.secc ? `${item.modo}:${item.secc}\n` : `${item.modo}\n`;
            this._workerIn.put_string(cmd, this._cancel);
            this._workerOut.read_line_async(GLib.PRIORITY_DEFAULT, this._cancel, (stream, res) => {
                this._workerBusy = false;
                this._ocupado[item.modo] = false;
                try {
                    const [line] = stream.read_line_finish_utf8(res);
                    if (line === null) {
                        this._cierraWorker();
                    } else {
                        const j = JSON.parse(line);
                        if (j && !j.error) {
                            this._aplicaDatos(item.modo, j);
                        }
                    }
                } catch (_e) {
                    this._cierraWorker();
                }
                this._bombeaWorker();
            });
        } catch (_e) {
            this._workerBusy = false;
            this._ocupado[item.modo] = false;
            this._cierraWorker();
        }
    }

    _cierraWorker() {
        try { this._workerIn?.close(null); } catch (_e) {}
        try { this._workerOut?.close(null); } catch (_e) {}
        try { this._workerProc?.force_exit(); } catch (_e) {}
        this._workerProc = null;
        this._workerIn = null;
        this._workerOut = null;
        this._workerBusy = false;
        this._workerQueue = [];
    }

    _aplicaDatos(modo, j) {
        if (modo === 'rapido') {
            const hadBat = Boolean(this.d?.bat);
            this.d = j;
            this.cpuH = this._push(this.cpuH, j.cpu ?? 0, 120);
            this.rxH = this._push(this.rxH, j.net?.rx ?? 0, 120);
            if (Boolean(j?.bat) !== hadBat && this._lastArea) this.coloca(this._lastArea);
        } else {
            this.s = j;
            if (this._lastArea) this.coloca(this._lastArea);
        }
        this.actor.queue_repaint();
    }

    _lanza(modo) {
        if (this._pausa || this._ocupado[modo]) return;
        const seccList = modo === 'rapido' ? this._seccionesRapido() : this._seccionesLento();
        if (!seccList.length) return;
        this._ocupado[modo] = true;
        this._workerQueue.push({modo, secc: seccList.join(',')});
        this._bombeaWorker();
    }

    _lanzaClima() {
        const clModo = (() => { try { return this._settings?.get_string('clima') || 'normal'; } catch (_e) { return 'normal'; } })();
        if (!this._ver('hud-clima') && clModo !== 'auto') return;
        if (this._ocupado.clima || !GLib.file_test(this._climaScript, GLib.FileTest.EXISTS)) return;
        this._ocupado.clima = true;
        try {
            const proc = Gio.Subprocess.new(['python3', this._climaScript],
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE);
            proc.communicate_utf8_async(null, this._cancel, (p, res) => {
                this._ocupado.clima = false;
                try {
                    const [, out] = p.communicate_utf8_finish(res);
                    const j = JSON.parse(out);
                    if (j && typeof j === 'object') {
                        this.clima = j;
                        if (j.lat && j.lon) {
                            this.lat = Number(j.lat);
                            this.lon = Number(j.lon);
                        }
                        this.actor.queue_repaint();
                    }
                } catch (_e) { /* sin red */ }
            });
        } catch (_e) {
            this._ocupado.clima = false;
        }
    }

    _lanzaMedia() {
        if (this._pausa || !this._ver('hud-audio') || this._ocupado.media) return;
        this._ocupado.media = true;
        Gio.DBus.session.call(
            'org.freedesktop.DBus', '/org/freedesktop/DBus', 'org.freedesktop.DBus', 'ListNames',
            null, new GLib.VariantType('(as)'), Gio.DBusCallFlags.NONE, 800, this._cancel,
            (conn, res) => {
                try {
                    const val = conn.call_finish(res);
                    const names = val.deep_unpack()[0].filter(n => n.startsWith('org.mpris.MediaPlayer2.'));
                    if (!names.length) {
                        this._ocupado.media = false;
                        this.media = {ok: false};
                        return;
                    }
                    // Priorizar Spotify o el primer reproductor
                    names.sort((a, b) => (a.includes('spotify') ? -1 : b.includes('spotify') ? 1 : 0));
                    this._leeMpris(names, 0, null);
                } catch (_e) {
                    this._ocupado.media = false;
                    this.media = {ok: false};
                }
            }
        );
    }

    _leeMpris(names, idx, mejor) {
        if (idx >= names.length) {
            this._ocupado.media = false;
            this.media = mejor || {ok: false};
            return;
        }
        const busName = names[idx];
        Gio.DBus.session.call(
            busName, '/org/mpris/MediaPlayer2', 'org.freedesktop.DBus.Properties', 'GetAll',
            new GLib.Variant('(s)', ['org.mpris.MediaPlayer2.Player']),
            new GLib.VariantType('(a{sv})'), Gio.DBusCallFlags.NONE, 700, this._cancel,
            (conn, res) => {
                let sigMejor = mejor;
                try {
                    const props = conn.call_finish(res).deep_unpack()[0];
                    const status = props.PlaybackStatus ? props.PlaybackStatus.unpack() : 'Stopped';
                    const meta = props.Metadata ? props.Metadata.deep_unpack() : {};
                    const title = meta['xesam:title'] ? String(meta['xesam:title']) : '';
                    const artistRaw = meta['xesam:artist'];
                    const artist = Array.isArray(artistRaw) ? artistRaw.join(', ') : (artistRaw ? String(artistRaw) : '');
                    const lenUs = meta['mpris:length'] ? Number(meta['mpris:length']) : 0;
                    const posUs = props.Position ? Number(props.Position.unpack()) : 0;
                    if (title) {
                        const rawApp = busName.replace('org.mpris.MediaPlayer2.', '').split('.')[0].toUpperCase();
                        const playing = status === 'Playing';
                        const cand = {
                            ok: true, app: rawApp, playing, title, artist,
                            posSec: Math.max(0, posUs / 1e6),
                            durSec: Math.max(0, lenUs / 1e6),
                            polledAt: Date.now(),
                        };
                        if (!sigMejor || (cand.playing && !sigMejor.playing)) sigMejor = cand;
                        if (cand.playing && rawApp.includes('SPOTIFY')) {
                            this._ocupado.media = false;
                            this.media = cand;
                            return;
                        }
                    }
                } catch (_e) { /* siguiente player */ }
                this._leeMpris(names, idx + 1, sigMejor);
            }
        );
    }

    _push(a, v, n) { const b = a.slice(); b.push(v); if (b.length > n) b.shift(); return b; }

    _cambiaHaiku() {
        const pasos = 10;
        let i = 0;
        const id = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 100, () => {
            i++;
            if (i <= 4) this.hkOp = 1 - i / 4;
            else if (i === 5) this.hk = (this.hk + 1) % this.citas.length;
            else this.hkOp = Math.min(1, (i - 4) / 6);
            this.actor.queue_repaint();
            if (i >= pasos) { this._timers = this._timers.filter(t => t !== id); return GLib.SOURCE_REMOVE; }
            return GLib.SOURCE_CONTINUE;
        });
        this._timers.push(id);
    }

    _fuente(fam, px) {
        const k = fam + px;
        if (!this._fuentes.has(k)) {
            const f = Pango.FontDescription.from_string(fam);
            f.set_absolute_size(px * Pango.SCALE);
            this._fuentes.set(k, f);
        }
        return this._fuentes.get(k);
    }
    _col(hex, a = 1) {
        let c = this._rgbCache.get(hex);
        if (!c) { c = rgb(hex); this._rgbCache.set(hex, c); }
        this.cr.setSourceRGBA(c[0], c[1], c[2], a);
    }
    _rect(x, y, w, h, hex, a = 1) { this._col(hex, a); this.cr.rectangle(x, y, w, h); this.cr.fill(); }
    _t(x, y, txt, o = {}) {
        const cr = this.cr;
        const lay = this._pangoLay || PangoCairo.create_layout(cr);
        lay.set_font_description(this._fuente(o.fam ?? MONO, o.px ?? 12));
        if (o.wrap && o.w) {
            lay.set_ellipsize(Pango.EllipsizeMode.NONE);
            lay.set_width(o.w * Pango.SCALE);
            lay.set_wrap(Pango.WrapMode.WORD);
        } else if (o.w && !o.align) {
            lay.set_width(o.w * Pango.SCALE);
            lay.set_ellipsize(Pango.EllipsizeMode.END);
        } else {
            lay.set_width(-1);
            lay.set_ellipsize(Pango.EllipsizeMode.NONE);
        }
        lay.set_text(String(txt), -1);
        const [tw] = lay.get_pixel_size();
        let xx = x;
        if (o.w && o.align === 'right') xx = x + o.w - tw;
        else if (o.w && o.align === 'center') xx = x + (o.w - tw) / 2;
        this._col(o.col ?? this._pal.text, o.a ?? 1);
        cr.moveTo(xx, y);
        PangoCairo.show_layout(cr, lay);
        return tw;
    }
    _etq(x, y, txt) { return this._t(x, y, txt, {px: 10.5, col: this._pal.dim}); }
    _val(x, y, txt, o = {}) { return this._t(x, y, txt, {px: 11.5, ...o}); }
    _pares(x, y, pares, sep = 10) {
        for (const [e, v, col] of pares) {
            x += this._etq(x, y + 1, e) + 5;
            x += this._val(x, y, v, {col}) + sep;
        }
    }
    _segbar(x, y, w, value, {c1, c2, c3, invert = false} = {}) {
        const P = this._pal;
        c1 = c1 ?? P.green; c2 = c2 ?? P.amber; c3 = c3 ?? P.hot;
        const segs = 20, sw = Math.floor((w - (segs - 1) * 2) / segs);
        const on = Math.round(Math.max(0, Math.min(100, value || 0)) / 100 * segs);
        for (let i = 0; i < segs; i++) {
            const f = (i + 1) / segs;
            const c = i < on ? (invert ? (f < 0.2 ? c3 : f < 0.4 ? c2 : c1) : (f < 0.6 ? c1 : f < 0.85 ? c2 : c3)) : P.track;
            this._rect(x + i * (sw + 2), y, sw, 8, c);
        }
    }
    _bar(x, y, w, pct, col) {
        const P = this._pal;
        this._rect(x, y, w, 5, P.track);
        const fw = Math.max(2, Math.round(Math.max(0, Math.min(100, pct || 0)) / 100 * w));
        this._rect(x, y, fw, 5, col ?? P.rosa);
    }
    _spark(x, y, w, h, serie, cols, maxv, col) {
        const P = this._pal;
        const bw = Math.floor((w - cols) / cols);
        for (let i = 0; i < cols; i++) {
            const j = serie.length - cols + i;
            const v = j >= 0 && j < serie.length ? serie[j] : 0;
            const bx = x + i * (bw + 1);
            this._rect(bx, y + h - 1, bw, 1, P.line);
            const bh = Math.max(2, Math.round(Math.min(1, v / maxv) * h));
            this._rect(bx, y + h - bh, bw, bh, col, 0.35 + 0.65 * (i / cols));
        }
    }
    _card(x0, y, h, emblem, title, meta) {
        const P = this._pal;
        const pad = 10, w = COL_W;
        this._rect(x0, y, w, h, P.bg, 0.84);
        this._col(P.border); this.cr.setLineWidth(1); this.cr.rectangle(x0 + 0.5, y + 0.5, w - 1, h - 1); this.cr.stroke();
        this._rect(x0, y, 6, 2, P.flor); this._rect(x0, y, 2, 6, P.flor);
        const kw = this._t(x0 + pad, y + 7, emblem, {px: 12, col: P.rosa});
        this._t(x0 + pad + kw + 6, y + 8, title.split('').join(' '), {px: 10.5, col: P.dim});
        if (meta) this._t(x0 + pad, y + 7, meta, {px: 10.5, col: P.dim, w: w - 2 * pad, align: 'right'});
        for (let x = x0 + pad; x < x0 + w - pad - 2; x += 4) this._rect(x, y + 25, 2, 1, P.line);
        return {x: x0 + pad, y: y + 31, w: w - 2 * pad};
    }

    _pintaTarjeta(id, x0, y, h) {
        const P = this._pal;
        const st = this._settings;
        const now = new Date(), d = this.d, s = this.s, net = d.net ?? {vpn: {}};
        const soloW = st ? st.get_boolean('solo-widgets') : false;

        if (id === 'tiempo') {
            let modoMeta = 'REAL';
            if (soloW) modoMeta = 'SOLO WIDGETS';
            else if (st?.get_boolean('ciclo-rapido')) modoMeta = st.get_int('ciclo-duracion') >= 3600 ? 'CICLO 90M' : 'DEMO 90S';
            else if ((st?.get_double('hora-simulada') ?? -1) >= 0) modoMeta = 'FIJA';

            const b = this._card(x0, y, h, '✦', 'TIEMPO', modoMeta);
            this._t(b.x - 2, b.y - 4, p2(now.getHours()) + ':' + p2(now.getMinutes()), {px: 40});
            this._t(b.x + 132, b.y + 12, p2(now.getSeconds()), {px: 16, col: P.rosa});
            this._t(b.x, b.y + 39, `${DIAS[now.getDay()]} ${now.getDate()} ${MESES[now.getMonth()]} ${now.getFullYear()}`, {px: 11.5});
            this._t(b.x, b.y + 56, soloW ? (s.host ?? 'FONDO EXTERNO') : this.eraSub, {px: 10.5, col: P.flor, w: b.w - 58});

            const L = luna();
            const mKey = Math.round(L.age * 4);
            if (this._moonKey !== mKey || !this._moonCells) {
                this._moonKey = mKey;
                const q = Math.cos(2 * Math.PI * L.p);
                const q2 = Math.cos(2 * Math.PI * (1 - L.p));
                const cells = [];
                for (let j = 0; j < 9; j++) {
                    for (let i = 0; i < 9; i++) {
                        const nx = (i - 4) / 4.5, ny = (j - 4) / 4.5;
                        if (nx * nx + ny * ny > 1.02) continue;
                        const ill = Math.sqrt(Math.max(0, 1 - ny * ny));
                        const lit = L.p < 0.5 ? nx >= q * ill : nx <= -q2 * ill;
                        cells.push([i * 4, j * 4, lit ? '#f6ecd4' : '#1e2c48']);
                    }
                }
                this._moonCells = cells;
            }
            const lx = b.x + b.w - 40, ly = b.y + 1;
            for (const [dx, dy, col] of this._moonCells) this._rect(lx + dx, ly + dy, 4, 4, col);
            this._t(b.x + b.w - 50, b.y + 39, 'LUNA ' + Math.round(L.age) + 'd', {px: 9.5, col: P.dim, w: 50, align: 'center'});
        } else if (id === 'clima') {
            const hf = st ? st.get_double('hora-simulada') : -1;
            let fSol = now;
            if (hf >= 0) {
                fSol = new Date(now);
                fSol.setHours(Math.floor(hf), Math.round((hf % 1) * 60), 0, 0);
            }
            const sol = calcSol(fSol, this.lat, this.lon);
            const faseTxt = sol.e < -6 ? 'NOCHE' : (sol.e < 4 ? 'DORADA' : 'DÍA');
            let clModo = 'normal';
            try { clModo = st?.get_string('clima') || 'normal'; } catch (_e) { clModo = 'normal'; }
            const clTag = (!soloW && clModo !== 'normal') ? ' · ' + clModo.toUpperCase() : '';
            const cl = this.clima;
            const meta = (cl && cl.ok && cl.city) ? `📍 ${String(cl.city).toUpperCase()}` : (faseTxt + clTag);
            const b = this._card(x0, y, h, '☀', 'CLIMA & ÓRBITA', meta);
            if (cl && cl.ok) {
                this._t(b.x, b.y, `🌡 ${cl.temp}°C · HUM ${cl.hum}%`, {px: 11.5, col: P.flor});
                this._t(b.x, b.y, `💨 ${Math.round(cl.wind)} km/h · SOL ${Math.round(sol.e)}°`, {px: 10.5, col: P.rosa, w: b.w, align: 'right'});
                this._bar(b.x, b.y + 18, b.w, ((sol.e + 18) / 68) * 100, P.flor);
                this._t(b.x, b.y + 27, `${String(cl.desc).toUpperCase()} · ${faseTxt}${clTag}`, {px: 10.5, col: P.dim, w: b.w});
            } else {
                this._t(b.x, b.y, `SOL ${sol.e.toFixed(1)}°`, {px: 11.5, col: P.flor});
                this._t(b.x, b.y, `AZ ${Math.round(sol.az)}°`, {px: 10.5, col: P.rosa, w: b.w, align: 'right'});
                this._bar(b.x, b.y + 18, b.w, ((sol.e + 18) / 68) * 100, P.flor);
                const luz = sol.e < -6 ? 'ESTRELLAS Y LUNA' : (sol.e < 4 ? 'SOL RASANTE · DORADA' : 'CIELO DESPEJADO');
                this._t(b.x, b.y + 27, luz + clTag, {px: 10.5, col: P.dim, w: b.w});
            }
        } else if (id === 'sistema') {
            const b = this._card(x0, y, h, '❖', 'SISTEMA', d.up ? 'UP ' + durac(d.up) : '');
            let fy = b.y;
            const fila = (etq, val, txt, opts) => {
                this._etq(b.x, fy + 1, etq);
                this._segbar(b.x + 34, fy + 2, 168, val, opts);
                this._t(b.x + 208, fy - 1, txt, {px: 11.5, w: b.w - 208, align: 'right'});
                fy += 17;
            };
            fila('CPU', d.cpu, Math.round(d.cpu) + '% ' + (d.nuc ?? '') + 'c');
            fila('RAM', d.ram?.pct, (d.ram?.usado ?? 0) + '/' + Math.round(d.ram?.total ?? 0) + 'G');
            fila('TMP', d.temp ? (d.temp - 30) / 60 * 100 : 0, (d.temp ? d.temp.toFixed(0) : '--') + '°C', {c1: P.cyan, c2: P.amber, c3: P.hot});
            if (d.bat) fila(d.bat.estado === 'Charging' ? 'CAR' : 'BAT', d.bat.pct, d.bat.pct + '% ' + horas(d.bat.min), {invert: true});
            fy += 4;
            this._spark(b.x, fy, b.w, 22, this.cpuH, 52, Math.max(12, ...this.cpuH, 0), P.rosa);
            fy += 27;
            this._pares(b.x, fy, [['CARGA', (d.load?.[0] ?? 0).toFixed(2)], ['DISCO', Math.round(d.disco ?? 0) + '%'],
                ['TOP', d.top?.length ? d.top[0][0].substring(0, 8) : '--', P.amber]], 11);
        } else if (id === 'gpu') {
            const g = d.gpu ?? {};
            const fps = st ? st.get_int('fps') : 8;
            const meta = g.temp ? `${g.temp}°C · ${fps} FPS` : `${fps} FPS`;
            const b = this._card(x0, y, h, '▣', 'GPU & MOTOR', meta);
            this._t(b.x, b.y, g.nombre || 'GPU LINUX', {px: 11, col: P.flor, w: b.w});
            const uso = g.uso ?? 0;
            this._etq(b.x, b.y + 19, 'CARGA');
            this._bar(b.x + 42, b.y + 23, b.w - 86, uso, P.cyan);
            this._t(b.x + b.w - 40, b.y + 18, `${uso}%`, {px: 11, w: 40, align: 'right'});
            const vramTxt = (g.vram_u && g.vram_t) ? ` · VRAM ${g.vram_u}/${g.vram_t}M` : ' · GNOME';
            this._t(b.x, b.y + 38, `${this.monW}×${this.monH}${vramTxt}`, {px: 10.5, col: P.dim, w: b.w});
        } else if (id === 'red') {
            const b = this._card(x0, y, h, '◈', 'RED ACTIVA', net.iface ?? 'sin red');
            let fy = b.y;
            for (let i = 0; i < 4; i++) {
                const on = net.senal !== null && net.senal !== undefined && net.senal >= (i + 1) * 25 - 10;
                const bh = 3 + i * 3;
                this._rect(b.x + i * 4, fy + 13 - bh, 3, bh, on ? P.green : P.track);
            }
            this._t(b.x + 22, fy, net.ssid ?? (net.iface ? 'cableado' : '--'), {px: 12, w: b.w - 22});
            fy += 17;
            this._pares(b.x, fy, [['IP', net.ip ?? '--'], ['GW', net.gw ?? '--']]);
            fy += 17;
            const vpn = net.vpn ?? {};
            this._rect(b.x, fy + 3, 8, 8, vpn.on ? P.green : P.faint);
            this._etq(b.x + 15, fy + 1, 'VPN');
            this._val(b.x + 44, fy, vpn.on ? `${vpn.iface} ${vpn.ip ?? ''}` : 'inactiva', {col: vpn.on ? P.green : P.dim});
            fy += 18;
            this._val(b.x, fy, '↓ ' + tasa(net.rx ?? 0), {col: P.cyan});
            this._val(b.x, fy + 14, '↑ ' + tasa(net.tx ?? 0), {col: P.rosa});
            this._spark(b.x + 92, fy, b.w - 92, 26, this.rxH, 36, Math.max(20000, ...this.rxH, 0), P.cyan);
            fy += 33;
            let pxX = b.x;
            for (const pt of (s.puertos ?? []).slice(0, 6)) {
                const txt = pt.p + (pt.n ? ' ' + pt.n.substring(0, 5) : '');
                const lay = this._pangoLay || PangoCairo.create_layout(this.cr);
                lay.set_width(-1);
                lay.set_ellipsize(Pango.EllipsizeMode.NONE);
                lay.set_font_description(this._fuente(MONO, 10)); lay.set_text(txt, -1);
                const tw = lay.get_pixel_size()[0] + 8;
                if (pxX + tw > b.x + b.w) { pxX = b.x; fy += 18; if (fy > y + h - 30) break; }
                const c = pt.local ? P.faint : P.amber;
                this._col(c); this.cr.setLineWidth(1); this.cr.rectangle(pxX + 0.5, fy + 0.5, tw - 1, 14); this.cr.stroke();
                this._t(pxX + 4, fy + 1, txt, {px: 10, col: pt.local ? P.dim : P.amber});
                pxX += tw + 4;
            }
            this._pares(b.x, y + h - 22, [['CONN', s.est ?? 0], ['LAN', (s.vecinos ?? 0) + ' eq'], ['DNS', s.dns ?? '--']], 8);
        } else if (id === 'audio') {
            const m = this.media;
            let meta = 'AMBIENTE BSO', track = 'Ambient Pixel · OST', sub = '90 BPM · STEREO', pos = '0:00', dur = '--:--', pct = 0;
            if (m && m.ok) {
                meta = m.playing ? `${m.app} · EN VIVO` : `${m.app} · PAUSA`;
                track = m.title;
                sub = m.artist || `${m.app} · AUDIO ACTIVO`;
                if (m.durSec > 0) {
                    const extra = m.playing ? Math.max(0, (Date.now() - m.polledAt) / 1000) : 0;
                    const posNow = Math.min(m.durSec, Math.max(0, m.posSec + extra));
                    pos = fmtSeg(posNow);
                    dur = fmtSeg(m.durSec);
                    pct = (posNow / m.durSec) * 100;
                } else {
                    pct = m.playing ? 100 : 0;
                }
            } else if (soloW) {
                meta = 'AUDIO SISTEMA';
                track = 'Sin música activa';
                sub = 'Spotify · Navegador · MPRIS';
            } else {
                const tid = st?.get_string('tema') || 'fittoa';
                const info = WORLD_AUDIO[tid] || ['Ambient Pixel · OST', '90 BPM · STEREO'];
                track = info[0];
                sub = info[1];
            }
            const b = this._card(x0, y, h, '♪', 'MÚSICA & AUDIO', meta);
            this._t(b.x, b.y, track, {px: 11.5, col: P.flor, w: b.w});
            this._t(b.x, b.y + 19, sub, {px: 10, col: P.dim, w: b.w});
            this._t(b.x, b.y + 37, pos, {px: 9.5, col: P.dim});
            this._t(b.x, b.y + 37, dur, {px: 9.5, col: P.dim, w: b.w, align: 'right'});
            this._bar(b.x + 42, b.y + 41, b.w - 84, pct, P.rosa);
        } else if (id === 'dev') {
            const repos = s.repos ?? [];
            const b = this._card(x0, y, h, '⚔', 'DEV', (s.host ? s.host + ' ' : '') + (s.kernel ?? ''));
            let fy = b.y;
            if (!repos.length) { this._val(b.x, fy, 'sin repos git en workspace', {col: P.faint}); fy += 16; }
            for (const r of repos) {
                this._rect(b.x, fy + 4, 7, 7, r.sucio > 0 ? P.amber : P.green);
                let x = b.x + 14;
                x += this._val(x, fy, r.n.substring(0, 13)) + 6;
                x += this._val(x, fy, r.b, {col: P.rosa}) + 6;
                this._val(x, fy, (r.sucio ? '~' + r.sucio : '') + (r.adelante ? ' ↑' + r.adelante : '') + (r.atras ? ' ↓' + r.atras : ''), {col: P.amber});
                fy += 16;
            }
            const tc = s.tc ?? {};
            this._pares(b.x, fy, [['PY', tc.py ?? '—'], ['NODE', tc.node ?? '—', tc.node ? P.text : P.faint],
                ['GO', tc.go ?? '—', tc.go ? P.text : P.faint], ['RUST', tc.rust ?? '—', tc.rust ? P.text : P.faint]], 8);
            fy += 16;
            this._rect(b.x, fy + 4, 7, 7, s.fallos > 0 ? P.hot : P.green);
            const sync = s.pacman_h !== null && s.pacman_h !== undefined ? (s.pacman_h > 48 ? Math.floor(s.pacman_h / 24) + 'd' : s.pacman_h + 'h') : '--';
            this._pares(b.x + 15, fy, [['SVC', (s.fallos ?? 0) + ' fall', s.fallos > 0 ? P.hot : P.text],
                ['ERR', s.errores ?? 0, s.errores > 0 ? P.amber : P.text], ['APT', sync]], 8);
        } else if (id === 'foco') {
            const secTot = Math.max(0, Math.floor((Date.now() - this.sessionStart) / 1000));
            const cicloSec = 1500;
            const rest = cicloSec - (secTot % cicloSec);
            const cicloNum = Math.floor(secTot / cicloSec) + 1;
            const b = this._card(x0, y, h, '⧖', 'FOCO ZEN', `CICLO ${cicloNum} · ZEN`);
            this._t(b.x, b.y - 2, `${p2(Math.floor(rest / 60))}:${p2(rest % 60)}`, {px: 18, col: P.flor});
            this._t(b.x, b.y + 4, `${Math.floor(secTot / 60)}m ${p2(secTot % 60)}s sesión`, {px: 10.5, col: P.dim, w: b.w, align: 'right'});
            this._bar(b.x, b.y + 28, b.w, Math.max(4, ((cicloSec - rest) / cicloSec) * 100), P.rosa);
        } else if (id === 'grimorio') {
            const hk = this.citas[this.hk % this.citas.length];
            const b = this._card(x0, y, h, '✧', 'GRIMORIO', hk.au);
            this._t(b.x, b.y, hk.sub, {px: 10.5, col: P.flor, a: this.hkOp, w: b.w});
            this._t(b.x, b.y + 18, hk.es, {px: 11, col: P.dim, w: b.w, wrap: true, a: this.hkOp});
        }
    }

    _pinta(area) {
        const cr = area.get_context();
        this.cr = cr;
        this._pangoLay = PangoCairo.create_layout(cr);
        this._pal = this._paleta();
        try {
            const [sw] = area.get_surface_size();
            const lay = this._layoutColumnas(this._lastAltoDisp);
            const k = sw / lay.totalW;
            cr.scale(k, k);

            for (let cIdx = 0; cIdx < lay.cols.length; cIdx++) {
                const x0 = cIdx * (COL_W + COL_GAP);
                let y = 0;
                for (const card of lay.cols[cIdx]) {
                    this._pintaTarjeta(card.id, x0, y, card.h);
                    y += card.h + lay.gap;
                }
            }
        } catch (e) {
            logError(e, 'PixelZen HUD');
        } finally {
            this._pangoLay = null;
            cr.$dispose();
            this.cr = null;
        }
    }

    destroy() {
        this._cancel.cancel();
        this._cierraWorker();
        this._paraTimers();
        this.actor.destroy();
    }
}
