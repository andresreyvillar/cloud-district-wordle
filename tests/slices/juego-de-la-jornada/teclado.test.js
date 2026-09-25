/**
 * El teclado y el scroll de la página, de `juego-de-la-jornada`.
 *
 *     node --test tests/slices/juego-de-la-jornada/
 *
 * Con el juego enfocado, sus teclas son del juego y no mueven la página —**también con Shift**, que es como
 * se corre y como se hace el pisotón—; lo demás que hace scroll sigue libre. El detalle de dónde se engancha
 * ese bloqueo —en el padre, no en el lienzo— lo fija un `checks:` del delta, porque engancharlo en el lienzo
 * dejaba el juego sin teclas y ningún test lo habría visto.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { esTeclaDelJuego } from '../../../v2/js/ui/juego.js';

/** @scenarios las-teclas-del-juego-no-mueven-la-pagina */
test('el espacio y las flechas son del juego', () => {
  for (const key of [' ', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight']) {
    assert.ok(esTeclaDelJuego({ key }), key);
  }
});

/** @scenarios las-teclas-del-juego-no-mueven-la-pagina */
test('también con Shift, que es como se corre y como se hace el pisotón', () => {
  // Phaser deja de bloquearlas cuando va un modificador pulsado, y Shift + Espacio sube la página de golpe.
  assert.ok(esTeclaDelJuego({ key: ' ', shiftKey: true }));
  assert.ok(esTeclaDelJuego({ key: 'ArrowDown', shiftKey: true }));
});

/** @scenarios la-pagina-se-sigue-moviendo-con-lo-demas */
test('lo que no usa el juego sigue moviendo la página', () => {
  for (const key of ['PageDown', 'PageUp', 'Home', 'End', 'Tab']) {
    assert.ok(!esTeclaDelJuego({ key }), key);
  }
});
