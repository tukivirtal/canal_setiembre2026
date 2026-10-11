// Recibe los eventos de la página (la visita, el botón, los audios, cuánto se quedaron) y los
// anota en el embudo. La lógica está en netlify/lib/embudo.mjs.
import { getStore } from '@netlify/blobs';
import { ALMACEN, manejarEvento } from '../lib/embudo.mjs';

export default (req, context) => manejarEvento(req, context, getStore(ALMACEN));

export const config = { path: '/api/evento' };
