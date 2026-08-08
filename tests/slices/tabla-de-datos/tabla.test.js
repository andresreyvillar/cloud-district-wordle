/**
 * Escenarios de `tabla-de-datos` (Fase 2 — TDD rojo).
 *
 *     node --test tests/slices/tabla-de-datos/
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { filasDeDatos } from '../../../v2/js/data/tabla.js';

const LUNES = '2026-08-03';
const MARTES = '2026-08-04';
const SABADO = '2026-08-08';

function r(nombre, jornada, intentos, fecha) {
  return {
    jugador: `U_${nombre.toUpperCase()}`,
    nombre,
    jornada,
    intentos,
    fecha,
    mes: fecha.slice(0, 7),
    patron: null,
  };
}

/** El límite viaja en las reglas, como en producción: la vista no lo tiene escrito. */
const REGLAS = [
  {
    id: 'temporada-cero',
    titulo: 'Todo lo jugado antes de agosto de 2026 es la temporada 0',
    parametros: [
      { nombre: 'la temporada 1 empieza', valor: '2026-08', fuente: 'seasons.INICIO_TEMPORADAS' },
    ],
  },
];

/** Una instantánea con sus días válidos: el lunes cuenta, el martes no llegó a la muestra, el sábado nunca. */
function instantaneas(dias = [1670], conCero = false) {
  const mapa = new Map([
    ['2026-08', { temporada: '2026-08', etiqueta: 'Temporada 1 · agosto 2026', dias, reglas: REGLAS }],
  ]);
  if (conCero) {
    mapa.set('0', { temporada: '0', etiqueta: 'Temporada 0 · el histórico', dias: [1500], reglas: REGLAS });
  }
  return mapa;
}

/** @scenarios la-tabla-lista-todos-los-resultados */
test('la tabla lista todos los resultados, sin filtrar ninguno', () => {
  const filas = [r('Ana', 1670, 3, LUNES), r('Bea', 1670, 4, LUNES), r('Ana', 1675, 5, SABADO)];

  const tabla = filasDeDatos(filas, instantaneas());

  assert.equal(tabla.length, 3, 'la vista cruda no filtra: filtrar impide comprobar el resto');
});

/** @scenarios orden-de-la-mas-reciente-a-la-mas-antigua */
test('las filas salen de la más reciente a la más antigua, con orden estable dentro del día', () => {
  const filas = [
    r('Ana', 1670, 3, LUNES),
    r('Zoe', 1671, 4, MARTES),
    r('Ana', 1671, 2, MARTES),
    r('Bea', 1670, 5, LUNES),
  ];

  const tabla = filasDeDatos(filas, instantaneas());

  assert.deepEqual(
    tabla.map((f) => [f.fecha, f.nombre]),
    [
      [MARTES, 'Ana'],
      [MARTES, 'Zoe'],
      [LUNES, 'Ana'],
      [LUNES, 'Bea'],
    ],
  );
  // dos cargas con las filas en otro orden dan la misma lista
  assert.deepEqual(filasDeDatos([...filas].reverse(), instantaneas()), tabla);
});

/** @scenarios la-tabla-dice-si-una-fila-cuenta-y-por-que */
test('una jornada que no es día de temporada se declara, con el motivo', () => {
  const filas = [r('Ana', 1670, 3, LUNES), r('Ana', 1671, 4, MARTES), r('Ana', 1675, 5, SABADO)];

  const tabla = filasDeDatos(filas, instantaneas([1670]));
  const por = Object.fromEntries(tabla.map((f) => [f.jornada, f]));

  assert.equal(por[1670].cuenta, true);
  assert.equal(por[1670].motivo, null);

  assert.equal(por[1671].cuenta, false, 'martes laborable pero sin muestra suficiente');
  assert.equal(por[1671].motivo, 'muestra');

  assert.equal(por[1675].cuenta, false);
  assert.equal(por[1675].motivo, 'fin de semana');
});

/** @scenarios una-fila-de-temporada-sin-materializar-no-afirma-nada */
test('sin instantánea de su temporada, la fila no afirma si cuenta', () => {
  // mayo es anterior al límite: su temporada es la 0, y aquí la 0 no está materializada
  const filas = [r('Ana', 1500, 3, '2026-05-04')];

  const tabla = filasDeDatos(filas, instantaneas());

  assert.equal(tabla[0].cuenta, null);
  assert.equal(tabla[0].motivo, null);
});

/** @scenarios la-temporada-de-una-fila-la-decide-el-modelo */
test('una fila anterior al límite se compara con la temporada 0, no con su mes', () => {
  const filas = [r('Ana', 1500, 3, '2026-05-04'), r('Bea', 1499, 4, '2026-05-05')];

  const tabla = filasDeDatos(filas, instantaneas([1670], true));
  const por = Object.fromEntries(tabla.map((f) => [f.jornada, f]));

  assert.equal(por[1500].temporada, '0', 'mayo es temporada 0, no la temporada "2026-05"');
  assert.equal(por[1500].cuenta, true, 'la jornada 1500 sí está entre los días de la temporada 0');
  assert.equal(por[1499].cuenta, false);
});

/** @scenarios la-temporada-de-una-fila-la-decide-el-modelo */
test('sin el límite publicado, la tabla no adivina la temporada de una fila', () => {
  const sinReglas = new Map([['2026-08', { temporada: '2026-08', dias: [1670] }]]);

  const tabla = filasDeDatos([r('Ana', 1670, 3, LUNES)], sinReglas);

  assert.equal(tabla[0].temporada, null);
  assert.equal(tabla[0].cuenta, null, 'sin frontera no se puede afirmar a qué temporada pertenece');
});

/** @scenarios el-fallo-se-distingue-de-un-seis */
test('el fallo se distingue de un seis', () => {
  const filas = [r('Ana', 1670, 6, LUNES), r('Bea', 1670, 7, LUNES)];

  const tabla = filasDeDatos(filas, instantaneas());
  const por = Object.fromEntries(tabla.map((f) => [f.nombre, f]));

  assert.equal(por.Ana.fallo, false);
  assert.equal(por.Ana.marca, '6');
  assert.equal(por.Bea.fallo, true);
  assert.equal(por.Bea.marca, 'X', 'un 7 no es una puntuación: es el fallo');
});

/** @scenarios sin-resultados-la-tabla-lo-dice */
test('sin resultados la tabla sale vacía, no rota', () => {
  assert.deepEqual(filasDeDatos([], instantaneas()), []);
  assert.deepEqual(filasDeDatos([], new Map()), []);
});
