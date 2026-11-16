/**
 * La pantalla del proyector del evento, de `pantalla-del-evento` (cambio `feat-frase-del-evento`).
 *
 *     node --test tests/slices/pantalla-del-evento/
 *
 * Sin red: la API del evento se dobla. Participantes sintéticos.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { FalloDelEvento } from '../../../v2/js/evento/api.js';
import { controlDeLaPantalla, vistaDeLaPantalla } from '../../../v2/js/evento/pantalla.js';

const T0 = Date.parse('2026-11-20T10:00:00Z');
const MIN = 60_000;
const DIRECCION = 'wordle.example/2/evento';

function estado({ inicio = T0, ahora = T0 + MIN, soluciones = null, terminado = false, contadores = {} } = {}) {
  return {
    titulo: 'Evento de test',
    ahora: new Date(ahora).toISOString(),
    empieza_en: inicio === null ? null : new Date(inicio).toISOString(),
    intervalo_minutos: 10,
    participantes: 7,
    terminado,
    frases: [1, 2, 3, 4, 5].map((orden) => ({
      orden,
      abre_en: inicio === null ? null : new Date(inicio + (orden - 1) * 10 * MIN).toISOString(),
      jugando: 0, resueltas: 0, sin_resolver: 0, ...(contadores[orden] ?? {}),
      ...(soluciones ? { solucion: soluciones[orden - 1] } : {}),
    })),
  };
}

function apiFalsa({ est = estado(), ...sobre } = {}) {
  const llamadas = [];
  const apunta = (nombre, fn) => async (...args) => { llamadas.push([nombre, ...args]); return fn(...args); };
  return {
    llamadas,
    estado: apunta('estado', () => est),
    empezarEvento: apunta('empezarEvento', () => ({ empieza_en: est.empieza_en })),
    terminarEvento: apunta('terminarEvento', () => ({ terminado_en: est.ahora })),
    ranking: apunta('ranking', () => []),
    ...sobre,
  };
}

async function pantalla(api, ahora = T0 + MIN) {
  const control = controlDeLaPantalla({ api, reloj: () => ahora });
  await control.refrescar();
  return { control, html: vistaDeLaPantalla(control.estado, control.ahora(), DIRECCION) };
}

/** @scenarios antes-de-empezar-se-ve-la-espera */
test('sin empezar se ve la espera con los apuntados, la dirección y el PIN para empezar', async () => {
  const { html } = await pantalla(apiFalsa({ est: estado({ inicio: null }) }));

  assert.match(html, /<strong>7<\/strong> participantes apuntados/);
  assert.match(html, /Entra en <strong>wordle\.example\/2\/evento<\/strong>/);
  assert.match(html, /data-formulario="empezar"[\s\S]*name="pin" type="password"/);
});

/** @scenarios la-cuenta-atras-a-la-siguiente-frase */
test('en curso se ve cuántas frases van y cuánto falta para la siguiente, con la hora del servidor', async () => {
  // El proyector va 5 minutos atrasado: manda el servidor (10:12 → dos frases, la 3 sale en 8:00).
  const { html } = await pantalla(apiFalsa({ est: estado({ ahora: T0 + 12 * MIN }) }), T0 + 7 * MIN);

  assert.match(html, /2 de 5 frases en juego/);
  assert.match(html, /La frase 3 sale en[\s\S]*data-cuenta-atras="\d+">8:00</);
  assert.doesNotMatch(html, /data-formulario="terminar"/, 'no se puede terminar con frases por salir');
});

/** @scenarios los-contadores-no-tienen-nombres */
test('los contadores de cada frase liberada se pintan sin nombres ni tiempos', async () => {
  const api = apiFalsa({ est: estado({ ahora: T0 + 12 * MIN, contadores: { 1: { jugando: 12, resueltas: 30, sin_resolver: 4 } } }) });
  const { html } = await pantalla(api);

  assert.match(html, /Frase 1<\/th>\s*<td><strong>12<\/strong> jugando[\s\S]*<strong>30<\/strong> la han resuelto[\s\S]*<strong>4<\/strong> sin palabras/);
  assert.match(html, /Frase 2<\/th>/);
  assert.doesNotMatch(html, /Frase 3<\/th>/, 'la 3 aún no ha salido');
  assert.ok(!api.llamadas.some(([n]) => n === 'ranking'), 'durante el evento no se pide el ranking');
});

