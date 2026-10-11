#!/usr/bin/env python3
"""Détoure l'emblème KASHING de assets/kashing_logo_source.jpg (fond noir) → assets/kashing_logo.png.

On garde les pixels d'origine (aucune retouche de texture) : le triangle est découpé par
ses trois sommets, les cornes qui dépassent du triangle sont ajoutées par seuil de luminosité.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "kashing_logo_source.jpg"
OUT = ROOT / "assets" / "kashing_logo.png"
TRI = [(1001, 14), (360, 1018), (1644, 1018)]       # sommets mesurés sur la source, avec le biseau
HORNS = [(770, 250, 880, 420), (1120, 250, 1230, 420)]  # zones où les cornes sortent du triangle


def main():
    src = Image.open(SRC).convert("RGB")
    w, h = src.size
    ss = 4
    tri = Image.new("L", (w * ss, h * ss))
    ImageDraw.Draw(tri).polygon([(x * ss, y * ss) for x, y in TRI], fill=255)
    tri = tri.resize((w, h), Image.LANCZOS)          # bord anticrénelé

    lum = np.asarray(src.convert("L")).astype(np.float32)
    horns = np.zeros((h, w), np.uint8)
    for x0, y0, x1, y1 in HORNS:
        zone = lum[y0:y1, x0:x1]
        horns[y0:y1, x0:x1] = np.clip((zone - 45) * 6, 0, 255).astype(np.uint8)  # rampe douce sur le bord
    horns = Image.fromarray(horns, "L").filter(ImageFilter.MedianFilter(5))

    alpha = ImageChops.lighter(tri, horns)
    out = src.convert("RGBA")
    out.putalpha(alpha)
    out = out.crop(alpha.getbbox())
    out.save(OUT)
    print(f"→ {OUT.relative_to(ROOT)} {out.size}")


if __name__ == "__main__":
    main()
