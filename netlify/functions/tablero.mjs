// El tablero del embudo: https://estudioarmonia.com/api/embudo?clave=…
// La clave es la variable EMBUDO_CLAVE de Netlify; sin ella, el tablero no abre.
import { getStore } from '@netlify/blobs';
import { ALMACEN, manejarEmbudo } from '../lib/embudo.mjs';

export default (req) =>
  manejarEmbudo(req, getStore(ALMACEN), globalThis.Netlify?.env.get('EMBUDO_CLAVE') ?? process.env.EMBUDO_CLAVE);

export const config = { path: '/api/embudo' };
