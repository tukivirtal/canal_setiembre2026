#!/usr/bin/env python3
"""
Un Short a partir de una obra ya montada: el mandala vertical de su paleta, un
recorte de su audio y el rótulo con la frecuencia y la intención.

    python3 05-produccion/shorts/hacer_short.py OBRA-012
    python3 05-produccion/shorts/hacer_short.py OBRA-012 --inicio 300 --n 2

Necesita produccion/<id>/video.mp4 (lo deja montar.py): el audio sale de ahí,
así no hace falta volver a componer. Deja en produccion/<id>/:

    short-<n>.mp4          1080x1920, 45 s, listo para subir
    short-<n>.json         título, descripción y etiquetas del Short

El mandala vertical se renderiza una vez por paleta (~30 min) y se reutiliza.
"""
import argparse, csv, json, pathlib, subprocess, sys, tempfile, urllib.parse
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parents[2]
AQUI = pathlib.Path(__file__).resolve().parent
BUCLES = RAIZ / '05-produccion' / 'fondo-mandala' / 'bucles'
CHROMIUM = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

FRASE = {   # lo que promete el Short, en una línea
    'Dormir': 'to fall asleep',
    'Ansiedad': "for when your mind won't stop",
    'Meditar': 'for a quiet meditation',
    'Soltar': 'to let go of the day',
    'Concentración': 'for deep focus',
}
ETIQ = {
    'Dormir': ['sleep music', 'deep sleep'],
    'Ansiedad': ['anxiety relief', 'calming music'],
    'Meditar': ['meditation music', 'mindfulness'],
    'Soltar': ['stress relief', 'relaxing music'],
    'Concentración': ['focus music', 'study music'],
}


def duracion_txt(minutos):
    m = int(minutos)
    return f'{m // 60} h' if m >= 60 and m % 60 == 0 else f'{m} min'


def rotulo(o, destino):
    q = urllib.parse.urlencode({'hz': o['raiz_hz'], 'frase': FRASE[o['tema']],
                                'pie': f"Full piece · {duracion_txt(o['duracion_min'])} · on the channel"})
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        pag = nav.new_page(viewport={'width': 1080, 'height': 1920})
        pag.goto(f"file://{AQUI / 'rotulo.html'}?{q}")
        pag.wait_for_timeout(300)                    # fuentes
        pag.screenshot(path=str(destino), omit_background=True)
        nav.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('id')
    p.add_argument('--inicio', type=float, default=None,
                   help='segundo del video largo donde empieza el recorte (por defecto, el 40 %%)')
    p.add_argument('--duracion', type=float, default=45)
    p.add_argument('--n', type=int, default=1, help='número del Short de esta obra')
    a = p.parse_args()

    with open(RAIZ / '08-catalogo' / 'catalogo.csv', encoding='utf-8') as f:
        o = next((x for x in csv.DictReader(f) if x['id'] == a.id), None)
    if not o:
        sys.exit(f'{a.id} no está en el catálogo')
    d = RAIZ / 'produccion' / a.id
    largo = d / 'video.mp4'
    if not largo.exists():
        sys.exit(f'Falta {largo}: primero montar.py {a.id}')

    bucle = BUCLES / f"vertical-{o['ambiente']}.mp4"
    if not bucle.exists():
        subprocess.run([sys.executable, str(RAIZ / '05-produccion/fondo-mandala/render_mandala.py'),
                        '--vertical', '--paleta', o['ambiente'], '--crf', '24',
                        '--salida', str(bucle)], check=True)

    total = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                  '-of', 'csv=p=0', str(largo)], capture_output=True, text=True).stdout)
    inicio = a.inicio if a.inicio is not None else round(total * 0.4)
    T = a.duracion
    salida = d / f'short-{a.n}.mp4'
    with tempfile.TemporaryDirectory() as tmp:
        png = pathlib.Path(tmp) / 'rotulo.png'
        rotulo(o, png)
        # El Short se oye en el teléfono, más fuerte que la obra (-22 LUFS):
        # -18, con fundidos para que no arranque ni corte en seco.
        subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y',
                        '-stream_loop', '-1', '-i', str(bucle), '-i', str(png),
                        '-ss', str(inicio), '-t', str(T), '-i', str(largo),
                        '-filter_complex',
                        f'[0:v][1:v]overlay=0:0,fade=t=in:d=0.6,fade=t=out:st={T - 1.5}:d=1.5[v];'
                        f'[2:a]afade=t=in:d=1.5,afade=t=out:st={T - 3}:d=3,'
                        f'loudnorm=I=-18:TP=-2:LRA=7[a]',
                        '-map', '[v]', '-map', '[a]', '-t', str(T),
                        '-c:v', 'libx264', '-crf', '23', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                        '-movflags', '+faststart', str(salida)], check=True)

    amb = o['titulo'].split(' · ')[1]
    (d / f'short-{a.n}.json').write_text(json.dumps({
        'title': f"{o['raiz_hz']} Hz {FRASE[o['tema']]} · {amb}",
        'description': (f"{o['raiz_hz']} Hz · {amb.lower()} · original composition.\n"
                        f"Full piece ({duracion_txt(o['duracion_min'])}): {o['titulo']}\n\n"
                        f"{o['hashtags']} #shorts"),
        'tags': ETIQ[o['tema']] + [f"{o['raiz_hz']} hz", amb.lower(), 'Rin'],
        'related_video': o['url_video'],
        'inicio_en_la_obra': inicio,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{salida.relative_to(RAIZ)}  ·  {salida.stat().st_size / 2**20:.1f} MB  ·  desde {inicio:.0f} s')


if __name__ == '__main__':
    main()
