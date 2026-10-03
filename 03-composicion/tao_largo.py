#!/usr/bin/env python3
"""
La versión larga del guqin de tao.py, para dormir: horas de cuerda pulsada,
flauta xiao y armónicos de campana sobre un bordón grave que respira.

    python3 03-composicion/tao_largo.py --minutos 180 --raiz 432 --modo yu --semilla 7 --salida obra.wav

Solo la obra. La lluvia la pone ambiente.py (--fondo lluvia), como el mar en
las demás, así el ambiente es continuo durante las tres horas.

Se compone por tramos de 4 minutos, cada uno con su propia semilla (nada se
repite), sobre un único ciclo respiratorio para toda la obra (de 4.5 a 3.5
respiraciones por minuto: las frases caen en la exhalación) y con las colas de
la sala que pasan de un tramo al siguiente, así no hay costuras. Tres horas de
una sola vez no entran en memoria; por tramos, cada uno pesa unos cientos de MB.

Para dormir la música se va retirando: la primera media hora suena como el
TikTok, después el guqin toca en cada vez menos respiraciones, la xiao se
despide antes de la hora y media, y en la última hora quedan pocas notas, los
armónicos y el bordón, cada vez más bajos.
"""
import argparse, math, pathlib, sys, wave
import numpy as np
from scipy.signal import fftconvolve

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tao

tao.SR = SR = 44100                    # la del resto del canal (ambiente.py)
TRAMO = 240.0                          # segundos de cada tramo
COLA = 14.0                            # lo que suena después: la nota y la sala


def entre(t, puntos):
    """Interpolación lineal en minutos: puntos = [(minuto, valor), ...]."""
    m, v = zip(*puntos)
    return float(np.interp(t / 60, m, v))


