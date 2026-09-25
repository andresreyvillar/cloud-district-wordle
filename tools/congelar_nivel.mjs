#!/usr/bin/env node
/**
 * Congela el nivel de SuperWordleBros de la última jornada asentada en `game_levels`.
 *
 * Slice: `nivel-congelado` (openspec/slices/dashboard/nivel-congelado.md).
 *
 *     node tools/congelar_nivel.mjs                              # fecha y hora de Madrid, ahora
 *     node tools/congelar_nivel.mjs --hoy 2026-09-25 --hora 04:10 --seco
 *
 * El nivel sale del **mismo** `nivelDe` que usa la web (`v2/js/domain/superbros.js`): una sola
 * implementación. Lo ejecuta el cron de sincronización tras cada vuelta, con `SUPABASE_URL` y
 * `SUPABASE_SERVICE_ROLE_KEY` en el entorno —los secretos del workflow, los mismos que usa `add_results.py`—.
 *
 * **Toca producción**: escribe en `game_levels`. Nunca reescribe una jornada ya congelada —la inserción ignora
 * el duplicado, y la base de datos rechaza cualquier cambio—, y dice qué va a escribir antes de escribirlo.
 */

import { pathToFileURL } from 'node:url';

import { normalizar } from '../v2/js/data/results.js';
import { fechaDe, jornadaACongelar, nivelDe } from '../v2/js/domain/superbros.js';

/** Cuántos días atrás se leen resultados. Sobra: el cron congela la de ayer o, como mucho, la de anteayer. */
const DIAS_DE_MARGEN = 10;

const COLUMNAS = 'slack_user_id,player_name,wordle_id,score,date,pattern';

function restarDias(fecha, dias) {
  const [a, m, d] = fecha.split('-').map(Number);
  return new Date(Date.UTC(a, m - 1, d - dias)).toISOString().slice(0, 10);
}

/** La fecha y la hora de Madrid ahora. **El único reloj del script**, y solo en el borde. */
export function ahoraEnMadrid(ahora = new Date()) {
  const partes = Object.fromEntries(
    new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
    }).formatToParts(ahora).map(({ type, value }) => [type, value]),
  );
  return { hoy: `${partes.year}-${partes.month}-${partes.day}`, hora: `${partes.hour}:${partes.minute}` };
}

/**
 * Hace el trabajo. Todo entra por parámetro —`fetch`, credenciales, fecha, hora— para poder probarlo sin red.
 * Devuelve `{ accion, jornada }`, con `accion` en `congelado | ya-congelado | todavia-no | sin-cuadriculas | seco`.
 */
export async function congelar({ fetch, url, clave, hoy, hora, seco, log }) {
  const cabeceras = { apikey: clave, Authorization: `Bearer ${clave}` };
  const pedir = async (ruta, opciones = {}) => {
    const respuesta = await fetch(`${url}/rest/v1/${ruta}`, { ...opciones, headers: { ...cabeceras, ...opciones.headers } });
    // **Solo el `message`, nunca el cuerpo entero.** El log del cron es público —el repositorio lo es—, y el
    // `details` de un error de Postgres puede traer la fila rechazada, con los nombres del nivel.
    if (!respuesta.ok) {
      const cuerpo = await respuesta.text();
      let motivo = 'sin detalle';
      try {
        motivo = JSON.parse(cuerpo).message ?? motivo;
      } catch {
        // cuerpo que no es JSON: no se copia al log
      }
      throw new Error(`PostgREST ${respuesta.status}: ${motivo}`);
    }
    return respuesta.json();
  };

  const desde = restarDias(hoy, DIAS_DE_MARGEN);
  const filas = await pedir(
    `wordle_results?select=${COLUMNAS}&date=gte.${desde}&date=lt.${hoy}&order=wordle_id.asc`,
  );
  const resultados = filas.map(normalizar);

  const jornada = jornadaACongelar(resultados, hoy, hora);
  if (jornada === null) {
    log(`nada que congelar: no hay jornadas asentadas entre ${desde} y ${hoy} ${hora}`);
    return { accion: 'todavia-no', jornada: null };
  }

  const existentes = await pedir(`game_levels?select=jornada&jornada=eq.${jornada}`);
  if (existentes.length) {
    log(`#${jornada} ya está congelada: no se toca`);
    return { accion: 'ya-congelado', jornada };
  }

  const nivel = nivelDe(resultados, jornada);
  if (!nivel) {
    log(`#${jornada} no tiene a nadie con cuadrícula: no hay nivel que congelar`);
    return { accion: 'sin-cuadriculas', jornada };
  }

  const fecha = fechaDe(resultados, jornada);
  log(`congelo #${jornada} · ${fecha} · ${nivel.labels.length} tramos · ${nivel.collectibles.length} estrellas`);
  if (seco) {
    log('--seco: no se escribe');
    return { accion: 'seco', jornada };
  }

  const escritas = await pedir('game_levels?on_conflict=jornada', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Prefer: 'resolution=ignore-duplicates,return=representation' },
    body: JSON.stringify({ jornada, fecha, nivel }),
  });
  // Otra vuelta pudo congelarla entre la consulta y la escritura. El duplicado se ignora y se dice.
  if (!escritas.length) {
    log(`#${jornada} la congeló otra ejecución a la vez: no se toca`);
    return { accion: 'ya-congelado', jornada };
  }
  log(`#${jornada} congelada`);
  return { accion: 'congelado', jornada };
}

function argumento(nombre) {
  const indice = process.argv.indexOf(`--${nombre}`);
  return indice > 0 ? process.argv[indice + 1] : undefined;
}

async function principal() {
  const url = process.env.SUPABASE_URL;
  const clave = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !clave) {
    console.error('faltan SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en el entorno');
    process.exit(2);
  }
  const ahora = ahoraEnMadrid();
  await congelar({
    fetch: globalThis.fetch,
    url,
    clave,
    hoy: argumento('hoy') ?? ahora.hoy,
    hora: argumento('hora') ?? ahora.hora,
    seco: process.argv.includes('--seco'),
    log: (linea) => console.log(`   nivel: ${linea}`),
  });
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  principal().catch((error) => {
    console.error(`   nivel: ${error.message}`);
    process.exit(1);
  });
}
