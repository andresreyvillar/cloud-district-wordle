/**
 * El bloque «Cómo juegas» de la ficha, de `indicadores-de-juego` (pack `feat-indicadores-de-juego`).
 *
 *     node --test tests/slices/indicadores-de-juego/
 *
 * Los indicadores llegan como los materializa el pipeline. Jugadores sintéticos: el repositorio es público.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { pintarJugador, tarjetaDeIndicadores } from '../../../v2/js/ui/jugador.js';

const INDICADORES = {
  minimo: 5,
  referencia: 3.41,
  grupo: { media: 4.28, apertura: [49.5, 4], suerte_por_partida: -0.265, partidas: 249 },
  jugadores: {
    U_ANA: {
      partidas: 8, media: 3.08, apertura: [40.5, 2], suerte: 3.03, suerte_por_partida: 0.379,
      milagro: { jornada: 1730, intentos: 2, candidatas: 31 },
    },
    U_BEA: {
      partidas: 11, media: 3.69, apertura: [16, 3], suerte: -0.68, suerte_por_partida: -0.062,
      milagro: { jornada: 1744, intentos: 3, candidatas: 1 },
    },
    U_CRIS: { partidas: 2, faltan: 3 },
  },
};

const bloque = (jugador, indicadores = INDICADORES) => tarjetaDeIndicadores(indicadores, jugador);

/** @scenarios el-bloque-sale-en-la-ficha */
test('el bloque lleva sus cuatro indicadores', () => {
  const html = bloque('U_ANA');

  assert.match(html, /CÓMO JUEGAS/);
  for (const titulo of ['Eficiencia', 'Apertura', 'Suerte', 'Acierto más milagroso']) {
    assert.match(html, new RegExp(titulo), titulo);
  }
});

/** @scenarios el-bloque-sale-en-la-ficha, sin-lista-no-hay-indicadores */
test('la ficha pinta el bloque con la instantánea, y sin indicadores lo dice y sigue', () => {
  const instantanea = (indicadores) => ({
    temporada: '2026-10', etiqueta: 'octubre de 2026', estado: 'en curso', dias: [1, 2],
    clasificacion: [{ posicion: 1, jugador: 'U_ANA', nombre: 'Ana', clasificado: true, dias: 2, jugados: 2,
      media_temporada: 3, media_jugada: 3, mejor: 3, peor: 3, distribucion: [0, 0, 2, 0, 0, 0, 0], por_dia: [] }],
    logros: {},
    ...(indicadores ? { indicadores } : {}),
  });
  const pintar = (indicadores) => {
    const contenedor = { innerHTML: '' };
    pintarJugador(contenedor, new Map([['2026-10', instantanea(indicadores)]]), '2026-10', 'U_ANA');
    return contenedor.innerHTML;
  };

  assert.match(pintar(INDICADORES), /CÓMO JUEGAS[\s\S]*Eficiencia/);
  const sin = pintar(null);
  assert.match(sin, /CÓMO JUEGAS[\s\S]*no están disponibles/);
  assert.match(sin, /Ana/, 'el resto de la ficha se pinta igual');
});

/** @scenarios la-eficiencia-se-compara-con-el-optimo-y-con-el-grupo */
test('la eficiencia enseña la media del jugador, la del grupo y la del solucionador', () => {
  const eficiencia = bloque('U_ANA').split('Eficiencia')[1].split('Apertura')[0];

  assert.match(eficiencia, /3,08/);
  assert.match(eficiencia, /grupo 4,28/);
  assert.match(eficiencia, /3,41/);
});

/** @scenarios la-apertura-cuenta-cuantas-quedan-tras-cada-intento */
test('la apertura enseña las candidatas tras el primer y el segundo intento, con las del grupo', () => {
  const apertura = bloque('U_ANA').split('Apertura')[1].split('Suerte')[0];

  assert.match(apertura, /1\.º intento[^·]*40,5[^·]*grupo: 49,5/);
  assert.match(apertura, /2\.º[^·]*2 [^·]*grupo: 4\b/);
});

