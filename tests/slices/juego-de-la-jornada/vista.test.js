/**
 * La pestaña del juego, de `juego-de-la-jornada`.
 *
 *     node --test tests/slices/juego-de-la-jornada/
 *
 * La atribución a Joel se verifica como comportamiento y no como detalle de estilo: el juego es suyo y la
 * pestaña tiene que decirlo sin que nadie pregunte. Un cambio de maquetación que se la lleve por delante
 * tiene que ponerse en rojo.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { ID_DEL_CONTENEDOR, vista } from '../../../v2/js/ui/juego.js';

const NIVEL = {
  widthTiles: 13,
  heightTiles: 6,
  blocks: [{ col: 0, row: 0, type: 'ground' }],
  labels: [{ col: 3, row: 5, text: 'Ana  3/6' }],
  collectibles: [{ col: 4, row: 2 }],
  finish: { col: 10, row: 1 },
};

/** @scenarios la-pestana-existe-y-dice-de-quien-es */
test('la pestaña atribuye el juego a Joel', () => {
  assert.match(vista(NIVEL, 1700), /un juego de Joel/);
});

/** @scenarios la-pestana-existe-y-dice-de-quien-es */
test('lo dice también cuando no hay nivel que pintar', () => {
  assert.match(vista(null, null), /un juego de Joel/);
});

/** @scenarios una-jornada-sin-nadie-no-genera-nivel */
test('sin nivel se avisa en lugar de pintar un escenario vacío', () => {
  const html = vista(null, null);

  assert.match(html, /todavía no hay ningún nivel/);
  assert.ok(!html.includes(ID_DEL_CONTENEDOR), 'no se monta el lienzo si no hay nivel');
});

/** @scenarios la-pestana-existe-y-dice-de-quien-es */
test('el nombre de quien juega se escapa antes de entrar al DOM', () => {
  const conTrampa = { ...NIVEL, labels: [{ col: 3, row: 5, text: '<img src=x onerror=alert(1)>  3/6' }] };

  // La etiqueta no se pinta en el HTML de la vista, pero el recuento sí: lo que se comprueba es que la
  // vista no abre ninguna vía para meter marcado desde un nombre de jugador.
  assert.ok(!vista(conTrampa, 1700).includes('<img'));
});
