/**
 * Escenarios de `escala-fija-comparable` (Fase 2 — TDD rojo).
 *
 *     node --test tests/slices/escala-fija-comparable/
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
  ESCALA_DE_INTENTOS,
  alturaDeIntentos,
  escalaDeDistribucion,
  alturaEnEscala,
} from '../../../v2/js/data/escala.js';

/** @scenarios la-dificultad-va-en-la-escala-de-intentos */
test('la dificultad se pinta en la escala de intentos, no en la del mes', () => {
  assert.deepEqual(ESCALA_DE_INTENTOS, { minimo: 1, maximo: 7 });

  // el fallo llena la barra; el mejor resultado posible la deja al mínimo visible
  assert.equal(alturaDeIntentos(7), 100);
  assert.equal(alturaDeIntentos(4), 50);
  assert.ok(alturaDeIntentos(1) > 0, 'una barra de cero se lee como que no hay dato');
  assert.ok(alturaDeIntentos(1) < 5);
});

/** @scenarios dos-temporadas-se-pueden-comparar */
test('la misma dificultad da la misma altura en dos temporadas distintas', () => {
  // un mes cuya jornada más dura fue 4,2 y otro que llegó a 6,0
  const mesFacil = [3.1, 3.8, 4.2];
  const mesDuro = [3.8, 5.1, 6.0];

  const alturasFacil = mesFacil.map(alturaDeIntentos);
  const alturasDuro = mesDuro.map(alturaDeIntentos);

  assert.equal(alturasFacil[1], alturasDuro[0], '3,8 es 3,8 en los dos meses');
  assert.ok(Math.max(...alturasFacil) < Math.max(...alturasDuro), 'el mes fácil tiene que verse más bajo');
  assert.ok(Math.max(...alturasFacil) < 100, 'ningún mes toca el techo por ser su propio máximo');
});

/** @scenarios la-distribucion-comparte-escala-entre-jugadores */
test('la distribución comparte la escala de toda la temporada', () => {
  // El máximo NO está en el primer jugador a propósito: con el máximo en la primera fila, mirar solo esa
  // fila daba la respuesta correcta por casualidad y el mutante sobrevivía.
  const clasificacion = [
    { nombre: 'Esporadico', distribucion: [0, 1, 3, 2, 0, 0, 0] },
    { nombre: 'Constante', distribucion: [0, 2, 40, 30, 8, 2, 1] },
  ];

  const escala = escalaDeDistribucion(clasificacion);

  assert.equal(escala, 40, 'el mayor recuento de CUALQUIER jugador, no el del primero');
  assert.equal(alturaEnEscala(40, escala), 100);
  assert.equal(alturaEnEscala(3, escala), alturaEnEscala(3, escala), 'el mismo recuento, la misma altura');
});

/** @scenarios la-distribucion-comparte-escala-entre-jugadores */
test('quien jugó poco se ve pequeño, que es lo que el autoescalado borraba', () => {
  const clasificacion = [
    { nombre: 'Esporadico', distribucion: [0, 1, 3, 2, 0, 0, 0] },
    { nombre: 'Constante', distribucion: [0, 2, 40, 30, 8, 2, 1] },
  ];
  const escala = escalaDeDistribucion(clasificacion);

  const altoConstante = Math.max(...clasificacion[1].distribucion.map((n) => alturaEnEscala(n, escala)));
  const altoEsporadico = Math.max(...clasificacion[0].distribucion.map((n) => alturaEnEscala(n, escala)));

  assert.equal(altoConstante, 100);
  assert.ok(altoEsporadico < 15, `el esporádico llega al ${altoEsporadico}%, tendría que verse pequeño`);
});

/** @scenarios un-valor-fuera-de-escala-no-se-sale-del-gráfico */
test('un valor fuera de escala se recorta en lugar de desbordar', () => {
  assert.equal(alturaDeIntentos(9), 100);
  assert.equal(alturaDeIntentos(0), alturaDeIntentos(1));
  assert.equal(alturaEnEscala(50, 40), 100);
  assert.equal(alturaEnEscala(-3, 40), 0);
});

/** @scenarios sin-datos-no-se-divide-por-cero */
test('sin recuentos la escala sigue siendo utilizable', () => {
  assert.equal(escalaDeDistribucion([]), 1);
  assert.equal(escalaDeDistribucion([{ distribucion: [0, 0, 0, 0, 0, 0, 0] }]), 1);
  assert.equal(alturaEnEscala(0, escalaDeDistribucion([])), 0);

  // Con escala cero, `valor / 0` da infinito y el recorte lo convertía en 100: una barra LLENA a partir de
  // nada. Y `0 / 0` da NaN, que se cuela como altura. Las dos tienen que ser cero.
  assert.equal(alturaEnEscala(1, 0), 0, 'una escala cero no puede llenar la barra');
  assert.equal(alturaEnEscala(0, 0), 0);
});

/** @scenarios la-escala-se-declara */
test('la escala se puede enunciar, para que el gráfico la anuncie', () => {
  assert.match(alturaDeIntentos.leyenda ?? '', /1.*7/, 'la escala de intentos se enuncia');
  assert.match(escalaDeDistribucion.leyenda?.(40) ?? '', /40/, 'la de distribución dice su máximo');
});
