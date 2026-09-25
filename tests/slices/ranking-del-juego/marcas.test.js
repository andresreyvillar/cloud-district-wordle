/**
 * El ranking del juego en la web, de `ranking-del-juego`.
 *
 *     node --test tests/slices/ranking-del-juego/
 *
 * Aquí no hay red ni base de datos: la página recibe la API del ranking por parámetro y se le pasa un doble.
 * Lo que decide la base de datos —qué marca se queda, qué se rechaza— se prueba en `test_registrar_tiempo.py`
 * contra un Postgres de verdad. Los nombres son sintéticos: el repositorio es público.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { normalizar } from '../../../v2/js/data/results.js';
import { clasificacionDelNivel, jugadoresDelGrupo, tiempoPreciso } from '../../../v2/js/domain/superbros.js';
import {
  CLAVE_JUGADOR, controlDelRanking, jugadorRecordado, rankingDelNivel, recordarJugador, selectorDeJugador, vista,
} from '../../../v2/js/ui/juego.js';

/** Filas con la forma de la tabla, pasadas por el `normalizar` de verdad: la forma que ve la web. */
const RESULTADOS = [
  { slack_user_id: 'U_BEA', player_name: 'Bea', wordle_id: 1721, score: 4, date: '2026-09-23', pattern: '🟩🟩🟩🟩🟩' },
  { slack_user_id: 'U_ANA', player_name: 'Ana', wordle_id: 1721, score: 3, date: '2026-09-23', pattern: '🟩🟩🟩🟩🟩' },
  { slack_user_id: 'U_BEA', player_name: 'Bea', wordle_id: 1722, score: 2, date: '2026-09-24', pattern: '🟩🟩🟩🟩🟩' },
  { slack_user_id: 'U_CAR', player_name: 'Carlos <b>', wordle_id: 1700, score: 5, date: '2026-09-02', pattern: null },
].map(normalizar);

const JUGADORES = jugadoresDelGrupo(RESULTADOS);

/** Un almacén en memoria con la interfaz de `localStorage`. */
function almacen(inicial = {}) {
  const datos = { ...inicial };
  return { getItem: (k) => datos[k] ?? null, setItem: (k, v) => { datos[k] = String(v); }, datos };
}

/** Un almacén que lanza, como en navegación privada con el almacenamiento bloqueado. */
const ROTO = { getItem() { throw new Error('bloqueado'); }, setItem() { throw new Error('bloqueado'); } };

/** Una API de ranking falsa que recuerda lo que se le mandó. */
function api(respuesta = { mejora: true, segundos: 40 }) {
  const enviadas = [];
  return {
    enviadas,
    registrar: async (marca) => {
      enviadas.push(marca);
      if (respuesta instanceof Error) throw respuesta;
      return respuesta;
    },
  };
}

/** @scenarios elige-su-nombre-de-la-lista */
test('cada jugador del grupo sale una vez, por orden alfabético', () => {
  assert.deepEqual(JUGADORES.map((j) => j.jugador), ['U_ANA', 'U_BEA', 'U_CAR']);
  assert.deepEqual(JUGADORES.map((j) => j.nombre), ['Ana', 'Bea', 'Carlos <b>']);
});

/** @scenarios elige-su-nombre-de-la-lista */
test('también quien no jugó la jornada del nivel', () => {
  assert.ok(JUGADORES.some((j) => j.jugador === 'U_CAR'), 'jugar al juego no exige haber jugado ese Wordle');
});

/** @scenarios elige-su-nombre-de-la-lista */
test('el desplegable pregunta quién eres y trae una opción vacía', () => {
  const html = selectorDeJugador(JUGADORES, null);

  assert.match(html, /¿Quién eres\?/);
  assert.match(html, /<option value="" selected>/);
  assert.equal((html.match(/<option /g) ?? []).length, JUGADORES.length + 1);
});

/** @scenarios elige-su-nombre-de-la-lista */
test('los nombres se escapan', () => {
  const html = selectorDeJugador(JUGADORES, null);

  assert.ok(!html.includes('Carlos <b>'));
  assert.match(html, /Carlos &lt;b&gt;/);
});

/** @scenarios elige-su-nombre-de-la-lista */
test('la vista pone el desplegable y el ranking debajo del juego', () => {
  const nivel = { widthTiles: 13, heightTiles: 6, blocks: [], labels: [{ col: 3, row: 5, text: 'x' }], collectibles: [], finish: { col: 10, row: 1 } };
  const html = vista(nivel, 1722, '', JUGADORES, 'U_BEA');

  const lienzo = html.indexOf('juego-lienzo');
  assert.ok(lienzo > 0);
  assert.ok(html.indexOf('quien-eres') > lienzo, 'el desplegable va debajo del juego');
  assert.ok(html.indexOf('ranking-juego') > lienzo, 'el ranking va debajo del juego');
});

