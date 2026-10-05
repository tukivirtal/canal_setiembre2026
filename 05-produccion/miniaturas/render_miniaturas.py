#!/usr/bin/env python3
"""
Miniaturas de YouTube (1280x720) para las obras del catálogo.

    python3 05-produccion/miniaturas/render_miniaturas.py              # las 40
    python3 05-produccion/miniaturas/render_miniaturas.py --muestra    # una por intención
    python3 05-produccion/miniaturas/render_miniaturas.py --id OBRA-001

La fórmula, tomada de lo que funciona en el nicho (Meditative Mind):
  - la frecuencia en letra enorme arriba
  - la intención en una palabra, en el color de la paleta
  - una pastilla con el ambiente y la duración
  - el mandala del video de fondo, con el color de su ambiente
  - la firma de Rin abajo a la izquierda

La miniatura se diseña para leerse a 160 px de ancho, que es como se ve en el
celular: por eso la letra es tan pesada y hay tan pocas palabras.

Salida: 05-produccion/miniaturas/export/<id>.jpg (menos de 2 MB, el límite de YouTube).
"""
import argparse, csv, pathlib, urllib.parse, os
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
# El Chromium de la sesión de Claude; en GitHub Actions no existe y se usa el
# que instala Playwright (executable_path=None).
_CH = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
CHROMIUM = os.environ.get('CHROMIUM') or (_CH if os.path.exists(_CH) else None)

PALABRA = {'Dormir': 'DEEP SLEEP', 'Ansiedad': 'CALM', 'Meditar': 'MEDITATION',
           'Soltar': 'RELEASE', 'Concentración': 'DEEP FOCUS'}
AMBIENTE = {'mar': 'Ocean Waves', 'mar-aves': 'Ocean & Birds', 'zen': 'Zen Temple',
            'selva': 'Tropical Rainforest', 'lluvia-tambor': 'Rain on Leaves',
            'jardin': 'Birds & Temple Bells', 'lluvia': 'Gentle Rain', 'theta': 'Headphones On', 'guqin': 'Guqin & Xiao',
            'marron': 'Brown Noise & Bells', 'delta': 'Headphones On'}
# Obras con la promesa en grande en vez de la frecuencia (como la variante D
# de la prueba del 29/09): la persona busca «dark screen sleep music», no «432 Hz».
PROMESA = {'OBRA-043': ('DARK SCREEN\nSLEEP MUSIC', '432 Hz'),
           'OBRA-044': ('THETA WAVES\nDEEP SLEEP', 'DARK SCREEN'),
           'OBRA-045': ('WOKE UP\nAT 3 AM?', 'FALL BACK ASLEEP'),
           'OBRA-046': ('3 AM\nRESET', 'FALL BACK ASLEEP'),
           'OBRA-047': ('5-MINUTE\nRESET', 'CALM ANXIETY FAST'),
           'OBRA-048': ('TEMPLE BELLS\nDEEP SLEEP', 'BLACK SCREEN'),
           'OBRA-049': ('STOP\nOVERTHINKING', '10 MINUTES'),
           'OBRA-050': ('BROWN NOISE\nDEEP SLEEP', 'BLACK SCREEN'),
           'OBRA-051': ('PINK NOISE\n+ DELTA WAVES', 'DEEP SLEEP')}


def duracion(m):
    m = int(m)
    if m >= 60 and m % 60 == 0:
        return f'{m // 60} Hour' + ('s' if m > 60 else '')
    return f'{m} Minutes'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--muestra', action='store_true', help='una miniatura por intención')
    p.add_argument('--id')
    a = p.parse_args()
    with open(RAIZ / '08-catalogo' / 'catalogo.csv', encoding='utf-8') as f:
        obras = list(csv.DictReader(f))
    if a.id:
        obras = [o for o in obras if o['id'] == a.id]
    elif a.muestra:
        vistas, sel = set(), []
        for o in obras:
            if o['tema'] not in vistas:
                vistas.add(o['tema']); sel.append(o)
        obras = sel
    salida = AQUI / 'export'; salida.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        pag = nav.new_page(viewport={'width': 1280, 'height': 720})
        for o in obras:
            q = urllib.parse.urlencode({
                'paleta': o['ambiente'], 'tono': o.get('tono') or 0,
                'grande': PROMESA.get(o['id'], (f"{o['raiz_hz']} Hz",))[0],
                'palabra': PROMESA.get(o['id'], (0, PALABRA[o['tema']]))[1],
                'pastilla': f"{AMBIENTE[o['ambiente']]} · {duracion(o['duracion_min'])}",
                # cada obra con un instante distinto del mandala: nunca dos portadas iguales
                't': int(o['semilla']) % 48})
            pag.goto(f"file://{AQUI / 'miniatura.html'}?{q}")
            pag.wait_for_timeout(700)
            destino = salida / f"{o['id']}.jpg"
            pag.query_selector('#m').screenshot(path=str(destino), type='jpeg', quality=90)
            print(f"{destino.name}  {destino.stat().st_size // 1024} KB  {o['titulo'][:60]}")
        nav.close()


if __name__ == '__main__':
    main()
