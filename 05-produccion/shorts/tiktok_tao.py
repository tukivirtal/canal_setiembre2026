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

# 05/10: la muestra C de la escucha, ondas delta y campanas del templo, sin
# ruido: la que más tranquilizó. El ruido rosa y el marrón sonaban a interferencia.
TEXTOS_DELTA_CAMPANAS = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Delta waves for deep sleep',
                'sub': 'With soft temple bells. Headphones on.'}),
    (8.0, 40.0, {'titulo': 'Each ear hears a different tone',
                 'sub': 'The difference is 2 Hz: the rhythm of deep sleep.'}),
    (48.0, 85.0, {'titulo': 'Breathe out longer than you breathe in.'}),
    (95.0, 130.0, {'titulo': 'Let your jaw soften.', 'sub': 'Nothing to do now. Just the bells.'}),
    (172.0, 180.0, {'tipo': 'fin', 'titulo': 'Save this for tonight',
                    'sub': 'Rin · delta waves and temple bells, composed from scratch.'}),
]
TEXTO_DELTA_CAMPANAS = """Delta waves for deep sleep 🌙 With soft zen temple bells.
🎧 Headphones on: each ear hears a slightly different tone, and the 2 Hz difference is the rhythm of deep sleep.
Breathe out longer than you breathe in. Nothing to do now, just the bells.
Composed from scratch by Rin, no samples. Save this for tonight. Full pieces on YouTube, link in bio.

#deltawaves #binauralbeats #sleepmusic #deepsleep #templebells"""

# 05/10: historia con el Dhammapada 100 (traducción propia del pali, dominio
# público), con el audio sin ruido del TikTok de ondas delta y campanas.
TEXTOS_HIST_DHAMMA = [
    (0.6, 15.0, {'titulo': 'Better than a thousand hollow words is one word that brings peace.',
                 'fuente': 'DHAMMAPADA · 100'}),
]
TEXTO_HIST_DHAMMA = "Better than a thousand hollow words is one word that brings peace. Dhammapada 🌙"

# 05/10: diapasones en 396 Hz y su quinta abajo (264, 3:2), puros, sobre el drone
# nuevo sin graves: la muestra C, la única que pasó la escucha sin «bocina».
TEXTOS_DIAPASONES = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': '396 Hz tuning forks',
                'sub': 'The frequency of letting go. Just listen.'}),
    (8.0, 40.0, {'titulo': 'Each strike rings, then fades', 'sub': 'Breathe out with the fading sound.'}),
    (48.0, 85.0, {'titulo': "Let go of what you're carrying."}),
    (95.0, 130.0, {'titulo': 'Unclench your jaw.', 'sub': 'Drop your shoulders.'}),
    (172.0, 180.0, {'tipo': 'fin', 'titulo': 'Save this for a hard day',
                    'sub': 'Rin · tuning forks at 396 Hz, composed from scratch.'}),
]
TEXTO_DIAPASONES = """396 Hz tuning forks 🔔 The solfeggio frequency of letting go.
Each strike rings, then fades. Breathe out with the fading sound.
Let go of what you're carrying. Unclench your jaw, drop your shoulders.
Composed from scratch by Rin, no samples. More meditations: link in bio.

#396hz #tuningfork #soundhealing #letgo #meditation"""

# 05/10: historia que acompaña al TikTok de diapasones («soltar»). Tao Te Ching
# 48, traducción propia (dominio público), con el audio de los diapasones.
TEXTOS_HIST_SOLTAR = [
    (0.6, 15.0, {'titulo': 'To gain knowledge, add something every day. To find peace, let something go.',
                 'fuente': 'TAO TE CHING · 48'}),
]
TEXTO_HIST_SOLTAR = "What will you let go of today? 🔔 Tao Te Ching 48"

