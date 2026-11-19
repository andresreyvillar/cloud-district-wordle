import assert from 'node:assert/strict';
import { test } from 'node:test';
import { configurarBase, esDelEvento, resolver, rutaDe, VISTAS } from '../../../v2/js/router.js';
import { prepareResults, buildStandings, createResultsController, renderResults, podiumAnimation } from '../../../v2/js/evento/resultados.js';

const scores = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1];
const panel = (extra = {}) => ({
  terminado: true,
  grupos_f1: scores.map((points, index) => ({ grupo: `Equipo ${index + 1}`, puesto: index + 1, puntos: points,
    personas: [{ nombre: `Persona ${index + 1}`, puesto: index + 1, puntos: points }] })),
  ...extra,
});

/** @scenarios ruta-independiente */
test('resultados es una ruta del evento fuera de las estadísticas', () => {
  configurarBase('/2/');
  assert.deepEqual(resolver('/2/evento/resultados'), { vista: VISTAS.RESULTADOS_DEL_EVENTO });
  assert.equal(VISTAS.RESULTADOS_DEL_EVENTO, 'resultados-del-evento');
  assert.ok(esDelEvento(resolver('/2/evento/resultados')));
  assert.equal(rutaDe({ vista: VISTAS.RESULTADOS_DEL_EVENTO }), '/2/evento/resultados');
});

/** @scenarios espera-al-cierre */
test('el borde no revela puntos de un evento activo y se puede refrescar hasta su cierre', async () => {
  let closed = false; let calls = 0;
  const control = createResultsController({ tablero: async () => { calls++; return panel({ terminado: closed }); } });
  await control.refresh();
  assert.equal(control.state.results, null);
  assert.doesNotMatch(renderResults(control.state), /Persona 1|Equipo 1|25|revelar/i);
  control.advance(); assert.equal(control.state.step, 0);
  closed = true; await control.refresh(); assert.ok(control.state.results);
  await control.refresh(); assert.equal(calls, 2, 'el resultado cerrado queda congelado para el presentador');
});

/** @scenarios reintenta-la-lectura */
test('un fallo en la API no convierte el tablero en resultados y se recupera', async () => {
  let fail = true;
  const control = createResultsController({ tablero: async () => { if (fail) throw new Error('sin red'); return panel(); } });
  await control.refresh(); assert.match(renderResults(control.state), /Reintentar/);
  assert.equal(control.state.results, null);
  fail = false; await control.refresh(); assert.ok(control.state.results); assert.equal(control.state.error, null);
});

/** @scenarios comienza-en-cero */
test('un tablero terminado empieza en cero y no muestra todavía los nombres premiados', async () => {
  const control = createResultsController({ tablero: async () => panel() }); await control.refresh();
  assert.equal(buildStandings(control.state.results, 0).length, 10);
  assert.ok(buildStandings(control.state.results, 0).every(team => team.points === 0 && team.people.length === 0));
  assert.doesNotMatch(renderResults(control.state), /Persona \d/);
});

/** @scenarios reparte-en-orden-inverso */
test('el último premio se suma al equipo correcto y el final conserva los 101 puntos del servidor', () => {
  const results = prepareResults(panel());
  assert.equal(results.awards[0].rank, 10); assert.equal(results.awards.at(-1).rank, 1);
  const first = buildStandings(results, 1);
  assert.equal(first.find(team => team.name === 'Equipo 10').points, 1);
  assert.equal(first.filter(team => team.points > 0).length, 1);
  assert.equal(buildStandings(results, 10).reduce((sum, team) => sum + team.points, 0), 101);
  const different = prepareResults(panel({ grupos_f1: [{ grupo: 'Otro', puntos: 3.25, personas: [{ nombre: 'Nueva', puesto: 4, puntos: 3.25 }] }] }));
  assert.equal(buildStandings(different, 1)[0].points, 3.25, 'no asigna un premio nominal ni usa el fixture');
});

/** @scenarios conserva-los-empates */
test('dos primeros se revelan juntos con 21,5 cada uno y los equipos comparten puesto', () => {
  const results = prepareResults(panel({ grupos_f1: [
    { grupo: 'A', puntos: 21.5, personas: [{ nombre: 'Uno', puesto: 1, puntos: 21.5 }] },
    { grupo: 'B', puntos: 21.5, personas: [{ nombre: 'Dos', puesto: 1, puntos: 21.5 }] },
    { grupo: 'C', puntos: 0, personas: [] },
  ] }));
  assert.equal(results.awards.length, 1); assert.equal(results.awards[0].people.length, 2);
  assert.deepEqual(buildStandings(results, 1).map(team => [team.points, team.rank]), [[21.5, 1], [21.5, 1], [0, 3]]);
});

/** @scenarios retrocede-y-reinicia */
test('volver y reavanzar no duplica puntos y los límites no inventan premios', async () => {
  const control = createResultsController({ tablero: async () => panel() }); await control.refresh();
  control.back(); assert.equal(control.state.step, 0);
  control.advance(); control.advance(); control.back(); control.advance();
  assert.equal(buildStandings(control.state.results, control.state.step).reduce((sum, team) => sum + team.points, 0), 3);
  for (let index = 0; index < 20; index++) control.advance();
  assert.equal(control.state.step, 10);
  control.reset(); assert.equal(control.state.step, 0);
});

/** @scenarios anima-el-podio */
test('solo el podio se anima y movimiento reducido evita todos sus efectos', () => {
  assert.equal(podiumAnimation(4, false), null);
  for (const rank of [1, 2, 3]) assert.equal(podiumAnimation(rank, true), null);
  assert.equal(podiumAnimation(3, false).fireworks, false);
  assert.equal(podiumAnimation(2, false).fireworks, false);
  assert.equal(podiumAnimation(1, false).fireworks, true);
});

/** @scenarios sin-puntos-no-inventa-premios */
test('sin premios no hay ganador ni avance y los nombres del servidor siempre se escapan', async () => {
  const control = createResultsController({ tablero: async () => panel({ grupos_f1: [{ grupo: '<img src=x onerror=alert(1)>', puntos: 0, personas: [] }] }) });
  await control.refresh();control.advance();
  assert.equal(control.state.step, 0);
  const html = renderResults(control.state);
  assert.match(html, /No hay puntos F1 para repartir/);assert.doesNotMatch(html, /<img|Empate en cabeza/);
  const evil = prepareResults(panel({ grupos_f1: [{ grupo: '<img>', personas: [{ nombre: '<script>bad()</script>', puesto: 1, puntos: 25 }] }] }));
  const finished = renderResults({ results: evil, step: 1 });
  assert.doesNotMatch(finished, /<script>|<img>/); assert.match(finished, /&lt;script&gt;/);
});
