#!/usr/bin/env python3
"""
La cola de Shorts que lee Make: una hoja de Google «Rin_Shorts» con una fila
por Short listo para subir, en el orden en que se suben (de arriba abajo).

    python3 08-catalogo/cola_shorts.py OBRA-012 OBRA-015 > cola.csv

Intercala las obras y no pone seguidos dos Shorts con el mismo número (tienen
la misma frase en pantalla si las obras comparten intención). La columna B
(estado) empieza en «pendiente»; Make la pasa a «completado» al subir.

url_archivo apunta a la versión liviana (short-<n>-web.mp4, bajo 5 MB) en la
rama «shorts» del repositorio, que es público: Make la descarga de ahí.
"""
import csv, sys, pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[1]
RAW = 'https://raw.githubusercontent.com/tukivirtal/canal_setiembre2026/shorts'
COLS = ['id_short', 'estado', 'obra', 'n', 'url_archivo', 'yt_titulo', 'yt_descripcion',
        'yt_etiquetas', 'yt_video_relacionado', 'tiktok_portada', 'tiktok_descripcion',
        'url_youtube', 'fecha_youtube', 'url_tiktok', 'fecha_tiktok']


def orden(obras, n=5):
    """Obra por obra en ronda, desplazando el número del Short en cada obra:
    con dos obras sale S1, S2, S3, S4, S5, S1, S2... alternando obra."""
    filas = []
    for vuelta in range(n):
        for j, o in enumerate(obras):
            filas.append((o, (vuelta * len(obras) + j) % n + 1))
    return filas


def main():
    obras = sys.argv[1:]
    with open(RAIZ / '08-catalogo' / 'shorts.csv', encoding='utf-8') as f:
        s = {x['id_short']: x for x in csv.DictReader(f)}
    w = csv.writer(sys.stdout)
    w.writerow(COLS)
    for o, n in orden(obras):
        x = s[f'{o}-S{n}']
        w.writerow([x['id_short'], 'pendiente', o, n, f'{RAW}/{o}/short-{n}-web.mp4',
                    x['yt_titulo'], x['yt_descripcion'], x['yt_etiquetas'],
                    x['yt_video_relacionado'], x['tiktok_portada'], x['tiktok_descripcion'],
                    '', '', '', ''])


if __name__ == '__main__':
    main()
