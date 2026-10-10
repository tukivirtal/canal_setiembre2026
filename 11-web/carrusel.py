#!/usr/bin/env python3
"""Carrusel de fotos de TikTok con el regalo: portada, las 3 tarjetas y el cierre (1080x1920).

La portada lleva la pregunta de la landing y las tarjetas en abanico; el cierre, cómo se usa
y dónde están las noches. Todo queda arriba de los 1430 px: en el modo foto, la descripción y
el nombre de la cuenta tapan la parte de abajo, y los botones el borde derecho.

Uso: python3 11-web/carrusel.py   → produccion/carrusel-regalo/1-portada.jpg … 5-cierre.jpg
"""
import pathlib
import shutil
import sys
import tempfile

from playwright.sync_api import sync_playwright
from PIL import Image

AQUI = pathlib.Path(__file__).resolve().parent
REPO = AQUI.parent
sys.path.insert(0, str(AQUI))
from vetas import textura  # noqa: E402

CHROMIUM = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

ESTILO = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<link rel="stylesheet" href="{fuentes}">
<style>
  :root{{--oro:#e6c46a;--crema:#f6e7b8;--texto:#efe6d0}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{width:1080px;height:1920px;background:#0b0c0f url({fondo}) center/cover;color:var(--texto);
        font-family:'Nunito Sans',sans-serif;position:relative}}
  .panel{{position:absolute;top:170px;left:65px;width:950px;height:1260px;padding:84px 86px 70px;border-radius:40px;
          background:rgba(8,9,12,.76);border:1.5px solid rgba(230,196,106,.28);
          box-shadow:0 30px 120px rgba(0,0,0,.55);display:flex;flex-direction:column;align-items:center;text-align:center}}
  .marca{{font-family:Cinzel,serif;font-size:30px;letter-spacing:.42em;color:var(--oro);padding-left:.42em;opacity:.9}}
  .ceja{{font-family:Cinzel,serif;font-weight:600;font-size:30px;letter-spacing:.32em;color:var(--oro);padding-left:.32em;margin-top:58px}}
  h1{{font-family:'Cormorant Garamond',serif;font-weight:600;font-size:96px;line-height:1.02;color:var(--crema);
      margin-top:28px;text-wrap:balance;font-variant-numeric:lining-nums}}
  .bajada{{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:500;font-size:54px;line-height:1.15;
           color:var(--texto);margin-top:30px;text-wrap:balance;font-variant-numeric:lining-nums}}
  .abanico{{position:relative;width:100%;height:440px;margin-top:46px}}
  .abanico img{{position:absolute;top:0;left:50%;width:220px;height:391px;margin-left:-110px;border-radius:18px;
                border:1.5px solid rgba(230,196,106,.4);box-shadow:0 20px 50px rgba(0,0,0,.7)}}
  .abanico img:nth-child(1){{transform:translateX(-170px) translateY(24px) rotate(-9deg)}}
  .abanico img:nth-child(2){{z-index:1}}
  .abanico img:nth-child(3){{transform:translateX(170px) translateY(24px) rotate(9deg)}}
  .desliza{{margin-top:auto;font-weight:700;font-size:36px;color:var(--oro);letter-spacing:.02em}}
  ol{{list-style:none;margin-top:44px;text-align:left;width:100%}}
  li{{display:flex;gap:30px;font-size:42px;line-height:1.36;margin-top:34px}}
  li b{{font-weight:700;color:var(--oro);min-width:28px}}
  .raya{{width:150px;height:1.5px;background:linear-gradient(90deg,transparent,var(--oro),transparent);margin:62px auto 54px}}
  .final{{font-family:'Cormorant Garamond',serif;font-weight:600;font-size:70px;line-height:1.08;color:var(--crema);
          text-wrap:balance;font-variant-numeric:lining-nums}}
  .chico{{margin-top:auto;font-size:30px;color:#b9b09f}}
</style></head><body><div class="panel">{contenido}</div></body></html>"""

PORTADA = """
  <div class="marca">RIN</div>
  <div class="ceja">TRES NOCHES · GRATIS</div>
  <h1>¿Te acuestas y la cabeza no para?</h1>
  <p class="bajada">Te regalo 3 noches para soltar el día.</p>
  <div class="abanico"><img src="{t1}"><img src="{t2}"><img src="{t3}"></div>
  <p class="desliza">Desliza para verlas →</p>"""

CIERRE = """
  <div class="marca">RIN</div>
  <div class="ceja">ASÍ SE USA</div>
  <ol>
    <li><b>1</b><span>Lees la tarjeta de la noche. Son 30&nbsp;segundos.</span></li>
    <li><b>2</b><span>Pones el sonido y bloqueas el celular. Sigue sonando con la pantalla apagada.</span></li>
    <li><b>3</b><span>Cada vez que suena, exhalas largo.</span></li>
  </ol>
  <div class="raya"></div>
  <p class="final">Las 3 noches, con su audio de 12 minutos, están gratis en el enlace de mi perfil.</p>
  <p class="chico">Sin voces y sin tener que saber meditar.</p>"""


def main():
    salida = REPO / 'produccion' / 'carrusel-regalo'
    salida.mkdir(parents=True, exist_ok=True)
    img = REPO / 'web' / 'img'
    tarjetas = [img / f'tarjeta-noche-{n}.jpg' for n in (1, 2, 3)]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        fondo = tmp / 'vetas.png'
        textura(1080, 1920, 7).save(fondo)
        paginas = {
            '1-portada': PORTADA.format(t1=tarjetas[0].as_uri(), t2=tarjetas[1].as_uri(), t3=tarjetas[2].as_uri()),
            '5-cierre': CIERRE,
        }
        with sync_playwright() as pw:
            nav = pw.chromium.launch(executable_path=CHROMIUM)
            pag = nav.new_page(viewport={'width': 1080, 'height': 1920})
            for nombre, contenido in paginas.items():
                pagina = tmp / f'{nombre}.html'
                pagina.write_text(ESTILO.format(fuentes=(REPO / 'web' / 'fuentes' / 'fuentes.css').as_uri(),
                                                fondo=fondo.as_uri(), contenido=contenido), encoding='utf-8')
                pag.goto(pagina.as_uri())
                pag.evaluate('document.fonts.ready')
                pag.wait_for_timeout(400)
                png = tmp / f'{nombre}.png'
                pag.screenshot(path=str(png))
                destino = salida / f'{nombre}.jpg'
                Image.open(png).convert('RGB').save(destino, quality=90, optimize=True, progressive=True)
                print(destino)
            nav.close()
    for n, t in enumerate(tarjetas, 2):
        destino = salida / f'{n}-noche-{n - 1}.jpg'
        shutil.copyfile(t, destino)
        print(destino)


if __name__ == '__main__':
    main()
