/**
 * Escenarios de vista de `figuras-de-la-jornada`.
 *
 *     node --test tests/slices/figuras-de-la-jornada/
 *
 * El catálogo del fixture asigna emojis **distintos de los reales** a propósito: con los de verdad, una web
 * que los tuviera escritos a mano pasaría el test igual, y eso es justo lo que hay que descartar.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { figurasDeLaJornada } from '../../../v2/js/data/dia.js';
import { tarjetasDeHoy } from '../../../v2/js/ui/hoy.js';

const CATALOGO = [
  { clave: 'loro', emoji: '🐦', puntua: true },
  { clave: 'flores', emoji: '🌻', puntua: true },
  { clave: 'abstracto', emoji: '🌀', puntua: false },
];

const CARGA = {
  album: {
    categorias: CATALOGO,
    ultima_jornada: { jornada: 1701, figuras: { U1: 'loro', U2: 'abstracto' } },
  },
};

const DIA = {
  jornada: 1701,
  jugaron: [
    { jugador: 'U1', nombre: 'Ana', intentos: 3, fallo: false },
    { jugador: 'U2', nombre: 'Bea', intentos: 5, fallo: false },
    { jugador: 'U3', nombre: 'Cris', intentos: 4, fallo: false },
  ],
};

/** @scenarios la-figura-de-cada-participante */
test('cada participante lleva la figura que publicó la instantánea', () => {
  const figuras = figurasDeLaJornada(CARGA, 1701);

  assert.equal(figuras.get('U1'), '🐦');
  assert.equal(figuras.get('U2'), '🌀');
  assert.equal(figuras.has('U3'), false, 'quien no tiene figura publicada no lleva ninguna');
});

/** @scenarios la-web-no-clasifica */
test('el emoji sale del catálogo publicado, no de un mapa de la web', () => {
  // El loro de verdad es 🦜; aquí el catálogo dice 🐦. Manda el catálogo.
  assert.equal(figurasDeLaJornada(CARGA, 1701).get('U1'), '🐦');
});

/** @scenarios el-desfase-se-declara */
test('quien llegó después de la materialización no tiene figura, y la vista lo explica', () => {
  const html = tarjetasDeHoy(DIA, '2026-09', CARGA);

  const deCris = html.split('<a ').find((t) => t.includes('Cris'));
  assert.ok(!/[🐦🌻🌀]/u.test(deCris), 'Cris no tiene figura publicada todavía');
  assert.match(html, /siguiente actualización/i, 'y se explica por qué');
});

/** @scenarios la-figura-de-cada-participante */
test('la tarjeta de quien sí tiene figura la muestra', () => {
  const html = tarjetasDeHoy(DIA, '2026-09', CARGA);

  const deAna = html.split('<a ').find((t) => t.includes('Ana'));
  assert.match(deAna, /🐦/u);
});

/** @scenarios instantanea-sin-figuras-no-rompe */
test('una instantánea sin figuras se pinta como antes', () => {
  const vieja = { album: { categorias: [], jugadores: [] } };

  assert.equal(figurasDeLaJornada(vieja, 1701).size, 0);
  assert.equal(figurasDeLaJornada(null, 1701).size, 0);

  const html = tarjetasDeHoy(DIA, '2026-09', vieja);
  assert.match(html, /Ana/);
  assert.ok(!/siguiente actualización/i.test(html), 'sin figuras no se avisa de un desfase que no aplica');
});

/** @scenarios instantanea-sin-figuras-no-rompe */
test('las figuras de OTRA jornada no se pintan en esta', () => {
  const otra = {
    album: { categorias: CATALOGO, ultima_jornada: { jornada: 1700, figuras: { U1: 'loro' } } },
  };

  assert.equal(figurasDeLaJornada(otra, 1701).size, 0, 'son de ayer, no de hoy');
});
