#!/usr/bin/env python3
"""
Pieza corta de estilo taoísta, sintetizada desde cero: guqin (cítara de siete
cuerdas, pulsada, con sus deslizamientos y armónicos de campana), flauta xiao,
lluvia y un bordón grave que respira. Pensada para TikTok (2 minutos, vertical).

    python3 03-composicion/tao.py salida.wav --raiz 432 --segundos 120 --semilla 7

Como el resto de Rin: afinación justa (pentatónica china gong: 1, 9/8, 5/4, 3/2,
5/3), la respiración escrita en la música (de 5.5 a 4.5 respiraciones por minuto,
40 % inhalar / 60 % exhalar: las frases caen en la exhalación) y ninguna muestra
ajena. El final vuelve a la lluvia sola del principio, así el video se puede
repetir en bucle sin corte.
"""
import argparse, math, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
GONG = [1, 9/8, 5/4, 3/2, 5/3]


def escala(base, octavas):
    return [base * 2 ** o * r for o in range(octavas) for r in GONG]


def lp(x, fc, orden=2):
    return sosfilt(butter(orden, fc, 'low', fs=SR, output='sos'), x)


def bp(x, f1, f2, orden=2):
    return sosfilt(butter(orden, [f1, f2], 'band', fs=SR, output='sos'), x)


# ---------------------------------------------------------------- instrumentos

def guqin(f, dur=6.0, deslizar=0.0, vibrato=0.0, fuerza=1.0, rnd=None):
    """Cuerda pulsada, síntesis modal: parciales casi armónicos que se apagan más
    rápido cuanto más agudos. deslizar: razón de frecuencia al final de la nota
    (1.125 = sube un tono, como el shang del guqin). vibrato: el yin, lento."""
    n = int(dur * SR); t = np.arange(n) / SR
    g = np.ones(n)
    if deslizar:
        a, b = 0.35, 0.95                                     # empieza y termina el deslizamiento
        x = np.clip((t - a) / (b - a), 0, 1); x = x * x * (3 - 2 * x)
        g = deslizar ** x
    if vibrato:
        entra = np.clip((t - 0.3) / 0.8, 0, 1)
        g = g * (1 + vibrato * entra * np.exp(-t / 3) * np.sin(2 * math.pi * 4.3 * t))
    y = np.zeros(n); p = 0.19                                 # punto de pulsación
    for k in range(1, 14):
        fk = k * f * (1 + 0.00012 * k * k)
        if fk > 9000: break
        amp = abs(math.sin(math.pi * k * p)) / k ** 1.05
        tau = 5.5 / (1 + 0.45 * (k - 1))
        fase = 2 * math.pi * np.cumsum(fk * g) / SR
        y += amp * np.exp(-t / tau) * np.sin(fase)
    # el ataque del dedo: un soplo de ruido muy corto
    m = int(0.012 * SR)
    ruido = (rnd or np.random).standard_normal(m) * np.hanning(2 * m)[m:]
    y[:m] += 0.25 * lp(ruido, 3000)
    y *= np.minimum(1, t / 0.003)                             # sin clic
    y *= np.clip((dur - t) / 0.4, 0, 1)
    return fuerza * lp(y, 4200) / 2.2


def armonico(f, dur=5.0, fuerza=1.0):
    """Fan yin: el dedo roza el nodo y queda un sonido puro de campana."""
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2 * math.pi * f * t) + 0.12 * np.sin(2 * math.pi * 2 * f * t) * np.exp(-t / 0.8)
    y *= np.exp(-t / 2.8) * np.minimum(1, t / 0.004) * np.clip((dur - t) / 0.4, 0, 1)
    return fuerza * 0.55 * y


def xiao(f, dur, fuerza=1.0, rnd=None):
    """Flauta de bambú vertical: tono redondo, entra desde abajo, vibrato tardío
    y mucho aire."""
    rnd = rnd or np.random
    n = int(dur * SR); t = np.arange(n) / SR
    g = 1 - 0.008 * np.exp(-t / 0.12)                         # entra un poco baja
    vib = np.clip((t - 0.45 * dur) / (0.3 * dur), 0, 1)
    g = g * (1 + 0.005 * vib * np.sin(2 * math.pi * 4.8 * t))
    fase = 2 * math.pi * np.cumsum(f * g) / SR
    y = np.sin(fase) + 0.22 * np.sin(2 * fase) + 0.07 * np.sin(3 * fase) + 0.03 * np.sin(4 * fase)
    aire = bp(rnd.standard_normal(n), f * 1.2, min(f * 4, 9000))
    aire /= np.max(np.abs(aire)) + 1e-9
    soplo = 0.18 + 0.5 * np.exp(-t / 0.09)                    # el chiff del ataque
    y = y + soplo * aire * 0.9
    env = np.minimum(1, t / 0.35) ** 1.5 * np.clip((dur - t) / 0.9, 0, 1) ** 1.3
    env *= 1 + 0.08 * np.sin(2 * math.pi * 0.23 * t)          # el aliento no es parejo
    return fuerza * 0.33 * y * env


