/**
 * Los apodos de la web, de `apodos-en-la-web` (Fase 2 — TDD rojo).
 *
 *     node --test tests/slices/apodos-en-la-web/
 *
 * El apodo es presentación: se pinta en lugar del nombre y la identidad (el id de Slack) no cambia.
 */

import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { test } from 'node:test';

import { APODOS, etiquetaVisible, nivelConApodos, nombreVisible } from '../../../v2/js/domain/apodos.js';
import { normalizar } from '../../../v2/js/data/results.js';
import { pintarDatos } from '../../../v2/js/ui/datos.js';
import { pintarHoy } from '../../../v2/js/ui/hoy.js';
import { controlDelRanking, rankingDelNivel, selectorDeJugador } from '../../../v2/js/ui/juego.js';
import { pintarJugador } from '../../../v2/js/ui/jugador.js';
import { pintarTemporada } from '../../../v2/js/ui/temporada.js';

const TACHADO = '̶';
const APODO = `${[...'Carrillo'].map((letra) => letra + TACHADO).join('')} ChatGPT`;

function carga() {
  const fila = (jugador, nombre, posicion) => ({
    jugador, nombre, posicion, clasificado: true, media_temporada: 3 + posicion / 10, jugados: 5, por_dia: [3, 4], dias: 2,
  });
  return {
    etiqueta: 'Temporada 2', estado: 'en curso', dias: [1, 2], jugadores: ['U_CARRILLO', 'U_ANA'], resultados: 10,
    clasificacion: [fila('U_CARRILLO', 'Carrillo', 1), fila('U_ANA', 'Ana', 2)],
    album: { categorias: [], jugadores: [], clasificados: 0, minimo: 3, sin_patron: 0, clasificadas: 0 },
    dificultad: { 1: 3.5, 2: 4.2 },
    logros: { fondista: ['Carrillo', 'Ana'] },
    juego: {
      escala: [10, 8, 6, 5, 4, 3, 2, 1],
      niveles: 2,
      clasificacion: [{ posicion: 1, jugador: 'U_CARRILLO', nombre: 'Carrillo', puntos: 20, niveles: 2, victorias: 2 }],
    },
  };
}

function temporada() {
  const contenedor = { innerHTML: '' };
  pintarTemporada(contenedor, carga(), '2026-10');
  return contenedor.innerHTML;
}

/** @scenarios el-apodo-sustituye-al-nombre-en-cada-vista */
test('Carrillo tiene declarado su apodo, con el nombre tachado letra a letra', () => {
  assert.equal(nombreVisible('Carrillo'), APODO);
  assert.equal(APODOS.Carrillo, APODO);
});

/** @scenarios el-apodo-sustituye-al-nombre-en-cada-vista */
test('la temporada pinta el apodo en podio, titular, marcador, juego y logros', () => {
  const html = temporada();

  // Podio, titular, tira de partida, marcador y bloque del juego: cinco apariciones al menos, más logros.
  assert.ok(html.split(APODO).length - 1 >= 6, `apariciones: ${html.split(APODO).length - 1}`);
  assert.ok(!/>Carrillo</.test(html), 'ningún enlace dice «Carrillo» a secas');
  assert.match(html, new RegExp(`${APODO}, Ana`), 'los logros también');
});

/** @scenarios el-apodo-sustituye-al-nombre-en-cada-vista */
test('el selector y el ranking del SuperWordleBros pintan el apodo', () => {
  const selector = selectorDeJugador([{ jugador: 'U_CARRILLO', nombre: 'Carrillo' }], null);
  const ranking = rankingDelNivel([{ puesto: 1, jugador: 'U_CARRILLO', nombre: 'Carrillo', segundos: 31.2, estrellas: 9 }], null);

  assert.ok(selector.includes(`>${APODO}</option>`), selector);
  assert.ok(ranking.includes(`<td>${APODO}</td>`), ranking);
});

/** @scenarios el-apodo-sustituye-al-nombre-en-cada-vista, el-apodo-va-escapado */
test('ninguna vista pinta un nombre de jugador sin pasar por nombreVisible dentro de escapar', () => {
  const carpeta = new URL('../../../v2/js/ui/', import.meta.url);
  // Lo que se llama `nombre` pero no es una persona: el nombre de un parámetro de regla y el de un logro.
  const noEsUnaPersona = /escapar\((p|logro)\.nombre\)/;
  const sueltos = [];
  for (const fichero of readdirSync(carpeta).filter((f) => f.endsWith('.js'))) {
    readFileSync(new URL(fichero, carpeta), 'utf8').split('\n').forEach((linea, i) => {
      for (const uso of linea.match(/escapar\((?!nombreVisible\()[^)]*\b(nombre|quienes\.join)\b[^)]*\)/g) ?? []) {
        if (!noEsUnaPersona.test(uso)) sueltos.push(`${fichero}:${i + 1} ${uso}`);
      }
    });
  }
  assert.deepEqual(sueltos, []);
});

