/**
 * La ficha de un jugador: una proyección de las instantáneas, no un cálculo nuevo.
 *
 * Slice: `ficha-de-jugador` (openspec/slices/estadisticas/ficha-de-jugador.md).
 *
 * Funciones **puras**: entran las instantáneas y salen objetos. Ni reloj, ni DOM, ni red, y por eso los
 * escenarios se verifican con `node --test` sin navegador (§10 del protocolo).
 *
 * Todo lo que la ficha muestra de una temporada está ya dentro de su instantánea, que es lo que publica el
 * bot ([ADR 0008](../../../openspec/decisions/0008-donde-vive-el-calculo.md)): la media, el desglose por
 * jornada, la distribución y las medallas. Aquí no se recalcula ninguna, **se seleccionan**. Lo único que se
 * arma es el palmarés, cruzando las instantáneas que la web ya tiene cargadas.
 */

import { conBase } from '../router.js';
import { escalaDeDistribucion } from './escala.js';

/** Los decimales con los que se publica una diferencia de medias. Más no significan nada al leerlas. */
const DECIMALES = 2;

function redondear(valor, decimales = DECIMALES) {
  const factor = 10 ** decimales;
  return Math.round(valor * factor) / factor;
}

/** La ruta canónica de una ficha. El identificador es el de Slack: un renombre no rompe el enlace. */
export function rutaDeFicha(temporada, jugador) {
  return conBase(`/t/${temporada}/j/${jugador}`);
}

function filaDe(carga, jugador) {
  return (carga?.clasificacion ?? []).find((fila) => fila.jugador === jugador) ?? null;
}

/**
 * Las temporadas en que ese jugador tiene resultados, de la más reciente a la más antigua.
 *
 * Ordena por `ordinal` y no por el identificador: la temporada 0 es un bloque histórico y ordenarla como
 * cadena la pondría antes de `2026-08`, que es justo al revés de lo que cuenta.
 */
export function palmares(instantaneas, jugador, actual = null) {
  return [...instantaneas.entries()]
    .map(([temporada, carga]) => ({ temporada, carga, fila: filaDe(carga, jugador) }))
    .filter(({ fila }) => fila !== null)
    .map(({ temporada, carga, fila }) => ({
      temporada,
      etiqueta: carga.etiqueta ?? temporada,
      ordinal: carga.ordinal ?? 0,
      estado: carga.estado ?? null,
      posicion: fila.posicion ?? null,
      clasificado: fila.clasificado !== false,
      media_temporada: fila.media_temporada,
      media_jugada: fila.media_jugada,
      jugados: fila.jugados,
      dias: fila.dias,
      actual: temporada === actual,
    }))
    .sort((a, b) => b.ordinal - a.ordinal);
}

/** El nombre con el que ese jugador aparece en cualquier temporada, o su identificador si no aparece. */
function nombreConocido(instantaneas, jugador) {
  for (const carga of instantaneas.values()) {
    const fila = filaDe(carga, jugador);
    if (fila) return fila.nombre;
  }
  return jugador;
}

/** Las medallas que ese jugador ganó en esa temporada. */
function medallasDe(carga, nombre) {
  return Object.entries(carga?.logros ?? {})
    .filter(([, quienes]) => (quienes ?? []).includes(nombre))
    .map(([clave]) => clave);
}

/**
 * La ficha de un jugador en una temporada.
 *
 * Devuelve siempre un objeto: `existe: false` cuando ese jugador no jugó esa temporada, con las temporadas
 * en que sí lo hizo. Con el fallback SPA del Worker cualquier ruta devuelve 200, así que la vista **tiene**
 * que saber decir "aquí no hay nada" por su cuenta.
 */
export function ficha(instantaneas, temporada, jugador) {
  const carga = instantaneas.get(temporada) ?? null;
  const fila = filaDe(carga, jugador);
  const etiqueta = carga?.etiqueta ?? temporada;

  if (!fila) {
    return {
      existe: false,
      jugador,
      nombre: nombreConocido(instantaneas, jugador),
      temporada,
      etiqueta,
      otras: palmares(instantaneas, jugador, temporada),
    };
  }

  // Una temporada que no imputa no tiene ausencias con nota, así que no hay coste que comparar: la 0 se
  // ordena por lo que cada uno jugó de verdad. Inventar aquí un cero diría "faltar no te costó nada"
  // cuando lo cierto es que en esa temporada faltar no se medía.
  const imputa = carga.imputada !== false;
  const imputadas = fila.por_dia.filter((dia) => dia.imputado).length;

  return {
    existe: true,
    jugador,
    nombre: fila.nombre,
    temporada,
    etiqueta,
    ordinal: carga.ordinal ?? 0,
    estado: carga.estado ?? null,
    imputa,
    imputadas,
    coste_de_faltar: imputa ? redondear(fila.media_temporada - fila.media_jugada) : null,
    posicion: fila.posicion ?? null,
    clasificado: fila.clasificado !== false,
    media_temporada: fila.media_temporada,
    media_jugada: fila.media_jugada,
    media_grupo: carga.media_grupo ?? null,
    jugados: fila.jugados,
    dias: fila.dias,
    mejor: fila.mejor,
    peor: fila.peor,
    distribucion: fila.distribucion ?? [],
    // La escala del gráfico sale de la temporada entera, para que dos fichas se puedan comparar.
    escala_distribucion: escalaDeDistribucion(carga.clasificacion),
    por_dia: fila.por_dia,
    medallas: medallasDe(carga, fila.nombre),
    palmares: palmares(instantaneas, jugador, temporada),
  };
}
