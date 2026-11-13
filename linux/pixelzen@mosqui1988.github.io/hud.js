// PixelZen para GNOME - panel de datos (HUD).
import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import St from 'gi://St';
import Pango from 'gi://Pango';
import PangoCairo from 'gi://PangoCairo';

const ANCHO = 336, ALTO = 880;
const PAL = {
    bg: '#0b1020', bg2: '#121a30', track: '#1c2844', line: '#2f4266', border: '#7d6540',
    text: '#f3ead6', dim: '#a8b8cf', faint: '#687a96', red: '#d6a34a', hot: '#e0584e',
    rosa: '#54ded4', flor: '#e6c06e', amber: '#e6b45a', green: '#72c48c', cyan: '#66dce0',
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
function durac(s) {
    const dd = Math.floor(s / 86400), hh = Math.floor(s % 86400 / 3600), mm = Math.floor(s % 3600 / 60);
    return dd > 0 ? dd + 'd' + hh + 'h' : hh + 'h' + p2(mm);
}
function luna() {
    const syn = 29.530588853, ref = Date.UTC(2000, 0, 6, 18, 14) / 86400000;
    const age = (((Date.now() / 86400000 - ref) % syn) + syn) % syn;
    return {age, p: age / syn};
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
        this.d = {cpu: 0, ram: {pct: 0, usado: 0, total: 0}, temp: 0, bat: null, net: {vpn: {}}, load: [0, 0, 0], up: 0, disco: 0, top: [], nuc: 0};
        this.s = {puertos: [], repos: [], tc: {}, tools: {}, fallos: 0, errores: 0, est: 0, vecinos: 0};
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

        this.actor = new St.DrawingArea({reactive: false});
        this.actor.connect('repaint', a => this._pinta(a));

        this._lanza('rapido'); this._lanza('lento');
        this._cada(2000, () => this._lanza('rapido'));
        this._cada(20000, () => this._lanza('lento'));
        this._cada(1000, () => this.actor.queue_repaint());
        this._cada(90000, () => this._cambiaHaiku());
    }

    recargaTema() {
        try {
            const id = this._settings?.get_string('tema') || '';
            const sub = id ? `${this._dir}/temas/${id}/tema.json` : '';
            const ruta = (sub && GLib.file_test(sub, GLib.FileTest.EXISTS)) ? sub : `${this._dir}/tema.json`;
            const raw = JSON.parse(new TextDecoder().decode(
                GLib.file_get_contents(ruta)[1]));
            this.citas = (raw.citas && raw.citas.length) ? raw.citas : CITAS_DEFECTO;
            this.eraSub = raw.nombre ?? 'Era del Dragón Acorazado';
            this.hk = this.hk % this.citas.length;
        } catch (e) {
            this.citas = CITAS_DEFECTO;
        }
        this.actor?.queue_repaint();
    }

    _altoActivo() {
        const s = this._settings;
        const ver = k => s ? s.get_boolean(k) : true;
        let h = 0;
        if (ver('hud-tiempo')) h += 130;
        if (ver('hud-sistema')) h += 196;
        if (ver('hud-red')) h += 202;
        if (ver('hud-dev')) {
            const repos = this.s?.repos ?? [];
            h += 110 + Math.max(0, repos.length - 1) * 17;
        }
        if (ver('hud-grimorio')) h += 92;
        return Math.max(120, h);
    }

    coloca(area) {
        const margen = 24;
        const altoBase = Math.max(ALTO, this._altoActivo());
        this.k = Math.max(0.5, Math.min(1.6, (area.height - 2 * margen) / altoBase));
        const w = Math.round(ANCHO * this.k), h = Math.round(this._altoActivo() * this.k);
        this.actor.set_size(w, h);
        this.actor.set_position(area.x + area.width - w - margen, area.y + margen);
        this.actor.queue_repaint();
    }

    _cada(ms, fn) {
        this._timers.push(GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => { fn(); return GLib.SOURCE_CONTINUE; }));
    }

    _lanza(modo) {
        if (this._ocupado[modo]) return;
        this._ocupado[modo] = true;
        let proc;
        try {
            proc = Gio.Subprocess.new(['python3', '-I', this._script, modo, 'gnome'],
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE);
        } catch (e) {
            this._ocupado[modo] = false;
            return;
        }
        proc.communicate_utf8_async(null, this._cancel, (p, res) => {
            this._ocupado[modo] = false;
            try {
                const [, out] = p.communicate_utf8_finish(res);
                const j = JSON.parse(out);
                if (modo === 'rapido') {
                    this.d = j;
                    this.cpuH = this._push(this.cpuH, j.cpu, 120);
                    this.rxH = this._push(this.rxH, j.net?.rx ?? 0, 120);
                } else {
                    this.s = j;
                }
                this.actor.queue_repaint();
            } catch (e) { /* reintento en el siguiente ciclo */ }
        });
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
    _col(hex, a = 1) { const [r, g, b] = rgb(hex); this.cr.setSourceRGBA(r, g, b, a); }
    _rect(x, y, w, h, hex, a = 1) { this._col(hex, a); this.cr.rectangle(x, y, w, h); this.cr.fill(); }
    _t(x, y, txt, o = {}) {
        const cr = this.cr;
        const lay = PangoCairo.create_layout(cr);
        lay.set_font_description(this._fuente(o.fam ?? MONO, o.px ?? 13));
        if (o.wrap && o.w) { lay.set_width(o.w * Pango.SCALE); lay.set_wrap(Pango.WrapMode.WORD); }
        lay.set_text(String(txt), -1);
        const [tw] = lay.get_pixel_size();
        let xx = x;
        if (o.w && o.align === 'right') xx = x + o.w - tw;
        else if (o.w && o.align === 'center') xx = x + (o.w - tw) / 2;
        this._col(o.col ?? PAL.text, o.a ?? 1);
        cr.moveTo(xx, y);
        PangoCairo.show_layout(cr, lay);
        return tw;
    }
    _etq(x, y, txt) { return this._t(x, y, txt, {px: 11, col: PAL.dim}); }
    _val(x, y, txt, o = {}) { return this._t(x, y, txt, {px: 12, ...o}); }
    _pares(x, y, pares, sep = 12) {
        for (const [e, v, col] of pares) {
            x += this._etq(x, y + 2, e) + 6;
            x += this._val(x, y, v, {col}) + sep;
        }
    }
    _segbar(x, y, w, value, {c1 = PAL.green, c2 = PAL.amber, c3 = PAL.hot, invert = false} = {}) {
        const segs = 22, sw = Math.floor((w - (segs - 1) * 2) / segs);
        const on = Math.round(Math.max(0, Math.min(100, value || 0)) / 100 * segs);
        for (let i = 0; i < segs; i++) {
            const f = (i + 1) / segs;
            const c = i < on ? (invert ? (f < 0.2 ? c3 : f < 0.4 ? c2 : c1) : (f < 0.6 ? c1 : f < 0.85 ? c2 : c3)) : PAL.track;
            this._rect(x + i * (sw + 2), y, sw, 9, c);
        }
    }
    _spark(x, y, w, h, serie, cols, maxv, col) {
        const bw = Math.floor((w - cols) / cols);
        for (let i = 0; i < cols; i++) {
            const j = serie.length - cols + i;
            const v = j >= 0 && j < serie.length ? serie[j] : 0;
            const bx = x + i * (bw + 1);
            this._rect(bx, y + h - 1, bw, 1, PAL.line);
            const bh = Math.max(2, Math.round(Math.min(1, v / maxv) * h));
            this._rect(bx, y + h - bh, bw, bh, col, 0.35 + 0.65 * (i / cols));
        }
    }
    _card(y, h, emblem, title, meta) {
        const pad = 11, w = ANCHO;
        this._rect(0, y, w, h, PAL.bg, 0.80);
        this._col(PAL.border); this.cr.setLineWidth(1); this.cr.rectangle(0.5, y + 0.5, w - 1, h - 1); this.cr.stroke();
        this._rect(0, y, 6, 2, PAL.red); this._rect(0, y, 2, 6, PAL.red);
        const kw = this._t(pad, y + 8, emblem, {px: 13, col: PAL.rosa});
        this._t(pad + kw + 7, y + 10, title.split('').join(' '), {px: 11, col: PAL.dim});
        if (meta) this._t(pad, y + 8, meta, {px: 12, col: PAL.dim, w: w - 2 * pad, align: 'right'});
        for (let x = pad; x < w - pad - 2; x += 4) this._rect(x, y + 27, 2, 1, PAL.line);
        return {x: pad, y: y + 34, w: w - 2 * pad};
    }

    _pinta(area) {
        const cr = area.get_context();
        this.cr = cr;
        try {
            const [sw] = area.get_surface_size();
            const k = sw / ANCHO;
            cr.scale(k, k);
            const now = new Date(), d = this.d, s = this.s, net = d.net ?? {vpn: {}};
            const st = this._settings;
            const ver = k => st ? st.get_boolean(k) : true;
            let y = 0;

            if (ver('hud-tiempo')) {
                let b = this._card(y, 120, '✦', 'TIEMPO', s.host ?? '');
                this._t(b.x - 2, b.y - 2, p2(now.getHours()) + ':' + p2(now.getMinutes()), {px: 46});
                this._t(b.x + 148, b.y + 16, p2(now.getSeconds()), {px: 18, col: PAL.rosa});
                this._t(b.x, b.y + 44, `${DIAS[now.getDay()]} ${now.getDate()} ${MESES[now.getMonth()]} ${now.getFullYear()}`, {px: 13});
                this._t(b.x, b.y + 62, this.eraSub, {px: 11, col: PAL.flor});
                const L = luna(), q = Math.cos(2 * Math.PI * L.p);
                const lx = b.x + b.w - 44, ly = b.y + 2;
                for (let j = 0; j < 9; j++) {
                    for (let i = 0; i < 9; i++) {
                        const nx = (i - 4) / 4.5, ny = (j - 4) / 4.5;
                        if (nx * nx + ny * ny > 1.02) continue;
                        const ill = Math.sqrt(Math.max(0, 1 - ny * ny));
                        const lit = L.p < 0.5 ? nx >= q * ill : nx <= -Math.cos(2 * Math.PI * (1 - L.p)) * ill;
                        this._rect(lx + i * 4, ly + j * 4, 4, 4, lit ? '#f6ecd4' : '#1e2c48');
                    }
                }
                this._t(b.x + b.w - 54, b.y + 40, 'LUNA ' + Math.round(L.age) + 'd', {px: 10, col: PAL.dim, w: 54, align: 'center'});
                y += 130;
            }

            if (ver('hud-sistema')) {
                let b = this._card(y, 186, '❖', 'SISTEMA', d.up ? 'UP ' + durac(d.up) : '');
                let fy = b.y;
                const fila = (etq, val, txt, opts) => {
                    this._etq(b.x, fy + 1, etq);
                    this._segbar(b.x + 38, fy + 3, 178, val, opts);
                    this._t(b.x + 224, fy - 1, txt, {px: 13, w: 80, align: 'right'});
                    fy += 19;
                };
                fila('CPU', d.cpu, Math.round(d.cpu) + '%  ' + (d.nuc ?? '') + 'c');
                fila('RAM', d.ram?.pct, (d.ram?.usado ?? 0) + '/' + Math.round(d.ram?.total ?? 0) + 'G');
                fila('TMP', d.temp ? (d.temp - 30) / 60 * 100 : 0, (d.temp ? d.temp.toFixed(0) : '--') + '°C', {c1: PAL.cyan, c2: PAL.amber, c3: PAL.hot});
                if (d.bat) fila(d.bat.estado === 'Charging' ? 'CAR' : 'BAT', d.bat.pct, d.bat.pct + '% ' + horas(d.bat.min), {invert: true});
                fy += 6;
                this._spark(b.x, fy, b.w, 24, this.cpuH, 56, Math.max(12, ...this.cpuH, 0), PAL.rosa);
                fy += 30;
                this._pares(b.x, fy, [['CARGA', (d.load?.[0] ?? 0).toFixed(2)], ['DISCO', Math.round(d.disco ?? 0) + '%'],
                    ['TOP', d.top?.length ? d.top[0][0].substring(0, 8) : '--', PAL.amber]], 14);
                y += 196;
            }

            if (ver('hud-red')) {
                let b = this._card(y, 192, '◈', 'RED', net.iface ?? 'sin red');
                let fy = b.y;
                for (let i = 0; i < 4; i++) {
                    const on = net.senal !== null && net.senal !== undefined && net.senal >= (i + 1) * 25 - 10;
                    const bh = 3 + i * 3;
                    this._rect(b.x + i * 4, fy + 14 - bh, 3, bh, on ? PAL.green : PAL.track);
                }
                this._t(b.x + 24, fy, net.ssid ?? (net.iface ? 'cableado' : '--'), {px: 13});
                fy += 19;
                this._pares(b.x, fy, [['IP', net.ip ?? '--'], ['GW', net.gw ?? '--']]);
                fy += 19;
                const vpn = net.vpn ?? {};
                this._rect(b.x, fy + 3, 9, 9, vpn.on ? PAL.green : PAL.faint);
                this._etq(b.x + 17, fy + 2, 'VPN');
                this._val(b.x + 47, fy, vpn.on ? `${vpn.iface}  ${vpn.ip ?? ''}` : 'inactiva', {col: vpn.on ? PAL.green : PAL.dim});
                fy += 19;
                this._val(b.x, fy, '↓ ' + tasa(net.rx ?? 0), {col: PAL.cyan});
                this._val(b.x, fy + 15, '↑ ' + tasa(net.tx ?? 0), {col: PAL.rosa});
                this._spark(b.x + 102, fy, 200, 28, this.rxH, 40, Math.max(20000, ...this.rxH, 0), PAL.cyan);
                fy += 36;
                let px = b.x;
                for (const pt of (s.puertos ?? []).slice(0, 8)) {
                    const txt = pt.p + (pt.n ? ' ' + pt.n.substring(0, 6) : '');
                    const lay = PangoCairo.create_layout(cr);
                    lay.set_font_description(this._fuente(MONO, 11)); lay.set_text(txt, -1);
                    const tw = lay.get_pixel_size()[0] + 10;
                    if (px + tw > b.x + b.w) { px = b.x; fy += 20; if (fy > b.y + 130) break; }
                    const c = pt.local ? PAL.faint : PAL.amber;
                    this._col(c); cr.setLineWidth(1); cr.rectangle(px + 0.5, fy + 0.5, tw - 1, 15); cr.stroke();
                    this._t(px + 5, fy + 1, txt, {px: 11, col: pt.local ? PAL.dim : PAL.amber});
                    px += tw + 4;
                }
                this._pares(b.x, y + 192 - 11 - 16, [['CONN', s.est ?? 0], ['LAN', (s.vecinos ?? 0) + ' equipos'], ['DNS', s.dns ?? '--']]);
                y += 202;
            }

            if (ver('hud-dev')) {
                const repos = s.repos ?? [];
                const hDev = 100 + Math.max(0, repos.length - 1) * 17;
                let b = this._card(y, hDev, '⚔', 'DEV', s.kernel ? 'linux ' + s.kernel : '');
                let fy = b.y;
                if (!repos.length) { this._val(b.x, fy, 'sin repos git en workspace, dev o src', {col: PAL.faint}); fy += 17; }
                for (const r of repos) {
                    this._rect(b.x, fy + 5, 8, 8, r.sucio > 0 ? PAL.amber : PAL.green);
                    let x = b.x + 16;
                    x += this._val(x, fy, r.n.substring(0, 14)) + 8;
                    x += this._val(x, fy, r.b, {col: PAL.rosa}) + 8;
                    this._val(x, fy, (r.sucio ? '~' + r.sucio : '') + (r.adelante ? ' ↑' + r.adelante : '') + (r.atras ? ' ↓' + r.atras : ''), {col: PAL.amber});
                    fy += 17;
                }
                const tc = s.tc ?? {};
                this._pares(b.x, fy, [['PY', tc.py ?? '—'], ['NODE', tc.node ?? '—', tc.node ? PAL.text : PAL.faint],
                    ['GO', tc.go ?? '—', tc.go ? PAL.text : PAL.faint], ['RUST', tc.rust ?? '—', tc.rust ? PAL.text : PAL.faint]], 10);
                fy += 17;
                this._rect(b.x, fy + 5, 8, 8, s.fallos > 0 ? PAL.hot : PAL.green);
                const sync = s.pacman_h !== null && s.pacman_h !== undefined ? (s.pacman_h > 48 ? Math.floor(s.pacman_h / 24) + 'd' : s.pacman_h + 'h') : '--';
                this._pares(b.x + 18, fy, [['SVC', (s.fallos ?? 0) + ' fallidos', s.fallos > 0 ? PAL.hot : PAL.text],
                    ['ERR 1H', s.errores ?? 0, s.errores > 0 ? PAL.amber : PAL.text], ['APT', sync]], 10);
                y += hDev + 10;
            }

            if (ver('hud-grimorio')) {
                const hk = this.citas[this.hk % this.citas.length];
                let b = this._card(y, 92, '✧', 'GRIMORIO', hk.au);
                this._t(b.x, b.y, hk.sub, {px: 11, col: PAL.rosa, a: this.hkOp});
                this._t(b.x, b.y + 18, hk.es, {px: 12, col: PAL.dim, w: b.w, wrap: true, a: this.hkOp});
            }
        } catch (e) {
            logError(e, 'PixelZen HUD');
        } finally {
            cr.$dispose();
            this.cr = null;
        }
    }

    destroy() {
        this._cancel.cancel();
        for (const t of this._timers) GLib.source_remove(t);
        this._timers = [];
        this.actor.destroy();
    }
}
