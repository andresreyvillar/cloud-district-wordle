/**
 * El tutorial del pisotón, de `juego-de-la-jornada`.
 *
 *     node --test tests/slices/juego-de-la-jornada/
 *
 * Sale **la primera vez que hace falta**: justo antes del primer muro que el salto normal no sube, una sola
 * vez por navegador y con la partida en pausa, para que leer cómo se salta no cueste tiempo en el ranking.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { primerMuroQueNecesitaPisoton } from '../../../v2/js/juego/motor.js';
import {
  CLAVE_TUTORIAL, abrirTutorial, guiaDeControles, marcarTutorialVisto, panelDeTutorial, tutorialVisto, vista,
} from '../../../v2/js/ui/juego.js';

/** Columnas macizas: `{3: 4}` es un muro de 4 en la columna 3. */
function bloques(alturas, extra = []) {
  const lista = [];
  for (const [col, alto] of Object.entries(alturas)) {
    for (let row = 1; row <= alto; row += 1) lista.push({ col: Number(col), row, type: 'green' });
  }
  return [...lista, ...extra];
}

/** @scenarios el-tutorial-sale-antes-del-primer-muro-que-pide-pisoton */
test('el primer muro que pide pisotón es el primero más alto que el salto normal', () => {
  assert.equal(primerMuroQueNecesitaPisoton(bloques({ 3: 2, 6: 4, 9: 5 }), 12, 3), 6);
});

/** @scenarios el-tutorial-sale-antes-del-primer-muro-que-pide-pisoton */
test('si el salto normal basta para todo, no hay aviso', () => {
  assert.equal(primerMuroQueNecesitaPisoton(bloques({ 3: 2, 6: 3 }), 10, 3), null);
});

/** @scenarios el-tutorial-sale-antes-del-primer-muro-que-pide-pisoton */
test('un bloque flotante no es muro: se pasa por debajo', () => {
  // Un verde en el suelo y un naranja arriba del todo, con hueco en medio: como el de Luis del día 24.
  const flotante = [{ col: 5, row: 1, type: 'green' }, { col: 5, row: 6, type: 'orange' }];

  assert.equal(primerMuroQueNecesitaPisoton(flotante, 8, 3), null);
});

/** @scenarios el-tutorial-sale-antes-del-primer-muro-que-pide-pisoton */
test('una escalera se sube escalón a escalón', () => {
  // 2, 4, 6: cada escalón sube 2 desde el anterior, así que el salto normal basta.
  assert.equal(primerMuroQueNecesitaPisoton(bloques({ 3: 2, 4: 4, 5: 6 }), 8, 3), null);
});

/** @scenarios el-tutorial-sale-una-sola-vez */
test('el tutorial se recuerda como visto', () => {
  const almacen = new Map();
  const falso = { getItem: (k) => almacen.get(k) ?? null, setItem: (k, v) => almacen.set(k, v) };

  assert.equal(tutorialVisto(falso), false);
  marcarTutorialVisto(falso);
  assert.equal(tutorialVisto(falso), true);
  assert.equal(almacen.get(CLAVE_TUTORIAL), 'si');
});

/** @scenarios el-tutorial-sale-una-sola-vez */
test('un almacén que falla no rompe nada: cuenta como no visto', () => {
  const roto = { getItem: () => { throw new Error('privado'); }, setItem: () => { throw new Error('privado'); } };

  assert.equal(tutorialVisto(roto), false);
  assert.doesNotThrow(() => marcarTutorialVisto(roto));
  assert.equal(tutorialVisto(null), false);
});

/** Un contenedor y una partida de mentira, que apuntan lo que se les hace. */
function escenario() {
  const registro = [];
  let panel = null;
  const boton = { handlers: {}, addEventListener(e, f) { this.handlers[e] = f; }, focus() {} };
  const contenedor = {
    insertAdjacentHTML(_, html) {
      panel = { html, remove() { panel = null; registro.push('cerrado'); },
        addEventListener() {}, querySelector: (s) => (s === '.tutorial-vale' ? boton : null) };
    },
    querySelector: (s) => (s === '.tutorial-pisoton' ? panel : null),
  };
  const partida = { scene: { pause: (k) => registro.push(`pausa ${k}`), resume: (k) => registro.push(`sigue ${k}`) } };
  const almacen = new Map();
  const falso = { getItem: (k) => almacen.get(k) ?? null, setItem: (k, v) => almacen.set(k, v) };
  return { contenedor, partida, falso, boton, registro, abierto: () => panel !== null };
}

/** @scenarios el-tutorial-pausa-la-partida */
test('abrir el tutorial pausa la partida, y cerrarlo la reanuda', () => {
  const e = escenario();

  abrirTutorial(e.contenedor, e.partida, e.falso);
  assert.deepEqual(e.registro, ['pausa main']);
  assert.ok(e.abierto());

  e.boton.handlers.click();
  assert.deepEqual(e.registro, ['pausa main', 'cerrado', 'sigue main']);
  assert.ok(!e.abierto());
});

/** @scenarios el-tutorial-sale-una-sola-vez */
test('cerrar el tutorial lo deja apuntado como visto', () => {
  const e = escenario();

  abrirTutorial(e.contenedor, e.partida, e.falso);
  e.boton.handlers.click();

  assert.equal(tutorialVisto(e.falso), true);
});

/** @scenarios el-tutorial-pausa-la-partida */
test('no se abren dos tutoriales a la vez', () => {
  const e = escenario();

  abrirTutorial(e.contenedor, e.partida, e.falso);
  abrirTutorial(e.contenedor, e.partida, e.falso);

  assert.deepEqual(e.registro, ['pausa main']);
});

/** @scenarios el-tutorial-sale-antes-del-primer-muro-que-pide-pisoton */
test('el panel enseña el GIF y los tres pasos', () => {
  const html = panelDeTutorial('/2/assets/juego/pisoton.gif');

  assert.match(html, /<img src="\/2\/assets\/juego\/pisoton\.gif"/);
  assert.match(html, /Shift/);
  assert.match(html, /¡Entendido!/);
  assert.match(html, /pausa/);
});

/** @scenarios el-tutorial-se-puede-volver-a-ver */
test('la guía trae un enlace para volver a ver el tutorial', () => {
  assert.match(guiaDeControles(), /class="ver-tutorial"/);
});

/** @scenarios el-tutorial-sale-antes-del-primer-muro-que-pide-pisoton */
test('al entrar en la pestaña el tutorial no está abierto', () => {
  const nivel = { widthTiles: 13, heightTiles: 6, blocks: [], labels: [{ col: 3, row: 5, text: 'Ana  3/6' }],
    collectibles: [], finish: { col: 10, row: 1 } };

  assert.doesNotMatch(vista(nivel, 1722), /tutorial-pisoton/);
});
