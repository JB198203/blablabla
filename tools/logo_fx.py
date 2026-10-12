#!/usr/bin/env python3
"""Logo KASHING animé, partagé par les Reels, les clips YouTube et l'animation du logo.

Le logo est l'image d'origine détourée (assets/kashing_logo.png, voir tools/cutout_logo.py) :
aucune retouche, jamais agrandie au-delà de sa taille native. Il rebondit sur le kick
(saut, grossissement, bascule au tempo) et un scanner rouge façon K2000 balaie la fente.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "assets" / "kashing_logo.png"
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


class LogoFX:
    """Prépare le logo à une largeur d'affichage donnée et rend une image par frame."""

    def __init__(self, width, scanner=True):
        src = Image.open(LOGO).convert("RGBA")
        self.width = min(width, src.width)
        self.height = int(src.height * self.width / src.width)
        # maître un peu plus grand que l'affichage (marge pour le rebond), jamais plus grand que la source
        mw = min(src.width, int(self.width * 1.1))
        self.master = src.resize((mw, int(src.height * mw / src.width)), Image.LANCZOS)
        self.scanner = Scanner(self.master.size, mw / src.width) if scanner else None

    def render(self, t, bpm, kick, punch, scale=1.0, bounce=1.0):
        """Renvoie (image RGBA, saut vers le haut en px). kick et punch entre 0 et 1."""
        img = self.master
        if self.scanner is not None:
            img = Image.alpha_composite(img, self.scanner.render(t * bpm / 60, kick))
        sc = scale * (1 + 0.08 * punch * bounce) * self.width / self.master.width
        img = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BICUBIC)
        # bascule gauche / droite : un aller-retour toutes les 2 temps, amplitude selon le kick
        tilt = 4 * punch * bounce * np.sin(np.pi * t * bpm / 60)
        img = img.rotate(tilt, resample=Image.BICUBIC, expand=True)
        return img, int(self.height * 0.07 * punch * bounce)
