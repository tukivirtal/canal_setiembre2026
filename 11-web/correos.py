#!/usr/bin/env python3
"""Los 3 correos del regalo, uno por noche. Se cargan en la automatización de MailerLite
«Rin · Regalo 3 noches» (se dispara cuando alguien entra al grupo del mismo nombre).

Claros y casi de texto, a propósito: llegan mejor a la bandeja principal que un diseño
oscuro, y se leen como una carta. Un solo botón por correo.

Uso: python3 11-web/correos.py [--sitio https://...]  → imprime un JSON con los 3 correos
"""
import argparse
import json

SITIO = 'https://rin-pausas.netlify.app'

CORREOS = [
    dict(asunto='Tus 3 noches ya están aquí',
         previa='Empieza esta noche por la primera.',
         boton='Abrir mis 3 noches', ancla='',
         parrafos=['Hola:',
                   'Aquí están tus 3 primeras noches. Guarda este correo: el botón te lleva siempre a ellas.',
                   '{boton}',
                   'Esta noche, empieza por la primera: <strong>Dejar el trabajo en la puerta</strong>.',
                   '1. Lee la tarjeta. Son 30 segundos.<br>2. Pon el sonido y bloquea el celular.<br>'
                   '3. Cada vez que suene, exhala largo.',
                   'Si te duermes antes del final, está bien: para eso es.',
                   'Mañana te escribo para la noche dos.',
                   'Rin']),
    dict(asunto='Noche dos: la lista de la almohada',
         previa='Para cuando ya estás pensando en todo lo de mañana.',
         boton='Abrir la noche dos', ancla='#noche-2',
         parrafos=['Hola:',
                   '¿Cómo te fue anoche? Si quieres, responde este correo y cuéntame. Lo leo.',
                   'Esta noche toca <strong>la lista de la almohada</strong>. Antes de acostarte, escribe en '
                   'un papel lo que tienes que hacer mañana, bien concreto: «llamar a…», «pagar…», '
                   '«terminar…». Deja el papel lejos de la cama.',
                   'Lo que está escrito ya no tiene que estar en tu cabeza.',
                   '{boton}',
                   'Rin']),
    dict(asunto='Noche tres: cuando la cabeza da vueltas',
         previa='No hace falta dejar la mente en blanco.',
         boton='Abrir la noche tres', ancla='#noche-3',
         parrafos=['Hola:',
                   'Llegamos a la tercera noche.',
                   'Cuando la cabeza da vueltas, pelear con los pensamientos los hace más fuertes. Esta noche '
                   'no vas a intentar dejar la mente en blanco: cuando llegue un pensamiento, solo nótalo y '
                   'suéltalo en la exhalación. Si vuelve, lo sueltas otra vez.',
                   '{boton}',
                   'Estas son las 3 primeras de 21 noches. Pronto te cuento cómo seguir.',
                   'Rin']),
]

LETRA = "font-family:Arial,Helvetica,sans-serif;font-size:17px;line-height:1.6;color:#23211c;"


def html(c, sitio):
    url = f'{sitio}/tus-noches/{c["ancla"]}'
    boton = ('<table role="presentation" cellpadding="0" cellspacing="0" style="margin:26px auto;"><tr>'
             '<td style="border-radius:999px;background:#14161b;">'
             f'<a href="{url}" style="display:inline-block;padding:15px 30px;font-family:Arial,Helvetica,sans-serif;'
             f'font-size:17px;font-weight:bold;color:#f6e7b8;text-decoration:none;border-radius:999px;">{c["boton"]}</a>'
             '</td></tr></table>')
    cuerpo = ''.join(boton if p == '{boton}' else f'<p style="margin:0 0 16px;{LETRA}">{p}</p>'
                     for p in c['parrafos'])
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{c["asunto"]}</title></head><body style="margin:0;padding:0;background:#f4f1ea;">'
            f'<div style="display:none;max-height:0;overflow:hidden;">{c["previa"]}</div>'
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f1ea;">'
            '<tr><td align="center" style="padding:28px 14px;">'
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            'style="max-width:560px;background:#ffffff;border-radius:14px;">'
            '<tr><td style="padding:34px 32px 6px;text-align:center;font-family:Georgia,\'Times New Roman\',serif;'
            'font-size:15px;letter-spacing:6px;color:#a8873a;">RIN</td></tr>'
            f'<tr><td style="padding:18px 32px 22px;">{cuerpo}</td></tr></table>'
            '<p style="max-width:560px;margin:18px auto 0;font-family:Arial,Helvetica,sans-serif;font-size:12px;'
            'line-height:1.5;color:#8a857a;">Recibes este correo porque pediste las 3 noches de Rin. '
            '<a href="{$unsubscribe}" style="color:#8a857a;">Darte de baja</a>.</p>'
            '</td></tr></table></body></html>')


def texto(c, sitio):
    url = f'{sitio}/tus-noches/{c["ancla"]}'
    partes = []
    for p in c['parrafos']:
        if p == '{boton}':
            partes.append(f'{c["boton"]}: {url}')
        else:
            partes.append(p.replace('<strong>', '').replace('</strong>', '').replace('<br>', '\n'))
    return '\n\n'.join(partes) + '\n\nPara darte de baja: {$unsubscribe}'


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--sitio', default=SITIO)
    x = a.parse_args()
    print(json.dumps([dict(asunto=c['asunto'], previa=c['previa'], html=html(c, x.sitio), texto=texto(c, x.sitio))
                      for c in CORREOS], ensure_ascii=False, indent=1))