def lluvia(seg, rnd):
    """Lluvia suave: ruido rosado filtrado que ondula, y gotas sueltas."""
    n = int(seg * SR)
    blanco = rnd.standard_normal((2, n))
    # rosado aproximado (Paul Kellet, versión corta) por canal
    out = np.zeros((2, n))
    for c in range(2):
        b = sosfilt(butter(1, 800, 'low', fs=SR, output='sos'), blanco[c]) * 3 + blanco[c] * 0.35
        out[c] = bp(b, 250, 7000)
    lento = 1 + 0.25 * np.sin(2 * math.pi * np.arange(n) / SR / 17 + rnd.uniform(0, 6))
    out *= lento / np.max(np.abs(out))
    gotas = np.zeros((2, n))
    for _ in range(int(seg * 6)):
        i = rnd.integers(0, n - 2000); f = rnd.uniform(1400, 3600); d = int(SR * rnd.uniform(0.008, 0.02))
        tt = np.arange(d) / SR
        g = np.sin(2 * math.pi * (f + 900 * tt / tt[-1]) * tt) * np.exp(-tt / (d / SR / 4))
        c = rnd.integers(0, 2)
        gotas[c, i:i + d] += g * rnd.uniform(0.1, 0.35)
    return 0.3 * out + 0.08 * gotas


def reverb(rt60, rnd, brillo=6000):
    n = int(rt60 * SR * 1.2); t = np.arange(n) / SR
    ir = rnd.standard_normal((2, n)) * np.exp(-6.9 * t / rt60)
    ir = np.stack([lp(ir[0], brillo), lp(ir[1], brillo)])
    ir[:, :int(0.012 * SR)] = 0                               # predelay
    return ir / np.sqrt(np.sum(ir ** 2, axis=1, keepdims=True))


# -------------------------------------------------------------------- partitura

def respiraciones(seg, ini=5.5, fin=4.5):
    """Inicios de cada ciclo y su duración, de 5.5 a 4.5 respiraciones/min."""
    out, t = [], 0.0
    while t < seg:
        r = ini + (fin - ini) * min(1, t / seg)
        d = 60 / r
        out.append((t, d)); t += d
    return out


