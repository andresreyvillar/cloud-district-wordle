/**
 * Escenarios de `resultado-del-dia` (Fase 2 — TDD rojo).
 *
 *     node --test tests/slices/resultado-del-dia/
 *
 * Las filas del fixture tienen la forma que devuelve `normalizar()` en `js/data/results.js`, que es el único
 * punto de mapeo de la v2.0. Las reglas del fixture tienen la forma de `tools/rules.py::como_json`, porque
 * de ahí lee la vista el umbral en lugar de escribirlo.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { diaEnCurso } from '../../../v2/js/data/dia.js';

/** Un lunes y un sábado reales de agosto de 2026, para que el filtro de laborable sea comprobable. */
const LUNES = '2026-08-03';
const SABADO = '2026-08-08';

function r(jugador, jornada, intentos, fecha = LUNES) {
  return {
    jugador,
    nombre: jugador.replace('U_', ''),
    jornada,
    intentos,
    fecha,
    temporada: fecha.slice(0, 7),
    patron: null,
  };
}

/** Las reglas como las publica la instantánea: el umbral viaja con su valor y su fuente. */
function reglas(minimo = 5) {
  return [
    {
      id: 'dia-con-muestra-minima',
      titulo: 'Un día con menos de cinco jugadores no cuenta',
      parametros: [
        {
          nombre: 'jugadores mínimos',
          valor: minimo,
          fuente: 'seasons.MUESTRA_MINIMA_DEL_DIA',
          unidad: 'personas',
        },
      ],
    },
  ];
}

function carga({ minimo = 5, jugadores = ['U_ANA', 'U_BEA', 'U_CAR', 'U_DAN', 'U_EVA', 'U_ZOE'] } = {}) {
  return {
    temporada: '2026-08',
    etiqueta: 'Temporada 1 · agosto 2026',
    jugadores,
    media_grupo: 4.0,
    reglas: reglas(minimo),
  };
}

/** @scenarios el-dia-en-curso-se-deriva-de-los-datos */
test('la jornada en curso es la más alta con resultados, no la del reloj', () => {
  const filas = [r('U_ANA', 1670, 3), r('U_BEA', 1671, 4), r('U_ANA', 1671, 5)];

  const dia = diaEnCurso(filas, carga());

  assert.equal(dia.existe, true);
  assert.equal(dia.jornada, 1671);
  assert.equal(dia.fecha, LUNES);
});

/** @scenarios quien-ha-jugado-aparece-con-su-resultado */
test('quien ha jugado sale con sus intentos, del mejor al peor', () => {
  const filas = [r('U_ANA', 1670, 5), r('U_BEA', 1670, 2), r('U_CAR', 1670, 7)];

  const dia = diaEnCurso(filas, carga());

  assert.deepEqual(
    dia.jugaron.map((j) => [j.nombre, j.intentos]),
    [
      ['BEA', 2],
      ['ANA', 5],
      ['CAR', 7],
    ],
  );
  assert.equal(dia.jugaron[2].fallo, true, 'un 7 es un fallo, no un 7');
  assert.equal(dia.jugaron[1].fallo, false);
});

/** @scenarios quien-falta-aparece-declarado */
test('quien falta aparece contado, con el nombre que se le conoce', () => {
  const filas = [r('U_ANA', 1670, 3), r('U_BEA', 1670, 4)];
  const instantanea = carga({ jugadores: ['U_ANA', 'U_BEA', 'U_ZOE'] });

  const dia = diaEnCurso(filas, instantanea, new Map([['U_ZOE', 'Zoe']]));

  assert.deepEqual(
    dia.faltan.map((j) => j.jugador),
    ['U_ZOE'],
  );
  assert.equal(dia.faltan[0].nombre, 'Zoe');
  assert.equal(dia.cuantos_faltan, 1);
});