/** @scenarios se-termina-con-el-pin */
test('con todas las frases fuera aparece Terminar, que envía el PIN', async () => {
  const api = apiFalsa({ est: estado({ ahora: T0 + 45 * MIN }) });
  const { control, html } = await pantalla(api, T0 + 45 * MIN);
  assert.match(html, /data-formulario="terminar"[\s\S]*Terminar el evento/);

  await control.terminar('prueba-local');

  assert.deepEqual(api.llamadas.find(([n]) => n === 'terminarEvento'), ['terminarEvento', 'prueba-local']);
});

/** @scenarios se-empieza-con-el-pin, un-pin-incorrecto-no-hace-nada */
test('el botón de empezar envía el PIN escrito y un rechazo se dice sin empezar nada', async () => {
  const buena = apiFalsa({ est: estado({ inicio: null }) });
  const control = controlDeLaPantalla({ api: buena, reloj: () => T0 });
  await control.empezar('prueba-local');
  assert.deepEqual(buena.llamadas.find(([n]) => n === 'empezarEvento'), ['empezarEvento', 'prueba-local']);
  assert.equal(control.estado.aviso, null);

  const mala = apiFalsa({
    est: estado({ inicio: null }),
    empezarEvento: async () => { throw new FalloDelEvento('PIN incorrecto', 'rechazo'); },
  });
  const otro = controlDeLaPantalla({ api: mala, reloj: () => T0 });
  await otro.empezar('mal');

  const html = vistaDeLaPantalla(otro.estado, otro.ahora(), DIRECCION);
  assert.match(html, /El PIN no es correcto/);
  assert.match(html, /name="pin"/, 'sigue esperando el PIN');
});

/** @scenarios al-terminar-se-ven-las-soluciones, el-ranking-sale-al-terminar-el-evento */
test('terminado el evento se pintan el podio, el ranking con frases y tiempo, y las frases', async () => {
  const api = apiFalsa({
    est: estado({ terminado: true, soluciones: ['sol y mar', 'b', 'c', 'd', '¿Quién dijo miedo?'] }),
    ranking: async () => [
      { puesto: 1, nombre: 'Ana', resueltas: 5, tiempo_ms: 1_234_000, frases: [] },
      { puesto: 2, nombre: 'Bea', resueltas: 4, tiempo_ms: 600_000, frases: [] },
    ],
  });
  const { html } = await pantalla(api);

  assert.match(html, /class="pa-podio-1"><span>1º<\/span><strong>Ana<\/strong><em>5 frases · 20:34<\/em>/);
  assert.match(html, /<td class="pa-nombre">Bea<\/td>\s*<td>4<\/td>\s*<td class="pa-total">10:00<\/td>/);
  assert.match(html, /Las frases[\s\S]*¿Quién dijo miedo\?/);
});

/** @scenarios los-nombres-se-escapan-en-la-pantalla */
test('un nombre con HTML se pinta como texto en el ranking', async () => {
  const api = apiFalsa({
    est: estado({ terminado: true }),
    ranking: async () => [{ puesto: 1, nombre: '<b>Ana</b>', resueltas: 1, tiempo_ms: 1, frases: [] }],
  });
  const { html } = await pantalla(api);

  assert.doesNotMatch(html, /<b>Ana/);
  assert.match(html, /&lt;b&gt;Ana/);
});

/** @scenarios la-pantalla-pide-la-contrasena */
test('con contraseña, el proyector solo pide la contraseña y después enseña el evento', async () => {
  const cerrado = { ahora: new Date(T0).toISOString(), con_clave: true, bloqueado: true };
  const api = apiFalsa({ estado: async (_token, clave) => (clave === 'cl4ve' ? estado({ inicio: null }) : cerrado) });
  const control = controlDeLaPantalla({ api, reloj: () => T0 });
  await control.refrescar();

  const puerta = vistaDeLaPantalla(control.estado, control.ahora(), DIRECCION);
  assert.match(puerta, /data-formulario="clave"/);
  assert.doesNotMatch(puerta, /Evento de test|wordle\.example|participantes|name="pin"/);

  await control.desbloquear('cl4ve');
  const abierta = vistaDeLaPantalla(control.estado, control.ahora(), DIRECCION);
  assert.match(abierta, /Evento de test[\s\S]*name="pin"/);
});
