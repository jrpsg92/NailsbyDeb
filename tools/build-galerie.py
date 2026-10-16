#!/usr/bin/env python3
"""
Génère le HTML de la galerie à partir de galerie.json.

Le balisage est écrit en dur dans les pages (entre les marqueurs), et non
chargé en JavaScript : les photos restent visibles sans JS et indexables.
Les filtres sont un confort ajouté par-dessus.

Usage : python3 tools/build-galerie.py
"""
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MANIFESTE = json.loads((RACINE / "galerie.json").read_text(encoding="utf-8"))

POSES = MANIFESTE["poses"]
CATEGORIES = MANIFESTE["categories"]

# Nombre de poses mises en avant sur l'accueil
APERCU = 8


def vignette(pose: dict, tailles: str, differee: bool = True) -> str:
    f = pose["fichier"]
    petite = RACINE / "img" / f"{f}-480.webp"
    grande = RACINE / "img" / f"{f}-800.webp"
    if not petite.exists():
        raise SystemExit(
            f"Image manquante pour {f}. Lancer d'abord : python3 tools/build-images.py"
        )
    jeu = f"img/{f}-480.webp 480w"
    if grande.exists():
        jeu += f", img/{f}-800.webp 800w"
    chargement = ' loading="lazy"' if differee else ""
    return (
        f'        <figure class="piece" data-piece data-cat="{pose["cat"]}">\n'
        f'          <img src="img/{f}-480.webp" srcset="{jeu}"\n'
        f'               sizes="{tailles}" alt="{pose["alt"]}"{chargement}>\n'
        f"        </figure>"
    )


def filtres() -> str:
    puces = ['        <button class="puce" data-filtre="tout" aria-pressed="true">Tout</button>']
    for c in CATEGORIES:
        if not any(p["cat"] == c["cle"] for p in POSES):
            continue  # pas de filtre vide
        puces.append(
            f'        <button class="puce" data-filtre="{c["cle"]}" '
            f'aria-pressed="false">{c["nom"]}</button>'
        )
    return (
        '      <div class="filtres" data-filtres role="group" '
        'aria-label="Filtrer les réalisations">\n'
        + "\n".join(puces)
        + "\n      </div>"
    )


def remplacer(chemin: Path, balise: str, contenu: str) -> None:
    texte = chemin.read_text(encoding="utf-8")
    motif = re.compile(
        rf"(<!-- {balise}:debut -->).*?(<!-- {balise}:fin -->)", re.S
    )
    if not motif.search(texte):
        raise SystemExit(f"Marqueurs « {balise} » introuvables dans {chemin.name}")
    chemin.write_text(
        motif.sub(lambda m: f"{m.group(1)}\n{contenu}\n      {m.group(2)}", texte),
        encoding="utf-8",
    )
    print(f"  {chemin.name} : bloc « {balise} » régénéré")


def main() -> None:
    tailles_galerie = (
        "(min-width: 75rem) 23vw, (min-width: 48rem) 31vw, 47vw"
    )
    grille = "\n".join(vignette(p, tailles_galerie) for p in POSES)
    remplacer(
        RACINE / "realisations.html",
        "galerie",
        filtres() + '\n\n      <div class="galerie galerie--dense" data-grille>\n'
        + grille
        + "\n      </div>",
    )

    apercu = "\n".join(
        vignette(p, "(min-width: 48rem) 23vw, 47vw", differee=(i > 1))
        for i, p in enumerate(POSES[:APERCU])
    )
    remplacer(
        RACINE / "index.html",
        "apercu",
        '      <div class="galerie galerie--dense">\n' + apercu + "\n      </div>",
    )

    print(f"\n{len(POSES)} poses au total, {APERCU} en aperçu sur l'accueil.")


if __name__ == "__main__":
    main()
