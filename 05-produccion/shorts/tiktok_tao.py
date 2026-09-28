#!/usr/bin/env python3
"""
Videos verticales solo para TikTok: un audio, el mandala vertical de su color,
un gancho en el primer segundo y unos pocos textos que entran y salen.

    python3 05-produccion/shorts/tiktok_tao.py                 # «Two minutes of stillness»
    python3 05-produccion/shorts/tiktok_tao.py --pieza pensar   # «Stop overthinking» (OBRA-041)
    python3 05-produccion/shorts/tiktok_tao.py --pieza nervios  # «Calm your nervous system», 3 min de OBRA-042

tao: guqin, xiao y lluvia (03-composicion/tao.py) sobre el mandala jade, con dos
líneas del Tao Te Ching (traducción propia; el original es de dominio público).
pensar: 75 s de OBRA-041, pájaros y campanas del templo.

Deja en produccion/tiktok-<pieza>/: <pieza>-tiktok.mp4 (bajo 30 MB) y textos.txt.
"""
import argparse, pathlib, subprocess, sys, tempfile, urllib.parse, os
from playwright.sync_api import sync_playwright
from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parents[2]
AQUI = pathlib.Path(__file__).resolve().parent
_CH = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
CHROMIUM = os.environ.get('CHROMIUM') or (_CH if os.path.exists(_CH) else None)
BUCLES = RAIZ / '05-produccion/fondo-mandala/bucles'

# (desde, hasta, parámetros del texto)
TEXTOS_TAO = [
    (0.0, 7.0, {'tipo': 'gancho', 'titulo': 'Two minutes of stillness',
                'sub': 'Headphones on. Let the strings breathe for you.'}),
    (9.0, 30.0, {'titulo': 'Breathe out when the strings play',
                 'sub': 'The music slows your breath, little by little.'}),
    (34.0, 56.0, {'titulo': 'The highest good is like water.', 'fuente': 'TAO TE CHING · 8'}),
    (60.0, 82.0, {'titulo': 'It nourishes all things and does not compete.', 'fuente': 'TAO TE CHING · 8'}),
    (86.0, 106.0, {'titulo': 'Muddy water, left still, slowly clears.', 'fuente': 'TAO TE CHING · 15'}),
    (109.0, 120.0, {'tipo': 'fin', 'titulo': 'Full pieces on YouTube',
                    'sub': 'Rin · original music, composed from scratch. Guqin, xiao and rain, tuned to 432 Hz.'}),
]

TEXTO_TAO = """Two minutes of stillness 🌙 Guqin, xiao flute and soft rain.
Headphones on. Breathe out when the strings play.
"The highest good is like water." Tao Te Ching
Composed from scratch by Rin, no samples. Tuned to 432 Hz.
Full pieces on YouTube, link in bio.

#taoism #guqin #meditationmusic #zenmusic #calm"""

TEXTOS_PENSAR = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Stop overthinking',
                'sub': 'Birdsong, temple bells and a slower breath.'}),
    (8.0, 26.0, {'titulo': 'Breathe out longer than you breathe in',
                 'sub': 'The music slows down with you.'}),
    (30.0, 50.0, {'titulo': "You don't have to solve it tonight."}),
    (53.0, 66.0, {'titulo': 'Just listen. The birds are not in a hurry.'}),
    (67.5, 75.0, {'tipo': 'fin', 'titulo': 'The full hour is on YouTube',
                  'sub': 'Rin · original music, composed from scratch. 432 Hz.'}),
]
TEXTO_PENSAR = """Stop overthinking 🌿 Birdsong, soft temple bells and a slower breath.
Breathe out longer than you breathe in, and let the music lead.
You don't have to solve it tonight. Just listen.
Original music composed from scratch by Rin, no samples. Tuned to 432 Hz.
The full hour is on YouTube, link in bio.

#stopoverthinking #anxietyrelief #nervoussystem #birdsong #432hz"""

TEXTOS_NERVIOS = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Calm your nervous system',
                'sub': '3 minutes. Zen temple bells and a slower breath.'}),
    (8.0, 40.0, {'titulo': 'Breathe out longer than you breathe in',
                 'sub': 'The music slows down. Let your body follow.'}),
    (48.0, 82.0, {'titulo': 'Unclench your jaw. Drop your shoulders.'}),
    (92.0, 126.0, {'titulo': 'Nothing to fix right now. Just this breath.'}),
    (136.0, 168.0, {'titulo': 'Stay a little longer.', 'sub': 'Your breath already slowed down.'}),
    (171.0, 180.0, {'tipo': 'fin', 'titulo': 'The full 3 hours are on YouTube',
                    'sub': 'Rin · original music, composed from scratch. 528 Hz.'}),
]
TEXTO_NERVIOS = """Calm your nervous system 🌿 3 minutes of zen temple bells and a slower breath.
Breathe out longer than you breathe in. Unclench your jaw, drop your shoulders.
Nothing to fix right now. Just this breath.
Original music composed from scratch by Rin, no samples. Tuned to 528 Hz.
The full 3 hours are on YouTube, link in bio.

#calmyournervoussystem #nervoussystemregulation #anxietyrelief #zenmusic #528hz"""

