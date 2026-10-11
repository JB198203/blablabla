#!/usr/bin/env python3
"""Génère un Reel vertical KASHING (1080x1920, 30 i/s) à partir d'un MP3.

Visuel « chrome & laser » : masque chromé dont les yeux s'allument sur le kick,
lasers cyan/magenta qui balayent, spectre en bas, flash sur les kicks forts.
Le passage le plus énergique (le drop) est détecté automatiquement.

Usage :
  python3 tools/make_clip.py site/audio/07_Sugar_Spike_Blues.mp3
  python3 tools/make_clip.py track.mp3 --start 62.5 --duration 15 --out clips/x.mp4
  python3 tools/make_clip.py track.mp3 --format youtube --cover   # 16:9, morceau entier
Options utiles : --title "TITRE", --cover (exporte aussi une image de couverture).
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
# Mises en page : « reel » (Instagram / Shorts, 9:16) et « youtube » (16:9, morceau entier).
LAYOUTS = {
    "reel": dict(size=(1080, 1920), fps=30, mask_w=500, mask_y=470, word_y=180, word_size=190,
                 spec_cy=1250, spec_h=80, title_y=1400, meta_y=1464, title_size=52, meta_size=30),
    "youtube": dict(size=(1920, 1080), fps=24, mask_w=360, mask_y=225, word_y=40, word_size=120,
                    spec_cy=790, spec_h=50, title_y=930, meta_y=990, title_size=48, meta_size=28),
}
L = LAYOUTS["reel"]
W, H = L["size"]
FPS = L["fps"]
SR = 22050

BG_TOP, BG_BOTTOM = (5, 6, 10), (12, 14, 30)
CYAN, MAGENTA = (34, 232, 255), (255, 43, 214)
CHROME = [(0, (255, 255, 255)), (.36, (185, 193, 210)), (.5, (43, 48, 64)),
          (.56, (215, 222, 234)), (.82, (115, 123, 144)), (1, (238, 242, 248))]


# --- Audio -----------------------------------------------------------------

def decode(path, sr=SR):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32)


def find_drop(x, sr, duration):
    """Début du passage le plus fort, en privilégiant une montée brutale (le drop)."""
    step = sr // 2
    n = len(x) // step
    rms = np.sqrt((x[: n * step].reshape(n, step) ** 2).mean(axis=1))
    win = int(duration * 2)
    if n <= win:
        return 0.0
    best, best_s = -1.0, 0
    for s in range(8, n - win):
        body = rms[s:s + win].mean()
        jump = max(0.0, rms[s:s + 4].mean() - rms[s - 8:s].mean())
        score = body + 1.5 * jump
        if score > best:
            best, best_s = score, s
    return best_s * step / sr


def features(x, sr, frames):
    """Énergie du kick (0–1) et spectre en 40 bandes (0–1) pour chaque image."""
    n_fft = 2048
    win = np.hanning(n_fft).astype(np.float32)
    freqs = np.fft.rfftfreq(n_fft, 1 / sr)
    kick_bins = (freqs >= 35) & (freqs <= 150)
    edges = np.geomspace(60, 12000, 41)
    band_idx = [np.where((freqs >= edges[i]) & (freqs < edges[i + 1]))[0] for i in range(40)]
    pad = np.concatenate([np.zeros(n_fft, np.float32), x, np.zeros(n_fft, np.float32)])
    kick, spec = np.zeros(frames), np.zeros((frames, 40))
    for f in range(frames):
        c = int(f / FPS * sr) + n_fft
        mag = np.abs(np.fft.rfft(pad[c - n_fft // 2: c + n_fft // 2] * win))
        kick[f] = mag[kick_bins].mean()
        spec[f] = [mag[i].mean() if len(i) else 0 for i in band_idx]
    kick = np.clip((kick - np.percentile(kick, 20)) / (np.percentile(kick, 97) - np.percentile(kick, 20) + 1e-9), 0, 1)
    spec = 20 * np.log10(spec + 1e-6)
    spec = np.clip((spec - np.percentile(spec, 30)) / (np.percentile(spec, 99) - np.percentile(spec, 30) + 1e-9), 0, 1)
    # attaque rapide, relâche lente
    for f in range(1, frames):
        kick[f] = max(kick[f], kick[f - 1] * 0.82)
        spec[f] = np.maximum(spec[f], spec[f - 1] * 0.85)
    return kick, spec


# --- Dessin ----------------------------------------------------------------

def gradient(h, stops):
    t = np.linspace(0, 1, h)
    pos = [s[0] for s in stops]
    return np.stack([np.interp(t, pos, [s[1][c] for s in stops]) for c in range(3)], axis=1)


def chrome_fill(alpha):
    """Remplit un masque L avec le dégradé chrome (bornes verticales du masque)."""
    a = np.array(alpha)
    ys = np.where(a.max(axis=1) > 0)[0]
    rgb = np.zeros((*a.shape, 3), np.float32)
    if len(ys):
        rgb[ys[0]:ys[-1] + 1] = gradient(ys[-1] - ys[0] + 1, CHROME)[:, None, :]
    img = Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA")
    img.putalpha(alpha)
    return img


def background():
    top, bot = np.array(BG_TOP, np.float32), np.array(BG_BOTTOM, np.float32)
    t = np.linspace(0, 1, H)[:, None]
    arr = np.repeat((top + (bot - top) * t)[:, None, :], W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB")
    sw, sh = W // 4, H // 4
    smoke = Image.new("RGB", (sw, sh))
    d = ImageDraw.Draw(smoke)
    # fumée au sol : positions relatives, pour fonctionner en 9:16 comme en 16:9
    for fx, fy, fr, col in [(.22, .83, .33, (40, 8, 34)), (.78, .875, .37, (5, 34, 42)), (.5, .98, .44, (18, 20, 28))]:
        cx, cy, r = fx * sw, fy * sh, fr * min(sw, sh * 0.5625)
        d.ellipse([cx - r, cy - r * .6, cx + r, cy + r * .6], fill=col)
    smoke = smoke.filter(ImageFilter.GaussianBlur(28)).resize((W, H), Image.BILINEAR)
    return ImageChops.add(img, smoke)


def cubic(p0, p1, p2, p3, n=24):
    return [tuple((1 - t) ** 3 * np.array(p0) + 3 * (1 - t) ** 2 * t * np.array(p1)
                  + 3 * (1 - t) * t ** 2 * np.array(p2) + t ** 3 * np.array(p3))
            for t in np.linspace(0, 1, n)]


def mask_layers(width=500):
    """Masque chromé (RGBA) + calque des yeux + halo des yeux, à partir de site/mask.svg."""
    ss = 2
    k = width * ss / 200
    sw, sh = int(200 * k), int(240 * k)
    P = lambda pts: [(x * k, y * k) for x, y in pts]
    shield = (cubic((100, 8), (150, 8), (184, 40), (184, 100)) + cubic((184, 100), (184, 160), (150, 210), (100, 232))
              + cubic((100, 232), (50, 210), (16, 160), (16, 100)) + cubic((16, 100), (16, 40), (50, 8), (100, 8)))
    alpha = Image.new("L", (sw, sh))
    ImageDraw.Draw(alpha).polygon(P(shield), fill=255)
    face = chrome_fill(alpha)
    # reflet latéral
    sheen = np.abs(np.linspace(-1, 1, sw)) ** 1.6 * 115
    dark = Image.fromarray(np.repeat(sheen[None, :], sh, axis=0).astype(np.uint8), "L")
    face = Image.composite(Image.new("RGBA", (sw, sh), (0, 0, 0, 255)), face, ImageChops.multiply(dark, alpha))
    face.putalpha(alpha)
    marks = Image.new("RGBA", (sw, sh))
    d = ImageDraw.Draw(marks)
    d.line(P([(100, 18), (100, 222)]), fill=(11, 13, 20, 70), width=int(1.5 * k))
    for x, y, w in [(72, 164, 56), (78, 178, 44), (86, 192, 28)]:
        d.rounded_rectangle(P([(x, y), (x + w, y + 6)]), radius=3 * k, fill=(11, 13, 20, 255))
    face.alpha_composite(marks)
    eyes_pts = [[(38, 90), (90, 108), (86, 124), (44, 112)], [(162, 90), (110, 108), (114, 124), (156, 112)]]
    eyes = Image.new("RGBA", (sw, sh))
    de = ImageDraw.Draw(eyes)
    for e in eyes_pts:
        de.polygon(P(e), fill=CYAN + (255,))
    face.alpha_composite(eyes)
    size = (width, int(width * 1.2))
    face = face.resize(size, Image.LANCZOS)
    eyes = eyes.resize(size, Image.LANCZOS)
    glow = Image.new("RGBA", (size[0] + 200, size[1] + 200))
    glow.paste(eyes, (100, 100))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    glow = ImageChops.add(glow, glow)  # renforce le halo
    return face, eyes, glow


def fit_font(path, text, max_w, start):
    size = start
    while size > 20:
        f = ImageFont.truetype(str(path), size)
        if f.getbbox(text)[2] <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(str(path), size)


def text_layer(title, meta):
    layer = Image.new("RGBA", (W, H))
    # wordmark chromé
    disp = fit_font(FONTS / "Unbounded.ttf", "KASHING", min(880, W - 200), L["word_size"])
    bbox = disp.getbbox("KASHING")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    a = Image.new("L", (W, th + 40))
    ImageDraw.Draw(a).text(((W - tw) / 2 - bbox[0], 20 - bbox[1]), "KASHING", font=disp, fill=255)
    word = chrome_fill(a)
    shadow = Image.new("RGBA", word.size, (0, 0, 0, 0))
    shadow.putalpha(a.filter(ImageFilter.GaussianBlur(10)))
    layer.alpha_composite(shadow, (0, L["word_y"] + 16))
    layer.alpha_composite(word, (0, L["word_y"]))
    # titre + infos (zone sûre : au-dessus de la légende Instagram)
    mono = fit_font(FONTS / "JetBrainsMono.ttf", title.upper(), min(900, W - 180), L["title_size"])
    d = ImageDraw.Draw(layer)
    d.text((W / 2, L["title_y"]), title.upper(), font=mono, fill=CYAN + (255,), anchor="mm")
    small = ImageFont.truetype(str(FONTS / "JetBrainsMono.ttf"), L["meta_size"])
    d.text((W / 2, L["meta_y"]), meta, font=small, fill=(150, 156, 175, 255), anchor="mm")
    return layer


def laser_layer(t, energy):
    """Lasers depuis le haut, dessinés en basse résolution puis floutés pour le halo."""
    q = 4
    lw, lh = W // q, H // q
    glow = Image.new("RGB", (lw, lh))
    core = Image.new("RGB", (W, H))
    dg, dc = ImageDraw.Draw(glow), ImageDraw.Draw(core)
    level = 0.25 + 0.75 * energy
    for i in range(8):
        base = -56 + i * 16
        ang = math.radians(base + 16 * math.sin(2 * math.pi * t / (5 + i % 3) + i * 1.7))
        col = CYAN if i % 2 == 0 else MAGENTA
        c = tuple(int(v * level) for v in col)
        x0, y0 = W / 2, -60
        x1, y1 = x0 + math.sin(ang) * 2600, y0 + math.cos(ang) * 2600
        dc.line([(x0, y0), (x1, y1)], fill=c, width=3)
        dg.line([(x0 / q, y0 / q), (x1 / q, y1 / q)], fill=c, width=3)
    glow = glow.filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    return ImageChops.add(ImageChops.add(glow, glow), core)


def spectrum(d, bands):
    n, bw, gap = len(bands), 14, 8
    x0 = (W - n * (bw + gap) + gap) / 2
    cy = L["spec_cy"]
    for i, v in enumerate(bands):
        h = 6 + v * L["spec_h"]
        t = i / (n - 1)
        col = tuple(int(CYAN[c] + (MAGENTA[c] - CYAN[c]) * t) for c in range(3))
        x = x0 + i * (bw + gap)
        d.rounded_rectangle([x, cy - h, x + bw, cy + h], radius=4, fill=col + (230,))


# --- Rendu -----------------------------------------------------------------

def render(mp3, out, start, duration, title, meta, cover):
    x = decode(mp3)
    if duration is None:  # morceau entier
        start, duration = 0.0, len(x) / SR
    if start is None:
        start = find_drop(x, SR, duration)
    start = max(0.0, min(start, len(x) / SR - duration))
    seg = x[int(start * SR): int((start + duration) * SR)]
    frames = int(len(seg) / SR * FPS)
    kick, spec = features(seg, SR, frames)
    print(f"  segment {start:.1f}s → {start + duration:.1f}s, {frames} images")

    bg = background().convert("RGBA")
    face, eyes, eyes_glow = mask_layers(L["mask_w"])
    texts = text_layer(title, meta)
    mx, my = (W - face.width) // 2, L["mask_y"]

    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-i", str(mp3),
           "-map", "0:v", "-map", "1:a",
           "-af", f"afade=t=in:d=0.05,afade=t=out:st={max(0, duration - 1.2):.2f}:d=1.2",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    best_frame, best_kick = None, -1
    try:
        for f in range(frames):
            t, e = f / FPS, float(kick[f])
            frame = ImageChops.add(bg, laser_layer(t, e).convert("RGBA"))
            s = 1 + 0.035 * e
            m = face if s < 1.002 else face.resize((int(face.width * s), int(face.height * s)), Image.BILINEAR)
            frame.alpha_composite(m, (mx - (m.width - face.width) // 2, my - (m.height - face.height) // 2))
            g = eyes_glow.copy()
            g.putalpha(g.getchannel("A").point(lambda v, k=0.35 + 0.65 * e: int(v * k)))
            frame.alpha_composite(g, (mx - 100, my - 100))
            d = ImageDraw.Draw(frame)
            spectrum(d, spec[f])
            frame.alpha_composite(texts)
            rgb = frame.convert("RGB")
            # couverture : un kick fort, avant le flash
            if cover and e > best_kick and f > FPS:
                best_kick, best_frame = e, rgb
            if e > 0.9:
                rgb = Image.blend(rgb, Image.new("RGB", (W, H), (255, 255, 255)), (e - 0.9) * 0.6)
            proc.stdin.write(rgb.tobytes())
    finally:
        proc.stdin.close()
        proc.wait()
    if proc.returncode:
        sys.exit(f"ffmpeg a échoué ({proc.returncode})")
    if cover and best_frame is not None:
        if W > H:  # miniature YouTube : 1280x720, moins de 2 Mo
            best_frame = best_frame.resize((1280, 720), Image.LANCZOS)
        best_frame.save(out.with_suffix(".jpg"), quality=92)
    return start


def track_info(mp3):
    """Titre / BPM depuis site/audio/tracks.js si le fichier y est indexé."""
    js = ROOT / "site" / "audio" / "tracks.js"
    if js.exists():
        txt = js.read_text(encoding="utf-8")
        data = json.loads(txt[txt.index("["): txt.rindex("]") + 1])
        for t in data:
            for v in t.get("versions", [t]):
                if v["file"] == Path(mp3).name:
                    return t.get("title"), v.get("bpm")
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mp3", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--start", type=float, help="début en secondes (sinon : drop détecté)")
    ap.add_argument("--duration", type=float, help="durée en secondes (défaut : 20 s en reel, morceau entier en youtube)")
    ap.add_argument("--format", choices=LAYOUTS, default="reel",
                    help="reel = 1080x1920 (Instagram, Shorts) ; youtube = 1920x1080, morceau entier")
    ap.add_argument("--title")
    ap.add_argument("--handle", default="@kashingguudenoff")
    ap.add_argument("--cover", action="store_true", help="exporte aussi une couverture .jpg")
    a = ap.parse_args()
    global L, W, H, FPS
    L = LAYOUTS[a.format]
    W, H = L["size"]
    FPS = L["fps"]
    duration = a.duration if a.duration else (None if a.format == "youtube" else 20)

    title, bpm = track_info(a.mp3)
    title = a.title or title or a.mp3.stem
    meta = " · ".join(filter(None, [f"{bpm} BPM" if bpm else None, a.handle]))
    suffix = "" if a.format == "reel" else "_youtube"
    out = a.out or ROOT / "clips" / (a.mp3.stem + suffix + ".mp4")
    start = render(a.mp3, out, a.start, duration, title, meta, a.cover)
    print(f"  → {out}  (début {start:.1f}s)")


if __name__ == "__main__":
    main()
