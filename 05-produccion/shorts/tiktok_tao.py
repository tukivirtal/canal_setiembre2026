#!/usr/bin/env python3
"""
Videos verticales solo para TikTok: un audio, el mandala vertical de su color,
un gancho en el primer segundo y unos pocos textos que entran y salen.

    python3 05-produccion/shorts/tiktok_tao.py                 # «Two minutes of stillness»
    python3 05-produccion/shorts/tiktok_tao.py --pieza pensar   # «Stop overthinking» (OBRA-041)
    python3 05-produccion/shorts/tiktok_tao.py --pieza nervios  # «Calm your nervous system», 3 min de OBRA-042
    python3 05-produccion/shorts/tiktok_tao.py --pieza lluvia   # «Can't sleep?», 3 min de OBRA-043
    python3 05-produccion/shorts/tiktok_tao.py --pieza theta    # «Put your headphones on», 3 min de OBRA-044
    python3 05-produccion/shorts/tiktok_tao.py --pieza 3am      # «Woke up at 3 AM again?», guqin en modo yu

tao: guqin, xiao y lluvia (03-composicion/tao.py) sobre el mandala jade, con dos
líneas del Tao Te Ching (traducción propia; el original es de dominio público).
pensar: 75 s de OBRA-041, pájaros y campanas del templo.

Deja en produccion/tiktok-<pieza>/: <pieza>-tiktok.mp4 (bajo 30 MB) y textos.txt.
"""
import argparse, pathlib, subprocess, sys, tempfile, urllib.parse, os
from playwright.sync_api import sync_playwright
from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parents[2]
AQUI = pathlib.Path(__file__).resolve().parent
_CH = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
CHROMIUM = os.environ.get('CHROMIUM') or (_CH if os.path.exists(_CH) else None)
BUCLES = RAIZ / '05-produccion/fondo-mandala/bucles'

# (desde, hasta, parámetros del texto)
TEXTOS_TAO = [
    (0.0, 7.0, {'tipo': 'gancho', 'titulo': 'Two minutes of stillness',
                'sub': 'Headphones on. Let the strings breathe for you.'}),
    (9.0, 30.0, {'titulo': 'Breathe out when the strings play',
                 'sub': 'The music slows your breath, little by little.'}),
    (34.0, 56.0, {'titulo': 'The highest good is like water.', 'fuente': 'TAO TE CHING · 8'}),
    (60.0, 82.0, {'titulo': 'It nourishes all things and does not compete.', 'fuente': 'TAO TE CHING · 8'}),
    (86.0, 106.0, {'titulo': 'Muddy water, left still, slowly clears.', 'fuente': 'TAO TE CHING · 15'}),
    (109.0, 120.0, {'tipo': 'fin', 'titulo': 'Full pieces on YouTube',
                    'sub': 'Rin · original music, composed from scratch. Guqin, xiao and rain, tuned to 432 Hz.'}),
]

TEXTO_TAO = """Two minutes of stillness 🌙 Guqin, xiao flute and soft rain.
Headphones on. Breathe out when the strings play.
"The highest good is like water." Tao Te Ching
Composed from scratch by Rin, no samples. Tuned to 432 Hz.
Full pieces on YouTube, link in bio.

#taoism #guqin #meditationmusic #zenmusic #calm"""

TEXTOS_PENSAR = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Stop overthinking',
                'sub': 'Birdsong, temple bells and a slower breath.'}),
    (8.0, 26.0, {'titulo': 'Breathe out longer than you breathe in',
                 'sub': 'The music slows down with you.'}),
    (30.0, 50.0, {'titulo': "You don't have to solve it tonight."}),
    (53.0, 66.0, {'titulo': 'Just listen. The birds are not in a hurry.'}),
    (67.5, 75.0, {'tipo': 'fin', 'titulo': 'The full hour is on YouTube',
                  'sub': 'Rin · original music, composed from scratch. 432 Hz.'}),
]
TEXTO_PENSAR = """Stop overthinking 🌿 Birdsong, soft temple bells and a slower breath.
Breathe out longer than you breathe in, and let the music lead.
You don't have to solve it tonight. Just listen.
Original music composed from scratch by Rin, no samples. Tuned to 432 Hz.
The full hour is on YouTube, link in bio.

#stopoverthinking #anxietyrelief #nervoussystem #birdsong #432hz"""

