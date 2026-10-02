#!/usr/bin/env python3
"""
Carruseles de fotos para TikTok (1080x1920), con el mandala de fondo:

    python3 05-produccion/redes/render_tiktok.py

Deja en produccion/redes/tiktok/<carrusel>/NN.jpg y textos.txt con la
descripción de cada uno. En TikTok: + → Foto → elegir las imágenes en orden.
"""
import pathlib, urllib.parse, os
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parents[2]
AQUI = pathlib.Path(__file__).resolve().parent
_CH = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
CHROMIUM = os.environ.get('CHROMIUM') or (_CH if os.path.exists(_CH) else None)

# (etiqueta, título, cuerpo, paleta, tono)
CARRUSELES = {
    # 02/10: el reloj chino del cuerpo (tendencia «Chinamaxxing»). Termina en una
    # pregunta fácil de contestar: los comentarios son lo que más empuja en TikTok.
    '3am': ([
        ('SAVE THIS FOR TONIGHT', 'Why you wake up at 3 AM', 'The Chinese body clock has an answer. Swipe →', 'zen', 165),
        ('THE CHINESE BODY CLOCK', 'Every two hours, one organ', '11 PM – 1 AM · gallbladder\n1 – 3 AM · liver\n3 – 5 AM · lungs', 'zen', 165),
        ('1 – 3 AM · LIVER', 'The hour of what you couldn’t let go of', 'In Chinese medicine the liver holds stress and frustration. At night, it speaks up.', 'zen', 165),
        ('WHAT TO DO', 'Don’t check the time', 'Phone face down. Stay in bed. Eyes closed.', 'zen', 165),
        ('XŪ · THE LIVER SOUND', 'Breathe out through your lips: shhh', 'From the Six Healing Sounds (Liu Zi Jue). Six slow breaths, longer out than in.', 'zen', 165),
        ('RIN', 'Then let slow music carry you back', '3-hour sleep pieces with a dark screen, composed from scratch. On YouTube.', 'zen', 165),
    ], """Why you wake up at 3 AM 🌙 The Chinese body clock says 1 to 3 AM is the liver's hour: the hour of what you couldn't let go of.
Don't check the time. Breathe out through your lips, "shhh" (xū), six times. Then let slow music carry you back.
A 2,000-year-old tradition, not medical advice.
What time do you usually wake up: 1, 3 or 5 AM? 👇

#chinamaxxing #chinesemedicine #3am #cantsleep #sleeptok"""),
    'reset-60s': ([
        ('SAVE THIS FOR TONIGHT', 'A 60-second reset for when your mind won’t stop', 'No app. Just your breath. Swipe →', 'mar-aves', 0),
        ('STEP 1', 'Drop your shoulders', 'Unclench your jaw. Let your tongue rest.', 'mar-aves', 0),
        ('STEP 2', 'Breathe in for 4', 'Slowly, through the nose.', 'mar-aves', 0),
        ('STEP 3', 'Breathe out for 6', 'Longer out than in. That is the whole trick.', 'mar-aves', 0),
        ('STEP 4', 'Six rounds', 'That is one minute. Notice what changed.', 'mar-aves', 0),
        ('RIN', 'Music that breathes at this pace', 'Every piece slows from 6 to 4.5 breaths per minute. Full pieces on YouTube.', 'mar-aves', 0),
    ], """A 60-second reset for when your mind won't stop 🌙
Longer out than in. Save it for tonight.

Full pieces on YouTube, link in bio.

#nervoussystemreset #breathwork #anxietyrelief #sleeptok #meditationmusic"""),
    'elige-mandala': ([
        ('PICK ONE', 'Pick a mandala. It picks tonight’s music.', 'Swipe, choose, comment your number.', 'zen', 0),
        ('N° 1 · 639 Hz', 'Ocean and Birds', 'For a mind that won’t stop. 15 min.', 'mar-aves', 0),
        ('N° 2 · 528 Hz', 'Zen Temple', 'For a brief pause in the day. 10 min.', 'zen', 0),
        ('N° 3 · 528 Hz', 'Rain on Leaves', 'For a quiet sit. 30 min.', 'lluvia-tambor', 0),
        ('N° 4 · 417 Hz', 'Ocean Waves', 'For the hour before sleep. 90 min.', 'mar', 0),
        ('YOUR NUMBER?', 'Tell me in the comments', 'Every piece is composed from scratch. Full pieces on YouTube.', 'selva', 0),
    ], """Pick a mandala 1, 2, 3 or 4. It picks your music tonight 🌙
Comment your number 👇

Full pieces on YouTube, link in bio.

#pickone #meditationmusic #sleeptok #528hz #aesthetic"""),
    'mision': ([
        (None, 'Some music fills the silence. Rin makes room for it.', '', 'mar', 0),
        (None, 'Every piece is composed from scratch, for one moment of your day.', '', 'mar-aves', 0),
        (None, 'It slows down, breath by breath, until you do too.', '', 'zen', 0),
    ], """Rin is original meditation music, made for the real moments of your day 🌙
Every piece is composed from scratch: one intention, one root note, no samples.
The breath is written into the music. It slows from 6 to 4.5 breaths per minute.
You don't have to do anything. Just press play and let it lead.
For sleep, for anxiety, for a quiet meditation, for letting go of the day.
No miracle promises. Just music that gives your breath a slower pace to follow.
Full pieces on YouTube, link in bio.
Which moment do you need music for tonight? 👇

#meditationmusic #sleepmusic #anxietyrelief #calm #relaxingmusic"""),
}


def main():
    out = RAIZ / 'produccion' / 'redes' / 'tiktok'
    textos = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        pag = nav.new_page(viewport={'width': 1080, 'height': 1920})
        import sys
        solo = sys.argv[1:]                        # p. ej. «3am»: solo ese carrusel
        for clave, (slides, cap) in CARRUSELES.items():
            if solo and clave not in solo:
                continue
            (out / clave).mkdir(parents=True, exist_ok=True)
            for j, (et, tit, cuerpo, pal, tono) in enumerate(slides, 1):
                q = {'tipo': 'slide', 'tiktok': 1, 'paleta': pal, 'tono': tono, 't': 4 + j * 7,
                     'etiqueta': et, 'titulo': tit, 'cuerpo': cuerpo}
                if et is None:                     # sin etiqueta: una frase sola
                    q = {'tipo': 'frase', 'tiktok': 1, 'paleta': pal, 'tono': tono, 't': 4 + j * 7, 'texto': tit}
                pag.goto(f"file://{AQUI / 'pieza.html'}?{urllib.parse.urlencode(q)}")
                pag.wait_for_timeout(700)
                pag.query_selector('#m').screenshot(path=str(out / clave / f'{j:02d}.jpg'), type='jpeg', quality=90)
            textos.append(f'---------- {clave} · {len(slides)} fotos\n{cap}\n\n')
        nav.close()
    (out / 'textos.txt').write_text(''.join(textos), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
