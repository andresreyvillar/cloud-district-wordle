/**
 * La pantalla del admin del evento, de `admin-del-evento` (cambio `feat-palabras-del-evento`).
 *
 *     node --test tests/slices/admin-del-evento/
 *
 * Sin red: la API del evento se dobla. Participantes, grupos y PIN inventados.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { FalloDelEvento } from '../../../v2/js/evento/api.js';
import {
  controlDelAdmin, csvDeGrupos, csvDeParticipantes, exportacion, vistaDelAdmin,
} from '../../../v2/js/evento/admin.js';

const PIN = '1234';

const palabras = (extra = []) => [1, 2].map((orden, i) => ({ orden, jugando: 0, resueltas: 0, falladas: 0, ...(extra[i] ?? {}) }));

const panelActivo = (extra = {}) => ({
  ahora: '2026-11-20T10:00:00Z', titulo: 'Evento de test', activo: true, terminado: false,
  empieza_en: '2026-11-20T09:00:00Z', terminado_en: null, segundos_por_intento: 30,
  participantes: 4, elegidos: 2,
  nombres: [{ nombre: 'Ana', elegido: true }, { nombre: 'Bea', elegido: false }],
  palabras: palabras(), ...extra,
});

const panelTerminado = () => panelActivo({
  activo: false, terminado: true, terminado_en: '2026-11-20T11:00:00Z',
  palabras: palabras().map((p, i) => ({ ...p, palabra: ['casas', 'perro'][i] })),
  jugadores: [
    { puesto: 1, nombre: 'Ana', grupo: 'Rojo', puntos: 5, palabras: [
      { orden: 1, resuelta: true, intentos: 3, tiempo_ms: 61_500, marca_ms: 151_500, puntos: 3 },
      { orden: 2, resuelta: true, intentos: 4, tiempo_ms: 30_000, marca_ms: 150_000, puntos: 2 }] },
    { puesto: 2, nombre: '=Bea, "la jefa"', grupo: 'Azul', puntos: 1, palabras: [
      { orden: 1, resuelta: false, intentos: 6, tiempo_ms: 200_000, marca_ms: null, puntos: 0 },
      { orden: 2, resuelta: true, intentos: 5, tiempo_ms: 40_000, marca_ms: 190_000, puntos: 1 }] },
    { puesto: 3, nombre: 'Cris', grupo: 'Azul', puntos: 0, palabras: [] },
  ],
  grupos: [
    { puesto: 1, grupo: 'Rojo', miembros: 1, jugaron: 1, puntos_totales: 5, puntos: 5.0 },
    { puesto: 2, grupo: 'Azul', miembros: 2, jugaron: 1, puntos_totales: 1, puntos: 0.5 },
  ],
});

function apiFalsa({ panel = panelActivo(), ...sobre } = {}) {
  const llamadas = [];
  const apunta = (nombre, fn) => async (...args) => { llamadas.push([nombre, ...args]); return fn(...args); };
  const conPin = (fn) => (pin, ...resto) => {
    if (pin !== PIN) throw new FalloDelEvento('PIN incorrecto', 'rechazo');
    return fn(...resto);
  };
  return {
    llamadas,
    panel: apunta('panel', conPin(() => panel)),
    activar: apunta('activar', conPin(() => ({ empieza_en: 'ya' }))),
    terminar: apunta('terminar', conPin(() => ({ terminado_en: 'ya' }))),
    liberar: apunta('liberar', conPin((nombre) => ({ nombre }))),
    ...sobre,
  };
}

async function dentro(api) {
  const control = controlDelAdmin({ api });
  await control.entrar(PIN);
  return control;
}

/** @scenarios se-entra-con-el-pin, un-pin-incorrecto-no-hace-nada */
test('sin PIN solo se ve el campo del PIN; uno que no vale se dice y no enseña nada', async () => {
  const control = controlDelAdmin({ api: apiFalsa() });
  assert.match(vistaDelAdmin(control.estado), /data-formulario="pin"[\s\S]*name="pin" type="password"/);

  await control.entrar('0000');

  const html = vistaDelAdmin(control.estado);
  assert.match(html, /PIN incorrecto/);
  assert.doesNotMatch(html, /Evento de test|Activar|Terminar/);
  assert.equal(control.estado.pin, null);
});

/** @scenarios cinco-fallos-bloquean-el-pin-un-minuto */
test('el bloqueo del PIN se enseña tal cual lo dice el servidor', async () => {
  const api = { ...apiFalsa(), panel: async () => { throw new FalloDelEvento('Demasiados intentos: espera unos minutos.', 'rechazo'); } };
  const control = controlDelAdmin({ api });

  await control.entrar(PIN);

  assert.match(vistaDelAdmin(control.estado), /Demasiados intentos: espera unos minutos/);
});

/** @scenarios se-activa-con-el-pin */
test('con el PIN y el evento sin activar se ve Activar, que envía el PIN guardado', async () => {
  const api = apiFalsa({ panel: panelActivo({ activo: false, empieza_en: null }) });
  const control = await dentro(api);
  assert.match(vistaDelAdmin(control.estado), /se activará en[\s\S]*breve[\s\S]*data-accion="activar"/);

  await control.activar();

  assert.deepEqual(api.llamadas.find(([n]) => n === 'activar'), ['activar', PIN]);
});

