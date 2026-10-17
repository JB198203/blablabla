#!/usr/bin/env python3
"""Reel « réveil » pour Le Matin C'est Maintenant : un écran d'alarme qui sonne et vibre,
puis le drop tombe pile quand l'heure passe à 07:00, et le logo KASHING prend le relais.

  python3 tools/make_alarm_reel.py site/audio/21_Le_Matin_C_est_Maintenant.mp3
  python3 tools/make_alarm_reel.py track.mp3 --drop 201.5 --intro 3 --duration 18

Écran d'alarme générique (pas l'interface d'un vrai téléphone).
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_clip as mc  # noqa: E402

W, H, FPS = 1080, 1920, 30
MONO = mc.FONTS / "JetBrainsMono.ttf"
BRAND = mc.FONTS / "Tourney-BlackItalic.ttf"


def alarm_frame(t, intro, label):
    """Écran d'alarme à l'instant t (0 → intro) : 06:59, puis 07:00 juste avant le drop."""
    img = Image.new("RGB", (W, H), (8, 9, 14))
    d = ImageDraw.Draw(img)
    # halo qui pulse au rythme de la sonnerie (2 bips par seconde)
    ring = 0.5 + 0.5 * np.cos(2 * np.pi * 2 * t)
    halo = Image.new("L", (W, H))
    ImageDraw.Draw(halo).ellipse([W / 2 - 420, 560, W / 2 + 420, 1380], fill=int(70 + 90 * ring))
    halo = halo.filter(ImageFilter.GaussianBlur(120))
    img = Image.composite(Image.new("RGB", (W, H), (120, 20, 30)), img, halo)
    d = ImageDraw.Draw(img)

    clock = "07:00" if t >= intro - 0.9 else "06:59"
    big = ImageFont.truetype(str(MONO), 300)
    d.text((W / 2, 760), clock, font=big, fill=(245, 245, 250), anchor="mm")
    small = ImageFont.truetype(str(MONO), 44)
    d.text((W / 2, 980), label, font=small, fill=(255, 90, 90), anchor="mm")
    d.text((W / 2, 1050), "KASHING", font=ImageFont.truetype(str(BRAND), 64), fill=(200, 205, 220), anchor="mm")

    # boutons génériques
    btn = ImageFont.truetype(str(MONO), 46)
    for x, txt, col in [(W / 2 - 230, "SNOOZE", (60, 64, 80)), (W / 2 + 230, "STOP", (200, 40, 50))]:
        d.rounded_rectangle([x - 190, 1460, x + 190, 1580], radius=60, fill=col)
        d.text((x, 1520), txt, font=btn, fill=(245, 245, 250), anchor="mm")

    # vibration : l'écran tremble pendant les bips
    if ring > 0.6:
        dx, dy = np.random.default_rng(int(t * 100)).integers(-14, 15, 2)
        img = img.transform(img.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), fillcolor=(8, 9, 14))
    # flash blanc sur les 0,25 dernières secondes : le drop arrive
    if t > intro - 0.25:
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), (t - (intro - 0.25)) / 0.25)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mp3", type=Path)
    ap.add_argument("--drop", type=float, help="seconde du drop (sinon détecté)")
    ap.add_argument("--intro", type=float, default=3.0, help="durée de l'écran d'alarme avant le drop")
    ap.add_argument("--duration", type=float, default=17.0, help="durée après le drop")
    ap.add_argument("--label", default="LE MATIN C'EST MAINTENANT")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    x = mc.decode(a.mp3)
    drop = a.drop if a.drop is not None else mc.find_drop(x, mc.SR, a.duration)
    out = a.out or mc.ROOT / "clips" / f"{a.mp3.stem}_alarm.mp4"
    tmp = out.with_suffix(".parts")
    tmp.mkdir(parents=True, exist_ok=True)

    # 1. écran d'alarme, avec le son qui monte vers le drop
    intro = tmp / "intro.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-ss", f"{drop - a.intro:.3f}", "-t", f"{a.intro:.3f}", "-i", str(a.mp3),
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", str(intro)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(int(a.intro * FPS)):
        p.stdin.write(alarm_frame(f / FPS, a.intro, a.label).tobytes())
    p.stdin.close()
    p.wait()

    # 2. le Reel classique à partir du drop (logo qui rebondit, scanner K2000)
    main_part = tmp / "drop.mp4"
    subprocess.run([sys.executable, str(mc.ROOT / "tools" / "make_clip.py"), str(a.mp3), "--start", f"{drop:.3f}",
                    "--duration", f"{a.duration:.3f}", "--out", str(main_part)], check=True)

    # 3. collage
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(intro), "-i", str(main_part), "-filter_complex",
                    "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(out)], check=True)
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    print(f"  → {out}  (drop à {drop:.1f}s)")


if __name__ == "__main__":
    main()