# 05/10: el mismo sonido de diapasones en 60 s, con golpes cada ~5 s y un texto
# nuevo cada ~8: para comparar en TikTok contra el de 3 minutos (formato, no sonido).
TEXTOS_SOLTAR60 = [
    (0.0, 5.0, {'tipo': 'gancho', 'titulo': '60 seconds to let go', 'sub': 'One strike, one breath.'}),
    (6.0, 13.0, {'titulo': 'Listen to the strike.'}),
    (14.0, 21.0, {'titulo': 'Breathe in.'}),
    (22.0, 30.0, {'titulo': 'Breathe out as it fades.'}),
    (31.0, 39.0, {'titulo': 'Drop your shoulders.'}),
    (40.0, 48.0, {'titulo': 'Let one thought go.'}),
    (49.0, 55.0, {'titulo': 'Just one.'}),
    (55.5, 60.0, {'tipo': 'fin', 'titulo': 'Do it again tomorrow',
                  'sub': 'Rin · tuning forks at 396 Hz, composed from scratch.'}),
]
TEXTO_SOLTAR60 = """60 seconds to let go 🔔 One strike, one breath.
Listen to the strike, breathe in, and breathe out as it fades. Let one thought go. Just one.
Tuning forks at 396 Hz, composed from scratch by Rin. More meditations: link in bio.

#letgo #60secondmeditation #396hz #breathe #calm"""

# 06/10: historia para el TikTok de 60 s. Séneca, Cartas a Lucilio 13.4,
# traducción propia del latín (dominio público), con el audio de los diapasones.
TEXTOS_HIST_SENECA = [
    (0.6, 15.0, {'titulo': 'We suffer more often in imagination than in reality.',
                 'fuente': 'SENECA · LETTERS 13'}),
]
TEXTO_HIST_SENECA = "Let one thought go 🔔 Seneca, Letters 13"

# 06/10: curiosidad verdadera. Jámblico (Vida de Pitágoras) cuenta que los
# pitagóricos cantaban con la lira al anochecer para calmar la mente del día y
# dormir bien. Lira sintetizada (la cuerda pulsada de tao.py) en intervalos
# pitagóricos, sin terceras, sobre el drone nuevo sin graves.
TEXTOS_PITAGORAS = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Pythagoras had a ritual for sleep',
                'sub': 'His students ended every day like this.'}),
    (8.0, 32.0, {'titulo': 'Before sleep, they sang with the lyre', 'sub': 'To quiet the noise of the day.',
                 'fuente': 'IAMBLICHUS · LIFE OF PYTHAGORAS'}),
    (36.0, 66.0, {'titulo': 'Then they went over the day.', 'sub': 'What did I do well? What can I let go of?'}),
    (72.0, 104.0, {'titulo': 'Breathe out.', 'sub': 'Let the strings do the rest.'}),
    (110.0, 140.0, {'titulo': 'A lyre in Pythagorean tuning', 'sub': 'Pure fifths, the intervals he measured.'}),
    (290.0, 300.0, {'tipo': 'fin', 'titulo': 'Try it tonight',
                    'sub': 'Rin · ancient sleep rituals, composed from scratch.'}),
]
TEXTO_PITAGORAS = """Pythagoras had a ritual for sleep 🌙 His students sang with the lyre every evening, to quiet the noise of the day. Then they went over the day: what did I do well, what can I let go of?
This is a lyre in Pythagorean tuning, pure fifths, composed from scratch by Rin. Try it tonight. More meditations: link in bio.

#pythagoras #sleepritual #ancientwisdom #lyre #sleepmusic"""

# Historia: Versos dorados pitagóricos 40-44, traducción propia (dominio público).
TEXTOS_HIST_VERSOS = [
    (0.6, 15.0, {'titulo': 'Do not let sleep close your eyes before you have gone over each deed of the day.',
                 'fuente': 'GOLDEN VERSES OF PYTHAGORAS'}),
]
TEXTO_HIST_VERSOS = "Tonight, before sleep 🌙 Golden Verses of Pythagoras"

