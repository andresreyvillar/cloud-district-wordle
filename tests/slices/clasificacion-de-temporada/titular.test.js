/**
 * Slice: `clasificacion-de-temporada`.
 *
 * El titular publicaba «Claire le sigue a 0,00» con un empate real en cabeza: tomaba el segundo elemento del
 * array como el segundo clasificado y restaba las medias. El dato de `posicion` ya venía en la instantánea
 * —los empates comparten puesto— y nadie lo leía.
 */

import { test } from 'node:test';
import assert from 'node:assert/strict';

import { titular } from '../../../v2/js/ui/temporada.js';

const fila = (nombre, posicion, media) => ({
  nombre,
  posicion,
  media_temporada: media,
  clasificado: true,
});

/** @scenarios el-titular-cuenta-la-pelea-por-el-primer-puesto */
test('un empate en cabeza se cuenta como empate, no como ventaja de cero', () => {
  // El caso real de producción: dos personas a 3,57 compartiendo el primer puesto.
  const texto = titular([
    fila('Claire', 1, 3.57),
    fila('Andrés R.', 1, 3.57),
    fila('Juan (Kokuma)', 3, 4.08),
  ]);

  assert.ok(texto.includes('Claire') && texto.includes('Andrés R.'), texto);
  assert.ok(/empatad/i.test(texto), `debe decir que van empatados: ${texto}`);
  assert.ok(!texto.includes('0,00'), `nunca «le sigue a 0,00»: ${texto}`);
  assert.ok(!/le sigue/i.test(texto), `nadie sigue a nadie en un empate: ${texto}`);
});

/** @scenarios el-titular-cuenta-la-pelea-por-el-primer-puesto */
test('tres empatados en cabeza no nombran a dos y se callan el tercero', () => {
  const texto = titular([
    fila('Ana', 1, 3.5),
    fila('Bea', 1, 3.5),
    fila('Cris', 1, 3.5),
    fila('Dan', 4, 4.0),
  ]);

  assert.ok(/3 empatados/.test(texto), texto);
  assert.ok(!texto.includes('Dan'), `el cuarto no está en la pelea: ${texto}`);
});

/** @scenarios el-titular-cuenta-la-pelea-por-el-primer-puesto */
test('una ventaja mínima se cuenta como pelea, no como liderazgo tranquilo', () => {
  const texto = titular([fila('Ana', 1, 3.5), fila('Bea', 2, 3.6)]);

  assert.ok(/respira en el cuello/.test(texto), texto);
  assert.ok(texto.includes('0,10'), `y con la distancia real: ${texto}`);
});

/** @scenarios el-titular-cuenta-la-pelea-por-el-primer-puesto */
test('una ventaja amplia se cuenta como liderazgo', () => {
  const texto = titular([fila('Ana', 1, 3.0), fila('Bea', 2, 4.5)]);

  assert.ok(/le sigue a/.test(texto), texto);
  assert.ok(texto.includes('1,50'), texto);
});

/** @scenarios el-titular-cuenta-la-pelea-por-el-primer-puesto */
test('un solo clasificado no inventa rival', () => {
  const texto = titular([fila('Ana', 1, 3.0)]);

  assert.ok(texto.includes('Ana') && /lidera/.test(texto), texto);
  assert.ok(!/empatad|sigue|cuello/.test(texto), texto);
});

/** @scenarios el-titular-cuenta-la-pelea-por-el-primer-puesto */
test('sin clasificados no se afirma que alguien lidera', () => {
  assert.ok(!/lidera/.test(titular([])));
  assert.ok(!/lidera/.test(titular([{ nombre: 'Ana', clasificado: false }])));
});

/** @scenarios el-titular-cuenta-la-pelea-por-el-primer-puesto */
test('el nombre pasa por escapado', () => {
  const texto = titular([fila('<img onerror=alert(1)>', 1, 3.0)]);

  assert.ok(!texto.includes('<img'), `el nombre entra al DOM: hay que escaparlo: ${texto}`);
});
