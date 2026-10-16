#!/usr/bin/env python3
"""
Prépare le logo officiel pour le site :
  1. efface le texte de gabarit (« VISION / DISCIPLINE / RES… ») resté
     en bas à droite de l'original ;
  2. bascule la teinte aqua vers le framboise de la direction artistique ;
  3. découpe le disque en transparence pour qu'il se pose sur le sable ;
  4. exporte les tailles utiles plus les icônes.

Source : logo-officiel.png (original conservé, jamais modifié).
Usage  : python3 tools/build-logo.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "logo-officiel.png"
SORTIE = RACINE / "img"
SORTIE.mkdir(exist_ok=True)

# Teinte cible : framboise #A82E60 (~337° sur la roue, soit 239 sur 255)
TEINTE = 239
ESPRESSO = (30, 23, 17)


def effacer_gabarit(im: Image.Image) -> Image.Image:
    """Remplace le texte parasite par une estimation du fond local."""
    w, h = im.size
    boite = (int(w * 0.78), int(h * 0.74), int(w * 0.98), int(h * 0.88))
    zone = im.crop(boite)

    # Le texte est plus clair que l'aplat : on le repère par sa luminosité.
    gris = zone.convert("L")
    seuil = sorted(gris.getdata())[int(len(gris.getdata()) * 0.88)]
    masque = gris.point(lambda v: 255 if v > seuil else 0)
    masque = masque.filter(ImageFilter.MaxFilter(9))          # épaissit
    masque = masque.filter(ImageFilter.GaussianBlur(3))        # adoucit les bords

    # Le fond y est quasi uni : un filtre médian large efface les lettres.
    fond = zone.filter(ImageFilter.MedianFilter(size=9))
    for _ in range(4):
        fond = fond.filter(ImageFilter.MedianFilter(size=9))
    fond = fond.filter(ImageFilter.GaussianBlur(6))

    zone = Image.composite(fond, zone, masque)
    im = im.copy()
    im.paste(zone, boite)
    return im


def vers_framboise(im: Image.Image) -> Image.Image:
    """Garde le modelé (saturation, lumière) et ne change que la teinte."""
    hsv = im.convert("RGB").convert("HSV")
    t, s, v = hsv.split()
    t = t.point(lambda _: TEINTE)
    # Un peu plus de saturation : le framboise doit exister sur fond sable.
    s = s.point(lambda x: min(255, int(x * 1.3)))
    # Le lettrage et le disque partagent la même teinte : sans accentuation
    # du modelé, les lettres se noient dans le fond.
    v = v.point(lambda x: max(0, min(255, int(128 + (x - 128) * 1.55))))
    rgb = Image.merge("HSV", (t, s, v)).convert("RGB")
    return ImageEnhance.Color(rgb).enhance(1.15)


def disque(im: Image.Image) -> Image.Image:
    """Découpe le disque du logo, les angles noirs deviennent transparents."""
    c = min(im.size)
    masque = Image.new("L", (c * 4, c * 4), 0)
    ImageDraw.Draw(masque).ellipse((0, 0, c * 4 - 1, c * 4 - 1), fill=255)
    masque = masque.resize((c, c), Image.LANCZOS)
    sortie = im.convert("RGBA").resize((c, c), Image.LANCZOS)
    sortie.putalpha(masque)
    return sortie


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Original introuvable : {SOURCE}")

    brut = Image.open(SOURCE).convert("RGB")
    propre = effacer_gabarit(brut)
    colore = vers_framboise(propre)
    rond = disque(colore)

    for taille in (96, 192, 384):
        cible = SORTIE / f"logo-{taille}.png"
        rond.resize((taille, taille), Image.LANCZOS).save(cible, optimize=True)
        print(f"  {cible.name:<22} {cible.stat().st_size / 1024:6.1f} Ko")

    # Icônes : le disque posé sur l'espresso, sans transparence
    for taille, nom in ((180, "apple-touch-icon.png"), (512, "icon-512.png")):
        fond = Image.new("RGB", (taille, taille), ESPRESSO)
        marge = round(taille * 0.06)
        vignette = rond.resize((taille - 2 * marge, taille - 2 * marge), Image.LANCZOS)
        fond.paste(vignette, (marge, marge), vignette)
        cible = SORTIE / nom
        fond.save(cible, optimize=True)
        print(f"  {nom:<22} {cible.stat().st_size / 1024:6.1f} Ko")

    # Aperçu de partage : logo à gauche, pose à droite
    og = Image.new("RGB", (1200, 630), ESPRESSO)
    marque = rond.resize((330, 330), Image.LANCZOS)
    og.paste(marque, (120, 150), marque)
    pose = SORTIE / "galerie9-800.webp"
    if pose.exists():
        with Image.open(pose) as ph:
            ph = ph.convert("RGB")
            haut = 630
            large = round(ph.width * haut / ph.height)
            ph = ph.resize((large, haut), Image.LANCZOS)
            g = max(0, (large - 520) // 2)
            og.paste(ph.crop((g, 0, g + 520, 630)), (680, 0))
    cible = SORTIE / "og-image.jpg"
    og.save(cible, quality=82, optimize=True)
    print(f"  og-image.jpg           {cible.stat().st_size / 1024:6.1f} Ko")


if __name__ == "__main__":
    main()
