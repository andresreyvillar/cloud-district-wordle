/**
 * La cabecera y la guía de la pestaña, de `juego-de-la-jornada`.
 *
 *     node --test tests/slices/juego-de-la-jornada/
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { cuandoFue } from '../../../v2/js/domain/superbros.js';
import { CONTROLES, guiaDeControles, vista } from '../../../v2/js/ui/juego.js';

const NIVEL = {
  widthTiles: 13, heightTiles: 6, blocks: [], labels: [{ col: 3, row: 5, text: 'Ana  3/6' }],
  collectibles: [], finish: { col: 10, row: 1 },
};

/** @scenarios la-cabecera-dice-que-dia-es */
test('si la jornada fue ayer, la cabecera lo dice', () => {
  assert.equal(cuandoFue('2026-09-24', '2026-09-25'), 'jornada de ayer · 24 de septiembre');
});

/** @scenarios la-cabecera-dice-que-dia-es */
test('si no fue ayer, dice la fecha y no miente con un «ayer»', () => {
  // Un lunes enseñando el viernes, o un día que nadie jugó: «ayer» sería falso.
  assert.equal(cuandoFue('2026-09-22', '2026-09-25'), 'jornada del 22 de septiembre');
});

/** @scenarios la-cabecera-dice-que-dia-es */
test('el cambio de mes no descuadra el «ayer»', () => {
  assert.equal(cuandoFue('2026-09-30', '2026-10-01'), 'jornada de ayer · 30 de septiembre');
});

/** @scenarios la-cabecera-dice-que-dia-es */
test('la cabecera de la vista lleva el día y el número de jornada', () => {
  const html = vista(NIVEL, 1722, 'jornada de ayer · 24 de septiembre');

  assert.match(html, /jornada de ayer · 24 de septiembre · #1722/);
  assert.match(html, /un juego de Joel/);
});

/** @scenarios la-pestana-explica-como-se-juega */
test('la pestaña trae la guía de controles', () => {
  const html = vista(NIVEL, 1722);

  assert.match(html, /Cómo se juega/);
  for (const { que } of CONTROLES) {
    assert.ok(html.includes(que), `falta el control «${que}»`);
  }
});

/** @scenarios la-pestana-explica-como-se-juega */
test('la guía dice que se juega con teclado', () => {
  assert.match(guiaDeControles(), /teclado/);
});

/** @scenarios la-pestana-explica-como-se-juega */
test('la pestaña ya no dice que el juego está por llegar', () => {
  assert.doesNotMatch(vista(NIVEL, 1722), /llega por pull request/);
});