# 06/10: los primeros en español. El público de la promoción es de México,
# Argentina y Chile, de 35 a 54 años. Mismo sonido que los ganadores
# (diapasones en 396 Hz), con filosofía oriental. Español neutro (tú).
# 1 min: la historia zen de la taza de té (Nan-in, Japón, era Meiji; contada
# con palabras propias). Golpe cada ~5 s y un texto cada ~8, como «60 seconds».
TEXTOS_TAZA = [
    (0.0, 5.0, {'tipo': 'gancho', 'titulo': 'Vacía tu taza', 'sub': 'Una historia zen en 60 segundos.'}),
    (6.0, 13.0, {'titulo': 'Un profesor fue a ver al maestro zen Nan-in.'}),
    (14.0, 21.0, {'titulo': 'Nan-in le sirvió té. La taza se llenó, y siguió sirviendo.'}),
    (22.0, 30.0, {'titulo': '«Está llena. Ya no entra nada más.»'}),
    (31.0, 39.0, {'titulo': '«Como tú», dijo Nan-in. «Primero vacía tu taza.»'}),
    (40.0, 48.0, {'titulo': 'Exhala con el sonido.', 'sub': 'Suelta una idea.'}),
    (49.0, 55.0, {'titulo': 'Solo una.'}),
    (55.5, 60.0, {'tipo': 'fin', 'titulo': 'Vuelve mañana',
                  'sub': 'Rin · diapasones en 396\u00a0Hz, compuesto desde cero.'}),
]
TEXTO_TAZA = """Vacía tu taza 🍵 Una historia zen en 60 segundos.
Un profesor fue a ver al maestro Nan-in. Nan-in le sirvió té y siguió sirviendo hasta que la taza rebalsó. «Como tú», le dijo. «Primero vacía tu taza.»
Exhala con el sonido y suelta una idea. Solo una.
Diapasones en 396 Hz, compuesto desde cero por Rin. Más meditaciones: link en la bio.

#zen #meditacion #396hz #soltar #calma"""

# 3 min: «Sé como el agua», Tao Te Ching 8 y 78 (traducción propia del chino,
# dominio público), con el sonido y el ritmo del TikTok de diapasones de 3 min.
TEXTOS_AGUA = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': 'Diapasones en 396 Hz',
                'sub': 'Sé como el agua. Solo escucha.'}),
    (8.0, 40.0, {'titulo': 'Cada golpe suena y se apaga', 'sub': 'Exhala mientras se apaga.'}),
    (46.0, 78.0, {'titulo': 'La bondad más alta es como el agua.', 'fuente': 'TAO TE CHING · 8'}),
    (84.0, 116.0, {'titulo': 'Nutre a todas las cosas y no compite.', 'fuente': 'TAO TE CHING · 8'}),
    (122.0, 160.0, {'titulo': 'Nada es más blando que el agua, y nada la supera para vencer lo duro.',
                    'fuente': 'TAO TE CHING · 78'}),
    (172.0, 180.0, {'tipo': 'fin', 'titulo': 'Guárdalo para un día difícil',
                    'sub': 'Rin · diapasones en 396\u00a0Hz, compuesto desde cero.'}),
]
TEXTO_AGUA = """Diapasones en 396 Hz 💧 Sé como el agua.
Cada golpe suena y se apaga: exhala mientras se apaga.
«La bondad más alta es como el agua: nutre a todas las cosas y no compite.» Tao Te Ching 8
Compuesto desde cero por Rin, sin muestras. Más meditaciones: link en la bio.

#396hz #diapasones #taoismo #meditacion #soltar"""

# 07/10: historia para los TikToks en español («Vacía tu taza» y «Sé como el
# agua»). Zhuangzi, cap. 5 (人莫鑑於流水而鑑於止水), traducción propia.
TEXTOS_HIST_QUIETA = [
    (0.6, 15.0, {'titulo': 'Nadie se mira en el agua que corre. Nos miramos en el agua quieta.',
                 'fuente': 'ZHUANGZI · 5'}),
]
TEXTO_HIST_QUIETA = "Quédate quieto un momento 💧 Zhuangzi"

