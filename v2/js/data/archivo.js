/**
 * El archivo de temporadas y el medallero acumulado.
 *
 * Slice: `archivo-de-temporadas` (openspec/slices/ranking/archivo-de-temporadas.md).
 *
 * Funciones **puras**: entran las instantáneas y salen listas. No calculan clasificaciones ni medallas —eso
 * viene materializado (ADR 0008)—; agrupan y suman lo que ya está publicado.
 */

import { conBase } from '../router.js';

/** El identificador de la temporada histórica. El mismo que `tools/seasons.py::TEMPORADA_CERO`. */
const TEMPORADA_CERO = '0';

const EN_CURSO = 'en curso';

/**
 * Desde qué temporada cuentan las tres competiciones —marcador, SuperWordleBros y figuras—. Decisión del dueño:
 * el juego empezó a mitad de septiembre, así que septiembre y las anteriores solo tienen el marcador.
 */
export const DESDE_TRES_COMPETICIONES = '2026-10';

/** Las competiciones de una temporada, en el orden en que se enseñan. */
const COMPETICIONES = [
  { clave: 'marcador', titulo: 'MARCADOR', filas: (carga) => carga.clasificacion ?? [] },
  { clave: 'juego', titulo: 'SUPERWORDLEBROS', filas: (carga) => carga.juego?.clasificacion ?? [] },
  { clave: 'figuras', titulo: 'FIGURAS', filas: (carga) => carga.album?.jugadores ?? [] },
];

/**
 * **Todos los del primer puesto**, no el primero de la lista. Con la misma cifra comparten puesto, y coronar
 * solo al que la lista pone delante era decidir un desempate que la clasificación no hace.
 */
function cabezaDe(tabla) {
  const clasificados = tabla.filter((fila) => fila.clasificado !== false);
  const primero = clasificados[0];
  return primero ? clasificados.filter((fila) => fila.posicion === primero.posicion) : [];
}

/** Si una temporada cuenta las tres competiciones. Los identificadores `AAAA-MM` se comparan como texto. */
export function tieneTresCompeticiones(temporada) {
  return temporada !== TEMPORADA_CERO && temporada >= DESDE_TRES_COMPETICIONES;
}

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
      const cabeza = cabezaDe(tabla);
      const cerrada = carga.estado !== EN_CURSO;
      const competiciones = COMPETICIONES
        .filter(({ clave }) => clave === 'marcador' || tieneTresCompeticiones(temporada))
        .map(({ clave, titulo, filas }) => {
          const lideres = cabezaDe(filas(carga));
          return { clave, titulo, lideres, campeones: cerrada ? lideres : [] };
        });

      return {
        temporada,
        ruta: conBase(`/t/${temporada}`),
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
        // Las del marcador, que es la única competición de las temporadas anteriores a octubre.
        campeones: cerrada ? cabeza : [],
        lideres: cabeza,
        competiciones,
        // El primero de cada lista, para quien solo necesite uno. Con empate NO es «el campeón»: es el que la
        // lista pone delante, y para nombrar al campeón se usan las listas.
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
/**
 * Nombre → dónde vive la ficha de esa persona: su identificador y una temporada en la que aparece.
 *
 * El medallero se cuenta por **nombre**, porque así llegan los logros en la instantánea. Para enlazar hace
 * falta el identificador de Slack, y el único sitio donde conviven los dos es la clasificación.
 *
 * Se queda con la temporada de **mayor ordinal** en la que la persona aparece: enlazar a la más reciente
 * lleva a una ficha con datos, mientras que la primera que se encontrara podría ser una en la que jugó una
 * sola vez.
 */
function dondeVive(instantaneas) {
  const mapa = new Map();
  for (const [temporada, carga] of instantaneas.entries()) {
    const ordinal = carga.ordinal ?? 0;
    for (const fila of carga.clasificacion ?? []) {
      const previo = mapa.get(fila.nombre);
      if (!previo || ordinal > previo.ordinal) {
        mapa.set(fila.nombre, { jugador: fila.jugador, temporada, ordinal });
      }
    }
  }
  return mapa;
}

function nuevaFicha(nombre) {
  return { nombre, medallas: 0, temporadas_ganadas: 0, titulos: { marcador: 0, juego: 0, figuras: 0 }, por_clave: {} };
}

export function medallero(instantaneas) {
  const cuenta = new Map();
  const vive = dondeVive(instantaneas);

  for (const carga of instantaneas.values()) {
    for (const [clave, quienes] of Object.entries(carga.logros ?? {})) {
      for (const nombre of quienes) {
        if (!cuenta.has(nombre)) {
          cuenta.set(nombre, nuevaFicha(nombre));
        }
        const ficha = cuenta.get(nombre);
        ficha.medallas += 1;
        ficha.por_clave[clave] = (ficha.por_clave[clave] ?? 0) + 1;
      }
    }
  }

  // Ganar una temporada solo cuenta cuando está cerrada: en una abierta se va ganando, no se ha ganado.
  // Los títulos, **por competición**: un título del marcador no es uno de belleza. Uno compartido cuenta para
  // cada campeón. `temporadas_ganadas` sigue siendo el del marcador, que es lo que siempre contó.
  for (const entrada of archivo(instantaneas)) {
    for (const { clave, campeones } of entrada.competiciones) {
      for (const { nombre } of campeones) {
        if (!cuenta.has(nombre)) cuenta.set(nombre, nuevaFicha(nombre));
        cuenta.get(nombre).titulos[clave] += 1;
        if (clave === 'marcador') cuenta.get(nombre).temporadas_ganadas += 1;
      }
    }
  }

  // El destino de la ficha viaja con cada fila. Cuando no se puede resolver —un nombre que sale en los
  // logros y en ninguna clasificación— se deja en `null` y la vista lo pinta sin enlace: mandar a una
  // ficha inventada es peor que no enlazar.
  return [...cuenta.values()]
    .map((fila) => {
      const donde = vive.get(fila.nombre) ?? null;
      return { ...fila, jugador: donde?.jugador ?? null, temporada: donde?.temporada ?? null };
    })
    .sort(
      (a, b) =>
        b.medallas - a.medallas ||
        b.temporadas_ganadas - a.temporadas_ganadas ||
        a.nombre.localeCompare(b.nombre),
    );
}
