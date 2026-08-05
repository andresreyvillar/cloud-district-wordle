/**
 * Unitarios del router de la v2.0.
 *
 * El esqueleto es un change pack `Slice: N/A`, así que aquí no hay escenarios: el router no es
 * comportamiento observable del producto, es la plantilla sobre la que cada slice montará el suyo. Se
 * prueba porque es la única lógica del pack y porque el Gate 4c necesita algo que se ponga rojo.
 *
 *     node --test tests/v2/
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { resolver, rutaDe, seccionDe, VISTAS } from '../../v2/js/router.js';

test('la raíz es la temporada en curso, y "en curso" lo decide el borde', () => {
  // temporada: null a propósito — el router no sabe qué día es hoy
  assert.deepEqual(resolver('/'), { vista: VISTAS.TEMPORADA, temporada: null });
  assert.deepEqual(resolver(''), { vista: VISTAS.TEMPORADA, temporada: null });
});

test('una temporada concreta se resuelve con su identificador', () => {
  assert.deepEqual(resolver('/t/2026-07'), { vista: VISTAS.TEMPORADA, temporada: '2026-07' });
});

test('las tres vistas transversales tienen su ruta', () => {
  assert.equal(resolver('/temporadas').vista, VISTAS.TEMPORADAS);
  assert.equal(resolver('/hoy').vista, VISTAS.HOY);
  assert.equal(resolver('/datos').vista, VISTAS.DATOS);
});

test('el jugador va dentro de una temporada y se identifica por su id de Slack', () => {
  assert.deepEqual(resolver('/t/2026-07/j/U08U27DFDL2'), {
    vista: VISTAS.JUGADOR,
    temporada: '2026-07',
    jugador: 'U08U27DFDL2',
  });
});

test('un mes que no existe no es una temporada', () => {
  // El mes 13 y el 00 tienen la forma correcta y no son meses: el patrón los rechaza
  assert.equal(resolver('/t/2026-13').vista, VISTAS.DESCONOCIDA);
  assert.equal(resolver('/t/2026-00').vista, VISTAS.DESCONOCIDA);
  assert.equal(resolver('/t/26-07').vista, VISTAS.DESCONOCIDA);
  assert.equal(resolver('/t/2026-7').vista, VISTAS.DESCONOCIDA);
});

test('un nombre en el segmento de jugador no cuela', () => {
  // Es lo que la migración de identidad vino a evitar: los nombres cambian
  assert.equal(resolver('/t/2026-07/j/Andrés R.').vista, VISTAS.DESCONOCIDA);
  assert.equal(resolver('/t/2026-07/j/carlos.h').vista, VISTAS.DESCONOCIDA);
});

test('lo que no encaja se declara desconocido, no lanza', () => {
  assert.deepEqual(resolver('/ruta-mala'), { vista: VISTAS.DESCONOCIDA, ruta: '/ruta-mala' });
  assert.equal(resolver('/t').vista, VISTAS.DESCONOCIDA);
  assert.equal(resolver('/t/2026-07/j').vista, VISTAS.DESCONOCIDA);
  assert.equal(resolver('/temporadas/extra').vista, VISTAS.DESCONOCIDA);
  assert.equal(resolver(null).vista, VISTAS.TEMPORADA);
});

test('las barras de sobra y la query no cambian la vista', () => {
  assert.deepEqual(resolver('//t//2026-07//'), { vista: VISTAS.TEMPORADA, temporada: '2026-07' });
  assert.equal(resolver('/hoy?utm=slack').vista, VISTAS.HOY);
  assert.equal(resolver('/hoy#arriba').vista, VISTAS.HOY);
});

test('rutaDe es la inversa de resolver', () => {
  const rutas = ['/', '/t/2026-07', '/t/2026-07/j/U08U27DFDL2', '/temporadas', '/hoy', '/datos'];
  for (const ruta of rutas) {
    assert.equal(rutaDe(resolver(ruta)), ruta, `ida y vuelta de ${ruta}`);
  }
});

test('la ficha de jugador se navega dentro de la sección Temporada', () => {
  // Lo cazó el navegador: sin esto, en /t/2026-07/j/U… no se marcaba ninguna sección
  assert.equal(seccionDe(VISTAS.JUGADOR), VISTAS.TEMPORADA);
});

test('cada sección se contiene a sí misma y la ruta desconocida a ninguna', () => {
  for (const vista of [VISTAS.TEMPORADA, VISTAS.TEMPORADAS, VISTAS.HOY, VISTAS.DATOS]) {
    assert.equal(seccionDe(vista), vista);
  }
  assert.equal(seccionDe(VISTAS.DESCONOCIDA), null);
});
