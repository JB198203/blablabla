#!/usr/bin/env python3
"""Animation de la marque KASHING sur un extrait de morceau.

L'emblème (assets/kashing_logo.png, détouré de l'image d'origine par tools/cutout_logo.py)
rebondit sur le kick : il saute, grossit et bascule d'un côté puis de l'autre au tempo.
Les pixels d'origine sont gardés tels quels ; l'image n'est jamais agrandie au-delà de sa
taille native. Ouverture en zoom avant, « KASHING » en chrome dessous. Dans la fente, un
scanner rouge façon K2000 balaie de gauche à droite au tempo (--no-scanner pour l'enlever).

  python3 tools/make_logo_anim.py site/audio/15_Here_we_are.mp3                 # carré 1080, 8 s, sur le drop
  python3 tools/make_logo_anim.py track.mp3 --format wide --duration 5 --start 36
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_clip as mc  # noqa: E402

LOGO = mc.ROOT / "assets" / "kashing_logo.png"
SLOT = (440, 533, 850, 560)   # fente dans assets/kashing_logo.png (x0, y0, x1, y1), pour le scanner
RED = (255, 28, 18)


class Scanner:
    """Point rouge qui va et vient dans la fente avec une traînée (K2000), plus fort sur le kick."""

    def __init__(self, size, k):
        self.size = size
        self.x0, self.y0, self.x1, self.y1 = (v * k for v in SLOT)
        self.h = self.y1 - self.y0
        self.mask = Image.new("L", size)
        ImageDraw.Draw(self.mask).rounded_rectangle([self.x0, self.y0, self.x1, self.y1],
                                                    radius=self.h / 2, fill=255)

    @staticmethod
    def pos(beats):
        """Aller-retour toutes les 4 temps (un passage = 2 temps), ralenti aux extrémités."""
        ph = (beats / 2) % 2
        u = ph if ph < 1 else 2 - ph
        return (1 - np.cos(np.pi * u)) / 2

    def render(self, beats, energy):
        layer = Image.new("RGBA", self.size)
        d = ImageDraw.Draw(layer)
        span = self.x1 - self.x0 - self.h
        for i in range(12, -1, -1):                     # traînée : positions passées, de plus en plus pâles
            u = self.pos(beats - i * 0.045)
            cx = self.x0 + self.h / 2 + u * span
            a = int(255 * (1 - i / 13) ** 2)
            w = self.h * (1.6 if i == 0 else 1.2)
            d.ellipse([cx - w, self.y0 - 2, cx + w, self.y1 + 2], fill=RED + (a,))
        core = Image.new("RGBA", self.size)
        core.paste(layer, (0, 0), self.mask)            # la lumière reste dans la fente
        halo = core.filter(ImageFilter.GaussianBlur(self.h * 0.9))
        level = 0.75 + 0.25 * energy
        out = Image.alpha_composite(Image.alpha_composite(halo, halo), core)  # halo doublé : effet néon
        out.putalpha(out.getchannel("A").point(lambda v: int(min(255, v * level))))
        return out

FORMATS = {"square": (1080, 1080), "wide": (1920, 1080), "reel": (1080, 1920)}


def background(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w * .6)) ** 2 + ((yy - h / 2) / (h * .6)) ** 2)
    v = np.clip(34 - 26 * d, 6, 34)
    rng = np.random.default_rng(3)
    v = v + rng.normal(0, 2.2, (h, w))
    arr = np.stack([v * 1.0, v * 0.98, v * 0.95], axis=-1)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def wordmark(w, size):
    font = ImageFont.truetype(str(mc.FONTS / "Unbounded.ttf"), size)
    bb = font.getbbox("KASHING")
    a = Image.new("L", (w, bb[3] - bb[1] + 30))
    ImageDraw.Draw(a).text(((w - (bb[2] - bb[0])) / 2 - bb[0], 15 - bb[1]), "KASHING", font=font, fill=255)
    word = mc.chrome_fill(a)
    shadow = Image.new("RGBA", word.size, (0, 0, 0, 0))
    shadow.putalpha(a.filter(ImageFilter.GaussianBlur(8)))
    out = Image.new("RGBA", word.size)
    out.alpha_composite(shadow, (0, 0))
    out.alpha_composite(word)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mp3", type=Path)
    ap.add_argument("--format", choices=FORMATS, default="square")
    ap.add_argument("--start", type=float)
    ap.add_argument("--duration", type=float, default=8)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--no-scanner", action="store_true", help="sans le scanner rouge dans la fente")
    a = ap.parse_args()

    W, H = FORMATS[a.format]
    fps = 30
    mc.FPS = fps
    x = mc.decode(a.mp3)
    start = a.start if a.start is not None else mc.find_drop(x, mc.SR, a.duration)
    seg = x[int(start * mc.SR): int((start + a.duration) * mc.SR)]
    frames = int(len(seg) / mc.SR * fps)
    kick, spec = mc.features(seg, mc.SR, frames)
    title, bpm = mc.track_info(a.mp3)
    bpm = bpm or 190
    punch = kick ** 1.5                               # kick plus sec : petits coups ignorés, gros coups marqués

    src = Image.open(LOGO).convert("RGBA")
    logo_w = min(int(min(W, H) * 0.66), src.width)
    lh = int(src.height * logo_w / src.width)
    # maître légèrement plus grand que l'affichage (marge pour le rebond), jamais plus grand que la source
    mw = min(src.width, int(logo_w * 1.1))
    master = src.resize((mw, int(src.height * mw / src.width)), Image.LANCZOS)
    k = mw / src.width
    scanner = None if a.no_scanner else Scanner(master.size, k)
    bg = background(W, H)
    word = wordmark(W, int(min(W, H) * 0.075))
    ly = int(H * 0.47 - lh / 2) - (word.height // 2)
    wy = ly + lh + int(min(W, H) * 0.02)

    out = a.out or mc.ROOT / "clips" / f"logo_{a.mp3.stem}_{a.format}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
           "-i", "-", "-ss", f"{start:.3f}", "-t", f"{a.duration:.3f}", "-i", str(a.mp3), "-map", "0:v", "-map", "1:a",
           "-af", f"afade=t=in:d=0.3,afade=t=out:st={max(0, a.duration - 1):.2f}:d=1",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for f in range(frames):
            t, e = f / fps, float(kick[f])
            intro = min(1.0, t / 0.8)                      # ouverture : zoom + fondu sur 0,8 s
            ease = 1 - (1 - intro) ** 3
            p = float(punch[f])
            img = master
            if scanner is not None:
                img = Image.alpha_composite(master, scanner.render(t * bpm / 60, e))
            sc = (0.82 + 0.18 * ease) * (1 + 0.08 * p) * logo_w / mw
            img = img.resize((int(img.width * sc), int(img.height * sc)), Image.BICUBIC)
            # bascule gauche / droite : un aller-retour toutes les 2 temps, amplitude selon le kick
            tilt = 4 * p * np.sin(np.pi * t * bpm / 60)
            img = img.rotate(tilt, resample=Image.BICUBIC, expand=True)
            jump = int(min(W, H) * 0.045 * p)
            if ease < 1:
                img.putalpha(img.getchannel("A").point(lambda v, k=ease: int(v * k)))
            frame = bg.copy()
            frame.alpha_composite(img, ((W - img.width) // 2, ly + (lh - img.height) // 2 - jump))
            wa = max(0.0, min(1.0, (t - 0.5) / 0.6))       # le nom arrive juste après
            if wa > 0:
                wimg = word.copy()
                wimg.putalpha(wimg.getchannel("A").point(lambda v, k=wa: int(v * k)))
                frame.alpha_composite(wimg, (0, wy))
            rgb = frame.convert("RGB")
            if e > 0.9:
                rgb = Image.blend(rgb, Image.new("RGB", (W, H), (255, 255, 255)), (e - 0.9) * 0.5)
            proc.stdin.write(rgb.tobytes())
    finally:
        proc.stdin.close()
        proc.wait()
    if proc.returncode:
        sys.exit(f"ffmpeg a échoué ({proc.returncode})")
    print(f"  → {out}  (début {start:.1f}s)")


if __name__ == "__main__":
    main()
