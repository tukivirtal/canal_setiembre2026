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


# La invitación a suscribirse, en los videos para dormir: entre el 0:45 y el
# 2:30, mientras todavía miran la pantalla (al final del video ya duermen).
SUSCRIBIR_DESDE, SUSCRIBIR_HASTA = 45, 150


def rotulo_suscribir(png, w, h):
    from playwright.sync_api import sync_playwright
    ch = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=os.environ.get('CHROMIUM') or (ch if os.path.exists(ch) else None))
        pag = nav.new_page(viewport={'width': int(w), 'height': int(h)})
        pag.goto(f"file://{RAIZ / '05-produccion' / 'suscribir.html'}")
        pag.wait_for_timeout(500)                    # fuentes
        pag.screenshot(path=str(png), omit_background=True)
        nav.close()


def pantalla_oscura(hevc, final, video, dur, visible, crf):
    """Video para dormir (29/09, «dark screen sleep music»): el mandala los
    primeros minutos, un fundido a negro de 30 s y negro hasta el final, para
    que la luz del teléfono no despierte. Se codifica solo el tramo con mandala
    y 48 s de negro; el resto es ese negro repetido sin recodificar, como el
    bucle. Con los encabezados en cada fotograma clave, los tramos se pegan sin
    saltos. De paso el archivo pesa mucho menos: el negro casi no ocupa."""
    x265 = ['-c:v', 'libx265', '-crf', str(crf), '-preset', 'slow', '-tag:v', 'hvc1',
            '-pix_fmt', 'yuv420p',
            '-x265-params', 'keyint=1152:min-keyint=1152:repeat-headers=1:log-level=error']
    info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                           'stream=width,height,r_frame_rate', '-of', 'csv=p=0', str(hevc)],
                          capture_output=True, text=True, check=True).stdout.strip().split(',')
    w, h, fps = info[0], info[1], info[2]
    tramos = video.with_name('tramos')
    tramos.mkdir(exist_ok=True)
    mandala, negro = tramos / 'mandala.mp4', tramos / 'negro.mp4'
    png = tramos / 'suscribir.png'
    rotulo_suscribir(png, w, h)
    a, b = SUSCRIBIR_DESDE, SUSCRIBIR_HASTA
    correr(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-stream_loop', '-1', '-i', hevc,
            '-loop', '1', '-framerate', fps, '-i', png, '-t', f'{visible:.3f}', '-filter_complex',
            f'[1:v]format=rgba,fade=t=in:st={a}:d=2:alpha=1,fade=t=out:st={b - 2}:d=2:alpha=1[s];'
            f"[0:v][s]overlay=0:0:enable='between(t,{a},{b})',"
            f'fade=t=out:st={visible - 30:.3f}:d=30[v]',
            '-map', '[v]', '-an', *x265, mandala])
    correr(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-f', 'lavfi',
            '-i', f'color=c=black:s={w}x{h}:r={fps}:d=48', '-an', *x265, negro])
    veces = int((dur - visible) // 48) + 2
    lista = tramos / 'lista.txt'
    lista.write_text(f"file '{mandala.name}'\n" + f"file '{negro.name}'\n" * veces)
    correr(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-f', 'concat', '-safe', '0',
            '-i', lista, '-i', final, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '320k', '-t', f'{dur:.3f}',
            '-movflags', '+faststart', video])
    shutil.rmtree(tramos)


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
        # El bucle va en HEVC siempre, y YouTube lo acepta igual. Con crf 27 no
        # bajaba nada (OBRA-041: 1 GB por hora, lo mismo que en H.264); con 31
        # pesa ~570 MB por hora y al 100 % no se distingue del bucle original
        # (SSIM 0,987, comparado el 27/09). El audio no se toca: AAC a 320 kbps.
        # Más de 2,5 h: crf 33 (~1 Mbps), para que 3 h de video no pasen los 2 GB
        # que admite una Release (con 31 serían ~2,1 GB).
        crf = 33 if dur > 150 * 60 else 31
        hevc = bucle.with_name(bucle.stem + f'-hevc{crf}.mp4')
        if not hevc.exists():
            correr(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-i', bucle,
                    '-c:v', 'libx265', '-crf', str(crf), '-preset', 'slow',
                    '-x265-params', 'keyint=1152:min-keyint=1152:log-level=error',
                    '-tag:v', 'hvc1', '-pix_fmt', 'yuv420p', hevc])
        oscura = float(o.get('pantalla_oscura_min') or 0)
        if oscura:
            pantalla_oscura(hevc, final, video, dur, oscura * 60, crf)
        else:
            correr(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-stream_loop', '-1',
                    '-i', hevc, '-i', final, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '320k', '-t', f'{dur:.3f}',
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
        'pinned_comment': o.get('comentario_fijado', ''),
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
