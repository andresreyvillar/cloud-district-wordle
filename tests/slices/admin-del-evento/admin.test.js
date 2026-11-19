/**
 * El dashboard del evento, de `admin-del-evento` (cambios `feat-palabras-del-evento`, `feat-admin-en-directo` y
 * `feat-admin-dashboard`).
 *
 *     node --test tests/slices/admin-del-evento/
 *
 * Sin red: la API del evento se dobla. Participantes, grupos y palabras inventados.
 */

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

import { FalloDelEvento } from '../../../v2/js/evento/api.js';
import {
  controlDelAdmin, controlDePalabras, csvDeGrupos, csvDeParticipantes, cuantoFalta, exportacion, textoParaCompartir,
  vistaDelAdmin, vistaDePalabras,
} from '../../../v2/js/evento/admin.js';

const palabras = (extra = []) => [1, 2].map((orden, i) => ({ orden, jugando: 0, resueltas: 0, falladas: 0, ...(extra[i] ?? {}) }));

// De 10:00 a 16:00 de Madrid (UTC+1 en noviembre).
const HORARIO = { empieza_en: '2026-11-20T09:00:00Z', terminado_en: '2026-11-20T15:00:00Z' };

const panelActivo = (extra = {}) => ({
  ahora: '2026-11-20T10:00:00Z', titulo: 'Evento de test', antes: false, activo: true, terminado: false, ...HORARIO,
  segundos_por_intento: 30, participantes: 4, elegidos: 2,
  palabras: palabras(),
  // En directo: Ana juega su segunda palabra desde hace 1:30, Dani ha terminado las dos, Eli no ha empezado y Bea no
  // ha entrado.
  jugadores: [
    { puesto: 1, nombre: 'Ana', grupo: 'Rojo', puntos: 15, f1: 25, elegido: true, empezadas: 2, terminadas: 1,
      resueltas: 1, tiempo_ms: 61_000, jugando_desde: '2026-11-20T09:58:30Z', palabras: [] },
    { puesto: 2, nombre: 'Dani', grupo: 'Azul', puntos: 12.5, f1: 18, elegido: true, empezadas: 2, terminadas: 2,
      resueltas: 1, tiempo_ms: 400_000, jugando_desde: null, palabras: [] },
    { puesto: 3, nombre: 'Bea', grupo: 'Azul', puntos: 0, f1: 0, elegido: false, empezadas: 0, terminadas: 0,
      resueltas: 0, tiempo_ms: 0, jugando_desde: null, palabras: [] },
    { puesto: 3, nombre: 'Eli', grupo: 'Rojo', puntos: 0, f1: 0, elegido: true, empezadas: 0, terminadas: 0,
      resueltas: 0, tiempo_ms: 0, jugando_desde: null, palabras: [] },
  ],
  grupos: [
    { puesto: 1, grupo: 'Rojo', miembros: 2, jugaron: 1, puntos_totales: 15, puntos: 7.5 },
    { puesto: 2, grupo: 'Azul', miembros: 2, jugaron: 1, puntos_totales: 12.5, puntos: 6.25 },
  ],
  grupos_f1: [
    { puesto: 1, grupo: 'Rojo', puntos: 25, personas: [{ nombre: 'Ana', puesto: 1, puntos: 25 }] },
    { puesto: 2, grupo: 'Azul', puntos: 18, personas: [{ nombre: 'Dani', puesto: 2, puntos: 18 }] },
  ],
  ...extra,
});

const panelAntes = () => panelActivo({
  ahora: '2026-11-20T06:47:00Z', antes: true, activo: false, elegidos: 0,
  palabras: palabras().map((p, i) => ({ ...p, palabra: ['casas', 'perro'][i] })),
});