TEXTOS_NERVIOS = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Calm your nervous system',
                'sub': '3 minutes. Zen temple bells and a slower breath.'}),
    (8.0, 40.0, {'titulo': 'Breathe out longer than you breathe in',
                 'sub': 'The music slows down. Let your body follow.'}),
    (48.0, 82.0, {'titulo': 'Unclench your jaw. Drop your shoulders.'}),
    (92.0, 126.0, {'titulo': 'Nothing to fix right now. Just this breath.'}),
    (136.0, 168.0, {'titulo': 'Stay a little longer.', 'sub': 'Your breath already slowed down.'}),
    (171.0, 180.0, {'tipo': 'fin', 'titulo': 'The full 3 hours are on YouTube',
                    'sub': 'Rin · original music, composed from scratch. 528 Hz.'}),
]
TEXTO_NERVIOS = """Calm your nervous system 🌿 3 minutes of zen temple bells and a slower breath.
Breathe out longer than you breathe in. Unclench your jaw, drop your shoulders.
Nothing to fix right now. Just this breath.
Original music composed from scratch by Rin, no samples. Tuned to 528 Hz.
The full 3 hours are on YouTube, link in bio.

#calmyournervoussystem #nervoussystemregulation #anxietyrelief #zenmusic #528hz"""

TEXTOS_LLUVIA = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': "Can't sleep?",
                'sub': '3 minutes of gentle rain. Lights off, volume low.'}),
    (8.0, 40.0, {'titulo': 'Breathe out longer than you breathe in',
                 'sub': 'The music slows down. Let your breath follow it.'}),
    (48.0, 82.0, {'titulo': 'Let your jaw soften. Let the pillow hold your head.'}),
    (92.0, 126.0, {'titulo': "Tomorrow can wait. You don't have to think now."}),
    (136.0, 168.0, {'titulo': 'Just the rain.', 'sub': 'Nothing else to do tonight.'}),
    (171.0, 180.0, {'tipo': 'fin', 'titulo': '3 hours, dark screen, on YouTube',
                    'sub': 'Rin · original music, composed from scratch. 432 Hz.'}),
]
TEXTO_LLUVIA = """Can't sleep? 🌙 3 minutes of gentle rain and a slow, warm drone.
Lights off, volume low. Breathe out longer than you breathe in.
Tomorrow can wait. Just the rain.
Original music composed from scratch by Rin, no samples. Tuned to 432 Hz.
The full 3 hours, with a dark screen for sleep, are on YouTube. Link in bio.

#sleepmusic #rainsounds #cantsleep #darkscreen #432hz"""

TEXTOS_THETA = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Put your headphones on',
                'sub': 'Theta waves for sleep. Each ear hears a different tone.'}),
    (8.0, 40.0, {'titulo': 'Breathe out longer than you breathe in',
                 'sub': 'The difference between your ears is slowing down.'}),
    (48.0, 82.0, {'titulo': 'Unclench your jaw. Let the pillow hold you.'}),
    (92.0, 126.0, {'titulo': 'Let the thought go. It will be there tomorrow.'}),
    (136.0, 168.0, {'titulo': 'Close your eyes.', 'sub': 'Just the ocean, far away.'}),
    (171.0, 180.0, {'tipo': 'fin', 'titulo': '3 hours, dark screen, on YouTube',
                    'sub': 'Rin · original music, composed from scratch. Theta to delta waves.'}),
]
TEXTO_THETA = """Put your headphones on 🎧 Theta waves for deep sleep, over a distant ocean.
Use headphones for the best experience: each ear hears a slightly different tone, and the difference slows you down.
Unclench your jaw. Let the thought go, it will be there tomorrow.
Original music composed from scratch by Rin, no samples.
The full 3 hours, with a dark screen for sleep, are on YouTube. Link in bio.

#thetawaves #binauralbeats #sleepmusic #darkscreen #cantsleep"""

