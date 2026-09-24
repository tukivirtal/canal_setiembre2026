#!/usr/bin/env python3
"""
Los 5 Shorts de una obra ya montada, según la hoja de Shorts del catálogo
(08-catalogo/shorts.csv): el mandala vertical de su paleta, un tramo de su
audio y el rótulo con la frecuencia y la frase.

    python3 05-produccion/shorts/hacer_short.py OBRA-012          # los 5
    python3 05-produccion/shorts/hacer_short.py OBRA-012 --n 3    # solo el 3

Necesita produccion/<id>/video.mp4 (lo deja montar.py): el audio sale de ahí,
así no hace falta volver a componer. Deja en produccion/<id>/:

    short-<n>.mp4     1080x1920, 45 s, listo para YouTube Shorts y TikTok
    short-<n>-web.mp4 la misma, bajo 5 MB: la que sube Make a YouTube
    short-<n>.json    la fila de la hoja: títulos, descripciones, etiquetas

Cada Short cambia de tramo (inicio_s), encuadre (zoom), instante del bucle
(desfase_s) y frase: ver 08-catalogo/shorts_catalogo.py.

El mandala vertical se renderiza una vez por paleta (~10 min) y se reutiliza.
"""
import argparse, csv, json, pathlib, subprocess, sys, tempfile, urllib.parse
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parents[2]
AQUI = pathlib.Path(__file__).resolve().parent
BUCLES = RAIZ / '05-produccion' / 'fondo-mandala' / 'bucles'
CHROMIUM = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'


def duracion_txt(minutos):
    m = int(minutos)
    return f'{m // 60} h' if m >= 60 and m % 60 == 0 else f'{m} min'


def rotulo(o, frase, destino):
    q = urllib.parse.urlencode({'hz': o['raiz_hz'], 'frase': frase,
                                'pie': f"Full piece · {duracion_txt(o['duracion_min'])} · on the channel"})
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        pag = nav.new_page(viewport={'width': 1080, 'height': 1920})
        pag.goto(f"file://{AQUI / 'rotulo.html'}?{q}")
        pag.wait_for_timeout(300)                    # fuentes
        pag.screenshot(path=str(destino), omit_background=True)
        nav.close()


LIMITE_WEB = 4_900_000    # bytes. Make (plan Free) no mueve archivos de más de 5 MB


def ligero(mp4):
    """short-<n>-web.mp4: la versión que sube Make. HEVC en dos pasadas para
    quedar bajo 5 MB con la misma imagen (comparada a ojo con la de 17 MB)."""
    web = mp4.with_name(mp4.stem + '-web.mp4')
    for kbps in (720, 640, 560):
        with tempfile.TemporaryDirectory() as tmp:
            log = str(pathlib.Path(tmp) / 'x265')
            base = ['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-i', str(mp4),
                    '-c:v', 'libx265', '-b:v', f'{kbps}k', '-preset', 'slow']
            subprocess.run(base + ['-x265-params', f'pass=1:stats={log}:log-level=error',
                                   '-an', '-f', 'null', '-'], check=True)
            subprocess.run(base + ['-x265-params', f'pass=2:stats={log}:log-level=error',
                                   '-tag:v', 'hvc1', '-pix_fmt', 'yuv420p',
                                   '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart',
                                   str(web)], check=True)
        if web.stat().st_size <= LIMITE_WEB:
            return web
    sys.exit(f'{web} no baja de {LIMITE_WEB} bytes')


def hacer(o, s, largo, bucle, d):
    T = 45
    z = float(s['zoom'])
    salida = d / s['archivo']
    with tempfile.TemporaryDirectory() as tmp:
        png = pathlib.Path(tmp) / 'rotulo.png'
        rotulo(o, s['frase_en_pantalla'], png)
        # El encuadre: se agranda el mandala vertical y se recorta al centro.
        # El Short se oye en el teléfono, más fuerte que la obra (-22 LUFS):
        # -18, con fundidos para que no arranque ni corte en seco.
        subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y',
                        '-stream_loop', '-1', '-ss', s['desfase_s'], '-i', str(bucle),
                        '-i', str(png),
                        '-ss', s['inicio_s'], '-t', str(T), '-i', str(largo),
                        '-filter_complex',
                        f'[0:v]scale=trunc(iw*{z}/2)*2:trunc(ih*{z}/2)*2:flags=lanczos,crop=1080:1920[m];'
                        f'[m][1:v]overlay=0:0,fade=t=in:d=0.6,fade=t=out:st={T - 1.5}:d=1.5[v];'
                        f'[2:a]afade=t=in:d=1.5,afade=t=out:st={T - 3}:d=3,'
                        f'loudnorm=I=-18:TP=-2:LRA=7[a]',
                        '-map', '[v]', '-map', '[a]', '-t', str(T),
                        '-c:v', 'libx264', '-crf', '23', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                        '-movflags', '+faststart', str(salida)], check=True)
    web = ligero(salida)
    (d / s['archivo'].replace('.mp4', '.json')).write_text(
        json.dumps(s, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"{salida.relative_to(RAIZ)}  ·  {salida.stat().st_size / 2**20:.1f} MB "
          f"(web {web.stat().st_size / 1e6:.2f} MB)  ·  "
          f"desde {s['inicio_s']} s  ·  zoom {z}  ·  {s['frase_en_pantalla']}", flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('id')
    p.add_argument('--n', type=int, help='solo este Short (1-5); por defecto, los cinco')
    a = p.parse_args()

    with open(RAIZ / '08-catalogo' / 'catalogo.csv', encoding='utf-8') as f:
        o = next((x for x in csv.DictReader(f) if x['id'] == a.id), None)
    if not o:
        sys.exit(f'{a.id} no está en el catálogo')
    with open(RAIZ / '08-catalogo' / 'shorts.csv', encoding='utf-8') as f:
        cola = [s for s in csv.DictReader(f) if s['obra'] == a.id and (not a.n or int(s['n']) == a.n)]
    d = RAIZ / 'produccion' / a.id
    largo = d / 'video.mp4'
    if not largo.exists():
        sys.exit(f'Falta {largo}: primero montar.py {a.id}')

    bucle = BUCLES / f"vertical-{o['ambiente']}.mp4"
    if not bucle.exists():
        subprocess.run([sys.executable, str(RAIZ / '05-produccion/fondo-mandala/render_mandala.py'),
                        '--vertical', '--paleta', o['ambiente'], '--crf', '24',
                        '--salida', str(bucle)], check=True)
    for s in cola:
        hacer(o, s, largo, bucle, d)


if __name__ == '__main__':
    main()
