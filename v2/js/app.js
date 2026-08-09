/**
 * El borde de la v2.0: arranca, carga los datos, resuelve la ruta y pinta.
 *
 * Es el **único** sitio donde se lee el reloj y la URL del navegador (§10 del protocolo). Todo lo que
 * calcula recibe la temporada y los resultados por parámetro, y por eso se puede verificar con datos fijos.
 */

import { conBase, configurarBase, resolver, VISTAS } from './router.js';
import { animar, movimientoReducido, seguirScroll } from './ui/animacion.js';
import { cargarResultados, cargarInstantaneas } from './data/results.js';
import { pintarReglas } from './ui/reglas.js';
import { pintarDatos } from './ui/datos.js';
import { pintarHoy } from './ui/hoy.js';
import { pintarJugador } from './ui/jugador.js';
import { pintarTemporada } from './ui/temporada.js';
import { pintarTemporadas } from './ui/temporadas.js';
import {
  pintarCargando,
  pintarDesconocida,
  pintarError,
  pintarNavegacion,
  pintarPendiente,
  pintarSelector,
} from './ui/shell.js';

/** Qué slice traerá cada vista. Se va vaciando a medida que se implementan. */
const PENDIENTES = {
  [VISTAS.TEMPORADA]: 'clasificacion-de-temporada',
};

/**
 * Las temporadas que existen, según las instantáneas.
 *
 * Salen de la instantánea y **no de los resultados crudos**: el modelo agrupa todo lo anterior al límite en
 * la temporada 0, así que derivarlas del mes de cada fila listaba nueve temporadas que ya no existen.
 */
export function temporadasDe(instantaneas) {
  return [...instantaneas.entries()]
    .map(([id, carga]) => ({ id, etiqueta: carga.etiqueta ?? id, ordinal: carga.ordinal ?? 0 }))
    .sort((a, b) => b.ordinal - a.ordinal);
}

/**
 * La temporada que toca mostrar.
 *
 * Si la ruta no la fija, es la más reciente **de los datos** y no la del reloj: así la vista es
 * reproducible y no queda vacía el día 1 de un mes en que nadie ha jugado todavía.
 */
export function temporadaEfectiva(destino, temporadas) {
  return destino.temporada ?? temporadas[0]?.id ?? null;
}

function elementos() {
  return {
    navegacion: document.querySelector('[data-navegacion]'),
    selector: document.querySelector('[data-selector-temporada]'),
    vista: document.querySelector('[data-vista]'),
  };
}

/**
 * Pinta una vista y le pone el movimiento.
 *
 * El movimiento se arranca **aquí y no en cada vista**: es un envoltorio alrededor del despacho, así que
 * ninguna vista tiene que acordarse de llamarlo y no hay forma de que una se quede quieta por olvido.
 */
function pintar(destino, resultados, instantaneas) {
  despachar(destino, resultados, instantaneas);
  animar(elementos().vista);
}

function despachar(destino, resultados, instantaneas) {
  const { navegacion, selector, vista } = elementos();
  const temporadas = temporadasDe(instantaneas);
  const actual = temporadaEfectiva(destino, temporadas);

  pintarNavegacion(navegacion, { ...destino, temporada: actual });
  pintarSelector(selector, temporadas, destino.temporada);

  if (destino.vista === VISTAS.DESCONOCIDA) {
    pintarDesconocida(vista, destino);
    return;
  }
  if (destino.vista === VISTAS.TEMPORADA) {
    pintarTemporada(vista, instantaneas.get(actual), actual);
    return;
  }
  if (destino.vista === VISTAS.DATOS) {
    pintarDatos(vista, resultados, instantaneas);
    return;
  }
  if (destino.vista === VISTAS.TEMPORADAS) {
    pintarTemporadas(vista, instantaneas);
    return;
  }
  if (destino.vista === VISTAS.HOY) {
    // La jornada abierta no está materializada: esta vista lee las filas crudas (excepción del ADR 0008).
    pintarHoy(vista, resultados, instantaneas, actual);
    return;
  }
  if (destino.vista === VISTAS.JUGADOR) {
    // La ficha necesita TODAS las instantáneas, no solo la de la temporada: el palmarés se arma cruzándolas.
    pintarJugador(vista, instantaneas, actual, destino.jugador);
    return;
  }
  if (destino.vista === VISTAS.REGLAS) {
    // Las reglas viajan con la temporada: se leen de la que se esté mirando, así que una cerrada
    // explica las que se le aplicaron y no las de hoy.
    const carga = instantaneas.get(actual);
    pintarReglas(vista, carga?.reglas, actual);
    return;
  }
  pintarPendiente(vista, { ...destino, temporada: actual }, PENDIENTES[destino.vista]);
}

/**
 * Navega sin recargar y vuelve a pintar.
 *
 * Con `startViewTransition` el navegador funde la vista vieja con la nueva. Se pide **solo si existe y si
 * no hay preferencia de movimiento reducido**; si falta cualquiera de las dos cosas se pinta directamente,
 * que es exactamente lo que hacía antes.
 */
function navegar(ruta, resultados, instantaneas) {
  window.history.pushState({}, '', ruta);
  const pintarAhora = () => pintar(resolver(ruta), resultados, instantaneas);

  if (!document.startViewTransition || movimientoReducido()) {
    pintarAhora();
    return;
  }
  document.startViewTransition(pintarAhora);
}

export async function arrancar() {
  // El prefijo se lee del propio documento: `<base href="/2/">` lo declara y aquí se recoge, así que la web
  // funciona montada donde sea sin recompilar nada ni configurar nada. Es lo primero que pasa, antes de que
  // cualquier vista construya un enlace.
  configurarBase(new URL('.', document.baseURI).pathname);

  const { vista } = elementos();
  pintarCargando(vista);

  let resultados;
  let instantaneas;
  try {
    [resultados, instantaneas] = await Promise.all([cargarResultados(), cargarInstantaneas()]);
  } catch (error) {
    pintarError(vista, error.message);
    return;
  }

  pintar(resolver(window.location.pathname), resultados, instantaneas);
  seguirScroll();

  // Los enlaces internos se interceptan para que el router los resuelva sin ir al servidor.
  document.addEventListener('click', (evento) => {
    const enlace = evento.target.closest('a[href^="/"]');
    if (!enlace || enlace.target === '_blank' || evento.metaKey || evento.ctrlKey) return;
    evento.preventDefault();
    navegar(enlace.getAttribute('href'), resultados, instantaneas);
  });

  document.querySelector('[data-selector-temporada]').addEventListener('change', (evento) => {
    const temporada = evento.target.value;
    navegar(conBase(temporada ? `/t/${temporada}` : '/'), resultados, instantaneas);
  });

  window.addEventListener('popstate', () => {
    pintar(resolver(window.location.pathname), resultados, instantaneas);
  seguirScroll();
  });
}

if (typeof window !== 'undefined') {
  arrancar();
}
