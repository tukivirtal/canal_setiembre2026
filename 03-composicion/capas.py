#!/usr/bin/env python3
"""
Capas de sonido que acompañan a la obra: pájaros o sonidos zen.

    python3 03-composicion/capas.py aves 160 capa-aves.wav
    python3 03-composicion/capas.py zen  160 capa-zen.wav --raiz 528

Después se mezclan con ambiente.py (--capa). Todo se sintetiza acá, sin
grabaciones ajenas, así que el máster sigue siendo propio.

Pedido de la prueba de escucha del 23/09: que la obra empiece con pájaros, o con
"golpecitos de objetos asiáticos". Después, "ancestral": fuego, tambor
chamánico y palo de lluvia. Las capas son deliberadamente escasas y
bajas: acompañan, no llaman la atención. Arrancan más densas en los primeros
20 segundos, cuando todavía no entró la obra, y se van espaciando.
"""
import argparse, array, math, random, wave

SR = 44100
HIRAJOSHI = [1, 9/8, 6/5, 3/2, 8/5]


def env_suave(i, n, ataque):
    """Ataque en curva y caída en coseno: sin esquinas, sin clic."""
    if i < ataque:
        x = i / ataque
        return x * x * (3 - 2 * x)
    x = (i - ataque) / max(1, n - ataque)
    return 0.5 + 0.5 * math.cos(math.pi * x)


def nota_ave(f0, f1, dur, vibrato=0.0):
    n = int(dur * SR); b = array.array('d', [0.0]) * n; fase = 0.0
    for i in range(n):
        x = i / n
        f = f0 + (f1 - f0) * x + vibrato * f0 * 0.02 * math.sin(2 * math.pi * 7 * i / SR)
        fase += 2 * math.pi * f / SR
        a = math.sin(math.pi * x) ** 2
        b[i] = a * (math.sin(fase) + 0.12 * math.sin(2 * fase))
    return b


def frase_ave(rnd):
    """Dos tipos: un trino corto de notas rápidas, o un silbido de pocas notas largas."""
    partes, t = [], 0.0
    if rnd.random() < 0.6:                                   # trino
        base = rnd.uniform(2400, 3800)
        for _ in range(rnd.randint(4, 9)):
            d = rnd.uniform(0.04, 0.09)
            f0 = base * rnd.uniform(0.92, 1.08)
            partes.append((t, nota_ave(f0, f0 * rnd.choice([1.18, 0.86, 1.1]), d)))
            t += d + rnd.uniform(0.03, 0.06)
    else:                                                    # silbido
        base = rnd.uniform(1500, 2400)
        for _ in range(rnd.randint(2, 3)):
            d = rnd.uniform(0.18, 0.32)
            f0 = base * rnd.choice([1, 9/8, 5/4, 4/5])
            partes.append((t, nota_ave(f0, f0 * rnd.uniform(0.95, 1.12), d, vibrato=1)))
            t += d + rnd.uniform(0.08, 0.2)
    return partes


def campanita(f, dur=5.0):
    """Campana pequeña de metal (furin, tingsha): parciales inarmónicos, toque suave."""
    n = int(dur * SR); b = array.array('d', [0.0]) * n
    for ratio, amp, tau in ((1.0, 1.0, 2.2), (2.76, 0.22, 0.9), (5.40, 0.06, 0.4)):
        w = 2 * math.pi * f * ratio / SR
        for i in range(n):
            b[i] += amp * math.sin(w * i) * math.exp(-i / (tau * SR))
    at = int(0.004 * SR)
    for i in range(at):
        x = i / at; b[i] *= x * x * (3 - 2 * x)
    return b


def madera(f, rnd):
    """Bloque de madera (mokugyo): cuerpo hueco, caída muy corta."""
    n = int(0.25 * SR); b = array.array('d', [0.0]) * n
    for ratio, amp, tau in ((1.0, 1.0, 0.07), (1.58, 0.35, 0.04), (2.31, 0.15, 0.025)):
        w = 2 * math.pi * f * ratio / SR
        for i in range(n):
            b[i] += amp * math.sin(w * i) * math.exp(-i / (tau * SR))
    at = int(0.003 * SR)
    for i in range(at):
        x = i / at; b[i] *= x * x * (3 - 2 * x)
    return b


def tambor(rnd):
    """Tambor chamánico de parche: un golpe grave que cae de tono (de ~105 a
    ~62 Hz), como el cuero que se afloja después del golpe. Ataque de 8 ms,
    suave: tiene que sonar a mazo forrado, no a palo."""
    n = int(0.9 * SR); b = array.array('d', [0.0]) * n; fase = 0.0
    f_ini, f_fin = rnd.uniform(98, 110), rnd.uniform(58, 66)
    for i in range(n):
        t = i / SR
        f = f_fin + (f_ini - f_fin) * math.exp(-t / 0.06)
        fase += 2 * math.pi * f / SR
        b[i] = (math.sin(fase) + 0.18 * math.sin(1.5 * fase)) * math.exp(-t / 0.28)
    at = int(0.008 * SR)
    for i in range(at):
        x = i / at; b[i] *= x * x * (3 - 2 * x)
    return b


def chasquido(rnd):
    """Un chasquido de leña: un grano de ruido cortísimo, oscurecido con un filtro
    de un polo para que no pinche."""
    n = int(rnd.uniform(0.002, 0.012) * SR); b = array.array('d', [0.0]) * n
    y, a = 0.0, rnd.uniform(0.25, 0.55)
    for i in range(n):
        y += a * (rnd.uniform(-1, 1) - y)
        b[i] = y * math.exp(-i / (n * 0.3))
    return b


