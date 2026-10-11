// Lecteur KASHING : playlist, forme d'onde cliquable, lasers qui réagissent au son.
// La liste des morceaux vient de audio/tracks.js, généré par tools/build_tracks.py.
(() => {
  const tracks = Array.isArray(window.TRACKS) ? window.TRACKS : [];
  const $ = (id) => document.getElementById(id);
  const audio = $('audio');
  const playlist = $('playlist');
  const wave = $('wave');
  const wg = wave.getContext('2d');
  const playBtn = $('playBtn');
  const root = document.documentElement;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  let current = -1;

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
    const li = document.createElement('li');
    const b = document.createElement('button');
    b.type = 'button';
    b.innerHTML = `<span class="pl-n">${String(i + 1).padStart(2, '0')}</span>
      <span class="pl-title"></span>
      <span class="pl-bpm">${t.bpm ? t.bpm + ' BPM' : ''}</span>
      <span class="pl-dur">${fmt(t.duration)}</span>`;
    b.querySelector('.pl-title').textContent = t.title;
    b.addEventListener('click', () => (i === current ? toggle() : load(i, true)));
    li.appendChild(b);
    playlist.appendChild(li);
  });

  function load(i, autoplay) {
    if (!tracks.length) return;
    current = (i + tracks.length) % tracks.length;
    const t = tracks[current];
    audio.src = 'audio/' + encodeURIComponent(t.file);
    $('nowTitle').textContent = t.title;
    $('nowMeta').textContent = [t.bpm && `${t.bpm} BPM`, t.key, fmt(t.duration)].filter(Boolean).join(' · ');
    [...playlist.children].forEach((li, n) => li.classList.toggle('is-current', n === current));
    if ('mediaSession' in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: t.title, artist: 'KASHING',
        artwork: [{ src: 'mask.svg', sizes: '512x512', type: 'image/svg+xml' }],
      });
    }
    drawWave();
    if (autoplay) play();
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
    $('musique').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' });
    if (tracks.length) play();
  });
  audio.addEventListener('play', () => { playBtn.textContent = '❚❚'; playBtn.setAttribute('aria-label', 'Pause'); });
  audio.addEventListener('pause', () => { playBtn.textContent = '▶'; playBtn.setAttribute('aria-label', 'Lecture'); });
  audio.addEventListener('ended', () => load(current + 1, true));
  audio.addEventListener('timeupdate', () => {
    $('time').textContent = `${fmt(audio.currentTime)} / ${fmt(audio.duration || tracks[current]?.duration)}`;
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
    if (!t || !t.peaks || !t.peaks.length) return;
    const peaks = t.peaks;
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
        const bpm = tracks[current]?.bpm || 200;
        target = Math.exp(-((audio.currentTime * bpm / 60) % 1) * 6);
      }
      drawWave();
    }
    energy += (target - energy) * (target > energy ? 0.6 : 0.15);
    root.style.setProperty('--energy', energy.toFixed(3));
    requestAnimationFrame(frame);
  }
  if (!reduceMotion) frame();

  if (tracks.length) load(0, false);
})();