/** @scenarios la-dificultad-del-dia-se-compara-con-la-temporada */
test('la media del día se compara con la de la temporada, con la diferencia', () => {
  // media del día = (5 + 5 + 5) / 3 = 5,0 frente a 4,0 de la temporada
  const filas = [r('U_ANA', 1670, 5), r('U_BEA', 1670, 5), r('U_CAR', 1670, 5)];

  const dia = diaEnCurso(filas, carga());

  assert.equal(dia.media, 5);
  assert.equal(dia.media_temporada, 4);
  assert.equal(dia.diferencia, 1);
  assert.equal(dia.veredicto, 'más dura');
  assert.equal(dia.mejor, 5);
  assert.equal(dia.peor, 5);
});

/** @scenarios la-dificultad-del-dia-se-compara-con-la-temporada */
test('un día más fácil que la temporada lo dice al revés', () => {
  const filas = [r('U_ANA', 1670, 2), r('U_BEA', 1670, 3)];

  const dia = diaEnCurso(filas, carga());

  assert.equal(dia.media, 2.5);
  assert.equal(dia.diferencia, -1.5);
  assert.equal(dia.veredicto, 'más fácil');
});

/** @scenarios un-dia-que-aun-no-cuenta-lo-dice */
test('una jornada por debajo de la muestra mínima no cuenta, y dice cuántos faltan', () => {
  const filas = [r('U_ANA', 1670, 3), r('U_BEA', 1670, 4)];

  const dia = diaEnCurso(filas, carga({ minimo: 5 }));

  assert.equal(dia.cuenta, false);
  assert.equal(dia.faltan_para_contar, 3, 'dos de cinco: faltan tres');
  assert.equal(dia.motivo, 'muestra');
});

/** @scenarios un-dia-que-aun-no-cuenta-lo-dice */
test('con la muestra alcanzada, la jornada cuenta', () => {
  const filas = ['U_ANA', 'U_BEA', 'U_CAR', 'U_DAN', 'U_EVA'].map((j) => r(j, 1670, 4));

  const dia = diaEnCurso(filas, carga({ minimo: 5 }));

  assert.equal(dia.cuenta, true);
  assert.equal(dia.faltan_para_contar, 0);
  assert.equal(dia.motivo, null);
});

/** @scenarios un-dia-no-laborable-no-cuenta */
test('un sábado no cuenta ni con el grupo entero jugando', () => {
  const filas = ['U_ANA', 'U_BEA', 'U_CAR', 'U_DAN', 'U_EVA', 'U_ZOE'].map((j) => r(j, 1675, 4, SABADO));

  const dia = diaEnCurso(filas, carga());

  assert.equal(dia.laborable, false);
  assert.equal(dia.cuenta, false);
  assert.equal(dia.motivo, 'fin de semana');
  assert.equal(dia.jugaron.length, 6, 'los resultados se muestran igual');
});

/** @scenarios el-umbral-sale-de-las-reglas-y-no-del-codigo-de-la-vista */
test('el umbral se lee de las reglas publicadas, no está escrito en la vista', () => {
  const filas = [r('U_ANA', 1670, 3), r('U_BEA', 1670, 4), r('U_CAR', 1670, 4)];

  // con el umbral recalibrado a 3 en Python, la misma jornada pasa a contar sin tocar esta vista
  assert.equal(diaEnCurso(filas, carga({ minimo: 5 })).cuenta, false);
  assert.equal(diaEnCurso(filas, carga({ minimo: 3 })).cuenta, true);
  assert.equal(diaEnCurso(filas, carga({ minimo: 3 })).minimo, 3);
});

/** @scenarios el-umbral-sale-de-las-reglas-y-no-del-codigo-de-la-vista */
test('sin reglas en la instantánea, la vista no se inventa un umbral', () => {
  const filas = [r('U_ANA', 1670, 3)];
  const sinReglas = { ...carga(), reglas: [] };

  const dia = diaEnCurso(filas, sinReglas);

  assert.equal(dia.minimo, null);
  assert.equal(dia.cuenta, null, 'sin umbral no se puede afirmar que cuente ni que no');
});

/** @scenarios sin-resultados-no-hay-jornada */
test('sin resultados no hay jornada que mostrar', () => {
  const dia = diaEnCurso([], carga());

  assert.equal(dia.existe, false);
  assert.equal(dia.jornada, null);
  assert.deepEqual(dia.jugaron, []);
});