# 07/10: la fórmula que sale de los cuatro primeros (y de la lectura de
# Fátima: «al público hay que darle algo digerido, que se sienta
# identificado: esto me pasa a mí, qué bueno que vi esto»). En el primer
# segundo, una situación que la persona reconoce; después, instrucciones de
# pocas palabras y una frase que alivia. Nada que haya que leer de corrido.
# 1 min: el ritmo del «60 seconds to let go» ganador, golpe cada ~5 s.
TEXTOS_TRABAJO = [
    (0.0, 5.0, {'tipo': 'gancho', 'titulo': '¿Tu cabeza sigue en el trabajo?',
                'sub': '60 segundos para dejarlo afuera.'}),
    (6.0, 13.0, {'titulo': 'Escucha el golpe.'}),
    (14.0, 21.0, {'titulo': 'Inhala.'}),
    (22.0, 30.0, {'titulo': 'Exhala mientras se apaga.'}),
    (31.0, 39.0, {'titulo': 'Suelta los hombros.'}),
    (40.0, 48.0, {'titulo': 'Lo que quedó pendiente puede esperar.'}),
    (49.0, 55.0, {'titulo': 'Ya estás en casa.'}),
    (55.5, 60.0, {'tipo': 'fin', 'titulo': 'Mándaselo a quien lo necesite',
                  'sub': 'Rin · diapasones en 432\u00a0Hz, compuesto desde cero.'}),
]
TEXTO_TRABAJO = """¿Llegaste a casa pero tu cabeza sigue en el trabajo? 🔔
60 segundos para dejarlo afuera: escucha el golpe, exhala mientras se apaga y suelta los hombros. Lo pendiente puede esperar.
Diapasones en 432 Hz, compuesto desde cero por Rin. Más meditaciones: link en la bio.
Mándaselo a quien lo necesite 🤍

#estres #ansiedad #calma #432hz #soltar"""

# 07/10, pedido de Fátima: cada video con su color y sus notas, para que el
# perfil no se vea repetido. El timbre de diapasón (lo que funcionó) se queda;
# cambia la nota: 432, 528, 417, 396 y 396 + 528 Hz. Cada par es la raíz y su
# quinta abajo (3:2), salvo el de 396 + 528, que es una cuarta (4:3).
TEXTOS_CUIDAS = [
    (0.0, 5.0, {'tipo': 'gancho', 'titulo': '¿Siempre cuidas de todos?',
                'sub': 'Estos 60 segundos son para ti.'}),
    (6.0, 13.0, {'titulo': 'Escucha el golpe.'}),
    (14.0, 21.0, {'titulo': 'Inhala.'}),
    (22.0, 30.0, {'titulo': 'Exhala mientras se apaga.'}),
    (31.0, 39.0, {'titulo': 'Pon una mano en el pecho.'}),
    (40.0, 48.0, {'titulo': 'Tú también mereces una pausa.'}),
    (49.0, 55.0, {'titulo': 'Tómala sin culpa.'}),
    (55.5, 60.0, {'tipo': 'fin', 'titulo': 'Mándaselo a alguien que cuida de todos',
                  'sub': 'Rin · diapasones en 528\u00a0Hz, compuesto desde cero.'}),
]
TEXTO_CUIDAS = """¿Siempre cuidas de todos? 🤍
Estos 60 segundos son para ti: escucha el golpe, exhala mientras se apaga y pon una mano en el pecho. Tú también mereces una pausa. Tómala sin culpa.
Diapasones en 528 Hz, compuesto desde cero por Rin. Más meditaciones: link en la bio.
Mándaselo a alguien que cuida de todos.

#ansiedad #estres #autocuidado #528hz #calma"""