# 02/10: dolor -> solución -> música. El dolor: despertarse a las 3 AM. La
# solución viene del «Chinamaxxing» (la tendencia de 2026 de vivir «a la china»:
# acostarse temprano, qigong, medicina china): en el reloj chino del cuerpo, de 1
# a 3 es la hora del hígado, y el sonido del hígado en los Seis Sonidos (Liu Zi
# Jue) es «xū», una exhalación larga. Se dice como tradición, no como diagnóstico.
TEXTOS_3AM = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Woke up at 3 AM again?',
                'sub': 'Chinese medicine has a name for this hour.'}),
    (8.0, 27.0, {'titulo': '1 to 3 AM is the liver\'s hour',
                 'sub': 'The hour of what you couldn\'t let go of.', 'fuente': 'THE CHINESE BODY CLOCK'}),
    (30.0, 47.0, {'titulo': 'Don\'t check the time.',
                  'sub': 'Knowing it\'s 3:12 only wakes you up more.'}),
    (50.0, 72.0, {'titulo': 'Breathe out through your lips: shhh',
                  'sub': 'Six slow breaths, longer out than in.', 'fuente': 'XŪ · THE LIVER SOUND'}),
    (75.0, 83.0, {'titulo': 'Let the strings take it from here.'}),
    (84.0, 90.0, {'tipo': 'fin', 'titulo': 'Save this for 3 AM',
                  'sub': 'Rin · guqin and rain in the Chinese yu scale, the scale of night. Composed from scratch.'}),
]
TEXTO_3AM = """Woke up at 3 AM again? 🌙 In the Chinese body clock, 1 to 3 AM is the liver's hour: the hour of what you couldn't let go of.
Don't check the time. Breathe out slowly through your lips, "shhh" (xū, the liver sound of the Six Healing Sounds). Six times, longer out than in.
Guqin, xiao flute and rain in the yu scale, the one Chinese tradition saves for the night. Composed from scratch by Rin.
A 2,000-year-old tradition, not medical advice.
Full 3-hour sleep pieces on YouTube, link in bio. What time do you wake up? 👇

#chinamaxxing #chinesemedicine #3am #cantsleep #sleeptok"""

# 04/10: lo que mejor funcionó en los datos: las campanas del templo zen (los
# Shorts más vistos y los únicos dos suscriptores) y «Breathe out longer than
# you breathe in» (el Short n.° 1). El gancho nombra el cuerpo: «tenés los
# hombros arriba» hace que la persona se revise y se quede.
TEXTOS_EXHALA = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Your shoulders are up. Drop them.',
                'sub': '90 seconds. Zen temple bells. Just breathe.'}),
    (8.0, 28.0, {'titulo': 'Breathe out longer than you breathe in',
                 'sub': 'In for 4. Out for 6.'}),
    (31.0, 50.0, {'titulo': 'Unclench your jaw.', 'sub': 'Let your tongue rest. Soften your hands.'}),
    (53.0, 72.0, {'titulo': 'In for 4. Out for 6.', 'sub': 'Stay with the bells a little longer.'}),
    (75.0, 84.0, {'titulo': 'Notice what changed.'}),
    (85.0, 90.0, {'tipo': 'fin', 'titulo': 'Save this for the next hard moment',
                  'sub': 'Rin · zen temple bells, 528 Hz. Composed from scratch. Full pieces on YouTube.'}),
]
TEXTO_EXHALA = """Your shoulders are up. Drop them 🌿 90 seconds of zen temple bells.
Breathe out longer than you breathe in: in for 4, out for 6. Unclench your jaw.
Notice what changed.
Original music composed from scratch by Rin, no samples. 528 Hz.
Save this for the next hard moment. Full pieces on YouTube, link in bio.

#nervoussystemreset #anxietyrelief #breathwork #zen #528hz"""

