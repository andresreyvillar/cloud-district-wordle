/**
 * La web juega el nivel congelado, de `nivel-congelado`.
 *
 *     node --test tests/slices/nivel-congelado/
 *
 * Sin red: la capa de datos recibe un cliente falso con la interfaz de supabase-js, y la pestaña, una fuente
 * de niveles falsa.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { leerNivelCongelado } from '../../../v2/js/data/results.js';
import { nivelParaJugar, vista } from '../../../v2/js/ui/juego.js';

const NIVEL = {
  widthTiles: 13, heightTiles: 6, blocks: [{ col: 0, row: 0, type: 'ground' }],
  labels: [{ col: 3, row: 5, text: 'Ana  3/6' }], collectibles: [{ col: 4, row: 2 }], finish: { col: 10, row: 1 },
};

/** Un cliente de supabase-js falso que recuerda la consulta. */
function cliente(respuesta) {
  const consulta = {};
  const cadena = {
    from(tabla) { consulta.tabla = tabla; return cadena; },
    select(columnas) { consulta.columnas = columnas; return cadena; },
    order(columna, opciones) { consulta.orden = [columna, opciones]; return cadena; },
    limit(n) { consulta.limite = n; return Promise.resolve(respuesta); },
  };
  return { cadena, consulta };
}

/** @scenarios la-web-juega-el-ultimo-nivel-congelado */
test('la web lee el último nivel congelado de game_levels', async () => {
  const { cadena, consulta } = cliente({ data: [{ jornada: 1722, fecha: '2026-09-24', nivel: NIVEL }], error: null });

  const partida = await leerNivelCongelado(cadena);

  assert.equal(consulta.tabla, 'game_levels');
  assert.deepEqual(consulta.orden, ['jornada', { ascending: false }]);
  assert.equal(consulta.limite, 1);
  assert.deepEqual(partida, { jornada: 1722, fecha: '2026-09-24', nivel: NIVEL });
});

/** @scenarios la-web-juega-el-ultimo-nivel-congelado */
test('la pestaña juega lo que dice la fuente, no lo que calcularía de los resultados', async () => {
  const partida = await nivelParaJugar({ ultimo: async () => ({ jornada: 1700, fecha: '2026-09-02', nivel: NIVEL }) });

  assert.equal(partida.jornada, 1700);
  assert.equal(partida.nivel, NIVEL);
});

/** @scenarios la-web-juega-el-ultimo-nivel-congelado */
test('la cabecera lleva la jornada y la fecha del nivel congelado', () => {
  const html = vista(NIVEL, 1722, 'jornada de ayer · 24 de septiembre');

  assert.match(html, /#1722/);
  assert.match(html, /24 de septiembre/);
});

/** @scenarios sin-nivel-congelado-lo-dice */
test('sin niveles congelados no hay partida', async () => {
  const { cadena } = cliente({ data: [], error: null });

  assert.equal(await leerNivelCongelado(cadena), null);
  assert.equal(await nivelParaJugar({ ultimo: async () => null }), null);
});

/** @scenarios sin-nivel-congelado-lo-dice */
test('si no se puede leer, tampoco: no rompe la pestaña', async () => {
  assert.equal(await nivelParaJugar({ ultimo: async () => { throw new Error('red'); } }), null);
});

/** @scenarios sin-nivel-congelado-lo-dice */
test('y la vista lo dice en lugar de montar el lienzo', () => {
  const html = vista(null, null);

  assert.match(html, /todavía no hay ningún nivel/);
  assert.ok(!html.includes('juego-lienzo'));
});