def componer(salida, minutos, raiz, semilla, modo, resp=(4.5, 3.5)):
    total = minutos * 60
    grados = tao.MODOS[modo]
    qin = tao.escala(raiz / 4, 3, grados)          # 108 Hz … grave y medio del guqin
    fla = tao.escala(raiz / 2, 2, grados)[3:]      # la xiao, de 324 Hz para arriba
    ciclos = tao.respiraciones(total, *resp)
    r0 = np.random.default_rng(semilla)
    ir_c, ir_l = tao.reverb(2.6, r0, 5000), tao.reverb(4.2, r0, 4200)

    # Cómo se retira la música (por minuto de la obra)
    frase = [(0, 1.0), (30, 1.0), (90, 0.55), (150, 0.35), (180, 0.3)]     # prob. de frase de guqin
    notas_max = [(0, 4), (30, 4), (90, 3), (120, 2), (180, 2)]
    flauta = [(0, 0.0), (3, 0.0), (5, 0.7), (45, 0.6), (80, 0.15), (95, 0.0), (180, 0.0)]
    campana = [(0, 0.3), (60, 0.3), (120, 0.4), (180, 0.4)]
    nivel = [(0, 1.0), (60, 0.9), (120, 0.75), (180, 0.65)]               # −4 dB en tres horas

    n_total = int(total * SR)
    arrastre = np.zeros((2, 0))
    pico = 0.0
    w = wave.open(str(salida), 'wb')
    w.setnchannels(2); w.setsampwidth(4); w.setframerate(SR)
    k = 0
    while k * TRAMO < total:
        t0 = k * TRAMO
        dur = min(TRAMO, total - t0)
        L = int((dur + COLA) * SR)
        capas = {c: np.zeros((2, L)) for c in ('qin', 'arm', 'xiao')}
        rnd = np.random.default_rng(semilla * 1000 + k)

        def poner(capa, buf, t, pan=0.0):
            i = int((t - t0) * SR)                 # t en tiempo de la obra
            if i < 0 or i >= L: return
            buf = buf[:L - i]
            capas[capa][0, i:i + len(buf)] += buf * math.cos((pan + 1) * math.pi / 4)
            capas[capa][1, i:i + len(buf)] += buf * math.sin((pan + 1) * math.pi / 4)

        if k == 0:                                 # el gancho, como en el TikTok
            poner('arm', tao.armonico(raiz, 5), 0.25, -0.1)
            poner('arm', tao.armonico(raiz * 3 / 2, 5, 0.8), 0.9, 0.15)
            poner('qin', tao.guqin(qin[0], 7, vibrato=0.004, rnd=rnd), 0.6, -0.15)

        pos = 7
        for tc, d in ciclos:
            if not (t0 <= tc < t0 + dur) or tc < 4 or tc > total - 25:
                continue
            exh = tc + 0.4 * d
            if rnd.random() < entre(tc, frase):
                hay_xiao = rnd.random() < entre(tc, flauta)
                tope = int(round(entre(tc, notas_max)))
                notas = int(rnd.integers(1, 3)) if hay_xiao else int(rnd.integers(1, tope + 1))
                paso = 0.6 * d / (notas + 0.5)
                for j in range(notas):
                    pos = int(np.clip(pos + rnd.choice([-2, -1, -1, 1, 1, 2]), 2, len(qin) - 2))
                    if j == notas - 1 and rnd.random() < 0.5:
                        pos = 5 if pos > 5 else 0              # cierra en la raíz o su octava
                    desl = qin[pos + 1] / qin[pos] if rnd.random() < 0.25 else 0.0
                    poner('qin', tao.guqin(qin[pos], 6, deslizar=desl, vibrato=0.005 if not desl else 0,
                                           fuerza=rnd.uniform(0.7, 1.0), rnd=rnd),
                          exh + j * paso + rnd.uniform(-0.08, 0.08), -0.15)
                if hay_xiao:
                    f = fla[int(rnd.integers(0, len(fla)))]
                    poner('xiao', tao.xiao(f, 0.6 * d * rnd.uniform(0.85, 1.0), rnd.uniform(0.7, 0.95), rnd),
                          exh + 0.1, 0.2)
            if rnd.random() < entre(tc, campana):
                h = rnd.choice([raiz, raiz * 3 / 2, raiz * grados[2], raiz * 2])
                poner('arm', tao.armonico(h, 5, rnd.uniform(0.45, 0.75)),
                      exh + 0.6 * d * rnd.uniform(0.3, 1), rnd.uniform(-0.3, 0.3))

        if t0 + dur >= total:                      # el cierre: la cuerda grave y un armónico
            poner('qin', tao.guqin(qin[0], 8, vibrato=0.004, rnd=rnd), total - 18, -0.15)
            poner('arm', tao.armonico(raiz, 6, 0.6), total - 16, 0.1)

        def sala(x, ir, mojado):
            m = np.stack([fftconvolve(x[0], ir[0])[:L], fftconvolve(x[1], ir[1])[:L]])
            return (1 - mojado) * x + mojado * m * 1.4

        t = t0 + np.arange(L) / SR
        mezcla = sala(capas['qin'], ir_c, 0.3) + sala(capas['arm'], ir_l, 0.45) + sala(capas['xiao'], ir_l, 0.4)
        mezcla *= np.interp(t / 60, *zip(*nivel))

        # el bordón: raíz y quinta muy bajas, crecen al inhalar. Solo en el tramo
        # propio (no en la cola, que ya es del siguiente), con el tiempo absoluto
        # y el ciclo global: así sigue sin costura de un tramo al otro.
        n_ok = min(int(dur * SR), n_total - int(t0 * SR))
        tb = t[:n_ok]
        resp_env = np.zeros(n_ok)
        for tc, d in ciclos:
            if tc + d < t0 or tc > t0 + dur:
                continue
            i0, i1 = max(0, int((tc - t0) * SR)), min(n_ok, int((tc + d - t0) * SR))
            x = (tb[i0:i1] - tc) / d
            resp_env[i0:i1] = np.where(x < 0.4, np.sin(math.pi * x / 0.8) ** 2,
                                       np.cos(math.pi * (x - 0.4) / 1.2) ** 2)
        dr = (np.sin(2 * math.pi * raiz / 4 * tb) + 0.6 * np.sin(2 * math.pi * raiz * 3 / 8 * tb + 1)
              + 0.25 * np.sin(2 * math.pi * raiz / 2 * tb + 2)) * (0.45 + 0.55 * resp_env)
        dr *= np.clip(tb / 6, 0, 1) * np.clip((total - 4 - tb) / 10, 0, 1)
        mezcla[:, :n_ok] += 0.1 * np.stack([dr, dr])

        mezcla[:, :arrastre.shape[1]] += arrastre
        listo, arrastre = mezcla[:, :n_ok] * 0.4, mezcla[:, n_ok:]
        pico = max(pico, float(np.max(np.abs(listo))))
        pcm = (np.clip(listo.T, -1, 1) * 2147483647).astype('<i4')
        w.writeframes(pcm.tobytes())
        print(f'  tramo {k + 1}: {t0 / 60:5.1f}-{(t0 + dur) / 60:5.1f} min  ·  pico {20 * math.log10(pico + 1e-12):.1f} dBFS',
              flush=True)
        k += 1
    w.close()
    print(f'{salida}  ·  {minutos:g} min  ·  {modo} sobre {raiz:g} Hz  ·  pico {20 * math.log10(pico + 1e-12):.1f} dBFS')
    if pico >= 1:
        sys.exit('saturó: bajar la ganancia')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--minutos', type=float, default=180)
    p.add_argument('--raiz', type=float, default=432)
    p.add_argument('--modo', choices=list(tao.MODOS), default='yu')
    p.add_argument('--semilla', type=int, default=7)
    p.add_argument('--salida', required=True)
    a = p.parse_args()
    componer(a.salida, a.minutos, a.raiz, a.semilla, a.modo)


if __name__ == '__main__':
    main()