# 04/10: historias de TikTok (15 s, desaparecen en 24 h). Una avisa el estreno
# de la noche; la otra pregunta y se responde con A o B (la caja de respuesta
# de la historia), así la gente escribe y TikTok la muestra a más. Sin emojis en
# la imagen: el Chromium del render no tiene la fuente.
TEXTOS_HIST_THETA = [
    (0.0, 5.0, {'tipo': 'gancho', 'titulo': 'New tonight', 'sub': '3 hours of theta waves for deep sleep.'}),
    (5.5, 10.5, {'titulo': 'Put your headphones on', 'sub': 'Each ear hears a slightly different tone.'}),
    (11.0, 15.0, {'tipo': 'fin', 'titulo': 'Tonight on YouTube', 'sub': 'Rin · dark screen, 3 hours. Link in bio.'}),
]
TEXTO_HIST_THETA = "New tonight 🌙 3 hours of theta waves for deep sleep. Headphones on 🎧 Link in bio."

TEXTOS_HIST_3AM = [
    (0.0, 4.5, {'tipo': 'gancho', 'titulo': 'Be honest', 'sub': 'What keeps you awake at night?'}),
    (5.0, 10.5, {'titulo': 'Thoughts, or 3 AM?', 'sub': 'A · my thoughts won\'t stop\nB · I wake up at 3 AM', 'fuente': 'REPLY A OR B'}),
    (11.0, 15.0, {'tipo': 'fin', 'titulo': 'Tomorrow: 3 AM Reset', 'sub': 'Rin · 10 minutes of guqin and rain to fall back asleep.'}),
]
TEXTO_HIST_3AM = "A or B? 👇 Tomorrow's piece is for the 3 AM ones."

# 04/10: historias para fijar en el perfil (quedan, no hablan de «esta noche»):
# imagen en movimiento y una sola frase. La zen es del Zenrin Kushu (antología
# de dichos zen del siglo XV); la de Marco Aurelio es traducción propia de las
# Meditaciones 4.3 (el griego es de dominio público).
TEXTOS_HIST_ZEN = [
    (0.6, 15.0, {'titulo': 'Sitting quietly, doing nothing, spring comes, and the grass grows by itself.',
                 'fuente': 'ZEN SAYING · ZENRIN KUSHU'}),
]
TEXTO_HIST_ZEN = "Sitting quietly, doing nothing, spring comes, and the grass grows by itself. 🌿"

TEXTOS_HIST_MARCO = [
    (0.6, 15.0, {'titulo': 'Nowhere can you retreat to a quieter place than your own mind.',
                 'fuente': 'MARCUS AURELIUS · MEDITATIONS 4.3'}),
]
TEXTO_HIST_MARCO = "Nowhere can you retreat to a quieter place than your own mind. Marcus Aurelius 🌙"

# La tercera fijada: Tao Te Ching 15, traducción propia (dominio público), con
# el guqin en modo yu y el mandala violeta.
TEXTOS_HIST_TAO = [
    (0.6, 15.0, {'titulo': 'Muddy water, left still, slowly clears.', 'fuente': 'TAO TE CHING · 15'}),
]
TEXTO_HIST_TAO = "Muddy water, left still, slowly clears. Tao Te Ching 🌙"

# 04/10: TikTok acepta subir videos de hasta 60 min (10 min seguro en todas las
# cuentas). El 3 AM Reset entero (OBRA-046), en vertical: textos solo al
# principio, después nada que lea, para dormirse con el teléfono boca abajo.
TEXTOS_RESET10 = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Woke up at 3 AM?',
                'sub': '10 minutes of guqin and rain to fall back asleep.'}),
    (8.0, 30.0, {'titulo': "Don't check the time.", 'sub': 'Phone face down. Volume low.'}),
    (34.0, 70.0, {'titulo': 'Breathe out through your lips: shhh',
                  'sub': 'Six slow breaths, longer out than in.'}),
    (76.0, 110.0, {'titulo': 'Let the strings take it from here.'}),
    (592.0, 600.0, {'tipo': 'fin', 'titulo': 'Sleep well',
                    'sub': 'Rin · the full 3 hours, dark screen, are on YouTube.'}),
]
TEXTO_RESET10 = """Woke up at 3 AM? 🌙 10 minutes of guqin, xiao flute and rain to fall back asleep.
Don't check the time. Phone face down, volume low. Breathe out through your lips, "shhh", six times.
Original music composed from scratch by Rin, in the Chinese yu scale, the scale of night.
The full 3 hours, with a dark screen, are on YouTube. Link in bio.

#sleepmusic #3am #cantsleep #guqin #fallasleepfast"""

