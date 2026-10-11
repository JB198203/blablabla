#!/usr/bin/env python3
"""Diagnostic « prêt pour un DJ » de chaque morceau de site/audio/ (MP3 ou WAV).

Pour chaque fichier :
  - tempo : BPM mesuré par fenêtres de 20 s là où le kick tourne ; un écart > 3 BPM rend le calage difficile ;
  - intro : nombre de mesures avant l'arrivée du kick (un DJ en veut 16 à 32) ;
  - outro : nombre de mesures entre le dernier kick et la fin ;
  - loudness intégrée (LUFS) et true peak (dBTP) via le filtre ebur128 de ffmpeg.

Usage : python3 tools/dj_check.py [fichiers...]   (défaut : site/audio/*.mp3 et *.wav)
"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tracks import estimate_bpm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RATE = 4000


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(RATE),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32)


def loudness(path):
    err = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-filter_complex", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    summary = err[err.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", summary)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary)
    return (float(i.group(1)) if i else None, float(tp.group(1)) if tp else None)


def low_energy(x):
    """Énergie des basses (≈ kick) par tranche de 0,1 s."""
    hop = RATE // 10
    n = len(x) // hop
    spec = np.abs(np.fft.rfft(x[: n * hop].reshape(n, hop), axis=1))
    freqs = np.fft.rfftfreq(hop, 1 / RATE)
    return spec[:, (freqs >= 40) & (freqs <= 150)].mean(axis=1), hop


def tempo_range(x):
    """BPM par fenêtres de 20 s, uniquement là où le kick tourne (les breakdowns faussent la mesure).

    On garde les 10e et 90e centiles pour écarter les fenêtres aberrantes.
    """
    low, hop = low_energy(x)
    thr = 0.5 * np.percentile(low, 90)
    win, step = 20 * RATE, 10 * RATE
    bpms = []
    for s in range(0, max(1, len(x) - win), step):
        seg = low[s // hop:(s + win) // hop]
        if len(seg) and (seg > thr).mean() > 0.6:
            b = estimate_bpm(x[s:s + win])
            if b:
                bpms.append(b)
    if not bpms:
        return None, None
    return int(np.percentile(bpms, 10)), int(np.percentile(bpms, 90))


def kick_span(x):
    """Premier et dernier instant où les basses (≈ kick) dépassent la moitié de leur niveau typique."""
    low, hop = low_energy(x)
    n = len(low)
    on = np.where(low > 0.5 * np.percentile(low, 90))[0]
    if not len(on):
        return None, None
    return on[0] * hop / RATE, (n - on[-1]) * hop / RATE


def main():
    files = [Path(f) for f in sys.argv[1:]] or sorted(
        list((ROOT / "site" / "audio").glob("*.mp3")) + list((ROOT / "site" / "audio").glob("*.wav")))
    print(f"{'morceau':40s} {'tempo':>11s} {'intro':>9s} {'outro':>9s} {'LUFS':>6s} {'TP':>6s}  remarques")
    for f in files:
        x = decode(f)
        lo, hi = tempo_range(x)
        bpm = estimate_bpm(x)
        intro_s, outro_s = kick_span(x)
        bar = 4 * 60 / bpm if bpm else None
        intro = intro_s / bar if bar and intro_s is not None else None
        outro = outro_s / bar if bar and outro_s is not None else None
        lufs, tp = loudness(f)
        notes = []
        if lo and hi - lo > 3:
            notes.append("tempo variable")
        if intro is not None and intro < 8:
            notes.append("intro courte")
        if outro is not None and outro < 8:
            notes.append("outro courte")
        if tp is not None and tp > -0.3:
            notes.append("peak à 0 dB")
        tempo = "?" if not lo else (f"{lo}-{hi}" if hi != lo else f"{lo}")
        print(f"{f.stem[:40]:40s} {tempo:>11s} {(f'{intro:.0f} mes.' if intro is not None else '?'):>9s} "
              f"{(f'{outro:.0f} mes.' if outro is not None else '?'):>9s} "
              f"{(f'{lufs:.1f}' if lufs is not None else '?'):>6s} {(f'{tp:.1f}' if tp is not None else '?'):>6s}  "
              f"{', '.join(notes)}")


if __name__ == "__main__":
    main()