const panelTerminado = () => panelActivo({
  ahora: '2026-11-20T15:30:00Z', activo: false, terminado: true,
  palabras: palabras().map((p, i) => ({ ...p, palabra: ['casas', 'perro'][i] })),
  jugadores: [
    { puesto: 1, nombre: 'Ana', grupo: 'Rojo', puntos: 27.5, f1: 25, elegido: true, palabras: [
      { orden: 1, resuelta: true, intentos: 3, tiempo_ms: 61_500, marca_ms: 151_500, puntos: 15 },
      { orden: 2, resuelta: true, intentos: 4, tiempo_ms: 30_000, marca_ms: 150_000, puntos: 12.5 }] },
    { puesto: 2, nombre: '=Bea, "la jefa"', grupo: 'Azul', puntos: 10, f1: 18, elegido: true, palabras: [
      { orden: 1, resuelta: false, intentos: 6, tiempo_ms: 200_000, marca_ms: null, puntos: 0 },
      { orden: 2, resuelta: true, intentos: 5, tiempo_ms: 40_000, marca_ms: 190_000, puntos: 10 }] },
    { puesto: 3, nombre: 'Cris', grupo: 'Azul', puntos: 0, f1: 0, elegido: false, palabras: [] },
  ],
  grupos: [
    { puesto: 1, grupo: 'Rojo', miembros: 1, jugaron: 1, puntos_totales: 27.5, puntos: 27.5 },
    { puesto: 2, grupo: 'Azul', miembros: 2, jugaron: 1, puntos_totales: 10, puntos: 5 },
  ],
  grupos_f1: [
    { puesto: 1, grupo: 'Rojo', puntos: 25, personas: [{ nombre: 'Ana', puesto: 1, puntos: 25 }] },
    { puesto: 2, grupo: 'Azul', puntos: 18, personas: [{ nombre: '=Bea, "la jefa"', puesto: 2, puntos: 18 }] },
  ],
});

/** Una API falsa que apunta las llamadas. Sin PIN: el dashboard no lo pide. */
function apiFalsa({ panel = panelActivo(), ...sobre } = {}) {
  const llamadas = [];
  const apunta = (nombre, fn) => async (...args) => { llamadas.push([nombre, ...args]); return fn(...args); };
  return {
    llamadas,
    tablero: apunta('tablero', () => panel),
    echar: apunta('echar', (nombre) => ({ nombre })),
    cambiarPalabra: apunta('cambiarPalabra', (orden, palabra) => ({ orden, palabra })),
    ...sobre,
  };
}

async function abierto(api) {
  const control = controlDelAdmin({ api });
  await control.refrescar();
  return control;
}

const vista = async (api) => vistaDelAdmin((await abierto(api)).estado);

// ── Sin PIN, a su hora ───────────────────────────────────────────────────────────────────────────────────────

/** @scenarios el-panel-se-ve-sin-pin, el-evento-empieza-y-termina-a-su-hora */
test('el dashboard se abre sin contraseña y, antes de empezar, dice cuánto falta sin enseñar las palabras', async () => {
  const api = apiFalsa({ panel: { ...panelAntes(), palabras: palabras() } });

  const html = await vista(api);

  assert.deepEqual(api.llamadas, [['tablero']], 'sin PIN');
  assert.doesNotMatch(html, /type="password"/, 'el dashboard no pide contraseña');
  assert.match(html, /Empieza en 2 h 13 min · de 10:00 a 16:00/);
  assert.doesNotMatch(html, /name="palabra"|CASAS|PERRO/, 'el dashboard no las enseña');
  assert.doesNotMatch(html, /data-accion="(activar|terminar)"/, 'empieza y termina solo');
});

/** @scenarios el-evento-empieza-y-termina-a-su-hora */
test('en juego dice cuánto falta para terminar; terminado, que ha terminado', async () => {
  assert.match(await vista(apiFalsa()), /En juego · termina en 5 h 0 min · de 10:00 a 16:00/);
  assert.match(await vista(apiFalsa({ panel: panelTerminado() })), /class="pa-estado">Terminado</);
  assert.equal(cuantoFalta(45_000), '45 s');
  assert.equal(cuantoFalta(13 * 60_000 + 5_000), '13 min');
});

/** @scenarios el-panel-se-ve-sin-pin */
test('mientras se juega, el dashboard no enseña ninguna palabra', async () => {
  assert.doesNotMatch(await vista(apiFalsa()), /name="palabra"|pa-soluciones|CASAS|PERRO/);
});

