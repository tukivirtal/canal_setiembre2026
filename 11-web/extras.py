#!/usr/bin/env python3
"""Piezas chicas de la web: miniaturas de las tarjetas, la imagen para compartir y los íconos.

Uso: python3 11-web/extras.py   (después de tarjetas.py)
"""
import pathlib
import tempfile

from playwright.sync_api import sync_playwright
from PIL import Image

from tarjetas import CHROMIUM
from vetas import textura

REPO = pathlib.Path(__file__).resolve().parents[1]
IMG = REPO / 'web' / 'img'

COMPARTIR = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<link rel="stylesheet" href="{fuentes}"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1200px;height:630px;background:#0b0c0f url({fondo}) center/cover;display:flex;align-items:center;justify-content:center}}
.panel{{width:1000px;height:470px;border-radius:30px;background:rgba(8,9,12,.72);border:1.5px solid rgba(230,196,106,.28);
        display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
.marca{{font-family:Cinzel,serif;font-size:26px;letter-spacing:.42em;padding-left:.42em;color:#e6c46a}}
h1{{font-family:'Cormorant Garamond',serif;font-weight:600;font-size:84px;line-height:1.02;color:#f6e7b8;margin-top:26px;text-wrap:balance;max-width:860px}}
p{{font-family:Cinzel,serif;font-weight:600;font-size:24px;letter-spacing:.3em;padding-left:.3em;color:#e6c46a;margin-top:30px}}
</style></head><body><div class="panel"><div class="marca">RIN</div>
<h1>¿Te acuestas y la cabeza no para?</h1><p>TRES NOCHES · GRATIS</p></div></body></html>"""


def main():
    for n in (1, 2, 3):
        im = Image.open(IMG / f'tarjeta-noche-{n}.jpg').convert('RGB')
        im.resize((360, 640), Image.LANCZOS).save(IMG / f'tarjeta-noche-{n}-chica.webp', quality=80, method=6)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        fondo = tmp / 'vetas.png'
        textura(1200, 630, 7).save(fondo)
        pagina = tmp / 'compartir.html'
        pagina.write_text(COMPARTIR.format(fuentes=(REPO / 'web/fuentes/fuentes.css').as_uri(),
                                           fondo=fondo.as_uri()), encoding='utf-8')
        icono = tmp / 'icono.html'
        icono.write_text('<html><body style="margin:0;background:#0b0c0f">'
                         f'<img src="{(REPO / "web/favicon.svg").as_uri()}" width="180" height="180"></body></html>')
        with sync_playwright() as pw:
            nav = pw.chromium.launch(executable_path=CHROMIUM)
            pag = nav.new_page(viewport={'width': 1200, 'height': 630})
            pag.goto(pagina.as_uri())
            pag.evaluate('document.fonts.ready')
            pag.wait_for_timeout(300)
            pag.screenshot(path=str(tmp / 'compartir.png'))
            Image.open(tmp / 'compartir.png').convert('RGB').save(IMG / 'compartir.jpg', quality=88, optimize=True)
            pag = nav.new_page(viewport={'width': 180, 'height': 180})
            pag.goto(icono.as_uri())
            pag.wait_for_timeout(200)
            pag.screenshot(path=str(IMG / 'icono-180.png'))
            nav.close()
    for f in sorted(IMG.iterdir()):
        print(f.name, f.stat().st_size)


if __name__ == '__main__':
    main()
