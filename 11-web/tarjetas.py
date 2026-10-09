#!/usr/bin/env python3
"""Tarjetas de las noches (1080x1920): la pregunta, tres pasos y la frase de un antiguo.

Se leen antes de poner el sonido; la persona las guarda en el celular. El fondo es la
textura de vetas.py y las tipografías son las de la web (web/fuentes).

Uso: python3 11-web/tarjetas.py            (todas)
     python3 11-web/tarjetas.py --noche 2  (una)
"""
import argparse
import html
import pathlib
import sys
import tempfile

from playwright.sync_api import sync_playwright
from PIL import Image

AQUI = pathlib.Path(__file__).resolve().parent
REPO = AQUI.parent
sys.path.insert(0, str(AQUI))
from vetas import textura  # noqa: E402

CHROMIUM = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

NOCHES = {
    1: dict(titulo='Dejar el trabajo en la puerta',
            pregunta='¿Te acostaste y la cabeza sigue en el trabajo?',
            pasos=['Antes de acostarte, di en voz baja: «Por hoy, terminé».',
                   'Pon el sonido y bloquea el celular.',
                   'Cada vez que suene, exhala largo y afloja algo: la frente, la mandíbula, los hombros, las manos.'],
            frase='En ningún lugar puede uno retirarse con más calma que en su propia alma.',
            fuente='Marco Aurelio · Meditaciones IV, 3'),
    2: dict(titulo='La lista de la almohada',
            pregunta='¿Ya estás pensando en todo lo de mañana?',
            pasos=['Antes de acostarte, escribe en un papel lo que tienes que hacer mañana. Bien concreto: «llamar a…», «pagar…».',
                   'Deja el papel lejos de la cama. Lo que está escrito ya no tiene que estar en tu cabeza.',
                   'Pon el sonido, bloquea el celular y cuenta las exhalaciones. Si pierdes la cuenta, vuelve a uno.'],
            frase='Que el futuro no te perturbe: llegarás a él, si hace falta, con la misma razón que hoy usas para el presente.',
            fuente='Marco Aurelio · Meditaciones VII, 8'),
    3: dict(titulo='Cuando la cabeza da vueltas',
            pregunta='¿Te acuestas y la cabeza no para?',
            pasos=['No intentes dejar la mente en blanco. Cuando llegue un pensamiento, solo nótalo: «estoy pensando».',
                   'Pon el sonido y deja el celular boca abajo.',
                   'Con cada sonido, suelta ese pensamiento en la exhalación. Si vuelve, lo sueltas otra vez.'],
            frase='Sufrimos más a menudo en la imaginación que en la realidad.',
            fuente='Séneca · Cartas a Lucilio, 13'),
}

PLANTILLA = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<link rel="stylesheet" href="{fuentes}">
<style>
  :root{{--oro:#e6c46a;--crema:#f6e7b8;--texto:#efe6d0}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{width:1080px;height:1920px;background:#0b0c0f url({fondo}) center/cover;color:var(--texto);
        font-family:'Nunito Sans',sans-serif;display:flex;align-items:center;justify-content:center}}
  .panel{{width:950px;min-height:1640px;padding:92px 86px 80px;border-radius:40px;
          background:rgba(8,9,12,.74);border:1.5px solid rgba(230,196,106,.28);
          box-shadow:0 30px 120px rgba(0,0,0,.55);display:flex;flex-direction:column;align-items:center;text-align:center}}
  .marca{{font-family:Cinzel,serif;font-size:30px;letter-spacing:.42em;color:var(--oro);padding-left:.42em;opacity:.9}}
  .noche{{font-family:Cinzel,serif;font-weight:600;font-size:30px;letter-spacing:.32em;color:var(--oro);padding-left:.32em;margin-top:70px}}
  h1{{font-family:'Cormorant Garamond',serif;font-weight:600;font-size:88px;line-height:1.02;color:var(--crema);margin-top:26px;text-wrap:balance}}
  .pregunta{{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:500;font-size:50px;line-height:1.15;color:var(--texto);opacity:.9;margin-top:34px;text-wrap:balance}}
  .raya{{width:150px;height:1.5px;background:linear-gradient(90deg,transparent,var(--oro),transparent);margin:58px auto 52px;position:relative}}
  .esta{{font-family:Cinzel,serif;font-size:27px;letter-spacing:.34em;color:var(--oro);padding-left:.34em}}
  ol{{list-style:none;margin-top:34px;text-align:left;width:100%}}
  li{{display:flex;gap:30px;font-size:39px;line-height:1.38;margin-top:30px}}
  li b{{font-weight:700;font-size:40px;line-height:1.38;color:var(--oro);min-width:28px}}
  .frase{{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:500;font-size:46px;line-height:1.2;color:var(--crema);margin-top:auto;padding-top:56px;text-wrap:balance}}
  .fuente{{font-family:Cinzel,serif;font-size:23px;letter-spacing:.26em;color:var(--oro);margin-top:24px;padding-left:.26em}}
</style></head><body><div class="panel">
  <div class="marca">RIN</div>
  <div class="noche">NOCHE {nombre}</div>
  <h1>{titulo}</h1>
  <p class="pregunta">{pregunta}</p>
  <div class="raya"></div>
  <div class="esta">ESTA NOCHE</div>
  <ol>{pasos}</ol>
  <p class="frase">«{frase}»</p>
  <p class="fuente">{fuente}</p>
</div></body></html>"""


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--noche', type=int, choices=sorted(NOCHES))
    a.add_argument('--salida', default=str(REPO / 'web' / 'img'))
    x = a.parse_args()
    salida = pathlib.Path(x.salida)
    salida.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        fondo = tmp / 'vetas.png'
        textura(1080, 1920, 7).save(fondo)
        with sync_playwright() as pw:
            nav = pw.chromium.launch(executable_path=CHROMIUM)
            pag = nav.new_page(viewport={'width': 1080, 'height': 1920})
            for n in ([x.noche] if x.noche else sorted(NOCHES)):
                d = NOCHES[n]
                pasos = ''.join(f'<li><b>{i}</b><span>{html.escape(p)}</span></li>'
                                for i, p in enumerate(d['pasos'], 1))
                pagina = tmp / f'noche-{n}.html'
                pagina.write_text(PLANTILLA.format(
                    fuentes=(REPO / 'web' / 'fuentes' / 'fuentes.css').as_uri(), fondo=fondo.as_uri(),
                    nombre=('UNO', 'DOS', 'TRES')[n - 1] if n <= 3 else n,
                    titulo=html.escape(d['titulo']), pregunta=html.escape(d['pregunta']), pasos=pasos,
                    frase=html.escape(d['frase']), fuente=html.escape(d['fuente'].upper())), encoding='utf-8')
                pag.goto(pagina.as_uri())
                pag.evaluate('document.fonts.ready')
                pag.wait_for_timeout(300)
                png = tmp / f'noche-{n}.png'
                pag.screenshot(path=str(png))
                destino = salida / f'tarjeta-noche-{n}.jpg'
                Image.open(png).convert('RGB').save(destino, quality=88, optimize=True, progressive=True)
                print(destino)
            nav.close()


if __name__ == '__main__':
    main()
