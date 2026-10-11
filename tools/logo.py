#!/usr/bin/env python3
"""Emblème KASHING dessiné en code : triangle d'acier, disque doré à cornes, fente, dents.

Les dents servent d'égaliseur (5 niveaux 0–1) et la fente s'allume sur le kick,
pour animer la marque sur la musique. Espace de dessin : 600 x 560, mis à l'échelle.

  python3 tools/logo.py                      # exporte site/logo.png (1024 px, fond transparent)
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
CYAN = (34, 232, 255)
STEEL = [(0, (236, 238, 242)), (.35, (168, 172, 180)), (.5, (110, 114, 122)), (.62, (196, 200, 206)), (1, (128, 132, 140))]
GOLD = [(0, (250, 226, 150)), (.3, (204, 160, 62)), (.5, (122, 84, 22)), (.7, (226, 186, 90)), (1, (140, 98, 32))]
DARK = (14, 12, 8, 255)

CX, CY, R = 300, 330, 150          # disque
TRI = [(300, 16), (590, 532), (10, 532)]
GROOVE = [(300, 96), (520, 494), (80, 494)]
SCREWS = [(300, 62), (58, 508), (542, 508)]
# colonnes des dents (x relatifs au centre) ; les bords sont rognés par le cercle
TEETH = [(-128, -100), (-88, -36), (-24, 24), (36, 88), (100, 128)]
TEETH_BOTTOM = 480
SLOT = (-92, -40, 92, -24)          # fente (x0, y0, x1, y1) relative au centre


def smile_y(x):
    """Ligne du sourire : haute sur les bords, basse au milieu."""
    return CY + 4 + 34 * (1 - (x / 130) ** 2)


def _gradient(w, h, stops, angle=0.6):
    """Dégradé linéaire en diagonale + grain « brossé » horizontal."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (xx * math.cos(angle) + yy * math.sin(angle))
    t = (t - t.min()) / (t.max() - t.min() + 1e-6)
    pos = [s[0] for s in stops]
    rgb = np.stack([np.interp(t, pos, [s[1][c] for s in stops]) for c in range(3)], axis=-1)
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 1, (h, w)).astype(np.float32)
    k = max(3, w // 60)
    noise = np.apply_along_axis(lambda r: np.convolve(r, np.ones(k) / k, "same"), 1, noise)
    rgb += noise[..., None] * 14
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def _horn(side, s):
    """Corne courbe posée sur l'anneau, côté -1 (gauche) ou 1 (droite)."""
    pts = []
    a0, a1 = math.radians(-90 + side * 30), math.radians(-90 + side * 46)
    base = [(CX + R * math.cos(a), CY + R * math.sin(a)) for a in (a0, a1)]
    tip = (CX + side * 128, CY - R - 34)
    ctrl = (CX + side * 134, CY - R + 10)
    for t in np.linspace(0, 1, 16):  # bord extérieur : base[1] → pointe
        pts.append(((1 - t) ** 2 * base[1][0] + 2 * (1 - t) * t * ctrl[0] + t ** 2 * tip[0],
                    (1 - t) ** 2 * base[1][1] + 2 * (1 - t) * t * ctrl[1] + t ** 2 * tip[1]))
    inner = (CX + side * 108, CY - R + 6)
    for t in np.linspace(0, 1, 12):  # bord intérieur : pointe → base[0]
        pts.append(((1 - t) ** 2 * tip[0] + 2 * (1 - t) * t * inner[0] + t ** 2 * base[0][0],
                    (1 - t) ** 2 * tip[1] + 2 * (1 - t) * t * inner[1] + t ** 2 * base[0][1]))
    return [(x * s, y * s) for x, y in pts]


class Logo:
    """Pré-calcule les couches fixes ; render() ne redessine que les dents et la lueur."""

    def __init__(self, width=600):
        self.ss = 2
        self.s = width * self.ss / 600
        self.w, self.h = int(600 * self.s), int(560 * self.s)
        s = self.s
        P = lambda pts: [(x * s, y * s) for x, y in pts]
        C = lambda cx, cy, r: [(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s]
        steel, gold = _gradient(self.w, self.h, STEEL), _gradient(self.w, self.h, GOLD, angle=1.1)
        base = Image.new("RGBA", (self.w, self.h))

        m = Image.new("L", base.size)
        ImageDraw.Draw(m).polygon(P(TRI), fill=255)
        base.paste(steel, (0, 0), m)
        d = ImageDraw.Draw(base)
        d.line(P(GROOVE + GROOVE[:1]), fill=(40, 42, 46, 255), width=int(9 * s), joint="curve")
        d.line(P([(x + 2, y + 3) for x, y in GROOVE + GROOVE[:1]]), fill=(230, 232, 236, 160), width=int(2 * s))
        for x, y in SCREWS:
            d.ellipse(C(x, y, 11), fill=(120, 124, 130, 255), outline=(50, 52, 56, 255), width=int(2 * s))
            d.line(P([(x - 7, y - 4), (x + 7, y + 4)]), fill=(40, 42, 46, 255), width=int(2.5 * s))

        # cornes + anneau + plaque du visage (or), avec une gorge sombre entre anneau et visage
        m = Image.new("L", base.size)
        dm = ImageDraw.Draw(m)
        dm.ellipse(C(CX, CY, R), fill=255)
        dm.polygon(_horn(-1, s), fill=255)
        dm.polygon(_horn(1, s), fill=255)
        shadow = m.filter(ImageFilter.GaussianBlur(10 * s))
        base.paste((0, 0, 0, 140), (int(6 * s), int(10 * s)), shadow)
        base.paste(gold, (0, 0), m)
        d.ellipse(C(CX, CY, 134), fill=DARK)
        face = Image.new("L", base.size)
        ImageDraw.Draw(face).ellipse(C(CX, CY, 126), fill=255)
        self.face_mask = face
        self.gold = gold
        self.base = base
        self.P, self.C = P, C

    def render(self, levels=(1, 1, 1, 1, 1), glow=0.0, size=None):
        """levels : hauteur des 5 dents (0–1) ; glow : lueur cyan de la fente (0–1)."""
        s, P = self.s, self.P
        img = self.base.copy()
        face = self.gold.copy()
        df = ImageDraw.Draw(face)
        xs = np.linspace(-140, 140, 57)
        smile = [(CX + x, smile_y(x)) for x in xs]
        # tout ce qui est sous le sourire est sombre, puis on y pose les dents
        df.polygon(P(smile + [(CX + 140, TEETH_BOTTOM + 20), (CX - 140, TEETH_BOTTOM + 20)]), fill=DARK)
        for (x0, x1), v in zip(TEETH, levels):
            k = 0.5 + 0.5 * max(0.0, min(1.0, v))  # les dents ne descendent jamais sous la moitié
            top = [(CX + x, TEETH_BOTTOM - (TEETH_BOTTOM - smile_y(x) - 13) * k) for x in np.linspace(x0, x1, 8)]
            df.polygon(P(top + [(CX + x1, TEETH_BOTTOM + 20), (CX + x0, TEETH_BOTTOM + 20)]), fill=(0, 0, 0, 0))
        teeth = face.getchannel("A").point(lambda a: 255 - a)
        face.putalpha(255)
        face.paste(self.gold, (0, 0), teeth)
        x0, y0, x1, y1 = SLOT
        df = ImageDraw.Draw(face)
        df.rounded_rectangle(P([(CX + x0, CY + y0), (CX + x1, CY + y1)]), radius=8 * s, fill=DARK)
        img.paste(face, (0, 0), self.face_mask)
        # lueur de la fente
        if glow > 0.01:
            g = Image.new("RGBA", img.size)
            x0, y0, x1, y1 = SLOT
            ImageDraw.Draw(g).rounded_rectangle(P([(CX + x0 + 3, CY + y0 + 3), (CX + x1 - 3, CY + y1 - 3)]),
                                                radius=8 * s, fill=CYAN + (int(255 * glow),))
            halo = g.filter(ImageFilter.GaussianBlur(14 * s))
            img = Image.alpha_composite(img, ImageChops.add(halo, halo))
            img = Image.alpha_composite(img, g)
        out = img.resize((img.width // self.ss, img.height // self.ss), Image.LANCZOS)
        if size:
            out = out.resize(size, Image.LANCZOS)
        return out


if __name__ == "__main__":
    logo = Logo(1024)
    logo.render().save(ROOT / "site" / "logo.png")
    print("→ site/logo.png")
