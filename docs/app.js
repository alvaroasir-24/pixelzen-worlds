(() => {
  const WORLDS = [
    {
      id: 'fittoa',
      serie: 'Mushoku Tensei',
      cat: 'anime',
      titulo: 'Región de Fittoa',
      m1: { name: 'Aldea de Buena', sub: 'K407 · Mansión Greyrat y Lago de Fittoa', desc: 'Aldea de Buena con la Mansión Greyrat, torre de mago, cascada lejana, muelle, arco rúnico con cristal de maná y Gran Roble.' },
      m2: { name: 'Base de Perugius', sub: 'Chaos Breaker · Fortaleza sobre Ars', desc: 'Sobre las llanuras de Asura y la Capital Real de Ars flota Chaos Breaker, la fortaleza celeste del Rey Dragón Blindado.' },
      m3: { name: 'Santuario del Teletransporte', sub: 'K407 · Monolito de Maná y Buena', desc: 'Santuario rúnico del bosque de Fittoa con monolito de teletransporte, cabaña del guardabosques y sendero empedrado.' },
      cita: '«Incluso desde un segundo intento, cada mañana bajo el Gran Roble de Buena vale la pena vivirla en serio.» — Rudeus Greyrat',
    },
    {
      id: 'continente-demoniaco',
      serie: 'Mushoku Tensei',
      cat: 'anime',
      titulo: 'Continente Demoníaco',
      m1: { name: 'Rikarisu · Dead End', sub: 'K410 · Basalto y Ruinas de Teletransporte', desc: 'Ciudadela demoníaca de Rikarisu entre agujas de basalto, cristales gigantes de maná, monolitos carmesí y río de obsidiana.' },
      m2: { name: 'Fortaleza Basalto', sub: 'Rikarisu y Rudeus · Invocación Arcana', desc: 'Fortaleza volcánica con torres con cuernos, grietas de lava y Rudeus Greyrat conjurando un hechizo con Aqua Heartia.' },
      m3: { name: 'Puerta de Obsidiana', sub: 'K410 · Abismo Carmesí y Roca Roja', desc: 'Puerta gemela de basalto y obsidiana sobre el profundo cañón volcánico de Rikarisu con cristales de maná.' },
      cita: '«Si confías en los compañeros que caminan a tu lado, incluso el Continente Demoníaco tiene salida.» — Ruijerd Superdia',
    },
    {
      id: 'hunter-x-hunter',
      serie: 'Hunter × Hunter',
      cat: 'anime',
      titulo: 'Isla Ballena y H×H',
      m1: { name: 'Isla Ballena', sub: 'Árbol del Mundo y Muelle de Gon', desc: 'Colosal Árbol del Mundo en la distancia, cabaña de Mito-san, muelle donde Gon pesca, dirigible de Cazadores y Aura Nen.' },
      m2: { name: 'Greed Island', sub: 'Praderas y Torre de Eta y Elena', desc: 'Vastas praderas verdes bajo nubes suaves con la icónica torre de recepción de techo cónico y Gon y Killua jugando.' },
      m3: { name: 'Torre Celestial', sub: 'Piso 251 · Arena del Cielo', desc: 'Silueta monumental de la Torre Celestial alzada sobre una gran plaza urbana iluminada junto al dirigible del Examen.' },
      cita: '«Deberías disfrutar los pequeños desvíos tanto como el objetivo final.» — Ging Freecss',
    },
    {
      id: 'black-clover',
      serie: 'Black Clover',
      cat: 'anime',
      titulo: 'Reino del Trébol y Picas',
      m1: { name: 'Aldea de Hage', sub: 'Cráneo del Demonio y Torre de Grimorios', desc: 'Aldea de Hage bajo el Cráneo del Demonio y estatua del Primer Rey Mago, con la Iglesia, Torre de Grimorios y espada de Asta.' },
      m2: { name: 'Reino de Picas y Asta', sub: 'Fortaleza Helada y Espada Demon-Slayer', desc: 'Cumbres nevadas, el Castillo de Picas bajo el sello del Qliphoth y Asta blandiendo la espada Danma con su grimorio negro.' },
      m3: { name: 'Altar del Grimorio Real', sub: 'Reino del Trébol · Ruinas Góticas', desc: 'Altar gótico y plaza ceremonial de piedra del Trébol con la espada antimagia clavada sobre un sello rúnico iluminado.' },
      cita: '«En las cinco hojas del trébol aguarda el poder que nunca se rinde.» — Asta',
    },
    {
      id: 'spiderman-miles-morales',
      serie: 'Marvel · Spider-Verse',
      cat: 'marvel',
      titulo: 'Miles Morales',
      m1: { name: 'Brooklyn & Estatua', sub: 'Brooklyn · Horizonte de Manhattan', desc: 'Ladrillo de Brooklyn con depósitos de agua, Puente de Brooklyn, Estatua de la Libertad, Manhattan y Miles con chispas Venom.' },
      m2: { name: 'Midtown y Harlem', sub: 'Tierra-1610 · Metro Elevado y Torres', desc: 'Rascacielos Art Déco, tren elevado de Nueva York, azoteas de Harlem con mural neón Spider-Verse y Miles balanceándose.' },
      m3: { name: 'Azotea de Harlem', sub: 'Manhattan · Vigilancia Nocturna', desc: 'Miles Morales vigilando el horizonte iluminado de Manhattan desde una azotea de ladrillo en Brooklyn.' },
      cita: '«Cualquiera puede llevar la máscara. Lo que importa es levantarse siempre una vez más.» — Miles Morales',
    },
    {
      id: 'solo-leveling',
      serie: 'Solo Leveling',
      cat: 'anime',
      titulo: 'Monarca de las Sombras',
      m1: { name: 'Castillo del Monarca', sub: 'Trono Carmesí · Jin-Woo e Igris', desc: 'Ciudadela gótica donde Sung Jin-Woo es proclamado Monarca de las Sombras junto a Igris y su ejército surgido de la oscuridad.' },
      m2: { name: 'Isla de Jeju y Beru', sub: 'Colmena de Hormigas · Rey Beru', desc: 'Acantilados volcánicos de la Isla de Jeju bajo el nido infectado, huevos bioluminiscentes y la imponente silueta alada de Beru.' },
      m3: { name: 'Portal del Monarca', sub: 'Portón Rango S · Dagas Sombra', desc: 'Portón dimensional azul-violeta flanqueado por obeliscos rúnicos y las dagas gemelas de Jin-Woo ante el sello de invocación.' },
      cita: '«Surge.» — Sung Jin-Woo, Monarca de las Sombras',
    },
    {
      id: 'demon-slayer',
      serie: 'Demon Slayer',
      cat: 'anime',
      titulo: 'Kimetsu no Yaiba',
      m1: { name: 'Tren Infinito', sub: 'Mugen Train · Rengoku vs Akaza', desc: 'Claro nocturno junto al Tren Infinito descarrilado donde Kyojuro Rengoku desata la Respiración de la Llama frente a Akaza.' },
      m2: { name: 'Aldea de los Herreros', sub: 'Valle Brumoso · Tokito vs Gyokko', desc: 'Sendero brumoso entre cedros junto al taller de los herreros donde Muichiro Tokito blande la Respiración de la Niebla contra Gyokko.' },
      m3: { name: 'Santuario de Glicinias', sub: 'Monte Fujikasane · Torii y Nichirin', desc: 'Santuario bajo cascadas de glicinias púrpuras que ahuyentan a los demonios, con faroles de piedra y katana Nichirin en el altar.' },
      cita: '«Haz arder tu corazón, supera tus límites y protege a los demás.» — Kyojuro Rengoku',
    },
    {
      id: 'stranger-things',
      serie: 'Stranger Things',
      cat: 'series',
      titulo: 'Hawkins y Upside Down',
      m1: { name: 'Hawkins y Creel House', sub: 'Casa Creel · Azotamentes y Bicis', desc: 'Noche tormentosa en Hawkins bajo la grieta carmesí del Upside Down con el Azotamentes alzándose y los chicos en bici.' },
      m2: { name: 'Bosque y Demogorgon', sub: 'Cabaña Byers · Luces y Demogorgon', desc: 'Linde del bosque de Hawkins con la cabaña iluminada por luces navideñas y la amenaza sombría del Demogorgon entre esporas.' },
      m3: { name: 'Reloj de Creel', sub: 'Maldición de Vecna · Grieta Escarlata', desc: 'El antiguo reloj de pie de la casa Creel atrapado entre grietas rojas del Mundo del Revés y esporas flotantes.' },
      cita: '«Los amigos nunca mienten, ni siquiera cuando el cielo se abre sobre Hawkins.» — Hawkins, Indiana',
    },
    {
      id: 'harry-potter',
      serie: 'Harry Potter',
      cat: 'series',
      titulo: 'Castillo de Hogwarts',
      m1: { name: 'Castillo y Lago Negro', sub: 'Torre de Astronomía y Quidditch', desc: 'Castillo de Hogwarts sobre acantilados de Escocia reflejado en el Lago Negro, barcas iluminadas y Harry tras la Snitch Dorada.' },
      m2: { name: 'Hogsmeade y Expreso', sub: 'Viaducto 5972 y Ciervo Patronus', desc: 'Cabañas nevadas de Hogsmeade con chimeneas humeantes, el Expreso de Hogwarts en el viaducto y el Ciervo Patronus brillante.' },
      m3: { name: 'Andén 9¾ y Reliquias', sub: "King's Cross · Hedwig y Saúco", desc: 'Arco victoriano del Andén 9¾ iluminado con faroles dorados, baúl con Hedwig y el resplandor de las Reliquias de la Muerte.' },
      cita: '«La felicidad se puede hallar hasta en los momentos más oscuros si recuerdas encender la luz.» — Albus Dumbledore',
    },
  ];

  const STAT_KEYS = ['tiempo', 'clima', 'sistema', 'gpu', 'red', 'audio', 'dev', 'foco', 'grimorio'];
  const canvas = document.getElementById('lienzo');
  const canvasSec = document.getElementById('lienzo-sec');
  const canvasBloq = document.getElementById('lienzo-bloq');
  const wrapEl = document.getElementById('canvas-wrap');
  const loadingEl = document.getElementById('canvas-loading');
  const sliderEl = document.getElementById('hora-slider');
  const horaLabelEl = document.getElementById('hora-label');
  const badgeSecEl = document.getElementById('badge-sec');
  const badgeBloqEl = document.getElementById('badge-bloq');

  let numMonitores = 2;

  const renderer = window.PixelZenCanvas.createRenderer(canvas, {
    initialState: {
      tema: 'fittoa',
      pantalla: 'principal',
      modoHora: 3,
      horaFija: 18.75,
      fps: 10,
      mostrarHud: true,
      hudStats: {
        tiempo: true, clima: true, sistema: true, gpu: true,
        red: true, audio: true, dev: true, foco: true, grimorio: true,
      },
      inicioHora: 18.75,
    },
    onTemaLoaded(tema, id) {
      wrapEl.style.background = tema.cielo_fondo || '#060814';
      loadingEl.classList.add('is-hidden');
      actualizaLoreStage(id);
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

  function crearSecundarioRenderer(el, pantallaKey, badgeEl, badgePrefix) {
    if (!el) return null;
    return window.PixelZenCanvas.createRenderer(el, {
      initialState: {
        tema: 'fittoa',
        pantalla: pantallaKey,
        modoHora: 3,
        horaFija: 18.75,
        fps: 10,
        mostrarHud: false,
        inicioHora: 18.75,
      },
      onTemaLoaded(tema) {
        if (badgeEl && tema && tema.nombre) {
          badgeEl.textContent = `${badgePrefix} · ${tema.nombre.toUpperCase()}`;
        }
      },
    });
  }

  const rendererSec = crearSecundarioRenderer(canvasSec, 'secundaria', badgeSecEl, 'MONITOR 2');
  const rendererBloq = crearSecundarioRenderer(canvasBloq, 'bloqueo', badgeBloqEl, 'BLOQUEO');
  const { state } = renderer;

  function sincronizaAuxiliares() {
    for (const aux of [rendererSec, rendererBloq]) {
      if (!aux) continue;
      aux.state.modoHora = state.modoHora;
      aux.state.horaFija = state.horaFija;
      aux.state.inicioMs = state.inicioMs;
      aux.state.inicioHora = state.inicioHora;
      aux.state.tick = state.tick;
    }
  }

  function renderTodo() {
    renderer.render();
    sincronizaAuxiliares();
    if (rendererSec && numMonitores >= 2) rendererSec.render();
    if (rendererBloq && numMonitores >= 3) rendererBloq.render();
  }

  function actualizaLoreStage(id) {
    const w = WORLDS.find(x => x.id === id);
    if (!w) return;
    const tEl = document.getElementById('stage-lore-title');
    const dEl = document.getElementById('stage-lore-desc');
    if (tEl) tEl.textContent = `${w.titulo} (${w.serie})`;
    if (dEl) dEl.textContent = `M1 ${w.m1.name} · M2 ${w.m2.name} · M3 ${w.m3.name}`;
  }

  function seleccionaYCarga(id) {
    loadingEl.classList.remove('is-hidden');
    const jobs = [renderer.cargarTema(id, { pantalla: 'principal' })];
    if (rendererSec && numMonitores >= 2) jobs.push(rendererSec.cargarTema(id, { pantalla: 'secundaria' }));
    if (rendererBloq && numMonitores >= 3) jobs.push(rendererBloq.cargarTema(id, { pantalla: 'bloqueo' }));
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
      wrapEl.classList.toggle('is-dual', numMonitores === 2);
      wrapEl.classList.toggle('is-triple', numMonitores === 3);
      seleccionaYCarga(state.tema);
    });
  });

  function aplicaHudPreset(modo) {
    const sets = {
      all: STAT_KEYS,
      essential: ['tiempo', 'clima', 'sistema', 'grimorio'],
      minimal: ['tiempo', 'grimorio'],
    };
    const activos = sets[modo] || STAT_KEYS;
    state.mostrarHud = true;
    document.getElementById('btn-hud').textContent = 'HUD: ON';
    for (const k of STAT_KEYS) {
      const on = activos.includes(k);
      state.hudStats[k] = on;
      const chk = document.querySelector(`input[data-stat="${k}"]`);
      if (chk) chk.checked = on;
    }
    document.querySelectorAll('.btn-opt[data-hud-preset]').forEach(b => {
      b.classList.toggle('is-active', b.dataset.hudPreset === modo);
    });
    renderTodo();
  }

  document.querySelectorAll('.btn-opt[data-hud-preset]').forEach(btn => {
    btn.addEventListener('click', () => aplicaHudPreset(btn.dataset.hudPreset));
  });

  document.querySelectorAll('input[data-stat]').forEach(chk => {
    chk.addEventListener('change', () => {
      state.hudStats[chk.dataset.stat] = chk.checked;
      document.querySelectorAll('.btn-opt[data-hud-preset]').forEach(b => b.classList.remove('is-active'));
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
    if (document.fullscreenElement) document.exitFullscreen();
    else if (wrapEl.requestFullscreen) wrapEl.requestFullscreen();
  });

  /* GALERÍA DINÁMICA DE 9 MUNDOS × 3 ESCENAS */
  const gridEl = document.getElementById('worlds-grid');
  const cardCtrl = {};

  function previewUrl(id, pan, fase) {
    const pref = pan === 'm2' ? 'm2-' : pan === 'm3' ? 'm3-' : '';
    return `previews/${id}/${pref}${fase}.png`;
  }

  function renderCards() {
    gridEl.innerHTML = '';
    for (const w of WORLDS) {
      const card = document.createElement('article');
      card.className = 'world-card';
      card.dataset.world = w.id;
      card.dataset.cat = w.cat;
      card.innerHTML = `
        <div class="world-media">
          <img src="${previewUrl(w.id, 'm1', 'dorado')}" alt="${w.titulo} (${w.m1.name})" loading="lazy" />
          <span class="world-screen-pill">M1 · ${w.m1.name}</span>
          <div class="phase-switch">
            <div class="phase-sub">
              <button class="is-active" data-pan="m1" title="Monitor 1 Principal">M1</button>
              <button data-pan="m2" title="Monitor 2 Continuación">M2</button>
              <button data-pan="m3" title="Pantalla de Bloqueo">M3</button>
            </div>
            <div class="phase-sub">
              <button data-fase="dia">Día</button>
              <button class="is-active" data-fase="dorado">Dorado</button>
              <button data-fase="noche">Noche</button>
            </div>
          </div>
        </div>
        <div class="world-body">
          <div class="world-top">
            <h3>${w.titulo}</h3>
            <span class="world-serie">${w.serie}</span>
          </div>
          <div class="world-scene-sub">${w.m1.sub}</div>
          <p>${w.m1.desc}</p>
          <div class="world-actions">
            <button class="btn-mini btn-inspect">🔍 3 Vistas</button>
            <button class="btn-mini btn-try" style="border-color:var(--border-gold);color:var(--gold)">▶ Probar en vivo</button>
          </div>
        </div>
      `;

      const img = card.querySelector('.world-media img');
      const pill = card.querySelector('.world-screen-pill');
      const subEl = card.querySelector('.world-scene-sub');
      const descEl = card.querySelector('.world-body p');
      const estadoCard = { pan: 'm1', fase: 'dorado' };

      function syncCard() {
        const info = w[estadoCard.pan];
        img.src = previewUrl(w.id, estadoCard.pan, estadoCard.fase);
        img.alt = `${w.titulo} — ${info.name}`;
        pill.textContent = `${estadoCard.pan.toUpperCase()} · ${info.name}`;
        subEl.textContent = info.sub;
        descEl.textContent = info.desc;
        card.querySelectorAll('button[data-pan]').forEach(b => b.classList.toggle('is-active', b.dataset.pan === estadoCard.pan));
        card.querySelectorAll('button[data-fase]').forEach(b => b.classList.toggle('is-active', b.dataset.fase === estadoCard.fase));
      }

      cardCtrl[w.id] = { estado: estadoCard, sync: syncCard };

      card.querySelector('.phase-switch').addEventListener('click', e => e.stopPropagation());
      card.querySelectorAll('button[data-pan]').forEach(btn => {
        btn.addEventListener('click', () => { estadoCard.pan = btn.dataset.pan; syncCard(); });
      });
      card.querySelectorAll('button[data-fase]').forEach(btn => {
        btn.addEventListener('click', () => { estadoCard.fase = btn.dataset.fase; syncCard(); });
      });
      card.querySelector('.world-media').addEventListener('click', () => abreModal(w.id, estadoCard.pan, estadoCard.fase));
      card.querySelector('.btn-inspect').addEventListener('click', () => abreModal(w.id, estadoCard.pan, estadoCard.fase));
      card.querySelector('.btn-try').addEventListener('click', () => {
        seleccionarTema(w.id);
        document.getElementById('visor').scrollIntoView({ behavior: 'smooth' });
      });

      gridEl.appendChild(card);
    }
  }
  renderCards();

  document.querySelectorAll('#cat-filters button[data-cat]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#cat-filters button[data-cat]').forEach(b => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      const cat = btn.dataset.cat;
      document.querySelectorAll('.world-card').forEach(c => {
        c.classList.toggle('is-hidden', cat !== 'all' && c.dataset.cat !== cat);
      });
    });
  });

  document.querySelectorAll('button[data-global-pan]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('button[data-global-pan]').forEach(b => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      const p = btn.dataset.globalPan;
      Object.values(cardCtrl).forEach(ctrl => { ctrl.estado.pan = p; ctrl.sync(); });
    });
  });

  document.querySelectorAll('button[data-global-fase]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('button[data-global-fase]').forEach(b => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      const f = btn.dataset.globalFase;
      Object.values(cardCtrl).forEach(ctrl => { ctrl.estado.fase = f; ctrl.sync(); });
    });
  });

  /* MODAL LIGHTBOX 3 PANTALLAS */
  const modalEl = document.getElementById('world-modal');
  let modalState = { id: 'fittoa', pan: 'm1', fase: 'dorado' };

  function pintaModal() {
    const w = WORLDS.find(x => x.id === modalState.id) || WORLDS[0];
    const info = w[modalState.pan];
    document.getElementById('modal-serie').textContent = `${w.serie} · ID: ${w.id}`;
    document.getElementById('modal-title').textContent = `${w.titulo} — ${info.name}`;
    document.getElementById('modal-sub').textContent = info.sub;
    document.getElementById('modal-desc').textContent = info.desc;
    document.getElementById('modal-img').src = previewUrl(w.id, modalState.pan, modalState.fase);
    document.getElementById('modal-quote').textContent = w.cita;

    document.querySelectorAll('#modal-pan-btns button').forEach(b => b.classList.toggle('is-active', b.dataset.mpan === modalState.pan));
    document.querySelectorAll('#modal-fase-btns button').forEach(b => b.classList.toggle('is-active', b.dataset.mfase === modalState.fase));

    const trip = document.getElementById('modal-triptych');
    trip.innerHTML = '';
    for (const pan of ['m1', 'm2', 'm3']) {
      const div = document.createElement('div');
      div.className = 'trip-thumb' + (modalState.pan === pan ? ' is-active' : '');
      div.innerHTML = `<img src="${previewUrl(w.id, pan, modalState.fase)}" alt="${w[pan].name}" /><span>${pan.toUpperCase()} · ${w[pan].name}</span>`;
      div.addEventListener('click', () => { modalState.pan = pan; pintaModal(); });
      trip.appendChild(div);
    }
  }

  function abreModal(id, pan = 'm1', fase = 'dorado') {
    modalState = { id, pan, fase };
    pintaModal();
    modalEl.classList.add('is-open');
    modalEl.setAttribute('aria-hidden', 'false');
  }

  function cierraModal() {
    modalEl.classList.remove('is-open');
    modalEl.setAttribute('aria-hidden', 'true');
  }

  document.querySelectorAll('#modal-pan-btns button').forEach(b => b.addEventListener('click', () => { modalState.pan = b.dataset.mpan; pintaModal(); }));
  document.querySelectorAll('#modal-fase-btns button').forEach(b => b.addEventListener('click', () => { modalState.fase = b.dataset.mfase; pintaModal(); }));
  document.getElementById('modal-close').addEventListener('click', cierraModal);
  modalEl.addEventListener('click', e => { if (e.target === modalEl) cierraModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') cierraModal(); });
  document.getElementById('modal-try').addEventListener('click', () => {
    cierraModal();
    seleccionarTema(modalState.id);
    document.getElementById('visor').scrollIntoView({ behavior: 'smooth' });
  });

  document.getElementById('btn-modal-active').addEventListener('click', () => abreModal(state.tema, 'm1', 'dorado'));
  document.getElementById('btn-stage-inspect').addEventListener('click', () => abreModal(state.tema, 'm1', 'dorado'));

  /* GENERADOR DE COMANDO DE INSTALACIÓN */
  const genMundo = document.getElementById('gen-mundo');
  const genModo = document.getElementById('gen-modo');
  const genMon = document.getElementById('gen-mon');
  const genCmd = document.getElementById('gen-cmd');
  const genCopy = document.getElementById('gen-copy');

  function actualizaComando() {
    if (!genMundo || !genCmd) return;
    const m = genMundo.value;
    const mod = genModo.value;
    const mon = genMon.value;
    const flagModo = mod === '21:30' ? '--hora 21:30' : `--${mod}`;
    const cmd = `python windows/pixelzen_win.py --tema ${m} ${flagModo} --monitores ${mon}`;
    genCmd.textContent = cmd;
    genCopy.dataset.copy = cmd;
  }
  [genMundo, genModo, genMon].forEach(el => { if (el) el.addEventListener('change', actualizaComando); });
  actualizaComando();

  /* TABS SO Y COPIAR AL PORTAPAPELES */
  document.querySelectorAll('.os-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.os-tab').forEach(t => t.classList.remove('is-active'));
      document.querySelectorAll('.os-pane').forEach(p => p.classList.remove('is-active'));
      tab.classList.add('is-active');
      const pane = document.querySelector(`.os-pane[data-pane="${tab.dataset.os}"]`);
      if (pane) pane.classList.add('is-active');
    });
  });

  document.querySelectorAll('.copy-btn, #btn-copy-oneliner').forEach(btn => {
    btn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
        const orig = btn.textContent;
        btn.textContent = '✓ ¡Copiado!';
        setTimeout(() => { btn.textContent = orig; }, 1400);
      } catch {
        btn.textContent = 'Usa Ctrl+C';
      }
    });
  });

  setInterval(() => { state.tick++; renderTodo(); }, 100);
  seleccionaYCarga(state.tema);
})();
