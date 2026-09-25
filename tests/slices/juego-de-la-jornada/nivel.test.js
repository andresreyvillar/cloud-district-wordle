/**
 * El nivel del juego, de `juego-de-la-jornada`.
 *
 *     node --test tests/slices/juego-de-la-jornada/
 *
 * Las reglas de forma —ocho columnas por jugador, la cuadrícula en las cinco centrales, las filas de abajo
 * arriba— **no se inventaron aquí**: se dedujeron de los dos prototipos de Joel y se verificaron contra la
 * tabla, reconstruyendo el patrón desde sus bloques. Por eso los fixtures llevan patrones con forma de
 * patrón real y no cadenas cualesquiera.
 *
 * Los nombres son inventados a propósito: lo que se prueba es la regla, no quién jugó ese día.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { COLUMNAS_POR_JUGADOR, jornadaDelNivel, nivelDe } from '../../../v2/js/domain/superbros.js';
import { normalizar } from '../../../v2/js/data/results.js';

/**
 * Una fila **tal y como la recibe la vista**: pasada por `normalizar()`, igual que en la web.
 *
 * La primera versión de este fixture tenía la forma de la tabla —`wordle_id`, `player_name`— y todos los
 * tests pasaban mientras la pestaña, con datos reales, no generaba nada. Construirla con el `normalizar` de
 * verdad es lo que ata el test a lo que la web entrega de verdad.
 */
function resultado(nombre, jornada, score, pattern) {
  return normalizar({
    player_name: nombre, slack_user_id: `U_${nombre}`, wordle_id: jornada, score, pattern, date: fechaDeJornada(jornada),
  });
}

/** Una jornada por día, como en el juego: la 1700 es el 1 de septiembre. */
function fechaDeJornada(jornada) {
  return new Date(Date.UTC(2026, 8, 1 + (jornada - 1700))).toISOString().slice(0, 10);
}

const AYER = 1700;
const HOY = 1701;

/** Una jornada cerrada con tres jugadores, y la de hoy a medias. */
const RESULTADOS = [
  resultado('Ana', AYER, 3, '..G../.G..Y/GGGGG'),
  resultado('Bruno', AYER, 2, 'Y...Y/GGGGG'),
  resultado('Cris', AYER, 4, '...../..Y../.GG.G/GGGGG'),
  resultado('Ana', HOY, 3, '..G../.G..Y/GGGGG'),
];

/** Los bloques de un tramo, sin el suelo, indexados por fila. */
function rejillaDe(nivel, indice) {
  const base = indice * COLUMNAS_POR_JUGADOR;
  const dentro = nivel.blocks.filter(
    (b) => b.type !== 'ground' && b.col >= base && b.col < base + COLUMNAS_POR_JUGADOR,
  );
  const filas = {};
  for (const b of dentro) {
    filas[b.row] = filas[b.row] || {};
    filas[b.row][b.col - base] = b.type;
  }
  return filas;
}

/** Reconstruye el patrón a partir de los bloques: la prueba de que el escenario ES la cuadrícula. */
function patronDe(nivel, indice, score) {
  const filas = rejillaDe(nivel, indice);
  const texto = [];
  for (let fila = score; fila >= 1; fila -= 1) {
    let linea = '';
    for (let col = 3; col <= 7; col += 1) {
      const tipo = (filas[fila] || {})[col];
      linea += tipo === 'green' ? 'G' : tipo === 'orange' ? 'Y' : '.';
    }
    texto.push(linea);
  }
  return texto.join('/');
}

/** El día en que se juega: la jornada HOY está en curso. */
const DIA_DE_HOY = fechaDeJornada(HOY);

/** @scenarios el-nivel-sale-de-la-jornada-anterior */
test('el nivel usa la última jornada cerrada, no la de hoy', () => {
  assert.equal(jornadaDelNivel(RESULTADOS, DIA_DE_HOY), AYER);
});

/** @scenarios el-nivel-sale-de-la-jornada-anterior */
test('a primera hora, sin nadie jugando todavía, sigue siendo la de ayer y no la de anteayer', () => {
  // **El fallo que se vio en vivo.** Coger «la penúltima jornada de la tabla» funciona por la tarde, pero de
  // madrugada la de hoy aún no tiene filas y la penúltima es la de anteayer: a las 00:18 del 25 de
  // septiembre la pestaña enseñaba la 1721 cuando la de ayer era la 1722.
  const deMadrugada = [
    resultado('Ana', AYER - 1, 4, '...../.G..Y/.GG.G/GGGGG'),
    ...RESULTADOS.filter((fila) => fila.jornada !== HOY),
  ];

  assert.equal(jornadaDelNivel(deMadrugada, DIA_DE_HOY), AYER);
});

