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
      hc: 22, hr: 0, rows: [
        '......................HR..', '.....................RRK..', '....................SSK...',
        '..........KSSK.....SSK....', '.........KSRWWWR..SSK.....', '.........KSKWWWWR.SSK.....',
        '.........KSKKWWWKSSK......', '..........KKKKKKSSK.......', '........SSKRRRRRKSS.......',
        '.......SSKKRRRRRKK........', '......SS..KKRRRKK.........', '.....SS...KKKKKK..KKKK....',
        '....HR....KKKKKKKKKKSSKK..', '....E....KKKKKK..KKK..KKK.', '........KKSSKK........SSK.',
        '.......KK..KK.........RRR.', '......KK..............RR..', '.....SS...................',
        '....RR....................', '....R.....................',
      ],
    },
    {
      hc: 18, hr: 0, rows: [
        '..................HR......', '.................RRK......', '................SSK.......',
        '........KSSK...SSK........', '.......KSRWWWRSSK.........', '.......KSKWWWWRSK.........',
        '.......KSKKWWWKSS.........', '........KKKKKKKSS.........', '......SSKRRRRRKSS.........',
        '.....SSKKRRRRRKK..........', '....SS..KKRRRKK...........', '...HR...KKKKKK..KKKK......',
        '...E...KKKKKKKKKKSSKK.....', '.......KKKKK...KKK.KKK....', '......KKSSK........RRR....',
        '.....KK..KK.........R.....', '....RR...RR...............', '....R.....................',
        '..........................', '..........................',
      ],
    },
    {
      hc: 14, hr: 0, rows: [
        '..............HR..........', '.............RRK..........', '............SSK...........',
        '............SSK.KSSK......', '...........SSK.KSRWWWR....', '...........SSKKKSKWWWWR...',
        '............SSKKKSKWWWK...', '...........SSKRRRRKKKK....', '..........SSKKRRRRKK......',
        '.........SS..KKRRKK.......', '........HR...KKKKK..KKKK..', '........E...KKKKKK.KKSSKK.',
        '...........KKSSK....KK.KK.', '..........KK..KK.......RRR', '.........KK............RR.',
        '........SS................', '.......RR.................', '..........................',
        '..........................', '..........................',
      ],
    },
    {
      hc: 14, hr: 7, rows: [
        '..........................', '..........................', '..........................',
        '..........KSSK............', '.........KSRWWWR..........', '.........KSKWWWWR.........',
        '.........KSKKWWWK.........', '..........KKKKKK..........', '........SSKRRRRRKSS.......',
        '.......SSKKRRRRKKKRR......', '......SS..KKRRKK..E.......', '.....HR...KKKKK.KKKK......',
        '..........KKKKKKKKSSKK....', '.........KKKKK....RRR.....', '........KKSSKK....R.......',
        '.......KK..KK.............', '......RR...RR.............', '..........................',
        '..........................', '..........................',
      ],
    },
  ];
  const MILES_COLS = { K: '#0b0a14', S: '#2e3358', R: '#e61e3c', H: '#ff5470', W: '#ffffff', E: '#00e5ff' };

  function lcg(seed) {
    let s = seed;
    return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
  }
  const clamp01 = v => (v < 0 ? 0 : v > 1 ? 1 : v);
  const suave = t => { t = clamp01(t); return t * t * (3 - 2 * t); };

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

  const canvas = document.getElementById('lienzo');
  const ctx = canvas.getContext('2d');
  ctx.imageSmoothingEnabled = false;

  const loadingEl = document.getElementById('canvas-loading');
  const hudEl = document.getElementById('hud');
  const sliderEl = document.getElementById('hora-slider');
  const horaLabelEl = document.getElementById('hora-label');

  const state = {
    tema: 'fittoa',
    modoHora: 3, // 0=real, 1=90m, 2=demo90s, 3=fija
    horaFija: 18.75,
    fps: 10,
    mostrarHud: true,
    lat: 40.4,
    lon: -3.7,
    tick: 0,
    inicioMs: Date.now(),
    inicioHora: 18.75,
    D: null,
    T: null,
    img: {},
    brillantes: [],
  };

  function loadImage(src) {
    return new Promise((res, rej) => {
      const im = new Image();
      im.onload = () => res(im);
      im.onerror = rej;
      im.src = src;
    });
  }

  async function cargarTema(id) {
    loadingEl.classList.remove('is-hidden');
    const base = `temas/${id}`;
    const names = [
      'cielo-noche', 'cielo-dorado', 'cielo-dia',
      'escena-noche', 'escena-dorado', 'escena-dia',
      'nubes-noche', 'nubes-dorado', 'nubes-dia',
      'sol', 'luna',
    ];
    const [datos, tema, ...imgs] = await Promise.all([
      fetch(`${base}/datos.json`).then(r => r.json()),
      fetch(`${base}/tema.json`).then(r => r.json()),
      ...names.map(f => loadImage(`${base}/images/${f}.png`)),
    ]);
    if (state.tema !== id) return;
    const map = {};
    names.forEach((k, i) => { map[k] = imgs[i]; });
    state.D = datos;
    state.T = tema;
    state.img = map;
    state.brillantes = datos.estrellas.filter(e => e[3] === 1);
    document.getElementById('canvas-wrap').style.background = tema.cielo_fondo || '#060814';
    loadingEl.classList.add('is-hidden');
    render();
  }

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

  function px(hex, op, ax, ay, aw = 1, ah = 1) {
    if (op <= 0.004) return;
    ctx.globalAlpha = clamp01(op);
    ctx.fillStyle = hex;
    ctx.fillRect(Math.round(ax), Math.round(ay), aw, ah);
  }

  function osc(f, p) { return 0.5 + 0.5 * Math.sin(state.tick * f + p); }

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

  function render() {
    if (!state.D || !state.T) return;
    const D = state.D, T = state.T, I = state.img, t = state.tick;
    const fecha = fechaEfectiva();
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
    const cuerpoX = s.e > -1 ? solX : lunaX;
    const cuerpoOp = s.e > -1 ? clamp01((s.e + 2) / 6) : lunaOp;

    // 1. Cielo
    ctx.globalAlpha = 1;
    ctx.drawImage(I['cielo-noche'], 0, 0);
    if (wA > 0.01) { ctx.globalAlpha = wA; ctx.drawImage(I['cielo-dorado'], 0, 0); }
    if (wB > 0.01) { ctx.globalAlpha = wB; ctx.drawImage(I['cielo-dia'], 0, 0); }

    // 2. Estrellas y aves/wyverns
    if (ef > 0.01) {
      D.estrellas.forEach((e, i) => {
        const o = i % 3 === 0 ? 0.3 + 0.7 * osc(0.10 + (i % 7) * 0.02, i * 1.3) : 1;
        px(e[2], ef * o, e[0], e[1]);
      });
      state.brillantes.forEach((e, i) => {
        const o = ef * 0.8 * Math.max(0, osc(0.07 + (i % 5) * 0.01, i * 2.1) - 0.55) / 0.45;
        if (o <= 0.004) return;
        px('#c7ccff', o, e[0] - 1, e[1]); px('#c7ccff', o, e[0] + 1, e[1]);
        px('#c7ccff', o, e[0], e[1] - 1); px('#c7ccff', o, e[0], e[1] + 1);
      });
    }
    const alas = T.modo_pajaros === 'wyverns' ? ALAS_WYVERN : ALAS_GRULLA;
    const cuadro = [0, 1, 2, 1][Math.floor(t / 5) % 4];
    for (const [cx, cy] of [
      [((t * 0.22 + 40) % 760) - 60, 126 + 4 * Math.sin(t * 0.03)],
      [((t * 0.22 + 22) % 760) - 60, 116 + 4 * Math.sin(t * 0.03 + 1)],
      [((t * 0.20 + 5) % 760) - 60, 138 + 4 * Math.sin(t * 0.025 + 2)],
    ]) {
      for (const [dx, dy] of alas[cuadro]) px(T.color_pajaros, 1, cx + dx, cy + dy);
      px(T.color_pajaros, 1, cx, cy + 1);
    }

    // 3. Sol y luna
    if (solOp > 0.01) { ctx.globalAlpha = solOp; ctx.drawImage(I.sol, Math.round(solX - 104), Math.round(solY - 104)); }
    if (lunaOp > 0.01) { ctx.globalAlpha = lunaOp; ctx.drawImage(I.luna, Math.round(lunaX - 104), Math.round(lunaY - 104)); }

    // 4. Nubes
    const noche = s.e < 0;
    const opNub = [noche ? 1 - wA : 0, noche ? wA : 1 - wB, wB];
    const fasesN = ['nubes-noche', 'nubes-dorado', 'nubes-dia'];
    D.nubes.forEach((nb, i) => {
      const v = 0.035 + (i % 4) * 0.012;
      const cx = Math.round(((nb[0] + nb[2] + t * v) % (640 + nb[2])) - nb[2]);
      for (let k = 0; k < 3; k++) {
        if (opNub[k] <= 0.01) continue;
        ctx.globalAlpha = opNub[k];
        ctx.drawImage(I[fasesN[k]], 0, nb[4], nb[2], nb[3], cx, nb[1], nb[2], nb[3]);
      }
    });

    // 5. Escena principal
    ctx.globalAlpha = 1;
    ctx.drawImage(I['escena-noche'], 0, 0);
    if (wA > 0.01) { ctx.globalAlpha = wA; ctx.drawImage(I['escena-dorado'], 0, 0); }
    if (wB > 0.01) { ctx.globalAlpha = wB; ctx.drawImage(I['escena-dia'], 0, 0); }

    // 6. Efectos delanteros
    if (T.modo_heroe === 'miles_morales') { pintaFerry(t, nf); pintaMiles(t, nf); }
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
    for (const o of olas) {
      px(o[5] ? T.color_olas[0] : T.color_olas[1],
        (0.08 + 0.55 * Math.max(0, Math.sin(t * 0.04 + o[3]))) * (1 - 0.6 * wB),
        o[0] + 6 * Math.sin(t * o[4] + o[3]), o[1], o[2], 1);
    }
    if (cuerpoOp > 0.02) {
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
        const fx = lc[0] + 9 * Math.sin(t * (0.021 + i * 0.002) + i * 2.3);
        const fy = lc[1] + 5 * Math.sin(t * (0.017 + i * 0.0015) + i * 1.1);
        const b = nf * Math.pow(Math.max(0, Math.sin(t * (0.05 + i * 0.004) + i * 1.9)), 2);
        px(T.color_fuegos_halo[i % T.color_fuegos_halo.length], 0.28 * b, fx - 1, fy - 1, 3, 3);
        px(T.color_fuegos_centro[i % T.color_fuegos_centro.length], 0.2 + 0.8 * b, fx, fy, 1, 1);
      });
    }
    ctx.globalAlpha = 1;

    // HUD y etiqueta de hora
    const p2 = v => String(v).padStart(2, '0');
    const hm = `${p2(fecha.getHours())}:${p2(fecha.getMinutes())}`;
    horaLabelEl.textContent = hm;
    if (state.modoHora !== 3) {
      sliderEl.value = (fecha.getHours() + fecha.getMinutes() / 60).toFixed(2);
    }

    hudEl.style.display = state.mostrarHud ? 'flex' : 'none';
    if (state.mostrarHud) {
      document.getElementById('hud-hm').textContent = hm;
      document.getElementById('hud-s').textContent = p2(fecha.getSeconds());
      document.getElementById('hud-modo').textContent = ['REAL', 'CICLO 90M', 'DEMO 90S', 'FIJA'][state.modoHora];
      document.getElementById('hud-fecha').textContent = fecha.toLocaleDateString('es-ES', {
        weekday: 'long', day: 'numeric', month: 'short',
      });
      document.getElementById('hud-tema').textContent = T.nombre || state.tema;
      const citas = T.citas || [];
      if (citas.length) {
        const hk = citas[Math.floor(Date.now() / 15000) % citas.length];
        document.getElementById('hud-au').textContent = hk.au || '';
        document.getElementById('hud-qsub').textContent = hk.sub || '';
        document.getElementById('hud-qtxt').textContent = hk.es || '';
      }
    }
  }

  function seleccionarTema(id) {
    state.tema = id;
    document.querySelectorAll('.pill[data-tema]').forEach(b => {
      b.classList.toggle('is-active', b.dataset.tema === id);
    });
    cargarTema(id);
  }

  function limpiarModos() {
    document.querySelectorAll('.btn-mode, .btn-phase').forEach(b => b.classList.remove('is-active'));
  }

  // Botones de tema en el visor
  document.querySelectorAll('.pill[data-tema]').forEach(btn => {
    btn.addEventListener('click', () => seleccionarTema(btn.dataset.tema));
  });

  // Modos de tiempo
  document.querySelectorAll('.btn-mode').forEach(btn => {
    btn.addEventListener('click', () => {
      limpiarModos();
      btn.classList.add('is-active');
      const m = btn.dataset.modo;
      if (m === '90m') {
        state.modoHora = 1;
        state.inicioMs = Date.now();
        state.inicioHora = parseFloat(sliderEl.value) || 12;
      } else if (m === 'demo') {
        state.modoHora = 2;
      } else {
        state.modoHora = 0;
      }
      render();
    });
  });

  // Presets de fase (Día / Atardecer / Noche)
  document.querySelectorAll('.btn-phase').forEach(btn => {
    btn.addEventListener('click', () => {
      limpiarModos();
      btn.classList.add('is-active');
      state.modoHora = 3;
      state.horaFija = parseFloat(btn.dataset.hora);
      sliderEl.value = state.horaFija;
      render();
    });
  });

  // Slider manual 24h
  sliderEl.addEventListener('input', () => {
    limpiarModos();
    state.modoHora = 3;
    state.horaFija = parseFloat(sliderEl.value);
    render();
  });

  // Toggle HUD y Pantalla completa
  const btnHud = document.getElementById('btn-hud');
  btnHud.addEventListener('click', () => {
    state.mostrarHud = !state.mostrarHud;
    btnHud.textContent = `HUD: ${state.mostrarHud ? 'ON' : 'OFF'}`;
    render();
  });

  document.getElementById('btn-fullscreen').addEventListener('click', () => {
    const wrap = document.getElementById('canvas-wrap');
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (wrap.requestFullscreen) {
      wrap.requestFullscreen();
    }
  });

  // Galería de mundos: cambio de fase y botón "Probar en el visor"
  document.querySelectorAll('.world-card').forEach(card => {
    const id = card.dataset.world;
    const img = card.querySelector('.world-media img');
    card.querySelectorAll('.phase-switch button').forEach(btn => {
      btn.addEventListener('click', () => {
        card.querySelectorAll('.phase-switch button').forEach(b => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        img.src = `previews/${id}/${btn.dataset.fase}.png`;
      });
    });
    const tryBtn = card.querySelector('.btn-try');
    if (tryBtn) {
      tryBtn.addEventListener('click', () => {
        seleccionarTema(id);
        document.getElementById('visor').scrollIntoView({ behavior: 'smooth' });
      });
    }
  });

  // Pestañas de instalación y botones de copia
  document.querySelectorAll('.os-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.os-tab').forEach(t => t.classList.remove('is-active'));
      document.querySelectorAll('.os-pane').forEach(p => p.classList.remove('is-active'));
      tab.classList.add('is-active');
      document.querySelector(`.os-pane[data-pane="${tab.dataset.os}"]`).classList.add('is-active');
    });
  });

  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
        const orig = btn.textContent;
        btn.textContent = '¡Copiado!';
        setTimeout(() => { btn.textContent = orig; }, 1400);
      } catch {
        btn.textContent = 'Usa Ctrl+C';
      }
    });
  });

  setInterval(() => { state.tick++; render(); }, 100);
  cargarTema(state.tema);
})();
