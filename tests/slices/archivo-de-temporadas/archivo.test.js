/**
 * Escenarios de `archivo-de-temporadas` (Fase 2 — TDD rojo).
 *
 *     node --test tests/slices/archivo-de-temporadas/
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { archivo, medallero } from '../../../v2/js/data/archivo.js';

function temporada(id, { ordinal, etiqueta, estado, tabla = [], logros = {}, dias = 20 }) {
  return [
    id,
    {
      temporada: id,
      ordinal,
      etiqueta,
      estado,
      imputada: id !== '0',
      dias: Array.from({ length: dias }, (_, i) => 1600 + i),
      resultados: tabla.length * dias,
      jugadores: tabla.map((f) => f.jugador),
      media_grupo: 4.1,
      clasificacion: tabla,
      logros,
    },
  ];
}

function fila(jugador, nombre, posicion, media) {
  return {
    jugador,
    nombre,
    posicion,
    media_temporada: media,
    media_jugada: media,
    jugados: 18,
    dias: 20,
    clasificado: true,
  };
}

function instantaneas() {
  return new Map([
    temporada('2026-09', {
      ordinal: 2,
      etiqueta: 'Temporada 2 · septiembre 2026',
      estado: 'en curso',
      tabla: [fila('U_ANA', 'Ana', 1, 3.7), fila('U_ZOE', 'Zoe', 2, 3.9)],
      logros: { fondista: ['Ana'], verdugo: ['Ana', 'Zoe'] },
    }),
    temporada('2026-08', {
      ordinal: 1,
      etiqueta: 'Temporada 1 · agosto 2026',
      estado: 'cerrada',
      tabla: [fila('U_ZOE', 'Zoe', 1, 3.5), fila('U_ANA', 'Ana', 2, 4.0)],
      logros: { impecable: ['Zoe'] },
    }),
    temporada('0', {
      ordinal: 0,
      etiqueta: 'Temporada 0 · el histórico',
      estado: 'cerrada',
      dias: 181,
      tabla: [fila('U_ANA', 'Ana', 1, 3.56)],
      logros: { fondista: ['Ana'] },
    }),
  ]);
}

/** @scenarios el-archivo-lista-las-temporadas-de-la-mas-reciente-a-la-mas-antigua */
test('el archivo ordena por número de orden descendente, con la 0 al final', () => {
  const lista = archivo(instantaneas());

  assert.deepEqual(
    lista.map((t) => t.temporada),
    ['2026-09', '2026-08', '0'],
  );
});

/** @scenarios cada-temporada-cerrada-muestra-su-campeon */
test('una temporada cerrada muestra su campeón y sus totales', () => {
  const agosto = archivo(instantaneas()).find((t) => t.temporada === '2026-08');

  assert.equal(agosto.cerrada, true);
  assert.equal(agosto.campeon.nombre, 'Zoe');
  assert.equal(agosto.campeon.media_temporada, 3.5);
  assert.equal(agosto.campeon.jugador, 'U_ZOE');
  assert.equal(agosto.jornadas, 20);
  assert.equal(agosto.jugadores, 2);
  assert.equal(agosto.resultados, 40);
});

/** @scenarios la-temporada-en-curso-no-tiene-campeon-todavia */
test('la temporada en curso no tiene campeón: tiene quien va ganando', () => {
  const septiembre = archivo(instantaneas()).find((t) => t.temporada === '2026-09');

  assert.equal(septiembre.cerrada, false);
  assert.equal(septiembre.campeon, null, 'una temporada abierta no ha coronado a nadie');
  assert.equal(septiembre.lider.nombre, 'Ana');
});

/** @scenarios el-medallero-acumula-todas-las-temporadas */
test('el medallero suma las medallas de todas las temporadas y las temporadas ganadas', () => {
  const tabla = medallero(instantaneas());

  // Ana: fondista + verdugo en septiembre, fondista en la 0 = 3. Zoe: verdugo en septiembre + impecable = 2
  assert.deepEqual(
    tabla.map((f) => [f.nombre, f.medallas]),
    [
      ['Ana', 3],
      ['Zoe', 2],
    ],
  );
  // temporadas ganadas: la 0 la ganó Ana; agosto, Zoe. Septiembre está abierta y no cuenta
  assert.equal(tabla.find((f) => f.nombre === 'Ana').temporadas_ganadas, 1);
  assert.equal(tabla.find((f) => f.nombre === 'Zoe').temporadas_ganadas, 1);
});

/** @scenarios el-medallero-acumula-todas-las-temporadas */
test('el medallero desglosa por tipo de medalla', () => {
  const ana = medallero(instantaneas()).find((f) => f.nombre === 'Ana');

  assert.deepEqual(ana.por_clave, { fondista: 2, verdugo: 1 });
});

/** @scenarios la-temporada-cero-se-marca-como-bloque-historico */
test('la temporada 0 va marcada como bloque histórico con otras reglas', () => {
  const lista = archivo(instantaneas());
  const cero = lista.find((t) => t.temporada === '0');
  const mes = lista.find((t) => t.temporada === '2026-08');

  assert.equal(cero.historica, true);
  assert.equal(cero.imputada, false);
  assert.equal(mes.historica, false, 'un mes normal no es bloque histórico');
});

/** @scenarios cada-temporada-enlaza-a-su-marcador */
test('cada entrada trae la ruta de su marcador', () => {
  const lista = archivo(instantaneas());

  assert.deepEqual(
    lista.map((t) => t.ruta),
    ['/t/2026-09', '/t/2026-08', '/t/0'],
  );
});

/** @scenarios sin-temporadas-materializadas-lo-dice */
test('sin instantáneas el archivo sale vacío, no roto', () => {
  assert.deepEqual(archivo(new Map()), []);
  assert.deepEqual(medallero(new Map()), []);
});

/** @scenarios cada-temporada-cerrada-muestra-su-campeon */
test('una temporada vacía aparece sin campeón en lugar de desaparecer', () => {
  const vacia = new Map([
    temporada('2026-10', {
      ordinal: 3,
      etiqueta: 'Temporada 3 · octubre 2026',
      estado: 'cerrada',
      dias: 0,
      tabla: [],
    }),
  ]);

  const lista = archivo(vacia);

  assert.equal(lista.length, 1, 'un mes sin jornadas válidas sigue siendo parte de la historia');
  assert.equal(lista[0].jornadas, 0);
  assert.equal(lista[0].campeon, null);
});
