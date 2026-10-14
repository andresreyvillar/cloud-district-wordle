/**
 * El apartado «Debate de reglas» de Info, de `debate-de-reglas` (pack `feat-debate-de-reglas`).
 *
 *     node --test tests/slices/debate-de-reglas/
 *
 * Sin red: la API del debate se dobla. Los jugadores son sintéticos: el repositorio es público.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { recuento } from '../../../v2/js/domain/debate.js';
import { controlDelDebate, pintarDebate, vistaDebate } from '../../../v2/js/ui/debate.js';
import { pintarInfo } from '../../../v2/js/ui/info.js';

const JUGADORES = [
  { jugador: 'U-ANA', nombre: 'Ana' },
  { jugador: 'U-BEA', nombre: 'Bea' },
  { jugador: 'U-CRIS', nombre: 'Cris' },
];

const VOTACION = {
  id: 'anti-spoilers',
  titulo: '¿Qué hacemos con los spoilers?',
  descripcion: 'Una pista en un comentario ayuda a quien juega después.',
  opciones: [
    { id: 'anular', texto: 'Anular la jornada y sancionar a quien dio la pista' },
    { id: 'nada', texto: 'No hacer nada' },
  ],
  abierta: true,
};

const VOTOS = [
  { votacion: 'anti-spoilers', votante: 'U-ANA', opcion: 'anular' },
  { votacion: 'anti-spoilers', votante: 'U-BEA', opcion: 'anular' },
  { votacion: 'anti-spoilers', votante: 'U-CRIS', opcion: 'nada' },
];

const PROPUESTAS = [
  { id: 1, autor: 'U-BEA', titulo: 'Premio al más madrugador', texto: 'Una medalla para quien publique primero.', created_at: '2026-10-14T09:00:00Z' },
];

const DATOS = { votaciones: [VOTACION], votos: VOTOS, propuestas: PROPUESTAS };

/** @scenarios la-votacion-abierta-se-ve-con-su-recuento */
test('el recuento cuenta los votos de cada opción y dice quién la votó', () => {
  const [anular, nada] = recuento(VOTACION, VOTOS);

  assert.equal(anular.total, 2);
  assert.deepEqual(anular.votantes, ['U-ANA', 'U-BEA']);
  assert.equal(nada.total, 1);
});

/** @scenarios la-votacion-abierta-se-ve-con-su-recuento */
test('la votación abierta se pinta con su pregunta, sus opciones, sus votos y los nombres', () => {
  const html = vistaDebate(DATOS, JUGADORES, null);

  assert.match(html, /¿Qué hacemos con los spoilers\?/);
  assert.match(html, /Anular la jornada/);
  assert.match(html, /No hacer nada/);
  assert.match(html, /2 votos/);
  assert.match(html, /1 voto\b/);
  assert.match(html, /Ana, Bea/, 'se ve quién votó cada opción');
  assert.equal((html.match(/data-opcion=/g) ?? []).length, 2, 'un botón por opción');
});

/** @scenarios el-voto-se-puede-cambiar */
test('quien ya votó ve marcada su opción', () => {
  const html = vistaDebate(DATOS, JUGADORES, 'U-CRIS');

  assert.match(html, /data-opcion="nada"[^>]*aria-pressed="true"/);
  assert.match(html, /data-opcion="anular"[^>]*aria-pressed="false"/);
});

/** @scenarios el-voto-se-puede-cambiar */
test('un voto nuevo de la misma persona sustituye al anterior en el recuento', () => {
  const votos = [...VOTOS, { votacion: 'anti-spoilers', votante: 'U-CRIS', opcion: 'anular' }];

  const [anular, nada] = recuento(VOTACION, votos);

  assert.equal(anular.total, 3);
  assert.equal(nada.total, 0);
});

/** @scenarios una-votacion-cerrada-no-admite-votos */
test('una votación cerrada enseña su resultado sin botones', () => {
  const html = vistaDebate({ ...DATOS, votaciones: [{ ...VOTACION, abierta: false }] }, JUGADORES, 'U-ANA');

  assert.doesNotMatch(html, /data-opcion=/);
  assert.match(html, /cerrada/i);
  assert.match(html, /2 votos/);
});

/** @scenarios sin-nombre-no-se-vota */
test('sin nombre elegido el voto no se envía y se pide elegir quién eres', async () => {
  const enviados = [];
  const control = controlDelDebate({ api: { votar: async (v) => enviados.push(v) } });

  const resultado = await control.votar(null, 'anti-spoilers', 'anular');

  assert.equal(resultado.estado, 'sin-jugador');
  assert.match(resultado.texto, /elige/i);
  assert.equal(enviados.length, 0);
});

