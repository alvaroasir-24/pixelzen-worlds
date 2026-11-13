(() => {
  const TEMAS_DISPONIBLES = ['fittoa', 'continente-demoniaco', 'hunter-x-hunter', 'black-clover', 'spiderman-miles-morales'];
  const params = new URLSearchParams(window.location.search);
  const canvas = document.getElementById('lienzo');
  const d = new Date();
  let liveStats = null;

  const statsParam = params.get('stats');
  const hudStatsInit = statsParam ? {
    tiempo: statsParam.includes('tiempo'),
    sistema: statsParam.includes('sistema'),
    red: statsParam.includes('red'),
    dev: statsParam.includes('dev'),
    grimorio: statsParam.includes('grimorio'),
  } : {
    tiempo: params.get('hud_tiempo') !== '0',
    sistema: params.get('hud_sistema') !== '0',
    red: params.get('hud_red') !== '0',
    dev: params.get('hud_dev') !== '0',
    grimorio: params.get('hud_grimorio') !== '0',
  };

  const pantallaParam = params.get('pantalla') === 'secundaria' ? 'secundaria' : 'principal';
  const mostrarHudParam = params.has('hud')
    ? params.get('hud') !== '0'
    : pantallaParam !== 'secundaria';

  const renderer = window.PixelZenCanvas.createRenderer(canvas, {
    initialState: {
      tema: params.get('tema') || 'fittoa',
      pantalla: pantallaParam,
      modoHora: params.get('modo') === 'real' ? 0 : (params.get('modo') === 'demo' ? 2 : (params.get('modo') === 'fija' ? 3 : 1)),
      horaFija: parseFloat(params.get('hora') || '21.5'),
      fps: parseInt(params.get('fps') || '8', 10),
      mostrarHud: mostrarHudParam,
      hudStats: hudStatsInit,
      inicioHora: d.getHours() + d.getMinutes() / 60 + d.getSeconds() / 3600,
    },
    onTemaLoaded(tema) {
      document.body.style.background = tema.cielo_fondo || '#0a0c24';
    },
    onRender(fecha, T) {
      renderer.actualizaHud(fecha, T, { quoteIntervalMs: 90000, stats: liveStats });
    },
  });

  const { state } = renderer;
  let timer = null;
  function reprogramar() {
    if (timer) clearInterval(timer);
    timer = setInterval(() => { state.tick++; renderer.render(); }, Math.round(1000 / Math.max(2, Math.min(24, state.fps))));
  }

  async function refrescaStats() {
    if (window.location.protocol === 'file:') return;
    try {
      const res = await fetch('/api/stats');
      if (res.ok) liveStats = await res.json();
    } catch (_e) { /* servidor local opcional */ }
  }
  refrescaStats();
  setInterval(refrescaStats, 2500);

  window.livelyPropertyListener = (name, val) => {
    if (name === 'tema') {
      const nuevo = TEMAS_DISPONIBLES[val] || TEMAS_DISPONIBLES[0];
      if (nuevo !== state.tema) { renderer.cargarTema(nuevo).then(renderer.render); }
    } else if (name === 'pantalla') {
      const nueva = val === 1 ? 'secundaria' : 'principal';
      if (nueva !== state.pantalla) { renderer.cargarTema(state.tema, { pantalla: nueva }).then(renderer.render); }
    } else if (name === 'modoHora') {
      state.modoHora = val;
      if (val === 1) {
        state.inicioMs = Date.now();
        const now = new Date();
        state.inicioHora = now.getHours() + now.getMinutes() / 60 + now.getSeconds() / 3600;
      }
    } else if (name === 'horaFija') state.horaFija = val;
    else if (name === 'fps') { state.fps = val; reprogramar(); }
    else if (name === 'mostrarHud') state.mostrarHud = !!val;
    else if (name === 'hudTiempo') state.hudStats.tiempo = !!val;
    else if (name === 'hudSistema') state.hudStats.sistema = !!val;
    else if (name === 'hudRed') state.hudStats.red = !!val;
    else if (name === 'hudDev') state.hudStats.dev = !!val;
    else if (name === 'hudGrimorio') state.hudStats.grimorio = !!val;
    renderer.render();
  };

  renderer.cargarTema(state.tema, { pantalla: state.pantalla }).then(() => { renderer.render(); reprogramar(); });
})();
