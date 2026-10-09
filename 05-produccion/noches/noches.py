#!/usr/bin/env python3
"""Pausas para la noche: el sonido de los TikToks, sin voz, estirado a una noche.

Es la receta de los diapasones de los TikToks (seno puro con ataque de 0,03 s,
parcial de golpe en 6,27 f, la raíz y su quinta abajo alternadas de un lado y del
otro, sala de 2,2 s y el drone grave del compositor), con tres cambios para la cama:

- el espacio entre golpes pasa de unos 9,5 a unos 15 segundos, y la respiración
  de quien escucha se alarga con él (de unas 6 a unas 4 por minuto);
- la cola de cada golpe se alarga de 4,5 a 6 segundos;
- el golpe baja de a poco (unos 5 dB) y al final queda el drone, que se apaga.

No se normaliza con loudnorm dinámico: aplastaría el descenso de volumen, que es
justamente lo que lleva al sueño.

Uso:
  python3 05-produccion/noches/noches.py --raiz 432 --minutos 12 --semilla 4321 \\
      --salida web/audio/noche-1.mp3 --titulo "Noche 1 · Dejar el trabajo en la puerta"
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
COLA_FINAL = 35       # segundos sin golpes al final, para que todo se apague
FUNDIDO_FINAL = 40    # segundos de fundido de salida


def suave(x):
    """De 0 a 1 con arranque y llegada lentos."""
    return x * x * (3 - 2 * x)


def golpes(segundos, raiz, semilla):
    n = int(segundos * SR)
    izq = np.zeros(n)
    der = np.zeros(n)
    rnd = np.random.default_rng(semilla)
    fin = segundos - COLA_FINAL
    t, k = 1.5, 0
    while t < fin:
        p = suave(min(t / fin, 1.0))
        cola = 4.5 + 1.5 * p
        tg = np.arange(int(7 * cola * SR)) / SR
        f = (raiz, raiz * 2 / 3)[k % 2]
        pan = (0.35, 0.65)[k % 2]
        fuerza = rnd.uniform(0.85, 1.0) * (1.0 - 0.45 * p)
        golpe = fuerza * 0.3 * (
            np.sin(2 * np.pi * f * tg) * (1 - np.exp(-tg / 0.03)) * np.exp(-tg / cola)
            + 0.12 * np.sin(2 * np.pi * 6.27 * f * tg) * np.exp(-tg / 0.08))
        i = int(t * SR)
        m = min(len(golpe), n - i)
        izq[i:i + m] += golpe[:m] * np.cos(pan * np.pi / 2)
        der[i:i + m] += golpe[:m] * np.sin(pan * np.pi / 2)
        k += 1
        t += rnd.uniform(8.5 + 4.5 * p, 10.5 + 5.0 * p)
    largo = int(2.2 * SR)
    sala = np.random.default_rng(1).standard_normal(largo) * np.exp(-np.arange(largo) / SR / 0.6) * 0.02
    izq = izq + fftconvolve(izq, sala)[:n]
    der = der + fftconvolve(der, sala)[:n]
    return np.stack([izq, der], 1), k


def drone(segundos, raiz, semilla, carpeta):
    ruta = os.path.join(carpeta, 'drone.wav')
    subprocess.run(
        [sys.executable, os.path.join(REPO, '03-composicion', 'compositor.py'),
         '--minutos', f'{segundos / 60 + 0.3:.2f}', '--raiz', str(raiz), '--modo', 'shin',
         '--registro', 'grave', '--caracter', 'sin-cuenco', '--aves', '0',
         '--semilla', str(semilla), '--salida', ruta],
        check=True, stdout=subprocess.DEVNULL)
    d, sr = sf.read(ruta)
    assert sr == SR, f'el drone salió a {sr} Hz'
    n = int(segundos * SR)
    d = d[:n]
    paso_alto = butter(4, 160, 'highpass', fs=SR, output='sos')
    d = sosfilt(paso_alto, d, axis=0) * 0.12
    return d * np.clip(np.arange(n) / SR / 3, 0, 1)[:, None]


def sonoridad(wav):
    """Sonoridad integrada (LUFS) medida por ffmpeg."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', wav, '-af', 'ebur128',
                        '-f', 'null', '-'], capture_output=True, text=True)
    resumen = r.stderr[r.stderr.rfind('Summary:'):]
    return float(resumen.split('I:')[1].split('LUFS')[0])


def mp3(wav, salida, titulo, album, nota, ganancia=0.0, desde=0.0, segundos=None, fundido=0.0):
    filtros = [f'volume={ganancia:.2f}dB']
    if fundido:
        filtros.append(f'afade=t=out:st={segundos - fundido}:d={fundido}')
    cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-ss', str(desde), '-i', wav]
    if segundos:
        cmd += ['-t', str(segundos)]
    if filtros:
        cmd += ['-af', ','.join(filtros)]
    cmd += ['-codec:a', 'libmp3lame', '-b:a', '128k', '-ar', str(SR), '-id3v2_version', '3',
            '-metadata', f'title={titulo}', '-metadata', 'artist=Rin',
            '-metadata', f'album={album}', '-metadata', f'comment={nota}', salida]
    subprocess.run(cmd, check=True)


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('--raiz', type=float, required=True, help='nota del diapasón, en Hz')
    a.add_argument('--minutos', type=float, default=12)
    a.add_argument('--semilla', type=int, default=1)
    a.add_argument('--salida', required=True, help='mp3 de la noche')
    a.add_argument('--titulo', required=True)
    a.add_argument('--album', default='Rin · Las 3 primeras noches')
    a.add_argument('--pico', type=float, default=-1.5, help='pico máximo, en dBFS')
    a.add_argument('--lufs', type=float, default=-20,
                   help='sonoridad integrada; más baja que los TikToks (-16) porque es para la cama')
    a.add_argument('--muestra', help='además, un mp3 con los primeros segundos (para la landing)')
    a.add_argument('--segundos-muestra', type=float, default=40)
    a.add_argument('--wav', help='guardar también el master en wav')
    x = a.parse_args()

    segundos = x.minutos * 60
    with tempfile.TemporaryDirectory() as tmp:
        g, k = golpes(segundos, x.raiz, x.semilla)
        mezcla = g + drone(segundos, x.raiz, x.semilla, tmp)
        m = int(FUNDIDO_FINAL * SR)
        mezcla[-m:] *= (np.cos(np.linspace(0, np.pi / 2, m)) ** 2)[:, None]
        mezcla *= 10 ** (x.pico / 20) / np.abs(mezcla).max()
        wav = x.wav or os.path.join(tmp, 'noche.wav')
        sf.write(wav, mezcla.astype(np.float32), SR, subtype='FLOAT')
        # Ganancia fija hasta la sonoridad pedida, sin pasar el pico: el descenso queda intacto.
        medida = sonoridad(wav)
        ganancia = min(x.lufs - medida, 0.0)
        nota = f'Sonido en {x.raiz:g} Hz y su quinta abajo. Sin voz.'
        os.makedirs(os.path.dirname(os.path.abspath(x.salida)), exist_ok=True)
        mp3(wav, x.salida, x.titulo, x.album, nota, ganancia)
        if x.muestra:
            mp3(wav, x.muestra, f'{x.titulo} (muestra)', x.album, nota, ganancia,
                segundos=x.segundos_muestra, fundido=5)
    print(f'{x.salida}: {k} golpes, {x.minutos:g} min, {x.raiz:g} Hz, '
          f'{medida + ganancia:.1f} LUFS (ganancia {ganancia:+.1f} dB)')


if __name__ == '__main__':
    main()
