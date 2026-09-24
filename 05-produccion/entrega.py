#!/usr/bin/env python3
"""
Los textos para publicar una obra a mano, en un solo archivo:

    python3 05-produccion/entrega.py OBRA-020   →   produccion/OBRA-020/textos.txt

El video largo (título, descripción, etiquetas, ajustes y la traducción al
español) y sus 5 Shorts (YouTube y TikTok por separado). Sale de
metadatos.json (montar.py) y short-<n>.json (hacer_short.py).
"""
import json, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def main():
    obra = sys.argv[1]
    d = RAIZ / 'produccion' / obra
    m = json.loads((d / 'metadatos.json').read_text(encoding='utf-8'))
    es = m['localizations']['es']
    t = [f'''{obra}

==================== VIDEO LARGO ====================

TÍTULO
{m['title']}

DESCRIPCIÓN
{m['description']}

ETIQUETAS
{', '.join(m['tags'])}

AJUSTES
Categoría: Música
Idioma del video: Inglés
Certificación de subtítulos: Ninguna
¿Es contenido creado para niños?: No
Contenido alterado o sintético: No
Licencia: Licencia estándar de YouTube

TRADUCCIÓN AL ESPAÑOL (opcional: Subtítulos > Agregar idioma > Español > Título y descripción)
Título: {es['title']}

Descripción:
{es['description']}
''']
    for n in range(1, 6):
        f = d / f'short-{n}.json'
        if not f.exists():
            continue
        s = json.loads(f.read_text(encoding='utf-8'))
        t.append(f'''
==================== SHORT {n} ====================

--- YOUTUBE SHORTS ---
Título:
{s['yt_titulo']}

Descripción:
{s['yt_descripcion']}

Etiquetas:
{s['yt_etiquetas']}

Video relacionado:
{s['yt_video_relacionado'] or '(el video largo, una vez publicado)'}

--- TIKTOK ---
Título de portada (el que se ve en el perfil):
{s['tiktok_portada']}

Descripción (va con el video):
{s['tiktok_descripcion']}
''')
    (d / 'textos.txt').write_text(''.join(t), encoding='utf-8')
    print(d / 'textos.txt')


if __name__ == '__main__':
    main()
