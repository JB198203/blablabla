#!/usr/bin/env sh
# Génère un Reel + une couverture pour chaque MP3 de site/audio/ dans clips/.
# Une seule version par morceau. Compter ~1 min par clip de 20 s. Les clips déjà générés sont ignorés.
set -e
cd "$(dirname "$0")/.."
for f in site/audio/*.mp3; do
  # versions alternatives (_1, _2…) ignorées : une version par morceau suffit
  case "$f" in *_[0-9].mp3) continue ;; esac
  out="clips/$(basename "${f%.mp3}").mp4"
  [ -f "$out" ] && { echo "déjà fait : $out"; continue; }
  echo "→ $f"
  python3 tools/make_clip.py "$f" --cover --out "$out"
done
