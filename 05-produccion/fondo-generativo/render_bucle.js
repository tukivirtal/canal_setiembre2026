#!/usr/bin/env node
/**
 * Renderiza el fondo generativo a fotogramas PNG usando Chromium sin interfaz.
 *
 * El bucle dura 48 s exactos (4 respiraciones a 5/min = un intervalo de cuenco).
 * El script NO depende del reloj: le pide a la página que pinte un instante
 * concreto, así que los fotogramas son deterministas y el último empalma con
 * el primero al milisegundo.
 *
 *   npm i playwright          (los navegadores ya están en Codespaces)
 *   node render_bucle.js
 *   node render_bucle.js --fps 30            (los valores del canal ya son
 *                                             nitidez 0.85 y densidad 200)
 *   node render_bucle.js --salida frames/ --ancho 1920 --alto 1080
 *
 * Después, con ffmpeg:
 *   ffmpeg -framerate 25 -i frames/f%05d.png -c:v libx264 -crf 18 \
 *     -pix_fmt yuv420p -preset slow bucle48.mp4
 *   ffmpeg -stream_loop -1 -i bucle48.mp4 -i audio/OBRA-001.wav \
 *     -c:v copy -c:a aac -b:a 320k -shortest video/OBRA-001.mp4
 *
 * `-c:v copy` en el segundo paso es lo que hace que esto sea barato: el video
 * no se recodifica, solo se repite. Una obra de 3 horas se monta en segundos.
 */

const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

// ---------------------------------------------------------------------------

/** Chromium ya instalado en el sistema, si lo hay. */
function buscarChrome() {
  const base = process.env.PLAYWRIGHT_BROWSERS_PATH;
  if (!base || !fs.existsSync(base)) return null;
  const dirs = fs.readdirSync(base)
    .filter((d) => d.startsWith("chromium-"))
    .sort()
    .reverse();
  for (const d of dirs) {
    const bin = path.join(base, d, "chrome-linux", "chrome");
    if (fs.existsSync(bin)) return bin;
  }
  return null;
}

function args() {
  const a = process.argv.slice(2);
  const o = {
    pagina: path.join(__dirname, "campo-motas.html"),
    salida: "frames",
    ancho: 1920,
    alto: 1080,
    fps: 25,
    // Parámetros visuales: los mismos nombres que los controles de la página,
    // para poder copiar los valores que te gustaron y renderizar eso exacto.
    dens: 200,
    vel: 1,
    resp: 5,
    brillo: 1,
    nitidez: 0.85,
    ondas: true,
    destellos: true,
    marca: true,
    // Ruta al binario de Chromium. Vacío = el que Playwright traiga por
    // defecto. Hace falta cuando la versión de Playwright no coincide con
    // los navegadores ya instalados, que es lo normal en entornos
    // preconfigurados: evita descargar 150 MB para nada.
    chrome: "",
  };
  for (let i = 0; i < a.length; i += 2) {
    const k = a[i].replace(/^--/, "");
    if (!(k in o)) {
      console.error(`Parámetro desconocido: ${a[i]}`);
      console.error(`Válidos: ${Object.keys(o).join(", ")}`);
      process.exit(1);
    }
    const v = a[i + 1];
    o[k] = typeof o[k] === "boolean" ? v !== "false"
         : typeof o[k] === "number" ? parseFloat(v)
         : v;
  }
  return o;
}

async function main() {
  const o = args();

  if (!fs.existsSync(o.pagina)) {
    console.error(`No encuentro la página: ${o.pagina}`);
    process.exit(1);
  }
  fs.mkdirSync(o.salida, { recursive: true });

  const lanzar = { args: ["--force-color-profile=srgb", "--disable-lcd-text"] };
  const chrome = o.chrome || buscarChrome();
  if (chrome) {
    lanzar.executablePath = chrome;
    console.log(`chromium: ${chrome}`);
  }
  const navegador = await chromium.launch(lanzar);
  const pagina = await navegador.newPage({
    viewport: { width: o.ancho, height: o.alto },
    deviceScaleFactor: 1,
  });

  const url = new URL("file://" + path.resolve(o.pagina));
  url.searchParams.set("render", "1");
  if (!o.marca) url.searchParams.set("marca", "0");
  await pagina.goto(url.href, { waitUntil: "networkidle" });

  // La fuente del sello tarda un momento; sin esperarla, los primeros
  // fotogramas saldrían con la tipografía de reserva y el sello daría un salto.
  await pagina.evaluate(() => document.fonts.ready);

  const visual = {
    dens: o.dens, vel: o.vel, resp: o.resp,
    brillo: o.brillo, nitidez: o.nitidez,
    ondas: o.ondas, destellos: o.destellos,
  };
  await pagina.evaluate((c) => {
    window.RIN.medir();
    window.RIN.config(c);
  }, visual);

  const LOOP = await pagina.evaluate(() => window.RIN.LOOP);
  const total = Math.round(LOOP * o.fps);

  console.log(`bucle de ${LOOP} s · ${o.fps} fps · ${total} fotogramas · ${o.ancho}x${o.alto}`);
  console.log(`nitidez ${o.nitidez} · densidad ${o.dens} · deriva ${o.vel}x · respiración ${o.resp}/min\n`);

  const t0 = Date.now();
  for (let i = 0; i < total; i++) {
    // El último fotograma NO es t = LOOP (sería idéntico al primero y el bucle
    // repetiría una imagen). Por eso i/total y no i/(total-1).
    await pagina.evaluate((t) => window.RIN.pintar(t), (i / total) * LOOP);
    await pagina.screenshot({
      path: path.join(o.salida, `f${String(i).padStart(5, "0")}.png`),
      animations: "disabled",
    });

    if (i % 50 === 0 || i === total - 1) {
      const hechos = i + 1;
      const seg = (Date.now() - t0) / 1000;
      const queda = seg / hechos * (total - hechos);
      process.stdout.write(
        `\r  ${hechos}/${total}  ${(hechos / seg).toFixed(1)} fps  ` +
        `quedan ${Math.round(queda)} s      `
      );
    }
  }
  await navegador.close();

  const seg = ((Date.now() - t0) / 1000).toFixed(0);
  console.log(`\n\n${total} fotogramas en ${seg} s -> ${o.salida}/\n`);
  console.log("Siguiente paso:\n");
  console.log(`  ffmpeg -framerate ${o.fps} -i ${o.salida}/f%05d.png \\`);
  console.log(`    -c:v libx264 -crf 18 -pix_fmt yuv420p -preset slow bucle48.mp4\n`);
  console.log(`  ffmpeg -stream_loop -1 -i bucle48.mp4 -i audio/OBRA-001.wav \\`);
  console.log(`    -c:v copy -c:a aac -b:a 320k -shortest video/OBRA-001.mp4\n`);
}

main().catch((e) => {
  console.error("\n" + e.message);
  process.exit(1);
});
