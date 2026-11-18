/**
 * La vista del participante del evento, de `palabras-del-evento` (cambio `feat-palabras-del-evento`).
 *
 *     node --test tests/slices/palabras-del-evento/
 *
 * Sin red: la API del evento se dobla. Participantes y palabras inventados: el repositorio es público.
 */

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

import { FalloDelEvento, apiDelEvento, esRechazo } from '../../../v2/js/evento/api.js';
import {
  buscarNombres, coloresDelTeclado, normaliza, puntoDelJuego, tokenAleatorio,
} from '../../../v2/js/evento/dominio.js';
import {
  comoSeJuega, controlDelEvento, listaDeNombres, tablero, teclado, vistaDelEvento,
} from '../../../v2/js/evento/jugador.js';
import { esDelEvento, resolver, rutaDe, VISTAS } from '../../../v2/js/router.js';
import { navegacion } from '../../../v2/js/ui/shell.js';

const T0 = Date.parse('2026-11-20T10:00:00Z');
const PALABRAS = new Set(['sacos', 'salas', 'tunde', 'casas', 'pique']);
const NOMBRES = [
  { nombre: 'Ana López', libre: true }, { nombre: 'Bea', libre: false }, { nombre: 'Íñigo Pérez', libre: true },
];

const estadoActivo = (extra = {}) => ({
  ahora: new Date(T0).toISOString(), activo: true, terminado: false, titulo: 'Evento de test', total: 3,
  soluciones: null, ...extra,
});
const ESPERA = { ahora: new Date(T0).toISOString(), activo: false, terminado: false };

const ronda = (orden, extra = {}) => ({
  orden, empezada_en: new Date(T0).toISOString(), terminada_en: null, resuelta: false, tiempo_ms: null, intentos: [],
  ...extra,
});
const resuelta = (orden, intentos = [{ palabra: 'casas', colores: 'GGGGG' }], tiempo_ms = 61_000) => ronda(orden, {
  terminada_en: new Date(T0 + tiempo_ms).toISOString(), resuelta: true, tiempo_ms, intentos,
});

/** Una API falsa que apunta las llamadas. `rondas` es lo que el servidor tiene jugado. */
function apiFalsa({ est = estadoActivo(), rondas = new Map(), elegidos = new Map(), ...sobre } = {}) {
  const llamadas = [];
  const apunta = (nombre, fn) => async (...args) => { llamadas.push([nombre, ...args]); return fn(...args); };
  return {
    llamadas,
    evento: 'prueba',
    estado: apunta('estado', () => est),
    nombres: apunta('nombres', () => NOMBRES),
    elegir: apunta('elegir', (nombre, token) => {
      const encontrado = NOMBRES.find((n) => normaliza(n.nombre) === normaliza(nombre));
      if (!encontrado) throw new FalloDelEvento('ese nombre no está en la lista', 'rechazo');
      elegidos.set(token, encontrado.nombre);
      return { nombre: encontrado.nombre };
    }),
    miJuego: apunta('miJuego', (token) => {
      if (!elegidos.has(token)) throw new FalloDelEvento('no has elegido nombre', 'rechazo');
      return { nombre: elegidos.get(token), rondas: [...rondas.values()] };
    }),
    empezar: apunta('empezar', (_t, orden) => {
      if (!rondas.has(orden)) rondas.set(orden, ronda(orden));
      return rondas.get(orden);
    }),
    probar: apunta('probar', (_t, orden, palabra) => {
      if (!PALABRAS.has(palabra)) throw new FalloDelEvento('la palabra no está en la lista', 'rechazo');
      const colores = palabra === 'casas' ? 'GGGGG' : 'YG.GG';
      const r = rondas.get(orden);
      const intentos = [...r.intentos, { palabra, colores }];
      const fin = colores === 'GGGGG' || intentos.length === 6;
      rondas.set(orden, { ...r, intentos, resuelta: colores === 'GGGGG', terminada_en: fin ? new Date(T0 + 30_000).toISOString() : null,
        tiempo_ms: fin ? 30_000 : null });
      return rondas.get(orden);
    }),
    ...sobre,
  };
}

