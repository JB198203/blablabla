#!/usr/bin/env python3
"""Indexe les MP3 de site/audio/ et écrit site/audio/tracks.js pour le lecteur.

Pour chaque fichier : titre (tag ID3 ou nom de fichier), BPM (tag TBPM),
durée et forme d'onde (peaks). Les champs édités à la main dans tracks.js
(title, bpm, key) sont conservés d'une exécution à l'autre.

Usage : python3 tools/build_tracks.py
Ordre de la playlist : alphabétique par nom de fichier (préfixer 01_, 02_...).
Versions : « 04_Squirrel.mp3 » et « 04_Squirrel_1.mp3 » forment un seul morceau
avec deux versions (sélecteur V1 / V2 dans le lecteur).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "site" / "audio"
OUT = AUDIO / "tracks.js"
PEAKS = 180


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:format_tags",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    fmt = json.loads(out)["format"]
    tags = {k.lower(): v for k, v in fmt.get("tags", {}).items()}
    return float(fmt["duration"]), tags


def decode(path, rate=4000):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(rate),
         "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32)


def peaks(x):
    # RMS plutôt que crête : sur des masters très compressés, les crêtes sont plates.
    if not len(x):
        return []
    p = np.array([np.sqrt((c ** 2).mean()) if len(c) else 0 for c in np.array_split(x, PEAKS)])
    p = (p / (p.max() or 1)) ** 1.5
    return [round(float(v), 3) for v in p]


def estimate_bpm(x, rate=4000, lo=120, hi=240):
    """Tempo approximatif par autocorrélation de l'enveloppe d'attaques.

    Plage limitée à 120–240 BPM (hardbass → frenchcore) pour éviter les
    erreurs de demi-tempo ; les multiples (2 et 4 temps) renforcent le bon
    candidat. Précision ~±2 BPM : à corriger à la main dans tracks.js si besoin.
    """
    hop = 8  # 2 ms
    n = len(x) // hop
    if n < 5000:
        return None
    env = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    env = np.convolve(env, np.ones(5) / 5, "same")
    onset = np.maximum(np.diff(env), 0)
    onset -= onset.mean()
    fps = rate / hop
    ac = lambda l: np.dot(onset[:-l], onset[l:])
    lags = np.arange(int(fps * 60 / hi), int(fps * 60 / lo) + 2)
    score = np.array([ac(l) + 0.5 * ac(2 * l) + 0.5 * ac(4 * l) for l in lags])
    i = int(score.argmax())
    d = 0.0
    if 0 < i < len(score) - 1:
        a, b, c = score[i - 1: i + 2]
        d = 0.5 * (a - c) / (a - 2 * b + c)
    return int(round(60 * fps / (lags[i] + d)))


def clean_title(s):
    s = re.sub(r"^\d+[\s._-]*", "", s.strip())
    return re.sub(r"_+", " ", s).strip()


def title_from(path, tags):
    return clean_title(tags.get("title") or "") or clean_title(path.stem) or path.stem


def group_key(path):
    """« 04_Squirrel_1.mp3 » → (« 04_Squirrel », 1) : les suffixes _1, _2… sont d'autres versions Suno."""
    m = re.match(r"^(.*?)_(\d)$", path.stem)
    return (m.group(1), int(m.group(2))) if m else (path.stem, 0)


def load_existing():
    """Champs édités à la main, indexés par fichier (titre/key du morceau, bpm de la version)."""
    if not OUT.exists():
        return {}
    txt = OUT.read_text(encoding="utf-8")
    m = re.search(r"window\.TRACKS\s*=\s*(\[.*\]);?\s*$", txt, re.S)
    out = {}
    try:
        for t in json.loads(m.group(1)) if m else []:
            for v in t.get("versions", [t]):
                out[v["file"]] = {"title": t.get("title"), "key": t.get("key"), "bpm": v.get("bpm")}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}
    return out


def main():
    files = sorted(AUDIO.glob("*.mp3"), key=lambda p: group_key(p))
    existing = load_existing()
    groups = {}
    for f in files:
        duration, tags = probe(f)
        x = decode(f)
        bpm = tags.get("tbpm") or tags.get("bpm")
        old = existing.get(f.name, {})
        v = {
            "file": f.name,
            "bpm": old.get("bpm") or (int(float(bpm)) if bpm and bpm.replace(".", "").isdigit() else estimate_bpm(x)),
            "duration": round(duration, 2),
            "peaks": peaks(x),
        }
        base, _ = group_key(f)
        t = groups.setdefault(base, {
            "title": old.get("title") or title_from(f, tags),
            "key": old.get("key") or tags.get("initialkey") or tags.get("tkey"),
            "versions": [],
        })
        t["versions"].append(v)
        print(f"  {f.name:42s} {t['title'][:30]:30s} {v['bpm'] or '-':>4} BPM  {duration:6.1f}s")

    tracks = list(groups.values())
    OUT.write_text(
        "// Généré par tools/build_tracks.py — title, key et bpm peuvent être édités à la main.\n"
        "window.TRACKS = " + json.dumps(tracks, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    n = sum(len(t["versions"]) for t in tracks)
    print(f"{len(tracks)} morceaux ({n} fichiers) → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
