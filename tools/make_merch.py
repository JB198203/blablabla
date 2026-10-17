#!/usr/bin/env python3
"""Fichiers d'impression pour le merch KASHING (Fourthwall ou autre impression à la demande).

Tous les fichiers sont des PNG sur fond transparent, à 300 DPI, recadrés au plus près du motif :
on les place et on les met à l'échelle dans l'éditeur de produit de Fourthwall.

  python3 tools/make_merch.py          # écrit dans assets/merch/

Le logo vient de assets/kashing_logo.png (1289 px de large). À 300 DPI, il imprime net jusqu'à
11 cm de large. La version x2 sert pour une impression plus grande (jusqu'à environ 22 cm) :
elle est agrandie, donc un peu plus douce de près. Pour un grand dos, il faut un logo source
en plus haute définition.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_clip import gradient, CHROME  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "merch"
FONT = ROOT / "tools" / "fonts" / "Tourney-BlackItalic.ttf"
LOGO = ROOT / "assets" / "kashing_logo.png"
DPI = (300, 300)
WHITE, BLACK = (255, 255, 255), (12, 12, 14)


def trim(img, pad=0):
    box = img.getchannel("A").getbbox()
    img = img.crop(box)
    if pad:
        out = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad))
        out.alpha_composite(img, (pad, pad))
        img = out
    return img


def text_mask(text, width):
    """Masque du texte en Tourney Black Italic, mis à l'échelle pour faire `width` px de large."""
    size = 1000
    font = ImageFont.truetype(str(FONT), size)
    l, t, r, b = font.getbbox(text)
    m = Image.new("L", (r - l + 40, b - t + 40))
    ImageDraw.Draw(m).text((20 - l, 20 - t), text, font=font, fill=255)
    m = m.crop(m.getbbox())
    # fermeture morphologique : bouche les fines jointures entre contours de la police
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    return m.resize((width, round(m.height * width / m.width)), Image.LANCZOS)


def fill(mask, color):
    img = Image.new("RGBA", mask.size, color + (0,))
    img.putalpha(mask)
    return img


def chrome(mask):
    """Dégradé chrome du site, du haut au bas des lettres."""
    rgb = np.repeat(gradient(mask.height, CHROME)[:, None, :], mask.width, axis=1)
    img = Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA")
    img.putalpha(mask)
    return img


def stack(*layers, gap):
    """Empile des calques centrés verticalement."""
    w = max(l.width for l in layers)
    h = sum(l.height for l in layers) + gap * (len(layers) - 1)
    out = Image.new("RGBA", (w, h))
    y = 0
    for l in layers:
        out.alpha_composite(l, ((w - l.width) // 2, y))
        y += l.height + gap
    return out


def outline(img, px, color=WHITE):
    """Contour plein autour du motif (découpe de sticker)."""
    a = img.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    big = Image.new("L", (img.width + 4 * px, img.height + 4 * px))
    big.paste(a, (2 * px, 2 * px))
    big = big.filter(ImageFilter.MaxFilter(2 * px + 1)).filter(ImageFilter.GaussianBlur(1.5))
    out = fill(big, color)
    out.alpha_composite(img, (2 * px, 2 * px))
    return trim(out)


def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name, dpi=DPI, optimize=True)
    cm = img.width / 300 * 2.54
    print(f"  {name:34s} {img.width}x{img.height}  ({cm:.0f} cm de large à 300 DPI)")
    return img


def main():
    logo = trim(Image.open(LOGO).convert("RGBA"))
    logo2 = logo.resize((logo.width * 2, logo.height * 2), Image.LANCZOS)
    logo2 = logo2.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))

    save(logo, "logo_11cm.png")
    save(logo2, "logo_22cm.png")

    word = text_mask("KASHING", 3600)
    save(chrome(word), "kashing_chrome.png")
    save(fill(word, WHITE), "kashing_white.png")
    save(fill(word, BLACK), "kashing_black.png")

    ftd = [text_mask(t, 3000) for t in ("FEEL", "THE", "DROP")]
    # chaque ligne à la même largeur : effet bloc, lisible de loin
    save(stack(*[fill(m, WHITE) for m in ftd], gap=90), "feel_the_drop_white.png")
    save(stack(*[fill(m, BLACK) for m in ftd], gap=90), "feel_the_drop_black.png")

    # t-shirt foncé : logo + KASHING chromé dessous (devant)
    w_small = text_mask("KASHING", logo2.width + 400)
    save(stack(logo2, chrome(w_small), gap=120), "tee_front_logo_kashing.png")

    # sticker découpé : logo avec contour blanc
    save(outline(logo2, 36), "sticker_logo.png")

    preview()


def preview():
    """Planche d'aperçu : chaque motif sur tissu noir et sur tissu blanc."""
    items = [("tee_front_logo_kashing.png", BLACK), ("feel_the_drop_white.png", BLACK),
             ("kashing_chrome.png", BLACK), ("feel_the_drop_black.png", (240, 240, 236)),
             ("kashing_black.png", (240, 240, 236)), ("sticker_logo.png", (60, 64, 72))]
    cell = 600
    sheet = Image.new("RGB", (cell * 3, cell * 2), (30, 30, 34))
    label = ImageFont.truetype(str(ROOT / "tools" / "fonts" / "JetBrainsMono.ttf"), 18)
    for i, (name, bg) in enumerate(items):
        x, y = (i % 3) * cell, (i // 3) * cell
        tile = Image.new("RGBA", (cell - 20, cell - 20), bg + (255,))
        art = Image.open(OUT / name)
        art.thumbnail((cell - 120, cell - 140), Image.LANCZOS)
        tile.alpha_composite(art, ((tile.width - art.width) // 2, (tile.height - art.height) // 2 - 10))
        d = ImageDraw.Draw(tile)
        d.text((12, tile.height - 30), name, font=label, fill=(150, 150, 150) if bg != BLACK else (120, 120, 130))
        sheet.paste(tile.convert("RGB"), (x + 10, y + 10))
    sheet.save(OUT / "preview.jpg", quality=88)
    print("  preview.jpg")


if __name__ == "__main__":
    main()