TEXTOS_NOLLEGO = [
    (0.0, 5.0, {'tipo': 'gancho', 'titulo': '¿Sientes que no llegas a todo?',
                'sub': '60 segundos para parar.'}),
    (6.0, 13.0, {'titulo': 'Para un momento.'}),
    (14.0, 21.0, {'titulo': 'Escucha el golpe.'}),
    (22.0, 30.0, {'titulo': 'Exhala mientras se apaga.'}),
    (31.0, 39.0, {'titulo': 'Suelta los hombros.'}),
    (40.0, 48.0, {'titulo': 'Haces lo que puedes.'}),
    (49.0, 55.0, {'titulo': 'Y eso es suficiente.'}),
    (55.5, 60.0, {'tipo': 'fin', 'titulo': 'Guárdalo para un día difícil',
                  'sub': 'Rin · diapasones en 417\u00a0Hz, compuesto desde cero.'}),
]
TEXTO_NOLLEGO = """¿Sientes que no llegas a todo? 🔔
60 segundos para parar: escucha el golpe, exhala mientras se apaga y suelta los hombros. Haces lo que puedes, y eso es suficiente.
Diapasones en 417 Hz, compuesto desde cero por Rin. Más meditaciones: link en la bio.
Guárdalo para un día difícil.

#ansiedad #estres #calma #417hz #soltar"""

# 2 min: golpe cada ~9 s, 528 y 396 Hz alternados.
TEXTOS_DISCUSION = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': '¿Una discusión te quedó dando vueltas?',
                'sub': 'Diapasones en 396 y 528 Hz. Solo escucha.'}),
    (8.0, 30.0, {'titulo': 'No tienes que responder ahora.'}),
    (35.0, 57.0, {'titulo': 'Escucha cada golpe hasta que se apague.', 'sub': 'Exhala con él.'}),
    (62.0, 84.0, {'titulo': 'Afloja las manos.', 'sub': 'Suelta la mandíbula.'}),
    (89.0, 110.0, {'titulo': 'Primero, calma. Después, palabras.'}),
    (113.0, 120.0, {'tipo': 'fin', 'titulo': 'Guárdalo para la próxima vez',
                    'sub': 'Rin · diapasones en 396 y 528\u00a0Hz, compuesto desde cero.'}),
]
TEXTO_DISCUSION = """¿Una discusión te quedó dando vueltas? 🌙
No tienes que responder ahora. Escucha cada golpe hasta que se apague y exhala con él. Primero, calma. Después, palabras.
Diapasones en 396 y 528 Hz, compuesto desde cero por Rin. Más meditaciones: link en la bio.
¿Te pasa seguido? Cuéntame 👇

#ansiedad #estres #calma #396hz #528hz"""

# 3 min: el ritmo del de diapasones de 3 min, golpe cada ~9 s.
TEXTOS_NOCHE = [
    (0.0, 6.0, {'tipo': 'gancho', 'titulo': '¿Te acuestas y la cabeza no para?',
                'sub': 'Diapasones en 396 Hz. Solo escucha.'}),
    (8.0, 40.0, {'titulo': 'No tienes que resolver nada esta noche.'}),
    (46.0, 78.0, {'titulo': 'Escucha cada golpe hasta que se apague.', 'sub': 'Exhala con él.'}),
    (84.0, 116.0, {'titulo': 'Afloja la mandíbula.', 'sub': 'Suelta los hombros.'}),
    (122.0, 160.0, {'titulo': 'Lo que no hiciste hoy puede esperar a mañana.'}),
    (172.0, 180.0, {'tipo': 'fin', 'titulo': 'Guárdalo para esta noche',
                    'sub': 'Rin · diapasones en 396\u00a0Hz, compuesto desde cero.'}),
]
TEXTO_NOCHE = """¿Te acuestas y la cabeza no para? 🌙
No tienes que resolver nada esta noche. Escucha cada golpe hasta que se apague y exhala con él.
Diapasones en 396 Hz, compuesto desde cero por Rin. Más meditaciones: link en la bio.
¿Qué es lo que más te da vueltas de noche? Cuéntame 👇

#insomnio #ansiedad #dormir #396hz #meditacion"""