/** @scenarios recuerda-quien-eres */
test('el nombre elegido se recuerda y vuelve elegido', () => {
  const guardado = almacen();
  recordarJugador(guardado, 'U_BEA');

  assert.equal(guardado.datos[CLAVE_JUGADOR], 'U_BEA');
  assert.equal(jugadorRecordado(guardado, JUGADORES), 'U_BEA');
  assert.match(selectorDeJugador(JUGADORES, 'U_BEA'), /<option value="U_BEA" selected>/);
});

/** @scenarios recuerda-quien-eres */
test('un nombre guardado que ya no está en la lista no se elige', () => {
  assert.equal(jugadorRecordado(almacen({ [CLAVE_JUGADOR]: 'U_SE_FUE' }), JUGADORES), null);
});

/** @scenarios recuerda-quien-eres */
test('sin almacén se juega igual', () => {
  assert.equal(jugadorRecordado(ROTO, JUGADORES), null);
  assert.doesNotThrow(() => recordarJugador(ROTO, 'U_ANA'));
  assert.equal(jugadorRecordado(null, JUGADORES), null);
});

/** @scenarios terminar-registra-el-tiempo */
test('con nombre elegido, terminar manda la marca de esa jornada', async () => {
  const doble = api();
  const control = controlDelRanking({ api: doble, jornada: 1722, total: 2 });
  await control.elegir('U_BEA');

  const resultado = await control.terminar({ segundos: 41.237, estrellas: 2 });

  assert.deepEqual(doble.enviadas, [{ jornada: 1722, jugador: 'U_BEA', segundos: 41.24, estrellas: 2 }]);
  assert.equal(resultado.estado, 'mejora');
});

/** @scenarios terminar-registra-el-tiempo */
test('las estrellas se acotan al total antes de mandarlas', async () => {
  const doble = api();
  const control = controlDelRanking({ api: doble, jornada: 1722, total: 2 });
  await control.elegir('U_BEA');

  await control.terminar({ segundos: 40, estrellas: 9 });

  assert.equal(doble.enviadas[0].estrellas, 2);
});

/** @scenarios sin-nombre-el-tiempo-espera */
test('sin nombre no se manda nada y se pide que elija', async () => {
  const doble = api();
  const control = controlDelRanking({ api: doble, jornada: 1722, total: 2 });

  const resultado = await control.terminar({ segundos: 40, estrellas: 1 });

  assert.equal(resultado.estado, 'sin-jugador');
  assert.match(resultado.texto, /[Ee]lige quién eres/);
  assert.equal(doble.enviadas.length, 0);
});

/** @scenarios sin-nombre-el-tiempo-espera */
test('al elegir después se guarda ese mismo tiempo, una sola vez', async () => {
  const doble = api();
  const control = controlDelRanking({ api: doble, jornada: 1722, total: 2 });
  await control.terminar({ segundos: 40, estrellas: 1 });

  const resultado = await control.elegir('U_ANA');
  await control.elegir('U_BEA');

  assert.equal(resultado.estado, 'mejora');
  assert.deepEqual(doble.enviadas, [{ jornada: 1722, jugador: 'U_ANA', segundos: 40, estrellas: 1 }]);
});

/** @scenarios sin-nombre-el-tiempo-espera */
test('elegir nombre sin partida pendiente no manda nada', async () => {
  const doble = api();
  const control = controlDelRanking({ api: doble, jornada: 1722, total: 2 });

  assert.equal(await control.elegir('U_ANA'), null);
  assert.equal(doble.enviadas.length, 0);
});

/** @scenarios solo-se-sobrescribe-si-mejora */
test('la página dice si fue marca nueva', async () => {
  const control = controlDelRanking({ api: api({ mejora: true, segundos: 38.5 }), jornada: 1722, total: 2 });
  await control.elegir('U_BEA');

  const { estado, texto } = await control.terminar({ segundos: 38.5, estrellas: 1 });

  assert.equal(estado, 'mejora');
  assert.match(texto, /[Nn]ueva marca/);
  assert.match(texto, /0:38\.50/);
});

/** @scenarios solo-se-sobrescribe-si-mejora */
test('y si no mejora, cuál es la marca que se queda', async () => {
  const control = controlDelRanking({ api: api({ mejora: false, segundos: 31 }), jornada: 1722, total: 2 });
  await control.elegir('U_BEA');

  const { estado, texto } = await control.terminar({ segundos: 45, estrellas: 1 });

  assert.equal(estado, 'sin-mejora');
  assert.match(texto, /0:31\.00/);
  assert.ok(!/[Nn]ueva marca/.test(texto));
});