// ── Las palabras ──────────────────────────────────────────────────────────────────────────────────────────

const ESTADO_PALABRAS = { ahora: '2026-11-20T06:47:00Z', titulo: 'Evento de test', empieza_en: HORARIO.empieza_en,
  antes: true, tiene_pin: false };
const PALABRAS = { ahora: '2026-11-20T06:47:00Z', titulo: 'Evento de test', empieza_en: HORARIO.empieza_en,
  palabras: [{ orden: 1, palabra: 'casas' }, { orden: 2, palabra: 'perro' }] };

/** Una API falsa de las palabras: el PIN que vale es 4321 una vez creado. */
function apiDePalabras({ tienePin = false, ...sobre } = {}) {
  const llamadas = [];
  let pin = tienePin ? '4321' : null;
  const apunta = (nombre, fn) => async (...args) => { llamadas.push([nombre, ...args]); return fn(...args); };
  return {
    llamadas,
    estadoDeLasPalabras: apunta('estado', () => ({ ...ESTADO_PALABRAS, tiene_pin: pin !== null })),
    crearPinDePalabras: apunta('crearPin', (nuevo) => { pin = nuevo; return { ok: true }; }),
    verPalabras: apunta('ver', (dado) => {
      if (dado !== pin) throw new FalloDelEvento('PIN incorrecto', 'rechazo');
      return PALABRAS;
    }),
    guardarPalabra: apunta('guardar', (dado, orden, palabra) => ({ orden, palabra })),
    ...sobre,
  };
}

async function enLasPalabras(api) {
  const control = controlDePalabras({ api });
  await control.refrescar();
  return control;
}

/** @scenarios las-palabras-tienen-su-propio-pin */
test('antes de empezar, el dashboard tiene un botón para revisar las palabras, sin enseñarlas', async () => {
  const html = await vista(apiFalsa({ panel: panelAntes() }));

  assert.match(html, /<a class="ev-boton" href="evento\/palabras">Revisar las palabras<\/a>/);
  assert.doesNotMatch(await vista(apiFalsa()), /Revisar las palabras/, 'en juego, no');
});

/** @scenarios las-palabras-tienen-su-propio-pin */
test('la primera vez se crea un PIN de cuatro cifras, escrito dos veces igual, y con él se ven las palabras', async () => {
  const api = apiDePalabras();
  const control = await enLasPalabras(api);
  assert.match(vistaDePalabras(control.estado), /data-formulario="crear-pin"[\s\S]*name="repetido"/);
  assert.doesNotMatch(vistaDePalabras(control.estado), /CASAS/);

  await control.crearPin('12', '12');
  assert.match(vistaDePalabras(control.estado), /cuatro cifras/);
  await control.crearPin('4321', '4320');
  assert.match(vistaDePalabras(control.estado), /no coinciden/);
  assert.ok(!api.llamadas.some(([n]) => n === 'crearPin'), 'lo que no vale no se envía');

  await control.crearPin('4321', '4321');

  assert.deepEqual(api.llamadas.find(([n]) => n === 'crearPin'), ['crearPin', '4321']);
  assert.match(vistaDePalabras(control.estado), /name="palabra" value="CASAS"[\s\S]*name="palabra" value="PERRO"/);
});

/** @scenarios las-palabras-tienen-su-propio-pin */
test('con el PIN ya creado se pide para entrar; uno que no vale no enseña nada', async () => {
  const control = await enLasPalabras(apiDePalabras({ tienePin: true }));
  assert.match(vistaDePalabras(control.estado), /data-formulario="pin"/);
  assert.doesNotMatch(vistaDePalabras(control.estado), /crear-pin/);

  await control.entrar('0000');
  assert.match(vistaDePalabras(control.estado), /PIN incorrecto/);
  assert.doesNotMatch(vistaDePalabras(control.estado), /CASAS/);

  await control.entrar('4321');
  assert.match(vistaDePalabras(control.estado), /value="CASAS"/);
});

