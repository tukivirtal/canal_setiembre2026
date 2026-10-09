#!/usr/bin/env python3
"""Textura de Rin para la web y las tarjetas: negro mate con vetas azul noche y oro.

Los colores salen del banner de YouTube (09-canal): el azul de los pétalos (#24486c)
y el oro del nombre (#e6c46a), sobre un negro mate con grano. Las vetas son mármol
con el dominio deformado por ruido fractal; las de oro aparecen solo en algunos
tramos, como una grieta reparada con oro.

Uso: python3 11-web/vetas.py --ancho 1080 --alto 1920 --semilla 7 --salida web/img/vetas-movil.webp
"""
import argparse

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

NEGRO = np.array([11, 12, 15], float)
NOCHE = np.array([20, 38, 60], float)
AZUL = np.array([36, 72, 108], float)
ORO = np.array([230, 196, 106], float)
ORO_SOMBRA = np.array([150, 118, 52], float)


def ruido(alto, ancho, rng, octavas, base, persistencia=0.5):
    """Ruido fractal suave, de media 0 y desvío 1."""
    total = np.zeros((alto, ancho), np.float32)
    amp, lado = 1.0, max(alto, ancho)
    for o in range(octavas):
        n = base * 2 ** o
        g = rng.standard_normal((max(2, int(n * alto / lado) + 3), max(2, int(n * ancho / lado) + 3)))
        total += amp * np.asarray(Image.fromarray(g.astype(np.float32), 'F').resize((ancho, alto), Image.BICUBIC))
        amp *= persistencia
    return (total - total.mean()) / total.std()


def suave(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def lineas(alto, ancho, rng, frec, angulo, deformacion, grosor, base=1.5, octavas=4):
    """Vetas de mármol: franjas que siguen una dirección, deformadas por ruido de baja frecuencia."""
    y, x = np.mgrid[0:alto, 0:ancho].astype(np.float32) / max(alto, ancho)
    u = x * np.cos(angulo) + y * np.sin(angulo)
    v = u * frec + deformacion * ruido(alto, ancho, rng, octavas, base, 0.45) \
        + 0.08 * deformacion * ruido(alto, ancho, rng, 3, base * 6)
    return np.exp(-np.abs(np.sin(np.pi * v)) / grosor)


def textura(ancho, alto, semilla, oro=1.0):
    rng = np.random.default_rng(semilla)
    img = np.broadcast_to(NEGRO, (alto, ancho, 3)).copy()
    escala = max(alto, ancho) / 1920

    def mezclar(color, alfa):
        img[:] = img * (1 - alfa[..., None]) + color * alfa[..., None]

    # Profundidad: nubes y bandas anchas de azul noche, como los pétalos translúcidos del banner.
    mezclar(NOCHE, 0.28 * suave(0.45 + 0.3 * ruido(alto, ancho, rng, 5, 1.2)))
    mezclar(AZUL, 0.16 * lineas(alto, ancho, rng, 1.1, 1.05, 0.6, 0.22, 1.2))
    mezclar(AZUL, 0.26 * lineas(alto, ancho, rng, 3.4, 0.85, 0.7, 0.02, 2.0)
            * suave(0.4 + 0.5 * ruido(alto, ancho, rng, 3, 1.5)))

    # Oro: dos o tres vetas principales y una red de grietas finas cerca de ellas.
    principal = lineas(alto, ancho, rng, 1.25, 0.95, 0.42, 0.009, 1.3, 3)
    principal *= suave(0.55 + 0.6 * ruido(alto, ancho, rng, 3, 1.2))
    cerca = gaussian_filter(principal, 45 * escala)
    cerca = suave(cerca / (cerca.max() + 1e-6) * 2.2)
    grietas = lineas(alto, ancho, rng, 6.0, 0.55, 1.0, 0.006, 3.0) * cerca
    hilo = np.clip(principal + 0.6 * grietas, 0, 1) * oro
    img[:] = img + ORO_SOMBRA * (0.45 * gaussian_filter(hilo, 5 * escala))[..., None]
    mezclar(ORO, np.clip(0.9 * hilo, 0, 1))

    # Mate: viñeta suave y grano.
    yy, xx = np.mgrid[0:alto, 0:ancho].astype(np.float32)
    r = np.hypot((xx - ancho / 2) / (ancho / 2), (yy - alto / 2) / (alto / 2))
    img *= (1 - 0.35 * suave((r - 0.55) / 0.9))[..., None]
    img += rng.normal(0, 2.2, (alto, ancho, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--ancho', type=int, default=1080)
    a.add_argument('--alto', type=int, default=1920)
    a.add_argument('--semilla', type=int, default=7)
    a.add_argument('--oro', type=float, default=1.0, help='cuánto oro: 0 lo apaga')
    a.add_argument('--salida', required=True)
    x = a.parse_args()
    im = textura(x.ancho, x.alto, x.semilla, x.oro)
    opciones = {'quality': 82, 'method': 6} if x.salida.endswith('.webp') else {}
    im.save(x.salida, **opciones)
    print(x.salida, im.size)
