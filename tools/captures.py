#!/usr/bin/env python3
"""
Captures d'écran locales pour relire le rendu pendant le développement.

Usage : python3 tools/captures.py [page.html ...]
Sortie : /tmp/.../captures/<page>-<mobile|bureau>.png
"""
import http.server
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
SORTIE = Path("/tmp/claude-0/-home-claude/2702f910-8c66-52f5-85be-a67914141a47/scratchpad/captures")
SORTIE.mkdir(parents=True, exist_ok=True)

PAGES = sys.argv[1:] or ["index.html"]
FORMATS = {"mobile": (390, 844), "bureau": (1440, 900)}


class Silencieux(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(RACINE), **kw)

    def log_message(self, *a):
        pass


def main() -> None:
    with socketserver.TCPServer(("127.0.0.1", 0), Silencieux) as srv:
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()

        with sync_playwright() as p:
            nav = p.chromium.launch()
            for page_nom in PAGES:
                for nom, (w, h) in FORMATS.items():
                    ctx = nav.new_context(viewport={"width": w, "height": h})
                    pg = ctx.new_page()
                    erreurs = []
                    pg.on("pageerror", lambda e: erreurs.append(str(e)))
                    pg.goto(f"http://127.0.0.1:{port}/{page_nom}", wait_until="load")
                    pg.wait_for_timeout(2600)  # laisse finir polices et animation
                    cible = SORTIE / f"{Path(page_nom).stem}-{nom}.png"
                    pg.screenshot(path=str(cible), full_page=(nom == "bureau"))
                    print(f"  {cible}")
                    for e in erreurs:
                        print(f"    ERREUR JS : {e}")
                    ctx.close()
            nav.close()
        srv.shutdown()


if __name__ == "__main__":
    main()