# 04/10: ruidos de color, lo más buscado para dormir (01-nicho/tendencias-sonidos-
# 2026-10.md). El título dice exactamente qué es: ruido marrón con campanas
# lejanas; ruido rosa con ondas delta.
TEXTOS_MARRON = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Brown noise for deep sleep',
                'sub': 'The sound millions fall asleep to. With distant temple bells.'}),
    (8.0, 40.0, {'titulo': 'Low, warm and steady', 'sub': 'Like heavy rain on a faraway roof.'}),
    (48.0, 85.0, {'titulo': 'Nothing to listen for.', 'sub': 'No beat, no melody to follow. Just let it cover the noise.'}),
    (95.0, 130.0, {'titulo': 'Lights off. Volume low.'}),
    (172.0, 180.0, {'tipo': 'fin', 'titulo': '3 hours, black screen, on YouTube',
                    'sub': 'Rin · brown noise and temple bells, composed from scratch.'}),
]
TEXTO_MARRON = """Brown noise for deep sleep 🌙 The sound millions fall asleep to, with distant temple bells.
Low, warm and steady, like heavy rain on a faraway roof. No beat, nothing to follow.
Lights off, volume low. Save it for tonight.
Composed from scratch by Rin, no samples. The full 3 hours, black screen, on YouTube. Link in bio.

#brownnoise #sleepsounds #deepsleep #cantsleep #sleeptok"""

TEXTOS_DELTA = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Pink noise + delta waves',
                'sub': 'For deep sleep. Headphones on.'}),
    (8.0, 40.0, {'titulo': 'Pink noise: soft and even', 'sub': 'Like steady rain. It covers what keeps you awake.'}),
    (48.0, 85.0, {'titulo': 'Delta waves: 2 Hz', 'sub': 'Each ear hears a slightly different tone. The difference is the rhythm of deep sleep.'}),
    (95.0, 130.0, {'titulo': 'Breathe out slowly.', 'sub': 'Let your jaw soften.'}),
    (172.0, 180.0, {'tipo': 'fin', 'titulo': '3 hours, black screen, on YouTube',
                    'sub': 'Rin · pink noise and delta waves, composed from scratch.'}),
]
TEXTO_DELTA = """Pink noise + delta waves for deep sleep 🌙
🎧 Headphones on: each ear hears a slightly different tone, and the 2 Hz difference is the rhythm of deep sleep.
Pink noise is soft and even, like steady rain. It covers what keeps you awake.
Composed from scratch by Rin, no samples. The full 3 hours, black screen, on YouTube. Link in bio.

#pinknoise #deltawaves #binauralbeats #deepsleep #sleeptok"""

