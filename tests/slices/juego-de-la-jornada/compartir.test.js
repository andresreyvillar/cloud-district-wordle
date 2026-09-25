/**
 * Compartir la puntuación en el canal, de `juego-de-la-jornada`.
 *
 *     node --test tests/slices/juego-de-la-jornada/
 *
 * La puntuación se comparte **como el Wordle: la pega quien jugó**. La web no puede publicar en su nombre
 * —el token del bot vive solo en el workflow— y además no conviene: un mensaje pegado por su dueño lleva
 * autor de verdad, que es exactamente lo que un ranking necesita y un desplegable no da.
 *
 * El formato se prueba **de ida y vuelta**: lo que se escribe tiene que poder leerse. Es lo que permite que
 * algún día el ranking se saque del canal, igual que hoy se sacan los resultados.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { leerPuntuacion, textoParaCompartir, tiempo } from '../../../v2/js/domain/superbros.js';
import { panelDeCompartir, vista } from '../../../v2/js/ui/juego.js';

const PARTIDA = { jornada: 1721, segundos: 83, estrellas: 8, total: 10 };

/** @scenarios el-texto-compartido-dice-de-que-jornada-es */
test('el texto lleva jornada, tiempo y estrellas sobre el total', () => {
  const texto = textoParaCompartir(PARTIDA);

  assert.match(texto, /#1721/);
  assert.match(texto, /1:23/);
  assert.match(texto, /8\/10/);
});

/** @scenarios el-texto-compartido-dice-de-que-jornada-es */
test('se lee de vuelta exactamente lo que se escribió', () => {
  assert.deepEqual(leerPuntuacion(textoParaCompartir(PARTIDA)), PARTIDA);
});

/** @scenarios el-texto-compartido-dice-de-que-jornada-es */
test('el tiempo se escribe como minutos y segundos con dos cifras', () => {
  assert.equal(tiempo(83), '1:23');
  assert.equal(tiempo(5), '0:05');
  assert.equal(tiempo(600), '10:00');
});

/** @scenarios el-texto-compartido-dice-de-que-jornada-es */
test('la barra de estrellas tiene una casilla por coleccionable', () => {
  const barra = textoParaCompartir(PARTIDA).split('\n')[1];

  assert.equal([...barra].length, 10);
  assert.equal([...barra].filter((c) => c === '🟨').length, 8);
});

/** @scenarios el-mismo-resultado-da-el-mismo-texto */
test('la misma partida da el mismo texto', () => {
  assert.equal(textoParaCompartir(PARTIDA), textoParaCompartir({ ...PARTIDA }));
});

/** @scenarios el-mismo-resultado-da-el-mismo-texto */
test('un texto que no es una puntuación del juego no se lee como tal', () => {
  assert.equal(leerPuntuacion('La palabra del día #1721 4/6'), null);
  assert.equal(leerPuntuacion(''), null);
});

/** @scenarios al-terminar-se-ofrece-compartir */
test('al terminar se ofrece el texto y un botón para copiarlo', () => {
  const html = panelDeCompartir(textoParaCompartir(PARTIDA));

  assert.match(html, /#1721/);
  assert.match(html, /<button/);
});

/** @scenarios el-texto-lo-pega-la-persona-no-el-bot */
test('compartir copia el texto; no hay ninguna vía para publicarlo desde la web', () => {
  const html = panelDeCompartir(textoParaCompartir(PARTIDA));

  // El botón copia al portapapeles. Nada en el panel apunta a Slack ni a un endpoint que publique.
  assert.match(html, /[Cc]opiar/);
  assert.ok(!/slack\.com|hooks\.|chat\.postMessage/.test(html));
});

/** @scenarios sin-terminar-no-hay-nada-que-compartir */
test('antes de terminar no se ofrece compartir', () => {
  const nivel = {
    widthTiles: 13, heightTiles: 6, blocks: [], labels: [{ col: 3, row: 5, text: 'Ana  3/6' }],
    collectibles: [], finish: { col: 10, row: 1 },
  };

  assert.ok(!/[Cc]opiar/.test(vista(nivel, 1721)));
});

/** @scenarios el-texto-compartido-dice-de-que-jornada-es */
test('un contador que se pasa no escribe en el canal más estrellas que el total', () => {
  // Un coleccionable contado dos veces en el motor no puede llegar al canal como `11/10`.
  const texto = textoParaCompartir({ ...PARTIDA, estrellas: 11 });

  assert.match(texto, /⭐ 10\/10/);
  assert.equal([...texto.split('\n')[1]].length, 10);
});
