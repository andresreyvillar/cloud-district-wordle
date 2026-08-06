/**
 * El archivo de temporadas y el medallero acumulado.
 *
 * Slice: `archivo-de-temporadas` (openspec/slices/ranking/archivo-de-temporadas.md).
 *
 * Funciones **puras**: entran las instantáneas y salen listas. No calculan clasificaciones ni medallas —eso
 * viene materializado (ADR 0008)—; agrupan y suman lo que ya está publicado.
 */

/** El identificador de la temporada histórica. El mismo que `tools/seasons.py::TEMPORADA_CERO`. */
const TEMPORADA_CERO = '0';

const EN_CURSO = 'en curso';

/**
 * Una entrada por temporada materializada, de la más reciente a la más antigua.
 *
 * Ordena por `ordinal`, no por el identificador: la temporada 0 es un bloque histórico y ordenarla como
 * cadena la pondría antes de `2026-08`, que es exactamente al revés.
 */
export function archivo(instantaneas) {
  return [...instantaneas.entries()]
    .map(([temporada, carga]) => {
      const tabla = carga.clasificacion ?? [];
      const primero = tabla.find((fila) => fila.clasificado !== false) ?? null;
      const cerrada = carga.estado !== EN_CURSO;

      return {
        temporada,
        ruta: `/t/${temporada}`,
        etiqueta: carga.etiqueta ?? temporada,
        ordinal: carga.ordinal ?? 0,
        estado: carga.estado ?? null,
        cerrada,
        // La 0 se jugó con otras reglas: sin imputar y contando todas las jornadas. Presentarla junto a los
        // meses sin marcarla invitaría a comparar 181 jornadas sin imputar con 20 imputadas.
        historica: temporada === TEMPORADA_CERO,
        imputada: carga.imputada !== false,
        jornadas: (carga.dias ?? []).length,
        jugadores: (carga.jugadores ?? []).length,
        resultados: carga.resultados ?? 0,
        media_grupo: carga.media_grupo ?? null,
        // Una temporada abierta no ha coronado a nadie: tiene quien va ganando, que no es lo mismo.
        campeon: cerrada ? primero : null,
        lider: primero,
        medallas: Object.values(carga.logros ?? {}).reduce((suma, quienes) => suma + quienes.length, 0),
      };
    })
    .sort((a, b) => b.ordinal - a.ordinal);
}

/**
 * El medallero acumulado: cada jugador con sus medallas de todas las temporadas.
 *
 * Suma **por nombre** porque así se publican las medallas en la instantánea (`tools/badges.py` agrupa por
 * `player_name`). Está declarado como defecto conocido en el slice: la identidad debería ser el id de Slack,
 * y arreglarlo es un cambio del lado de Python.
 */
export function medallero(instantaneas) {
  const cuenta = new Map();

  for (const carga of instantaneas.values()) {
    for (const [clave, quienes] of Object.entries(carga.logros ?? {})) {
      for (const nombre of quienes) {
        if (!cuenta.has(nombre)) {
          cuenta.set(nombre, { nombre, medallas: 0, temporadas_ganadas: 0, por_clave: {} });
        }
        const ficha = cuenta.get(nombre);
        ficha.medallas += 1;
        ficha.por_clave[clave] = (ficha.por_clave[clave] ?? 0) + 1;
      }
    }
  }

  // Ganar una temporada solo cuenta cuando está cerrada: en una abierta se va ganando, no se ha ganado.
  for (const entrada of archivo(instantaneas)) {
    if (!entrada.campeon) continue;
    const nombre = entrada.campeon.nombre;
    if (!cuenta.has(nombre)) {
      cuenta.set(nombre, { nombre, medallas: 0, temporadas_ganadas: 0, por_clave: {} });
    }
    cuenta.get(nombre).temporadas_ganadas += 1;
  }

  return [...cuenta.values()].sort(
    (a, b) =>
      b.medallas - a.medallas ||
      b.temporadas_ganadas - a.temporadas_ganadas ||
      a.nombre.localeCompare(b.nombre),
  );
}