/** @scenarios se-cambian-las-palabras-antes-de-empezar */
test('con el PIN se cambia una palabra; si el servidor dice que no, se dice por qué', async () => {
  const api = apiDePalabras({ tienePin: true });
  const control = await enLasPalabras(api);
  await control.entrar('4321');

  await control.cambiarPalabra(2, 'gozne');
  assert.deepEqual(api.llamadas.find(([n]) => n === 'guardar'), ['guardar', '4321', 2, 'gozne']);
  assert.match(vistaDePalabras(control.estado), /Palabra 2 guardada/);

  const otro = await enLasPalabras(apiDePalabras({ tienePin: true, guardarPalabra: async () => {
    throw new FalloDelEvento('Esa palabra no está en el diccionario del juego.', 'rechazo');
  } }));
  await otro.entrar('4321');
  await otro.cambiarPalabra(1, 'zzzzz');
  assert.match(vistaDePalabras(otro.estado), /Esa palabra no está en el diccionario del juego/);
});

/** @scenarios se-cambian-las-palabras-antes-de-empezar */
test('empezado el evento, la página de las palabras solo dice que ya no se ven', async () => {
  const control = await enLasPalabras(apiDePalabras({ estadoDeLasPalabras: async () => ({ ...ESTADO_PALABRAS, antes: false }) }));

  const html = vistaDePalabras(control.estado);

  assert.match(html, /ya ha empezado/);
  assert.doesNotMatch(html, /name="palabra"|name="pin"/);
});

// ── En directo ────────────────────────────────────────────────────────────────────────────────────────────

/** @scenarios el-admin-sigue-a-cada-participante */
test('en juego, cuenta por palabra y sigue a cada participante que ha entrado, con sus puntos F1', async () => {
  const html = await vista(apiFalsa({ panel: panelActivo({ palabras: palabras([{ jugando: 12, resueltas: 30, falladas: 4 }]) }) }));

  assert.match(html, /<strong>2<\/strong> de 4\s+participantes han entrado/);
  assert.match(html, /Palabra 1<\/th>\s*<td><strong>12<\/strong> jugando[\s\S]*<strong>30<\/strong> resuelta[\s\S]*<strong>4<\/strong> fallada/);
  assert.match(html, /<td class="pa-nombre">Ana<\/td><td>Rojo<\/td><td class="pa-total">15<\/td><td>25<\/td><td>1\/2<\/td><td>1:01<\/td><td>Jugando la 2\/2 · 1:30<\/td>/);
  assert.match(html, /<td class="pa-nombre">Dani<\/td>[\s\S]*?<td class="pa-total">12,5<\/td><td>18<\/td><td>1\/2<\/td><td>6:40<\/td><td>Ha terminado<\/td>/);
  assert.match(html, /<td class="pa-nombre">Eli<\/td>[\s\S]*?<td>Sin empezar<\/td>/);
  assert.doesNotMatch(html, /<td class="pa-nombre">Bea</, 'quien no ha entrado no tiene fila');
});

/** @scenarios el-ranking-se-ve-en-directo */
test('en juego se ven el puesto de cada uno, el ranking de grupos por la media y la F1, como provisionales', async () => {
  const html = await vista(apiFalsa());

  assert.match(html, /<td class="pa-puesto">1<\/td><td class="pa-nombre">Ana<\/td>/);
  assert.match(html, /Grupos · media de la lista[\s\S]*<td class="pa-nombre">Rojo<\/td>\s*<td class="pa-total">7,5<\/td>/);
  assert.match(html, /Grupos · F1/);
  assert.match(html, /[Pp]rovisional/);
});

/** @scenarios los-diez-primeros-suman-f1-a-su-grupo */
test('la tabla F1 enseña cada grupo con sus puntos y quién los ha sumado', async () => {
  const html = await vista(apiFalsa());

  assert.match(html, /<td class="pa-nombre">Rojo<\/td><td class="pa-total">25<\/td><td class="pa-quien"><span>Ana <em>25<\/em><\/span><\/td>/);
  assert.match(html, /<td class="pa-nombre">Azul<\/td><td class="pa-total">18<\/td><td class="pa-quien"><span>Dani <em>18<\/em><\/span><\/td>/);
  assert.match(html, /25, 18, 15, 12, 10, 8, 6, 4, 2 y 1/);
});