def palo_de_lluvia(rnd, dur):
    """Granitos que caen por dentro de una caña: cientos de chasquidos mínimos
    con una envolvente que sube, se sostiene y se apaga."""
    n = int(dur * SR); b = array.array('d', [0.0]) * n
    for _ in range(int(dur * 180)):
        o = int(rnd.uniform(0, dur - 0.02) * SR)
        x = o / n
        g = math.sin(math.pi * x) ** 0.7 * rnd.uniform(0.2, 1.0)
        y, a = 0.0, rnd.uniform(0.35, 0.6)
        for i in range(int(0.004 * SR)):
            y += a * (rnd.uniform(-1, 1) - y)
            if o + i < n:
                b[o + i] += g * y * math.exp(-i / 40)
    return b


def poner(izq, der, buf, t, vol, pan):
    o = int(t * SR)
    for i in range(min(len(buf), len(izq) - o)):
        v = buf[i] * vol
        izq[o + i] += v * (1 - pan); der[o + i] += v * pan


def main():
    p = argparse.ArgumentParser()
    p.add_argument('tipo', choices=['aves', 'zen', 'ancestral'])
    p.add_argument('segundos', type=float)
    p.add_argument('salida')
    p.add_argument('--raiz', type=float, default=528.0)
    p.add_argument('--semilla', type=int, default=1)
    p.add_argument('--densidad', type=float, default=1.0,
                   help='más de 1 = más eventos. La selva pide ~2')
    a = p.parse_args()
    rnd = random.Random(a.semilla)
    n = int(a.segundos * SR)
    izq = array.array('d', [0.0]) * n; der = array.array('d', [0.0]) * n

    t, eventos = 1.5, 0
    if a.tipo == 'ancestral':
        # Fuego: chasquidos al azar desde el primer segundo, con rachas.
        tt = 0.3
        while tt < a.segundos - 1:
            poner(izq, der, chasquido(rnd), tt, rnd.uniform(0.15, 0.9) ** 2,
                  rnd.uniform(0.3, 0.7))
            tt += rnd.expovariate(7) * (0.4 if rnd.random() < 0.1 else 1)
            eventos += 1
        # Tambor: un latido que entra a los 20 s, crece durante 40 y se va
        # desacelerando de 62 a 54 golpes por minuto, como la respiración de
        # la obra. Nunca exactamente a tiempo: lo perfectamente regular suena
        # a máquina.
        tt, fin = 20.0, a.segundos - 22
        while tt < fin:
            prog = (tt - 20) / max(1, fin - 20)
            entra = min(1.0, (tt - 20) / 40) ** 2
            sale = min(1.0, (fin - tt) / 15)
            poner(izq, der, tambor(rnd), tt + rnd.uniform(-0.03, 0.03),
                  0.38 * entra * sale * rnd.uniform(0.8, 1.0), rnd.uniform(0.45, 0.55))
            tt += 60 / (62 - 8 * prog)
            eventos += 1
        # Palo de lluvia, dos o tres veces en toda la obra.
        tt = rnd.uniform(35, 50)
        while tt < a.segundos - 30:
            dur = rnd.uniform(3, 5)
            poner(izq, der, palo_de_lluvia(rnd, dur), tt, 0.35, rnd.choice([0.25, 0.75]))
            tt += rnd.uniform(40, 60)
            eventos += 1
    while a.tipo != 'ancestral' and t < a.segundos - 6:
        denso = t < 25                   # más presencia antes de que entre la obra
        if a.tipo == 'aves':
            pan, vol = rnd.uniform(0.1, 0.9), rnd.uniform(0.35, 1.0)
            for dt, nota in frase_ave(rnd):
                poner(izq, der, nota, t + dt, vol, pan)
            t += (rnd.uniform(2.5, 5) if denso else rnd.uniform(5, 11)) / a.densidad
        else:
            if rnd.random() < 0.65:      # racimo de campanitas, como un furin al viento
                pan = rnd.uniform(0.2, 0.8)
                for k in range(rnd.randint(2, 5)):
                    f = a.raiz * rnd.choice(HIRAJOSHI) * rnd.choice([1, 2])
                    poner(izq, der, campanita(f), t + k * rnd.uniform(0.15, 0.45),
                          rnd.uniform(0.25, 0.6), pan)
            else:                        # tres golpes lentos de madera
                f = rnd.uniform(380, 520); pan = rnd.uniform(0.3, 0.7)
                for k in range(3):
                    poner(izq, der, madera(f, rnd), t + k * 1.3, 0.7 - 0.15 * k, pan)
            t += (rnd.uniform(4, 7) if denso else rnd.uniform(8, 16)) / a.densidad
        eventos += 1

    pico = max(max(abs(v) for v in izq), max(abs(v) for v in der)) or 1.0
    g = 0.5 / pico
    out = array.array('h', [0]) * (2 * n)
    for i in range(n):
        out[2 * i] = int(izq[i] * g * 32767); out[2 * i + 1] = int(der[i] * g * 32767)
    with wave.open(a.salida, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
    print(f'{a.salida}  ·  {a.tipo}  ·  {eventos} eventos en {a.segundos:g} s')


if __name__ == '__main__':
    main()