PIEZAS = {
    'marron': dict(bucle='vertical-zen-t35.mp4', audio='tiktok-marron/marron-master.wav', T=180,
                   textos=TEXTOS_MARRON, texto=TEXTO_MARRON, out='tiktok-marron',
                   nombre='brown-noise-tiktok.mp4', kbps=1100),
    'delta': dict(bucle='vertical-theta.mp4', audio='tiktok-delta/delta-master.wav', T=180,
                  textos=TEXTOS_DELTA, texto=TEXTO_DELTA, out='tiktok-delta',
                  nombre='pink-noise-delta-tiktok.mp4', kbps=1100),
    'reset10': dict(bucle='vertical-zen-t165.mp4', audio='tiktok-reset10/reset10-master.wav', T=600,
                    textos=TEXTOS_RESET10, texto=TEXTO_RESET10, out='tiktok-reset10',
                    nombre='3am-reset-10min-tiktok.mp4', kbps=900),
    'historia-tao': dict(bucle='vertical-theta.mp4', audio='historia-tao/tao-historia.wav', T=15,
                         textos=TEXTOS_HIST_TAO, texto=TEXTO_HIST_TAO, out='historia-tao',
                         nombre='historia-tao.mp4', kbps=4000, marca_fija=True),
    'historia-zen': dict(bucle='vertical-zen-t165.mp4', audio='historia-zen/zen-historia.wav', T=15,
                         textos=TEXTOS_HIST_ZEN, texto=TEXTO_HIST_ZEN, out='historia-zen',
                         nombre='historia-zen.mp4', kbps=4000, marca_fija=True),
    'historia-marco': dict(bucle='vertical-lluvia.mp4', audio='historia-marco/marco-historia.wav', T=15,
                           textos=TEXTOS_HIST_MARCO, texto=TEXTO_HIST_MARCO, out='historia-marco',
                           nombre='historia-marco.mp4', kbps=4000, marca_fija=True),
    'historia-theta': dict(bucle='vertical-theta.mp4', audio='historia-theta/theta-historia.wav', T=15,
                           textos=TEXTOS_HIST_THETA, texto=TEXTO_HIST_THETA, out='historia-theta',
                           nombre='historia-theta.mp4', kbps=4000),
    'historia-3am': dict(bucle='vertical-zen-t165.mp4', audio='historia-3am/3am-historia.wav', T=15,
                         textos=TEXTOS_HIST_3AM, texto=TEXTO_HIST_3AM, out='historia-3am',
                         nombre='historia-3am.mp4', kbps=4000),
    'tao': dict(bucle='vertical-zen-t165.mp4', audio='tiktok-tao/tao-master.wav', T=120,
                textos=TEXTOS_TAO, texto=TEXTO_TAO, out='tiktok-tao', nombre='tao-tiktok.mp4'),
    'pensar': dict(bucle='vertical-jardin.mp4', audio='tiktok-pensar/pensar-master.wav', T=75,
                   textos=TEXTOS_PENSAR, texto=TEXTO_PENSAR, out='tiktok-pensar', nombre='pensar-tiktok.mp4'),
    # 3 min: con 1600 kbps pasaría los 30 MB; 1100 alcanza para un mandala lento
    'nervios': dict(bucle='vertical-zen-t35.mp4', audio='tiktok-nervios/nervios-master.wav', T=180,
                    textos=TEXTOS_NERVIOS, texto=TEXTO_NERVIOS, out='tiktok-nervios',
                    nombre='nervios-tiktok.mp4', kbps=1100),
    # 3 min de OBRA-043 desde el minuto 10 (la música ya entera), con el mandala
    # azul noche: en TikTok la pantalla negra no retiene, en YouTube sí
    'lluvia': dict(bucle='vertical-lluvia.mp4', audio='tiktok-lluvia/lluvia-master.wav', T=180,
                   textos=TEXTOS_LLUVIA, texto=TEXTO_LLUVIA, out='tiktok-lluvia',
                   nombre='lluvia-tiktok.mp4', kbps=1100),
    # 3 min de OBRA-044 desde el minuto 10, con el mandala violeta. El gancho
    # pide auriculares: sin ellos las ondas theta no existen
    'theta': dict(bucle='vertical-theta.mp4', audio='tiktok-theta/theta-master.wav', T=180,
                  textos=TEXTOS_THETA, texto=TEXTO_THETA, out='tiktok-theta',
                  nombre='theta-tiktok.mp4', kbps=1100),
    # 90 s de guqin en modo yu, compuesto para el video (tao.py --modo yu), sobre jade
    '3am': dict(bucle='vertical-zen-t165.mp4', audio='tiktok-3am/3am-master.wav', T=90,
                textos=TEXTOS_3AM, texto=TEXTO_3AM, out='tiktok-3am', nombre='3am-tiktok.mp4'),
    'exhala': dict(bucle='vertical-zen.mp4', audio='tiktok-exhala/exhala-master.wav', T=90,
                   textos=TEXTOS_EXHALA, texto=TEXTO_EXHALA, out='tiktok-exhala', nombre='exhala-tiktok.mp4'),
}


