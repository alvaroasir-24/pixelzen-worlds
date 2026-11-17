(() => {
  const ALAS_GRULLA = [
    [[-5, -2], [-4, -2], [-3, -1], [-2, -1], [-1, 0], [0, 0], [1, 0], [2, -1], [3, -1], [4, -2], [5, -2]],
    [[-5, 1], [-4, 1], [-3, 1], [-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0], [3, 1], [4, 1], [5, 1]],
    [[-5, 2], [-4, 1], [-3, 1], [-2, 0], [-1, 0], [0, 1], [1, 0], [2, 0], [3, 1], [4, 1], [5, 2]],
  ];
  const ALAS_WYVERN = [
    [[-7, -3], [-6, -3], [-5, -2], [-4, -2], [-3, -1], [-2, -1], [-1, 0], [0, 0], [1, 0], [2, -1], [3, -1], [4, -2], [5, -2], [6, -3], [7, -3], [0, 2]],
    [[-7, 1], [-6, 1], [-5, 1], [-4, 0], [-3, 0], [-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 1], [6, 1], [7, 1], [0, 2]],
    [[-7, 3], [-6, 2], [-5, 2], [-4, 1], [-3, 1], [-2, 0], [-1, 0], [0, 1], [1, 0], [2, 0], [3, 1], [4, 1], [5, 2], [6, 2], [7, 3], [0, 2]],
  ];
  const MOTAS_MANA = [
    [70, 300], [95, 330], [130, 290], [565, 310], [590, 340],
    [20, 345], [470, 296], [160, 355], [248, 318], [520, 352],
  ];
  const MILES_FRAMES = [
    {
      hc: 23, hr: 0, rows: [
        '......................RRK.', '.....................RRKK.', '....................KKK...',
        '..........KKKKKK...KKK....', '.........KKKKKKKK.KKK.....', '........KKWWKKWWKKKR......',
        '........KKWWKKWWKKK.......', '.........KKKKKKKKK........', '......KKKKKRRRRKK.........',
        '.....KKRRKKRRRRK..........', '....KKR.KKRKKRRKKKKKKKK...', '...KKK..KKRRRRKKKKKKSSK...',
        '..KK....KKRRKK...KKK..KK..', '..K.....KK.KK.....KK....K.', '.......KK...KK............',
        '......KK.....RR...........', '.....RR......WW...........', '.....WW...................',
      ],
    },
    {
      hc: 19, hr: 0, rows: [
        '..................RRK.....', '.................RRKK.....', '................KKK.......',
        '.........KKKKKK.KKK.......', '........KKKKKKKKKK........', '.......KKWWKKWWKKK........',
        '.......KKWWKKWWKKK........', '........KKKKKKKKK.........', '.....KKKKKKRRRKK..........',
        '....KKRKKRRRRRKK..........', '....KK.KKRKKRRKKKKKKKK....', '...KK..KKRRRRKKKKKKSSK....',
        '...K...KKRRKK...KKK..KK...', '......KK..KK.....KK.......', '.....KK....RR.............',
        '....RRR....WW.............', '....WWW...................', '..........................',
      ],
    },
    {
      hc: 16, hr: 0, rows: [
        '...............RRK........', '..............RRKK........', '.............KKK..........',
        '.......KKKKKKKR...........', '......KKKKKKKKK...........', '.....KKWWKKWWKKK..........',
        '.....KKWWKKWWKKK..........', '......KKKKKKKKK...........', '....KKKKKRRRKK............',
        '...KKRKKRRRRKK............', '...KK.KKRKKRRKKKKKKK......', '..KK..KKRRRRKKKKSSKK......',
        '..K...KKRRKK..KKK..KK.....', '.....KK..KK....KK.........', '....KK....RR..............',
        '...RRR....WW..............', '...WWW....................', '..........................',
      ],
    },
    {
      hc: 22, hr: 2, rows: [
        '.........KKKKKK...........', '........KKKKKKKK..........', '.......KKWWKKWWKKK..RRK...',
        '.......KKWWKKWWKKK.RRKK...', '........KKKKKKKKK.KKK.....', '......KKKKKKKKKKK.KK......',
        '.....KKRRKKRRRRKKKK.......', '....KKR.KKRKKRRKKRRKK.....', '...KKK..KKRRRRKK..SSKK....',
        '...KK...KKRRKK.....KK.K...', '.......KK..KK.............', '......KK....RR............',
        '.....RRR....WW............', '.....WWW..................', '..........................',
        '..........................', '..........................', '..........................',
      ],
    },
  ];
  const MILES_HANG_ROWS = [
    [
      '......BRB......', '.....BKKKB.....', '....BKK.KKB....', '...BKK...KKB...',
      '...BRK...KRB...', '....BKKKKKB....', '...BKKRRRKKB...', '..BKKRRRRRKKB..',
      '..BRKRRRRRKRB..', '.BKK.KKKKK.KKB.', '.BK...KRK...KB.', '....BKKKKKB....',
      '...BKKKKKKKB...', '..BKKWKKKWKKB..', '..BKWWKKKWWKB..', '..BKKWKKKWKKB..',
      '...BKKRRRKKB...', '....BKKKKKB....',
    ],
    [
      '......BRB......', '.....BKKKB.....', '....BKK.KKB....', '...BKK...KKB...',
      '...BRK...KRB...', '....BKKKKKB....', '...BKKRRRKKB...', '..BKKRRRRRKKB..',
      '..BRKRRRRRKRB..', '..BK.KKKKK.KKB.', '.....BKRK...KB.', '....BKKKKKB....',
      '...BKKKKKKKB...', '..BKKKKKKKKKB..', '..BKKWKKKWKKB..', '..BKKKKKKKKKB..',
      '...BKKRRRKKB...', '....BKKKKKB....',
    ],
  ];
  const MILES_COLS = { K: '#151521', R: '#eb2d3c', W: '#e4eeff', B: '#4a527a' };

  function lcg(seed) {
    let s = seed;
    return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
  }
  const clamp01 = v => (v < 0 ? 0 : v > 1 ? 1 : v);
  const suave = t => { t = clamp01(t); return t * t * (3 - 2 * t); };

  function loadImage(src) {
    return new Promise((res, rej) => {
      const im = new Image();
      im.onload = () => res(im);
      im.onerror = rej;
      im.src = src;
    });
  }

  function createRenderer(canvas, opts = {}) {
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    let rng = lcg(7);
    const olas = Array.from({ length: 44 }, () => [
      300 + Math.floor(rng() * 260),
      286 + Math.floor(rng() * 108),
      3 + Math.floor(rng() * 11),
      rng() * 6.28,
      0.03 + rng() * 0.05,
      rng() < 0.35,
    ]);
    rng = lcg(21);
    const hojas = Array.from({ length: 42 }, () => [
      rng() * 640,
      rng() * 400,
      0.30 + rng() * 0.42,
      0.06 + rng() * 0.12,
      rng() * 6.28,
      Math.floor(rng() * 4),
    ]);

    const state = {
      tema: 'fittoa',
      pantalla: 'principal',
      modoHora: 1,
      horaFija: 21.5,
      fps: 8,
      mostrarHud: true,
      hudCompacto: false,
      clima: 'normal',
      audioReactivo: true,
      audioEnergy: 0,
      parallax: true,
      parallaxX: 0,
      parallaxY: 0,
      evento: null,
      _lastHourEvent: -1,
      foco: {
        activo: true,
        descanso: false,
        cicloSec: 25 * 60,
        restSec: 25 * 60,
        sesionSec: 0,
        ciclo: 1,
        lastTickMs: Date.now(),
      },
      hudStats: {
        tiempo: true,
        clima: true,
        sistema: true,
        gpu: true,
        red: true,
        audio: true,
        dev: true,
        foco: true,
        grimorio: true,
      },
      astro: null,
      _gpuName: '',
      lat: 40.4,
      lon: -3.7,
      tick: 0,
      inicioMs: Date.now(),
      inicioHora: 12.0,
      D: null,
      T: null,
      img: {},
      brillantes: [],
      ...(opts.initialState || {}),
    };

    const GOTAS_CLIMA = Array.from({ length: 84 }, (_, i) => [
      (i * 53 + 17) % 640,
      (i * 89 + 31) % 390,
      5 + (i % 4) * 2,
      6 + (i % 3),
    ]);
    const COPOS_CLIMA = Array.from({ length: 68 }, (_, i) => [
      (i * 61 + 29) % 640,
      (i * 97 + 13) % 390,
      0.75 + (i % 4) * 0.35,
      i * 0.7,
      i % 5 === 0 ? 2 : 1,
    ]);

    const px = (hex, op, ax, ay, aw = 1, ah = 1) => {
      if (op <= 0.004) return;
      ctx.globalAlpha = clamp01(op);
      ctx.fillStyle = hex;
      ctx.fillRect(Math.round(ax), Math.round(ay), aw, ah);
    };
    const osc = (f, p) => 0.5 + 0.5 * Math.sin(state.tick * f + p);

    function fechaEfectiva() {
      const d = new Date();
      if (state.modoHora === 1) {
        const elapsedS = (Date.now() - state.inicioMs) / 1000;
        const h = (state.inicioHora + (elapsedS / 5400) * 24) % 24;
        d.setHours(Math.floor(h), Math.floor((h % 1) * 60), Math.floor((h * 3600) % 60), 0);
      } else if (state.modoHora === 2) {
        const h = ((Date.now() / 1000) % 90) / 90 * 24;
        d.setHours(Math.floor(h), Math.floor((h % 1) * 60), Math.floor((h * 3600) % 60), 0);
      } else if (state.modoHora === 3) {
        const h = state.horaFija;
        d.setHours(Math.floor(h), Math.round((h % 1) * 60), 0, 0);
      }
      return d;
    }

    function sol(fecha) {
      const rad = Math.PI / 180;
      const nn = fecha.getTime() / 86400000 + 2440587.5 - 2451545.0;
      const L = (280.460 + 0.9856474 * nn) % 360;
      const g = ((357.528 + 0.9856003 * nn) % 360) * rad;
      const lam = (L + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g)) * rad;
      const eps = (23.439 - 0.0000004 * nn) * rad;
      const ra = Math.atan2(Math.cos(eps) * Math.sin(lam), Math.cos(lam));
      const dec = Math.asin(Math.sin(eps) * Math.sin(lam));
      const gmst = (18.697374558 + 24.06570982441908 * nn) % 24;
      let Hh = (gmst * 15 + state.lon) * rad - ra;
      Hh = Math.atan2(Math.sin(Hh), Math.cos(Hh));
      const phi = state.lat * rad;
      const e = Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(Hh));
      const A = Math.atan2(Math.sin(Hh), Math.cos(Hh) * Math.sin(phi) - Math.tan(dec) * Math.cos(phi)) + Math.PI;
      const c0 = Math.max(-1, Math.min(1, -Math.tan(phi) * Math.tan(dec)));
      return { e: e / rad, az: (A / rad) % 360, H: Hh, H0: Math.acos(c0) };
    }

    function pintaMiles(t, nf) {
      const P = 340, mitad = 170;
      const fase = ((t % P) + P) % P;
      const der = fase < mitad;
      const u = der ? fase / mitad : (fase - mitad) / mitad;
      const flip = !der;
      const x = der ? -24 + u * 688 : 664 - u * 688;
      const arcW = 688 / 3;
      const arcIdx = Math.min(2, Math.floor(u * 3));
      const su = u * 3 - arcIdx;
      const tieneRed = su >= 0.08 && su <= 0.86;
      const fIdx = !tieneRed ? 3 : su < 0.34 ? 0 : su < 0.64 ? 1 : 2;
      let y = (der ? 62 : 76) + 52 * Math.sin(su * Math.PI);
      if (!tieneRed) {
        const j = su > 0.86 ? (su - 0.86) / 0.22 : (su + 0.14) / 0.22;
        y -= 7 * Math.sin(Math.min(1, Math.max(0, j)) * Math.PI);
      }
      const mx = Math.round(x), my = Math.round(y);
      const fr = MILES_FRAMES[fIdx];

      if (tieneRed) {
        const arcStart = der ? -24 + arcIdx * arcW : 664 - arcIdx * arcW;
        const ax = Math.round(der ? arcStart + arcW * 0.62 : arcStart - arcW * 0.62);
        const hx = mx + (flip ? 13 - fr.hc : fr.hc - 13);
        const hy = my + fr.hr - 10;
        const steps = Math.max(1, Math.max(Math.abs(ax - hx), Math.abs(hy)));
        for (let i = 0; i <= steps; i++) {
          const wx = Math.round(hx + (ax - hx) * i / steps);
          const wy = Math.round(hy * (1 - i / steps));
          px('#dceaff', (i % 2 === 0 ? 0.88 : 0.68) * (1 - 0.12 * nf), wx, wy, 1, 1);
        }
      }

      for (let r = 0; r < fr.rows.length; r++) {
        const row = fr.rows[r];
        for (let c = 0; c < row.length; c++) {
          const ch = row[c];
          if (ch !== '.') px(MILES_COLS[ch], 1, mx + (flip ? 13 - c : c - 13), my + r - 10, 1, 1);
        }
      }

      const tailDir = der ? -1 : 1;
      for (let k = 0; k < 3; k++) {
        if ((t + k) % 3 !== 0) continue;
        const sx = mx + tailDir * (10 + k * 4) + Math.round(Math.sin(t * 0.6 + k * 2) * 2);
        const sy = my + 2 + Math.round(Math.cos(t * 0.5 + k * 1.7) * 3);
        px(k === 1 ? '#ffd840' : '#00e5ff', 0.85, sx, sy, 1, 1);
      }
    }

    function pintaMilesColgado(t, nf) {
      const CYCLE = 220;
      const xs = [108, 224, 348, 418, 162, 578];
      const dropYs = [96, 82, 108, 88, 76, 94];
      const slot = Math.floor(t / CYCLE);
      const idx = ((slot % xs.length) + xs.length) % xs.length;
      const u = (((t % CYCLE) + CYCLE) % CYCLE) / CYCLE;
      if (u < 0.14 || u >= 0.88) return;

      const anchorX = xs[idx], targetY = dropYs[idx];
      let yTop, swayAmp = 0;
      if (u < 0.30) {
        const p = (u - 0.14) / 0.16;
        const ease = 1 - Math.pow(1 - p, 2);
        yTop = Math.round(-20 + (targetY + 20) * ease + Math.sin(p * Math.PI) * 5);
        swayAmp = 1;
      } else if (u < 0.72) {
        yTop = Math.round(targetY + Math.sin(t * 0.22));
        swayAmp = 2;
      } else {
        const p = (u - 0.72) / 0.16;
        yTop = Math.round(targetY - (targetY + 22) * (p * p));
        swayAmp = 1;
      }

      const mx = anchorX + Math.round(Math.sin(t * 0.14) * swayAmp);
      const footY = yTop + 1;
      if (footY > 0) {
        const steps = Math.max(1, footY);
        for (let i = 0; i <= steps; i++) {
          const wx = Math.round(anchorX + (mx - anchorX) * i / steps);
          const wy = Math.round(footY * i / steps);
          if (wy >= 0) px('#dceaff', (i % 2 === 0 ? 0.86 : 0.64) * (1 - 0.12 * nf), wx, wy, 1, 1);
        }
      }

      const fIdx = (u >= 0.30 && u < 0.72 && (t % 64) < 5) ? 1 : 0;
      const rows = MILES_HANG_ROWS[fIdx];
      for (let r = 0; r < rows.length; r++) {
        const ry = yTop + r;
        if (ry < 0) continue;
        const row = rows[r];
        for (let c = 0; c < row.length; c++) {
          const ch = row[c];
          if (ch !== '.') px(MILES_COLS[ch], 1, mx + c - 7, ry, 1, 1);
        }
      }
    }

    function pintaFerry(t, nf) {
      const P = 1800, mitad = 900;
      const f = ((t % P) + P) % P;
      const der = f < mitad;
      const u = der ? f / mitad : (f - mitad) / mitad;
      const fx = Math.round(der ? 180 + u * 320 : 500 - u * 320);
      const fy = 295 + (Math.sin(t * 0.08) > 0.6 ? 1 : 0);
      const dir = der ? 1 : -1;
      px('#141a2e', 0.95, fx - 10, fy, 20, 2);
      px('#e65c28', 0.95, fx - 9, fy - 1, 18, 1);
      px('#dce6f2', 0.95, fx - 7, fy - 3, 14, 2);
      px('#f0682c', 0.95, fx - 6, fy - 4, 12, 1);
      px('#dce6f2', 0.95, fx - 3, fy - 6, 6, 2);
      px('#1e2438', 0.95, fx - dir * 1, fy - 8, 2, 2);
      if (nf > 0.15) {
        for (let wx = -5; wx <= 5; wx += 2) px('#ffe088', 0.85 * nf, fx + wx, fy - 3, 1, 1);
        px('#ff3658', 0.9 * nf, fx - dir * 9, fy - 2, 1, 1);
        px('#54ff98', 0.9 * nf, fx + dir * 9, fy - 2, 1, 1);
      }
      for (let k = 1; k <= 7; k++) {
        if ((Math.floor(t / 2) + k) % 2 === 0) px('#d4ecff', 0.45 * (1 - k / 8), fx - dir * (10 + k * 2), fy + 1, 2, 1);
      }
    }

    function pintaTormentaStranger(t, nf, modo) {
      const pulse = 0.04 + 0.05 * osc(0.08, 0.5);
      px('#ff1e3c', pulse * (0.6 + 0.4 * nf), 0, 0, 640, 276);
      const slot = Math.floor(t / 44);
      const age = t % 44;
      if (age >= 6) return;
      const alpha = (1 - age / 6) * (age % 2 === 0 ? 1 : 0.55);
      px('#ff2a48', alpha * 0.14, 0, 0, 640, 272);
      const anchors = modo === 'stranger_demogorgon'
        ? [385, 428, 472, 340]
        : modo === 'stranger_reloj'
          ? [276, 364, 240, 400]
          : [132, 174, 212, 154];
      const bx0 = anchors[slot % anchors.length];
      let lx = bx0;
      const yIni = modo === 'stranger_azotamentes' ? 54 : 26;
      for (let i = 0; i < 120; i += 2) {
        const jit = Math.sin(slot * 7.3 + i * 0.47) > 0.25 ? 2 : (Math.cos(slot * 3.1 + i * 0.61) < -0.25 ? -2 : 0);
        lx += jit;
        const ly = yIni + i;
        if (ly > 268) break;
        px('#ff2848', alpha * 0.72, lx - 1, ly, 3, 2);
        px('#ffd8e2', alpha, lx, ly, 1, 2);
        if (i === 44 || i === 82) {
          const dir = (slot + i) % 2 === 0 ? 1 : -1;
          for (let b = 0; b < 22; b += 2) {
            px('#ff3454', alpha * 0.68, lx + dir * b, ly + b, 2, 2);
          }
        }
      }
    }

    function pintaStrangerPrincipal(t, nf) {
      // Zarcillos de tormenta y esporas escarlata girando en torno al Azotamentes
      for (let i = 0; i < 12; i++) {
        const ang = t * 0.07 + i * 0.52;
        const wx = 168 + Math.round(Math.cos(ang) * (24 + (i % 4) * 14));
        const wy = 148 + Math.round(Math.sin(ang * 0.8) * 32 - ((t * 0.4 + i * 5) % 18));
        px(i % 2 === 0 ? '#ff304c' : '#2a0814', 0.48 + 0.35 * nf, wx, wy, 2, 2);
      }

      // Chicos de Hawkins pedaleando en fila por la carretera con haz de faro movil
      const riders = [
        [0, 344, '#2c5ca8', '#e64242'],
        [-42, 338, '#d43c44', '#1b2030'],
        [-84, 346, '#e28832', '#263826'],
        [-126, 340, '#3e8a5c', '#543884'],
      ];
      const leadX = ((t * 1.65) % 860) - 70;
      const spoke = Math.floor(t / 2) % 2;
      riders.forEach(([ox, by, coat, hat], idx) => {
        const cx = Math.round(leadX + ox);
        if (cx < -35 || cx > 665) return;
        const bob = Math.sin(t * 0.45 + idx * 1.4) > 0.35 ? -1 : 0;
        // Ruedas y radios giratorios
        for (const wx of [cx - 6, cx + 6]) {
          px('#1d202c', 0.95, wx - 4, by - 7, 8, 2);
          px('#1d202c', 0.95, wx - 4, by - 1, 8, 2);
          px('#1d202c', 0.95, wx - 4, by - 6, 2, 6);
          px('#1d202c', 0.95, wx + 2, by - 6, 2, 6);
          px('#a8b4cc', 0.9, wx + (spoke ? 0 : -1), by - 4, 1, 1);
          px('#a8b4cc', 0.85, wx + (spoke ? 1 : 0), by - 5, 1, 1);
        }
        // Cuadro, manillar, mochila y cuerpo del chico
        px('#3a4052', 0.95, cx - 6, by - 6, 13, 1);
        px('#7c8498', 0.95, cx + 4, by - 10, 1, 4);
        px(coat, 0.96, cx - 2, by - 14 + bob, 5, 6);
        px('#181a24', 0.96, cx - 3, by - 13 + bob, 2, 4);
        px('#deb292', 0.96, cx - 1, by - 16 + bob, 3, 2);
        px(hat, 0.96, cx - 2, by - 18 + bob, 5, 2);
        // Cono de luz delantero proyectado sobre el asfalto
        for (let i = 1; i <= 22; i += 2) {
          const rad = Math.max(1, Math.floor(i / 5));
          const opBeam = Math.max(0.04, (0.34 - i * 0.013) * (0.45 + 0.55 * nf));
          px('#fff0b8', opBeam, cx + 7 + i, by - 9 - rad + 1, 2, rad * 2 - 1);
        }
        px('#fff8d4', 0.95, cx + 6, by - 9, 2, 1);
      });
    }

    function pintaStrangerDemogorgon(t, nf) {
      // Fauces del Demogorgon latiendo en rojo + esporas flotantes
      const mawP = 0.45 + 0.55 * osc(0.14, 0.2);
      px('#ff2448', 0.22 * mawP, 412, 314, 13, 13);
      px('#ffc8d4', 0.65 * mawP, 417, 319, 3, 3);
      for (let i = 0; i < 10; i++) {
        const sx = 392 + ((i * 19 + Math.round(t * 0.5)) % 56);
        const sy = 342 - ((t * 0.55 + i * 9) % 44);
        px(i % 2 === 0 ? '#ff3a5e' : '#ffd0d8', 0.55, sx, sy, 1, 1);
      }
      // Guirnalda de luces del alfabeto de Joyce parpadeando en secuencia
      const cols = ['#ff2e6a', '#48e8ff', '#ffd448', '#52ff88'];
      const active = Math.floor(t / 6) % 8;
      for (let i = 0; i < 8; i++) {
        const lx = 78 + i * 10;
        const ly = 292 + (i % 2) * 5;
        const isLit = i === active || ((Math.floor(t / 14) + i) % 5 === 0);
        const op = (isLit ? 0.95 : 0.30) * (0.55 + 0.45 * nf);
        const col = cols[i % 4];
        px(col, 0.24 * op, lx - 1, ly - 1, 4, 3);
        px(col, op, lx, ly, 2, 1);
      }
    }

    function pintaStrangerReloj(t, nf) {
      // Pendulo dorado oscilando detras del cristal del reloj de Creel
      const ang = 0.14 * Math.sin(t * 0.14);
      const px0 = 320, py0 = 232, len = 56;
      for (let r = 0; r <= len; r += 2) {
        const rx = Math.round(px0 + Math.sin(ang) * r);
        const ry = Math.round(py0 + Math.cos(ang) * r);
        px('#e6bc58', 0.96, rx, ry, 1, 2);
      }
      const bx = Math.round(px0 + Math.sin(ang) * len);
      const by = Math.round(py0 + Math.cos(ang) * len);
      px('#f2ca62', 0.98, bx - 3, by - 3, 7, 7);
      px('#fff4be', 0.90, bx - 1, by - 1, 3, 3);
      // Chispas escarlata pulsantes en la grieta de Vecna
      for (let k = 0; k < 6; k++) {
        const cy = 172 + ((t * 2 + k * 33) % 180);
        const cx = 320 + Math.round(Math.sin(cy * 0.15 + t * 0.08) * 14);
        px('#ff4868', 0.55 + 0.35 * nf, cx, cy, 2, 2);
      }
    }

    function pintaDemonRengoku(t, nf) {
      const imp = Math.pow(Math.max(0, Math.sin(t * 0.28)), 4);
      const clashTick = t % 24;
      const clash = clashTick < 5 ? 1 - clashTick / 5 : 0;
      const env = 0.65 + 0.35 * nf;

      // 1. Auras termicas/criogenicas y destello de choque en el claro
      px('#ff5820', (0.07 + 0.11 * imp) * env, 286, 266, 94, 46);
      px('#38d8ff', (0.07 + 0.11 * imp) * env, 404, 268, 96, 46);
      if (clash > 0.05) {
        const rC = Math.round(14 + (1 - clash) * 18);
        px('#ffe8a0', 0.16 * clash * env, 418 - rC, 284 - Math.round(rC * 0.7), rC * 2, Math.round(rC * 1.4));
      }

      // 2. Haori en llamas y aura ascendente de Rengoku (cx=334, by=310)
      for (let i = 0; i < 8; i++) {
        const fx = 306 + i * 3;
        const wave = Math.sin(t * 0.55 + i * 0.85);
        const fy = 287 + Math.round(i * 0.3 + wave * 1.8);
        const fh = 5 + ((Math.floor(t * 0.6) + i * 3) % 5);
        px('#ff3624', 0.82, fx, fy + fh - 3, 2, 3);
        px('#ff7e24', 0.88, fx, fy + 2, 2, 3);
        px('#ffd84c', 0.90, fx, fy, 2, 2);
      }
      for (let k = 0; k < 6; k++) {
        const lift = ((t * 1.6 + k * 7) % 18);
        const ax = 324 + ((k * 7) % 21) + Math.round(Math.sin(t * 0.4 + k) * 2);
        const ay = 294 - Math.round(lift);
        px(k % 2 === 0 ? '#ffd84c' : '#ff5e24', Math.max(0.15, (1 - lift / 18) * 0.85), ax, ay, 2, 2);
      }
      // Brillo vivo en la katana Nichirin de la Llama
      const bPos = (t * 2) % 20;
      px('#fff8d8', 0.95, 342 + bPos, 292 - Math.floor(bPos / 4), 3, 1);

      // 3. Novena Postura: Rengoku! Dragon de fuego rugiendo hacia el choque (x=356..422)
      for (let step = 0; step < 19; step++) {
        const u = step / 18;
        const pulseU = ((t * 0.11 + u * 2.2) % 1.0);
        const bx = Math.round(356 + u * 64);
        const by = Math.round(288 - Math.sin(u * Math.PI * 0.85) * 18 + Math.sin(u * 9.0 - t * 0.65) * 3.2);
        const rad = 3 + ((step + Math.floor(t * 0.5)) % 3);
        px('#ff2a18', 0.42, bx - rad - 1, by - rad - 1, (rad + 1) * 2, (rad + 1) * 2);
        px('#ff7e24', 0.84, bx - rad, by - rad, rad * 2, rad * 2);
        px(pulseU > 0.62 ? '#fff8c8' : '#ffd84c', 0.94, bx - 1, by - 1, 3, 3);
        // Anillos espirales alrededor del dragon
        const angR = t * 0.5 + step * 0.8;
        px('#ffe888', 0.80, bx + Math.round(Math.cos(angR) * 4), by + Math.round(Math.sin(angR) * 6), 2, 2);
      }
      // Fauces animadas del dragon en el choque (x=418, y=284)
      const jaw = Math.sin(t * 0.45) > 0 ? 1 : 0;
      px('#fff8d0', 0.96, 417, 281 - jaw, 6, 3);
      px('#ff7e24', 0.92, 421, 278 - jaw, 5, 2);
      px('#ff3624', 0.90, 421, 286 + jaw, 5, 2);

      // 4. Brujula Destructiva giratoria bajo los pies de Akaza (cx=456, cy=312)
      const rot = t * 0.065;
      for (let p = 0; p < 12; p++) {
        const ang = rot + (p * Math.PI * 2) / 12;
        const cA = Math.cos(ang), sA = Math.sin(ang);
        for (let r = 14; r <= 42; r += 4) {
          const rx = Math.round(456 + cA * r);
          const ry = Math.round(312 + sA * (r * 0.18));
          const esPunta = r >= 36;
          px(esPunta ? '#ffffff' : (r >= 26 ? '#92f0ff' : '#38d8ff'), esPunta ? 0.95 : 0.78, rx, ry, esPunta ? 2 : 1, 1);
        }
      }
      // Aura Soryu, ojos dorados y rafagas de Aire Destructivo de Akaza (446 -> 418)
      px('#ffd84c', 0.95, 450, 284, 1, 1);
      px('#ffd84c', 0.95, 454, 284, 1, 1);
      for (let k = 0; k < 4; k++) {
        const prog = ((t * 0.13 + k * 0.25) % 1.0);
        const ax = Math.round(446 - prog * 28);
        const ay = Math.round(288 + ((k % 2 === 0 ? -1 : 1) * 5) + Math.sin(t * 0.4 + k) * 2);
        px('#38d8ff', 0.85, ax, ay - 3, 4, 7);
        px('#d8385c', 0.72, ax + 2, ay - 2, 3, 5);
        px('#ffffff', 0.95, ax - 1, ay - 1, 2, 3);
      }

      // 5. Ondas de choque concentricas, relampagos de ki y pavesas en (418, 284)
      for (let rIdx = 0; rIdx < 2; rIdx++) {
        const rad = 4 + ((t * 2 + rIdx * 7) % 14);
        const opRing = Math.max(0.15, (1 - (rad - 4) / 14) * 0.9);
        for (let i = 0; i < 16; i++) {
          const a = (i * Math.PI * 2) / 16 + t * 0.08;
          const sx = Math.round(418 + Math.cos(a) * rad);
          const sy = Math.round(284 + Math.sin(a) * rad * 0.75);
          px(sx < 418 ? '#ffd84c' : '#38d8ff', opRing, sx, sy, 2, 1);
        }
      }
      for (let b = 0; b < 6; b++) {
        if ((t + b) % 3 === 0) continue;
        const ba = t * 0.37 + b * 1.05;
        const bl = 7 + ((t * 3 + b * 5) % 10);
        const colB = b % 2 === 0 ? '#ffe898' : '#78ecff';
        for (let s = 2; s <= bl; s += 2) {
          const jx = Math.round(Math.sin(s + t + b) * 1.4);
          px(colB, 0.88, 418 + Math.round(Math.cos(ba) * s) + jx, 284 + Math.round(Math.sin(ba) * s * 0.8), 1, 1);
        }
      }
      if (clash > 0.2) {
        px('#ffffff', 0.98 * clash, 416, 282, 5, 5);
      }

      // 6. Faro del Tren Infinito y fulgor vivo en la caldera (x=140..275)
      const fPulse = 0.7 + 0.3 * osc(0.22, 0.4);
      px('#ff8438', 0.22 * fPulse * env, 141, 222, 14, 9);
      for (let i = 1; i <= 34; i += 2) {
        const rh = 1 + Math.floor(i / 6);
        px('#ffe898', Math.max(0.03, (0.36 - i * 0.009) * fPulse * env), 225 + i, 238 - rh, 2, rh * 2);
      }
    }

    function pintaDemonTokito(t, nf) {
      const env = 0.65 + 0.35 * nf;

      // 1. Bancos de niebla turquesa de la Septima Postura deslizandose por el claro
      for (let i = 0; i < 6; i++) {
        const span = 350;
        const bx = 185 + ((Math.round(t * (1.2 + (i % 3) * 0.5)) + i * 64) % span);
        const by = 288 + (i % 3) * 11 + Math.round(Math.sin(t * 0.12 + i) * 2);
        const bw = 28 + (i % 3) * 14;
        px('#54e8cc', 0.16 * env, bx, by, bw, 3);
        px('#b8fff4', 0.22 * env, bx + 6, by + 1, Math.round(bw * 0.6), 1);
      }

      // 2. Melena menta, hoja Nichirin y arcos cortantes de Muichiro Tokito (cx=278, by=304)
      for (let h = 0; h < 5; h++) {
        const hx = 259 + h * 3;
        const hy = 283 + h + Math.round(Math.sin(t * 0.45 + h) * 1.4);
        px(h > 2 ? '#d8fff8' : '#74f0dc', 0.85, hx, hy, 2, 2);
      }
      const bladeS = (t * 2) % 18;
      px('#e8fffc', 0.95, 287 + bladeS, 285 - Math.floor(bladeS / 4), 3, 1);

      // Arcos de niebla veloces viajando desde Tokito (x=302) hasta Gyokko (x=448)
      for (let a = 0; a < 3; a++) {
        const prog = ((t * 0.10 + a * 0.33) % 1.0);
        const sx = Math.round(304 + prog * 144);
        const sy = Math.round(284 + Math.sin(prog * Math.PI * 2 + a) * 9);
        for (let dy = -6; dy <= 6; dy += 2) {
          const arch = Math.round((dy * dy) / 7);
          px('#54e8cc', 0.72, sx - arch, sy + dy, 3, 2);
          if (Math.abs(dy) <= 3) px('#e8fffc', 0.92, sx - arch + 1, sy + dy, 2, 1);
        }
      }

      // Destello relampago en X (Septima Postura: Neblina) sobre Gyokko
      const flashTick = t % 28;
      if (flashTick < 9) {
        const fAl = 1 - flashTick / 9;
        px('#54e8cc', 0.18 * fAl * env, 424, 260, 56, 42);
        for (let d = -14; d <= 14; d += 2) {
          px('#74f8e8', 0.86 * fAl, 444 + d, 280 + Math.round(d * 0.65), 2, 2);
          px('#ffffff', 0.95 * fAl, 444 + d, 280 - Math.round(d * 0.65), 2, 2);
        }
      }

      // 3. Tentaculos acuaticos agitados, ojos y agujas de Gyokko (cx=468, by=308)
      for (const side of [-1, 1]) {
        for (let seg = 0; seg < 12; seg++) {
          const u = seg / 11;
          const wave = Math.sin(t * 0.42 + u * 4.5 + side) * (2.5 + u * 3.5);
          const tx = Math.round(468 + side * (13 + seg * 2.5));
          const ty = Math.round(294 - Math.sin(u * 3.6) * 14 - u * 9 + wave);
          const rt = u < 0.5 ? 2 : 1;
          px('#2898a8', 0.75, tx - rt, ty - rt, rt * 2 + 1, rt * 2 + 1);
          px('#98fff0', 0.86, tx, ty, rt, rt);
        }
        // Salpicaduras en las puntas de los tentaculos
        if ((t + (side > 0 ? 1 : 0)) % 2 === 0) {
          const sxp = 468 + side * (36 + (t % 5));
          const syp = 266 + Math.round(Math.cos(t * 0.5 + side) * 4);
          px('#d8fffc', 0.88, sxp, syp, 2, 2);
        }
      }
      // Ojos verticales brillantes de Gyokko
      px('#ff4878', 0.92, 467, 270, 2, 2);
      px('#ffd858', 0.90, 467, 275, 2, 1);

      // Agujas de agua demoníacas chocando con la niebla en (392, 280)
      for (let j = 0; j < 3; j++) {
        const gp = ((t * 0.12 + j * 0.33) % 1.0);
        const gx = Math.round(452 - gp * 60);
        const gy = Math.round(278 + (j - 1) * 5 + Math.sin(t * 0.5 + j) * 2);
        px('#54e4d4', 0.86, gx, gy, 5, 1);
        px('#ff5488', 0.80, gx + 4, gy, 2, 1);
      }
      if (t % 3 !== 0) {
        px('#ffffff', 0.90, 391, 279, 3, 3);
        px('#ff6494', 0.80, 394 + (t % 4) - 2, 275 + ((t * 2) % 6), 2, 2);
      }
    }

    function pintaDemonGlicinias(t, nf) {
      const env = 0.65 + 0.35 * nf;

      // 1. Petalos luminosos de glicinia meciendo la brisa por todo el santuario
      const wCols = ['#c884ff', '#f0d8ff', '#9248e8', '#e6b8ff'];
      for (let i = 0; i < 20; i++) {
        const speedY = 0.45 + (i % 4) * 0.18;
        const speedX = 0.25 + (i % 3) * 0.12;
        const py = 116 + ((Math.round(t * speedY) + i * 19) % 218);
        const px0 = 36 + ((Math.round(t * speedX + Math.sin(t * 0.08 + i) * 14) + i * 31) % 568);
        const horiz = (Math.floor(t / 5) + i) % 2 === 0;
        px(wCols[i % 4], 0.82 * env, px0, py, horiz ? 2 : 1, horiz ? 1 : 2);
      }
      // Destellos bioluminiscentes en los racimos izquierdo y derecho y dintel del Torii
      for (let g = 0; g < 10; g++) {
        const gx = g < 4 ? (52 + g * 44) : g < 8 ? (418 + (g - 4) * 44) : (276 + (g - 8) * 86);
        const gy = g < 8 ? (136 + (g % 3) * 14) : 150;
        const op = (0.35 + 0.65 * osc(0.16, g * 1.3)) * env;
        px('#f0d8ff', op, gx, gy, 2, 2);
      }

      // 2. Llama sagrada viva danzando sobre la Katana Nichirin del altar (x=306..344, y=276..288)
      const pulseF = 0.72 + 0.28 * osc(0.24, 0.7);
      px('#ff7828', 0.16 * pulseF * env, 300, 266, 50, 24);
      for (let k = 0; k < 9; k++) {
        const kx = 307 + k * 4;
        const kyBase = 285 - Math.floor((k * 4 + 13) / 5);
        const fh = 3 + ((Math.floor(t * 0.7) + k * 3) % 7);
        const sway = Math.round(Math.sin(t * 0.5 + k * 0.9) * 1.2);
        px('#ff3820', 0.78, kx + sway, kyBase - fh, 2, 3);
        px('#ff9428', 0.88, kx, kyBase - Math.max(2, fh - 2), 2, 3);
        px('#fff4b8', 0.95, kx, kyBase - 1, 2, 2);
      }
      // Pavesas doradas elevandose hacia el Torii desde la hoja
      for (let e = 0; e < 5; e++) {
        const rise = ((t * 1.2 + e * 9) % 34);
        const ex = 310 + ((e * 11) % 30) + Math.round(Math.sin(t * 0.2 + e * 1.7) * 4);
        const ey = 280 - Math.round(rise);
        px(e % 2 === 0 ? '#ffe888' : '#ff9838', Math.max(0.1, (1 - rise / 34) * 0.88), ex, ey, 1, 2);
      }
    }

    function pintaNarutoBaryon(t, nf) {
      const env = 0.68 + 0.32 * nf;
      const kPulse = 0.5 + 0.5 * Math.sin(t * 0.26);

      // 1. Ojos rasgados (x=121, 154, y=175) y aliento chakra de la silueta de Kurama (136, 286)
      for (const ex of [121, 154]) {
        px('#ff2c18', 0.48 * kPulse * env, ex - 4, 173, 8, 5);
        px('#ff9430', 0.88, ex - 2, 174, 5, 3);
        px('#fff0a8', 0.96, ex, 174, 2, 2);
      }
      for (let w = 0; w < 4; w++) {
        const wy = 192 + w * 4 - ((t + w * 2) % 6);
        px('#ff5a24', 0.36 * env, 130 + ((w * 7) % 16), wy, 2, 3);
      }

      // 2. Nueve colas de chakra Modo Baryon ondeando (centro 192, 314)
      for (let k = 0; k < 9; k++) {
        const baseAng = -2.42 + k * 0.24;
        const len = 64 + (k % 3) * 18;
        for (let s = 2; s < 10; s++) {
          const u = s / 10;
          const sway = Math.sin(t * 0.34 + k * 0.9 + u * 3.1) * (4 + u * 8);
          const tx = Math.round(192 + Math.cos(baseAng) * (len * u) + sway * 0.45);
          const ty = Math.round(314 + Math.sin(baseAng) * (len * u) + sway * 0.3);
          if (tx < 48 || tx > 258 || ty < 178 || ty > 342) continue;
          const tip = s > 7;
          px(tip ? '#ffd068' : (s % 2 === 0 ? '#ff3c24' : '#ff7c2c'), (0.28 + 0.36 * (1 - u)) * env, tx, ty, tip ? 2 : 3, 2);
        }
      }

      // 3. Manto Baryon, cuernos (188/204, 300) y pavesas ascendiendo en Naruto (198, 344)
      for (let p = 0; p < 7; p++) {
        const rise = ((t * 1.7 + p * 5) % 28);
        const ax = 188 + ((p * 5) % 20) + Math.round(Math.sin(t * 0.45 + p) * 2);
        const ay = 340 - Math.round(rise);
        px(rise > 18 ? '#ff2c1c' : '#ff9c38', Math.max(0.12, (1 - rise / 28) * 0.78), ax, ay, 2, 2);
      }
      px('#ffe088', 0.85, 188, 300 + (t % 2), 1, 2);
      px('#ffe088', 0.85, 204, 300 + ((t + 1) % 2), 1, 2);

      // 4. Baryon Rasengan giratorio en la mano adelantada (220, 320)
      const rPulse = 0.65 + 0.35 * Math.sin(t * 0.65);
      px('#ff4020', 0.35 * rPulse, 214, 314, 13, 13);
      px('#ff9e3c', 0.80, 217, 317, 7, 7);
      px('#fff6dc', 0.96, 219, 319, 3, 3);
      for (let r = 0; r < 4; r++) {
        const ra = t * 0.55 + r * (Math.PI / 2);
        const rx = 220 + Math.round(Math.cos(ra) * 5.2);
        const ry = 320 + Math.round(Math.sin(ra) * 5.2);
        px(r % 2 === 0 ? '#ffe898' : '#ff4c28', 0.92, rx, ry, 2, 2);
      }

      // 5. Chispas de choque entre Baryon Rasengan (220, 320) e Isshiki/cubos (322, 280)
      if (t % 4 !== 0) {
        const cxm = 258 + ((t * 7) % 48);
        const cym = 304 - Math.round((cxm - 258) * 0.4) + Math.round(Math.sin(t * 0.9) * 5);
        px('#ffd878', 0.90, cxm, cym, 3, 1);
        px('#ff4828', 0.72, cxm - 2, cym + 1, 2, 1);
      }

      // 6. Cubos Daikokuten levitando (322,280), (290,294), (346,266)
      const cubos = [[322, 280, 7], [290, 294, 5], [346, 266, 4]];
      for (let i = 0; i < cubos.length; i++) {
        const bob = Math.round(Math.sin(t * 0.24 + i * 2.1) * 3);
        const cx = cubos[i][0];
        const cy = cubos[i][1] + bob;
        const sz = cubos[i][2];
        const flash = ((t + i * 11) % 36) < 4;
        px(flash ? '#ffb8ff' : '#c044ff', (flash ? 0.78 : 0.46) * env, cx - sz, cy - sz, sz * 2, 1);
        px('#8828c8', 0.36 * env, cx - sz, cy + sz - 1, sz * 2, 1);
      }

      // 7. Rueda Dharmachakra rotando detras de Isshiki (394, 282, r=23) y ojo Dharmagan (389, 309)
      for (let s = 0; s < 8; s++) {
        const wa = t * 0.14 + (s * Math.PI) / 4;
        const wx = Math.round(394 + Math.cos(wa) * 23);
        const wy = Math.round(282 + Math.sin(wa) * 23);
        px(s % 2 === 0 ? '#ffe878' : '#ffffff', 0.75 * env, wx, wy, 2, 2);
      }
      px('#c848ff', 0.42 * kPulse * env, 387, 308, 5, 3);
    }

    function pintaNarutoKonoha(t, nf) {
      const env = 0.60 + 0.40 * nf;

      // 1. Banderin en la cupula del Edificio Hokage (218, 224)
      const flagBob = Math.round(Math.sin(t * 0.35) * 1.2);
      px('#d84030', 0.85, 220, 224 + flagBob, 5, 2);
      px('#f8e8c8', 0.65 * env, 217, 228, 3, 1);

      // 2. Faroles y vapor aromatico de Ichiraku Ramen (44..90, 272)
      const sway = Math.round(Math.sin(t * 0.22) * 1.1);
      for (const lx of [46, 66, 88]) {
        px('#ff5232', 0.75 * env, lx + sway, 255, 3, 4);
        px('#ffe8a0', 0.50 * env, lx + sway, 256, 1, 2);
      }
      for (let v = 0; v < 4; v++) {
        const vr = ((t * 1.1 + v * 6) % 20);
        px('#f0f4f8', Math.max(0.08, (1 - vr / 20) * 0.42), 66 + Math.round(Math.sin(t * 0.2 + v) * 2), 248 - Math.round(vr), 2, 2);
      }

      // 3. Capas ondeantes de Naruto Hokage (342, 274) y Sasuke (370, 274)
      const cloakW = Math.round(Math.sin(t * 0.30) * 1.4);
      px('#ff7828', 0.82, 338 + cloakW, 265, 3, 4);
      px('#fff4e4', 0.78, 344 + cloakW, 261, 3, 3);
      px('#383058', 0.80, 372 - cloakW, 263, 3, 5);
      if (nf > 0.3) {
        px('#c870ff', 0.70 * env, 368, 256, 1, 1);
      }

      // 4. Hojas de Konoha arrastradas por la brisa (manteniendo libre la columna derecha)
      for (let i = 0; i < 7; i++) {
        const lx = 36 + ((Math.round(t * (1.3 + (i % 3) * 0.45)) + i * 59) % 404);
        const ly = 135 + (i % 4) * 32 + Math.round(Math.sin(t * 0.18 + i * 1.4) * 7);
        const lCol = nf > 0.55 ? '#4ca868' : (i % 2 === 0 ? '#74d05c' : '#e89844');
        px(lCol, 0.72, lx, ly, 2, 2);
      }

      // 5. Destellos suaves sobre el Rio Naka (y >= 284, x <= 440)
      for (let r = 0; r < 10; r++) {
        if ((t + r) % 3 === 0) continue;
        const rx = 44 + ((r * 39 + t * 2) % 390);
        const ry = 287 + (r % 5) * 9;
        px(nf > 0.55 ? '#98c8ff' : '#fff0b8', 0.42 * env, rx, ry, 4 + (r % 3) * 2, 1);
      }
    }

    function pintaNarutoValle(t, nf) {
      const env = 0.65 + 0.35 * nf;

      // 1. Cascada viva del Valle del Fin (x=244..324, y=151..280)
      for (let l = 0; l < 6; l++) {
        const wx = 250 + l * 13;
        const off = (t * 4 + l * 21) % 120;
        for (let k = 0; k < 3; k++) {
          const wy = 154 + ((off + k * 42) % 120);
          px(k === 0 ? '#ffffff' : '#b8eeff', 0.62 * env, wx, wy, 2, 6);
        }
      }
      for (let m = 0; m < 8; m++) {
        const mx = 242 + m * 11 + Math.round(Math.sin(t * 0.25 + m) * 2);
        const my = 275 + ((t + m * 3) % 5);
        px('#e8fbff', 0.52 * env, mx, my, 5, 3);
      }

      // 2. Choque Rasengan (277, 248) vs Chidori (291, 248) en (284, 248)
      const clash = 0.6 + 0.4 * Math.sin(t * 0.6);
      px('#48c4ff', 0.32 * clash, 271, 242, 12, 12);
      px('#d8f8ff', 0.90, 275, 246, 5, 5);
      for (let s = 0; s < 4; s++) {
        const sa = t * 0.65 + s * (Math.PI / 2);
        px('#80e4ff', 0.92, 277 + Math.round(Math.cos(sa) * 4), 248 + Math.round(Math.sin(sa) * 4), 2, 2);
      }

      // Rayos del Chidori alrededor de (291, 248)
      px('#a8d4ff', 0.32 * clash, 285, 241, 14, 14);
      for (let b = 0; b < 5; b++) {
        if ((t + b) % 3 === 0) continue;
        const ba = t * 0.48 + b * 1.25;
        const bl = 5 + ((t * 2 + b * 3) % 8);
        for (let d = 2; d <= bl; d += 2) {
          const j = Math.round(Math.sin(d + t + b) * 1.4);
          px(b % 2 === 0 ? '#ffffff' : '#b8b0ff', 0.92, 291 + Math.round(Math.cos(ba) * d) + j, 248 + Math.round(Math.sin(ba) * d), 1, 1);
        }
      }

      // Nucleo central de impacto y onda expansiva (284, 248)
      px('#ffffff', 0.96 * clash, 282, 246, 5, 5);
      const ringR = 5 + ((t * 2) % 20);
      const ringAl = Math.max(0.08, (1 - (ringR - 5) / 20) * 0.72);
      for (let a = 0; a < 12; a++) {
        const ang = (a * Math.PI * 2) / 12 + t * 0.1;
        px(a % 2 === 0 ? '#88e8ff' : '#ffffff', ringAl, 284 + Math.round(Math.cos(ang) * ringR), 248 + Math.round(Math.sin(ang) * ringR * 0.8), 2, 2);
      }

      // Aura de Naruto (254, 268) y Sasuke (314, 268)
      px('#ff9838', 0.65 * clash, 253, 255 - (t % 3), 2, 3);
      px('#9880ff', 0.65 * clash, 314, 255 - ((t + 1) % 3), 2, 3);

      // 3. Reflejo y ondas en la poza del Valle del Fin (284, 316)
      const poolW = 10 + ((t * 2) % 18);
      px('#90e8ff', 0.40 * clash, 284 - poolW, 315, poolW * 2, 2);
      px('#ffffff', 0.55 * clash, 279, 316, 10, 1);
    }

    function pintaJujutsu(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.55 + 0.45 * nf + aBoost);
      const pulse = 0.72 + 0.28 * Math.sin(t * 0.14);

      // 1. Agujero negro de Vacío Infinito pulsando detrás (446, 146)
      for (let a = 0; a < 10; a++) {
        const ang = (a * Math.PI * 2) / 10 + t * 0.06;
        const rX = 36 + Math.round(Math.sin(t * 0.1 + a) * 2);
        const rY = 12;
        px(a % 2 === 0 ? '#7dd3fc' : '#c084fc', 0.68 * al, 446 + Math.round(Math.cos(ang) * rX), 146 + Math.round(Math.sin(ang) * rY), 2, 1);
      }
      px('#ffffff', 0.42 * al * pulse, 444, 145, 4, 2);

      // 2. Santuario Malevolente (132, 210) — ojos demoníacos, boca y ascuas del santuario
      const eyeAl = Math.min(1, (0.55 + 0.45 * Math.sin(t * 0.16)) * al);
      px('#fb7185', 0.88 * eyeAl, 125, 189, 2, 2);
      px('#fb7185', 0.88 * eyeAl, 139, 189, 2, 2);
      px('#ff2848', 0.55 * al, 120, 232 + (t % 3 === 0 ? -1 : 0), 24, 2);
      for (let s = 0; s < 5; s++) {
        const sy = 188 + ((s * 17 + t * 3) % 68);
        const sx = 98 + ((s * 29) % 68);
        px(s % 2 === 0 ? '#ff4468' : '#fda4af', 0.72 * al, sx, sy, 5, 1);
      }

      // 3. Cortes Desmantelar de Sukuna (214, 348) hacia Gojo (398, 348) y aura azul
      px('#fb7185', 0.60 * al, 214, 314 - (t % 3), 2, 4);
      px('#ef4444', 0.60 * al, 224, 318 - ((t + 1) % 3), 2, 4);
      for (let k = 0; k < 4; k++) {
        const prog = ((t * 3 + k * 7) % 36);
        const sx0 = 242 + prog;
        const sy0 = 294 + ((k * 7) % 18) - Math.round(prog * 0.18);
        for (let d = 0; d < 7; d++) {
          px(d > 4 ? '#ffffff' : '#ff3355', 0.88 * al, sx0 + d, sy0 + (k % 2 === 0 ? d >> 1 : -(d >> 1)), 1, 1);
        }
      }

      // 4. Rojo/Azul de Gojo y Choque Púrpura Vacío (306, 298)
      px('#38bdf8', 0.68 * al, 396, 316 - ((t + 2) % 3), 2, 4);
      const rOrb = 10 + Math.round(Math.sin(t * 0.2) * 2);
      const rAng = t * 0.22;
      px('#fb7185', 0.90 * al, 306 + Math.round(Math.cos(rAng) * rOrb), 298 + Math.round(Math.sin(rAng) * rOrb * 0.6), 3, 3);
      px('#38bdf8', 0.90 * al, 306 - Math.round(Math.cos(rAng) * rOrb), 298 - Math.round(Math.sin(rAng) * rOrb * 0.6), 3, 3);

      const coreR = Math.round(4 + 3 * pulse + aBoost * 8);
      px('#9333ea', 0.40 * al, 306 - coreR - 4, 298 - coreR - 2, coreR * 2 + 8, coreR * 2 + 4);
      px('#e879f9', 0.72 * al, 306 - coreR, 298 - coreR, coreR * 2, coreR * 2);
      px('#fdf4ff', 0.96 * al, 304, 296, 5, 5);

      const wave = 8 + ((t * 2) % 24);
      const wAl = Math.max(0.08, (1 - (wave - 8) / 24) * 0.75 * al);
      for (let a = 0; a < 12; a++) {
        const ang = (a * Math.PI * 2) / 12 + t * 0.08;
        px(a % 2 === 0 ? '#e879f9' : '#7dd3fc', wAl, 306 + Math.round(Math.cos(ang) * wave), 298 + Math.round(Math.sin(ang) * wave * 0.7), 2, 2);
      }

      const rw = 12 + Math.round(4 * pulse);
      px('#c084fc', 0.42 * al, 306 - rw, 342, rw * 2, 2);
    }

    function pintaJujutsuSec(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.58 + 0.42 * nf + aBoost);
      const bob = Math.round(Math.sin(t * 0.12) * 2);

      // 1. Prisión Confinadora (314, 282)
      px('#eab308', 0.45 * al, 306, 274 + bob, 16, 16);
      if (t % 29 !== 0) {
        px('#fff8e8', 0.92 * al, 312, 280 + bob, 4, 4);
        px('#e11d48', 0.95 * al, 313, 281 + bob, 2, 2);
      }
      for (let c = 0; c < 4; c++) {
        const ang = c * Math.PI * 0.5 + t * 0.07;
        px('#facc15', 0.78 * al, 314 + Math.round(Math.cos(ang) * 14), 282 + bob + Math.round(Math.sin(ang) * 11), 2, 2);
      }

      // 2. Destello Negro de Yuji Itadori (puño 187, 323)
      const bfPulse = (t % 16) < 4;
      px('#09090b', 0.90, 184, 320, 7, 7);
      px(bfPulse ? '#ffffff' : '#fb7185', 0.92 * al, 186, 322, 3, 3);
      for (let b = 0; b < 6; b++) {
        const ang = t * 0.45 + b * 1.05;
        const dist = 5 + ((t * 2 + b * 3) % 10);
        px(b % 2 === 0 ? '#e11d48' : '#111827', 0.88, 187 + Math.round(Math.cos(ang) * dist), 323 + Math.round(Math.sin(ang) * dist), 2, 1);
      }

      // 3. Sombras de Megumi (402, 348), Perro Divino (446, 314) y rayos de Nue (390, 200)
      for (let s = 0; s < 5; s++) {
        const sy = 342 - ((t * 2 + s * 6) % 24);
        const sx = 398 + Math.round(Math.sin(t * 0.1 + s) * 8) + (s - 2) * 4;
        px(s % 2 === 0 ? '#38bdf8' : '#1e293b', 0.72 * al, sx, sy, 2, 2);
      }
      px('#38bdf8', 0.90 * al, 446, 314, 2, 1);
      if ((t % 14) < 3) {
        px('#bae6fd', 0.86 * al, 388 + (t % 5), 202, 2, 14);
      }
    }

    function pintaJujutsuBloq(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.58 + 0.42 * nf + aBoost);
      const sway = Math.round(Math.sin(t * 0.09) * 1.5);

      for (const ox of [284, 298, 312, 328, 342, 356]) {
        px('#fef3c7', 0.88 * al, ox + sway, 162, 2, 5);
        px('#ef4444', 0.78 * al, ox + sway, 164, 1, 2);
      }

      const pulse = 0.65 + 0.35 * Math.sin(t * 0.14);
      px('#e11d48', 0.38 * al * pulse, 313, 283, 14, 14);
      px('#fb7185', 0.88 * al * pulse, 318, 287 + (t % 6 < 3 ? 0 : -1), 4, 7);
      px('#fef2f2', 0.88 * al, 319, 288, 2, 2);

      for (let w = 0; w < 6; w++) {
        const prog = (t * 1.2 + w * 9) % 42;
        const wx = 290 + w * 12 + Math.round(Math.sin(t * 0.08 + w) * 3);
        const wy = 306 - Math.round(prog);
        px(w % 2 === 0 ? '#a855f7' : '#f43f5e', Math.max(0.15, (1 - prog / 42) * 0.80 * al), wx, wy, 2, 2);
      }
      for (const [fx, fy] of [[228, 236], [412, 236], [182, 310], [458, 310]]) {
        px('#fef08a', 0.65 * al * (0.7 + 0.3 * Math.sin(t * 0.2 + fx)), fx - 1, fy - 1, 3, 3);
      }
    }

    function pintaAotRumbling(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.58 + 0.42 * nf + aBoost);
      const pulse = 0.70 + 0.30 * Math.sin(t * 0.14);

      // Ojos esmeralda del Fundador (294, 134) + vapor y brasas de Colosales
      px('#4ade80', 0.92 * al * pulse, 289, 134, 2, 2);
      px('#4ade80', 0.92 * al * pulse, 297, 134, 2, 2);
      for (let i = 0; i < 6; i++) {
        const tx = [48, 124, 218, 376, 450, 174][i];
        const py = 248 - ((t * 2 + i * 11) % 52);
        const pxX = tx + Math.round(Math.sin(t * 0.08 + i) * 6);
        px(i % 2 === 0 ? '#fb923c' : '#cbd5e1', 0.55 * al, pxX, py, 3, 2);
      }

      // Remolino de cuchillas de Levi (392, 322) y bufanda roja de Mikasa (210, 326)
      for (let a = 0; a < 8; a++) {
        const ang = (a * Math.PI * 2) / 8 + t * 0.42;
        px(a % 2 === 0 ? '#f8fafc' : '#38bdf8', 0.85 * al, 392 + Math.round(Math.cos(ang) * 18), 322 + Math.round(Math.sin(ang) * 14), 3, 2);
      }
      px('#ef4444', 0.85 * al, 206 + (t % 3) - 1, 315, 6, 2);
    }

    function pintaAotShiganshina(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.60 + 0.40 * nf + aBoost);
      const pulse = 0.65 + 0.35 * Math.sin(t * 0.18);

      px('#fef08a', 0.92 * al * pulse, 190, 116, 3, 2);
      px('#fef08a', 0.92 * al * pulse, 212, 116, 3, 2);
      if ((t % 18) < 5) {
        for (let k = 0; k < 8; k++) {
          px(k % 2 === 0 ? '#fef08a' : '#f97316', 0.88 * al, 200 + Math.round(Math.sin(t + k) * 6), 24 + k * 9, 2, 7);
        }
      }
      for (let s = 0; s < 5; s++) {
        const sy = 194 - ((t + s * 9) % 34);
        px('#e2e8f0', 0.40 * al, 148 + s * 28 + Math.round(Math.sin(t * 0.06 + s) * 4), sy, 6, 3);
      }
      px('#ef4444', 0.80 * al, 320 + Math.round(Math.sin(t * 0.2) * 3), 270 - (t % 8), 2, 4);
    }

    function pintaAotPaths(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.60 + 0.40 * nf + aBoost);
      const pulse = 0.70 + 0.30 * Math.sin(t * 0.11);

      px('#e0f2fe', 0.45 * al * pulse, 316, 134, 8, 120);
      for (let i = 0; i < 8; i++) {
        const gy = 250 - ((t * 2 + i * 16) % 140);
        const gx = 320 + Math.round(Math.sin(t * 0.09 + i * 1.3) * (gy < 140 ? 38 : 7));
        px(i % 2 === 0 ? '#fde047' : '#67e8f9', 0.82 * al, gx, gy, 2, 2);
      }
      px('#f8fafc', 0.72 * al * pulse, 319, 312, 2, 6);
    }

    function pintaOpGear5(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.60 + 0.40 * nf + aBoost);
      const pulse = 0.68 + 0.32 * Math.sin(t * 0.16);

      // Haki del Conquistador de Luffy Nika (204, 348) + Bajrang Gun (236, 306)
      for (let h = 0; h < 6; h++) {
        const ang = t * 0.32 + h * 1.04;
        const dist = 8 + ((t * 2 + h * 4) % 16);
        px(h % 2 === 0 ? '#f43f5e' : '#09090b', 0.90 * al, 212 + Math.round(Math.cos(ang) * dist), 322 + Math.round(Math.sin(ang) * dist), 2, 2);
      }
      // Choque Bajrang Gun vs Bolo Breath (308, 276) y ojos de Kaido (358, 204)
      const cr = Math.round(5 + 3 * pulse + aBoost * 8);
      px('#fb923c', 0.65 * al, 308 - cr, 276 - cr, cr * 2, cr * 2);
      px('#ffffff', 0.94 * al, 306, 274, 4, 4);
      px('#fef08a', 0.90 * al * pulse, 352, 199, 2, 2);
      for (let f = 0; f < 5; f++) {
        const u = ((t * 0.12 + f * 0.2) % 1.0);
        px(u < 0.5 ? '#ef4444' : '#fde047', 0.88 * al, Math.round(338 - u * 30), Math.round(214 + u * 62), 3, 3);
      }
    }

    function pintaOpSunny(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.30 : 0;
      const al = Math.min(1, 0.55 + 0.45 * nf + aBoost);
      const bob = Math.round(Math.sin(t * 0.08));

      for (const lx of [276, 332]) {
        px('#fef08a', 0.78 * al, lx - 1, 233 + bob, 3, 3);
      }
      px('#4ade80', 0.85 * al, 291, 215 + bob, 3, 3);
      px('#38bdf8', 0.85 * al, 313, 215 + bob, 3, 3);
      px('#e0f2fe', 0.50 * al, 256 + ((t * 2) % 92), 282, 12, 1);
    }

    function pintaOpPoneglyph(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.58 + 0.42 * nf + aBoost);

      for (let g = 0; g < 6; g++) {
        const idx = (t + g * 5) % 24;
        const gx = 180 + (idx % 5) * 7;
        const gy = 248 + Math.floor(idx / 5) * 14;
        px('#fde047', 0.85 * al, gx, gy, 2, 2);
      }
      for (let m = 0; m < 4; m++) {
        const ang = t * 0.16 + m * 1.57;
        px('#e879f9', 0.82 * al, 404 + Math.round(Math.cos(ang) * 13), 318 + Math.round(Math.sin(ang) * 9), 2, 2);
      }
    }

    function pintaDbzUi(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.62 + 0.38 * nf + aBoost);
      const pulse = 0.70 + 0.30 * Math.sin(t * 0.2);

      // Aura plateada-cian Ultra Instinto en Goku (202, 348)
      for (let u = 0; u < 6; u++) {
        const uy = 344 - ((t * 2 + u * 7) % 36);
        const ux = 202 + Math.round(Math.sin(t * 0.25 + u) * 14);
        px(u % 2 === 0 ? '#e0f2fe' : '#38bdf8', 0.85 * al, ux, uy, 2, 3);
      }
      // Kamehameha vs Supernova (386, 296) -> choque (304, 298)
      px('#38bdf8', 0.78 * al * pulse, 232 + (t % 12) * 5, 315 - (t % 12) * 1.4, 8, 3);
      const sr = Math.round(5 + 3 * pulse + aBoost * 6);
      px('#f97316', 0.65 * al, 386 - sr, 296 - sr, sr * 2, sr * 2);
      px('#fef08a', 0.92 * al * pulse, 302, 296, 5, 5);
    }

    function pintaDbzNamek(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.58 + 0.42 * nf + aBoost);
      const activeIdx = Math.floor(t / 4) % 7;

      for (let b = 0; b < 7; b++) {
        const bx = 240 + b * 16;
        px(b === activeIdx ? '#ffffff' : '#fde047', (b === activeIdx ? 0.95 : 0.55) * al, bx - 1, 274, 3, 3);
      }
      px('#ef4444', 0.90 * al, 282, 120, 2, 2);
      for (let k = 0; k < 5; k++) {
        const ky = 250 - ((t * 3 + k * 24) % 160);
        px('#fde047', 0.72 * al, 278 + Math.round(Math.sin(t * 0.1 + k) * 18), ky, 2, 5);
      }
    }

    function pintaDbzKame(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.30 : 0;
      const al = Math.min(1, 0.55 + 0.45 * nf + aBoost);

      px('#fef3c7', 0.78 * al, 185, 213, 4, 4);
      const rGlow = 0.6 + 0.4 * Math.sin(t * 0.14);
      px('#fde047', 0.85 * al * rGlow, 421, 255, 3, 3);
      const sy = 176 - (t % 20);
      px('#fce7f3', Math.max(0.15, (1 - (t % 20) / 20) * 0.50), 206 + Math.round(Math.sin(t * 0.2) * 3), sy, 3, 2);
      px('#fde68a', 0.65 * al, 234 + (t % 16), 130, 2, 2);
    }

    function pintaCyberSandevistan(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.60 + 0.40 * nf + aBoost);
      const cols = ['#4ade80', '#22d3ee', '#f43f5e'];

      for (let s = 0; s < 3; s++) {
        const jitter = (t + s) % 3;
        px(cols[s], 0.52 * al, 178 + s * 16 - jitter, 314, 10, 14);
      }
      px('#22d3ee', 0.90 * al, 227, 316 + (t % 4), 2, 6);
      // Monofilo pulsante de Lucy (328, 308) + faros Quadra + AV
      const mU = ((t * 3) % 40) / 40;
      px('#fde047', 0.92 * al, Math.round(370 - mU * 82), Math.round(328 - Math.sin(mU * Math.PI * 1.35) * 26), 3, 2);
      px('#ef4444', 0.80 * al * (0.7 + 0.3 * Math.sin(t * 0.25)), 40, 319, 6, 2);
      px('#38bdf8', 0.82 * al, (92 + (t * 2)) % 460, 116, 4, 2);
    }

    function pintaCyberMoon(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.30 : 0;
      const al = Math.min(1, 0.58 + 0.42 * nf + aBoost);

      // Monorraíl NCART deslizando por viaducto y=219..225 + balizas de azotea
      const tx = ((96 + t * 2) % 440);
      px('#38bdf8', 0.85 * al, tx, 221, 18, 3);
      for (const bx of [42, 148, 240, 396]) {
        px((t + bx) % 16 < 8 ? '#38bdf8' : '#f472b6', 0.88 * al, bx, 259, 2, 2);
      }
      for (let p = 0; p < 4; p++) {
        const gy = 290 - ((t + p * 8) % 30);
        px('#bae6fd', 0.72 * al, 300 + p * 10 + Math.round(Math.sin(t * 0.1 + p) * 4), gy, 2, 2);
      }
    }

    function pintaCyberBloq(t, nf) {
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;
      const al = Math.min(1, 0.60 + 0.40 * nf + aBoost);

      // Onda neural por las 7 vértebras del Apogee Sandevistan (x=286..352, y=317)
      const activeSeg = Math.floor(t / 2) % 7;
      for (let s = 0; s < 7; s++) {
        const vx = 286 + s * 11;
        px(s === activeSeg ? '#ffffff' : (s % 2 === 0 ? '#22d3ee' : '#4ade80'), (s === activeSeg ? 0.96 : 0.68) * al, vx - 1, 315, 3, 5);
      }
      if ((t % 19) !== 0) {
        px('#f43f5e', 0.78 * al, 96, 166, 72, 1);
      }
      px('#4ade80', 0.60 * al * (0.6 + 0.4 * Math.sin(t * 0.15)), 316, 194, 8, 8);
    }

    function climaEfectivo(T, fecha) {
      const m = state.clima || 'normal';
      if (m !== 'auto') return m;
      const tid = state.tema || '';
      const h = fecha ? fecha.getHours() : 21;
      if ((tid === 'spiderman-miles-morales' && (h >= 20 || h < 5)) || tid === 'cyberpunk-edgerunners') return 'lluvia';
      if (tid === 'stranger-things' && h % 2 === 1) return 'tormenta';
      if (tid === 'dragon-ball-z' && h % 3 === 0) return 'tormenta';
      if (tid === 'attack-on-titan') return 'ceniza';
      if (tid === 'demon-slayer' || tid === 'harry-potter' || tid === 'jujutsu-kaisen') return 'niebla';
      if (tid === 'fittoa' && (h < 7 || h >= 22)) return 'niebla';
      return 'normal';
    }

    function pintaClima(t, wB, nf, fecha) {
      const modo = climaEfectivo(state.T, fecha);
      state._climaActivo = modo;
      if (modo === 'normal') return;
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.35 : 0;

      if (modo === 'lluvia' || modo === 'tormenta') {
        const pesado = modo === 'tormenta';
        const wind = pesado ? -2.2 : -1.0;
        const vyBase = pesado ? 1.55 : 1.0;
        const col = pesado ? '#bae6fd' : '#7dd3fc';
        const alphaBase = (pesado ? 0.56 : 0.42) * (1 - 0.15 * wB) + aBoost * 0.25;

        for (let i = 0; i < GOTAS_CLIMA.length; i++) {
          if (!pesado && i % 3 === 2) continue;
          const g = GOTAS_CLIMA[i];
          const gx = (((g[0] + t * wind * 2.2) % 640) + 640) % 640;
          const gy = ((g[1] + t * g[3] * vyBase) % 390);
          const len = Math.round(g[2] * (pesado ? 1.35 : 1.0));
          for (let d = 0; d < len; d++) {
            px(col, alphaBase * (1 - d * 0.08), gx + (wind < -1.5 ? -Math.floor(d * 0.4) : 0), gy + d, 1, 1);
          }
          if (gy > 282 && gy < 386 && i % 7 === 0) {
            const rw = 2 + ((t + i) % 3);
            px('#e0f2fe', 0.30 * alphaBase, gx - rw, gy + 1, rw * 2, 1);
          }
        }
        if (pesado) {
          const flash = ((t * 17 + 13) % 131);
          if (flash < 2) {
            px('#e0f2fe', flash === 0 ? 0.22 : 0.10, 0, 0, 640, 280);
            const lx = 110 + ((t * 97) % 420);
            for (let y = 8; y < 230; y += 4) {
              const jx = lx + Math.round(Math.sin(y * 0.18 + t) * 7);
              px('#f8fafc', 0.92, jx, y, 2, 4);
              px('#7dd3fc', 0.45, jx - 1, y, 4, 4);
            }
          }
        }
      } else if (modo === 'nieve') {
        const alphaBase = 0.72 + 0.2 * nf;
        for (let i = 0; i < COPOS_CLIMA.length; i++) {
          const c = COPOS_CLIMA[i];
          const sx = (((c[0] + Math.sin(t * 0.04 + c[3]) * 14 + t * 0.15) % 640) + 640) % 640;
          const sy = (c[1] + t * c[2]) % 394;
          px(i % 4 === 0 ? '#e0f2fe' : '#ffffff', alphaBase, sx, sy, c[4], c[4]);
        }
      } else if (modo === 'ceniza') {
        const alphaBase = 0.64 + 0.25 * nf;
        for (let i = 0; i < COPOS_CLIMA.length; i++) {
          const c = COPOS_CLIMA[i];
          const sx = (((c[0] + t * 0.45 + Math.sin(t * 0.05 + c[3]) * 10) % 640) + 640) % 640;
          const sy = (((c[1] - t * c[2] * 0.85) % 394) + 394) % 394;
          px(i % 5 === 0 ? '#fb923c' : (i % 2 === 0 ? '#fed7aa' : '#94a3b8'), alphaBase, sx, sy, c[4], 1);
        }
      } else if (modo === 'niebla') {
        const col = wB > 0.5 ? '#f8fafc' : '#cbd5e1';
        for (let i = 0; i < 6; i++) {
          const mx = (((i * 120 + t * (0.25 + (i % 3) * 0.12)) % 760) + 760) % 760 - 120;
          const my = 252 + i * 14;
          const mw = 95 + (i % 3) * 45;
          px(col, 0.09 + 0.06 * nf, mx, my, mw, 5);
          px(col, 0.05 + 0.04 * nf, mx + 16, my - 2, mw - 32, 2);
        }
      }
    }

    function dispararEvento(tipo) {
      const opciones = ['cometa', 'invocacion', 'anomalia'];
      const elegido = opciones.includes(tipo)
        ? tipo
        : opciones[Math.floor(Math.random() * opciones.length)];
      state.evento = {
        tipo: elegido,
        inicioTick: state.tick,
        duracion: 96,
      };
      return elegido;
    }

    function pintaEventoEspecial(t) {
      const ev = state.evento;
      if (!ev) return;
      const age = t - ev.inicioTick;
      if (age < 0 || age > ev.duracion) {
        state.evento = null;
        return;
      }
      const p = age / ev.duracion;
      const env = p < 0.15 ? p / 0.15 : p > 0.8 ? (1 - p) / 0.2 : 1;

      if (ev.tipo === 'cometa') {
        const cx = 60 + p * 520;
        const cy = 28 + p * 125 + Math.sin(p * Math.PI) * -18;
        for (let k = 0; k < 18; k++) {
          const tx = cx - k * 3.6;
          const ty = cy - k * 1.1;
          const a = (1 - k / 18) * 0.85 * env;
          px(k < 4 ? '#ffffff' : k < 10 ? '#fde047' : '#38bdf8', a, tx, ty, k < 5 ? 3 : 2, k < 5 ? 2 : 1);
          if (k % 3 === 0) px('#fdf4ff', a * 0.8, tx - 2, ty + ((k % 2 === 0) ? 2 : -2), 1, 1);
        }
        px('#ffffff', 0.98 * env, cx - 1, cy - 1, 4, 4);
      } else if (ev.tipo === 'invocacion') {
        const col = '#facc15';
        const col2 = '#38bdf8';
        for (let a = 0; a < 16; a++) {
          const ang = (a * Math.PI * 2) / 16 + t * 0.08;
          const rx = Math.round(Math.cos(ang) * 34);
          const ry = Math.round(Math.sin(ang) * 14);
          px(a % 2 === 0 ? col : col2, 0.82 * env, 320 + rx, 224 + ry, 2, 2);
        }
        for (const pxCol of [302, 320, 338]) {
          px(col, 0.22 * env, pxCol - 1, 56, 3, 224);
          px('#ffffff', 0.50 * env, pxCol, 76, 1, 204);
        }
        px(col2, 0.35 * env, 296, 314, 48, 3);
      } else if (ev.tipo === 'anomalia') {
        for (let i = -24; i <= 24; i += 2) {
          const y = 148 + i;
          const x = 320 + Math.round(Math.sin(i * 0.35 + t * 0.25) * 6);
          px('#09090b', 0.85 * env, x - 2, y, 5, 2);
          px(i % 4 === 0 ? '#e11d48' : '#a855f7', 0.90 * env, x - 3, y, 2, 2);
          px('#f43f5e', 0.90 * env, x + 2, y, 2, 2);
        }
        for (let r = 0; r < 10; r++) {
          const ang = r * 0.62 + t * 0.14;
          const rad = 14 + (age % 22);
          px(r % 2 === 0 ? '#f43f5e' : '#c084fc', 0.72 * env, 320 + Math.round(Math.cos(ang) * rad), 148 + Math.round(Math.sin(ang) * rad * 0.7), 2, 1);
        }
      }
    }

    function toggleFoco() {
      state.foco.activo = !state.foco.activo;
      state.foco.lastTickMs = Date.now();
      return state.foco.activo;
    }

    function resetFoco() {
      state.foco.restSec = state.foco.descanso ? 5 * 60 : 25 * 60;
      state.foco.cicloSec = state.foco.restSec;
      state.foco.lastTickMs = Date.now();
    }

    function setFocoModo(esDescanso) {
      state.foco.descanso = !!esDescanso;
      resetFoco();
    }

    const TRACK_POOL = [
      ['Lullaby of Fittoa · OST', '84 BPM · FLACO LO-FI', 220.0],
      ['Kaikai Kitan · Domain OST', '128 BPM · CURSED SYNTH', 196.0],
      ['Silhouette · Baryon OST', '132 BPM · TAIKO & SHAMISEN', 246.94],
      ['DARK ARIA <LV2> · Sawano', '116 BPM · SINFÓNICO', 185.0],
      ['Sunflower · Brooklyn Mix', '90 BPM · BOOM-BAP LO-FI', 261.63],
      ["Kids / Synthwave '83", '104 BPM · ANALÓGICO', 207.65],
      ['Kamado Tanjiro no Uta', '78 BPM · SHAKUHACHI', 233.08],
      ["Hedwig's Theme · Celesta", '88 BPM · CELESTA', 293.66],
    ];

    const audioState = {
      ctx: null,
      analyser: null,
      data: null,
      masterGain: null,
      playing: false,
      timerId: null,
      step: 0,
      trackOffset: 0,
      externalMs: 0,
      externalVal: 0,
    };

    const audioCtrl = {
      isPlaying() {
        return !!audioState.playing;
      },
      startSynth() {
        if (typeof window === 'undefined') return false;
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return false;
        if (!audioState.ctx) {
          audioState.ctx = new AC();
          audioState.analyser = audioState.ctx.createAnalyser();
          audioState.analyser.fftSize = 64;
          audioState.data = new Uint8Array(audioState.analyser.frequencyBinCount);
          audioState.masterGain = audioState.ctx.createGain();
          audioState.masterGain.gain.value = 0.08;
          audioState.masterGain.connect(audioState.analyser);
          audioState.analyser.connect(audioState.ctx.destination);
        }
        if (audioState.ctx.state === 'suspended') {
          audioState.ctx.resume().catch(() => {});
        }
        if (audioState.playing) return true;
        audioState.playing = true;
        const playStep = () => {
          if (!audioState.playing || !audioState.ctx) return;
          const now = audioState.ctx.currentTime;
          const baseHz = TRACK_POOL[(audioState.trackOffset % TRACK_POOL.length + TRACK_POOL.length) % TRACK_POOL.length][2];
          const scale = [1, 1.189, 1.335, 1.498, 1.782, 2.0];
          const ratio = scale[(audioState.step * 2 + (audioState.step % 3)) % scale.length];
          const oscNode = audioState.ctx.createOscillator();
          const filt = audioState.ctx.createBiquadFilter();
          const g = audioState.ctx.createGain();
          oscNode.type = audioState.step % 4 === 0 ? 'triangle' : 'sine';
          oscNode.frequency.setValueAtTime(baseHz * ratio, now);
          filt.type = 'lowpass';
          filt.frequency.setValueAtTime(920, now);
          g.gain.setValueAtTime(0.001, now);
          g.gain.exponentialRampToValueAtTime(0.32, now + 0.08);
          g.gain.exponentialRampToValueAtTime(0.001, now + 0.85);
          oscNode.connect(filt);
          filt.connect(g);
          g.connect(audioState.masterGain);
          oscNode.start(now);
          oscNode.stop(now + 0.9);
          audioState.step++;
        };
        playStep();
        audioState.timerId = setInterval(playStep, 520);
        return true;
      },
      stopSynth() {
        audioState.playing = false;
        if (audioState.timerId) {
          clearInterval(audioState.timerId);
          audioState.timerId = null;
        }
        state.audioEnergy = 0;
        return false;
      },
      toggleSynth() {
        return audioState.playing ? audioCtrl.stopSynth() : audioCtrl.startSynth();
      },
      nextTrack() {
        audioState.trackOffset++;
        if (audioState.playing) audioState.step = 0;
      },
      prevTrack() {
        audioState.trackOffset--;
        if (audioState.playing) audioState.step = 0;
      },
      setExternalEnergy(v) {
        audioState.externalVal = Math.max(0, Math.min(1, Number(v) || 0));
        audioState.externalMs = Date.now();
      },
      sampleEnergy() {
        if (audioState.playing && audioState.analyser && audioState.data) {
          audioState.analyser.getByteFrequencyData(audioState.data);
          let sum = 0;
          const bins = Math.min(12, audioState.data.length);
          for (let i = 0; i < bins; i++) sum += audioState.data[i];
          const val = Math.min(1, (sum / (bins * 255)) * 2.2);
          state.audioEnergy = state.audioEnergy * 0.45 + val * 0.55;
          return state.audioEnergy;
        }
        if (Date.now() - audioState.externalMs < 1500) {
          state.audioEnergy = state.audioEnergy * 0.4 + audioState.externalVal * 0.6;
          return state.audioEnergy;
        }
        state.audioEnergy = state.audioEnergy * 0.85;
        return state.audioEnergy;
      },
    };

    async function cargarTema(id, { pantalla } = {}) {
      state.tema = id;
      if (pantalla) state.pantalla = pantalla;
      const modo = state.pantalla === 'secundaria'
        ? 'secundario'
        : state.pantalla === 'bloqueo'
          ? 'bloqueo'
          : 'principal';
      const basePrim = `temas/${id}`;
      const base = modo === 'secundario'
        ? `${basePrim}/secundario`
        : modo === 'bloqueo'
          ? `${basePrim}/bloqueo`
          : basePrim;
      const names = [
        'cielo-noche', 'cielo-dorado', 'cielo-dia',
        'escena-noche', 'escena-dorado', 'escena-dia',
        'nubes-noche', 'nubes-dorado', 'nubes-dia',
        'sol', 'luna',
      ];
      const bundle = (typeof window !== 'undefined' && window.PIXELZEN_BUNDLE) ? window.PIXELZEN_BUNDLE : null;
      const fbBase = 'file:///C:/Users/david/.gemini/antigravity-cli/brain/8747b389-799a-4632-897a-f7f55a4233c0/scratch/out_root/docs/';
      const rawBases = (typeof window !== 'undefined' && Array.isArray(window.PIXELZEN_ASSET_BASES) && window.PIXELZEN_ASSET_BASES.length)
        ? window.PIXELZEN_ASSET_BASES
        : [''];
      const bases = rawBases.indexOf(fbBase) === -1 ? rawBases.concat([fbBase]) : rawBases;

      async function loadImageFallback(rel) {
        let lastErr;
        for (const prefix of bases) {
          try {
            return await loadImage(`${prefix}${rel}`);
          } catch (err) { lastErr = err; }
        }
        throw lastErr || new Error(`No image: ${rel}`);
      }

      async function readJsonFallback(rel) {
        let lastErr;
        for (const prefix of bases) {
          try {
            const res = await fetch(`${prefix}${rel}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
          } catch (err) { lastErr = err; }
        }
        throw lastErr || new Error(`No json: ${rel}`);
      }

      async function intentaCarga(dir, keySuffix) {
        const bKey = keySuffix ? `${id}/${keySuffix}` : id;
        const [datosPack, ...imgs] = await Promise.all([
          (async () => {
            if (bundle && bundle[bKey]) return bundle[bKey];
            const [datos, tema] = await Promise.all([
              readJsonFallback(`${dir}/datos.json`),
              readJsonFallback(`${dir}/tema.json`),
            ]);
            return { datos, tema };
          })(),
          ...names.map(f => loadImageFallback(`${dir}/images/${f}.png`)),
        ]);
        return { datos: datosPack.datos, tema: datosPack.tema, imgs };
      }

      let cargado;
      try {
        cargado = await intentaCarga(base, modo === 'principal' ? '' : modo);
      } catch (_err) {
        if (modo === 'principal') throw _err;
        cargado = await intentaCarga(basePrim, '');
      }
      if (state.tema !== id) return null;
      const { datos, tema, imgs } = cargado;
      const map = {};
      names.forEach((k, i) => { map[k] = imgs[i]; });
      state.D = datos;
      state.T = tema;
      state.img = map;
      state.brillantes = datos.estrellas.filter(e => e[3] === 1);
      if (opts.onTemaLoaded) opts.onTemaLoaded(tema, id);
      return tema;
    }

    function render() {
      if (!state.D || !state.T) return;
      const D = state.D, T = state.T, I = state.img, t = state.tick;
      const fecha = fechaEfectiva();
      audioCtrl.sampleEnergy();
      if (state.modoHora === 0 && opts.autoHourlyEvent !== false) {
        const hNow = fecha.getHours();
        if (fecha.getMinutes() === 0 && fecha.getSeconds() < 4 && state._lastHourEvent !== hNow) {
          state._lastHourEvent = hNow;
          dispararEvento();
        }
      }
      const pOn = !!state.parallax;
      const pxSky = pOn ? Math.round((state.parallaxX || 0) * 2) : 0;
      const pySky = pOn ? Math.round((state.parallaxY || 0) * 1.5) : 0;
      const pxCloud = pOn ? Math.round((state.parallaxX || 0) * 3.5) : 0;
      const aBoost = state.audioReactivo ? (state.audioEnergy || 0) * 0.45 : 0;

      const s = sol(fecha);
      const wA = s.e <= -14 ? 0 : s.e >= 0 ? 1 : suave((s.e + 14) / 14);
      const wB = s.e <= 0 ? 0 : s.e >= 16 ? 1 : suave(s.e / 16);
      const nf = clamp01((4 - s.e) / 10);
      const ef = clamp01((-6 - s.e) / 8);
      const solX = Math.max(30, Math.min(610, 320 + (s.az - 180) * 2.3));
      const solY = Math.max(24, 272 - Math.max(s.e, -9) * 3.6);
      const solOp = clamp01((s.e + 6) / 6);
      let f = -1;
      if (s.H >= s.H0) f = (s.H - s.H0) / (2 * Math.PI - 2 * s.H0);
      else if (s.H <= -s.H0) f = (s.H + 2 * Math.PI - s.H0) / (2 * Math.PI - 2 * s.H0);
      const lunaX = f >= 0 ? 110 + f * 420 : 320;
      const lunaY = f >= 0 ? 272 - 56 * Math.sin(Math.PI * f) * 3.6 : 300;
      const lunaOp = f >= 0 ? clamp01((-s.e - 1) / 5) : 0;
      state.astro = {
        elev: s.e,
        az: s.az,
        nf,
        ef,
        wA,
        wB,
        lunaVisible: lunaOp > 0.05,
        fase: s.e < -6 ? 'NOCHE' : s.e < 4 ? 'DORADA' : 'DÍA',
      };
      const cuerpoX = s.e > -1 ? solX : lunaX;
      const cuerpoOp = s.e > -1 ? clamp01((s.e + 2) / 6) : lunaOp;
      const conAstro = state.pantalla !== 'secundaria';

      ctx.globalAlpha = 1;
      if (wB >= 0.996) {
        ctx.drawImage(I['cielo-dia'], 0, 0);
      } else if (wA >= 0.996 && wB <= 0.01) {
        ctx.drawImage(I['cielo-dorado'], 0, 0);
      } else {
        ctx.drawImage(I['cielo-noche'], 0, 0);
        if (wA > 0.01) { ctx.globalAlpha = wA; ctx.drawImage(I['cielo-dorado'], 0, 0); }
        if (wB > 0.01) { ctx.globalAlpha = wB; ctx.drawImage(I['cielo-dia'], 0, 0); }
      }

      if (ef > 0.01) {
        D.estrellas.forEach((e, i) => {
          const o = i % 3 === 0 ? 0.3 + 0.7 * osc(0.10 + (i % 7) * 0.02, i * 1.3) : 1;
          px(e[2], Math.min(1, ef * o * (1 + aBoost * 0.5)), e[0] + pxSky, e[1] + pySky);
        });
        state.brillantes.forEach((e, i) => {
          const o = Math.min(1, ef * (0.8 + aBoost * 0.4) * Math.max(0, osc(0.07 + (i % 5) * 0.01, i * 2.1) - 0.55) / 0.45);
          if (o <= 0.004) return;
          const sx = e[0] + pxSky, sy = e[1] + pySky;
          px('#c7ccff', o, sx - 1, sy); px('#c7ccff', o, sx + 1, sy);
          px('#c7ccff', o, sx, sy - 1); px('#c7ccff', o, sx, sy + 1);
        });
      }
      const alas = T.modo_pajaros === 'wyverns' ? ALAS_WYVERN : ALAS_GRULLA;
      const cuadro = [0, 1, 2, 1][Math.floor(t / 5) % 4];
      for (const [cx, cy] of [
        [((t * 0.22 + 40) % 760) - 60 + pxCloud, 126 + 4 * Math.sin(t * 0.03) + pySky],
        [((t * 0.22 + 22) % 760) - 60 + pxCloud, 116 + 4 * Math.sin(t * 0.03 + 1) + pySky],
        [((t * 0.20 + 5) % 760) - 60 + pxCloud, 138 + 4 * Math.sin(t * 0.025 + 2) + pySky],
      ]) {
        for (const [dx, dy] of alas[cuadro]) px(T.color_pajaros, 1, cx + dx, cy + dy);
        px(T.color_pajaros, 1, cx, cy + 1);
      }

      if (conAstro && solOp > 0.01) { ctx.globalAlpha = solOp; ctx.drawImage(I.sol, Math.round(solX - 104 + pxSky), Math.round(solY - 104 + pySky)); }
      if (conAstro && lunaOp > 0.01) { ctx.globalAlpha = lunaOp; ctx.drawImage(I.luna, Math.round(lunaX - 104 + pxSky), Math.round(lunaY - 104 + pySky)); }

      const noche = s.e < 0;
      const opNub = [noche ? 1 - wA : 0, noche ? wA : 1 - wB, wB];
      const fasesN = ['nubes-noche', 'nubes-dorado', 'nubes-dia'];
      D.nubes.forEach((nb, i) => {
        const v = 0.11 + (i % 4) * 0.035;
        const cx = Math.round(((nb[0] + nb[2] + t * v) % (640 + nb[2])) - nb[2] + pxCloud);
        for (let k = 0; k < 3; k++) {
          if (opNub[k] <= 0.01) continue;
          ctx.globalAlpha = opNub[k];
          ctx.drawImage(I[fasesN[k]], 0, nb[4], nb[2], nb[3], cx, nb[1] + pySky, nb[2], nb[3]);
        }
      });

      const esStranger = T.modo_heroe && T.modo_heroe.startsWith('stranger_');
      if (esStranger) pintaTormentaStranger(t, nf, T.modo_heroe);

      ctx.globalAlpha = 1;
      ctx.drawImage(I['escena-noche'], 0, 0);
      if (wA > 0.01) { ctx.globalAlpha = wA; ctx.drawImage(I['escena-dorado'], 0, 0); }
      if (wB > 0.01) { ctx.globalAlpha = wB; ctx.drawImage(I['escena-dia'], 0, 0); }

      if (T.modo_heroe === 'miles_morales') { pintaFerry(t, nf); pintaMiles(t, nf); }
      else if (T.modo_heroe === 'miles_colgado') { pintaFerry(t, nf); pintaMilesColgado(t, nf); }
      else if (T.modo_heroe === 'stranger_azotamentes') { pintaStrangerPrincipal(t, nf); }
      else if (T.modo_heroe === 'stranger_demogorgon') { pintaStrangerDemogorgon(t, nf); }
      else if (T.modo_heroe === 'stranger_reloj') { pintaStrangerReloj(t, nf); }
      else if (T.modo_heroe === 'demon_rengoku') { pintaDemonRengoku(t, nf); }
      else if (T.modo_heroe === 'demon_tokito') { pintaDemonTokito(t, nf); }
      else if (T.modo_heroe === 'demon_glicinias') { pintaDemonGlicinias(t, nf); }
      else if (T.modo_heroe === 'naruto_baryon') { pintaNarutoBaryon(t, nf); }
      else if (T.modo_heroe === 'naruto_konoha') { pintaNarutoKonoha(t, nf); }
      else if (T.modo_heroe === 'naruto_valle') { pintaNarutoValle(t, nf); }
      else if (T.modo_heroe === 'jujutsu') { pintaJujutsu(t, nf); }
      else if (T.modo_heroe === 'jujutsu_sec') { pintaJujutsuSec(t, nf); }
      else if (T.modo_heroe === 'jujutsu_bloq') { pintaJujutsuBloq(t, nf); }
      else if (T.modo_heroe === 'aot_rumbling') { pintaAotRumbling(t, nf); }
      else if (T.modo_heroe === 'aot_shiganshina') { pintaAotShiganshina(t, nf); }
      else if (T.modo_heroe === 'aot_paths') { pintaAotPaths(t, nf); }
      else if (T.modo_heroe === 'op_gear5') { pintaOpGear5(t, nf); }
      else if (T.modo_heroe === 'op_sunny') { pintaOpSunny(t, nf); }
      else if (T.modo_heroe === 'op_poneglyph') { pintaOpPoneglyph(t, nf); }
      else if (T.modo_heroe === 'dbz_ui') { pintaDbzUi(t, nf); }
      else if (T.modo_heroe === 'dbz_namek') { pintaDbzNamek(t, nf); }
      else if (T.modo_heroe === 'dbz_kame') { pintaDbzKame(t, nf); }
      else if (T.modo_heroe === 'cyber_sandevistan') { pintaCyberSandevistan(t, nf); }
      else if (T.modo_heroe === 'cyber_moon') { pintaCyberMoon(t, nf); }
      else if (T.modo_heroe === 'cyber_bloq') { pintaCyberBloq(t, nf); }
      if (D.chimenea) {
        const [hx, hy] = D.chimenea;
        for (let i = 0; i < 9; i++) {
          const fase = ((t * 0.25 + i * 5) % 45) / 45;
          const sx = hx + Math.sin(t * 0.06 + i * 1.4) * (1.5 + fase * 5) + fase * 4;
          const sy = hy - fase * 26;
          const sz = fase < 0.35 ? 2 : 3;
          px(wB > 0.5 ? T.color_humo_dia : T.color_humo_noche, (1 - fase) * (0.28 + 0.16 * nf), sx, sy, sz, sz - 1);
        }
      }
      if (nf > 0.02) {
        D.ventanas.forEach((v, i) => {
          const p = nf * (((Math.floor(t / 24) + i) % 13 === 0) ? 0.25 : 0.7 + 0.3 * Math.sin(t * 0.09 * (1 + (i % 4) * 0.15) + i * 2.1));
          px(T.color_ventanas, 0.12 * p, v[0] - 1, v[1] - 1, 4, 6);
          px(T.color_ventanas, p, v[0], v[1], 2, 4);
        });
        D.faroles.forEach((fr, i) => {
          const p = nf * (0.65 + 0.35 * Math.sin(t * 0.11 + i * 1.7));
          const g = Math.max(2, Math.round(fr[2] / 3));
          px(T.color_faroles_halo, 0.06 * p, fr[0] - g * 2, fr[1] - g * 2, g * 4 + 1, g * 4 + 1);
          px(T.color_faroles_halo, 0.14 * p, fr[0] - g, fr[1] - g, g * 2 + 1, g * 2 + 1);
          px(T.color_faroles_centro, p, fr[0], fr[1], 1, 2);
        });
        if (D.runas) {
          const pr = (0.35 + 0.65 * nf) * (0.65 + 0.35 * Math.sin(t * 0.08));
          D.runas.forEach((rn, i) => {
            const pulse = pr * (0.75 + 0.25 * Math.sin(t * 0.12 + i * 0.4));
            px(T.color_runas_halo, 0.14 * pulse, rn[0] - 1, rn[1] - 1, 3, 3);
            px(T.color_runas_centro, pulse, rn[0], rn[1], 1, 1);
          });
        }
      }
      if (!T.sin_lago) {
        for (const o of olas) {
          px(o[5] ? T.color_olas[0] : T.color_olas[1],
            (0.08 + 0.55 * Math.max(0, Math.sin(t * 0.04 + o[3]))) * (1 - 0.6 * wB),
            o[0] + 6 * Math.sin(t * o[4] + o[3]), o[1], o[2], 1);
        }
        if (conAstro && cuerpoOp > 0.02) {
          const col = s.e > -1 ? T.color_reflejo_sol : T.color_reflejo_luna;
          for (let i = 0; i < 38; i++) {
            const d = 8 + i * 3, w = Math.max(3, 46 - d * 0.30);
            px(col, cuerpoOp * (0.75 - d * 0.005) * osc(0.07, i * 1.7),
              cuerpoX - w / 2 + 3 * Math.sin(t * 0.05 + i * 1.3), 280 + d, w * (0.45 + 0.55 * osc(0.09, i * 2.2)), 1);
          }
          const dx = cuerpoX - 352;
          D.destellos.forEach((ds, i) => {
            const o = cuerpoOp * Math.pow(Math.max(0, Math.sin(t * 0.16 + i * 0.9)), 3);
            if (o > 0.004) px(T.color_destello, o, ds[0] + dx, ds[1], 2, 1);
          });
        }
      }
      const esBrasas = T.modo_particulas === 'brasas_mana';
      hojas.forEach((p, i) => {
        const esMana = p[5] === 3;
        const ax = (p[0] + t * p[3] + 18 * Math.sin(t * 0.03 + p[4])) % 660 - 10;
        const dirY = (esMana || esBrasas) ? -p[2] * 0.45 : p[2];
        const ay = ((p[1] + t * dirY) % 420 + 420) % 420 - 10;
        if (ay >= 395) return;
        if (esMana) {
          const mOp = (0.25 + 0.75 * nf) * (0.45 + 0.55 * Math.sin(t * 0.11 + i));
          px(T.color_mana_halo, 0.25 * mOp, ax - 1, ay - 1, 3, 3);
          px(T.color_mana_centro, mOp, ax, ay, 1, 1);
        } else if (esBrasas) {
          const bOp = (0.35 + 0.65 * nf) * (0.5 + 0.5 * Math.sin(t * 0.13 + i));
          px(T.colores_hojas[p[5] % T.colores_hojas.length], bOp, ax, ay, 1, 1);
        } else {
          const h = Math.floor(t / 7 + i) % 2;
          px(T.colores_hojas[p[5] % T.colores_hojas.length], 0.92, ax, ay, h ? 2 : 1, h ? 1 : 2);
        }
      });
      if (nf > 0.25) {
        MOTAS_MANA.forEach((lc, i) => {
          const fx = lc[0] + 9 * Math.sin(t * (0.021 + i * 0.002) + i * 2.3) + pxSky;
          const fy = lc[1] + 5 * Math.sin(t * (0.017 + i * 0.0015) + i * 1.1) + pySky;
          const b = Math.min(1, nf * (1 + aBoost) * Math.pow(Math.max(0, Math.sin(t * (0.05 + i * 0.004) + i * 1.9)), 2));
          px(T.color_fuegos_halo[i % T.color_fuegos_halo.length], 0.28 * b, fx - 1, fy - 1, 3, 3);
          px(T.color_fuegos_centro[i % T.color_fuegos_centro.length], 0.2 + 0.8 * b, fx, fy, 1, 1);
        });
      }
      if (state.hudStats && state.hudStats.foco && state.foco && state.foco.activo) {
        const zCol = state.foco.descanso ? '#38bdf8' : '#e6c06e';
        for (let z = 0; z < 4; z++) {
          const zx = 320 + Math.round(Math.sin(t * 0.04 + z * 1.57) * 58);
          const zy = 356 + Math.round(Math.cos(t * 0.05 + z * 1.57) * 8);
          const zo = 0.25 + 0.35 * Math.sin(t * 0.09 + z);
          px(zCol, zo, zx, zy, 2, 1);
        }
      }
      pintaEventoEspecial(t);
      pintaClima(t, wB, nf, fecha);
      ctx.globalAlpha = 1;

      if (opts.onRender) opts.onRender(fecha, T);
    }

    const WORLD_THEMES = {
      'fittoa': ['#e6c06e', '#72c48c', 'rgba(230, 192, 110, 0.34)'],
      'continente-demoniaco': ['#ff7854', '#f4a261', 'rgba(255, 120, 84, 0.34)'],
      'hunter-x-hunter': ['#72c48c', '#f3c65f', 'rgba(114, 196, 140, 0.34)'],
      'black-clover': ['#b888ff', '#ef4444', 'rgba(184, 136, 255, 0.36)'],
      'spiderman-miles-morales': ['#f43f5e', '#38bdf8', 'rgba(244, 63, 94, 0.38)'],
      'solo-leveling': ['#a855f7', '#38bdf8', 'rgba(168, 85, 247, 0.42)'],
      'demon-slayer': ['#fb923c', '#22d3ee', 'rgba(251, 146, 60, 0.38)'],
      'stranger-things': ['#ef4444', '#a855f7', 'rgba(239, 68, 68, 0.40)'],
      'harry-potter': ['#eab308', '#38bdf8', 'rgba(234, 179, 8, 0.36)'],
      'naruto': ['#ff9b38', '#38bdf8', 'rgba(255, 155, 56, 0.40)'],
      'jujutsu-kaisen': ['#e11d48', '#c084fc', 'rgba(225, 29, 72, 0.40)'],
      'attack-on-titan': ['#f97316', '#22c55e', 'rgba(249, 115, 22, 0.40)'],
      'one-piece': ['#f43f5e', '#facc15', 'rgba(244, 63, 94, 0.40)'],
      'dragon-ball-z': ['#38bdf8', '#facc15', 'rgba(56, 189, 248, 0.42)'],
      'cyberpunk-edgerunners': ['#facc15', '#22d3ee', 'rgba(250, 204, 21, 0.42)'],
    };

    const WORLD_AUDIO = {
      'fittoa': ['Lullaby of Fittoa · OST', '84 BPM · FLACO LO-FI', 'VOL 68%'],
      'continente-demoniaco': ['Rikarisu Wasteland · OST', '92 BPM · SYNTH AMBIENT', 'VOL 64%'],
      'hunter-x-hunter': ['Departure! (Acoustic)', '96 BPM · GUITARRA LO-FI', 'VOL 72%'],
      'black-clover': ['Haruka Mirai (Piano)', '108 BPM · ORQUESTA', 'VOL 76%'],
      'spiderman-miles-morales': ['Sunflower · Brooklyn Mix', '90 BPM · BOOM-BAP LO-FI', 'VOL 80%'],
      'solo-leveling': ['DARK ARIA <LV2> · Sawano', '116 BPM · SINFÓNICO', 'VOL 78%'],
      'demon-slayer': ['Kamado Tanjiro no Uta', '78 BPM · SHAKUHACHI', 'VOL 70%'],
      'stranger-things': ["Kids / Synthwave '83", '104 BPM · ANALÓGICO', 'VOL 74%'],
      'harry-potter': ["Hedwig's Theme · Celesta", '88 BPM · CELESTA', 'VOL 66%'],
      'naruto': ['Silhouette · Baryon OST', '132 BPM · TAIKO & SHAMISEN', 'VOL 82%'],
      'jujutsu-kaisen': ['Kaikai Kitan · Domain OST', '128 BPM · CURSED SYNTH', 'VOL 84%'],
      'attack-on-titan': ['Atæk on Titan · Sawano OST', '138 BPM · CORO ÉPICO', 'VOL 86%'],
      'one-piece': ['Drums of Liberation · Nika', '126 BPM · TAMBORES', 'VOL 85%'],
      'dragon-ball-z': ['Ultimate Battle · UI OST', '145 BPM · ROCK SINFÓNICO', 'VOL 88%'],
      'cyberpunk-edgerunners': ['I Really Want to Stay · OST', '124 BPM · SYNTHWAVE', 'VOL 84%'],
    };

    function detectarGpu() {
      if (state._gpuName) return state._gpuName;
      let nombre = 'CANVAS 2D · PIXEL';
      try {
        if (typeof document !== 'undefined') {
          const glc = document.createElement('canvas');
          const gl = glc.getContext('webgl') || glc.getContext('experimental-webgl');
          if (gl) {
            const dbg = gl.getExtension('WEBGL_debug_renderer_info');
            const raw = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : '';
            if (raw) {
              nombre = String(raw).replace(/ANGLE \((?:[^,]+, )?([^)]+)\).*/, '$1').replace(/Direct3D.*|OpenGL.*/i, '').trim().slice(0, 26) || 'WEBGL ACCEL';
            } else {
              nombre = 'WEBGL 2D ACCEL';
            }
          }
        }
      } catch (_e) {}
      state._gpuName = nombre;
      return nombre;
    }

    function actualizaHud(fecha, T, { quoteIntervalMs = 90000, stats = null, hudStats = null, force = false } = {}) {
      const hudEl = document.getElementById('hud');
      if (!hudEl) return;
      const nowMs = Date.now();
      const hudKey = `${state.mostrarHud}|${state.tema}|${state.hudCompacto}|${state.modoHora}|${state.clima}`;
      if (!force && state._lastHudKey === hudKey && state._lastHudMs && (nowMs - state._lastHudMs) < 950) {
        return;
      }
      state._lastHudKey = hudKey;
      state._lastHudMs = nowMs;
      const hs = hudStats || state.hudStats || {};
      const vis = {
        tiempo: hs.tiempo !== false,
        clima: !!hs.clima,
        sistema: !!hs.sistema,
        gpu: !!hs.gpu,
        red: !!hs.red,
        audio: !!hs.audio,
        dev: !!hs.dev,
        foco: !!hs.foco,
        grimorio: hs.grimorio !== false,
      };
      const visibles = Object.values(vis).filter(Boolean).length;
      const activo = state.mostrarHud && visibles > 0;
      if (!activo) {
        hudEl.style.display = 'none';
        hudEl.classList.remove('is-multicol');
        return;
      }
      hudEl.style.removeProperty('display');
      hudEl.classList.remove('is-multicol');
      hudEl.classList.toggle('is-compact', !!state.hudCompacto);

      const themeCols = WORLD_THEMES[state.tema] || WORLD_THEMES['fittoa'];
      if (themeCols) {
        hudEl.style.setProperty('--hud-accent', themeCols[0]);
        hudEl.style.setProperty('--hud-accent-2', themeCols[1]);
        hudEl.style.setProperty('--hud-border', themeCols[2]);
        if (opts.themeRoot !== false && typeof document !== 'undefined' && document.documentElement) {
          document.documentElement.style.setProperty('--hud-accent', themeCols[0]);
          document.documentElement.style.setProperty('--hud-accent-2', themeCols[1]);
          document.documentElement.style.setProperty('--hud-border', themeCols[2]);
        }
      }

      const toggleCard = (id, visible) => {
        const el = document.getElementById(id);
        if (el) el.style.display = visible ? '' : 'none';
      };
      const setTxt = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
      };
      const setBar = (id, pct) => {
        const el = document.getElementById(id);
        if (el) el.style.width = `${Math.max(4, Math.min(100, pct))}%`;
      };

      toggleCard('card-tiempo', vis.tiempo);
      toggleCard('card-clima', vis.clima);
      toggleCard('card-sistema', vis.sistema);
      toggleCard('card-gpu', vis.gpu);
      toggleCard('card-red', vis.red);
      toggleCard('card-audio', vis.audio);
      toggleCard('card-dev', vis.dev);
      toggleCard('card-foco', vis.foco);
      toggleCard('card-grimorio', vis.grimorio);

      const p2 = v => String(v).padStart(2, '0');
      setTxt('hud-hm', `${p2(fecha.getHours())}:${p2(fecha.getMinutes())}`);
      setTxt('hud-s', p2(fecha.getSeconds()));
      setTxt('hud-modo', ['REAL', 'CICLO 90M', 'DEMO 90S', 'FIJA'][state.modoHora]);
      setTxt('hud-fecha', fecha.toLocaleDateString('es-ES', {
        weekday: 'long', day: 'numeric', month: 'short',
      }));
      setTxt('hud-tema', (T && T.nombre) || state.tema);

      if (vis.clima) {
        const cl = (stats && stats.clima) || {};
        const astro = state.astro || sol(fecha);
        const elev = astro.elev !== undefined ? astro.elev : astro.e;
        const az = astro.az || 0;
        const faseTxt = cl.fase || astro.fase || (elev < -6 ? 'NOCHE' : elev < 4 ? 'DORADA' : 'DÍA');
        const cAct = state._climaActivo && state._climaActivo !== 'normal' ? ` · ${state._climaActivo.toUpperCase()}` : '';
        const condTxt = (cl.cond || (elev < -6 ? (astro.lunaVisible ? 'LUNA Y ESTRELLAS' : 'NOCHE PROFUNDA') : elev < 4 ? 'SOL RASANTE · DORADO' : 'CIELO DESPEJADO')) + cAct;
        const luzPct = Math.round(clamp01((elev + 18) / 68) * 100);
        setTxt('hud-clima-meta', state.clima === 'auto' ? `${faseTxt} · AUTO` : faseTxt);
        setTxt('hud-clima-elev', `${elev >= 0 ? '+' : ''}${elev.toFixed(1)}°`);
        setTxt('hud-clima-az', `${Math.round(az)}°`);
        setTxt('hud-clima-luz', condTxt);
        setBar('hud-clima-bar', luzPct);
      }

      if (vis.sistema) {
        const sis = (stats && stats.sistema) || {};
        const cpu = sis.cpu ?? Math.round(14 + 9 * Math.abs(Math.sin(state.tick * 0.08)));
        const ramTxt = sis.ram ?? `${(6.2 + 0.4 * Math.sin(state.tick * 0.03)).toFixed(1)}/16G`;
        const disco = sis.disco ?? '58%';
        const bat = sis.bat ?? 'AC';
        setTxt('hud-sys-meta', sis.up || 'EN LÍNEA');
        setTxt('hud-cpu', `${cpu}%`);
        setTxt('hud-ram', ramTxt);
        setTxt('hud-disco', disco);
        setTxt('hud-bat', bat);
        setBar('hud-cpu-bar', parseFloat(cpu) || 0);
        if (sis.ramPct !== undefined) setBar('hud-ram-bar', sis.ramPct);
      }

      if (vis.gpu) {
        const g = (stats && stats.gpu) || {};
        const uso = g.uso ?? Math.round(18 + 8 * Math.abs(Math.sin(state.tick * 0.06 + 1.1)));
        setTxt('hud-gpu-meta', g.meta || `${state.fps} FPS`);
        setTxt('hud-gpu-nombre', g.nombre || detectarGpu());
        setTxt('hud-gpu-uso', `${uso}%`);
        setTxt('hud-gpu-res', g.res || (stats && stats.gpu_vram) || '640×400 PIXEL');
        setTxt('hud-gpu-temp', g.temp || (stats && stats.gpu_temp) || `${Math.round(49 + 3 * Math.sin(state.tick * 0.04))}°C`);
        setBar('hud-gpu-bar', parseFloat(uso) || 0);
      }

      if (vis.red) {
        const red = (stats && stats.red) || {};
        const conn = typeof navigator !== 'undefined' && navigator.connection ? navigator.connection : null;
        setTxt('hud-net-iface', red.iface || (conn && conn.effectiveType ? `WEB ${conn.effectiveType.toUpperCase()}` : 'ETHERNET / WIFI'));
        setTxt('hud-ip', red.ip || (typeof location !== 'undefined' && location.hostname ? location.hostname : '127.0.0.1'));
        setTxt('hud-rx', red.rx || (conn && conn.downlink ? `${conn.downlink} Mbps` : '1.4 MB/s'));
        setTxt('hud-tx', red.tx || '240 KB/s');
      }

      if (vis.audio) {
        const au = (stats && stats.audio) || {};
        const baseInfo = WORLD_AUDIO[state.tema] || ['Ambient Pixel · OST', '90 BPM · STEREO', 'VOL 70%'];
        const off = ((audioState.trackOffset % TRACK_POOL.length) + TRACK_POOL.length) % TRACK_POOL.length;
        const info = audioState.trackOffset === 0 ? baseInfo : [TRACK_POOL[off][0], TRACK_POOL[off][1], baseInfo[2] || 'VOL 75%'];
        const synthOn = audioCtrl.isPlaying();
        const estado = au.estado || (stats && stats.audio_meta) || (synthOn ? 'SYNTH EN VIVO' : 'AMBIENT OST');
        const paused = /PAUSA/i.test(estado);
        const nivel = au.nivel ?? (synthOn ? Math.round(28 + (state.audioEnergy || 0) * 72) : paused ? 18 : Math.round(48 + 38 * Math.abs(Math.sin(state.tick * 0.24) * Math.cos(state.tick * 0.11))));
        setTxt('hud-audio-meta', estado);
        setTxt('hud-audio-track', au.pista || (stats && stats.audio_track) || info[0]);
        setTxt('hud-audio-bpm', au.detalle || (stats && stats.audio_artist) || info[1]);
        setTxt('hud-audio-vol', au.vol || (au.pista ? (paused ? 'PAUSA' : 'LIVE') : (synthOn ? 'SYNTH ON' : info[2])));
        setBar('hud-audio-bar', nivel);
        const eq = document.getElementById('hud-eq');
        if (eq && eq.children.length) {
          for (let b = 0; b < eq.children.length; b++) {
            const hPct = paused ? 15 : synthOn
              ? Math.max(15, Math.min(100, Math.round(25 + (state.audioEnergy || 0) * 65 * (0.5 + 0.5 * Math.abs(Math.sin(state.tick * 0.4 + b))))))
              : Math.round(20 + 68 * Math.abs(Math.sin(state.tick * 0.28 + b * 0.85)));
            eq.children[b].style.height = `${hPct}%`;
          }
        }
      }

      if (vis.dev) {
        const dev = (stats && stats.dev) || {};
        setTxt('hud-dev-host', dev.host || 'pixelzen-worlds');
        setTxt('hud-repo', dev.repo || 'pixelzen-worlds · main');
        setTxt('hud-tc', dev.tc || 'PY 3.12 · JS ES6 · C# GDI+');
      }

      if (vis.foco) {
        const fc = (stats && stats.foco) || {};
        const nowMs = Date.now();
        const delta = Math.max(0, Math.floor((nowMs - (state.foco.lastTickMs || nowMs)) / 1000));
        if (delta >= 1) {
          state.foco.lastTickMs += delta * 1000;
          if (state.foco.activo) {
            state.foco.sesionSec += delta;
            state.foco.restSec -= delta;
            if (state.foco.restSec <= 0) {
              state.foco.descanso = !state.foco.descanso;
              if (!state.foco.descanso) state.foco.ciclo += 1;
              state.foco.cicloSec = state.foco.descanso ? 5 * 60 : 25 * 60;
              state.foco.restSec = state.foco.cicloSec;
            }
          }
        }
        const rest = Math.max(0, state.foco.restSec);
        const tot = Math.max(1, state.foco.cicloSec);
        const mm = p2(Math.floor(rest / 60)), ss = p2(rest % 60);
        const sm = Math.floor(state.foco.sesionSec / 60), ssec = p2(state.foco.sesionSec % 60);
        const modoTxt = state.foco.descanso ? 'DESCANSO' : 'ZEN';
        const pausaTxt = state.foco.activo ? '' : ' · PAUSA';
        setTxt('hud-foco-meta', fc.meta || `CICLO ${state.foco.ciclo} · ${modoTxt}${pausaTxt}`);
        setTxt('hud-foco-timer', fc.timer || `${mm}:${ss}`);
        setTxt('hud-foco-sesion', fc.sesion || `${sm}m ${ssec}s activa`);
        setBar('hud-foco-bar', ((tot - rest) / tot) * 100);
        const btnFoco = document.getElementById('btn-foco-toggle');
        if (btnFoco) btnFoco.textContent = state.foco.activo ? '⏸' : '▶';
      }

      const citas = (T && T.citas) || [];
      if (citas.length && vis.grimorio) {
        const hk = citas[Math.floor(Date.now() / quoteIntervalMs) % citas.length];
        setTxt('hud-au', hk.au || '');
        setTxt('hud-qsub', hk.sub || '');
        setTxt('hud-qtxt', hk.es || '');
      }
    }

    return {
      state,
      cargarTema,
      render,
      actualizaHud,
      dispararEvento,
      audioCtrl,
      toggleFoco,
      resetFoco,
      setFocoModo,
      WORLD_THEMES,
      WORLD_AUDIO,
    };
  }

  window.PixelZenCanvas = { createRenderer };
})();
