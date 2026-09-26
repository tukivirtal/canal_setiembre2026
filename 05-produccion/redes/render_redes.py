#!/usr/bin/env python3
"""
Posts y reels para Instagram (y Facebook, los mismos) de las obras publicadas.

    python3 05-produccion/redes/render_redes.py OBRA-012 OBRA-015 OBRA-020

Deja en produccion/redes/:
    posts/NN-....jpg        1080x1350 (4:5), en el orden sugerido de publicación;
                            los carruseles, una imagen por diapositiva
    portadas/OBRA-XXX-SN.jpg  portada de cada reel (1080x1920, el texto en la
                            franja 4:5 que Instagram muestra en el perfil)
    textos.txt              el texto de cada post y de cada reel, con hashtags

Los reels son los mismos Shorts (short-<n>.mp4 de calidad completa). Los colores
salen de la obra: paleta de su ambiente y su tono, como el video largo.
"""
import csv, pathlib, sys, urllib.parse, os
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parents[2]
AQUI = pathlib.Path(__file__).resolve().parent
_CH = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
CHROMIUM = os.environ.get('CHROMIUM') or (_CH if os.path.exists(_CH) else None)

PALABRA = {'Dormir': 'DEEP SLEEP', 'Ansiedad': 'CALM', 'Meditar': 'MEDITATION',
           'Soltar': 'RELEASE', 'Concentración': 'DEEP FOCUS'}
PROPOSITO = {'Dormir': 'For the hour before sleep.', 'Ansiedad': "For when your mind won't stop.",
             'Meditar': 'For a quiet meditation.', 'Soltar': "To let go of the day.",
             'Concentración': 'For deep, quiet work.'}
TAGS = {'Dormir': ['#sleepmusic', '#deepsleep'], 'Ansiedad': ['#anxietyrelief', '#calm'],
        'Meditar': ['#meditationmusic', '#mindfulness'], 'Soltar': ['#stressrelief', '#relaxingmusic'],
        'Concentración': ['#focusmusic', '#studymusic']}


def etiquetas(*grupos):
    """Instagram admite hasta 5 hashtags por publicación: sin repetir, en minúscula."""
    return ' '.join(list(dict.fromkeys(t for g in grupos for t in g))[:5]).lower()


def dur_txt(minutos):
    m = int(minutos)
    return f'{m // 60} h' if m >= 60 and m % 60 == 0 else f'{m} min'


# Los carruseles. Cada uno: paleta y tono del fondo, diapositivas (título, cuerpo)
# y el texto que acompaña.
CARRUSELES = [
    ('respirar', 'mar-aves', 0, [
        ('Breathe with the music', 'A 45-second practice. Swipe.'),
        ('Breathe in for 4', 'Slowly, through the nose.'),
        ('Breathe out for 6', 'Longer out than in. That is the whole trick.'),
        ('Let the music lead', 'Every Rin piece slows from 6 to 4.5 breaths per minute. Follow it.'),
        ('Lights low, volume low', 'Full pieces on YouTube. Link in bio.'),
    ], 'A simple way to use any Rin piece: breathe out longer than you breathe in, and let the music set '
       'the pace. It slows down on its own, from 6 to 4.5 breaths per minute.\n\nSave this for tonight.',
       ['#breathwork', '#meditation', '#calm', '#meditationmusic', '#relaxingmusic']),
    ('como-se-hace', 'lluvia-tambor', 0, [
        ('Composed, not assembled', 'How a Rin piece is made.'),
        ('One intention', 'Every piece is written for one moment: sleep, calm, meditation, release or focus.'),
        ('One root note', 'Tuned in just intonation around a root: 396, 432, 528, 639 Hz…'),
        ('The breath is written in', 'The music slows from 6 to 4.5 breaths per minute, 40 % in and 60 % out.'),
        ('Nothing borrowed', 'Ocean, birds, rain and bells are synthesized too. No samples. New pieces every week.'),
    ], 'Rin writes every piece from scratch: one intention, one root note, and a breathing cycle built into '
       'the music. The ocean, the birds and the rain are synthesized too.\n\nNew pieces every week on YouTube. '
       'Link in bio.',
       ['#meditationmusic', '#ambientmusic', '#relaxingmusic', '#justintonation']),
    ('una-nota-honesta', 'zen', 0, [
        ('An honest note about Hz', 'What 528 Hz is, and what it is not.'),
        ('It is a pitch', 'The note a piece is built on. We choose it for its color, like a painter chooses a light.'),
        ('It does not heal', 'No frequency repairs DNA or cures anything. We will never promise that.'),
        ('What music can do', 'Give your breath a slower pace to follow. That is what Rin is for.'),
    ], 'You will see a lot of promises about frequencies. Here is ours: the Hz is the note the piece is built '
       'on, chosen for its color. What the music can do is give your breath a slower pace to follow.',
       ['#528hz', '#meditationmusic', '#mindfulness', '#calm', '#relaxingmusic']),
]
FRASES = [
    ('you can put it down for now', 'zen', 0),
    ('let the day go quiet', 'mar', 110),
    ('breathe out longer than you breathe in', 'mar-aves', 0),
    ('nothing to do but listen', 'lluvia-tambor', 0),
    ('the day is over', 'mar', 0),
    ('one breath, then the next', 'selva', 0),
]


