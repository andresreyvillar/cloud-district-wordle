/**
 * El pisotón, de `juego-de-la-jornada`.
 *
 *     node --test tests/slices/juego-de-la-jornada/
 *
 * Es una propuesta sobre el motor de Joel, no suya: con su física el salto máximo es 3,52 casillas y una
 * cuadrícula levanta hasta 6, así que un escalón de 4 era un muro. El dueño probó una casilla más y la subió a
 * **cinco en total**, porque con +1 la torre de 6 de Luis del 24 de septiembre solo se pasaba con media
 * casilla de margen. Lo que se fija aquí es esa promesa, calculada con la física que haya.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { alturaDeSalto, impulsoDelRebote, velocidadParaAltura } from '../../../v2/js/juego/motor.js';
import { guiaDeControles } from '../../../v2/js/ui/juego.js';

// La física del motor de Joel.
const TILE = 32;
const SALTO = -520;
const GRAVEDAD_SUBIENDO = 1200;
const CASILLAS = 5;

/** @scenarios el-pisoton-rebota-cinco-casillas */
test('el rebote sube exactamente cinco casillas', () => {
  const altura = alturaDeSalto(velocidadParaAltura(GRAVEDAD_SUBIENDO, CASILLAS * TILE), GRAVEDAD_SUBIENDO);

  assert.ok(Math.abs(altura - CASILLAS * TILE) < 1e-9, `sube ${altura / TILE} casillas`);
});

/** @scenarios el-pisoton-rebota-cinco-casillas */
test('con la física de hoy, el rebote pasa un muro de 4 y el salto normal no', () => {
  const normal = alturaDeSalto(SALTO, GRAVEDAD_SUBIENDO) / TILE;
  const rebote = alturaDeSalto(velocidadParaAltura(GRAVEDAD_SUBIENDO, CASILLAS * TILE), GRAVEDAD_SUBIENDO) / TILE;

  assert.ok(normal < 4, 'el salto normal no llega a 4 casillas');
  assert.ok(rebote > 4, 'el rebote sí');
});

/** @scenarios el-pisoton-rebota-cinco-casillas */
test('la torre de 6 de Luis se pasa rebotando en lo alto del tramo de Juan', () => {
  // El caso que decidió el número. Desde el suelo no se puede —ninguna columna de 6 se pasa con 5—, pero
  // rebotando en la columna de altura 3 de Juan se llega a 8, dos casillas por encima de la torre.
  const rebote = alturaDeSalto(velocidadParaAltura(GRAVEDAD_SUBIENDO, CASILLAS * TILE), GRAVEDAD_SUBIENDO) / TILE;

  assert.ok(0 + rebote < 6, 'desde el suelo, no');
  assert.ok(3 + rebote >= 6 + 2, 'desde la columna de 3, con dos casillas de margen');
});

/** @scenarios el-pisoton-rebota-cinco-casillas */
test('si cambia la gravedad, sigue subiendo cinco casillas', () => {
  const otra = 1500;
  const altura = alturaDeSalto(velocidadParaAltura(otra, CASILLAS * TILE), otra);

  assert.ok(Math.abs(altura - CASILLAS * TILE) < 1e-9);
});

/** @scenarios el-pisoton-rebota-cinco-casillas */
test('la guía explica el pisotón', () => {
  assert.match(guiaDeControles(), /pisotón/);
  assert.match(guiaDeControles(), /5 casillas/);
});

/** @scenarios el-rebote-sale-hacia-delante */
test('el rebote sale hacia donde se pulsa', () => {
  assert.equal(impulsoDelRebote(1, true, 300), 300);
  assert.equal(impulsoDelRebote(-1, false, 300), -300);
});

/** @scenarios el-rebote-sale-hacia-delante */
test('sin dirección pulsada, sale hacia donde mira el personaje', () => {
  // Es lo que permite pulsar la dirección un poco tarde: el impulso ya ha salido hacia delante.
  assert.equal(impulsoDelRebote(0, false, 300), 300);
  assert.equal(impulsoDelRebote(0, true, 300), -300);
});

/** @scenarios el-rebote-sale-hacia-delante */
test('sale a velocidad de carrera, y no a otra', () => {
  assert.equal(Math.abs(impulsoDelRebote(1, false, 300)), 300);
});
