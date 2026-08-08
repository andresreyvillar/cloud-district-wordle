/**
 * Escenarios de `album-de-figuras` (Fase 2 — TDD rojo).
 *
 *     node --test tests/slices/album-de-figuras/
 *
 * La selección se prueba como datos y el bloque como **cadena de HTML**, que es el patrón que ya usa
 * `filaDeMarcador`: un constructor exportado se verifica sin navegador y sin captura.
 *
 * El fixture pone el catálogo con un emoji **distinto del real** en una categoría. Con los emojis de verdad,
 * una web que los tuviera escritos a mano pasaría el test igual, y el escenario que importa es justo ese.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { albumDeJugador, albumDeTemporada, tira } from '../../../v2/js/data/album.js';
import { bloqueDeAlbum } from '../../../v2/js/ui/temporada.js';
import { tarjetaDeAlbum } from '../../../v2/js/ui/jugador.js';

/** El catálogo tal y como lo publica Python: lista ordenada, las que puntúan primero. */
const CATALOGO = [
  { clave: 'loro', emoji: '🦜', puntua: true },
  { clave: 'flores', emoji: '🌷', puntua: true },
  { clave: 'geometrico', emoji: '📐', puntua: true },
  { clave: 'abstracto', emoji: '🌀', puntua: false },
];

function jugador(id, nombre, recuento, extra = {}) {
  const partidas = Object.values(recuento).reduce((a, b) => a + b, 0);
  const figuras = CATALOGO.filter((c) => c.puntua).reduce((a, c) => a + (recuento[c.clave] ?? 0), 0);
  return {
    jugador: id,
    nombre,
    partidas,
    figuras,
    tasa: partidas ? Math.round((figuras / partidas) * 10000) / 10000 : 0,
    recuento: { loro: 0, flores: 0, geometrico: 0, abstracto: 0, ...recuento },
    clasificado: partidas >= 5,
    posicion: null,
    ...extra,
  };
}

function instantanea(album) {
  return { temporada: '0', etiqueta: 'Temporada 0', clasificacion: [], album };
}

/** El texto que se ve, sin etiquetas. Se afirma sobre esto y no sobre el marcado: lo que importa es que la
 *  tira se lea `🦜8`, no con qué elementos se maquete. */
function texto(html) {
  return html.replace(/<[^>]*>/g, '');
}

const KOKUMA = jugador('U1', 'Juan (Kokuma)', { loro: 8, flores: 60, geometrico: 3, abstracto: 15 }, {
  posicion: 1,
});
const RAQUEL = jugador('U2', 'Raquel', { loro: 12, flores: 66, geometrico: 8, abstracto: 23 }, {
  posicion: 2,
});
const NOVATO = jugador('U3', 'Novato', { flores: 3 });

// `sin_patron` y `clasificadas` son cifras que no aparecen en ningún otro sitio del fixture: con un 12
// —que es el recuento de loros de Raquel— la aserción de cobertura pasaría casando con otra cosa.
const ALBUM = {
  minimo: 5,
  clasificadas: 198,
  sin_patron: 37,
  reparto: { loro: 20, flores: 129, geometrico: 11, abstracto: 38 },
  categorias: CATALOGO,
  jugadores: [KOKUMA, RAQUEL, NOVATO],
};

/** @scenarios tira-agrupada */
test('la tira agrupa: una entrada por categoría con su recuento, y ninguna vacía', () => {
  const entradas = tira(KOKUMA.recuento, CATALOGO);

  assert.deepEqual(
    entradas.map((e) => [e.categoria, e.partidas]),
    [
      ['loro', 8],
      ['flores', 60],
      ['geometrico', 3],
      ['abstracto', 15],
    ],
  );
  // 86 partidas y cuatro entradas: la tira no crece con las partidas, que es la razón de agruparla.
  assert.equal(entradas.length, 4);

  const sinLoros = tira({ loro: 0, flores: 3, geometrico: 0, abstracto: 1 }, CATALOGO);
  assert.deepEqual(
    sinLoros.map((e) => e.categoria),
    ['flores', 'abstracto'],
    'las categorías sin partidas no aparecen',
  );
});

/** @scenarios emoji-del-payload */
test('el emoji y el orden salen del catálogo publicado, no de un mapa de la web', () => {
  const otroCatalogo = [
    { clave: 'flores', emoji: '🌻', puntua: true },
    { clave: 'loro', emoji: '🐦', puntua: true },
    { clave: 'abstracto', emoji: '🌀', puntua: false },
  ];

  const entradas = tira({ loro: 2, flores: 5, abstracto: 1 }, otroCatalogo);

  assert.deepEqual(
    entradas.map((e) => `${e.emoji}${e.partidas}`),
    ['🌻5', '🐦2', '🌀1'],
    'manda el catálogo: otro emoji y otro orden',
  );
});