def main():
    ids = sys.argv[1:]
    cat = {o['id']: o for o in csv.DictReader(open(RAIZ / '08-catalogo/catalogo.csv', encoding='utf-8'))}
    shorts = [s for s in csv.DictReader(open(RAIZ / '08-catalogo/shorts.csv', encoding='utf-8')) if s['obra'] in ids]
    out = RAIZ / 'produccion' / 'redes'
    (out / 'posts').mkdir(parents=True, exist_ok=True)
    (out / 'portadas').mkdir(parents=True, exist_ok=True)

    # El calendario del feed: pieza nueva, carrusel y frase, alternados.
    piezas = [('pieza', i) for i in reversed(ids)]
    carr = [('carrusel', c) for c in CARRUSELES]
    fr = [('frase', f) for f in FRASES]
    orden = []
    while piezas or carr or fr:
        for lista in (piezas, carr, fr):
            if lista:
                orden.append(lista.pop(0))

    textos = ['POSTS DEL FEED (Instagram y Facebook, en este orden; uno por día)\n']
    trabajos = []                                  # (url, destino, alto)
    for k, (tipo, x) in enumerate(orden, 1):
        if tipo == 'pieza':
            o = cat[x]
            partes = o['titulo'].split(' · ')
            q = {'tipo': 'pieza', 'paleta': o['ambiente'], 'tono': o['tono'], 't': int(o['semilla']) % 48,
                 'hz': o['raiz_hz'], 'palabra': PALABRA[o['tema']], 'nombre': partes[3],
                 'pastilla': f"{partes[1]} · {dur_txt(o['duracion_min'])}"}
            nombre = f'{k:02d}-nueva-{x}.jpg'
            trabajos.append((q, out / 'posts' / nombre, False))
            txt = (f"New piece: {partes[3]}. {PROPOSITO[o['tema']]}\n"
                   f"{partes[1]}, {o['raiz_hz']} Hz, {dur_txt(o['duracion_min'])}. Composed from scratch, no samples.\n"
                   f"Full piece on YouTube. Link in bio.\n\n"
                   + etiquetas(TAGS[o['tema']], [f"#{o['raiz_hz']}hz", '#meditationmusic', '#relaxingmusic']))
            textos.append(f'\n---------- {k:02d} · POST: pieza nueva ({x}) · {nombre}\n{txt}\n')
        elif tipo == 'carrusel':
            clave, pal, tono, slides, cap, tags = x
            nombres = []
            for j, (tit, cuerpo) in enumerate(slides, 1):
                q = {'tipo': 'slide', 'paleta': pal, 'tono': tono, 't': 6 + j * 7, 'num': j,
                     'total': len(slides), 'titulo': tit, 'cuerpo': cuerpo}
                nombre = f'{k:02d}-carrusel-{clave}-{j}.jpg'
                nombres.append(nombre)
                trabajos.append((q, out / 'posts' / nombre, False))
            textos.append(f'\n---------- {k:02d} · CARRUSEL: {clave} · {len(slides)} imágenes '
                          f'({nombres[0]} … {nombres[-1]})\n{cap}\n\n{etiquetas(tags)}\n')
        else:
            frase, pal, tono = x
            q = {'tipo': 'frase', 'paleta': pal, 'tono': tono, 't': 20, 'texto': frase}
            nombre = f'{k:02d}-frase.jpg'
            trabajos.append((q, out / 'posts' / nombre, False))
            txt = (f"{frase[0].upper()}{frase[1:]}.\nSave it for the moment you need it.\n\n"
                   + etiquetas(['#meditation', '#calm', '#mindfulness', '#meditationmusic', '#relaxingmusic']))
            textos.append(f'\n---------- {k:02d} · POST: frase · {nombre}\n{txt}\n')

    textos.append('\n\nREELS (los mismos Shorts, archivo de calidad completa; 1 o 2 por día)\n')
    for s in shorts:
        o = cat[s['obra']]
        palabra = s['tiktok_portada'].split(' · ')[1].upper()
        q = {'tipo': 'portada', 'paleta': o['ambiente'], 'tono': o['tono'], 't': float(s['desfase_s']),
             'hz': o['raiz_hz'], 'palabra': palabra}
        nombre = f"{s['id_short']}.jpg"
        trabajos.append((q, out / 'portadas' / nombre, True))
        leyenda = s['tiktok_descripcion'].split(' Full ')[0]
        tags = [t for t in s['tiktok_descripcion'].split() if t.startswith('#')]
        txt = (f"{leyenda}\nFull {dur_txt(o['duracion_min'])} piece on YouTube. Link in bio.\n\n{etiquetas(tags)}")
        textos.append(f"\n---------- REEL {s['id_short']} · video short-{s['n']}.mp4 · portada {nombre}\n{txt}\n")

    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        pag = nav.new_page(viewport={'width': 1080, 'height': 1920})
        for q, destino, alto in trabajos:
            pag.goto(f"file://{AQUI / 'pieza.html'}?{urllib.parse.urlencode(q)}")
            pag.wait_for_timeout(600)
            pag.query_selector('#m').screenshot(path=str(destino), type='jpeg', quality=90)
        nav.close()
    (out / 'textos.txt').write_text(''.join(textos), encoding='utf-8')
    print(f'{len(trabajos)} imágenes en {out.relative_to(RAIZ)}')


if __name__ == '__main__':
    main()