/** @scenarios se-libera-un-nombre */
test('en juego, cada participante que ha entrado tiene un botón para echarlo, sin PIN', async () => {
  const api = apiFalsa();
  const control = await abierto(api);

  assert.match(vistaDelAdmin(control.estado), /data-liberar="Ana">Echar/);
  assert.doesNotMatch(vistaDelAdmin(control.estado), /data-liberar="Bea"/, 'solo quien ha entrado');

  await control.echar('Ana');
  assert.deepEqual(api.llamadas.find(([n]) => n === 'echar'), ['echar', 'Ana']);
  assert.doesNotMatch(await vista(apiFalsa({ panel: panelTerminado() })), /data-liberar/, 'terminado, ya no se echa a nadie');
});

// ── Al terminar ───────────────────────────────────────────────────────────────────────────────────────────

/** @scenarios las-soluciones-solo-se-ven-al-terminar, la-puntuacion-del-grupo-es-la-media-de-su-lista */
test('terminado, se ven los grupos con su media, cada palabra de cada participante y las soluciones', async () => {
  const html = await vista(apiFalsa({ panel: panelTerminado() }));

  assert.match(html, /<td class="pa-nombre">Rojo<\/td>\s*<td class="pa-total">27,5<\/td><td>27,5<\/td>\s*<td>1\/1<\/td>/);
  assert.match(html, /<td class="pa-nombre">Azul<\/td>\s*<td class="pa-total">5<\/td><td>10<\/td>\s*<td>1\/2<\/td>/);
  assert.match(html, /<td class="pa-nombre">Ana<\/td>\s*<td>Rojo<\/td><td class="pa-total">27,5<\/td>\s*<td>3 · 1:01 <em>15<\/em><\/td>/);
  assert.match(html, /<td class="pa-nada">✕<\/td>/);
  assert.match(html, /Las palabras[\s\S]*CASAS[\s\S]*PERRO/);
});

/** @scenarios se-exportan-los-puntos */
test('la exportación trae grupos (con F1) y participantes con todo el detalle, y los CSV se abren sin fórmulas', () => {
  const datos = exportacion(panelTerminado(), 'evento-2026-11-20');

  assert.equal(datos.evento, 'evento-2026-11-20');
  assert.equal(datos.segundos_por_intento, 30);
  assert.deepEqual(datos.grupos[1], { puesto: 2, grupo: 'Azul', puntos: 5, puntos_totales: 10, miembros: 2, jugaron: 1, puntos_f1: 18 });
  assert.deepEqual(datos.grupos_f1[0].personas, [{ nombre: 'Ana', puesto: 1, puntos: 25 }]);
  assert.equal(datos.participantes[0].palabras[0].marca_ms, 151_500);

  assert.equal(csvDeGrupos(datos), 'puesto,grupo,puntos,puntos_totales,miembros,jugaron,puntos_f1\n1,Rojo,27.5,27.5,1,1,25\n2,Azul,5,10,2,1,18\n');
  const filas = csvDeParticipantes(datos).trim().split('\n');
  assert.equal(filas[0], 'puesto,nombre,grupo,puntos,f1,p1_intentos,p1_segundos,p1_puntos,p2_intentos,p2_segundos,p2_puntos');
  assert.equal(filas[1], '1,Ana,Rojo,27.5,25,3,61.5,15,4,30.0,12.5');
  assert.equal(filas[2], `2,"'=Bea, ""la jefa""",Azul,10,18,X,200.0,0,5,40.0,10`, 'escapado y sin fórmula');
  assert.equal(filas[3], '3,Cris,Azul,0,0,,,0,,,0');
  const conTab = csvDeGrupos({ grupos: [{ puesto: 1, grupo: '\t=1+1', puntos: 0, puntos_totales: 0, miembros: 1, jugaron: 0 }] });
  assert.equal(conTab.split('\n')[1], "1,'\t=1+1,0,0,1,0,0", 'un tabulador delante tampoco abre una fórmula');
});

