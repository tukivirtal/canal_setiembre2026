#!/usr/bin/env python3
"""
Banner, foto de perfil y marca de agua del canal, listos para subir.

    python3 09-canal/render_identidad.py

Salida en 09-canal/export/:
  banner-2560x1440.png   · perfil-800x800.png   · marca-agua-150x150.png
  vista-dispositivos.png  (cómo recorta YouTube el banner en TV, escritorio y móvil)
"""
import pathlib
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

AQUI = pathlib.Path(__file__).resolve().parent
SALIDA = AQUI / 'export'
CHROMIUM = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'


def main():
    SALIDA.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        pag = nav.new_page(viewport={'width': 2600, 'height': 1500})
        pag.goto(f"file://{AQUI / 'identidad.html'}")
        pag.wait_for_timeout(1500)
        pag.query_selector('#banner').screenshot(path=str(SALIDA / 'banner-2560x1440.png'))
        pag.query_selector('#perfil').screenshot(path=str(SALIDA / 'perfil-800x800.png'))
        pag.query_selector('#agua').screenshot(path=str(SALIDA / 'marca-agua-150x150.png'),
                                              omit_background=True)
        nav.close()
    vista_dispositivos()
    for f in sorted(SALIDA.iterdir()):
        print(f'{f.name:28} {f.stat().st_size // 1024} KB')


def vista_dispositivos():
    """Los tres recortes que hace YouTube del mismo banner, lado a lado."""
    b = Image.open(SALIDA / 'banner-2560x1440.png').convert('RGB')
    W, H = b.size
    recortes = {'TV (todo)': (0, 0, W, H),
                'Escritorio': (0, (H - 423) // 2, W, (H + 423) // 2),
                'Móvil (zona segura)': ((W - 1546) // 2, (H - 423) // 2, (W + 1546) // 2, (H + 423) // 2)}
    ancho = 1200
    piezas = []
    for nombre, caja in recortes.items():
        im = b.crop(caja)
        im = im.resize((ancho, int(im.height * ancho / im.width)))
        piezas.append((nombre, im))
    alto = sum(im.height + 60 for _, im in piezas)
    lienzo = Image.new('RGB', (ancho, alto), (30, 30, 30))
    d = ImageDraw.Draw(lienzo); y = 0
    for nombre, im in piezas:
        d.text((10, y + 18), nombre, fill=(230, 230, 230))
        lienzo.paste(im, (0, y + 50)); y += im.height + 60
    lienzo.save(SALIDA / 'vista-dispositivos.png')


if __name__ == '__main__':
    main()