/** @scenarios se-vota-eligiendo-tu-nombre */
test('con nombre elegido el voto se envía con quién vota y qué', async () => {
  const enviados = [];
  const control = controlDelDebate({ api: { votar: async (v) => { enviados.push(v); return { opcion: v.opcion }; } } });

  const resultado = await control.votar('U-ANA', 'anti-spoilers', 'anular');

  assert.equal(resultado.estado, 'votado');
  assert.deepEqual(enviados, [{ votacion: 'anti-spoilers', votante: 'U-ANA', opcion: 'anular' }]);
});

/** @scenarios una-propuesta-queda-pendiente */
test('una propuesta se envía y se avisa de que queda pendiente de aprobar', async () => {
  const enviadas = [];
  const control = controlDelDebate({ api: { proponer: async (p) => { enviadas.push(p); return { estado: 'pendiente' }; } } });

  const resultado = await control.proponer('U-BEA', '  Sin spoilers  ', ' Nada de pistas antes de las 18:00. ');

  assert.equal(resultado.estado, 'pendiente');
  assert.match(resultado.texto, /aprueb/i);
  assert.deepEqual(enviadas, [{ autor: 'U-BEA', titulo: 'Sin spoilers', texto: 'Nada de pistas antes de las 18:00.' }]);
});

/** @scenarios una-propuesta-queda-pendiente, sin-nombre-no-se-vota */
test('una propuesta sin nombre o sin texto no se envía', async () => {
  const enviadas = [];
  const control = controlDelDebate({ api: { proponer: async (p) => enviadas.push(p) } });

  assert.equal((await control.proponer(null, 'Título', 'Una explicación')).estado, 'sin-jugador');
  assert.equal((await control.proponer('U-ANA', '  ', 'Una explicación')).estado, 'incompleta');
  assert.equal((await control.proponer('U-ANA', 'Título', '')).estado, 'incompleta');
  assert.equal(enviadas.length, 0);
});

/** @scenarios la-base-de-datos-valida-lo-que-entra */
test('si la base de datos rechaza el voto o la propuesta, se dice y no se da por hecho', async () => {
  const caida = async () => { throw new Error('Supabase: votación cerrada'); };
  const control = controlDelDebate({ api: { votar: caida, proponer: caida } });

  const voto = await control.votar('U-ANA', 'anti-spoilers', 'anular');
  const propuesta = await control.proponer('U-ANA', 'Título', 'Una explicación');

  assert.equal(voto.estado, 'error');
  assert.equal(propuesta.estado, 'error');
});

/** @scenarios solo-se-ven-las-propuestas-aprobadas */
test('las propuestas que llegan se pintan con su autor y hay formulario para proponer', () => {
  const html = vistaDebate(DATOS, JUGADORES, null);

  assert.match(html, /Premio al más madrugador/);
  assert.match(html, /Una medalla para quien publique primero\./);
  assert.match(html, /Bea/);
  assert.match(html, /<form class="propuesta-nueva"/);
});

/** @scenarios el-texto-de-los-jugadores-se-escapa */
test('el HTML de una propuesta o de un nombre se pinta como texto', () => {
  const datos = {
    ...DATOS,
    propuestas: [{ id: 2, autor: 'U-MAL', titulo: '<img src=x onerror=alert(1)>', texto: '<script>x()</script>', created_at: '2026-10-14T09:00:00Z' }],
  };
  const jugadores = [...JUGADORES, { jugador: 'U-MAL', nombre: '<b>Mal</b>' }];

  const html = vistaDebate(datos, jugadores, null);

  assert.doesNotMatch(html, /<img src=x/);
  assert.doesNotMatch(html, /<script>/);
  assert.doesNotMatch(html, /<b>Mal<\/b>/);
  assert.match(html, /&lt;script&gt;/);
});

/** @scenarios si-el-debate-no-carga-info-sigue */
test('si la lectura falla, el apartado lo dice', async () => {
  const contenedor = { innerHTML: '', ownerDocument: null };

  await pintarDebate(contenedor, [], { leer: async () => { throw new Error('Supabase caído'); } });

  assert.match(contenedor.innerHTML, /No se ha podido cargar/);
});

/** @scenarios si-el-debate-no-carga-info-sigue */
test('Info deja su sitio al debate después de las reglas vigentes', () => {
  const contenedor = { innerHTML: '' };
  pintarInfo(contenedor, []);

  const html = contenedor.innerHTML;
  assert.match(html, /<h2>Debate de reglas<\/h2>/);
  assert.match(html, /id="debate-de-reglas"/);
  assert.ok(html.indexOf('Reglas vigentes') < html.indexOf('Debate de reglas'));
});