/** @scenarios el-nivel-sale-de-la-jornada-anterior */
test('sin saber qué día es hoy no se adivina la jornada', () => {
  assert.equal(jornadaDelNivel(RESULTADOS, null), null);
});

/** @scenarios el-nivel-sale-de-la-jornada-anterior */
test('los tramos son los de esa jornada y no los de la siguiente', () => {
  const nivel = nivelDe(RESULTADOS, jornadaDelNivel(RESULTADOS, DIA_DE_HOY));

  assert.equal(nivel.labels.length, 3);
});

/** @scenarios cada-jugador-tiene-su-tramo */
test('el ancho es ocho columnas por jugador más la cola de la meta', () => {
  const nivel = nivelDe(RESULTADOS, AYER);

  assert.equal(nivel.widthTiles, 3 * COLUMNAS_POR_JUGADOR + 5);
  assert.equal(nivel.finish.col, nivel.widthTiles - 3);
});

/** @scenarios la-cuadricula-es-el-escenario */
test('los bloques reconstruyen exactamente el patrón de cada jugador', () => {
  const nivel = nivelDe(RESULTADOS, AYER);

  assert.equal(patronDe(nivel, 0, 3), '..G../.G..Y/GGGGG');
  assert.equal(patronDe(nivel, 1, 2), 'Y...Y/GGGGG');
  assert.equal(patronDe(nivel, 2, 4), '...../..Y../.GG.G/GGGGG');
});

/** @scenarios la-cuadricula-es-el-escenario */
test('la fila 1 es el último intento, el que resolvió', () => {
  const nivel = nivelDe(RESULTADOS, AYER);
  const filas = rejillaDe(nivel, 0);

  // El último intento de Ana es GGGGG: cinco verdes seguidos en la fila de abajo.
  assert.deepEqual(filas[1], { 3: 'green', 4: 'green', 5: 'green', 6: 'green', 7: 'green' });
});

/** @scenarios el-suelo-no-tiene-agujeros */
test('hay suelo bajo todas las columnas', () => {
  const nivel = nivelDe(RESULTADOS, AYER);
  const suelo = new Set(nivel.blocks.filter((b) => b.type === 'ground').map((b) => b.col));

  for (let col = 0; col < nivel.widthTiles; col += 1) {
    assert.ok(suelo.has(col), `falta suelo en la columna ${col}`);
  }
});

/** @scenarios cada-tramo-lleva-nombre-y-nota */
test('cada tramo lleva etiqueta con nombre y nota, por encima de su cuadrícula', () => {
  const nivel = nivelDe(RESULTADOS, AYER);

  assert.equal(nivel.labels.length, 3);
  for (const etiqueta of nivel.labels) {
    assert.match(etiqueta.text, /^\S.*\s{2}\d\/6$/);
  }
  const deAna = nivel.labels[0];
  assert.ok(deAna.text.startsWith('Ana'));
  assert.ok(deAna.row > 3, 'la etiqueta va por encima de la cuadrícula');
});

/** @scenarios el-nombre-es-el-de-la-tabla */
test('el nombre del nivel es el de la tabla y no el identificador', () => {
  const nivel = nivelDe(RESULTADOS, AYER);

  assert.ok(nivel.labels.some((l) => l.text.startsWith('Ana')));
  assert.ok(!JSON.stringify(nivel).includes('U_Ana'));
});

/** @scenarios el-coleccionable-se-puede-alcanzar */
test('cada coleccionable descansa sobre una plataforma', () => {
  const nivel = nivelDe(RESULTADOS, AYER);
  const bloques = new Set(nivel.blocks.map((b) => `${b.col},${b.row}`));

  assert.equal(nivel.collectibles.length, 3);
  for (const c of nivel.collectibles) {
    assert.ok(bloques.has(`${c.col},${c.row - 1}`), `el coleccionable de (${c.col},${c.row}) está en el aire`);
  }
});

/** @scenarios la-misma-jornada-da-el-mismo-nivel */
test('generar dos veces la misma jornada da el mismo nivel', () => {
  assert.deepEqual(nivelDe(RESULTADOS, AYER), nivelDe(RESULTADOS, AYER));
});

/** @scenarios una-jornada-sin-nadie-no-genera-nivel */
test('una jornada sin resultados no genera nivel', () => {
  assert.equal(nivelDe(RESULTADOS, 1234), null);
  assert.equal(nivelDe([], 1700), null);
});

/** @scenarios quien-no-tiene-cuadricula-no-rompe-el-nivel */
test('un resultado sin patrón se queda fuera y el resto se genera igual', () => {
  const conHueco = [...RESULTADOS, resultado('Sin patrón', AYER, 5, null)];

  const nivel = nivelDe(conHueco, AYER);

  assert.equal(nivel.labels.length, 3);
  assert.ok(!nivel.labels.some((l) => l.text.startsWith('Sin patrón')));
});
