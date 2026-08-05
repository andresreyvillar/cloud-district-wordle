/**
 * El borde de la v2.0: arranca, carga los datos, resuelve la ruta y pinta.
 *
 * Es el **único** sitio donde se lee el reloj y la URL del navegador (§10 del protocolo). Todo lo que
 * calcula recibe la temporada y los resultados por parámetro, y por eso se puede verificar con datos fijos.
 */

import { resolver, VISTAS } from './router.js';
import { cargarResultados, cargarInstantaneas } from './data/results.js';
import { pintarReglas } from './ui/reglas.js';
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
  [VISTAS.TEMPORADAS]: 'archivo-de-temporadas',
  [VISTAS.HOY]: 'resultado-del-dia',
  [VISTAS.DATOS]: 'tabla-de-datos',
  [VISTAS.JUGADOR]: 'ficha-de-jugador',
};

/** Las temporadas que hay en los datos, de más reciente a más antigua. */
export function temporadasDe(resultados) {
  return [...new Set(resultados.map((fila) => fila.temporada))].sort().reverse();
}

/**
 * La temporada que toca mostrar.
 *
 * Si la ruta no la fija, es la más reciente **de los datos** y no la del reloj: así la vista es
 * reproducible y no queda vacía el día 1 de un mes en que nadie ha jugado todavía.
 */
export function temporadaEfectiva(destino, temporadas) {
  return destino.temporada ?? temporadas[0] ?? null;
}

function elementos() {
  return {
    navegacion: document.querySelector('[data-navegacion]'),
    selector: document.querySelector('[data-selector-temporada]'),
    vista: document.querySelector('[data-vista]'),
  };
}

function pintar(destino, resultados, instantaneas) {
  const { navegacion, selector, vista } = elementos();
  const temporadas = temporadasDe(resultados);
  const actual = temporadaEfectiva(destino, temporadas);

  pintarNavegacion(navegacion, { ...destino, temporada: actual });
  pintarSelector(selector, temporadas, destino.temporada);

  if (destino.vista === VISTAS.DESCONOCIDA) {
    pintarDesconocida(vista, destino);
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

/** Navega sin recargar y vuelve a pintar. */
function navegar(ruta, resultados, instantaneas) {
  window.history.pushState({}, '', ruta);
  pintar(resolver(ruta), resultados, instantaneas);
}

export async function arrancar() {
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

  // Los enlaces internos se interceptan para que el router los resuelva sin ir al servidor.
  document.addEventListener('click', (evento) => {
    const enlace = evento.target.closest('a[href^="/"]');
    if (!enlace || enlace.target === '_blank' || evento.metaKey || evento.ctrlKey) return;
    evento.preventDefault();
    navegar(enlace.getAttribute('href'), resultados, instantaneas);
  });

  document.querySelector('[data-selector-temporada]').addEventListener('change', (evento) => {
    const temporada = evento.target.value;
    navegar(temporada ? `/t/${temporada}` : '/', resultados, instantaneas);
  });

  window.addEventListener('popstate', () => {
    pintar(resolver(window.location.pathname), resultados, instantaneas);
  });
}

if (typeof window !== 'undefined') {
  arrancar();
}