def pngs(tmp, TEXTOS, T):
    rutas = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        pag = nav.new_page(viewport={'width': 1080, 'height': 1920})
        for k, (a, b, q) in enumerate(TEXTOS + [(0, T, {'marca': '1'})]):
            q = dict(q)
            if 'titulo' in q: q['marca'] = '0'
            pag.goto(f"file://{AQUI / 'texto_tiktok.html'}?{urllib.parse.urlencode(q)}")
            pag.wait_for_timeout(400)
            r = tmp / f't{k}.png'
            pag.screenshot(path=str(r), omit_background=True)
            rutas.append(r)
        nav.close()
    # un velo oscuro y ovalado detrás del texto, para que se lea sobre el dorado
    import numpy as np
    y, x = np.mgrid[0:1920, 0:1080]
    d = np.sqrt(((x - 540) / 620) ** 2 + ((y - 520) / 330) ** 2)
    alfa = (0.72 * np.clip(1.25 - d, 0, 1) ** 1.2 * 255).astype('uint8')
    v = np.zeros((1920, 1080, 4), 'uint8'); v[..., 3] = alfa
    Image.fromarray(v, 'RGBA').save(tmp / 'velo.png')
    return rutas, tmp / 'velo.png'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pieza', choices=list(PIEZAS), default='tao')
    P = PIEZAS[ap.parse_args().pieza]
    TEXTOS, T = P['textos'], P['T']
    OUT = RAIZ / 'produccion' / P['out']
    BUCLE, audio = BUCLES / P['bucle'], RAIZ / 'produccion' / P['audio']
    if not BUCLE.exists() or not audio.exists():
        sys.exit(f'Faltan {BUCLE} o {audio}')
    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t)
        rutas, velo = pngs(tmp, TEXTOS, T)
        args = ['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-stream_loop', '-1', '-i', str(BUCLE),
                '-i', str(audio), '-loop', '1', '-framerate', '24', '-t', str(T), '-i', str(velo)]
        for r in rutas:
            args += ['-loop', '1', '-framerate', '24', '-t', str(T), '-i', str(r)]
        f = ['[0:v]fps=24,format=yuv420p[m0]', '[m0][2:v]overlay=0:0[m1]']
        cur = 'm1'
        for k, (a, b, q) in enumerate(TEXTOS):
            ent = 0.0 if a == 0 else 0.8
            fx = f"[{k + 3}:v]format=rgba" + (f",fade=t=in:st={a}:d={ent}:alpha=1" if ent else '') + \
                 f",fade=t=out:st={b - 1.2}:d=1.2:alpha=1[x{k}]"
            f.append(fx)
            f.append(f"[{cur}][x{k}]overlay=0:0:enable='between(t,{a},{b})'[m{k + 2}]")
            cur = f'm{k + 2}'
        marca = len(TEXTOS) + 3
        # la marca «Rin» queda fija, salvo cuando el texto final ya la nombra
        cuando = '1' if P.get('marca_fija') else f'lt(t,{TEXTOS[-1][0]})'
        f.append(f"[{cur}][{marca}:v]overlay=0:0:enable='{cuando}'[v]")
        salida = OUT / P['nombre']
        comun = ['-filter_complex', ';'.join(f), '-map', '[v]', '-map', '1:a', '-t', str(T),
                 '-c:v', 'libx264', '-preset', 'medium', '-b:v', f"{P.get('kbps', 1600)}k", '-pix_fmt', 'yuv420p']
        log = str(tmp / 'x264')
        subprocess.run(args + comun + ['-pass', '1', '-passlogfile', log, '-an', '-f', 'null', '-'], check=True)
        subprocess.run(args + comun + ['-pass', '2', '-passlogfile', log, '-c:a', 'aac', '-b:a', '192k',
                                       '-ar', '48000', '-movflags', '+faststart', str(salida)], check=True)
    (OUT / 'textos.txt').write_text(P['texto'] + '\n', encoding='utf-8')
    print(f'{salida}  {salida.stat().st_size / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
