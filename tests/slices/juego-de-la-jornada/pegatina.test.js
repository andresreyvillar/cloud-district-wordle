/**
 * El sticker de pestaña nueva, de `juego-de-la-jornada`.
 *
 *     node --test tests/slices/juego-de-la-jornada/
 *
 * La fecha entra por parámetro, así que el sticker se prueba antes, el último día y después de caducar sin
 * esperar a que llegue ninguno.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { navegacion } from '../../../v2/js/ui/shell.js';

const DESTINO = { vista: 'temporada', temporada: null };

/** El trozo de navegación que corresponde a la pestaña del juego. */
function pestanaDelJuego(html) {
  return html.split('</a>').find((trozo) => trozo.includes('>SuperWordleBros'));
}

/** @scenarios la-pestana-nueva-lleva-sticker-los-primeros-dias */
test('la pestaña se llama SuperWordleBros', () => {
  assert.ok(pestanaDelJuego(navegacion(DESTINO, '2026-09-25')));
});

/** @scenarios la-pestana-nueva-lleva-sticker-los-primeros-dias */
test('la pestaña del juego lleva el sticker mientras es nueva', () => {
  assert.match(pestanaDelJuego(navegacion(DESTINO, '2026-09-25')), /¡NUEVO!/);
});

/** @scenarios la-pestana-nueva-lleva-sticker-los-primeros-dias */
test('el último día fijado todavía lo lleva', () => {
  assert.match(pestanaDelJuego(navegacion(DESTINO, '2026-10-09')), /¡NUEVO!/);
});

/** @scenarios la-pestana-nueva-lleva-sticker-los-primeros-dias */
test('al día siguiente desaparece solo', () => {
  assert.doesNotMatch(navegacion(DESTINO, '2026-10-10'), /¡NUEVO!/);
});

/** @scenarios la-pestana-nueva-lleva-sticker-los-primeros-dias */
test('ninguna otra pestaña lleva sticker', () => {
  const html = navegacion(DESTINO, '2026-09-25');

  assert.equal((html.match(/¡NUEVO!/g) ?? []).length, 1);
});

/** @scenarios la-pestana-nueva-lleva-sticker-los-primeros-dias */
test('sin fecha no se inventa la novedad', () => {
  assert.doesNotMatch(navegacion(DESTINO, null), /¡NUEVO!/);
});
