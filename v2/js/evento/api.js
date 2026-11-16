/**
 * La API del juego del evento: solo funciones de la base de datos, nunca tablas.
 *
 * Slices: `frase-del-evento` y `pantalla-del-evento`. La clave pública no lee ni escribe ninguna tabla del evento:
 * la solución de una frase no puede llegar al navegador, así que todo pasa por funciones que devuelven lo que se
 * puede ver.
 *
 * **En local habla con el servidor local** (`tools/evento_local.py`), que emula `/rest/v1/rpc` sobre un Postgres
 * desechable: así el evento se prueba entero, también desde el móvil en la misma wifi, sin tocar Supabase.
 */

import { SUPABASE_PUBLISHABLE_KEY, SUPABASE_URL } from '../data/results.js';

/**
 * El evento que juega la web publicada. El de prueba (`prueba`, con su PIN en el repositorio) **solo** se juega en
 * local: si alguien lo cargara en Supabase, cualquiera podría empezarlo. Se puede cambiar con `?evento=`.
 */
export const EVENTO_PUBLICADO = 'evento-2026-11-20';
export const EVENTO_DE_PRUEBA = 'prueba';

/** Un host local o de la red de casa: `localhost`, `127.0.0.1`, `192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`. */
export function esLocal(hostname) {
  return /^(localhost|127\.\d+\.\d+\.\d+|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)$/
    .test(String(hostname ?? ''));
}

/** Contra qué servidor habla el evento: el local si la página se sirve en local, Supabase si no. */
export function servidorDelEvento(ubicacion) {
  return esLocal(ubicacion.hostname) ? ubicacion.origin : SUPABASE_URL;
}

/** Un fallo de la API. `rechazo` es que el servidor dijo que no (y por qué); `red` es que no contestó. */
export class FalloDelEvento extends Error {
  constructor(mensaje, tipo) {
    super(mensaje);
    this.tipo = tipo;
  }
}

/** Lo que se espera a una respuesta. Una petición colgada no deja el teclado bloqueado: pasado el plazo cuenta
 * como sin red, y reenviar es seguro porque cada palabra lleva su número (`p_numero`). */
export const PLAZO_MS = 10_000;

/** Un código SQLSTATE: cinco cifras o mayúsculas. Los de PostgREST (`PGRST…`) y los vacíos no lo son. */
export function esRechazo(codigo) {
  return /^[0-9A-Z]{5}$/.test(String(codigo ?? ''));
}

async function llamar(cliente, funcion, argumentos, plazo = PLAZO_MS) {
  let respuesta;
  let reloj;
  try {
    const agotado = new Promise((_, rechazar) => {
      reloj = setTimeout(() => rechazar(new Error('el servidor tarda demasiado')), plazo);
    });
    respuesta = await Promise.race([cliente.rpc(funcion, argumentos), agotado]);
  } catch (error) {
    throw new FalloDelEvento(String(error?.message ?? error), 'red');
  } finally {
    clearTimeout(reloj);
  }
  const { data, error } = respuesta;
  if (error) {
    // Con un código SQLSTATE (`22023` y compañía) la base de datos contestó que no; sin él, no hubo respuesta útil
    // (sin red, servidor caído) y lo escrito no se pierde.
    throw new FalloDelEvento(error.message ?? 'error desconocido', esRechazo(error.code) ? 'rechazo' : 'red');
  }
  return data;
}

/** La API sobre un cliente con `rpc(funcion, argumentos)`. Los tests le pasan uno falso. */
export function apiDelEvento(cliente, evento, plazo = PLAZO_MS) {
  const llamar_ = (funcion, argumentos) => llamar(cliente, funcion, argumentos, plazo);
  return {
    evento,
    unirse: (nombre, token, clave = null) =>
      llamar_('unirse_al_evento', { p_evento: evento, p_nombre: nombre, p_token: token, p_clave: clave }),
    // Con contraseña, el estado y el ranking solo llegan con el token de un participante o con la contraseña.
    estado: (token = null, clave = null) => llamar_('estado_del_evento', { p_evento: evento, p_token: token, p_clave: clave }),
    miPartida: (token) => llamar_('mi_partida_del_evento', { p_evento: evento, p_token: token }),
    empezar: (token, orden) => llamar_('empezar_frase', { p_evento: evento, p_token: token, p_orden: orden }),
    intentar: (token, orden, palabra, numero) => llamar_('intentar_palabra',
      { p_evento: evento, p_token: token, p_orden: orden, p_palabra: palabra, p_numero: numero }),
    terminarEvento: (pin) => llamar_('terminar_evento', { p_evento: evento, p_pin: pin }),
    empezarEvento: (pin) => llamar_('empezar_evento', { p_evento: evento, p_pin: pin }),
    ranking: (token = null, clave = null) => llamar_('ranking_del_evento', { p_evento: evento, p_token: token, p_clave: clave }),
  };
}

/** La API real. Se crea en el borde, con la ubicación de la página. */
export async function apiReal(ubicacion) {
  // Versión fija: el día del evento no puede cambiar la librería por debajo.
  const { createClient } = await import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/+esm');
  const evento = new URLSearchParams(ubicacion.search).get('evento')
    || (esLocal(ubicacion.hostname) ? EVENTO_DE_PRUEBA : EVENTO_PUBLICADO);
  return apiDelEvento(createClient(servidorDelEvento(ubicacion), SUPABASE_PUBLISHABLE_KEY), evento);
}
