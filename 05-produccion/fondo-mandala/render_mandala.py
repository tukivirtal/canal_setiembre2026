#!/usr/bin/env python3
"""
Renderiza el bucle del mandala a video, fotograma por fotograma.

    python3 05-produccion/fondo-mandala/render_mandala.py            # 1920x1080, 24 fps
    python3 05-produccion/fondo-mandala/render_mandala.py --fps 12   # prueba rápida

Sale mandala_bucle.mp4, de 48 s, que empalma consigo mismo. Para una obra:

    ffmpeg -stream_loop -1 -i mandala_bucle.mp4 -i obra.wav \\
      -c:v copy -c:a aac -b:a 320k -shortest video.mp4

El video no se recodifica al repetirse: una obra de 3 horas se monta en segundos.
"""
import argparse, pathlib, shutil, subprocess, tempfile, os
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
# El Chromium de la sesión de Claude; en GitHub Actions no existe y se usa el
# que instala Playwright (executable_path=None).
_CH = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
CHROMIUM = os.environ.get('CHROMIUM') or (_CH if os.path.exists(_CH) else None)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--fps', type=int, default=24)
    p.add_argument('--salida', default=str(AQUI / 'mandala_bucle.mp4'))
    p.add_argument('--paleta', default='mar',
                   help='mar, mar-aves, zen, selva o lluvia-tambor: una por ambiente')
    p.add_argument('--segundos', type=float, default=None,
                   help='solo los primeros N segundos: para previsualizar sin renderizar el bucle entero')
    p.add_argument('--tono', type=int, default=0,
                   help='giro de matiz en grados: cada obra de un mismo ambiente con su color')
    p.add_argument('--vertical', action='store_true',
                   help='1080x1920 para Shorts, sin firma y con el mandala más chico, entero en el ancho')
    p.add_argument('--crf', type=int, default=28,
                   help='calidad x264. Con 28 una obra de 3 h pesa unos 2,5 GB; con 24, unos 4,5')
    a = p.parse_args()
    tmp = pathlib.Path(tempfile.mkdtemp())
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        ancho, alto = (1080, 1920) if a.vertical else (1920, 1080)
        extra = f'&w={ancho}&h={alto}&r=0.34&firma=0' if a.vertical else ''
        pag = nav.new_page(viewport={'width': ancho, 'height': alto})
        pag.goto(f"file://{AQUI / 'mandala.html'}?paleta={a.paleta}&tono={a.tono}{extra}")
        largo = pag.evaluate('BUCLE')
        total = int((a.segundos or largo) * a.fps)
        lienzo = pag.query_selector('canvas')
        for i in range(total):              # el fotograma "total" sería el 0 otra vez
            pag.evaluate(f'pintar({i / a.fps})')
            lienzo.screenshot(path=str(tmp / f'f{i:05d}.png'))
            if i % (a.fps * 8) == 0:
                print(f'  {i}/{total}', flush=True)
        nav.close()
    subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-framerate', str(a.fps),
                    '-i', str(tmp / 'f%05d.png'), '-c:v', 'libx264', '-crf', str(a.crf),
                    '-preset', 'slow', '-tune', 'animation', '-pix_fmt', 'yuv420p', a.salida], check=True)
    shutil.rmtree(tmp)
    print(a.salida)


if __name__ == '__main__':
    main()