/** @scenarios los-contadores-no-tienen-nombres, se-termina-con-el-pin */
test('activo, el panel cuenta por palabra sin nombres y ofrece Terminar', async () => {
  const api = apiFalsa({ panel: panelActivo({ palabras: palabras([{ jugando: 12, resueltas: 30, falladas: 4 }]) }) });
  const control = await dentro(api);

  const html = vistaDelAdmin(control.estado);

  assert.match(html, /<strong>2<\/strong> de 4\s+participantes han elegido su nombre/);
  assert.match(html, /Palabra 1<\/th>\s*<td><strong>12<\/strong> jugando[\s\S]*<strong>30<\/strong> resuelta[\s\S]*<strong>4<\/strong> fallada/);
  assert.match(html, /data-accion="terminar"/);
  assert.doesNotMatch(html, /pa-ranking|Grupos/);

  await control.terminar();
  assert.deepEqual(api.llamadas.find(([n]) => n === 'terminar'), ['terminar', PIN]);
});

/** @scenarios se-libera-un-nombre */
test('la lista de nombres elegidos permite liberar uno con el PIN', async () => {
  const api = apiFalsa();
  const control = await dentro(api);

  assert.match(vistaDelAdmin(control.estado), /data-liberar="Ana">Liberar/);
  assert.doesNotMatch(vistaDelAdmin(control.estado), /data-liberar="Bea"/, 'solo los elegidos');

  await control.liberar('Ana');
  assert.deepEqual(api.llamadas.find(([n]) => n === 'liberar'), ['liberar', PIN, 'Ana']);
});

/** @scenarios los-puntos-solo-se-ven-al-terminar, la-puntuacion-del-grupo-es-la-media-de-su-lista */
test('terminado, se ven los grupos con su media, los participantes con cada palabra y las soluciones', async () => {
  const control = await dentro(apiFalsa({ panel: panelTerminado() }));

  const html = vistaDelAdmin(control.estado);

  assert.match(html, /<td class="pa-nombre">Rojo<\/td>\s*<td class="pa-total">5<\/td><td>5<\/td>\s*<td>1\/1<\/td>/);
  assert.match(html, /<td class="pa-nombre">Azul<\/td>\s*<td class="pa-total">0.5<\/td><td>1<\/td>\s*<td>1\/2<\/td>/);
  assert.match(html, /<td class="pa-nombre">Ana<\/td>\s*<td>Rojo<\/td><td class="pa-total">5<\/td>\s*<td>3 · 1:01 <em>3<\/em><\/td>/);
  assert.match(html, /<td class="pa-nada">✕<\/td>/);
  assert.match(html, /Las palabras[\s\S]*CASAS[\s\S]*PERRO/);
  assert.doesNotMatch(html, /data-accion="terminar"/);
});

/** @scenarios se-exportan-los-puntos */
test('la exportación trae grupos y participantes con todo el detalle, y los CSV se abren sin fórmulas', async () => {
  const datos = exportacion(panelTerminado(), 'evento-2026-11-20');

  assert.equal(datos.evento, 'evento-2026-11-20');
  assert.equal(datos.segundos_por_intento, 30);
  assert.deepEqual(datos.grupos[1], { puesto: 2, grupo: 'Azul', puntos: 0.5, puntos_totales: 1, miembros: 2, jugaron: 1 });
  assert.equal(datos.participantes[0].palabras[0].marca_ms, 151_500);

  assert.equal(csvDeGrupos(datos), 'puesto,grupo,puntos,puntos_totales,miembros,jugaron\n1,Rojo,5,5,1,1\n2,Azul,0.5,1,2,1\n');
  const filas = csvDeParticipantes(datos).trim().split('\n');
  assert.equal(filas[0], 'puesto,nombre,grupo,puntos,p1_intentos,p1_segundos,p1_puntos,p2_intentos,p2_segundos,p2_puntos');
  assert.equal(filas[1], '1,Ana,Rojo,5,3,61.5,3,4,30.0,2');
  assert.equal(filas[2], `2,"'=Bea, ""la jefa""",Azul,1,X,200.0,0,5,40.0,1`, 'escapado y sin fórmula');
  assert.equal(filas[3], '3,Cris,Azul,0,,,0,,,0');
  const conTab = csvDeGrupos({ grupos: [{ puesto: 1, grupo: '\t=1+1', puntos: 0, puntos_totales: 0, miembros: 1, jugaron: 0 }] });
  assert.equal(conTab.split('\n')[1], "1,'\t=1+1,0,0,1,0", 'un tabulador delante tampoco abre una fórmula');
});

/** @scenarios los-nombres-se-escapan-en-la-pantalla */
test('un nombre o un grupo con HTML se pinta como texto', async () => {
  const panel = panelTerminado();
  panel.jugadores[0].nombre = '<b>Ana</b>';
  panel.grupos[0].grupo = '<i>Rojo</i>';
  const control = await dentro(apiFalsa({ panel }));

  const html = vistaDelAdmin(control.estado);

  assert.doesNotMatch(html, /<b>Ana|<i>Rojo/);
  assert.match(html, /&lt;b&gt;Ana/);
});
