/**
 * Escenarios de `ficha-de-jugador` (Fase 2 — TDD rojo).
 *
 *     node --test tests/slices/ficha-de-jugador/
 *
 * Las instantáneas del fixture tienen la forma exacta que materializa `tools/seasons.py`: si divergieran,
 * estos tests pasarían con datos que producción no produce. La forma se copia de la carga útil real, no se
 * inventa.
 *
 * La ficha **no calcula**: proyecta la instantánea. Por eso el módulo bajo prueba es puro y no necesita
 * navegador; lo que sí necesita navegador —que se vea— se comprueba aparte.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { ficha, palmares, rutaDeFicha } from '../../../v2/js/data/ficha.js';
import { filaDeMarcador } from '../../../v2/js/ui/temporada.js';

const ANA = 'U_ANA';
const ZOE = 'U_ZOE';

function porDia(entradas) {
  return entradas.map(([jornada, intentos, imputado]) => ({
    jornada,
    fecha: `2026-09-${String(jornada - 1699).padStart(2, '0')}`,
    intentos,
    imputado,
  }));
}

/** Una fila de clasificación con la forma que materializa Python. */
function fila(jugador, nombre, extra = {}) {
  return {
    jugador,
    nombre,
    dias: 4,
    jugados: 3,
    media_jugada: 3.33,
    media_temporada: 3.75,
    mejor: 2,
    peor: 5,
    distribucion: [0, 1, 1, 0, 1, 0, 0],
    clasificado: true,
    posicion: 1,
    por_dia: porDia([
      [1700, 2, false],
      [1701, 3, false],
      [1702, 4.5, true],
      [1703, 5, false],
    ]),
    ...extra,
  };
}

function instantaneas({ imputada = true } = {}) {
  return new Map([
    [
      '2026-09',
      {
        temporada: '2026-09',
        ordinal: 2,
        etiqueta: 'Temporada 2 · septiembre 2026',
        estado: 'en curso',
        imputada,
        dias: [1700, 1701, 1702, 1703],
        media_grupo: 4.1,
        clasificacion: [
          fila(ANA, 'Ana'),
          fila(ZOE, 'Zoe', { posicion: 2, media_temporada: 4.0, media_jugada: 4.0, jugados: 4 }),
        ],
        logros: { fondista: ['Ana'], verdugo: ['Zoe'] },
      },
    ],
    [
      '0',
      {
        temporada: '0',
        ordinal: 0,
        etiqueta: 'Temporada 0 · el histórico',
        estado: 'cerrada',
        imputada: false,
        dias: [1, 2, 3, 4, 5, 6],
        media_grupo: 3.9,
        clasificacion: [
          // sin una sola jornada imputada, que es lo que produce Python cuando la temporada no imputa:
          // reutilizar aquí el `por_dia` de la temporada numerada habría probado un dato imposible
          fila(ZOE, 'Zoe', {
            posicion: 1,
            media_temporada: 3.5,
            media_jugada: 3.5,
            jugados: 6,
            dias: 6,
            distribucion: [0, 2, 2, 1, 1, 0, 0],
            por_dia: porDia([
              [1700, 3, false],
              [1701, 3, false],
              [1702, 4, false],
              [1703, 5, false],
              [1704, 2, false],
              [1705, 4, false],
            ]),
          }),
        ],
        logros: {},
      },
    ],
  ]);
}

/** @scenarios ficha-resume-la-temporada-del-jugador */
test('la ficha resume la temporada del jugador', () => {
  const f = ficha(instantaneas(), '2026-09', ANA);

  assert.equal(f.existe, true);
  assert.equal(f.nombre, 'Ana');
  assert.equal(f.posicion, 1);
  assert.equal(f.media_temporada, 3.75);
  assert.equal(f.media_jugada, 3.33);
  assert.equal(f.jugados, 3);
  assert.equal(f.dias, 4);
  assert.equal(f.mejor, 2);
  assert.equal(f.peor, 5);
  assert.equal(f.etiqueta, 'Temporada 2 · septiembre 2026');
});

/** @scenarios la-ficha-desglosa-jornada-a-jornada */
test('el desglose trae una entrada por jornada y distingue las imputadas', () => {
  const f = ficha(instantaneas(), '2026-09', ANA);

  assert.equal(f.por_dia.length, 4, 'una entrada por jornada de la temporada');
  assert.deepEqual(
    f.por_dia.map((d) => d.imputado),
    [false, false, true, false],
  );
  assert.deepEqual(
    f.por_dia.map((d) => d.jornada),
    [1700, 1701, 1702, 1703],
  );
  assert.ok(
    f.por_dia.every((d) => typeof d.fecha === 'string' && d.fecha.length === 10),
    'cada jornada dice su fecha',
  );
});

