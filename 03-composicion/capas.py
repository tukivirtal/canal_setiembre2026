#!/usr/bin/env python3
"""
Capas de sonido que acompañan a la obra: pájaros, sonidos zen, ancestral o
jardín (pájaros con campanitas de viento sueltas, afinadas a la raíz).

    python3 03-composicion/capas.py aves 160 capa-aves.wav
    python3 03-composicion/capas.py zen  160 capa-zen.wav --raiz 528
    python3 03-composicion/capas.py theta 10840 capa-theta.wav --raiz 432

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


def theta(segundos, salida, raiz, pulsos=(6.0, 4.0, 2.0), octava_abajo=False):
    """Ondas theta que bajan a delta (29/09, idea de YouTube Studio para el
    canal): dos senos puros, uno por oído, en la tercera mayor justa (5/4) de
    la raíz bajada a 150-300 Hz: 432 -> 216 -> 270 Hz. No en la raíz misma: el
    drone de dormir tiene fuerte la raíz, la quinta y las octavas (108, 162,
    216, 324 Hz) y una portadora a 3 Hz de una de ellas temblaría en cada oído,
    también por parlante. La tercera forma con ellas un acorde justo 4:5:6.
    La diferencia entre los dos oídos es el pulso que se percibe, y solo existe
    con auriculares: 6 Hz (theta, el momento de dormirse) que baja a 4 Hz en la
    primera hora y a 2 Hz (delta, sueño profundo) en la segunda; la tercera se
    queda en 2. Nada de golpes ni de ritmo audible: por parlante se oye un
    zumbido grave y quieto. Se calcula por bloques de un minuto (3 h en una
    sola pasada serían 4 GB) con la fase acumulada, así no hay saltos."""
    import numpy as np
    portadora = raiz
    while portadora > 300:
        portadora /= 2.0
    portadora *= 5 / 4
    if portadora > 300:
        portadora /= 2.0
    if octava_abajo:
        portadora /= 2.0
    n, bloque = int(segundos * SR), 60 * SR
    hora = 3600.0

    def pulso(t):
        a, b, c = pulsos
        return np.interp(t, [0, hora, 2 * hora, max(segundos, 2 * hora)], [a, b, c, c])

    fase_i = fase_d = 0.0
    with wave.open(salida, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        for ini in range(0, n, bloque):
            t = (ini + np.arange(min(bloque, n - ini))) / SR
            b = pulso(t)
            fi = fase_i + 2 * np.pi * np.cumsum(portadora - b / 2) / SR
            fd = fase_d + 2 * np.pi * np.cumsum(portadora + b / 2) / SR
            fase_i, fase_d = fi[-1] % (2 * np.pi), fd[-1] % (2 * np.pi)
            # entra en 20 s y sale en 15, y respira muy lento (±15 % cada 40 s)
            env = np.minimum(1, t / 20) ** 2 * np.clip((segundos - t) / 15, 0, 1) \
                * (0.85 + 0.15 * np.sin(2 * np.pi * t / 40))
            est = np.empty(2 * len(t), dtype='<i2')
            est[0::2] = (0.5 * env * np.sin(fi) * 32767).astype('<i2')
            est[1::2] = (0.5 * env * np.sin(fd) * 32767).astype('<i2')
            w.writeframes(est.tobytes())
    print(f'{salida}  ·  portadora {portadora:g} Hz, pulso {" -> ".join(f"{x:g}" for x in pulsos)} Hz en {segundos:g} s')


def diapasones(segundos, salida, raiz, semilla=1):
    """Diapasones (06/10): el sonido de los TikToks que ganaron («60 seconds to
    let go» y «396 Hz tuning forks»: 63 y 43 seguidores en 12 h, con la misma
    promoción que antes no traía ninguno). Un golpe cada 8,5–10,5 s, alternando
    la raíz y su quinta abajo (396 y 264, 3:2), uno a cada lado. Tono puro, apenas el
    «clang» del golpe (un parcial inarmónico a ~6,27 f que dura décimas) y una
    sala corta. Se calcula golpe por golpe, así un video de 15 min no ocupa
    gigas de memoria."""
    import numpy as np
    from scipy.signal import fftconvolve
    n = int(segundos * SR)
    izq = np.zeros(n, dtype=np.float32); der = np.zeros(n, dtype=np.float32)
    sala = np.random.default_rng(1).standard_normal(int(2.2 * SR)) \
        * np.exp(-np.arange(int(2.2 * SR)) / SR / 0.6) * 0.02
    sala[0] += 1.0
    tg = np.arange(int(14.0 * SR)) / SR
    env = (1 - np.exp(-tg / 0.03)) * np.exp(-tg / 4.5)
    rnd = np.random.default_rng(semilla)
    t, k = 0.8, 0
    while t < segundos - 12:
        f = (raiz, raiz * 2 / 3)[k % 2]; pan = (0.35, 0.65)[k % 2]
        golpe = np.sin(2 * np.pi * f * tg) * env \
            + 0.12 * np.sin(2 * np.pi * 6.27 * f * tg) * np.exp(-tg / 0.08)
        golpe = fftconvolve(golpe * rnd.uniform(0.8, 1.0) * 0.3, sala)
        o = int(t * SR); m = min(len(golpe), n - o)
        izq[o:o + m] += golpe[:m] * math.cos(pan * math.pi / 2)
        der[o:o + m] += golpe[:m] * math.sin(pan * math.pi / 2)
        k += 1; t += rnd.uniform(8.5, 10.5)
    g = 0.5 / (max(np.abs(izq).max(), np.abs(der).max()) or 1.0)
    est = np.empty(2 * n, dtype='<i2')
    est[0::2] = (izq * g * 32767).astype('<i2'); est[1::2] = (der * g * 32767).astype('<i2')
    with wave.open(salida, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(est.tobytes())
    print(f'{salida}  ·  diapasones {raiz:g} y {raiz * 2 / 3:g} Hz  ·  {k} golpes en {segundos:g} s')


def poner(izq, der, buf, t, vol, pan):
    o = int(t * SR)
    for i in range(min(len(buf), len(izq) - o)):
        v = buf[i] * vol
        izq[o + i] += v * (1 - pan); der[o + i] += v * pan


def main():
    p = argparse.ArgumentParser()
    p.add_argument('tipo', choices=['aves', 'zen', 'ancestral', 'jardin', 'theta', 'delta',
                                    'diapasones'])
    p.add_argument('segundos', type=float)
    p.add_argument('salida')
    p.add_argument('--raiz', type=float, default=528.0)
    p.add_argument('--semilla', type=int, default=1)
    p.add_argument('--densidad', type=float, default=1.0,
                   help='más de 1 = más eventos. La selva pide ~2')
    a = p.parse_args()
    if a.tipo == 'theta':
        return theta(a.segundos, a.salida, a.raiz)
    if a.tipo == 'diapasones':
        return diapasones(a.segundos, a.salida, a.raiz, a.semilla)
    if a.tipo == 'delta':
        # 04/10: ondas delta desde el principio, para el sueño profundo: de 3 Hz a
        # 2 en la primera hora y a 1,5 en la segunda. Va con el ruido rosa.
        # Una octava abajo (135 Hz): los dos tonos, mezclados en el aire, hacen
        # un temblor de 3 Hz que por el parlante del teléfono sonaba a
        # interferencia (escucha de Fátima, 05/10). A 135 Hz el teléfono casi no
        # lo reproduce y con auriculares el pulso sigue igual.
        return theta(a.segundos, a.salida, a.raiz, pulsos=(3.0, 2.0, 1.5), octava_abajo=True)
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
        if a.tipo in ('aves', 'jardin'):
            pan, vol = rnd.uniform(0.1, 0.9), rnd.uniform(0.35, 1.0)
            for dt, nota in frase_ave(rnd):
                poner(izq, der, nota, t + dt, vol, pan)
            # jardín: de vez en cuando, un furin lejano entre los pájaros. Pocas
            # campanitas, bajas y en la escala de la obra: se oyen sin llamar
            # la atención, que es lo que pide la ansiedad
            if a.tipo == 'jardin' and not denso and rnd.random() < 0.22:
                pb, tb = rnd.uniform(0.25, 0.75), t + rnd.uniform(1, 4)
                for k in range(rnd.randint(2, 3)):
                    f = a.raiz * rnd.choice(HIRAJOSHI) * rnd.choice([1, 2])
                    poner(izq, der, campanita(f), tb + k * rnd.uniform(0.3, 0.7),
                          rnd.uniform(0.12, 0.3), pb)
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