# 08/10: dos historias con la fórmula nueva, en dos tiempos: primero la
# pregunta en la que la persona se reconoce, después la respuesta de un
# antiguo, corta y verdadera. Un golpe de diapasón por cada cambio.
# Séneca, Cartas a Lucilio 13.4 («saepius opinione quam re laboramus»).
TEXTOS_HIST_IMAGINAR = [
    (0.3, 5.2, {'tipo': 'gancho', 'titulo': '¿Tu cabeza siempre imagina lo peor?'}),
    (5.4, 15.0, {'titulo': 'Sufrimos más a menudo en la imaginación que en la realidad.',
                 'fuente': 'SÉNECA · CARTAS A LUCILIO, 13'}),
]
TEXTO_HIST_IMAGINAR = "Hace 2.000 años ya nos pasaba 🌙 Séneca"

# Tao Te Ching 46 (知足之足，常足矣), traducción propia.
TEXTOS_HIST_SUFICIENTE = [
    (0.3, 5.2, {'tipo': 'gancho', 'titulo': '¿Sientes que nunca es suficiente?'}),
    (5.4, 15.0, {'titulo': 'Quien sabe que lo suficiente es suficiente, siempre tiene suficiente.',
                 'fuente': 'TAO TE CHING · 46'}),
]
TEXTO_HIST_SUFICIENTE = "Lo que hiciste hoy alcanza 🔔 Tao Te Ching"

# 08/10: «¿Tu cabeza sigue en el trabajo?» sacó 5.120 vistas con la misma
# promoción que los otros (458–1.077). Dos más sobre el trabajo, para el
# viernes a la tarde y el domingo a la noche.
TEXTOS_VIERNES = [
    (0.0, 5.0, {'tipo': 'gancho', 'titulo': '¿Terminó la semana y tu cabeza sigue en el trabajo?',
                'sub': '60 segundos para cerrar la semana.'}),
    (6.0, 13.0, {'titulo': 'Escucha el golpe.'}),
    (14.0, 21.0, {'titulo': 'Inhala.'}),
    (22.0, 30.0, {'titulo': 'Exhala mientras se apaga.'}),
    (31.0, 39.0, {'titulo': 'Suelta los hombros.'}),
    (40.0, 48.0, {'titulo': 'La semana ya terminó.'}),
    (49.0, 55.0, {'titulo': 'Lo que falta, el lunes.'}),
    (55.5, 60.0, {'tipo': 'fin', 'titulo': 'Mándaselo a quien trabajó de más esta semana',
                  'sub': 'Rin · diapasones en 432\u00a0Hz, compuesto desde cero.'}),
]
TEXTO_VIERNES = """¿Terminó la semana y tu cabeza sigue en el trabajo? 🔔
60 segundos para cerrar la semana: escucha el golpe, exhala mientras se apaga y suelta los hombros. Lo que falta, el lunes.
Diapasones en 432 Hz, compuesto desde cero por Rin. Más meditaciones: link en la bio.
Mándaselo a quien trabajó de más esta semana 🤍

#estres #trabajo #calma #432hz #viernes"""

TEXTOS_DOMINGO = [
    (0.0, 5.0, {'tipo': 'gancho', 'titulo': '¿Domingo a la noche y ya estás pensando en el lunes?',
                'sub': '60 segundos para quedarte en el domingo.'}),
    (6.0, 13.0, {'titulo': 'Escucha el golpe.'}),
    (14.0, 21.0, {'titulo': 'Inhala.'}),
    (22.0, 30.0, {'titulo': 'Exhala mientras se apaga.'}),
    (31.0, 39.0, {'titulo': 'Afloja la mandíbula.'}),
    (40.0, 48.0, {'titulo': 'El lunes todavía no llegó.'}),
    (49.0, 55.0, {'titulo': 'Hoy todavía es domingo.'}),
    (55.5, 60.0, {'tipo': 'fin', 'titulo': 'Guárdalo para cada domingo',
                  'sub': 'Rin · diapasones en 396\u00a0Hz, compuesto desde cero.'}),
]
TEXTO_DOMINGO = """¿Domingo a la noche y ya estás pensando en el lunes? 🌙
60 segundos para quedarte en el domingo: escucha el golpe, exhala mientras se apaga y afloja la mandíbula. El lunes todavía no llegó.
Diapasones en 396 Hz, compuesto desde cero por Rin. Más meditaciones: link en la bio.
Guárdalo para cada domingo.

#estres #trabajo #ansiedad #396hz #domingo"""