/** @scenarios se-comparten-los-resultados-en-texto */
test('terminado, el texto para compartir trae la F1 con quién sumó, los grupos por su media y el podio', () => {
  assert.equal(textoParaCompartir(panelTerminado()), [
    '🏆 Evento de test — resultados',
    '',
    'GRUPOS · F1',
    '🥇 Rojo · 25 puntos (Ana 25)',
    '🥈 Azul · 18 puntos (=Bea, "la jefa" 18)',
    '',
    'GRUPOS · MEDIA DE LA LISTA',
    '🥇 Rojo · 27,5 puntos',
    '🥈 Azul · 5 puntos',
    '',
    'PODIO',
    '🥇 Ana (Rojo) · 27,5 puntos',
    '🥈 =Bea, "la jefa" (Azul) · 10 puntos',
  ].join('\n'));
});

/** @scenarios se-comparten-los-resultados-en-texto */
test('terminado, el texto se ofrece para copiar, para WhatsApp y para email', async () => {
  const texto = textoParaCompartir(panelTerminado());

  const html = await vista(apiFalsa({ panel: panelTerminado() }));

  assert.match(html, /data-compartir="copiar"/);
  const enlace = (href) => href.replaceAll('&', '&amp;');
  assert.ok(html.includes(`href="${enlace(`https://wa.me/?text=${encodeURIComponent(texto)}`)}"`), 'WhatsApp');
  assert.ok(html.includes(`href="${enlace(`mailto:?subject=${encodeURIComponent('Evento de test — resultados')}&body=${encodeURIComponent(texto)}`)}"`), 'email');
  assert.match(html, /<textarea[^>]*readonly[^>]*>🏆 Evento de test/);
  assert.doesNotMatch(await vista(apiFalsa()), /data-compartir/, 'en juego no');
});

// ── Aspecto y texto ───────────────────────────────────────────────────────────────────────────────────────

/** @scenarios el-panel-tiene-el-estilo-del-cartel */
test('el dashboard tiene el estilo del cartel: cuadrícula, título grande en minúscula y la fecha en monoespaciada', async () => {
  const html = await vista(apiFalsa());
  assert.match(html, /<div class="pa pa-cartel">/);
  assert.match(html, /<p class="pa-fecha">2026\/<br>nov\/<br>20<\/p>/);
  assert.match(html, /<h1 class="pa-titulo">evento de test\.<\/h1>/);

  const hoja = readFileSync(new URL('../../../v2/css/evento.css', import.meta.url), 'utf8');
  assert.match(hoja, /body\.modo-evento:has\(\.pa-cartel\) \{[^}]*linear-gradient\(var\(--ev-cuadricula\) 1px/);
  assert.match(hoja, /\.modo-evento \.pa-cartel \.pa-titulo \{[^}]*font-weight: 400/);
  assert.match(hoja, /\.pa-fecha \{[^}]*font-family: var\(--ev-fuente-etiqueta\)/);
});

/** @scenarios los-nombres-se-escapan-en-la-pantalla */
test('un nombre o un grupo con HTML se pinta como texto', async () => {
  const panel = panelTerminado();
  panel.jugadores[0].nombre = '<b>Ana</b>';
  panel.grupos[0].grupo = '<i>Rojo</i>';
  panel.grupos_f1[0].personas[0].nombre = '<b>Ana</b>';
  const html = await vista(apiFalsa({ panel }));
  const enDirecto = await vista(apiFalsa({ panel: panelActivo({
    jugadores: [{ ...panelActivo().jugadores[0], nombre: '<b>Ana</b>' }] }) }));

  assert.doesNotMatch(enDirecto, /<b>Ana/);
  assert.match(enDirecto, /data-liberar="&lt;b&gt;Ana&lt;\/b&gt;"/);
  assert.doesNotMatch(html, /<b>Ana|<i>Rojo/);
  assert.match(html, /&lt;b&gt;Ana/);
});