/** @scenarios la-suerte-son-aciertos-reales-menos-esperados */
test('la suerte se enseña frente al grupo, y la cifra y la frase dicen lo mismo', () => {
  // Ana: (0,379 + 0,265) × 8 = +5,15 · Bea: (−0,062 + 0,265) × 11 = +2,23 · Dani, peor que el grupo.
  const conDani = { ...INDICADORES, jugadores: { ...INDICADORES.jugadores,
    U_DANI: { partidas: 10, media: 4.5, apertura: [60, 6], suerte: -5, suerte_por_partida: -0.5, milagro: null } } };
  const suerte = (j) => tarjetaDeIndicadores(conDani, j).split('Suerte')[1].split('Acierto más milagroso')[0];

  assert.match(suerte('U_ANA'), /\+5,15/);
  assert.match(suerte('U_ANA'), /le sonríe/);
  assert.match(suerte('U_BEA'), /\+2,23/);
  assert.match(suerte('U_BEA'), /le sonríe/, 'con suerte absoluta negativa pero mejor que el grupo, sonríe');
  assert.match(suerte('U_DANI'), /−2,35/);
  assert.match(suerte('U_DANI'), /le debe/);
});

/** @scenarios el-acierto-mas-milagroso-es-el-de-mas-candidatas, acertar-sabiendo-la-palabra-no-es-suerte */
test('el milagro enseña jornada, resultado y probabilidad; si siempre supo la palabra, lo dice', () => {
  const ana = bloque('U_ANA').split('Acierto más milagroso')[1];
  const bea = bloque('U_BEA').split('Acierto más milagroso')[1];

  assert.match(ana, /#1730/);
  assert.match(ana, /2\/6/);
  assert.match(ana, /31 candidatas/);
  assert.match(ana, /1 de cada 31/);
  assert.match(bea, /sabiendo la palabra/);
  assert.doesNotMatch(bea, /1 de cada/);
});

/** @scenarios con-pocas-partidas-no-hay-conclusiones */
test('con pocas partidas dice cuántas faltan y no enseña cifras', () => {
  const html = bloque('U_CRIS');

  assert.match(html, /faltan 3 partidas/i);
  assert.doesNotMatch(html, /Eficiencia|Apertura|Acierto más milagroso/);
});

/** @scenarios sin-lista-no-hay-indicadores */
test('sin indicadores en la instantánea dice que no están disponibles', () => {
  assert.match(bloque('U_ANA', null), /no están disponibles/);
  assert.match(tarjetaDeIndicadores(undefined, 'U_ANA'), /no están disponibles/);
});

/** @scenarios con-pocas-partidas-no-hay-conclusiones, el-bloque-sale-en-la-ficha */
test('todo lo que llega de datos se escapa, y un dato raro no deja la ficha en blanco', () => {
  const malo = '<img src=x onerror=alert(1)>';
  const pocas = tarjetaDeIndicadores({ minimo: malo, grupo: {}, jugadores: { U1: { partidas: 1, faltan: malo } } }, 'U1');
  const raro = tarjetaDeIndicadores({ referencia: 3.41, grupo: {}, jugadores: {
    U1: { partidas: malo, media: null, apertura: 5, suerte: 1, suerte_por_partida: null, milagro: null } } }, 'U1');

  assert.doesNotMatch(pocas + raro, /<img/);
  assert.match(raro, /Tras el 1\.º intento le quedan — palabras/);
  assert.doesNotMatch(raro, /NaN/);
  assert.match(tarjetaDeIndicadores({ minimo: 5, grupo: {}, jugadores: { U1: { partidas: 4, faltan: 1 } } }, 'U1'),
    /Le falta 1 partida /);
});

/** @scenarios la-suerte-son-aciertos-reales-menos-esperados */
test('en una temporada larga la frase sigue a la cifra: +9 aciertos no es suerte corriente', () => {
  const largo = { ...INDICADORES, grupo: { ...INDICADORES.grupo, suerte_por_partida: 0 },
    jugadores: { U1: { partidas: 100, media: 3.9, apertura: [40, 4], suerte: 9, suerte_por_partida: 0.09, milagro: null } } };

  const suerte = tarjetaDeIndicadores(largo, 'U1').split('Suerte')[1];

  assert.match(suerte, /\+9<\/b>/);
  assert.match(suerte, /le sonríe/);
});

/** @scenarios el-bloque-no-habla-de-trampas */
test('el bloque no habla de trampas en ningún caso', () => {
  for (const html of [bloque('U_ANA'), bloque('U_BEA'), bloque('U_CRIS'), bloque('U_ANA', null)]) {
    assert.doesNotMatch(html, /trampa|tramposo|sospech/i);
  }
});
