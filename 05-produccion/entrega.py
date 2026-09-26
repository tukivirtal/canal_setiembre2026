#!/usr/bin/env python3
"""
Los textos para publicar una obra a mano, en un solo archivo:

    python3 05-produccion/entrega.py OBRA-020   →   produccion/OBRA-020/textos.txt

El video largo (título, descripción, etiquetas, ajustes y la traducción al
español) y sus 5 Shorts (YouTube y TikTok por separado). Sale de
metadatos.json (montar.py) y de la hoja de Shorts del catálogo.
"""
import csv, json, pathlib, sys

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
    # Los textos de los Shorts salen de la hoja (08-catalogo/shorts.csv), no de
    # los short-<n>.json: así el archivo trae los 7 aunque se hayan hecho en
    # corridas distintas.
    with open(RAIZ / '08-catalogo' / 'shorts.csv', encoding='utf-8') as f:
        filas = [x for x in csv.DictReader(f) if x['obra'] == obra]
    for s in filas:
        n = s['n']
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
