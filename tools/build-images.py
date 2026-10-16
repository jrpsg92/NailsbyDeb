#!/usr/bin/env python3
"""
Génère les images optimisées du site à partir des originaux.

Les originaux (galerieN.jpg, deborah.jpg) restent intacts à la racine :
ce script ne fait que produire des dérivés dans img/.

Usage :  python3 tools/build-images.py
Ajouter une photo : la déposer à la racine sous galerie6.jpg, puis relancer.
"""
from pathlib import Path
from PIL import Image, ImageOps

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "img"
SORTIE.mkdir(exist_ok=True)

# Largeurs générées pour le jeu responsive (srcset)
LARGEURS_GALERIE = [480, 800, 1200]
LARGEUR_PORTRAIT = [600, 1000]


def exporter(src: Path, base: str, largeurs: list[int], qualite: int = 78) -> None:
    """Écrit base-<w>.webp pour chaque largeur, sans jamais agrandir l'original."""
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        for w in largeurs:
            if w > im.width:
                continue
            h = round(im.height * w / im.width)
            cible = SORTIE / f"{base}-{w}.webp"
            im.resize((w, h), Image.LANCZOS).save(
                cible, "WEBP", quality=qualite, method=6
            )
            print(f"  {cible.name:<24} {cible.stat().st_size / 1024:6.0f} Ko")


def main() -> None:
    total_avant = 0
    print("Galerie :")
    for src in sorted(RACINE.glob("galerie*.jpg")):
        total_avant += src.stat().st_size
        exporter(src, src.stem, LARGEURS_GALERIE)

    portrait = RACINE / "deborah.jpg"
    if portrait.exists():
        print("Portrait :")
        total_avant += portrait.stat().st_size
        exporter(portrait, "deborah", LARGEUR_PORTRAIT)

    total_apres = sum(f.stat().st_size for f in SORTIE.glob("*.webp"))
    print(
        f"\nOriginaux : {total_avant / 1024:.0f} Ko"
        f"  ->  dérivés : {total_apres / 1024:.0f} Ko"
    )


if __name__ == "__main__":
    main()
