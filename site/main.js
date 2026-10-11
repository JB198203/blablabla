// Kick Frenchcore synthétisé en Web Audio : aucune ressource audio à héberger.
(() => {
  const BPM = 200;
  const btn = document.getElementById('kickBtn');
  const label = btn.querySelector('.label');
  const canvas = document.getElementById('scope');
  const g = canvas.getContext('2d');
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  let ctx, out, analyser, data, timer, nextTime = 0, playing = false;

  // Courbe de saturation dure : c'est elle qui donne le grain "distorted kick".
  function distortionCurve(amount) {
    const n = 2048, curve = new Float32Array(n);
    for (let i = 0; i < n; i++) {
      const x = (i * 2) / n - 1;
      curve[i] = ((1 + amount) * x) / (1 + amount * Math.abs(x));
    }
    return curve;
  }

  function setup() {
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    const shaper = ctx.createWaveShaper();
    shaper.curve = distortionCurve(60);
    shaper.oversample = '4x';
    const lowpass = ctx.createBiquadFilter();
    lowpass.type = 'lowpass';
    lowpass.frequency.value = 6000;
    const master = ctx.createGain();
    master.gain.value = 0.35;
    analyser = ctx.createAnalyser();
    analyser.fftSize = 2048;
    data = new Uint8Array(analyser.fftSize);
    shaper.connect(lowpass).connect(master).connect(analyser).connect(ctx.destination);
    out = shaper;
  }

  function kick(t) {
    const osc = ctx.createOscillator();
    const amp = ctx.createGain();
    osc.type = 'sine';
    // Attaque très haute, chute rapide puis queue tonale longue.
    osc.frequency.setValueAtTime(380, t);
    osc.frequency.exponentialRampToValueAtTime(110, t + 0.02);
    osc.frequency.exponentialRampToValueAtTime(48, t + 0.12);
    amp.gain.setValueAtTime(0.0001, t);
    amp.gain.exponentialRampToValueAtTime(1, t + 0.002);
    amp.gain.setValueAtTime(1, t + 0.12);
    amp.gain.exponentialRampToValueAtTime(0.0001, t + 0.28);
    osc.connect(amp).connect(out);
    osc.start(t);
    osc.stop(t + 0.3);

    const delay = Math.max(0, (t - ctx.currentTime) * 1000);
    setTimeout(() => {
      document.body.classList.remove('kick');
      void document.body.offsetWidth;
      document.body.classList.add('kick');
    }, delay);
  }

  function schedule() {
    const step = 60 / BPM;
    while (nextTime < ctx.currentTime + 0.1) {
      kick(nextTime);
      nextTime += step;
    }
  }

  function start() {
    if (!ctx) setup();
    ctx.resume();
    nextTime = ctx.currentTime + 0.05;
    timer = setInterval(schedule, 25);
    playing = true;
    btn.setAttribute('aria-pressed', 'true');
    label.textContent = 'Stop';
  }

  function stop() {
    clearInterval(timer);
    playing = false;
    btn.setAttribute('aria-pressed', 'false');
    label.textContent = 'Tester le kick';
  }

  btn.addEventListener('click', () => (playing ? stop() : start()));

  // Oscilloscope en fond du hero.
  function resize() {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = canvas.clientWidth * dpr;
    canvas.height = canvas.clientHeight * dpr;
  }
  addEventListener('resize', resize);
  resize();

  function draw() {
    const { width: w, height: h } = canvas;
    g.clearRect(0, 0, w, h);
    g.lineWidth = 2 * (devicePixelRatio || 1);
    g.strokeStyle = '#ff2a2a';
    g.beginPath();
    if (analyser && playing) {
      analyser.getByteTimeDomainData(data);
      for (let i = 0; i < data.length; i++) {
        const x = (i / (data.length - 1)) * w;
        const y = h * 0.42 + ((data[i] - 128) / 128) * h * 0.3;
        i ? g.lineTo(x, y) : g.moveTo(x, y);
      }
    } else {
      g.moveTo(0, h * 0.42);
      g.lineTo(w, h * 0.42);
    }
    g.stroke();
    if (!reduceMotion) requestAnimationFrame(draw);
  }
  draw();
})();
