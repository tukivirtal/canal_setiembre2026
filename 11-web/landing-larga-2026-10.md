# La landing larga: prototipo · 21/10/2026

Pedido de Fátima: el correo no funciona; hace falta una landing nueva, larga, estilo Hotmart
(como las de dietas keto o ansiedad), colorida, con videos cinematográficos en vez de mandalas,
y con la mejor estrategia. «Después vemos qué se vende.»

**Prototipo (privado):** https://claude.ai/artifact/JzX9HFPzXpYUSmsAyTRBa4. La página y sus
videos, imágenes y audio quedan publicados ahí.

## La estrategia

Sin correo: la página deja probar primero y después vende directo (un producto, un precio, un
botón). El orden sale de lo que funcionó en TikTok (`10-metricas/2026-10-21-tiktok-que-engancha.md`):
la frase que describe el momento de quien mira y el sonido para usar ya.

1. **Portada según la hora de quien entra.** «¿Estás en la cama y la cabeza no para?» de noche,
   «¿Llegaste a casa y la cabeza sigue en el trabajo?» a la salida del trabajo, y así. Con la
   hora real del teléfono.
2. **El minuto, ahí mismo.** Sonido de 60 s (432 Hz, un golpe cada 6 s) con un círculo que
   late con cada golpe y una instrucción por vez. Al final: «¿Cómo estás ahora?».
3. **Un día, hora por hora** (07:40 a 03:00), cada hora con su color. La persona toca las que
   le pasan y ve cuántas son.
4. **El cambio de idea:** «No es que no sepas relajarte. Es que nadie le avisó a tu cabeza que
   el día terminó.»
5. **Séneca** (*Sobre la ira* III, 36: repasaba el día al apagarse la luz). Curiosidad y autoridad.
6. **Cómo es una noche**, las 21 noches, lo que recibe, para quién es y para quién no.
7. **Números reales de TikTok** y tres lugares para comentarios reales, con permiso.
8. **La oferta**, la garantía de 7 días, las preguntas y el cierre.

**Lo que no se usa:** contadores que se reinician, escasez inventada, testimonios inventados,
precios «tachados» que nunca existieron y promesas de curar la ansiedad o el insomnio. TikTok y
Meta rechazan esos anuncios, traen devoluciones y contracargos, y con un público ansioso la
presión juega en contra. El precio tachado del prototipo (USD 14) es el precio real que sigue al
de lanzamiento en `06-monetizacion/oferta-soltar-el-dia.md`.

## Videos e imágenes (Leonardo, por Make)

- Veo 3 Fast por el módulo de Make daba «400 Invalid Request». **Kling 2.5 Turbo** funciona por
  la API: `POST /v1/generations-image-to-video` con `prompt`, `imageId`, `imageType: GENERATED`,
  `resolution: RESOLUTION_1080`, `width: 1080`, `height: 1920`, `duration: 5` y
  `model: KLING2_5`. Cuesta USD 0,35 (235 créditos) por 5 s.
- Las imágenes (Lucid Realism, 864×1536) cuestan USD 0,016 cada una.
- Gasto del 21/10: 3 videos y 5 imágenes, 760 créditos (USD 1,14). Quedan 1.341.
- Los archivos viajan de Leonardo a Drive (escenario 6698072) y de Drive a la sesión con el
  conector de Drive. Ese conector no baja más de 10 MB ni respuestas muy grandes, así que los
  videos (14 a 17 MB) se traen en partes de 3 MB con el escenario 6726269 («Guardar parte de
  archivo en Drive», con la cabecera `Range`) y se unen.
- Al cerrar la laptop, Kling dibujó el logo de Apple: ese video se recortó a 4:5.
- Para la web, cada video es un bucle de ida y vuelta de 10 s, a 720 px (0,8 a 2 MB).

## Falta decidir

- El producto y el precio. En el prototipo está «Soltar el día» a USD 9 de lanzamiento, como en
  `06-monetizacion/oferta-soltar-el-dia.md`.
- La plataforma de pago (Hotmart o Payhip).
- Tres comentarios reales de TikTok, con permiso de quien los escribió.
- Pasarlo a `web/` (estudioarmonia.com) y medirlo con el embudo.
