#!/usr/bin/env python3
"""
Envuelve una obra en una capa de naturaleza: mar y viento.

    python3 03-composicion/ambiente.py obra.wav obra-final.wav
    python3 03-composicion/ambiente.py obra.wav obra-final.wav --intro 30 --lufs -24

Por qué existe: en la prueba de escucha del 23/09 el tono sostenido del fondo
se sentía incómodo justo donde queda expuesto: al entrar, al cambiar de sección
y al salir. La obra ahora empieza y termina solo con naturaleza, y el tono entra
y sale por debajo del mar, mucho más bajo que antes.

El mar y el viento se sintetizan a partir de ruido (marrón para el oleaje, rosa
para el viento), con ondas lentas de volumen. No hay grabaciones ajenas: el
máster sigue siendo propio, que es lo que habilita distribuir a streaming.

Requiere ffmpeg.
"""
import argparse, re, subprocess, tempfile, wave, os


# --- Fondos ------------------------------------------------------------------
# Cada fondo es un grafo de ffmpeg que termina en [fondo]. Se sintetizan a
# partir de ruido: nada grabado, el máster sigue siendo propio. Alternar el
# fondo entre obras es parte de que cada obra sea distinta (regla 3).

def fondo_mar(d):
    """Oleaje (ruido marrón sin agudos, ondas de ~10 s, distinto en cada oído)
    y viento en ráfagas muy lentas."""
    ola = ("anoisesrc=c=brown:r=44100:d={d}:s={s},highpass=f=45,lowpass=f=420,"
           "volume='0.30+0.70*pow(sin(PI*t/{p}+{f}),2)':eval=frame")
    return (f"{ola.format(d=d, s=11, p=9.5, f=0)}[mi];"
            f"{ola.format(d=d, s=22, p=10.7, f=1.3)}[md];"
            f"[mi][md]join=inputs=2:channel_layout=stereo[mar];"
            f"anoisesrc=c=pink:r=44100:d={d}:s=33,highpass=f=250,lowpass=f=1400,"
            f"volume='0.15+0.35*pow(sin(PI*t/23),2)':eval=frame,"
            f"pan=stereo|c0=c0|c1=c0[viento];"
            f"[mar][viento]amix=inputs=2:normalize=0:weights=0.9 0.35[fondo];")


def fondo_selva(d):
    """Selva tropical: aire húmedo y quieto, y un arroyo que corre cerca.

    Primera versión (23/09) descartada en la escucha: sonaba a "batidora". Tenía
    dos cosas periódicas y rápidas: el arroyo aleteaba a ~4 veces por segundo y
    los grillos zumbaban a 26. Todo lo periódico y rápido se oye como un motor.
    Ahora el agua solo cambia en ondas lentas que no coinciden entre sí, y los
    grillos se fueron: además eran lo único agudo del fondo."""
    agua = ("anoisesrc=c=brown:r=44100:d={d}:s={s},highpass=f=250,lowpass=f=2200,"
            "volume='0.42+0.12*sin(2*PI*t/5.3+{f})+0.10*sin(2*PI*t/7.9)"
            "+0.06*sin(2*PI*t/13.1+{f})':eval=frame")
    return (
        f"anoisesrc=c=pink:r=44100:d={d}:s=41,highpass=f=80,lowpass=f=1300,"
        f"volume='0.55+0.15*sin(2*PI*t/31)':eval=frame,"
        f"pan=stereo|c0=c0|c1=c0[aire];"
        f"{agua.format(d=d, s=52, f=0)}[ai];"
        f"{agua.format(d=d, s=63, f=1.7)}[ad];"
        f"[ai][ad]join=inputs=2:channel_layout=stereo[arroyo];"
        f"[aire][arroyo]amix=inputs=2:normalize=0:weights=0.8 0.6[fondo];")


def fondo_fuego(d):
    """Hoguera: el rumor grave del fuego (los chasquidos van en la capa
    ancestral) y un zumbido tipo didgeridoo en 66 Hz, que es 528 Hz dos octavas
    abajo, afinado con el resto del canal.

    El zumbido entra recién a los 25 s y crece en 45: un grave sostenido que
    aparece de golpe es justo lo que "retumba" en el oído. Sus "vocales" (el
    peso de los armónicos 2 a 5) se mueven con ondas lentas que no coinciden,
    así nunca se repite igual."""
    w = "(0.5+0.5*sin(2*PI*t/5.7)*sin(2*PI*t/3.1+1))"
    zumbido = (f"sin(2*PI*66*t+0.3*sin(2*PI*t/7))"
               f"+(0.35+0.30*{w})*sin(2*PI*132*t)"
               f"+(0.15+0.30*{w})*sin(2*PI*198*t)"
               f"+(0.05+0.22*{w})*sin(2*PI*264*t)"
               f"+(0.10*{w})*sin(2*PI*330*t)")
    entra = "pow(min(1,max(0,(t-25)/45)),2)"
    return (
        f"anoisesrc=c=brown:r=44100:d={d}:s=71,highpass=f=110,lowpass=f=700,"
        f"volume='0.55+0.12*sin(2*PI*t/4.1)+0.08*sin(2*PI*t/6.7+1)':eval=frame,"
        f"pan=stereo|c0=c0|c1=c0[rumor];"
        f"aevalsrc='0.06*{entra}*({zumbido})':s=44100:d={d},highpass=f=45,"
        f"pan=stereo|c0=c0|c1=c0[zumbido];"
        f"[rumor][zumbido]amix=inputs=2:normalize=0:weights=0.7 1[fondo];")


