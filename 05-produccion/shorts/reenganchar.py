#!/usr/bin/env python3
"""
Rehace las versiones livianas de Shorts ya armados, sin el fundido de entrada:
les corta el primer segundo (0,6 s de negro y 1,5 s de audio subiendo) para
que empiecen con imagen y sonido. Para los Shorts que ya estaban en la cola de
Make cuando se corrigió hacer_short.py (28/09).

    python3 05-produccion/shorts/reenganchar.py DESTINO OBRA-012 OBRA-015 ...

Toma el short-<n>.mp4 de calidad completa de produccion/<obra>/ o, si no está,
de la Release de la obra, y deja DESTINO/<obra>/short-<n>-web.mp4 (bajo 5 MB,
el mismo nombre que lee Make desde la rama «shorts»).
"""
import pathlib, subprocess, sys, tempfile, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from hacer_short import ligero, RAIZ

REL = 'https://github.com/tukivirtal/canal_setiembre2026/releases/download'
CORTE = 1.0     # segundos: pasado el fundido de imagen, el audio ya está casi entero


def fuente(obra, n, tmp):
    local = RAIZ / 'produccion' / obra / f'short-{n}.mp4'
    if local.exists():
        return local
    dest = tmp / f'{obra}-short-{n}.mp4'
    urllib.request.urlretrieve(f'{REL}/{obra}/{obra}-short-{n}.mp4', dest)
    return dest


def main():
    destino = pathlib.Path(sys.argv[1])
    for obra in sys.argv[2:]:
        (destino / obra).mkdir(parents=True, exist_ok=True)
        for n in range(1, 8):
            with tempfile.TemporaryDirectory() as t:
                tmp = pathlib.Path(t)
                src = fuente(obra, n, tmp)
                corto = tmp / f'short-{n}.mp4'
                subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-ss', str(CORTE), '-i', str(src),
                                '-af', 'afade=t=in:d=0.1', '-c:v', 'libx264', '-crf', '20', '-preset', 'fast',
                                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', str(corto)], check=True)
                web = ligero(corto)
                (destino / obra / web.name).write_bytes(web.read_bytes())
                print(f'{obra} short-{n}-web.mp4  {web.stat().st_size / 1e6:.2f} MB', flush=True)


if __name__ == '__main__':
    main()