def componer(seg, raiz, semilla):
    rnd = np.random.default_rng(semilla)
    L = int(seg * SR)
    capas = {k: np.zeros((2, L)) for k in ('qin', 'xiao', 'arm', 'drone')}

    def poner(capa, buf, t, pan=0.0):
        i = int(t * SR)
        if i >= L: return
        buf = buf[:L - i]
        capas[capa][0, i:i + len(buf)] += buf * math.cos((pan + 1) * math.pi / 4)
        capas[capa][1, i:i + len(buf)] += buf * math.sin((pan + 1) * math.pi / 4)

    qin = escala(raiz / 4, 3)        # 108 Hz … registro grave y medio del guqin
    fla = escala(raiz / 2, 2)[3:]    # la xiao: de 324 Hz para arriba
    ciclos = respiraciones(seg)

    # el gancho: dos armónicos y la cuerda grave en el primer segundo
    poner('arm', armonico(raiz, 5), 0.25, -0.1)
    poner('arm', armonico(raiz * 3 / 2, 5, 0.8), 0.9, 0.15)
    poner('qin', guqin(qin[0], 7, vibrato=0.004, rnd=rnd), 0.6, -0.15)

    pos = 7                                                   # índice en la escala del guqin
    for c, (t0, d) in enumerate(ciclos):
        exh = t0 + 0.4 * d                                    # empieza la exhalación
        if t0 < 4 or t0 > seg - 16: continue
        fase = t0 / seg
        # guqin: 2 a 4 notas en la exhalación; más escaso cuando canta la xiao
        notas = rnd.integers(2, 5) if not (0.3 < fase < 0.72) else rnd.integers(1, 3)
        paso = 0.6 * d / (notas + 0.5)
        for j in range(notas):
            pos = int(np.clip(pos + rnd.choice([-2, -1, -1, 1, 1, 2]), 2, len(qin) - 2))
            if j == notas - 1 and rnd.random() < 0.5:
                pos = 5 if pos > 5 else 0                      # cierra en la raíz o su octava
            desl = 0.0
            if rnd.random() < 0.25 and pos + 1 < len(qin):
                desl = qin[pos + 1] / qin[pos]                 # shang: sube a la nota vecina
            poner('qin', guqin(qin[pos], 6, deslizar=desl, vibrato=0.005 if not desl else 0,
                               fuerza=rnd.uniform(0.7, 1.0), rnd=rnd),
                  exh + j * paso + rnd.uniform(-0.08, 0.08), -0.15)
        # armónicos de campana, de vez en cuando
        if rnd.random() < (0.55 if fase > 0.7 else 0.3):
            h = rnd.choice([raiz, raiz * 3 / 2, raiz * 5 / 4, raiz * 2])
            poner('arm', armonico(h, 5, rnd.uniform(0.5, 0.8)), exh + 0.6 * d * rnd.uniform(0.3, 1), rnd.uniform(-0.3, 0.3))
        # la xiao: una nota larga por exhalación, de la mitad para adelante
        if 0.26 < fase < 0.84:
            f = fla[int(rnd.integers(0, len(fla)))]
            poner('xiao', xiao(f, 0.6 * d * rnd.uniform(0.85, 1.0), rnd.uniform(0.75, 1.0), rnd),
                  exh + 0.1, 0.2)
            if rnd.random() < 0.35:                            # a veces, una respuesta breve
                f2 = fla[int(np.clip(fla.index(f) + rnd.choice([-1, 1]), 0, len(fla) - 1))]
                poner('xiao', xiao(f2, 1.6, 0.6, rnd), t0 + d - 1.2, 0.2)

    # el cierre: la cuerda grave y un armónico, y después solo lluvia
    poner('qin', guqin(qin[0], 8, vibrato=0.004, rnd=rnd), seg - 15, -0.15)
    poner('arm', armonico(raiz, 6, 0.7), seg - 13, 0.1)

    # el bordón: raíz y quinta muy bajos, crecen al inhalar
    t = np.arange(L) / SR
    resp = np.zeros(L)
    for t0, d in ciclos:
        i0, i1 = int(t0 * SR), min(L, int((t0 + d) * SR))
        x = (np.arange(i1 - i0) / SR) / d
        resp[i0:i1] = np.where(x < 0.4, np.sin(math.pi * x / 0.8) ** 2, np.cos(math.pi * (x - 0.4) / 1.2) ** 2)
    dr = (np.sin(2 * math.pi * raiz / 4 * t) + 0.6 * np.sin(2 * math.pi * raiz * 3 / 8 * t + 1)
          + 0.25 * np.sin(2 * math.pi * raiz / 2 * t + 2)) * (0.45 + 0.55 * resp)
    dr *= np.clip(t / 6, 0, 1) * np.clip((seg - 12 - t) / 6, 0, 1)
    capas['drone'] += 0.1 * np.stack([dr, dr])

    # sala: el guqin más seco, la xiao y los armónicos más lejos
    ir_c, ir_l = reverb(2.6, rnd, 5000), reverb(4.2, rnd, 4200)
    def sala(x, ir, mojado):
        w = np.stack([fftconvolve(x[0], ir[0])[:L], fftconvolve(x[1], ir[1])[:L]])
        return (1 - mojado) * x + mojado * w * 1.4
    mezcla = (sala(capas['qin'], ir_c, 0.3) + sala(capas['arm'], ir_l, 0.45)
              + sala(capas['xiao'], ir_l, 0.4) + capas['drone'])
    ll = lluvia(seg, rnd)
    borde = np.clip(t / 2.5, 0, 1) * np.clip((seg - t) / 2.5, 0, 1)
    mezcla = mezcla + ll * (0.35 + 0.65 * borde)               # la lluvia nunca se va del todo
    return mezcla / (np.max(np.abs(mezcla)) + 1e-9) * 0.89


def main():
    p = argparse.ArgumentParser()
    p.add_argument('salida')
    p.add_argument('--raiz', type=float, default=432)
    p.add_argument('--segundos', type=float, default=120)
    p.add_argument('--semilla', type=int, default=7)
    a = p.parse_args()
    x = componer(a.segundos, a.raiz, a.semilla)
    pcm = (np.clip(x.T, -1, 1) * 32767).astype('<i2')
    with wave.open(a.salida, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(a.salida)


if __name__ == '__main__':
    main()