PIEZAS = {
    'tao': dict(bucle='vertical-zen-t165.mp4', audio='tiktok-tao/tao-master.wav', T=120,
                textos=TEXTOS_TAO, texto=TEXTO_TAO, out='tiktok-tao', nombre='tao-tiktok.mp4'),
    'pensar': dict(bucle='vertical-jardin.mp4', audio='tiktok-pensar/pensar-master.wav', T=75,
                   textos=TEXTOS_PENSAR, texto=TEXTO_PENSAR, out='tiktok-pensar', nombre='pensar-tiktok.mp4'),
    # 3 min: con 1600 kbps pasaría los 30 MB; 1100 alcanza para un mandala lento
    'nervios': dict(bucle='vertical-zen-t35.mp4', audio='tiktok-nervios/nervios-master.wav', T=180,
                    textos=TEXTOS_NERVIOS, texto=TEXTO_NERVIOS, out='tiktok-nervios',
                    nombre='nervios-tiktok.mp4', kbps=1100),
}


def pngs(tmp, TEXTOS, T):
    rutas = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        pag = nav.new_page(viewport={'width': 1080, 'height': 1920})
        for k, (a, b, q) in enumerate(TEXTOS + [(0, T, {'marca': '1'})]):
            q = dict(q)
            if 'titulo' in q: q['marca'] = '0'
            pag.goto(f"file://{AQUI / 'texto_tiktok.html'}?{urllib.parse.urlencode(q)}")
            pag.wait_for_timeout(400)
            r = tmp / f't{k}.png'
            pag.screenshot(path=str(r), omit_background=True)
            rutas.append(r)
        nav.close()
    # un velo oscuro y ovalado detrás del texto, para que se lea sobre el dorado
    import numpy as np
    y, x = np.mgrid[0:1920, 0:1080]
    d = np.sqrt(((x - 540) / 620) ** 2 + ((y - 520) / 330) ** 2)
    alfa = (0.72 * np.clip(1.25 - d, 0, 1) ** 1.2 * 255).astype('uint8')
    v = np.zeros((1920, 1080, 4), 'uint8'); v[..., 3] = alfa
    Image.fromarray(v, 'RGBA').save(tmp / 'velo.png')
    return rutas, tmp / 'velo.png'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pieza', choices=list(PIEZAS), default='tao')
    P = PIEZAS[ap.parse_args().pieza]
    TEXTOS, T = P['textos'], P['T']
    OUT = RAIZ / 'produccion' / P['out']
    BUCLE, audio = BUCLES / P['bucle'], RAIZ / 'produccion' / P['audio']
    if not BUCLE.exists() or not audio.exists():
        sys.exit(f'Faltan {BUCLE} o {audio}')
    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t)
        rutas, velo = pngs(tmp, TEXTOS, T)
        args = ['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-stream_loop', '-1', '-i', str(BUCLE),
                '-i', str(audio), '-loop', '1', '-framerate', '24', '-t', str(T), '-i', str(velo)]
        for r in rutas:
            args += ['-loop', '1', '-framerate', '24', '-t', str(T), '-i', str(r)]
        f = ['[0:v]fps=24,format=yuv420p[m0]', '[m0][2:v]overlay=0:0[m1]']
        cur = 'm1'
        for k, (a, b, q) in enumerate(TEXTOS):
            ent = 0.0 if a == 0 else 0.8
            fx = f"[{k + 3}:v]format=rgba" + (f",fade=t=in:st={a}:d={ent}:alpha=1" if ent else '') + \
                 f",fade=t=out:st={b - 1.2}:d=1.2:alpha=1[x{k}]"
            f.append(fx)
            f.append(f"[{cur}][x{k}]overlay=0:0:enable='between(t,{a},{b})'[m{k + 2}]")
            cur = f'm{k + 2}'
        marca = len(TEXTOS) + 3
        # la marca «Rin» queda fija, salvo cuando el texto final ya la nombra
        f.append(f"[{cur}][{marca}:v]overlay=0:0:enable='lt(t,{TEXTOS[-1][0]})'[v]")
        salida = OUT / P['nombre']
        comun = ['-filter_complex', ';'.join(f), '-map', '[v]', '-map', '1:a', '-t', str(T),
                 '-c:v', 'libx264', '-preset', 'medium', '-b:v', f"{P.get('kbps', 1600)}k", '-pix_fmt', 'yuv420p']
        log = str(tmp / 'x264')
        subprocess.run(args + comun + ['-pass', '1', '-passlogfile', log, '-an', '-f', 'null', '-'], check=True)
        subprocess.run(args + comun + ['-pass', '2', '-passlogfile', log, '-c:a', 'aac', '-b:a', '192k',
                                       '-ar', '48000', '-movflags', '+faststart', str(salida)], check=True)
    (OUT / 'textos.txt').write_text(P['texto'] + '\n', encoding='utf-8')
    print(f'{salida}  {salida.stat().st_size / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
