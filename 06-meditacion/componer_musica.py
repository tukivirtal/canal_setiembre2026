#!/usr/bin/env python3
"""
Compositor de música de meditación por síntesis aditiva.

No mezcla pistas ajenas ni repite un bucle: **compone**. Cada obra tiene una
progresión armónica que avanza por secciones, campanas que entran en posiciones
distintas y texturas que evolucionan. Dos ejecuciones con semilla distinta dan
dos obras distintas, no dos versiones del mismo archivo.

Esto importa por dos razones: el audio es inequívocamente propio (sin Content ID,
sin licencias de terceros), y una obra que se desarrolla **no es contenido
repetitivo** en el sentido que penaliza YouTube.

Uso:
    python3 componer_musica.py --listar
    python3 componer_musica.py --minutos 10 --raiz 528 --escala pentatonica
    python3 componer_musica.py --minutos 60 --afinacion 432 --semilla 12

Sin dependencias: solo Python 3.
"""

import argparse
import array
import math
import random
import wave

FRECUENCIA = 44100
AMPLITUD = 32767
TAM_TABLA = 2048

# Frecuencias solfeggio. Se ofrecen como **afinación**, que es una elección
# estética legítima, no como tratamiento. Ver la nota del final.
SOLFEGGIO = {
    "396": 396.0, "417": 417.0, "528": 528.0,
    "639": 639.0, "741": 741.0, "852": 852.0,
}

# Modos, en semitonos desde la raíz. Se eligieron los que no producen
# tensión sin resolver: nada de disonancias que despierten al oyente.
ESCALAS = {
    "pentatonica": [0, 2, 4, 7, 9],           # sin semitonos: imposible que suene mal
    "dorica":      [0, 2, 3, 5, 7, 9, 10],    # menor con sexta mayor: melancólica pero abierta
    "lidia":       [0, 2, 4, 6, 7, 9, 11],    # cuarta aumentada: flotante, "suspendida"
    "japonesa":    [0, 2, 3, 7, 8],           # in sen: contemplativa, muy espaciada
}

# Grados sobre los que se construyen los acordes de cada sección.
PROGRESIONES = [
    [0, 5, 3, 4],
    [0, 3, 5, 2],
    [0, 4, 2, 5],
    [0, 2, 5, 3],
]

NIVEL_COLCHON = 0.30
NIVEL_SUB = 0.16
NIVEL_CAMPANA = 0.30
NIVEL_TEXTURA = 0.13


def semitono(raiz, n):
    """Frecuencia a n semitonos de la raíz, en temperamento igual."""
    return raiz * (2.0 ** (n / 12.0))


def tabla_colchon():
    """
    Wavetable del pad: armónicos impares con caída suave. Los impares dan un
    timbre cálido tipo órgano; los pares lo harían más nasal.
    Se precalcula una vez y después solo se indexa: es lo que hace viable
    sintetizar una hora en Python puro.
    """
    parciales = [(1, 1.0), (2, 0.45), (3, 0.30), (4, 0.12), (5, 0.14), (7, 0.06)]
    norma = sum(a for _, a in parciales)
    tabla = array.array("d", [0.0]) * TAM_TABLA
    for i in range(TAM_TABLA):
        fase = 2.0 * math.pi * i / TAM_TABLA
        tabla[i] = sum(a * math.sin(n * fase) for n, a in parciales) / norma
    return tabla


