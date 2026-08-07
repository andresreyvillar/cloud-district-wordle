/**
 * La tabla cruda: un resultado por fila, tal como está guardado.
 *
 * Slice: `tabla-de-datos` (openspec/slices/dashboard/tabla-de-datos.md).
 *
 * Función **pura**. Es la vista que se mira cuando alguien no se fía de una cifra, así que **no filtra
 * nada**: filtrar aquí sería justo lo que impide comprobar el resto.
 *
 * La única columna que la v1 no podía tener es **si la fila cuenta para su temporada**. No se recalcula:
 * se mira si la jornada está entre los días que la instantánea publica como válidos
 * ([ADR 0008](../../../openspec/decisions/0008-donde-vive-el-calculo.md)).
 */

import { esLaborable } from './dia.js';
import { limiteDeTemporadas, reglasDe, temporadaDe } from './temporada.js';

const FALLO = 7;

/**
 * Las filas de la tabla, de la más reciente a la más antigua.
 *
 * El desempate dentro del mismo día es por nombre y jornada, no por el orden en que llegan de la base: dos
 * cargas tienen que dar la misma lista.
 */
export function filasDeDatos(resultados, instantaneas) {
  // La temporada de una fila la decide el modelo, NO el mes de su fecha: todo lo anterior al límite es la
  // temporada 0. Comparar por el mes dejaba 1502 de 1543 filas buscando una instantánea que no existe, y la
  // tabla decía "70 cuentan" sin quejarse. Es el mismo fallo que tuvo `badges.py`.
  const limite = limiteDelModelo(instantaneas);

  return resultados
    .map((fila) => {
      const temporada = temporadaDe(fila.fecha, limite);
      const carga = temporada ? (instantaneas.get(temporada) ?? null) : null;
      const dias = carga ? new Set(carga.dias ?? []) : null;

      // Sin instantánea no se afirma nada: decir "no cuenta" cuando lo que pasa es que no lo sabemos sería
      // exactamente el tipo de mentira que esta tabla existe para desmentir.
      let cuenta = null;
      let motivo = null;
      if (dias) {
        cuenta = dias.has(fila.jornada);
        if (!cuenta) motivo = esLaborable(fila.fecha) ? 'muestra' : 'fin de semana';
      }

      return {
        fecha: fila.fecha,
        jugador: fila.jugador,
        nombre: fila.nombre,
        jornada: fila.jornada,
        intentos: fila.intentos,
        fallo: fila.intentos >= FALLO,
        marca: fila.intentos >= FALLO ? 'X' : String(fila.intentos),
        temporada,
        etiqueta: carga?.etiqueta ?? null,
        cuenta,
        motivo,
      };
    })
    .sort(
      (a, b) =>
        b.fecha.localeCompare(a.fecha) ||
        a.nombre.localeCompare(b.nombre) ||
        a.jornada - b.jornada,
    );
}


/** El límite, leído una vez por llamada: recorrer las instantáneas por cada fila sería absurdo. */
function limiteDelModelo(instantaneas) {
  return limiteDeTemporadas(reglasDe(instantaneas));
}
