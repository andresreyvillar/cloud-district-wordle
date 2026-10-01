/**
 * El bloque SUPERWORDLEBROS de la temporada, de `marcador-del-juego` (Fase 2 — TDD rojo).
 *
 *     node --test tests/slices/marcador-del-juego/
 *
 * La web **pinta** la clasificación que dejó el pipeline en la instantánea: no puntúa ni ordena. Por eso los
 * fixtures traen `juego` ya calculado. Los nombres son sintéticos: el repositorio es público.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { pintarTemporada } from '../../../v2/js/ui/temporada.js';

const JUEGO = {
  escala: [10, 8, 6, 5, 4, 3, 2, 1],
  niveles: 4,
  clasificacion: [
    { posicion: 1, jugador: 'U_BEA', nombre: 'Bea', puntos: 36, niveles: 4, victorias: 3 },
    { posicion: 2, jugador: 'U_ANA', nombre: 'Ana', puntos: 28, niveles: 4, victorias: 1 },
    { posicion: 2, jugador: 'U_CAR', nombre: 'Carlos <b>', puntos: 28, niveles: 3, victorias: 0 },
  ],
};

/** Una carga mínima con la que `pintarTemporada` pinta todos sus bloques. `null`: una instantánea sin la clave `juego`. */
function carga(juego = JUEGO) {
  const fila = (jugador, nombre, posicion) => ({
    jugador, nombre, posicion, clasificado: true, media_temporada: 3 + posicion / 10, jugados: 5, por_dia: [3, 4], dias: 2,
  });
  return {
    etiqueta: 'Temporada 2', estado: 'en curso', dias: [1, 2], jugadores: ['U_ANA', 'U_BEA'], resultados: 10,
    clasificacion: [fila('U_ANA', 'Ana', 1), fila('U_BEA', 'Bea', 2)],
    album: { categorias: [], jugadores: [], clasificados: 0, minimo: 3, sin_patron: 0, clasificadas: 0 },
    dificultad: { 1: 3.5, 2: 4.2 },
    ...(juego === null ? {} : { juego }),
  };
}

function pintar(datos) {
  const contenedor = { innerHTML: '' };
  pintarTemporada(contenedor, datos, '2026-09');
  return contenedor.innerHTML;
}

/** Solo el bloque del juego, para no confundir sus filas con las del marcador general. */
function bloque(html) {
  const inicio = html.indexOf('SUPERWORDLEBROS');
  assert.ok(inicio >= 0, 'hay bloque del juego');
  return html.slice(inicio, html.indexOf('</section>', inicio));
}

/** @scenarios el-bloque-va-debajo-del-album */
test('el bloque del juego va entre el álbum de figuras y las estadísticas', () => {
  const html = pintar(carga());

  const album = html.indexOf('ÁLBUM DE FIGURAS');
  const juego = html.indexOf('SUPERWORDLEBROS');
  const estadisticas = html.indexOf('ESTADÍSTICAS');
  assert.ok(album >= 0 && juego > album && estadisticas > juego, `${album} < ${juego} < ${estadisticas}`);
});

/** @scenarios cada-fila-lleva-puesto-puntos-niveles-y-victorias */
test('cada fila lleva nombre, puntos, niveles y victorias, en el orden de la instantánea', () => {
  const html = bloque(pintar(carga()));

  assert.ok(html.indexOf('Bea') < html.indexOf('Ana'), 'respeta el orden del pipeline');
  assert.match(html, /Bea[\s\S]*?36[\s\S]*?4[\s\S]*?3/);
  assert.match(html, /Ana[\s\S]*?28[\s\S]*?4[\s\S]*?1/);
});

/** @scenarios los-empates-se-ven-como-empates */
test('el puesto compartido solo se escribe en la primera fila', () => {
  const html = bloque(pintar(carga()));

  assert.equal((html.match(/>2º?</g) ?? []).length, 1, 'el 2 sale una vez para Ana y Carlos');
});

/** @scenarios la-escala-se-explica */
test('el bloque explica la escala y cuántos niveles lleva el mes', () => {
  const html = bloque(pintar(carga()));

  assert.match(html, /10 · 8 · 6 · 5 · 4 · 3 · 2 · 1/);
  assert.match(html, /4 niveles/);
});

/** @scenarios sin-marcas-no-hay-bloque */
test('sin clasificación del juego, o sin la clave, no hay bloque y el resto sale igual', () => {
  const vacia = pintar(carga({ ...JUEGO, clasificacion: [] }));
  const antigua = pintar(carga(null));

  assert.ok(!vacia.includes('SUPERWORDLEBROS'));
  assert.ok(!antigua.includes('SUPERWORDLEBROS'));
  assert.ok(antigua.includes('ÁLBUM DE FIGURAS') && antigua.includes('ESTADÍSTICAS'));
});

/** @scenarios los-nombres-se-escapan */
test('los nombres se escapan', () => {
  const html = bloque(pintar(carga()));

  assert.ok(!html.includes('Carlos <b>'));
  assert.match(html, /Carlos &lt;b&gt;/);
});
