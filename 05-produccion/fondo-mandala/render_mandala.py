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
import argparse, pathlib, shutil, subprocess, tempfile
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
CHROMIUM = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--fps', type=int, default=24)
    p.add_argument('--salida', default=str(AQUI / 'mandala_bucle.mp4'))
    a = p.parse_args()
    tmp = pathlib.Path(tempfile.mkdtemp())
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        pag = nav.new_page(viewport={'width': 1920, 'height': 1080})
        pag.goto(f"file://{AQUI / 'mandala.html'}")
        largo = pag.evaluate('BUCLE')
        total = largo * a.fps
        lienzo = pag.query_selector('canvas')
        for i in range(total):              # el fotograma "total" sería el 0 otra vez
            pag.evaluate(f'pintar({i / a.fps})')
            lienzo.screenshot(path=str(tmp / f'f{i:05d}.png'))
            if i % (a.fps * 8) == 0:
                print(f'  {i}/{total}', flush=True)
        nav.close()
    subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-framerate', str(a.fps),
                    '-i', str(tmp / 'f%05d.png'), '-c:v', 'libx264', '-crf', '18',
                    '-preset', 'slow', '-pix_fmt', 'yuv420p', a.salida], check=True)
    shutil.rmtree(tmp)
    print(a.salida)


if __name__ == '__main__':
    main()