function almacenFalso(inicial = {}) {
  const datos = new Map(Object.entries(inicial));
  return { datos, leer: (k) => datos.get(k) ?? null, guardar: (k, v) => datos.set(k, v) };
}

function control(api, { almacen = almacenFalso(), ahora = T0 + 5_000 } = {}) {
  return controlDelEvento({ api, almacen, reloj: () => ahora, generarToken: () => 'tk-ana' });
}

async function dentro(api, opciones) {
  const c = control(api, opciones);
  await c.arrancar();
  await c.entrar('Ana López');
  return c;
}

const vista = (c) => vistaDelEvento(c.estado, c.ahora());
const escribir = (c, palabra) => [...palabra].forEach((letra) => c.teclear(letra));

// ── La ruta y el aspecto ─────────────────────────────────────────────────────────────────────────────────

/** @scenarios la-ruta-del-evento-no-sale-en-el-menu */
test('la ruta /evento y /evento/admin resuelven a sus vistas y ninguna pestaña lleva a ellas', () => {
  assert.equal(resolver('/evento').vista, VISTAS.EVENTO);
  assert.equal(resolver('/evento/admin').vista, VISTAS.ADMIN_DEL_EVENTO);
  assert.equal(resolver('/evento/pantalla').vista, VISTAS.DESCONOCIDA);
  assert.ok(esDelEvento(resolver('/evento')) && esDelEvento(resolver('/evento/admin')));
  assert.equal(rutaDe({ vista: VISTAS.ADMIN_DEL_EVENTO }), '/evento/admin');
  for (const destino of [{ vista: VISTAS.TEMPORADA }, { vista: VISTAS.EVENTO }]) {
    assert.doesNotMatch(navegacion(destino), /evento/);
  }
  const app = readFileSync(new URL('../../../v2/js/app.js', import.meta.url), 'utf8');
  const arranque = app.slice(app.indexOf('export async function arrancar()'));
  assert.ok(arranque.indexOf('arrancarEvento(') < arranque.indexOf('cargarResultados()'));
  assert.match(app, /querySelector\('\.cabecera'\)\?\.remove\(\)/);
});

