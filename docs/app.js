(() => {
  const canvas = document.getElementById('lienzo');
  const canvasSec = document.getElementById('lienzo-sec');
  const wrapEl = document.getElementById('canvas-wrap');
  const loadingEl = document.getElementById('canvas-loading');
  const sliderEl = document.getElementById('hora-slider');
  const horaLabelEl = document.getElementById('hora-label');
  const badgeSecEl = document.getElementById('badge-sec');

  let numMonitores = 2;

  const renderer = window.PixelZenCanvas.createRenderer(canvas, {
    initialState: {
      tema: 'fittoa',
      pantalla: 'principal',
      modoHora: 3, // 0=real, 1=90m, 2=demo90s, 3=fija
      horaFija: 18.75,
      fps: 10,
      mostrarHud: true,
      hudStats: {
        tiempo: true,
        sistema: true,
        red: true,
        dev: true,
        grimorio: true,
      },
      inicioHora: 18.75,
    },
    onTemaLoaded(tema) {
      wrapEl.style.background = tema.cielo_fondo || '#060814';
      loadingEl.classList.add('is-hidden');
      renderer.render();
    },
    onRender(fecha, T) {
      const p2 = v => String(v).padStart(2, '0');
      horaLabelEl.textContent = `${p2(fecha.getHours())}:${p2(fecha.getMinutes())}`;
      if (renderer.state.modoHora !== 3) {
        sliderEl.value = (fecha.getHours() + fecha.getMinutes() / 60).toFixed(2);
      }
      renderer.actualizaHud(fecha, T, { quoteIntervalMs: 15000 });
    },
  });

  const rendererSec = canvasSec ? window.PixelZenCanvas.createRenderer(canvasSec, {
    initialState: {
      tema: 'fittoa',
      pantalla: 'secundaria',
      modoHora: 3,
      horaFija: 18.75,
      fps: 10,
      mostrarHud: false,
      inicioHora: 18.75,
    },
    onTemaLoaded(tema) {
      if (badgeSecEl && tema && tema.nombre) {
        badgeSecEl.textContent = `MONITOR 2 · ${tema.nombre.toUpperCase()}`;
      }
      rendererSec.render();
    },
  }) : null;

  const { state } = renderer;

  function sincronizaSecundario() {
    if (!rendererSec) return;
    const s2 = rendererSec.state;
    s2.modoHora = state.modoHora;
    s2.horaFija = state.horaFija;
    s2.inicioMs = state.inicioMs;
    s2.inicioHora = state.inicioHora;
    s2.tick = state.tick;
  }

  function renderTodo() {
    renderer.render();
    if (rendererSec && numMonitores >= 2) {
      sincronizaSecundario();
      rendererSec.render();
    }
  }

  function seleccionaYCarga(id) {
    loadingEl.classList.remove('is-hidden');
    const jobs = [renderer.cargarTema(id, { pantalla: 'principal' })];
    if (rendererSec && numMonitores >= 2) {
      jobs.push(rendererSec.cargarTema(id, { pantalla: 'secundaria' }));
    }
    Promise.all(jobs).then(() => {
      loadingEl.classList.add('is-hidden');
      renderTodo();
    });
  }

  function seleccionarTema(id) {
    state.tema = id;
    document.querySelectorAll('.pill[data-tema]').forEach(b => {
      b.classList.toggle('is-active', b.dataset.tema === id);
    });
    seleccionaYCarga(id);
  }

  function limpiarModos() {
    document.querySelectorAll('.btn-mode, .btn-phase').forEach(b => b.classList.remove('is-active'));
  }

  document.querySelectorAll('.pill[data-tema]').forEach(btn => {
    btn.addEventListener('click', () => seleccionarTema(btn.dataset.tema));
  });

  document.querySelectorAll('.btn-opt[data-monitores]').forEach(btn => {
    btn.addEventListener('click', () => {
      numMonitores = parseInt(btn.dataset.monitores, 10) || 1;
      document.querySelectorAll('.btn-opt[data-monitores]').forEach(b => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      wrapEl.classList.toggle('is-dual', numMonitores >= 2);
      if (numMonitores >= 2 && rendererSec) {
        rendererSec.cargarTema(state.tema, { pantalla: 'secundaria' }).then(renderTodo);
      } else {
        renderTodo();
      }
    });
  });

  document.querySelectorAll('input[data-stat]').forEach(chk => {
    chk.addEventListener('change', () => {
      state.hudStats[chk.dataset.stat] = chk.checked;
      renderTodo();
    });
  });

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
      renderTodo();
    });
  });

  document.querySelectorAll('.btn-phase').forEach(btn => {
    btn.addEventListener('click', () => {
      limpiarModos();
      btn.classList.add('is-active');
      state.modoHora = 3;
      state.horaFija = parseFloat(btn.dataset.hora);
      sliderEl.value = state.horaFija;
      renderTodo();
    });
  });

  sliderEl.addEventListener('input', () => {
    limpiarModos();
    state.modoHora = 3;
    state.horaFija = parseFloat(sliderEl.value);
    renderTodo();
  });

  const btnHud = document.getElementById('btn-hud');
  btnHud.addEventListener('click', () => {
    state.mostrarHud = !state.mostrarHud;
    btnHud.textContent = `HUD: ${state.mostrarHud ? 'ON' : 'OFF'}`;
    renderTodo();
  });

  document.getElementById('btn-fullscreen').addEventListener('click', () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (wrapEl.requestFullscreen) {
      wrapEl.requestFullscreen();
    }
  });

  document.querySelectorAll('.world-card').forEach(card => {
    const id = card.dataset.world;
    const img = card.querySelector('.world-media img');
    let faseAct = 'dorado';
    let panAct = 'm1';

    function actualizaCardImg() {
      const pref = panAct === 'm2' ? 'm2-' : '';
      img.src = `previews/${id}/${pref}${faseAct}.png`;
    }

    card.querySelectorAll('.phase-switch button[data-fase]').forEach(btn => {
      btn.addEventListener('click', () => {
        card.querySelectorAll('.phase-switch button[data-fase]').forEach(b => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        faseAct = btn.dataset.fase;
        actualizaCardImg();
      });
    });

    card.querySelectorAll('.phase-switch button[data-pan]').forEach(btn => {
      btn.addEventListener('click', () => {
        card.querySelectorAll('.phase-switch button[data-pan]').forEach(b => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        panAct = btn.dataset.pan;
        actualizaCardImg();
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

  setInterval(() => { state.tick++; renderTodo(); }, 100);
  seleccionaYCarga(state.tema);
})();