FONDOS = {'mar': fondo_mar, 'selva': fondo_selva, 'fuego': fondo_fuego}


def duracion(ruta):
    with wave.open(ruta, 'rb') as w:
        return w.getnframes() / w.getframerate()


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    p.add_argument('entrada')
    p.add_argument('salida')
    p.add_argument('--intro', type=float, default=20.0,
                   help='segundos de naturaleza sola antes de que entre la obra')
    p.add_argument('--cola', type=float, default=20.0,
                   help='segundos de naturaleza sola después de la obra')
    p.add_argument('--entrada-obra', type=float, default=50.0,
                   help='segundos que tarda el tono en aparecer bajo el mar')
    p.add_argument('--nivel-obra', type=float, default=-16.0,
                   help='cuántos dB se baja la obra bajo la naturaleza')
    p.add_argument('--fondo', choices=['mar', 'selva', 'fuego'], default='mar')
    p.add_argument('--nivel-fondo', type=float, default=0.0,
                   help='dB del fondo. Negativo para que la capa mande (zen)')
    p.add_argument('--capa', default=None,
                   help='wav de capas.py (aves o zen) que suena desde el segundo 0')
    p.add_argument('--nivel-capa', type=float, default=-4.0,
                   help='dB de la capa respecto del mar')
    p.add_argument('--lufs', type=float, default=-22.0,
                   help='volumen final. -14 es música pop; para meditar, -20 a -24')
    a = p.parse_args()

    dur_obra = duracion(a.entrada)
    d = a.intro + dur_obra + a.cola
    e = a.entrada_obra
    ms = int(a.intro * 1000)
    fin = d - 12

    # El oleaje: ruido marrón sin agudos, que sube y baja cada ~10 s. Izquierda
    # y derecha con períodos distintos para que el mar tenga ancho y no pulse
    # en el centro de la cabeza.
    grafo = (
        # La obra aparece y desaparece en curva exponencial: casi nada durante
        # los primeros segundos y recién después se hace presente. Con una
        # subida lineal el oído la percibe entera de golpe (prueba del 23/09:
        # "rompe la tranquilidad de golpe").
        f"[0]volume={a.nivel_obra}dB,"
        f"afade=t=in:d={e}:curve=exp,"
        f"afade=t=out:st={max(0, dur_obra - e)}:d={e}:curve=exp,"
        f"adelay={ms}|{ms},apad=whole_dur={d}[obra];"
        + FONDOS[a.fondo](d) +
        f"[fondo]volume={a.nivel_fondo}dB[fondo2];"
        + (
            # La capa lleva un eco corto de sala, sin agudos por encima de 6 kHz:
            # los pájaros y las campanitas son lo más agudo de la mezcla y es
            # justo la zona que incomoda.
            f"[1]lowpass=f=6000,aecho=0.8:0.6:70|130:0.22|0.12,"
            f"volume={a.nivel_capa}dB,apad=whole_dur={d}[capa];"
            f"[obra][fondo2][capa]amix=inputs=3:normalize=0,"
            if a.capa else
            f"[obra][fondo2]amix=inputs=2:normalize=0,"
        ) +
        f"afade=t=in:d=6,afade=t=out:st={fin}:d=12"
    )
    # Volumen en dos pasadas: primero se mide y después se aplica una sola
    # ganancia fija. El ajuste automático sobre la marcha (loudnorm dinámico)
    # subía el mar mientras estaba solo y lo bajaba de golpe cuando entraba la
    # obra, y ese movimiento se oía.
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
    try:
        entradas = ['-i', a.entrada] + (['-i', a.capa] if a.capa else [])
        subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y',
                        *entradas, '-filter_complex', grafo,
                        '-ar', '44100', tmp], check=True)
        med = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af',
                              'ebur128=framelog=quiet', '-f', 'null', '-'],
                             capture_output=True, text=True).stderr
        medido = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', med)[-1])
        subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-i', tmp,
                        '-af', f'volume={a.lufs - medido:.2f}dB,'
                               f'alimiter=limit=0.708:level=disabled',
                        '-ar', '44100', a.salida], check=True)
    finally:
        os.unlink(tmp)
    print(f'{a.salida}  ·  {d/60:.1f} min  ·  {a.intro:g} s de {a.fondo} al entrar, '
          f'{a.cola:g} s al salir  ·  la obra aparece en {e:g} s, a {a.nivel_obra:g} dB  ·  '
          f'{a.lufs:g} LUFS')


if __name__ == '__main__':
    main()