/** @scenarios el-evento-tiene-su-propia-apariencia */
test('la hoja del evento usa negro y #FAF9F4, Helvetica y los colores del Wordle, y la web no la usa', () => {
  const hoja = readFileSync(new URL('../../../v2/css/evento.css', import.meta.url), 'utf8');
  const raiz = hoja.slice(hoja.indexOf(':root {'), hoja.indexOf('}', hoja.indexOf(':root {')));
  assert.match(raiz, /--ev-fondo: #FAF9F4;/);
  assert.match(raiz, /--ev-tinta: #000000;/);
  assert.match(raiz, /--ev-fuente: "Helvetica Neue", Helvetica,/);
  assert.doesNotMatch(hoja, /Host Grotesk|Host\+Grotesk/, 'no queda rastro de la fuente anterior');
  for (const variable of ['--ev-verde', '--ev-amarillo', '--ev-gris', '--ev-fuente-etiqueta']) {
    assert.match(raiz, new RegExp(`${variable}:`), variable);
  }
  assert.match(hoja, /\.ev-celda\.verde \{ background: var\(--ev-verde\)/);
  const web = readFileSync(new URL('../../../v2/css/styles.css', import.meta.url), 'utf8');
  assert.doesNotMatch(web, /--ev-|\.ev-|\.pa-/, 'la web de estadísticas no cambia con el tema');
  const index = readFileSync(new URL('../../../v2/index.html', import.meta.url), 'utf8');
  assert.doesNotMatch(index, /evento\.css/, 'la hoja solo se carga en las rutas del evento');
});

// ── Antes de activar ─────────────────────────────────────────────────────────────────────────────────────

/** @scenarios antes-de-activar-solo-se-ve-la-espera */
test('antes de activar solo se ve el aviso, sin título, reglas ni nombres, y no se pide la lista', async () => {
  // Aunque el servidor mandara de más, la espera no lo enseña.
  const api = apiFalsa({ est: { ...ESPERA, titulo: 'Evento de test', total: 3 } });
  const c = control(api);
  await c.arrancar();

  const html = vista(c);

  assert.match(html, /El evento se activará en breve/);
  assert.doesNotMatch(html, /Evento de test|Cómo se juega|nombre|Palabra|intentos/i);
  assert.ok(!api.llamadas.some(([n]) => n === 'nombres'));
});

/** @scenarios la-espera-pasa-sola-al-juego */
test('al activarse, el siguiente sondeo trae la lista de nombres y la vista pasa a pedir el nombre', async () => {
  let est = ESPERA;
  const api = apiFalsa({ estado: async () => est });
  const c = control(api);
  await c.arrancar();
  assert.match(vista(c), /se activará en breve/);

  est = estadoActivo();
  await c.refrescar();

  assert.match(vista(c), /¿Quién eres\?[\s\S]*name="nombre"/);
  assert.deepEqual(c.estado.nombres, NOMBRES);
});

// ── El nombre ────────────────────────────────────────────────────────────────────────────────────────────

/** @scenarios se-elige-el-nombre-de-la-lista */
test('el buscador filtra sin mayúsculas ni tildes, con los libres primero, y el desplegable enseña todos', () => {
  assert.deepEqual(buscarNombres(NOMBRES, 'inigo').map((n) => n.nombre), ['Íñigo Pérez']);
  assert.deepEqual(buscarNombres(NOMBRES, ' LÓP').map((n) => n.nombre), ['Ana López']);
  assert.deepEqual(buscarNombres(NOMBRES, '').map((n) => n.nombre), ['Ana López', 'Íñigo Pérez', 'Bea']);

  const lista = listaDeNombres({ desplegado: true, nombres: NOMBRES, buscado: '' });
  assert.match(lista, /data-nombre="Ana López">Ana López</);
  assert.match(lista, /<button type="button" role="option" disabled>Bea <em>ya elegido<\/em>/);
  assert.equal(listaDeNombres({ desplegado: false, nombres: NOMBRES, buscado: '' }), '');
});

/** @scenarios se-elige-el-nombre-de-la-lista */
test('se busca, se toca un nombre de la lista y se entra con él', async () => {
  const api = apiFalsa();
  const almacen = almacenFalso();
  const c = control(api, { almacen });
  await c.arrancar();

  c.buscar('íñi');
  c.marcar('Íñigo Pérez');
  await c.entrar();

  assert.equal(c.estado.nombre, 'Íñigo Pérez');
  assert.deepEqual(api.llamadas.find(([n]) => n === 'elegir'), ['elegir', 'Íñigo Pérez', 'tk-ana']);
  assert.equal(almacen.datos.get('evento:token:prueba'), 'tk-ana');
  assert.match(vista(c), /Íñigo Pérez[\s\S]*Empezar/);
});

/** @scenarios un-nombre-que-no-esta-en-la-lista-no-entra */
test('un nombre que no está en la lista no se envía y despliega la lista', async () => {
  const api = apiFalsa();
  const c = control(api);
  await c.arrancar();

  await c.entrar('Zoe');

  assert.equal(c.estado.nombre, null);
  assert.match(vista(c), /no está en la lista/);
  assert.ok(c.estado.desplegado);
  assert.ok(!api.llamadas.some(([n]) => n === 'elegir'));
});

/** @scenarios un-nombre-elegido-no-lo-coge-otro-movil */
test('si el servidor dice que el nombre ya está elegido, se avisa y se recarga la lista', async () => {
  const api = apiFalsa({
    elegir: async () => { throw new FalloDelEvento('ese nombre ya está elegido: si eres tú, avisa a la organización', 'rechazo'); },
  });
  const c = control(api);
  await c.arrancar();

  await c.entrar('Ana López');

  assert.equal(c.estado.nombre, null);
  assert.match(vista(c), /ya está elegido: si eres tú, avisa a la organización/);
  assert.equal(api.llamadas.filter(([n]) => n === 'nombres').length, 2);
});

/** @scenarios el-mismo-movil-recupera-su-nombre */
test('al recargar, el token guardado recupera el nombre y lo jugado sin pedir el nombre', async () => {
  const rondas = new Map([[1, resuelta(1)]]);
  const api = apiFalsa({ rondas, elegidos: new Map([['tk-guardado', 'Ana López']]) });
  const c = control(api, { almacen: almacenFalso({ 'evento:token:prueba': 'tk-guardado' }) });

  await c.arrancar();

  assert.equal(c.estado.nombre, 'Ana López');
  assert.match(vista(c), /Siguiente palabra 2\/3/);
  assert.ok(!api.llamadas.some(([n]) => n === 'elegir'));
});

/** @scenarios el-mismo-movil-recupera-su-nombre */
test('el token se guarda antes de pedir el nombre: si la respuesta se pierde, al recargar se recupera', async () => {
  const elegidos = new Map();
  const base = apiFalsa({ elegidos });
  const perdida = { ...base, elegir: async (...args) => { await base.elegir(...args); throw new FalloDelEvento('sin red', 'red'); } };
  const almacen = almacenFalso();
  const c = control(perdida, { almacen });
  await c.arrancar();
  await c.entrar('Ana López');
  assert.equal(c.estado.nombre, null);

  const recargado = control(base, { almacen });
  await recargado.arrancar();

  assert.equal(recargado.estado.nombre, 'Ana López');
});

/** @scenarios el-mismo-movil-recupera-su-nombre */
test('un fallo pasajero de la base de datos al recargar no tira el token', async () => {
  const api = apiFalsa({ miJuego: async () => { throw new FalloDelEvento('canceling statement due to statement timeout', 'rechazo'); } });
  const c = control(api, { almacen: almacenFalso({ 'evento:token:prueba': 'tk-guardado' }) });

  await c.arrancar();

  assert.equal(c.estado.token, 'tk-guardado');
  assert.match(vista(c), /Recuperando tu partida/);
});

/** @scenarios el-mismo-movil-recupera-su-nombre */
test('sin red al recargar, el token se conserva y se reintenta en vez de pedir otro nombre', async () => {
  const api = apiFalsa({ miJuego: async () => { throw new FalloDelEvento('sin red', 'red'); } });
  const c = control(api, { almacen: almacenFalso({ 'evento:token:prueba': 'tk-guardado' }) });

  await c.arrancar();

  assert.equal(c.estado.token, 'tk-guardado');
  assert.match(vista(c), /Recuperando tu partida/);
});

// ── Jugar ────────────────────────────────────────────────────────────────────────────────────────────────

/** @scenarios se-explica-como-se-juega */
test('antes de la primera palabra se explican las reglas del Wordle y los tres colores', async () => {
  const c = await dentro(apiFalsa());

  const html = vista(c);

  assert.match(html, /3 palabras, 6 intentos cada una/);
  assert.match(html, /palabra de 5 letras<\/strong> en <strong>6 intentos/);
  assert.match(html, /ev-celda verde">A<\/span><span>La letra está en la palabra y en la posición correcta/);
  assert.match(html, /ev-celda amarilla">A<\/span><span>La letra está en la palabra, pero en otra posición/);
  assert.match(html, /ev-celda gris">A<\/span><span>La letra no aparece en la palabra/);
  assert.match(comoSeJuega(), /PLUMA[\s\S]*NUBIA/);
});

/** @scenarios el-cronometro-de-cada-palabra-empieza-al-pulsar */
test('el tablero y el cronómetro salen al pulsar Empezar, con la hora de inicio del servidor', async () => {
  const api = apiFalsa({ est: estadoActivo({ ahora: new Date(T0 + 83_000).toISOString() }) });
  const c = await dentro(api, { ahora: T0 + 83_000 });
  assert.doesNotMatch(vista(c), /data-cronometro/);

  await c.empezar();

  assert.deepEqual(api.llamadas.find(([n]) => n === 'empezar'), ['empezar', 'tk-ana', 1]);
  const html = vista(c);
  assert.match(html, /Palabra 1\/3<\/span><strong class="ev-reloj" data-cronometro="\d+">1:23</);
  assert.equal((html.match(/class="ev-fila/g) ?? []).length, 6, 'seis filas');
});

/** @scenarios el-reloj-no-se-pausa */
test('al volver más tarde el cronómetro sigue desde la hora de inicio, sin descontar lo que estuvo cerrada', async () => {
  const rondas = new Map([[1, ronda(1)]]);
  const api = apiFalsa({ rondas, elegidos: new Map([['tk', 'Ana López']]),
    est: estadoActivo({ ahora: new Date(T0 + 10 * 60_000).toISOString() }) });
  const c = control(api, { almacen: almacenFalso({ 'evento:token:prueba': 'tk' }), ahora: T0 + 10 * 60_000 });

  await c.arrancar();

  assert.match(vista(c), /data-cronometro="\d+">10:00</);
});

/** @scenarios cada-palabra-tiene-seis-intentos-de-cinco-letras */
test('un intento incompleto no se envía y no pasa de cinco letras', async () => {
  const api = apiFalsa();
  const c = await dentro(api);
  await c.empezar();

  escribir(c, 'sac');
  await c.enviar();
  assert.match(vista(c), /Faltan 2 letras/);
  escribir(c, 'osxyz');
  assert.equal(c.estado.escrito.join(''), 'sacos');
  assert.ok(!api.llamadas.some(([n]) => n === 'probar'));
});

/** @scenarios una-palabra-que-no-esta-en-la-lista-no-gasta-intento */
test('una palabra que no está en la lista la rechaza el servidor: se avisa, se queda escrita y no gasta intento', async () => {
  const api = apiFalsa();
  const c = await dentro(api);
  await c.empezar();

  escribir(c, 'zzzzz');
  await c.enviar();

  assert.match(vista(c), /no está en la lista/);
  assert.equal(c.estado.escrito.join(''), 'zzzzz');
  assert.equal(c.estado.rondas.get(1).intentos.length, 0);
  assert.equal(c.estado.nombre, 'Ana López', 'un rechazo de la palabra no saca al participante');
});

/** @scenarios los-colores-son-los-del-wordle, una-letra-repetida-se-colorea-como-en-el-wordle */
test('el tablero pinta los colores del servidor y el teclado no baja de color', async () => {
  const api = apiFalsa();
  const c = await dentro(api);
  await c.empezar();
  escribir(c, 'salas');
  await c.enviar();

  assert.deepEqual(api.llamadas.find(([n]) => n === 'probar'), ['probar', 'tk-ana', 1, 'salas', 1]);
  const html = vista(c);
  assert.match(html, /ev-celda llena amarilla">S<\/span><span class="ev-celda llena verde">A<\/span><span class="ev-celda llena gris">L</);

  const colores = coloresDelTeclado([{ palabra: 'sacos', colores: 'YGY.G' }, { palabra: 'salas', colores: 'Y..G.' }]);
  assert.equal(colores.get('s'), 'G', 'verde no baja a amarilla');
  assert.equal(colores.get('a'), 'G', 'verde no baja a gris');
  assert.equal(colores.get('c'), 'Y');
  assert.equal(colores.get('o'), '.');
  assert.match(teclado([{ palabra: 'sacos', colores: 'YGY.G' }]), /class="ev-tecla verde" data-tecla="s"/);
  assert.match(teclado([]), /data-tecla="ñ"/);
});

/** @scenarios se-gana-con-cinco-verdes, al-terminar-una-palabra-se-pasa-a-la-siguiente */
test('al resolver se ve el resultado y Siguiente palabra 2/3, que empieza la 2 con su propio cronómetro', async () => {
  const api = apiFalsa();
  const c = await dentro(api);
  await c.empezar();
  escribir(c, 'casas');
  await c.enviar();

  const html = vista(c);
  assert.match(html, /¡Resuelta en 1 intento y 0:30!/);
  assert.match(html, /data-accion="empezar">Siguiente palabra 2\/3</);
  assert.doesNotMatch(html, /data-tecla/, 'sin teclado');

  await c.empezar();
  assert.deepEqual(api.llamadas.filter(([n]) => n === 'empezar').at(-1), ['empezar', 'tk-ana', 2]);
  assert.match(vista(c), /Palabra 2\/3/);
});

/** @scenarios las-palabras-se-juegan-en-orden */
test('el punto del juego sale de las rondas: empezar, jugando, entre palabras o fin', () => {
  assert.deepEqual(puntoDelJuego(new Map(), 3), { tipo: 'empezar', orden: 1 });
  assert.deepEqual(puntoDelJuego(new Map([[1, ronda(1)]]), 3), { tipo: 'jugando', orden: 1 });
  assert.deepEqual(puntoDelJuego(new Map([[2, resuelta(2)], [1, resuelta(1)]]), 3), { tipo: 'entre', orden: 2 });
  assert.deepEqual(puntoDelJuego(new Map([[1, resuelta(1)], [2, resuelta(2)], [3, resuelta(3)]]), 3), { tipo: 'fin', orden: 3 });
});

/** @scenarios la-solucion-no-viaja-al-movil */
test('al fallar la sexta no se enseña la palabra y se puede seguir con la siguiente', async () => {
  const api = apiFalsa();
  const c = await dentro(api);
  await c.empezar();
  for (let i = 0; i < 6; i += 1) {
    escribir(c, 'salas');
    await c.enviar();
  }

  const html = vista(c);
  assert.match(html, /No la has adivinado/);
  assert.match(html, /se desvela al terminar el evento/);
  assert.doesNotMatch(html, /CASAS|casas/);
  assert.match(html, /Siguiente palabra 2\/3/);
});

/** @scenarios al-terminar-una-palabra-se-pasa-a-la-siguiente */
test('tras la última palabra se ve el resumen de todas, sin puntos', async () => {
  const rondas = new Map([[1, resuelta(1)], [2, ronda(2, { terminada_en: new Date(T0).toISOString(), tiempo_ms: 90_000 })],
    [3, resuelta(3, [{ palabra: 'salas', colores: 'YG.GG' }, { palabra: 'casas', colores: 'GGGGG' }], 125_000)]]);
  const api = apiFalsa({ rondas, elegidos: new Map([['tk', 'Ana López']]) });
  const c = control(api, { almacen: almacenFalso({ 'evento:token:prueba': 'tk' }) });
  await c.arrancar();

  const html = vista(c);

  assert.match(html, /¡Has terminado las 3 palabras!/);
  assert.match(html, /Palabra 1<\/span><span>1 intento · 1:01/);
  assert.match(html, /Palabra 2<\/span><span>Sin resolver/);
  assert.match(html, /Palabra 3<\/span><span>2 intentos · 2:05/);
  assert.doesNotMatch(html, /Siguiente palabra|puntos:/i);
});

// ── Al terminar ──────────────────────────────────────────────────────────────────────────────────────────

/** @scenarios al-terminar-el-evento-no-se-admiten-palabras */
test('con el evento terminado no se teclea, no se envía y no se empieza nada', async () => {
  const est = estadoActivo();
  const api = apiFalsa({ est });
  const c = await dentro(api);
  await c.empezar();
  Object.assign(est, { activo: false, terminado: true });
  await c.refrescar();

  escribir(c, 'casas');
  await c.enviar();
  await c.empezar();

  assert.equal(c.estado.escrito.length, 0);
  assert.ok(!api.llamadas.some(([n]) => n === 'probar'));
  assert.equal(api.llamadas.filter(([n]) => n === 'empezar').length, 1);
  assert.doesNotMatch(vista(c), /data-tecla/);
});

const FIN = estadoActivo({ activo: false, terminado: true, total: 2,
  soluciones: [{ orden: 1, palabra: 'casas' }, { orden: 2, palabra: 'perro' }] });

/** @scenarios al-terminar-el-evento-se-ven-las-soluciones */
test('terminado el evento, cada uno ve sus palabras en su orden, con lo que hizo en cada una', async () => {
  const rondas = new Map([[1, resuelta(1)]]);
  const api = apiFalsa({
    rondas, est: FIN,
    miJuego: async () => ({ nombre: 'Ana López', rondas: [...rondas.values()], palabras: ['perro', 'casas'] }),
  });
  const c = control(api, { almacen: almacenFalso({ 'evento:token:prueba': 'tk' }) });
  await c.arrancar();

  const html = vista(c);

  assert.match(html, /El evento ha terminado/);
  assert.match(html, /Palabra 1 · PERRO<\/span><span>1 intento · 1:01/);
  assert.match(html, /Palabra 2 · CASAS<\/span><span>Sin jugar/);
  assert.doesNotMatch(html, /Las palabras/, 'la lista del evento va en otro orden que el suyo: no se enseña');
});

/** @scenarios al-terminar-el-evento-se-ven-las-soluciones */
test('si el evento termina con la página abierta, se piden sus palabras al servidor', async () => {
  const est = estadoActivo({ total: 2 });
  let fin = false;
  const api = apiFalsa({
    est,
    miJuego: async () => ({ nombre: 'Ana López', rondas: [], ...(fin ? { palabras: ['perro', 'casas'] } : {}) }),
  });
  const c = await dentro(api);
  assert.doesNotMatch(vista(c), /PERRO/);

  Object.assign(est, FIN);
  fin = true;
  await c.refrescar();

  assert.match(vista(c), /Palabra 1 · PERRO<\/span><span>Sin jugar/);
});

/** @scenarios al-terminar-el-evento-se-ven-las-soluciones */
test('terminado el evento, quien no eligió nombre ve las palabras del evento', () => {
  const html = vistaDelEvento({ estado: FIN, nombre: null, rondas: new Map(), escrito: [] }, T0);

  assert.match(html, /Las palabras[\s\S]*CASAS[\s\S]*PERRO/);
});

/** @scenarios el-tiempo-cuenta-y-se-dice */
test('al ir a empezar, en las reglas y con el reloj en marcha se dice que el tiempo cuenta', async () => {
  const c = await dentro(apiFalsa({ est: estadoActivo({ segundos_por_intento: 45 }) }));

  const inicio = vista(c);
  assert.match(inicio, /<strong>El tiempo cuenta\.<\/strong>/);
  assert.match(inicio, /Cada intento suma además 45 segundos/);
  assert.match(inicio, /Cuanto antes, más puntos/);
  assert.match(comoSeJuega(45), /<ol>\s*<li><strong>El tiempo cuenta<\/strong>/);
  assert.match(comoSeJuega(45), /cada intento suma además 45 segundos/);

  await c.empezar();
  assert.match(vista(c), /class="ev-cuenta">⏱ El tiempo cuenta</);
});

/** @scenarios el-tiempo-cuenta-y-se-dice */
test('sin los segundos del servidor, se dice igual que el tiempo cuenta, sin inventar la cifra', async () => {
  const c = await dentro(apiFalsa());

  const inicio = vista(c);

  assert.match(inicio, /<strong>El tiempo cuenta\.<\/strong>/);
  assert.doesNotMatch(inicio, /\d+ segundos/);
});

/** @scenarios el-texto-de-los-participantes-se-escapa */
test('un nombre con HTML se pinta como texto en la lista y en la cabecera', async () => {
  const lista = listaDeNombres({ desplegado: true, nombres: [{ nombre: '<b>Ana</b>', libre: true }], buscado: '' });
  assert.doesNotMatch(lista, /<b>Ana/);
  assert.match(lista, /&lt;b&gt;Ana/);

  const html = vistaDelEvento({ estado: estadoActivo(), nombre: '<img src=x>', rondas: new Map(), escrito: [] }, T0);
  assert.doesNotMatch(html, /<img/);
});

/** @scenarios el-mismo-movil-recupera-su-nombre */
test('si el admin libera el nombre entre palabras, al pulsar Siguiente el móvil vuelve a pedir el nombre', async () => {
  const rondas = new Map([[1, resuelta(1)]]);
  const elegidos = new Map([['tk', 'Ana López']]);
  const api = apiFalsa({ rondas, elegidos });
  const c = control(api, { almacen: almacenFalso({ 'evento:token:prueba': 'tk' }) });
  await c.arrancar();
  assert.match(vista(c), /Siguiente palabra 2\/3/);

  elegidos.delete('tk');
  api.empezar = async () => { throw new FalloDelEvento('no has elegido nombre', 'rechazo'); };
  await c.empezar();

  assert.equal(c.estado.nombre, null);
  assert.match(vista(c), /¿Quién eres\?/);
});

// ── La red ───────────────────────────────────────────────────────────────────────────────────────────────

/** @scenarios si-el-servidor-no-responde-el-intento-no-se-pierde */
test('sin red, la palabra se queda escrita y el reenvío lleva el mismo número de intento', async () => {
  let caida = true;
  const base = apiFalsa();
  const api = { ...base, probar: async (...args) => {
    if (caida) throw new FalloDelEvento('sin red', 'red');
    return base.probar(...args);
  } };
  const c = await dentro(api);
  await c.empezar();
  escribir(c, 'salas');

  await c.enviar();
  assert.equal(c.estado.escrito.join(''), 'salas');
  assert.match(vista(c), /Tu palabra sigue escrita/);

  caida = false;
  await c.enviar();
  assert.deepEqual(base.llamadas.find(([n]) => n === 'probar'), ['probar', 'tk-ana', 1, 'salas', 1]);
  assert.equal(c.estado.escrito.length, 0);
});

/** @scenarios si-el-servidor-no-responde-el-intento-no-se-pierde */
test('la API corta las peticiones colgadas y distingue rechazo de red; el PIN que no vale es un rechazo', async () => {
  const colgado = apiDelEvento({ rpc: () => new Promise(() => {}) }, 'prueba', 20);
  await assert.rejects(colgado.estado(), (e) => e instanceof FalloDelEvento && e.tipo === 'red');

  const rechaza = apiDelEvento({ rpc: async () => ({ data: null, error: { code: '22023', message: 'no' } }) }, 'prueba');
  await assert.rejects(rechaza.estado(), (e) => e.tipo === 'rechazo' && e.message === 'no');

  const pin = apiDelEvento({ rpc: async () => ({ data: { error: 'PIN incorrecto' }, error: null }) }, 'prueba');
  await assert.rejects(pin.panel('0'), (e) => e.tipo === 'rechazo' && e.message === 'PIN incorrecto');

  assert.ok(esRechazo('22023') && !esRechazo('PGRST202') && !esRechazo(''));
  assert.match(tokenAleatorio(() => new Uint8Array(16)), /^00000000-0000-4000-8000-000000000000$/);
});

/** @scenarios si-el-servidor-no-responde-el-intento-no-se-pierde */
test('la API manda a cada función sus parámetros con nombre', async () => {
  const llamadas = [];
  const api = apiDelEvento({ rpc: async (f, a) => { llamadas.push([f, a]); return { data: {}, error: null }; } }, 'ev');
  await api.estado();
  await api.nombres();
  await api.elegir('Ana', 'tk');
  await api.miJuego('tk');
  await api.empezar('tk', 2);
  await api.probar('tk', 2, 'casas', 3);

  assert.deepEqual(llamadas, [
    ['estado_del_juego', { p_evento: 'ev' }],
    ['nombres_del_evento', { p_evento: 'ev' }],
    ['elegir_nombre', { p_evento: 'ev', p_nombre: 'Ana', p_token: 'tk' }],
    ['mi_juego', { p_evento: 'ev', p_token: 'tk' }],
    ['empezar_palabra', { p_evento: 'ev', p_token: 'tk', p_orden: 2 }],
    ['probar_palabra', { p_evento: 'ev', p_token: 'tk', p_orden: 2, p_palabra: 'casas', p_numero: 3 }],
  ]);
  assert.equal(tablero({ intentos: [], terminada_en: null }, ['a']).match(/ev-fila/g).length, 6);
});