/** @scenarios la-ficha-dice-lo-que-costo-faltar */
test('la ficha dice cuántas ausencias hay y cuánto le han costado', () => {
  const f = ficha(instantaneas(), '2026-09', ANA);

  assert.equal(f.imputadas, 1);
  // 3,75 de temporada frente a 3,33 jugada: faltar le cuesta 0,42
  assert.equal(f.coste_de_faltar, 0.42);
  assert.equal(f.imputa, true);
});

/** @scenarios la-ficha-dice-lo-que-costo-faltar */
test('en una temporada sin imputación no se inventa un coste', () => {
  const f = ficha(instantaneas(), '0', ZOE);

  assert.equal(f.imputa, false);
  assert.equal(f.imputadas, 0);
  assert.equal(f.coste_de_faltar, null, 'sin imputación no hay coste que comparar');
});

/** @scenarios distribucion-de-intentos-del-jugador */
test('la distribución cuenta por intentos y suma las partidas jugadas', () => {
  const f = ficha(instantaneas(), '2026-09', ANA);

  assert.equal(f.distribucion.length, 7, 'del 1 al fallo');
  assert.equal(
    f.distribucion.reduce((a, b) => a + b, 0),
    f.jugados,
    'la distribución tiene que cuadrar con las partidas jugadas',
  );
  assert.equal(f.distribucion[6], 0, 'el último cajón es el fallo');
});

/** @scenarios palmares-de-todas-las-temporadas */
test('el palmarés trae una línea por temporada jugada, de la más reciente a la más antigua', () => {
  const p = palmares(instantaneas(), ZOE);

  assert.deepEqual(
    p.map((t) => t.temporada),
    ['2026-09', '0'],
    'ordenado por ordinal descendente, con la 0 al final',
  );
  assert.deepEqual(
    p.map((t) => t.posicion),
    [2, 1],
  );
  assert.equal(p[1].etiqueta, 'Temporada 0 · el histórico');
});

/** @scenarios palmares-de-todas-las-temporadas */
test('el palmarés señala la temporada que se está mirando y omite las que no jugó', () => {
  const p = palmares(instantaneas(), ANA, '2026-09');

  assert.deepEqual(
    p.map((t) => t.temporada),
    ['2026-09'],
    'Ana no jugó la temporada 0, así que no sale',
  );
  assert.equal(p[0].actual, true);
});

/** @scenarios medallas-del-jugador-en-la-temporada */
test('la ficha trae las medallas de esa temporada, y dice cuando no hay ninguna', () => {
  const conMedalla = ficha(instantaneas(), '2026-09', ANA);
  const sinMedalla = ficha(instantaneas(), '0', ZOE);

  assert.deepEqual(conMedalla.medallas, ['fondista']);
  assert.deepEqual(sinMedalla.medallas, []);
});

/** @scenarios jugador-que-no-jugo-la-temporada */
test('un jugador sin resultados en la temporada lo dice, y ofrece donde sí jugó', () => {
  const f = ficha(instantaneas(), '0', ANA);

  assert.equal(f.existe, false);
  assert.equal(f.etiqueta, 'Temporada 0 · el histórico', 'sigue diciendo qué temporada se miraba');
  assert.deepEqual(
    f.otras.map((t) => t.temporada),
    ['2026-09'],
    'las temporadas en que sí jugó',
  );
  assert.equal(f.nombre, 'Ana', 'el nombre se recupera de otra temporada para no mostrar el identificador');
});

/** @scenarios jugador-que-no-jugo-la-temporada */
test('un identificador que no existe en ninguna temporada no rompe la ficha', () => {
  const f = ficha(instantaneas(), '2026-09', 'U_NADIE');

  assert.equal(f.existe, false);
  assert.deepEqual(f.otras, []);
  assert.equal(f.nombre, 'U_NADIE', 'sin nombre conocido, el identificador es lo único honesto');
});

/** @scenarios el-marcador-enlaza-a-la-ficha */
test('cada fila del marcador enlaza a la ficha de esa temporada', () => {
  const html = filaDeMarcador(fila(ANA, 'Ana'), '2026-09');

  assert.match(html, /href="\/t\/2026-09\/j\/U_ANA"/);
  assert.match(html, />Ana</);
});

/** @scenarios el-marcador-enlaza-a-la-ficha */
test('la ruta de la ficha se construye con la temporada y el identificador', () => {
  assert.equal(rutaDeFicha('2026-09', ANA), '/t/2026-09/j/U_ANA');
  assert.equal(rutaDeFicha('0', ZOE), '/t/0/j/U_ZOE');
});

/** @scenarios el-marcador-enlaza-a-la-ficha */
test('un nombre con comillas no se cuela en el atributo del enlace', () => {
  const html = filaDeMarcador(fila('U_X', '"><script>alert(1)</script>'), '2026-09');

  assert.ok(!html.includes('<script>'), 'el nombre entra escapado');
});
