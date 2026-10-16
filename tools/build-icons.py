#!/usr/bin/env python3
"""
Génère les icônes PNG (apple-touch-icon, og-image) à partir de la même
géométrie que img/logo-mark.svg, sans dépendre d'un convertisseur SVG.

Usage : python3 tools/build-icons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "img"
SORTIE.mkdir(exist_ok=True)

ENCRE = (30, 23, 17)        # espresso
GEL_CLAIR = (250, 229, 236)  # nude rosé
GEL_MOYEN = (226, 141, 175)  # rose gel
GEL_SOMBRE = (148, 40, 84)   # framboise profond

SUR = 4  # suréchantillonnage pour des bords nets


def bezier(p0, p1, p2, p3, pas=60):
    """Échantillonne une cubique de Bézier."""
    pts = []
    for i in range(pas + 1):
        t = i / pas
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def forme_ongle(echelle, dx=0.0, dy=0.0):
    """Contour de l'ongle amande, repris du viewBox 64x64 du SVG."""
    def p(x, y):
        return (x * echelle + dx, y * echelle + dy)

    # Silhouette ballerine : bord libre plat en haut, galbe qui s'élargit,
    # cuticule arrondie en bas.
    contour = [p(26, 6.5), p(38, 6.5)]
    contour += bezier(p(38, 6.5), p(41, 14), p(43.5, 22), p(44.5, 30))[1:]
    contour += bezier(p(44.5, 30), p(46.5, 44), p(41.5, 56.5), p(32, 56.5))[1:]
    contour += bezier(p(32, 56.5), p(22.5, 56.5), p(17.5, 44), p(19.5, 30))[1:]
    contour += bezier(p(19.5, 30), p(20.5, 22), p(23, 14), p(26, 6.5))[1:]
    return contour


def degrade_gel(taille):
    """Dégradé diagonal clair -> moyen -> sombre."""
    grad = Image.new("RGB", (taille, taille))
    px = grad.load()
    for y in range(taille):
        for x in range(taille):
            # diagonale resserrée sur la zone réellement occupée par l'ongle
            t = min(max(((x * 0.4 + y * 0.6) / taille - 0.18) / 0.62, 0.0), 1.0)
            if t < 0.38:
                k = t / 0.38
                a, b = GEL_CLAIR, GEL_MOYEN
            else:
                k = (t - 0.38) / 0.62
                a, b = GEL_MOYEN, GEL_SOMBRE
            px[x, y] = tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))
    return grad


def icone(taille, fond=ENCRE, marge=0.16):
    grand = taille * SUR
    toile = Image.new("RGB", (grand, grand), fond)

    cote = grand * (1 - 2 * marge)
    echelle = cote / 64
    decalage = grand * marge

    masque = Image.new("L", (grand, grand), 0)
    ImageDraw.Draw(masque).polygon(
        forme_ongle(echelle, decalage, decalage), fill=255
    )
    toile.paste(degrade_gel(grand), (0, 0), masque)

    # reflet du gel, borné à la silhouette pour qu'il ne bave pas au-dehors
    reflet = Image.new("L", (grand, grand), 0)
    d = ImageDraw.Draw(reflet)
    pts = [
        (27.6, 9.5), (24.6, 17.5), (23.0, 26.5), (23.4, 38.0),
        (23.6, 44.0), (21.0, 44.6), (20.5, 38.2), (20.2, 26.0),
        (21.6, 16.5), (24.6, 8.5),
    ]
    d.polygon(
        [(x * echelle + decalage, y * echelle + decalage) for x, y in pts], fill=225
    )
    reflet = reflet.filter(ImageFilter.GaussianBlur(grand * 0.010))
    reflet = Image.composite(reflet, Image.new("L", (grand, grand), 0), masque)
    toile.paste(Image.new("RGB", (grand, grand), (255, 255, 255)), (0, 0), reflet)

    # strass
    sparkle = Image.new("L", (grand, grand), 0)
    ds = ImageDraw.Draw(sparkle)
    cx, cy, r = 37.5, 24.0, 5.4
    ds.polygon(
        [
            (cx * echelle + decalage, (cy - r) * echelle + decalage),
            ((cx + r * 0.42) * echelle + decalage, cy * echelle + decalage),
            (cx * echelle + decalage, (cy + r) * echelle + decalage),
            ((cx - r * 0.42) * echelle + decalage, cy * echelle + decalage),
        ],
        fill=255,
    )
    ds.polygon(
        [
            ((cx - r) * echelle + decalage, cy * echelle + decalage),
            (cx * echelle + decalage, (cy - r * 0.42) * echelle + decalage),
            ((cx + r) * echelle + decalage, cy * echelle + decalage),
            (cx * echelle + decalage, (cy + r * 0.42) * echelle + decalage),
        ],
        fill=255,
    )
    toile.paste(Image.new("RGB", (grand, grand), (255, 255, 255)), (0, 0), sparkle)

    return toile.resize((taille, taille), Image.LANCZOS)


def main() -> None:
    for taille, nom in [(180, "apple-touch-icon.png"), (512, "icon-512.png")]:
        chemin = SORTIE / nom
        icone(taille).save(chemin, optimize=True)
        print(f"  {nom:<24} {chemin.stat().st_size / 1024:5.0f} Ko")

    # Aperçu de partage (Instagram, WhatsApp) : 1200x630
    og = Image.new("RGB", (1200, 630), ENCRE)
    marque = icone(300, marge=0.04)
    og.paste(marque, (120, 165))
    photo_src = SORTIE / "galerie1-800.webp"
    if photo_src.exists():
        with Image.open(photo_src) as ph:
            ph = ph.convert("RGB")
            h = 630
            w = round(ph.width * h / ph.height)
            ph = ph.resize((w, h), Image.LANCZOS)
            gauche = max(0, (w - 520) // 2)
            og.paste(ph.crop((gauche, 0, gauche + 520, 630)), (680, 0))
    chemin = SORTIE / "og-image.jpg"
    og.save(chemin, quality=82, optimize=True)
    print(f"  og-image.jpg             {chemin.stat().st_size / 1024:5.0f} Ko")


if __name__ == "__main__":
    main()