def hacer_campana(frecuencia, duracion=5.0):
    """
    Una campana sintetizada: parciales **inarmónicos** con decaimiento
    exponencial, cada uno con su propia velocidad de caída.
    Lo inarmónico es lo que distingue una campana de una nota de órgano;
    que los agudos caigan más rápido es lo que la hace sonar a metal.
    """
    n = int(duracion * FRECUENCIA)
    buf = array.array("d", [0.0]) * n
    parciales = [(1.00, 1.00, 1.0), (2.00, 0.50, 1.6), (2.41, 0.32, 2.1),
                 (3.00, 0.22, 2.6), (4.52, 0.14, 3.4), (5.63, 0.08, 4.2)]
    ataque = int(0.004 * FRECUENCIA)
    for ratio, amp, veloc in parciales:
        w = 2.0 * math.pi * frecuencia * ratio / FRECUENCIA
        for i in range(n):
            buf[i] += amp * math.sin(w * i) * math.exp(-veloc * 2.6 * i / n)
    pico = max(abs(v) for v in buf) or 1.0
    for i in range(n):
        env = min(1.0, i / ataque) if i < ataque else 1.0
        buf[i] = buf[i] / pico * env
    return buf


def componer(ruta, segundos, raiz, escala, semilla):
    random.seed(semilla)
    total = int(segundos * FRECUENCIA)
    izq = array.array("d", [0.0]) * total
    der = array.array("d", [0.0]) * total

    grados = ESCALAS[escala]
    progresion = random.choice(PROGRESIONES)

    # Secciones de entre 40 y 70 s: suficientes para instalarse, cortas para
    # que la obra avance y nunca se perciba como un bucle.
    secciones = []
    t = 0.0
    i = 0
    while t < segundos:
        dur = min(random.uniform(40.0, 70.0), segundos - t)
        secciones.append((t, dur, progresion[i % len(progresion)]))
        t += dur
        i += 1

    tabla = tabla_colchon()
    campanas = {}

    print(f"  {len(secciones)} secciones · progresión {progresion} · escala {escala}")

    # --- Colchón armónico y sub ---
    for inicio, dur, grado in secciones:
        desplazamiento = grados[grado % len(grados)] + 12 * (grado // len(grados))
        fundamental = semitono(raiz, desplazamiento) / 2.0

        # Tríada tomada de la propia escala: nunca se sale del modo.
        idx = grados.index(grados[grado % len(grados)])
        notas = [grados[(idx + k) % len(grados)] + (12 if idx + k >= len(grados) else 0)
                 for k in (0, 2, 4)]
        voces = [semitono(raiz, n) for n in notas]

        i0 = int(inicio * FRECUENCIA)
        n = min(int(dur * FRECUENCIA), total - i0)
        fundido = int(min(8.0, dur / 3) * FRECUENCIA)

        for voz, frec in enumerate(voces):
            # Dos osciladores desafinados por voz: el batido lento entre ambos
            # es lo que da el "ancho" característico de un pad.
            for detune, pan in ((1.0, 0.0), (1.0015, 1.0)):
                paso = frec * detune * TAM_TABLA / FRECUENCIA
                fase = random.uniform(0, TAM_TABLA)
                # Cada voz respira a distinto ritmo: nunca se alinean.
                lfo_v = 0.05 + voz * 0.013
                g_izq = NIVEL_COLCHON * (1.0 - 0.35 * pan) / len(voces)
                g_der = NIVEL_COLCHON * (0.65 + 0.35 * pan) / len(voces)
                for i in range(n):
                    env = min(1.0, i / fundido, (n - i) / fundido)
                    resp = 0.82 + 0.18 * math.sin(2 * math.pi * lfo_v * i / FRECUENCIA)
                    v = tabla[int(fase) % TAM_TABLA] * env * resp
                    izq[i0 + i] += v * g_izq
                    der[i0 + i] += v * g_der
                    fase += paso

        # Sub: una sola onda senoidal grave que sostiene todo por debajo.
        paso_sub = fundamental * TAM_TABLA / FRECUENCIA
        fase = 0.0
        for i in range(n):
            env = min(1.0, i / fundido, (n - i) / fundido)
            v = math.sin(2 * math.pi * fase / TAM_TABLA) * env * NIVEL_SUB
            izq[i0 + i] += v
            der[i0 + i] += v
            fase += paso_sub

    # --- Campanas: eventos dispersos, nunca en rejilla regular ---
    t = random.uniform(8.0, 16.0)
    n_campanas = 0
    while t < segundos - 6.0:
        octava = random.choice([0, 0, 12, 12, 24])
        grado = random.choice(grados)
        frec = semitono(raiz, grado + octava)
        clave = round(frec, 1)
        if clave not in campanas:
            campanas[clave] = hacer_campana(frec)
        buf = campanas[clave]

        i0 = int(t * FRECUENCIA)
        pan = random.uniform(0.15, 0.85)
        vol = NIVEL_CAMPANA * random.uniform(0.5, 1.0)
        for i in range(min(len(buf), total - i0)):
            v = buf[i] * vol
            izq[i0 + i] += v * (1.0 - pan)
            der[i0 + i] += v * pan
        n_campanas += 1
        # Separación irregular: una rejilla regular suena a metrónomo.
        t += random.uniform(6.0, 15.0)

    print(f"  {n_campanas} campanas · {len(campanas)} timbres sintetizados")

    # --- Textura de fondo: ruido marrón muy bajo ---
    marron = 0.0
    for i in range(total):
        marron = (marron + 0.018 * random.uniform(-1, 1)) / 1.018
        v = marron * 3.2 * NIVEL_TEXTURA
        izq[i] += v
        der[i] += v * 0.92     # leve descorrelación estéreo: abre la imagen

    # --- Normalización y fundidos generales ---
    pico = max(max(abs(v) for v in izq), max(abs(v) for v in der)) or 1.0
    ganancia = 0.82 / pico
    fundido = int(6.0 * FRECUENCIA)

    muestras = array.array("h")
    for i in range(total):
        env = min(1.0, i / fundido, (total - i) / fundido)
        muestras.append(int(max(-1.0, min(1.0, izq[i] * ganancia * env)) * AMPLITUD))
        muestras.append(int(max(-1.0, min(1.0, der[i] * ganancia * env)) * AMPLITUD))

    with wave.open(ruta, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(FRECUENCIA)
        w.writeframes(muestras.tobytes())

    return len(secciones), n_campanas


def main():
    p = argparse.ArgumentParser(description="Compositor de música de meditación")
    p.add_argument("--minutos", type=float, default=1.0)
    p.add_argument("--raiz", default="528",
                   help="frecuencia raíz en Hz, o un nombre solfeggio (396…852)")
    p.add_argument("--escala", default="pentatonica", choices=list(ESCALAS))
    p.add_argument("--afinacion", type=float, default=None,
                   help="afinación de referencia La (432 o 440). Ignora --raiz")
    p.add_argument("--semilla", type=int, default=None)
    p.add_argument("--salida", default=None)
    p.add_argument("--listar", action="store_true")
    a = p.parse_args()

    if a.listar:
        print("Escalas:")
        for k, v in ESCALAS.items():
            print(f"  {k:14} {v}")
        print("\nFrecuencias solfeggio (afinación, no tratamiento):")
        for k, v in SOLFEGGIO.items():
            print(f"  {k:14} {v} Hz")
        print("\nAfinación de referencia: --afinacion 432 o 440")
        return

    if a.afinacion:
        raiz = a.afinacion / 2.0        # La grave como raíz
        etiqueta = f"la{int(a.afinacion)}"
    else:
        raiz = SOLFEGGIO.get(a.raiz, None) or float(a.raiz)
        etiqueta = a.raiz

    semilla = a.semilla if a.semilla is not None else random.randrange(1, 10 ** 6)
    ruta = a.salida or f"meditacion_{etiqueta}_{a.escala}_{semilla}.wav"

    print(f"Componiendo {a.minutos:g} min · raíz {raiz:.1f} Hz · semilla {semilla}")
    secciones, campanas = componer(ruta, a.minutos * 60, raiz, a.escala, semilla)
    print(f"{ruta}")
    print(f"Para repetir esta obra exacta: --semilla {semilla} "
          f"--raiz {etiqueta} --escala {a.escala}")


if __name__ == "__main__":
    main()
