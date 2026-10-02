/**
 * La pestaña Info, de `reglas-explicadas` (pack `feat-pestana-info`).
 *
 *     node --test tests/slices/reglas-explicadas/
 *
 * Las reglas llegan como las publica el pipeline: aquí, un catálogo sintético con una regla de cada tipo.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { configurarBase, resolver, VISTAS } from '../../../v2/js/router.js';
import { navegacion } from '../../../v2/js/ui/shell.js';
import { pintarInfo } from '../../../v2/js/ui/info.js';

const regla = (id, eje, estado, extra = {}) => ({
  id, eje, estado, titulo: `Regla ${id}`, que_hace: `Qué hace ${id}.`, por_que: `Por qué ${id}.`,
  votada: false, falta_decidir: '', historica: false, parametros: [], ...extra,
});

const REGLAS = [
  regla('dias-laborables', 'temporada', 'aplicada', { parametros: [{ nombre: 'jugadores por día', valor: 5, fuente: 'x', unidad: '' }] }),
  regla('temporada-cero', 'temporada', 'aplicada', { historica: true }),
  regla('rachas', 'medallas', 'sin-decidir', { falta_decidir: 'si cuentan los findes' }),
  regla('juego-puntos-por-puesto', 'juego', 'aplicada'),
];

function pintar(reglas = REGLAS) {
  const contenedor = { innerHTML: '' };
  pintarInfo(contenedor, reglas);
  return contenedor.innerHTML;
}

const secciones = (html) => [...html.matchAll(/<h2[^>]*>([^<]*)<\/h2>/g)].map(([, t]) => t);

/** @scenarios la-pestana-info-explica-como-se-juega */
test('Info tiene cuatro apartados en orden, con la palabra del día y el canal', () => {
  const html = pintar();

  assert.deepEqual(secciones(html).slice(0, 4), [
    'Cómo se juega', 'Las competiciones', 'Lo que publica el bot', 'Reglas vigentes',
  ]);
  assert.match(html, /href="https:\/\/lapalabradeldia\.com"/);
  assert.match(html, /#wordle-line/);
  for (const competicion of ['marcador', 'SuperWordleBros', 'figuras', 'medallas']) {
    assert.match(html, new RegExp(competicion, 'i'), competicion);
  }
});

/** @scenarios la-explicacion-no-lleva-numeros */
test('la explicación no escribe cifras a mano', () => {
  const html = pintar();
  const explicacion = html.slice(0, html.indexOf('Reglas vigentes')).replace(/<[^>]+>/g, ' ');

  assert.ok(!/\d/.test(explicacion), explicacion.match(/.{0,30}\d.{0,30}/)?.[0]);
});

/** @scenarios solo-se-ensenan-las-reglas-vigentes */
test('solo salen las reglas aplicadas que no son históricas, sin marcas de estado ni de votación', () => {
  const reglas = pintar().slice(pintar().indexOf('Reglas vigentes'));

  assert.match(reglas, /Regla dias-laborables/);
  assert.match(reglas, /Regla juego-puntos-por-puesto/);
  assert.ok(!reglas.includes('Regla temporada-cero'), 'la histórica no sale');
  assert.ok(!reglas.includes('Regla rachas'), 'la propuesta no sale');
  assert.ok(!/Sin decidir|Se aplica|votad/i.test(reglas), 'sin marcas de estado ni de votación');
});

/** @scenarios los-parametros-son-los-que-el-calculo-usa */
test('los números de una regla salen de sus parámetros', () => {
  assert.match(pintar(), /jugadores por día<\/span>\s*<span class="pvalor">5</);
});

/** @scenarios el-superwordlebros-tiene-sus-reglas */
test('las reglas del juego van en su propio apartado', () => {
  const reglas = pintar().slice(pintar().indexOf('Reglas vigentes'));

  assert.match(reglas, /SuperWordleBros[\s\S]*?Regla juego-puntos-por-puesto/);
});

/** @scenarios los-enlaces-viejos-llevan-a-info */
test('/reglas y /t/AAAA-MM/reglas llevan a Info, y la pestaña dice Info', () => {
  configurarBase('/2/');
  assert.equal(resolver('/2/reglas').vista, VISTAS.INFO);
  assert.equal(resolver('/2/t/2026-09/reglas').vista, VISTAS.INFO);
  assert.equal(resolver('/2/info').vista, VISTAS.INFO);
  const nav = navegacion({ vista: VISTAS.INFO });
  configurarBase('/');

  assert.match(nav, /<a href="\/2\/info"[^>]*>Info</);
  assert.ok(!/>Reglas</.test(nav));
});

/** @scenarios sin-instantanea-la-pagina-lo-dice */
test('sin reglas, Info explica igual cómo se juega y dice que las reglas no están disponibles', () => {
  const html = pintar(null);

  assert.match(html, /Cómo se juega/);
  assert.match(html, /no están disponibles/);
});
