/**
 * Congelar el nivel de cada jornada, de `nivel-congelado`.
 *
 *     node --test tests/slices/nivel-congelado/
 *
 * Aquí no hay red: el script recibe `fetch` por parámetro y se le pasa un doble que hace de PostgREST. El
 * reloj tampoco: la fecha y la hora de Madrid entran por parámetro, como exige §10. Los jugadores son
 * sintéticos: el repositorio es público.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { congelar } from '../../../tools/congelar_nivel.mjs';
import { HORA_DE_CONGELAR, jornadaACongelar, nivelDe } from '../../../v2/js/domain/superbros.js';
import { normalizar } from '../../../v2/js/data/results.js';

/** Filas con la forma de la tabla: la jornada 1722 es la del 24, la 1723 la del 25. */
const FILAS = [
  { slack_user_id: 'U_ANA', player_name: 'Ana', wordle_id: 1721, score: 3, date: '2026-09-23', pattern: '🟩⬛⬛⬛⬛/🟨🟩⬛⬛⬛/🟩🟩🟩🟩🟩' },
  { slack_user_id: 'U_ANA', player_name: 'Ana', wordle_id: 1722, score: 2, date: '2026-09-24', pattern: '🟩🟨⬛⬛⬛/🟩🟩🟩🟩🟩' },
  { slack_user_id: 'U_BEA', player_name: 'Bea', wordle_id: 1722, score: 4, date: '2026-09-24', pattern: '⬛⬛⬛⬛🟩/⬛⬛🟨⬛🟩/🟩⬛🟩⬛🟩/🟩🟩🟩🟩🟩' },
  { slack_user_id: 'U_BEA', player_name: 'Bea', wordle_id: 1723, score: 3, date: '2026-09-25', pattern: '🟩⬛⬛⬛⬛/🟩🟩⬛⬛⬛/🟩🟩🟩🟩🟩' },
];
const RESULTADOS = FILAS.map(normalizar);

const URL_BASE = 'https://ejemplo.supabase.co';

/**
 * Un PostgREST falso: sirve las filas pedidas, recuerda los niveles congelados y **no pisa uno que ya
 * existe**, como `resolution=ignore-duplicates`.
 */
function postgrest({ filas = FILAS, congelados = {} } = {}) {
  const peticiones = [];
  const niveles = { ...congelados };
  const fetch = async (direccion, opciones = {}) => {
    const url = new URL(direccion);
    const metodo = opciones.method ?? 'GET';
    peticiones.push({ metodo, url, cabeceras: opciones.headers ?? {}, cuerpo: opciones.body });
    const json = (datos, status = 200) => ({ ok: status < 300, status, json: async () => datos, text: async () => JSON.stringify(datos) });
    if (url.pathname === '/rest/v1/wordle_results') {
      const filtros = url.searchParams.getAll('date');
      const desde = filtros.find((f) => f.startsWith('gte.'))?.slice(4) ?? '0000';
      const hasta = filtros.find((f) => f.startsWith('lt.'))?.slice(3) ?? '9999';
      return json(filas.filter((f) => f.date >= desde && f.date < hasta));
    }
    if (url.pathname === '/rest/v1/game_levels' && metodo === 'GET') {
      const jornada = Number(url.searchParams.get('jornada').slice(3));
      return json(niveles[jornada] ? [{ jornada }] : []);
    }
    if (url.pathname === '/rest/v1/game_levels' && metodo === 'POST') {
      const fila = JSON.parse(opciones.body);
      if (niveles[fila.jornada]) return json([], 201);
      niveles[fila.jornada] = fila;
      return json([fila], 201);
    }
    return json({ message: 'ruta desconocida' }, 404);
  };
  return { fetch, peticiones, niveles };
}

function ejecutar(servidor, opciones) {
  const lineas = [];
  const hecho = congelar({
    fetch: servidor.fetch, url: URL_BASE, clave: 'clave-de-prueba', seco: false, log: (l) => lineas.push(l), ...opciones,
  });
  return hecho.then((resultado) => ({ ...resultado, lineas }));
}

const escrituras = (servidor) => servidor.peticiones.filter((p) => p.metodo !== 'GET');

/** @scenarios se-congela-a-la-hora */
test('a las 02:00 toca la jornada de ayer', () => {
  assert.equal(HORA_DE_CONGELAR, '02:00');
  assert.equal(jornadaACongelar(RESULTADOS, '2026-09-25', '02:00'), 1722);
  assert.equal(jornadaACongelar(RESULTADOS, '2026-09-25', '17:30'), 1722);
});

/** @scenarios se-congela-a-la-hora */
test('la de hoy no se congela nunca, aunque ya tenga cuadrículas', () => {
  assert.equal(jornadaACongelar(RESULTADOS, '2026-09-25', '23:59'), 1722);
});

/** @scenarios se-congela-a-la-hora */
test('el cron guarda el nivel que da nivelDe, con su jornada y su fecha', async () => {
  const servidor = postgrest();

  const resultado = await ejecutar(servidor, { hoy: '2026-09-25', hora: '02:10' });

  assert.equal(resultado.accion, 'congelado');
  assert.deepEqual(servidor.niveles[1722], { jornada: 1722, fecha: '2026-09-24', nivel: nivelDe(RESULTADOS, 1722) });
});

/** @scenarios se-congela-a-la-hora */
test('escribe con la clave de servicio y sin pisar un duplicado', async () => {
  const servidor = postgrest();

  await ejecutar(servidor, { hoy: '2026-09-25', hora: '02:10' });

  const [post] = escrituras(servidor);
  assert.equal(post.url.searchParams.get('on_conflict'), 'jornada');
  assert.match(post.cabeceras.Prefer, /resolution=ignore-duplicates/);
  assert.equal(post.cabeceras.Authorization, 'Bearer clave-de-prueba');
});

