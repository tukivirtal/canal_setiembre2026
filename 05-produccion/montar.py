#!/usr/bin/env python3
"""
Línea de montaje: una obra del catálogo → todo lo que se sube a YouTube.

    python3 05-produccion/montar.py OBRA-009
    python3 05-produccion/montar.py --siguientes 3     # las 3 primeras sin montar

Por obra deja en produccion/<id>/:

    video.mp4        la obra con su ambiente y el mandala de su color, 1080p
    miniatura.jpg    1280x720
    metadatos.json   título y descripción en inglés, traducción al español,
                     etiquetas, categoría. Es lo que lee la subida (Make).

Los pasos, en orden, y cada uno se salta si ya está hecho (se puede cortar y
relanzar sin perder trabajo):

    1. componer la obra          compositor.py, con el comando exacto del catálogo
    2. la capa del ambiente      capas.py (pájaros, zen o ancestral), si lleva
    3. envolver en el ambiente   ambiente.py
    4. el bucle del mandala      render_mandala.py, uno por paleta y tono, se
                                 reutiliza; corre en paralelo con los pasos 1-3
    5. el video                  el bucle repetido debajo del audio, sin recodificar
    6. la miniatura              render_miniaturas.py

Lo que más tarda es el paso 1 (~28 min de CPU por hora de audio) y el 4 la primera
vez que se usa cada paleta (~25 min). Pensado para correr en Codespaces.

Los WAV intermedios se borran al terminar: una obra de 3 horas son ~2 GB de WAV y
se regeneran idénticos con la semilla.
"""
import argparse, csv, json, os, pathlib, shlex, shutil, subprocess, sys, wave

RAIZ = pathlib.Path(__file__).resolve().parents[1]
CATALOGO = RAIZ / '08-catalogo' / 'catalogo.csv'
PRODUCCION = RAIZ / 'produccion'
BUCLES = RAIZ / '05-produccion' / 'fondo-mandala' / 'bucles'


def correr(cmd, **kw):
    print('   $', ' '.join(str(c) for c in cmd)[:150], flush=True)
    subprocess.run([str(c) for c in cmd], check=True, cwd=RAIZ, **kw)


def args_de(comando, script):
    """Los argumentos de un comando del catálogo, tal cual, sin el python3 script."""
    partes = shlex.split(comando)
    return partes[partes.index(script) + 1:]


def duracion_wav(ruta):
    with wave.open(str(ruta), 'rb') as w:
        return w.getnframes() / w.getframerate()


def montar(o):
    d = PRODUCCION / o['id']
    d.mkdir(parents=True, exist_ok=True)
    video, mini = d / 'video.mp4', d / 'miniatura.jpg'
    print(f"\n{o['id']} · {o['titulo']}")

    obra, capa, final = d / 'obra.wav', d / 'capa.wav', d / 'final.wav'
    # El bucle del mandala: uno por paleta y tono (cada obra de un ambiente
    # tiene su color), y se reutiliza. Se renderiza EN PARALELO con la
    # composición: los dos tardan del orden de media hora y no compiten.
    paleta, tono = o['ambiente'], int(o.get('tono') or 0)
    bucle = BUCLES / (f'mandala-{paleta}.mp4' if not tono else f'mandala-{paleta}-t{tono}.mp4')
    render = None
    if not video.exists() and not bucle.exists():
        BUCLES.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, '05-produccion/fondo-mandala/render_mandala.py',
               '--paleta', paleta, '--tono', str(tono), '--salida', str(bucle)]
        print('   $ (en paralelo)', ' '.join(cmd)[:150], flush=True)
        render = subprocess.Popen(cmd, cwd=RAIZ)
    if not video.exists():
        if not final.exists():
            # 1 · componer
            if not obra.exists():
                correr([sys.executable, '03-composicion/compositor.py',
                        *args_de(o['comando_regeneracion'], '03-composicion/compositor.py'),
                        '--salida', obra])
            # 2 y 3 · capa y ambiente, con los parámetros del catálogo
            pasos = o['comando_ambiente'].split(' && ')
            for paso in pasos:
                if 'capas.py' in paso and not capa.exists():
                    a = args_de(paso, '03-composicion/capas.py')
                    a[2] = str(capa)                       # salida
                    correr([sys.executable, '03-composicion/capas.py', *a])
            a = args_de(pasos[-1], '03-composicion/ambiente.py')
            a[0], a[1] = str(obra), str(final)
            if '--capa' in a:
                a[a.index('--capa') + 1] = str(capa)
            correr([sys.executable, '03-composicion/ambiente.py', *a])

        # 4 · esperar el bucle del mandala
        if render and render.wait() != 0:
            sys.exit('falló el render del mandala')

        # 5 · el video. Con -t y no con -shortest: -shortest no corta cuando el
        # video es un bucle infinito copiado, y el 23/09 generó un archivo de 31 GB.
        dur = duracion_wav(final)
        if dur > 100 * 60:
            # Más de 100 minutos en H.264 pasaría los 2 GB que admite una Release
            # de GitHub (2 h ≈ 2 GB). El bucle se pasa a HEVC, ~40 % más liviano
            # con la misma imagen; YouTube lo acepta igual.
            hevc = bucle.with_name(bucle.stem + '-hevc.mp4')
            if not hevc.exists():
                correr(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-i', bucle,
                        '-c:v', 'libx265', '-crf', '27', '-preset', 'slow',
                        '-x265-params', 'keyint=1152:min-keyint=1152:log-level=error',
                        '-tag:v', 'hvc1', '-pix_fmt', 'yuv420p', hevc])
            bucle = hevc
        correr(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-stream_loop', '-1',
                '-i', bucle, '-i', final, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '256k', '-t', f'{dur:.3f}',
                '-movflags', '+faststart', video])
    elif render:
        render.wait()

    # 6 · la miniatura
    if not mini.exists():
        correr([sys.executable, '05-produccion/miniaturas/render_miniaturas.py', '--id', o['id']])
        shutil.copy(RAIZ / '05-produccion' / 'miniaturas' / 'export' / f"{o['id']}.jpg", mini)

    # los metadatos para la subida
    (d / 'metadatos.json').write_text(json.dumps({
        'id': o['id'],
        'title': o['titulo'], 'description': o['descripcion_optimizada'],
        'tags': [t.strip() for t in o['etiquetas'].split(',')],
        'category_id': '10',                       # Música
        'default_language': 'en',
        'localizations': {'es': {'title': o['titulo_es'], 'description': o['descripcion_es']}},
        'made_for_kids': False,
        'files': {'video': 'video.mp4', 'thumbnail': 'miniatura.jpg'},
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    for f in (obra, capa, final):                  # se regeneran con la semilla
        f.unlink(missing_ok=True)
    tam = video.stat().st_size / 2 ** 30
    print(f"   listo: {d.relative_to(RAIZ)}/  ·  video {tam:.2f} GB")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('id', nargs='?')
    p.add_argument('--siguientes', type=int, help='montar las N primeras que falten')
    a = p.parse_args()
    with open(CATALOGO, encoding='utf-8') as f:
        obras = list(csv.DictReader(f))
    if a.id:
        cola = [o for o in obras if o['id'] == a.id]
        if not cola:
            sys.exit(f'{a.id} no está en el catálogo')
    elif a.siguientes:
        cola = [o for o in obras if not (PRODUCCION / o['id'] / 'metadatos.json').exists()][:a.siguientes]
    else:
        sys.exit('Decí qué obra: montar.py OBRA-009, o montar.py --siguientes 3')
    for o in cola:
        montar(o)


if __name__ == '__main__':
    main()