/** @scenarios se-puede-reintentar-sin-limite */
test('cada llegada a la meta se registra', async () => {
  const doble = api();
  const control = controlDelRanking({ api: doble, jornada: 1722, total: 2 });
  await control.elegir('U_BEA');

  for (const segundos of [50, 45, 60, 44]) await control.terminar({ segundos, estrellas: 1 });

  assert.deepEqual(doble.enviadas.map((m) => m.segundos), [50, 45, 60, 44]);
});

/** @scenarios un-ranking-por-nivel */
test('se ordena por tiempo y se muestra el nombre del grupo', () => {
  const tabla = clasificacionDelNivel([
    { jugador: 'U_ANA', segundos: 52.1, estrellas: 1 },
    { jugador: 'U_BEA', segundos: 40, estrellas: 2 },
  ], JUGADORES);

  assert.deepEqual(tabla.map((f) => [f.puesto, f.nombre]), [[1, 'Bea'], [2, 'Ana']]);
});

/** @scenarios un-ranking-por-nivel */
test('dos tiempos iguales comparten puesto y el siguiente salta', () => {
  const tabla = clasificacionDelNivel([
    { jugador: 'U_CAR', segundos: 50, estrellas: 0 },
    { jugador: 'U_ANA', segundos: 40, estrellas: 1 },
    { jugador: 'U_BEA', segundos: 40, estrellas: 2 },
  ], JUGADORES);

  assert.deepEqual(tabla.map((f) => f.puesto), [1, 1, 3]);
});

/** @scenarios un-ranking-por-nivel */
test('una marca de alguien que ya no está en la lista sale con su identificador', () => {
  const [fila] = clasificacionDelNivel([{ jugador: 'U_VIEJO', segundos: 40, estrellas: 0 }], JUGADORES);

  assert.equal(fila.nombre, 'U_VIEJO');
});

/** @scenarios un-ranking-por-nivel */
test('el tiempo del ranking lleva centésimas', () => {
  assert.equal(tiempoPreciso(42.371), '0:42.37');
  assert.equal(tiempoPreciso(61.5), '1:01.50');
  assert.equal(tiempoPreciso('38.9'), '0:38.90');
});

/** @scenarios un-ranking-por-nivel */
test('la tabla del ranking pinta puesto, nombre, tiempo y estrellas, y distingue tu fila', () => {
  const html = rankingDelNivel(clasificacionDelNivel([
    { jugador: 'U_BEA', segundos: 40, estrellas: 2 },
    { jugador: 'U_CAR', segundos: 50, estrellas: 0 },
  ], JUGADORES), 'U_BEA');

  assert.match(html, /Bea/);
  assert.match(html, /0:40\.00/);
  assert.match(html, /⭐ 2/);
  assert.match(html, /class="es-tuya"[^>]*>\s*<td>1<\/td>\s*<td>Bea/);
  assert.equal((html.match(/es-tuya/g) ?? []).length, 1);
  assert.match(html, /Carlos &lt;b&gt;/, 'los nombres se escapan');
});

/** @scenarios sin-marcas-lo-dice */
test('sin marcas se dice que nadie lo ha terminado', () => {
  const html = rankingDelNivel([], 'U_BEA');

  assert.match(html, /[Nn]adie ha terminado/);
  assert.ok(!html.includes('<table'));
});

/** @scenarios si-falla-el-guardado-se-dice */
test('si la llamada falla se dice y no se rompe nada', async () => {
  const control = controlDelRanking({ api: api(new Error('tiempo imposible')), jornada: 1722, total: 2 });
  await control.elegir('U_BEA');

  const { estado, texto } = await control.terminar({ segundos: 40, estrellas: 1 });

  assert.equal(estado, 'error');
  assert.match(texto, /no se ha podido guardar/);
});

/** @scenarios si-falla-el-guardado-se-dice */
test('tras un fallo se puede volver a terminar y guardar', async () => {
  let fallar = true;
  const enviadas = [];
  const doble = {
    registrar: async (marca) => {
      enviadas.push(marca);
      if (fallar) { fallar = false; throw new Error('red'); }
      return { mejora: true, segundos: marca.segundos };
    },
  };
  const control = controlDelRanking({ api: doble, jornada: 1722, total: 2 });
  await control.elegir('U_BEA');

  await control.terminar({ segundos: 40, estrellas: 1 });
  const segundo = await control.terminar({ segundos: 39, estrellas: 1 });

  assert.equal(segundo.estado, 'mejora');
  assert.equal(enviadas.length, 2);
});