/** @scenarios antes-de-la-hora-no-se-congela */
test('antes de las 02:00 la de ayer todavía no toca', () => {
  assert.equal(jornadaACongelar(RESULTADOS, '2026-09-25', '01:59'), 1721);
  assert.equal(jornadaACongelar(RESULTADOS, '2026-09-25', '00:00'), 1721);
});

/** @scenarios antes-de-la-hora-no-se-congela */
test('antes de las 02:00 se congela la de anteayer si el cron estuvo caído', async () => {
  const servidor = postgrest();

  const resultado = await ejecutar(servidor, { hoy: '2026-09-25', hora: '01:30' });

  assert.equal(resultado.accion, 'congelado');
  assert.equal(resultado.jornada, 1721);
  assert.equal(servidor.niveles[1722], undefined, 'la de ayer sigue sin congelar');
});

/** @scenarios antes-de-la-hora-no-se-congela */
test('antes de las 02:00, con anteayer ya congelado, no se escribe nada', async () => {
  const servidor = postgrest({ congelados: { 1721: { jornada: 1721 } } });

  const resultado = await ejecutar(servidor, { hoy: '2026-09-25', hora: '01:30' });

  assert.equal(resultado.accion, 'ya-congelado');
  assert.equal(escrituras(servidor).length, 0);
});

/** @scenarios un-nivel-congelado-no-cambia */
test('una jornada ya congelada no se vuelve a escribir, aunque haya cuadrículas nuevas', async () => {
  const antes = { jornada: 1722, fecha: '2026-09-24', nivel: { original: true } };
  const tarde = { slack_user_id: 'U_CAR', player_name: 'Carlos', wordle_id: 1722, score: 5, date: '2026-09-24', pattern: '🟩🟩🟩🟩🟩' };
  const servidor = postgrest({ filas: [...FILAS, tarde], congelados: { 1722: antes } });

  const resultado = await ejecutar(servidor, { hoy: '2026-09-25', hora: '10:00' });

  assert.equal(resultado.accion, 'ya-congelado');
  assert.equal(escrituras(servidor).length, 0);
  assert.deepEqual(servidor.niveles[1722], antes);
});

/** @scenarios un-nivel-congelado-no-cambia */
test('dos vueltas seguidas dejan un solo nivel', async () => {
  const servidor = postgrest();

  await ejecutar(servidor, { hoy: '2026-09-25', hora: '10:00' });
  const segunda = await ejecutar(servidor, { hoy: '2026-09-25', hora: '11:00' });

  assert.equal(segunda.accion, 'ya-congelado');
  assert.equal(escrituras(servidor).length, 1);
});

/** @scenarios el-cron-declara-lo-que-escribe */
test('dice qué congela antes de escribir', async () => {
  const servidor = postgrest();
  const lineas = [];
  let escritoAlDecirlo = null;
  const fetch = async (direccion, opciones = {}) => {
    if ((opciones.method ?? 'GET') === 'POST') escritoAlDecirlo = lineas.some((l) => /#1722/.test(l));
    return servidor.fetch(direccion, opciones);
  };

  await congelar({ fetch, url: URL_BASE, clave: 'k', hoy: '2026-09-25', hora: '10:00', seco: false, log: (l) => lineas.push(l) });

  assert.equal(escritoAlDecirlo, true, 'la línea con la jornada sale antes del POST');
  assert.match(lineas.join('\n'), /#1722 · 2026-09-24 · 2 tramos/);
});

/** @scenarios el-cron-declara-lo-que-escribe */
test('con --seco calcula y no escribe', async () => {
  const servidor = postgrest();

  const resultado = await ejecutar(servidor, { hoy: '2026-09-25', hora: '10:00', seco: true });

  assert.equal(resultado.accion, 'seco');
  assert.equal(escrituras(servidor).length, 0);
  assert.match(resultado.lineas.join('\n'), /no se escribe/);
});

/** @scenarios el-cron-declara-lo-que-escribe */
test('si nadie tiene cuadrícula lo dice y no escribe', async () => {
  const sinPatron = FILAS.map((f) => ({ ...f, pattern: null }));
  const servidor = postgrest({ filas: sinPatron });

  const resultado = await ejecutar(servidor, { hoy: '2026-09-25', hora: '10:00' });

  assert.equal(resultado.accion, 'sin-cuadriculas');
  assert.equal(escrituras(servidor).length, 0);
});

/** @scenarios el-cron-declara-lo-que-escribe */
test('el error que llega al log público no copia los detalles de la fila', async () => {
  const cuerpo = JSON.stringify({ code: '23514', message: 'viola nivel_con_forma', details: 'Failing row contains (Ana  2/6)' });
  const fetch = async () => ({ ok: false, status: 400, json: async () => JSON.parse(cuerpo), text: async () => cuerpo });

  await assert.rejects(
    congelar({ fetch, url: URL_BASE, clave: 'k', hoy: '2026-09-25', hora: '10:00', seco: false, log: () => {} }),
    (error) => /400: viola nivel_con_forma/.test(error.message) && !/Ana/.test(error.message),
  );
});

/** @scenarios el-cron-declara-lo-que-escribe */
test('si PostgREST falla, el script falla y lo dice', async () => {
  const fetch = async () => ({ ok: false, status: 500, json: async () => ({}), text: async () => 'caído' });

  await assert.rejects(
    congelar({ fetch, url: URL_BASE, clave: 'k', hoy: '2026-09-25', hora: '10:00', seco: false, log: () => {} }),
    /500/,
  );
});