/** @scenarios emoji-del-payload */
test('una categoría sin emoji se muestra por su nombre, no con uno inventado', () => {
  const entradas = tira({ loto: 2 }, [{ clave: 'loto', puntua: true }]);

  assert.equal(entradas[0].emoji, 'loto');
});

/** @scenarios ranking-de-belleza-en-la-temporada */
test('la temporada publica su ranking de belleza con puesto, tasa y tira', () => {
  const seleccion = albumDeTemporada(instantanea(ALBUM));

  assert.equal(seleccion.jugadores.length, 3);
  assert.equal(seleccion.clasificados, 2, 'Novato no llega al mínimo');
  assert.deepEqual(
    seleccion.jugadores.map((f) => f.nombre),
    ['Juan (Kokuma)', 'Raquel', 'Novato'],
    'se respeta el orden que llega: la web no reordena',
  );

  const visible = texto(bloqueDeAlbum(instantanea(ALBUM)));
  const html = bloqueDeAlbum(instantanea(ALBUM));
  assert.match(visible, /Juan \(Kokuma\)/);
  assert.match(visible, /🦜8/, "la tira agrupada");
  assert.match(visible, /83\s*%/, "la tasa, en porcentaje");
  assert.ok(!html.includes('MARCADOR'), 'es un bloque aparte del ranking de puntuación');
});

/** @scenarios cobertura-declarada */
test('el bloque dice cuántas partidas se quedaron sin dibujo', () => {
  const visible = texto(bloqueDeAlbum(instantanea(ALBUM)));

  // Atado a la frase que lo explica: un `/37/` suelto casaría con cualquier cifra de la página.
  assert.match(visible, /sobre 198 partidas con cuadrícula guardada/);
  assert.match(visible, /37 de esta temporada no la tienen/);
});

/** @scenarios sin-nadie-clasificado-se-dice */
test('sin nadie por encima del mínimo se explica, en lugar de una tabla vacía', () => {
  const agosto = instantanea({
    ...ALBUM,
    clasificadas: 19,
    sin_patron: 61,
    jugadores: [jugador('U9', 'Cata', { loro: 1, flores: 1 })],
  });

  const visible = texto(bloqueDeAlbum(agosto));

  assert.ok(!/1º/.test(visible), 'nadie ocupa el primer puesto');
  assert.match(visible, /hacen falta 5 partidas con\s+dibujo y nadie llega/);
  assert.match(visible, /61 no tienen cuadrícula/);
});

/** @scenarios album-en-la-ficha */
test('la ficha trae la tira, la tasa y el puesto de ese jugador', () => {
  const suyo = albumDeJugador(instantanea(ALBUM), 'U1');

  assert.equal(suyo.existe, true);
  assert.equal(suyo.posicion, 1);
  assert.equal(suyo.partidas, 86);

  const visible = texto(tarjetaDeAlbum(suyo));
  assert.match(visible, /🌷60/);
  assert.match(visible, /83\s*%/);
  assert.match(visible, /1º/);
});

/** @scenarios album-en-la-ficha */
test('por debajo del mínimo se dice cuántas partidas faltan, no un puesto en blanco', () => {
  const suyo = albumDeJugador(instantanea(ALBUM), 'U3');

  assert.equal(suyo.clasificado, false);
  assert.equal(suyo.faltan, 2, '3 partidas de las 5 que hacen falta');

  assert.match(texto(tarjetaDeAlbum(suyo)), /Le faltan 2 partidas con\s+dibujo/);
});

/** @scenarios album-en-la-ficha */
test('un jugador sin partidas clasificadas no ve un 0%', () => {
  const suyo = albumDeJugador(instantanea(ALBUM), 'U_SIN_DIBUJOS');

  assert.equal(suyo.existe, false);

  const html = tarjetaDeAlbum(suyo);
  assert.ok(!html.includes('0 %') && !html.includes('0%'), 'un 0% diría que dibujó mal');
});

/** @scenarios instantanea-sin-album-no-rompe */
test('una instantánea sin álbum se pinta igual, sin bloque y sin error', () => {
  const vieja = { temporada: '0', etiqueta: 'Temporada 0', clasificacion: [] };

  assert.equal(albumDeTemporada(vieja), null);
  assert.equal(albumDeJugador(vieja, 'U1'), null);
  assert.equal(bloqueDeAlbum(vieja), '');
  assert.equal(tarjetaDeAlbum(null), '');
});