PIEZAS = {
    'viernes': dict(bucle='vertical-zen.mp4', audio='tiktok-viernes/viernes-master.wav', T=60,
                    textos=TEXTOS_VIERNES, texto=TEXTO_VIERNES, out='tiktok-viernes',
                    nombre='viernes-cerrar-la-semana-tiktok.mp4', kbps=1600),
    'domingo': dict(bucle='vertical-jardin.mp4', audio='tiktok-domingo/domingo-master.wav', T=60,
                    textos=TEXTOS_DOMINGO, texto=TEXTO_DOMINGO, out='tiktok-domingo',
                    nombre='domingo-pensando-en-el-lunes-tiktok.mp4', kbps=1600),
    'historia-imaginar': dict(bucle='vertical-lluvia.mp4', audio='historia-imaginar/imaginar-historia.wav', T=15,
                              textos=TEXTOS_HIST_IMAGINAR, texto=TEXTO_HIST_IMAGINAR, out='historia-imaginar',
                              nombre='historia-seneca-imaginacion.mp4', kbps=4000, marca_fija=True),
    'historia-suficiente': dict(bucle='vertical-zen-t35.mp4', audio='historia-suficiente/suficiente-historia.wav', T=15,
                                textos=TEXTOS_HIST_SUFICIENTE, texto=TEXTO_HIST_SUFICIENTE, out='historia-suficiente',
                                nombre='historia-tao-suficiente.mp4', kbps=4000, marca_fija=True),
    'trabajo': dict(bucle='vertical-zen-t35.mp4', audio='tiktok-trabajo/trabajo-master.wav', T=60,
                    textos=TEXTOS_TRABAJO, texto=TEXTO_TRABAJO, out='tiktok-trabajo',
                    nombre='cabeza-en-el-trabajo-tiktok.mp4', kbps=1600),
    'noche': dict(bucle='vertical-lluvia.mp4', audio='tiktok-noche/noche-master.wav', T=180,
                  textos=TEXTOS_NOCHE, texto=TEXTO_NOCHE, out='tiktok-noche',
                  nombre='cabeza-no-para-tiktok.mp4', kbps=1100),
    'cuidas': dict(bucle='vertical-delta.mp4', audio='tiktok-cuidas/cuidas-master.wav', T=60,
                   textos=TEXTOS_CUIDAS, texto=TEXTO_CUIDAS, out='tiktok-cuidas',
                   nombre='cuidas-de-todos-tiktok.mp4', kbps=1600),
    'nollego': dict(bucle='vertical-mar-aves.mp4', audio='tiktok-nollego/nollego-master.wav', T=60,
                    textos=TEXTOS_NOLLEGO, texto=TEXTO_NOLLEGO, out='tiktok-nollego',
                    nombre='no-llegas-a-todo-tiktok.mp4', kbps=1600),
    'discusion': dict(bucle='vertical-theta.mp4', audio='tiktok-discusion/discusion-master.wav', T=120,
                      textos=TEXTOS_DISCUSION, texto=TEXTO_DISCUSION, out='tiktok-discusion',
                      nombre='discusion-dando-vueltas-tiktok.mp4', kbps=1400),
    'historia-quieta': dict(bucle='vertical-jardin.mp4', audio='historia-quieta/quieta-historia.wav', T=15,
                            textos=TEXTOS_HIST_QUIETA, texto=TEXTO_HIST_QUIETA, out='historia-quieta',
                            nombre='historia-agua-quieta.mp4', kbps=4000, marca_fija=True),
    'taza': dict(bucle='vertical-zen.mp4', audio='tiktok-taza/taza-master.wav', T=60,
                 textos=TEXTOS_TAZA, texto=TEXTO_TAZA, out='tiktok-taza',
                 nombre='vacia-tu-taza-tiktok.mp4', kbps=1600),
    'agua': dict(bucle='vertical-jardin.mp4', audio='tiktok-agua/agua-master.wav', T=180,
                 textos=TEXTOS_AGUA, texto=TEXTO_AGUA, out='tiktok-agua',
                 nombre='se-como-el-agua-tiktok.mp4', kbps=1100),
    'pitagoras': dict(bucle='vertical-lluvia.mp4', audio='tiktok-pitagoras/pitagoras-master.wav', T=300,
                      textos=TEXTOS_PITAGORAS, texto=TEXTO_PITAGORAS, out='tiktok-pitagoras',
                      nombre='pythagoras-sleep-ritual-tiktok.mp4', kbps=650),
    'historia-versos': dict(bucle='vertical-lluvia.mp4', audio='historia-versos/versos-historia.wav', T=15,
                            textos=TEXTOS_HIST_VERSOS, texto=TEXTO_HIST_VERSOS, out='historia-versos',
                            nombre='historia-versos-dorados.mp4', kbps=4000, marca_fija=True),
    'historia-seneca': dict(bucle='vertical-zen.mp4', audio='historia-seneca/seneca-historia.wav', T=15,
                            textos=TEXTOS_HIST_SENECA, texto=TEXTO_HIST_SENECA, out='historia-seneca',
                            nombre='historia-seneca.mp4', kbps=4000, marca_fija=True),
    'soltar60': dict(bucle='vertical-zen.mp4', audio='tiktok-soltar60/soltar60-master.wav', T=60,
                     textos=TEXTOS_SOLTAR60, texto=TEXTO_SOLTAR60, out='tiktok-soltar60',
                     nombre='60-seconds-to-let-go-tiktok.mp4', kbps=1600),
    'historia-soltar': dict(bucle='vertical-jardin.mp4', audio='historia-soltar/soltar-historia.wav', T=15,
                            textos=TEXTOS_HIST_SOLTAR, texto=TEXTO_HIST_SOLTAR, out='historia-soltar',
                            nombre='historia-soltar.mp4', kbps=4000, marca_fija=True),
    'diapasones': dict(bucle='vertical-jardin.mp4', audio='tiktok-diapasones/diapasones-master.wav', T=180,
                       textos=TEXTOS_DIAPASONES, texto=TEXTO_DIAPASONES, out='tiktok-diapasones',
                       nombre='396hz-tuning-forks-tiktok.mp4', kbps=1100),
    'historia-dhamma': dict(bucle='vertical-zen.mp4', audio='historia-dhamma/dhamma-historia.wav', T=15,
                            textos=TEXTOS_HIST_DHAMMA, texto=TEXTO_HIST_DHAMMA, out='historia-dhamma',
                            nombre='historia-dhammapada.mp4', kbps=4000, marca_fija=True),
    'delta-campanas': dict(bucle='vertical-theta.mp4', audio='tiktok-delta-campanas/delta-campanas-master.wav', T=180,
                           textos=TEXTOS_DELTA_CAMPANAS, texto=TEXTO_DELTA_CAMPANAS, out='tiktok-delta-campanas',
                           nombre='delta-waves-temple-bells-tiktok.mp4', kbps=1100),
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
        subprocess.run(args + comun + ['-pass', '2', '-passlogfile', log, '-c:a', 'aac', '-b:a', '256k',
                                       '-ar', '48000', '-movflags', '+faststart', str(salida)], check=True)
    (OUT / 'textos.txt').write_text(P['texto'] + '\n', encoding='utf-8')
    print(f'{salida}  {salida.stat().st_size / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