/** @scenarios la-identidad-no-cambia */
test('el enlace a la ficha y el valor del selector siguen siendo el id de Slack', () => {
  const html = temporada();
  const selector = selectorDeJugador([{ jugador: 'U_CARRILLO', nombre: 'Carrillo' }], 'U_CARRILLO');

  assert.match(html, new RegExp(`href="[^"]*/j/U_CARRILLO"[^>]*>${APODO}<`));
  assert.ok(selector.includes(`<option value="U_CARRILLO" selected>${APODO}</option>`), selector);
  const ranking = rankingDelNivel([{ puesto: 1, jugador: 'U_CARRILLO', nombre: 'Carrillo', segundos: 31.2, estrellas: 9 }], 'U_CARRILLO');
  assert.match(ranking, /class="es-tuya"/, 'la fila propia se reconoce por id');
});

/** @scenarios quien-no-tiene-apodo-sale-igual */
test('quien no tiene apodo sale con su nombre, sin tocar', () => {
  assert.equal(nombreVisible('Ana'), 'Ana');
  assert.equal(nombreVisible(undefined), undefined);
  assert.equal(etiquetaVisible('Ana  4/6'), 'Ana  4/6');
  assert.match(temporada(), /href="[^"]*\/j\/U_ANA"[^>]*>Ana</);
});

/** @scenarios el-nivel-del-juego-pinta-el-apodo */
test('la etiqueta del tramo lleva el apodo y el nivel congelado no cambia', () => {
  const nivel = { labels: [{ col: 1, row: 2, text: 'Carrillo  4/6' }, { col: 9, row: 2, text: 'Ana  X/6' }], blocks: [] };
  const copia = JSON.parse(JSON.stringify(nivel));

  const montado = nivelConApodos(nivel);

  assert.deepEqual(montado.labels.map((l) => l.text), [`${APODO}  4/6`, 'Ana  X/6']);
  assert.deepEqual(nivel, copia, 'el nivel original no se toca');
  assert.equal(etiquetaVisible('Carrillo Pérez  4/6'), 'Carrillo Pérez  4/6', 'solo el nombre entero');
  assert.equal(nivelConApodos(null), null);
});

/** @scenarios el-apodo-va-escapado */
test('un apodo con marcado sale como texto', () => {
  APODOS['Zoe'] = '<b>Zoe</b>';
  try {
    const selector = selectorDeJugador([{ jugador: 'U_ZOE', nombre: 'Zoe' }], null);
    assert.ok(selector.includes('&lt;b&gt;Zoe&lt;/b&gt;'), selector);
  } finally {
    delete APODOS['Zoe'];
  }
});

/** @scenarios el-nivel-del-juego-pinta-el-apodo */
test('la vista del juego monta el motor con el nivel apodado, no con el congelado', () => {
  // El motor es de Joel y monta lo que recibe: el apodo se aplica en la llamada, y el resto del nivel
  // (coleccionables, total del texto para compartir) se sigue leyendo del congelado.
  const fuente = readFileSync(new URL('../../../v2/js/ui/juego.js', import.meta.url), 'utf8');
  const llamadas = [...fuente.matchAll(/partida = montar\((.*)\);/g)].map((m) => m[1]);

  assert.deepEqual(llamadas, ['lienzo, nivelConApodos(nivel), Phaser']);
});

/** Las filas crudas de hoy, como llegan de Supabase. */
const HOY = '2026-10-02';
const FILAS = [
  { slack_user_id: 'U_CARRILLO', player_name: 'Carrillo', wordle_id: 1700, score: 4, date: HOY, pattern: null },
  { slack_user_id: 'U_ANA', player_name: 'Ana', wordle_id: 1700, score: 3, date: HOY, pattern: null },
].map(normalizar);

function pintada(pintar, ...argumentos) {
  const contenedor = { innerHTML: '' };
  pintar(contenedor, ...argumentos);
  return contenedor.innerHTML;
}

/** @scenarios el-apodo-sustituye-al-nombre-en-cada-vista */
test('hoy, la ficha y la tabla de datos pintan el apodo y nunca el nombre a secas', () => {
  const instantaneas = new Map([['2026-10', { ...carga(), temporada: '2026-10' }]]);
  const vistas = {
    hoy: pintada(pintarHoy, FILAS, instantaneas, '2026-10'),
    ficha: pintada(pintarJugador, instantaneas, '2026-10', 'U_CARRILLO'),
    datos: pintada(pintarDatos, FILAS, instantaneas),
  };

  for (const [cual, html] of Object.entries(vistas)) {
    assert.ok(html.includes(APODO), `${cual} pinta el apodo`);
    assert.ok(!html.replaceAll(APODO, '').includes('Carrillo'), `${cual} no dice «Carrillo» a secas`);
  }
});

/** @scenarios la-identidad-no-cambia */
test('elegir al apodado en el selector y terminar el nivel guarda la marca con su id', async () => {
  const selector = selectorDeJugador([{ jugador: 'U_CARRILLO', nombre: 'Carrillo' }], null);
  const valor = selector.match(new RegExp(`<option value="([^"]*)">${APODO}<`))[1];
  const enviadas = [];
  const control = controlDelRanking({
    api: { registrar: async (marca) => { enviadas.push(marca); return { mejora: true, segundos: 31.2, estrellas: 9 }; } },
    jornada: 1700,
    total: 10,
  });

  await control.elegir(valor);
  await control.terminar({ segundos: 31.2, estrellas: 9 });

  assert.equal(enviadas[0].jugador, 'U_CARRILLO');
});
