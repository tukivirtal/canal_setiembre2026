// Un Excel (.xlsx) mínimo y sin dependencias, para bajar el tablero del embudo.
// Un .xlsx es un zip con las hojas en XML: acá se arma el XML y el zip (comprimido con el
// zlib de Node). Celdas: texto, números, porcentajes ({ pct: 0.12 }), fechas ({ fecha: '2026-10-19' },
// que Excel muestra en el formato de cada país) y títulos en negrita ({ titulo: 'texto' }); una celda
// vacía es null, undefined o ''.
import { deflateRawSync } from 'node:zlib';

const TABLA_CRC = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(datos) {
  let c = 0xffffffff;
  for (let i = 0; i < datos.length; i++) c = TABLA_CRC[(c ^ datos[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

export function zip(archivos, fecha = new Date()) {
  const hora = (fecha.getUTCHours() << 11) | (fecha.getUTCMinutes() << 5) | (fecha.getUTCSeconds() >> 1);
  const dia = ((fecha.getUTCFullYear() - 1980) << 9) | ((fecha.getUTCMonth() + 1) << 5) | fecha.getUTCDate();
  const locales = [], centrales = [];
  let desplazamiento = 0;
  for (const { nombre, contenido } of archivos) {
    const nombreBytes = Buffer.from(nombre, 'utf8');
    const datos = Buffer.from(contenido, 'utf8');
    const comprimido = deflateRawSync(datos);
    const crc = crc32(datos);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);           // versión necesaria
    local.writeUInt16LE(0x0800, 6);       // nombres en UTF-8
    local.writeUInt16LE(8, 8);            // deflate
    local.writeUInt16LE(hora, 10);
    local.writeUInt16LE(dia, 12);
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(comprimido.length, 18);
    local.writeUInt32LE(datos.length, 22);
    local.writeUInt16LE(nombreBytes.length, 26);
    const central = Buffer.alloc(46);     // extra, comentario, disco y atributos quedan en cero
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(20, 4);
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(0x0800, 8);
    central.writeUInt16LE(8, 10);
    central.writeUInt16LE(hora, 12);
    central.writeUInt16LE(dia, 14);
    central.writeUInt32LE(crc, 16);
    central.writeUInt32LE(comprimido.length, 20);
    central.writeUInt32LE(datos.length, 24);
    central.writeUInt16LE(nombreBytes.length, 28);
    central.writeUInt32LE(desplazamiento, 42);
    locales.push(local, nombreBytes, comprimido);
    centrales.push(central, nombreBytes);
    desplazamiento += local.length + nombreBytes.length + comprimido.length;
  }
  const fin = Buffer.alloc(22);
  fin.writeUInt32LE(0x06054b50, 0);
  fin.writeUInt16LE(archivos.length, 8);
  fin.writeUInt16LE(archivos.length, 10);
  fin.writeUInt32LE(centrales.reduce((n, b) => n + b.length, 0), 12);
  fin.writeUInt32LE(desplazamiento, 16);
  return Buffer.concat([...locales, ...centrales, fin]);
}

// Sin los caracteres de control que el XML no admite.
const esc = (t) => String(t).replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f￾￿]/g, '')
  .replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

function columna(n) {          // 0 → A, 25 → Z, 26 → AA
  let s = '';
  for (n += 1; n > 0; n = Math.floor((n - 1) / 26)) s = String.fromCharCode(65 + ((n - 1) % 26)) + s;
  return s;
}

function celda(v, ref) {
  if (v === null || v === undefined || v === '') return '';
  if (typeof v === 'number') return Number.isFinite(v) ? `<c r="${ref}"><v>${v}</v></c>` : '';
  if (typeof v === 'object' && 'pct' in v) return Number.isFinite(v.pct) ? `<c r="${ref}" s="2"><v>${v.pct}</v></c>` : '';
  if (typeof v === 'object' && 'fecha' in v) {
    const [a, m, d] = String(v.fecha).split('-').map(Number);
    const serie = Date.UTC(a, m - 1, d) / 864e5 + 25569;    // días desde el 30/12/1899, como cuenta Excel
    return Number.isFinite(serie) ? `<c r="${ref}" s="3"><v>${serie}</v></c>` : '';
  }
  const titulo = typeof v === 'object' && 'titulo' in v;
  return `<c r="${ref}" t="inlineStr"${titulo ? ' s="1"' : ''}><is><t xml:space="preserve">${esc(titulo ? v.titulo : v)}</t></is></c>`;
}

const XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n';
const NS = 'http://schemas.openxmlformats.org';

function hoja({ filas, anchos = [], fijarPrimera = false }) {
  const vista = fijarPrimera ? '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" ' +
    'activePane="bottomLeft" state="frozen"/><selection pane="bottomLeft" activeCell="A2" sqref="A2"/></sheetView></sheetViews>' : '';
  const cols = anchos.length ? `<cols>${anchos.map((w, i) => `<col min="${i + 1}" max="${i + 1}" width="${w}" customWidth="1"/>`).join('')}</cols>` : '';
  const datos = filas.map((fila, i) => `<row r="${i + 1}">${fila.map((v, j) => celda(v, columna(j) + (i + 1))).join('')}</row>`).join('');
  return `${XML}<worksheet xmlns="${NS}/spreadsheetml/2006/main">${vista}${cols}<sheetData>${datos}</sheetData></worksheet>`;
}

// 0: normal · 1: negrita · 2: porcentaje sin decimales · 3: fecha corta del país
const ESTILOS = `${XML}<styleSheet xmlns="${NS}/spreadsheetml/2006/main">` +
  '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>' +
  '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>' +
  '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>' +
  '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>' +
  '<cellXfs count="4"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>' +
  '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>' +
  '<xf numFmtId="9" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>' +
  '<xf numFmtId="14" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs>' +
  '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>';

// hojas: [{ nombre, filas: [[celda, …], …], anchos: [ancho de cada columna], fijarPrimera }]
export function excel(hojas) {
  const nombres = hojas.map((h) => h.nombre.replace(/[[\]:*?/\\]/g, ' ').slice(0, 31));
  const tipo = (t) => `application/vnd.openxmlformats-officedocument.spreadsheetml.${t}+xml`;
  return zip([
    { nombre: '[Content_Types].xml', contenido: `${XML}<Types xmlns="${NS}/package/2006/content-types">` +
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>' +
      '<Default Extension="xml" ContentType="application/xml"/>' +
      `<Override PartName="/xl/workbook.xml" ContentType="${tipo('sheet.main')}"/>` +
      `<Override PartName="/xl/styles.xml" ContentType="${tipo('styles')}"/>` +
      hojas.map((_, i) => `<Override PartName="/xl/worksheets/sheet${i + 1}.xml" ContentType="${tipo('worksheet')}"/>`).join('') +
      '</Types>' },
    { nombre: '_rels/.rels', contenido: `${XML}<Relationships xmlns="${NS}/package/2006/relationships">` +
      `<Relationship Id="rId1" Type="${NS}/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>` },
    { nombre: 'xl/workbook.xml', contenido: `${XML}<workbook xmlns="${NS}/spreadsheetml/2006/main" ` +
      `xmlns:r="${NS}/officeDocument/2006/relationships"><bookViews><workbookView/></bookViews><sheets>` +
      nombres.map((n, i) => `<sheet name="${esc(n)}" sheetId="${i + 1}" r:id="rId${i + 1}"/>`).join('') + '</sheets></workbook>' },
    { nombre: 'xl/_rels/workbook.xml.rels', contenido: `${XML}<Relationships xmlns="${NS}/package/2006/relationships">` +
      hojas.map((_, i) => `<Relationship Id="rId${i + 1}" Type="${NS}/officeDocument/2006/relationships/worksheet" ` +
        `Target="worksheets/sheet${i + 1}.xml"/>`).join('') +
      `<Relationship Id="rId${hojas.length + 1}" Type="${NS}/officeDocument/2006/relationships/styles" Target="styles.xml"/>` +
      '</Relationships>' },
    { nombre: 'xl/styles.xml', contenido: ESTILOS },
    ...hojas.map((h, i) => ({ nombre: `xl/worksheets/sheet${i + 1}.xml`, contenido: hoja(h) })),
  ]);
}
