// Lecteur KASHING : playlist, forme d'onde cliquable, lasers qui réagissent au son.
// La liste des morceaux vient de audio/tracks.js, généré par tools/build_tracks.py.
(() => {
  // Genres phares d'abord, puis les morceaux « hors-piste » (focus: false).
  const all = Array.isArray(window.TRACKS) ? window.TRACKS : [];
  const tracks = [...all.filter((t) => t.focus !== false), ...all.filter((t) => t.focus === false)];
  const $ = (id) => document.getElementById(id);
  const audio = $('audio');
  const playlist = $('playlist');
  const wave = $('wave');
  const wg = wave.getContext('2d');
  const playBtn = $('playBtn');
  const root = document.documentElement;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  let current = -1;
  // Un morceau peut avoir plusieurs versions Suno ; t.v = version choisie.
  const V = (t) => t.versions[t.v || 0];

  const fmt = (s) => {
    if (!isFinite(s)) return '0:00';
    s = Math.floor(s);
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  };

  // --- Playlist ---------------------------------------------------------
  $('trackCount').textContent = tracks.length ? `${tracks.length} track${tracks.length > 1 ? 's' : ''}` : '';
  $('empty').hidden = tracks.length > 0;
  if (!tracks.length) $('player').querySelector('.now').hidden = true;

  tracks.forEach((t, i) => {
    if (t.focus === false && (i === 0 || tracks[i - 1].focus !== false)) {
      const sep = document.createElement('li');
      sep.className = 'pl-sep';
      sep.textContent = 'Off the map';
      playlist.appendChild(sep);
    }
    const li = document.createElement('li');
    li.dataset.index = i;
    const b = document.createElement('button');
    b.type = 'button';
    const v = V(t);
    b.innerHTML = `<span class="pl-n">${String(i + 1).padStart(2, '0')}</span>
      <span class="pl-title"></span>
      <span class="pl-dur">${fmt(v.duration)}</span>`;
    b.querySelector('.pl-title').textContent = t.title;
    if (t.versions.length > 1) {
      const tag = document.createElement('span');
      tag.className = 'pl-ver';
      tag.textContent = `${t.versions.length} versions`;
      b.querySelector('.pl-title').appendChild(tag);
    }
    b.addEventListener('click', () => (i === current ? toggle() : load(i, true)));
    li.appendChild(b);
    playlist.appendChild(li);
  });

  function load(i, autoplay, startAt = 0) {
    if (!tracks.length) return;
    current = (i + tracks.length) % tracks.length;
    const t = tracks[current];
    const v = V(t);
    audio.src = 'audio/' + encodeURIComponent(v.file);
    if (startAt) audio.addEventListener('loadedmetadata', () => { audio.currentTime = Math.min(startAt, audio.duration - 1); }, { once: true });
    $('nowTitle').textContent = t.title;
    $('nowMeta').textContent = [t.key, fmt(v.duration)].filter(Boolean).join(' · ');
    renderVersions(t);
    playlist.querySelectorAll('li[data-index]').forEach((li) => li.classList.toggle('is-current', +li.dataset.index === current));
    if ('mediaSession' in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: t.title, artist: 'KASHING',
        artwork: [{ src: 'logo-512.png', sizes: '512x512', type: 'image/png' }],
      });
    }
    drawWave();
    if (autoplay) play();
  }

  // Sélecteur V1 / V2 : garde la position pour comparer les versions à l'oreille.
  function renderVersions(t) {
    const box = $('versions');
    box.replaceChildren();
    box.hidden = t.versions.length < 2;
    t.versions.forEach((_, n) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'ver' + (n === (t.v || 0) ? ' is-on' : '');
      b.textContent = `V${n + 1}`;
      b.setAttribute('aria-pressed', String(n === (t.v || 0)));
      b.setAttribute('aria-label', `Version ${n + 1}`);
      b.addEventListener('click', () => {
        if (n === (t.v || 0)) return;
        const wasPlaying = !audio.paused;
        t.v = n;
        load(current, wasPlaying, audio.currentTime);
      });
      box.appendChild(b);
    });
  }

  function play() {
    if (current < 0) load(0, false);
    setupAnalyser();
    audio.play().catch(() => {});
  }
  function toggle() { audio.paused ? play() : audio.pause(); }

  playBtn.addEventListener('click', toggle);
  $('prevBtn').addEventListener('click', () => load(audio.currentTime > 3 ? current : current - 1, true));
  $('nextBtn').addEventListener('click', () => load(current + 1, true));
  $('heroPlay').addEventListener('click', () => {
    $('music').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' });
    if (tracks.length) play();
  });
  audio.addEventListener('play', () => { playBtn.textContent = '❚❚'; playBtn.setAttribute('aria-label', 'Pause'); });
  audio.addEventListener('pause', () => { playBtn.textContent = '▶'; playBtn.setAttribute('aria-label', 'Play'); });
  audio.addEventListener('ended', () => load(current + 1, true));
  audio.addEventListener('timeupdate', () => {
    $('time').textContent = `${fmt(audio.currentTime)} / ${fmt(audio.duration || (tracks[current] && V(tracks[current]).duration))}`;
    if (reduceMotion) drawWave();
  });

  if ('mediaSession' in navigator) {
    navigator.mediaSession.setActionHandler('previoustrack', () => load(current - 1, true));
    navigator.mediaSession.setActionHandler('nexttrack', () => load(current + 1, true));
  }

  // --- Forme d'onde -----------------------------------------------------
  function drawWave() {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    const w = (wave.width = wave.clientWidth * dpr);
    const h = (wave.height = wave.clientHeight * dpr);
    wg.clearRect(0, 0, w, h);
    const t = tracks[current];
    const peaks = t && V(t).peaks;
    if (!peaks || !peaks.length) return;
    const progress = audio.duration ? audio.currentTime / audio.duration : 0;
    const bw = w / peaks.length;
    const grad = wg.createLinearGradient(0, 0, w, 0);
    grad.addColorStop(0, '#22e8ff');
    grad.addColorStop(1, '#ff2bd6');
    peaks.forEach((p, i) => {
      const bh = Math.max(2 * dpr, p * h);
      wg.fillStyle = i / peaks.length < progress ? grad : '#262b3a';
      wg.fillRect(i * bw, (h - bh) / 2, Math.max(1, bw - dpr), bh);
    });
  }
  wave.addEventListener('click', (e) => {
    if (!audio.duration) return;
    const r = wave.getBoundingClientRect();
    audio.currentTime = ((e.clientX - r.left) / r.width) * audio.duration;
    drawWave();
  });
  addEventListener('resize', drawWave);

  // --- Énergie → lasers -------------------------------------------------
  // En http(s), on mesure vraiment les basses. En file://, Chrome rend un
  // MediaElementSource muet : on simule alors une pulsation au tempo.
  let analyser, bins;
  function setupAnalyser() {
    if (analyser || !location.protocol.startsWith('http')) return;
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const src = ctx.createMediaElementSource(audio);
      analyser = ctx.createAnalyser();
      analyser.fftSize = 1024;
      analyser.smoothingTimeConstant = 0.6;
      bins = new Uint8Array(analyser.frequencyBinCount);
      src.connect(analyser).connect(ctx.destination);
      audio.addEventListener('play', () => ctx.resume());
    } catch (_) { analyser = null; }
  }

  // --- Scanner K2000 dans la fente du logo ------------------------------
  // Même calcul que les vidéos (tools/logo_fx.py) : un passage toutes les 2 temps, traînée, halo.
  const scan = document.querySelector('.scanner');
  const sg = scan && scan.getContext('2d');
  const SLOT = { x0: 0.098, x1: 0.902, y0: 0.355, y1: 0.645 };   // fente, en fraction du canevas
  const kitt = (beats) => {
    const ph = (beats / 2) % 2;
    const u = ph < 1 ? ph : 2 - ph;
    return (1 - Math.cos(Math.PI * u)) / 2;
  };
  function drawScanner(beats, level) {
    if (!sg) return;
    const dpr = Math.min(devicePixelRatio || 1, 2);
    const w = (scan.width = scan.clientWidth * dpr);
    const h = (scan.height = scan.clientHeight * dpr);
    const x0 = SLOT.x0 * w, x1 = SLOT.x1 * w, y0 = SLOT.y0 * h, y1 = SLOT.y1 * h, sh = y1 - y0;
    const span = x1 - x0 - sh;
    const blobs = (g) => {
      for (let i = 12; i >= 0; i--) {
        const cx = x0 + sh / 2 + kitt(beats - i * 0.045) * span;
        const r = sh * (i === 0 ? 1.6 : 1.2);
        g.globalAlpha = level * (1 - i / 13) ** 2;
        g.beginPath();
        g.ellipse(cx, (y0 + y1) / 2, r, sh / 2 + 1, 0, 0, Math.PI * 2);
        g.fill();
      }
    };
    sg.clearRect(0, 0, w, h);
    sg.fillStyle = '#ff1c12';
    sg.save();                                    // halo : déborde légèrement sur l'or
    sg.shadowColor = '#ff1c12';
    sg.shadowBlur = sh * 1.4;
    sg.globalCompositeOperation = 'lighter';
    blobs(sg);
    sg.restore();
    sg.save();                                    // cœur : reste dans la fente
    sg.beginPath();
    sg.roundRect(x0, y0, x1 - x0, sh, sh / 2);
    sg.clip();
    blobs(sg);
    sg.restore();
    sg.globalAlpha = 1;
  }

  let energy = 0;
  function frame() {
    let target = 0;
    if (!audio.paused) {
      if (analyser) {
        analyser.getByteFrequencyData(bins);
        let sum = 0;
        for (let i = 1; i < 8; i++) sum += bins[i]; // ~40–350 Hz : le kick
        target = Math.max(0, (sum / 7 - 120) / 135);
      } else {
        const bpm = (tracks[current] && V(tracks[current]).bpm) || 200;
        target = Math.exp(-((audio.currentTime * bpm / 60) % 1) * 6);
      }
      drawWave();
    }
    energy += (target - energy) * (target > energy ? 0.6 : 0.15);
    root.style.setProperty('--energy', energy.toFixed(3));
    // à l'arrêt, le scanner balaie doucement (~120 BPM) ; en lecture, il suit le tempo du morceau
    const bpm = (tracks[current] && V(tracks[current]).bpm) || 190;
    const beats = audio.paused ? performance.now() / 500 : audio.currentTime * bpm / 60;
    root.style.setProperty('--tilt', `${(4 * energy * Math.sin(Math.PI * beats)).toFixed(2)}deg`);
    drawScanner(beats, 0.75 + 0.25 * energy);
    requestAnimationFrame(frame);
  }
  if (!reduceMotion) frame();
  else drawScanner(1, 1);                         // mouvement réduit : scanner fixe au centre

  if (tracks.length) load(0, false);
})();
