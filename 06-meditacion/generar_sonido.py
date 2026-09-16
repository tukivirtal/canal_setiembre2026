#!/usr/bin/env python3
"""
Generador de sonido de meditación por síntesis procedural.

No usa muestras ni librerías de música: construye la onda desde cero, así que el
audio resultante es 100 % tuyo. Sin Content ID, sin reclamos, sin licencias.

Uso:
    python3 generar_sonido.py                          # demo de 30 s
    python3 generar_sonido.py --minutos 60             # una hora
    python3 generar_sonido.py --preset theta --minutos 20
    python3 generar_sonido.py --listar

Presets (el "beat" es la diferencia entre el tono del oído izquierdo y el derecho;
el cerebro percibe esa diferencia como un pulso. Requiere auriculares):

    delta  2 Hz   sueño profundo
    theta  4 Hz   meditación, relajación honda
    alpha  8 Hz   calma despierta, estudio
    drone  --     solo colchón armónico y ruido, sin pulso binaural
"""

import argparse
import array
import math
import random
import wave

FRECUENCIA = 44100          # muestras por segundo
AMPLITUD = 32767            # máximo de 16 bits

PRESETS = {
    "delta": {"base": 180.0, "beat": 2.0, "descripcion": "sueño profundo"},
    "theta": {"base": 200.0, "beat": 4.0, "descripcion": "meditación"},
    "alpha": {"base": 220.0, "beat": 8.0, "descripcion": "calma despierta"},
    "drone": {"base": 200.0, "beat": 0.0, "descripcion": "sin pulso binaural"},
}

# Mezcla. La suma de los tres debe quedar por debajo de 1.0 para no saturar.
NIVEL_BINAURAL = 0.12
NIVEL_RUIDO = 0.34
NIVEL_COLCHON = 0.16


def ruido_marron(anterior):
    """
    Ruido marrón: ruido blanco integrado, con fuga para que no derive.
    Suena a lluvia lejana en vez de a estática de televisor, porque concentra
    la energía en las frecuencias graves.
    """
    blanco = random.uniform(-1.0, 1.0)
    actual = (anterior + 0.018 * blanco) / 1.018
    return actual, actual * 3.2      # se reescala: la integración baja el nivel


def envolvente(i, total, muestras_fundido):
    """Fundido de entrada y de salida, para que nunca haya un corte seco."""
    if i < muestras_fundido:
        return i / muestras_fundido
    if i > total - muestras_fundido:
        return (total - i) / muestras_fundido
    return 1.0


def generar(ruta, segundos, base, beat, semilla=None):
    if semilla is not None:
        random.seed(semilla)

    total = int(segundos * FRECUENCIA)
    fundido = min(int(4.0 * FRECUENCIA), total // 2)
    muestras = array.array("h")

    # Frecuencias de cada oído: la diferencia es el pulso percibido.
    izq_hz = base - beat / 2.0
    der_hz = base + beat / 2.0

    # Colchón armónico: fundamental grave + su quinta justa.
    colchon_hz = base / 2.0
    quinta_hz = colchon_hz * 1.5

    paso = 2.0 * math.pi / FRECUENCIA
    marron = 0.0

    for i in range(total):
        t = i * paso
        env = envolvente(i, total, fundido)

        # Respiración lenta del volumen: un ciclo cada ~12 s. Evita que el
        # oído se acostumbre y deje de percibir el sonido.
        respiracion = 0.88 + 0.12 * math.sin(t / 12.0)

        marron, ruido = ruido_marron(marron)
        ruido *= NIVEL_RUIDO

        colchon = (math.sin(t * colchon_hz) * 0.6
                   + math.sin(t * quinta_hz) * 0.4) * NIVEL_COLCHON

        tono_izq = math.sin(t * izq_hz) * NIVEL_BINAURAL
        tono_der = math.sin(t * der_hz) * NIVEL_BINAURAL

        g = env * respiracion
        izq = max(-1.0, min(1.0, (tono_izq + ruido + colchon) * g))
        der = max(-1.0, min(1.0, (tono_der + ruido + colchon) * g))

        muestras.append(int(izq * AMPLITUD))
        muestras.append(int(der * AMPLITUD))

    with wave.open(ruta, "w") as w:
        w.setnchannels(2)         # estéreo: el binaural lo exige
        w.setsampwidth(2)         # 16 bits
        w.setframerate(FRECUENCIA)
        w.writeframes(muestras.tobytes())

    return total


def main():
    p = argparse.ArgumentParser(description="Generador de sonido de meditación")
    p.add_argument("--preset", default="theta", choices=list(PRESETS))
    p.add_argument("--minutos", type=float, default=0.5)
    p.add_argument("--salida", default=None)
    p.add_argument("--semilla", type=int, default=None,
                   help="fija el ruido, para poder regenerar el mismo audio")
    p.add_argument("--listar", action="store_true")
    a = p.parse_args()

    if a.listar:
        for nombre, cfg in PRESETS.items():
            beat = f'{cfg["beat"]:.0f} Hz' if cfg["beat"] else "sin pulso"
            print(f'  {nombre:8} {beat:10} {cfg["descripcion"]}')
        return

    cfg = PRESETS[a.preset]
    segundos = a.minutos * 60
    ruta = a.salida or f"meditacion_{a.preset}_{int(a.minutos)}min.wav"

    print(f'Generando {a.minutos:g} min · preset {a.preset} '
          f'({cfg["descripcion"]}) · pulso {cfg["beat"]:.0f} Hz')
    total = generar(ruta, segundos, cfg["base"], cfg["beat"], a.semilla)
    print(f"{ruta} · {total:,} muestras · {total * 4 / 1e6:.1f} MB")
    print("Escuchar con auriculares: el efecto binaural no existe en altavoces.")


if __name__ == "__main__":
    main()
