#!/usr/bin/env python3
"""Sonido de los TikToks y las historias: diapasones (la raíz y su quinta abajo) sobre el drone grave.

Es la receta de los TikToks que funcionaron (trabajo, noche, mañana), que hasta ahora vivía en
comandos sueltos:
  corto     ~60 s: golpes cada 4,8–5,6 s, cola de 3,2 s
  largo     2–3 min: golpes cada 8,5–10,5 s, cola de 4,5 s
  historia  15 s: tres golpes, en 0,3 · 5,3 · 10,2 s

Uso:
  python3 05-produccion/shorts/sonido_tiktok.py --modo corto --raiz 417 --segundos 60 \\
      --semilla 4171 --salida produccion/tiktok-cansada/cansada-master.wav
"""
import argparse
import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODOS = {
    'corto': dict(cola=3.2, largo=10.0, separacion=(4.8, 5.6), inicio=0.3, desde_drone=20),
    'largo': dict(cola=4.5, largo=14.0, separacion=(8.5, 10.5), inicio=0.8, desde_drone=0),
    'historia': dict(cola=4.5, largo=14.0, golpes=(0.3, 5.3, 10.2), desde_drone=0),
}


def golpe(f, fuerza, cola, largo):
    t = np.arange(int(largo * SR)) / SR
    return fuerza * 0.3 * (np.sin(2 * np.pi * f * t) * (1 - np.exp(-t / 0.03)) * np.exp(-t / cola)
                           + 0.12 * np.sin(2 * np.pi * 6.27 * f * t) * np.exp(-t / 0.08))


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('--modo', choices=MODOS, required=True)
    a.add_argument('--raiz', type=float, required=True)
    a.add_argument('--segundos', type=float, required=True)
    a.add_argument('--semilla', type=int, default=1)
    a.add_argument('--salida', required=True)
    x = a.parse_args()
    m = MODOS[x.modo]
    dur = x.segundos
    n = int((dur + 4) * SR)
    rnd = np.random.default_rng(x.semilla)
    izq, der = np.zeros(n), np.zeros(n)
    if 'golpes' in m:
        tiempos = list(m['golpes'])
    else:
        tiempos, t = [], m['inicio']
        while t < dur - m['separacion'][0] - 1:
            tiempos.append(t)
            t += rnd.uniform(*m['separacion'])
    for k, t in enumerate(tiempos):
        f = (x.raiz, x.raiz * 2 / 3)[k % 2]
        pan = (0.35, 0.65)[k % 2]
        g = golpe(f, rnd.uniform(0.85, 1.0), m['cola'], m['largo'])
        i = int(t * SR)
        k2 = min(len(g), n - i)
        izq[i:i + k2] += g[:k2] * np.cos(pan * np.pi / 2)
        der[i:i + k2] += g[:k2] * np.sin(pan * np.pi / 2)
    largo_sala = int(2.2 * SR)
    sala = np.random.default_rng(1).standard_normal(largo_sala) * np.exp(-np.arange(largo_sala) / SR / 0.6) * 0.02
    izq = izq + fftconvolve(izq, sala)[:n]
    der = der + fftconvolve(der, sala)[:n]

    with tempfile.TemporaryDirectory() as tmp:
        ruta = os.path.join(tmp, 'drone.wav')
        subprocess.run([sys.executable, os.path.join(REPO, '03-composicion', 'compositor.py'),
                        '--minutos', f'{(dur + m["desde_drone"]) / 60 + 0.3:.2f}', '--raiz', str(x.raiz),
                        '--modo', 'shin', '--registro', 'grave', '--caracter', 'sin-cuenco', '--aves', '0',
                        '--semilla', str(x.semilla), '--salida', ruta], check=True, stdout=subprocess.DEVNULL)
        d, sr = sf.read(ruta)
        assert sr == SR
        i0 = int(m['desde_drone'] * SR)
        d = d[i0:i0 + n]
        if len(d) < n:
            d = np.pad(d, ((0, n - len(d)), (0, 0)))
        d = sosfilt(butter(4, 160, 'highpass', fs=SR, output='sos'), d, axis=0) * 0.12
        d *= np.clip(np.arange(n) / SR / 3, 0, 1)[:, None]
        mezcla = np.stack([izq, der], 1) + d
        mezcla *= 0.8 / np.abs(mezcla).max()
        crudo = os.path.join(tmp, 'crudo.wav')
        sf.write(crudo, mezcla.astype(np.float32), SR, subtype='FLOAT')
        fundido = 1.5 if x.modo == 'historia' else (4 if dur <= 90 else 5)
        os.makedirs(os.path.dirname(os.path.abspath(x.salida)), exist_ok=True)
        subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-i', crudo, '-t', str(dur), '-af',
                        f'loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st={dur - fundido}:d={fundido}',
                        '-ar', '48000', x.salida], check=True)
    print(f'{x.salida}: {len(tiempos)} golpes, {dur:g} s, {x.raiz:g} Hz')


if __name__ == '__main__':
    main()
