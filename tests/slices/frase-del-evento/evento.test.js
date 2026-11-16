/**
 * La vista del participante del evento, de `frase-del-evento` (cambio `feat-frase-del-evento`).
 *
 *     node --test tests/slices/frase-del-evento/
 *
 * Sin red: la API del evento se dobla. Participantes y frases sintéticos: el repositorio es público.
 */

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

import { FalloDelEvento, apiDelEvento, esLocal, esRechazo } from '../../../v2/js/evento/api.js';
import { celdasDeLaFrase, coloresDelTeclado, momentoDelEvento, normaliza, tokenAleatorio } from '../../../v2/js/evento/dominio.js';
import { comoSeJuega, controlDelEvento, panelDeLaFrase, tablero, teclado, vistaDelEvento } from '../../../v2/js/evento/jugador.js';
import { esDelEvento, resolver, rutaDe, VISTAS } from '../../../v2/js/router.js';
import { navegacion } from '../../../v2/js/ui/shell.js';

const T0 = Date.parse('2026-11-20T10:00:00Z');
const MIN = 60_000;
const PALABRAS = new Set(['sacas', 'salmo', 'rayos', 'tunde', 'museo']);

/** El estado del servidor con el evento empezado en `inicio` y una frase cada 10 minutos. */
function estado({ inicio = T0, ahora = T0 + MIN, frases = 3, soluciones = null, terminado = false } = {}) {
  return {
    titulo: 'Evento de test',
    ahora: new Date(ahora).toISOString(),
    empieza_en: inicio === null ? null : new Date(inicio).toISOString(),
    intervalo_minutos: 10,
    participantes: 2,
    terminado,
    frases: Array.from({ length: frases }, (_, i) => ({
      orden: i + 1,
      abre_en: inicio === null ? null : new Date(inicio + i * 10 * MIN).toISOString(),
      estado: 'abierta',
      jugando: 0, resueltas: 0, sin_resolver: 0,
      ...(soluciones ? { solucion: soluciones[i] } : {}),
    })),
  };
}

const partida = (extra = {}) => ({
  orden: 1, visible: '¿___ _ ___?', descubiertas: '', empezada_en: new Date(T0 + MIN).toISOString(),
  terminada_en: null, resuelta: false, tiempo_ms: null, intentos: [], ...extra,
});

/** Una API falsa que apunta las llamadas. */
function apiFalsa({ est = estado(), nombres = new Map(), ...sobre } = {}) {
  const llamadas = [];
  const apunta = (nombre, fn) => async (...args) => { llamadas.push([nombre, ...args]); return fn(...args); };
  return {
    llamadas,
    evento: 'prueba',
    estado: apunta('estado', () => est),
    unirse: apunta('unirse', (nombre, token) => { nombres.set(token, nombre.trim()); return { nombre: nombre.trim() }; }),
    miPartida: apunta('miPartida', (token) => {
      if (!nombres.has(token)) throw new FalloDelEvento('no estás apuntado al evento', 'rechazo');
      return { nombre: nombres.get(token), partidas: [] };
    }),
    empezar: apunta('empezar', () => partida()),
    intentar: apunta('intentar', (_t, _o, palabra) => partida({
      visible: '¿s__ _ _a_?', descubiertas: 'as', intentos: [{ palabra, colores: 'GG.GG' }],
    })),
    ranking: apunta('ranking', () => [{ puesto: 1, nombre: 'Ana', resueltas: 1, tiempo_ms: 161_350, frases: [] }]),
    ...sobre,
  };
}

function almacenFalso() {
  const datos = new Map();
  return { datos, leer: (k) => datos.get(k) ?? null, guardar: (k, v) => datos.set(k, v) };
}

async function dentro(api, ahora = T0 + MIN, palabras = PALABRAS) {
  const control = controlDelEvento({ api, almacen: almacenFalso(), reloj: () => ahora, palabras, generarToken: () => 'tk-ana' });
  await control.entrar('Ana');
  await control.refrescar();
  return control;
}

/** Dentro, con la frase 1 elegida y empezada. */
async function jugando(api, ahora = T0 + MIN, palabras = PALABRAS) {
  const control = await dentro(api, ahora, palabras);
  control.elegir(1);
  await control.empezar();
  return control;
}

const vista = (control) => vistaDelEvento(control.estado, control.ahora());
const escribir = (control, palabra) => [...palabra].forEach((letra) => control.teclear(letra));

/** @scenarios la-ruta-del-evento-no-sale-en-el-menu */
test('la ruta /evento resuelve a la vista del participante y ninguna pestaña lleva a ella', () => {
  assert.equal(resolver('/evento').vista, VISTAS.EVENTO);
  assert.equal(resolver('/evento/pantalla').vista, VISTAS.PANTALLA_DEL_EVENTO);
  assert.equal(resolver('/evento/otra').vista, VISTAS.DESCONOCIDA);
  assert.ok(esDelEvento(resolver('/evento')) && esDelEvento(resolver('/evento/pantalla')));
  assert.ok(!esDelEvento(resolver('/debate')));
  assert.equal(rutaDe({ vista: VISTAS.EVENTO }), '/evento');
  for (const destino of [{ vista: VISTAS.TEMPORADA }, { vista: VISTAS.EVENTO }]) {
    assert.doesNotMatch(navegacion(destino), /evento/);
  }
});

/** @scenarios la-ruta-del-evento-no-sale-en-el-menu */
test('el arranque pinta el evento antes de cargar los datos de la web y sin su cabecera', () => {
  const app = readFileSync(new URL('../../../v2/js/app.js', import.meta.url), 'utf8');
  const arranque = app.slice(app.indexOf('export async function arrancar()'));

  assert.ok(arranque.indexOf('arrancarEvento(') < arranque.indexOf('cargarResultados()'));
  assert.match(app, /querySelector\('\.cabecera'\)\?\.remove\(\)/);
});

/** @scenarios el-evento-tiene-su-propia-apariencia */
test('la hoja del evento declara colores, tipografía y logo como variables y la web no la usa', () => {
  const hoja = readFileSync(new URL('../../../v2/css/evento.css', import.meta.url), 'utf8');
  const raiz = hoja.slice(hoja.indexOf(':root {'), hoja.indexOf('}', hoja.indexOf(':root {')));
  for (const variable of ['--ev-fondo', '--ev-tinta', '--ev-acento', '--ev-verde', '--ev-amarillo', '--ev-gris', '--ev-fuente', '--ev-logo']) {
    assert.match(raiz, new RegExp(`${variable}:`), variable);
  }
  assert.match(hoja, /\.ev-celda\.verde \{ background: var\(--ev-verde\)/);
  const web = readFileSync(new URL('../../../v2/css/styles.css', import.meta.url), 'utf8');
  assert.doesNotMatch(web, /--ev-|\.ev-|\.pa-/, 'la web de estadísticas no cambia con el tema');
  const index = readFileSync(new URL('../../../v2/index.html', import.meta.url), 'utf8');
  assert.doesNotMatch(index, /evento\.css/, 'la hoja solo se carga en las rutas del evento');
});

/** @scenarios se-entra-con-un-nombre */
test('al entrar se guarda el token del móvil y al recargar sigue dentro', async () => {
  const nombres = new Map();
  const almacen = almacenFalso();
  const primera = controlDelEvento({ api: apiFalsa({ nombres }), almacen, reloj: () => T0, generarToken: () => 'tk-1' });
  await primera.entrar('  Ana ');

  const recargada = controlDelEvento({ api: apiFalsa({ nombres }), almacen, reloj: () => T0 });
  await recargada.arrancar();

  assert.equal(recargada.estado.nombre, 'Ana');
  assert.equal(recargada.estado.token, 'tk-1');
  assert.doesNotMatch(vista(recargada), /ev-nombre/, 'no se vuelve a pedir el nombre');
});

/** @scenarios se-entra-con-un-nombre */
test('sin nombre no se llama al servidor, y un rechazo se dice', async () => {
  const api = apiFalsa({ unirse: async () => { throw new FalloDelEvento('ese nombre ya está apuntado: elige otro', 'rechazo'); } });
  const control = controlDelEvento({ api, almacen: almacenFalso(), reloj: () => T0 });

  await control.entrar('   ');
  assert.match(control.estado.aviso, /nombre/);
  assert.equal(api.llamadas.length, 0);

  await control.entrar('Ana');
  assert.match(vista(control), /ya está apuntado/);
  assert.equal(control.estado.nombre, null);
});

/** @scenarios se-entra-con-un-nombre */
test('si al recargar no hay red, se conserva el token y se reintenta sin pedir el nombre', async () => {
  const almacen = almacenFalso();
  almacen.guardar('evento:token:prueba', 'tk-ana');
  let red = false;
  const api = apiFalsa({
    miPartida: async () => {
      if (!red) throw new FalloDelEvento('Failed to fetch', 'red');
      return { nombre: 'Ana', partidas: [] };
    },
  });
  const control = controlDelEvento({ api, almacen, reloj: () => T0 + MIN });

  await control.arrancar();
  assert.equal(control.estado.token, 'tk-ana');
  assert.match(vista(control), /Recuperando tu partida/);

  red = true;
  await control.arrancar();
  assert.equal(control.estado.nombre, 'Ana');
});

/** @scenarios se-entra-con-un-nombre, una-partida-por-frase */
test('un doble toque en Entrar manda el mismo token, y en Empezar no borra lo escrito', async () => {
  let tokens = 0;
  const control = controlDelEvento({ api: apiFalsa(), almacen: almacenFalso(), reloj: () => T0 + MIN, generarToken: () => `tk-${++tokens}` });
  await Promise.all([control.entrar('Ana'), control.entrar('Ana')]);
  assert.equal(tokens, 1);
  await control.refrescar();
  control.elegir(1);
  await control.empezar();
  control.teclear('s');

  await control.empezar();

  assert.deepEqual(control.estado.escrito, ['s']);
  assert.match(tokenAleatorio(), /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
});

/** @scenarios antes-de-liberar-se-ve-la-cuenta-atras */
test('sin empezar el evento se dice que empieza con el presentador, sin frases ni cuenta atrás', async () => {
  const control = await dentro(apiFalsa({ est: estado({ inicio: null }) }));

  const html = vista(control);

  assert.match(html, /en cuanto el presentador empiece/);
  assert.doesNotMatch(html, /data-cuenta-atras|data-elegir|data-accion="empezar"|ev-teclado/);
});

/** @scenarios antes-de-liberar-se-ve-la-cuenta-atras */
test('la cuenta atrás a la siguiente frase usa la hora del servidor aunque el móvil vaya desajustado', async () => {
  // El servidor va 1 hora por delante del móvil: son las 10:01 en el servidor.
  const control = await dentro(apiFalsa({ est: estado({ ahora: T0 + MIN }) }), T0 + MIN - 60 * MIN);

  assert.equal(control.ahora(), T0 + MIN);
  assert.match(vista(control), /La frase 2 sale en <strong[^>]*>9:00</);
});

/** @scenarios una-frase-liberada-se-juega-hasta-el-final */
test('la lista enseña las frases liberadas, también las anteriores, y cada una se puede elegir', async () => {
  const control = await dentro(apiFalsa({ est: estado({ ahora: T0 + 25 * MIN }) }), T0 + 25 * MIN);
  control.estado.partidas.set(1, partida({ terminada_en: 'x', resuelta: true, tiempo_ms: 95_000 }));

  const html = vista(control);

  assert.deepEqual([...html.matchAll(/data-elegir="(\d)"/g)].map((m) => m[1]), ['1', '2', '3']);
  assert.match(html, /Frase 1<\/strong><span>Resuelta en 1:35/);
  assert.match(html, /Frase 2<\/strong><span>Por jugar/);
  assert.match(html, /Ya están todas las frases/);
  assert.deepEqual(momentoDelEvento(control.estado.estado, control.ahora()).liberadas.map((f) => f.orden), [1, 2, 3]);
});

/** @scenarios el-tablero-sale-al-pulsar-empezar */
test('antes de Empezar no hay frase; al pulsarlo salen la frase tapada y el tablero de cinco palabras', async () => {
  const api = apiFalsa();
  const control = await dentro(api);
  control.elegir(1);
  assert.match(vista(control), /data-accion="empezar"/);
  assert.doesNotMatch(vista(control), /ev-casilla/);

  await control.empezar();
  const html = vista(control);

  assert.deepEqual(api.llamadas.find(([n]) => n === 'empezar'), ['empezar', 'tk-ana', 1]);
  assert.equal(html.match(/class="ev-casilla"/g).length, 7, 'una casilla tapada por letra');
  assert.match(html, /ev-signo">¿</);
  assert.equal(html.match(/class="ev-fila/g).length, 5);
  assert.equal(html.match(/class="ev-celda/g).length, 25);
});

/** @scenarios el-cronometro-empieza-en-cero, el-reloj-no-se-pausa */
test('el cronómetro cuenta desde Empezar con la hora del servidor, también al volver tras cerrar', async () => {
  const empezo = partida({ empezada_en: new Date(T0 + MIN).toISOString() });
  assert.match(vistaDelEvento({ ...(await jugando(apiFalsa(), T0 + MIN)).estado }, T0 + MIN), /data-cronometro="\d+">0:00</);

  // Cerró la web y vuelve cuatro minutos y medio después: el reloj no se ha parado.
  const nombres = new Map([['tk-ana', 'Ana']]);
  const almacen = almacenFalso();
  almacen.guardar('evento:token:prueba', 'tk-ana');
  const vuelta = controlDelEvento({
    api: apiFalsa({ nombres, est: estado({ ahora: T0 + MIN + 270_000 }), miPartida: async () => ({ nombre: 'Ana', partidas: [empezo] }) }),
    almacen, reloj: () => T0 + MIN + 270_000,
  });
  await vuelta.arrancar();
  vuelta.elegir(1);

  assert.match(vista(vuelta), /data-cronometro="\d+">4:30</);
});

/** @scenarios cada-intento-es-una-palabra-de-cinco-letras, verde-destapa-la-letra-en-toda-la-frase */
test('una palabra válida se envía con su número y la frase se pinta con lo que destapó', async () => {
  const api = apiFalsa();
  const control = await jugando(api);
  escribir(control, 'sacas');

  await control.enviar();
  const html = vista(control);

  assert.deepEqual(api.llamadas.find(([n]) => n === 'intentar'), ['intentar', 'tk-ana', 1, 'sacas', 1]);
  assert.match(html, /ev-casilla destapada">S</);
  assert.equal(html.match(/class="ev-celda llena verde"/g).length, 4);
  assert.match(html, /class="ev-celda llena gris">C</);
});

/** @scenarios una-palabra-que-no-esta-en-la-lista-no-gasta-intento */
test('una palabra que no está en la lista no se envía y se queda escrita', async () => {
  const api = apiFalsa();
  const control = await jugando(api);
  escribir(control, 'aeiou');

  await control.enviar();

  assert.ok(!api.llamadas.some(([n]) => n === 'intentar'));
  assert.match(control.estado.aviso, /no está en la lista/);
  assert.deepEqual(control.estado.escrito, [...'aeiou']);
});

/** @scenarios una-palabra-que-no-esta-en-la-lista-no-gasta-intento */
test('sin la lista cargada decide el servidor, y su rechazo se dice sin perder lo escrito', async () => {
  const api = apiFalsa({ intentar: async () => { throw new FalloDelEvento('la palabra no está en la lista', 'rechazo'); } });
  const control = await jugando(api, T0 + MIN, null);
  escribir(control, 'aeiou');

  await control.enviar();

  assert.ok(api.llamadas.some(([n]) => n === 'miPartida'), 'tras un rechazo se rehace la partida');
  assert.match(vista(control), /no está en la lista/);
  assert.deepEqual(control.estado.escrito, [...'aeiou']);
});

/** @scenarios un-intento-incompleto-no-se-envia */
test('con letras por rellenar Enviar no llama al servidor, y no se escribe más allá de la quinta', async () => {
  const api = apiFalsa();
  const control = await jugando(api);
  escribir(control, 'sac');

  await control.enviar();
  assert.ok(!api.llamadas.some(([n]) => n === 'intentar'));
  assert.match(control.estado.aviso, /Faltan 2 letras/);

  escribir(control, 'asxx');
  assert.deepEqual(control.estado.escrito, [...'sacas']);
});

/** @scenarios amarilla-si-ya-estaba-destapada, gris-si-no-esta, el-teclado-trae-la-ene */
test('el tablero pinta amarillas y grises, y el teclado tiene Ñ, verde lo que está y gris lo que no', () => {
  const html = tablero(partida({ intentos: [{ palabra: 'sosos', colores: 'YGYGY' }] }));
  assert.match(html, /class="ev-celda llena amarilla">S</);

  const colores = coloresDelTeclado([{ palabra: 'sacas', colores: 'GG.GG' }, { palabra: 'cosas', colores: '.GYYY' }]);
  assert.equal(colores.get('s'), 'G');
  assert.equal(colores.get('c'), '.');
  assert.equal(colores.get('o'), 'G', 'una amarilla también está en la frase');
  const teclas = teclado([{ palabra: 'ñandu', colores: 'G....' }]);
  assert.match(teclas, /class="ev-tecla verde" data-tecla="ñ">Ñ</);
  assert.match(teclas, /class="ev-tecla gris" data-tecla="u"/);
});

/** @scenarios los-acentos-no-cuentan-y-la-ene-si */
test('las tildes del teclado se quitan, la ñ se queda, y la frase destapada conserva sus tildes', () => {
  assert.equal(normaliza('Cañón'), 'cañon');
  assert.match(panelDeLaFrase('E_ año, canc_ón'), /destapada">Ó</);
  assert.deepEqual(celdasDeLaFrase('E_ a').map((p) => p.map((c) => c.tipo)), [['letra', 'tapada'], ['letra']]);
});

/** @scenarios se-gana-al-destapar-todas-las-letras, durante-el-evento-no-se-ve-la-posicion */
test('al destapar la última letra se ve «¡Resuelta en m:ss!» sin puesto ni puntos', async () => {
  const api = apiFalsa({
    intentar: async () => partida({ visible: 'sol y mar', terminada_en: 'x', resuelta: true, tiempo_ms: 161_350,
      intentos: [{ palabra: 'salmo', colores: 'GGGGG' }, { palabra: 'rayos', colores: 'GYGYY' }] }),
  });
  const control = await jugando(api);
  escribir(control, 'rayos');
  await control.enviar();

  const html = vista(control);

  assert.match(html, /¡Resuelta en 2:41!/);
  assert.doesNotMatch(html, /puesto|puntos|ranking|ev-teclado/i);
  assert.ok(!api.llamadas.some(([n]) => n === 'ranking'), 'durante el evento no se pide el ranking');
});

/** @scenarios cinco-palabras-sin-destaparla-se-pierde */
test('perdida tras cinco palabras, se dice y ya no hay teclado', async () => {
  const cinco = ['tunde', 'pique', 'chufa', 'nieve', 'bucle'].map((palabra) => ({ palabra, colores: '.....' }));
  const control = await jugando(apiFalsa());
  control.estado.partidas.set(1, partida({ terminada_en: 'x', resuelta: false, tiempo_ms: 99_000, intentos: cinco }));

  const html = vista(control);

  assert.match(html, /no ha podido ser/);
  assert.doesNotMatch(html, /ev-teclado|ev-actual/);
  control.teclear('a');
  assert.deepEqual(control.estado.escrito, []);
});

/** @scenarios la-solucion-no-viaja-al-movil, la-solucion-se-ve-al-terminar-el-evento */
test('la frase entera solo se pinta cuando el estado la trae, al terminar', async () => {
  const curso = await jugando(apiFalsa());
  assert.doesNotMatch(vista(curso), /Las frases/);

  const control = await dentro(apiFalsa({ est: estado({ terminado: true, soluciones: ['sol y mar', 'El año', 'Más vale'] }) }));

  assert.match(vista(control), /Las frases[\s\S]*sol y mar[\s\S]*Más vale/);
});

/** @scenarios al-terminar-el-evento-no-se-admiten-palabras */
test('con el evento terminado no se escribe ni se envía nada', async () => {
  const api = apiFalsa();
  const control = await jugando(api);
  control.estado.estado = estado({ terminado: true });

  control.teclear('s');
  await control.enviar();

  assert.deepEqual(control.estado.escrito, []);
  assert.ok(!api.llamadas.some(([n]) => n === 'intentar'));
});

/** @scenarios al-terminar-se-ve-el-ranking */
test('terminado el evento se pinta el ranking con la fila propia destacada', async () => {
  const api = apiFalsa({
    est: estado({ terminado: true }),
    ranking: async () => [
      { puesto: 1, nombre: 'Bea', resueltas: 3, tiempo_ms: 400_000, frases: [] },
      { puesto: 2, nombre: 'Ana', resueltas: 2, tiempo_ms: 161_350, frases: [] },
    ],
  });
  const control = await dentro(api);

  const html = vista(control);

  assert.match(html, /Ranking final/);
  assert.match(html, /<li class="mia">\s*<span class="ev-puesto">2<\/span>\s*<span class="ev-nombre">Ana/);
  assert.match(html, /2 frases · 2:41/);
});

/** @scenarios el-texto-de-los-participantes-se-escapa */
test('un nombre con HTML se pinta como texto', async () => {
  const malo = '<img src=x onerror=alert(1)>';
  const control = controlDelEvento({ api: apiFalsa(), almacen: almacenFalso(), reloj: () => T0 + MIN });
  await control.entrar(malo);
  await control.refrescar();
  const terminado = await dentro(apiFalsa({
    est: estado({ terminado: true }),
    ranking: async () => [{ puesto: 1, nombre: malo, resueltas: 1, tiempo_ms: 1, frases: [] }],
  }));

  for (const html of [vista(control), vista(terminado)]) {
    assert.doesNotMatch(html, /<img/);
    assert.match(html, /&lt;img/);
  }
});

/** @scenarios si-el-servidor-no-responde-el-intento-no-se-pierde */
test('si el envío falla por la red, la palabra sigue escrita y el reenvío lleva el mismo número', async () => {
  let fallar = true;
  const api = apiFalsa({
    intentar: async (...args) => {
      api.llamadas.push(['intentar', ...args]);
      if (fallar) { fallar = false; throw new FalloDelEvento('Failed to fetch', 'red'); }
      return partida({ intentos: [{ palabra: args[2], colores: 'GG.GG' }] });
    },
  });
  const control = await jugando(api);
  escribir(control, 'sacas');

  await control.enviar();
  assert.deepEqual(control.estado.escrito, [...'sacas']);
  assert.match(vista(control), /No se ha podido enviar\. Tu palabra sigue escrita/);
  await control.enviar();

  assert.deepEqual(api.llamadas.filter(([n]) => n === 'intentar').map((l) => l[4]), [1, 1]);
  assert.equal(control.estado.partidas.get(1).intentos.length, 1);
});

/** @scenarios si-el-servidor-no-responde-el-intento-no-se-pierde */
test('una petición colgada se da por perdida y el teclado sigue respondiendo', async () => {
  const colgado = { rpc: () => new Promise(() => {}) };
  const api = { ...apiDelEvento(colgado, 'prueba', 20), estado: async () => estado(), empezar: async () => partida() };
  const control = await jugando(api);
  escribir(control, 'sacas');

  await control.enviar();

  assert.equal(control.estado.enviando, false);
  assert.match(control.estado.aviso, /No se ha podido enviar/);
  control.borrar();
  assert.equal(control.estado.escrito.length, 4, 'el teclado responde');
  assert.ok(esRechazo('22023') && !esRechazo('') && !esRechazo('PGRST202'));
});

/** @scenarios si-el-servidor-no-responde-el-intento-no-se-pierde */
test('en local el evento habla con el servidor local y fuera, con Supabase', () => {
  for (const host of ['localhost', '127.0.0.1', '192.168.1.40', '10.0.0.5', '172.20.1.1']) assert.ok(esLocal(host), host);
  for (const host of ['cloud-district-wordle.clouddistrict.workers.dev', '172.32.0.1', '8.8.8.8']) assert.ok(!esLocal(host), host);
});

/** @scenarios tras-terminar-se-pasa-a-la-siguiente */
test('al terminar una frase con la siguiente liberada, un botón lleva a ella', async () => {
  const control = await jugando(apiFalsa({ est: estado({ ahora: T0 + 12 * MIN }) }), T0 + 12 * MIN);
  control.estado.partidas.set(1, partida({ terminada_en: 'x', resuelta: true, tiempo_ms: 95_000 }));

  const html = vista(control);

  assert.match(html, /¡Resuelta en 1:35![\s\S]*<button type="button" class="ev-boton grande" data-elegir="2">Ir a la frase 2<\/button>/);
  control.elegir(2);
  assert.match(vista(control), /Frase 2<\/h1>[\s\S]*data-accion="empezar"/);
});

/** @scenarios tras-terminar-se-pasa-a-la-siguiente */
test('si la siguiente aún no ha salido, el botón está apagado y cuenta lo que falta con la hora del servidor', async () => {
  // El móvil va 2 minutos atrasado: manda el servidor (10:03 → la frase 2 sale en 7:00).
  const control = await jugando(apiFalsa({ est: estado({ ahora: T0 + 3 * MIN }) }), T0 + MIN);
  control.estado.partidas.set(1, partida({ terminada_en: 'x', resuelta: false, tiempo_ms: 60_000 }));

  const html = vista(control);

  assert.match(html, /no ha podido ser[\s\S]*<button type="button" class="ev-boton grande" disabled>La frase 2 sale en <strong class="ev-reloj" data-cuenta-atras="\d+">7:00</);
  assert.doesNotMatch(html, /data-elegir="2"/);
});

/** @scenarios tras-terminar-se-pasa-a-la-siguiente */
test('tras la última frase se dice que el ranking sale al terminar el evento', async () => {
  const control = await dentro(apiFalsa({ est: estado({ ahora: T0 + 25 * MIN }) }), T0 + 25 * MIN);
  control.elegir(3);
  control.estado.partidas.set(3, partida({ orden: 3, terminada_en: 'x', resuelta: true, tiempo_ms: 30_000 }));

  assert.match(vista(control), /Era la última frase\. El ranking sale cuando el presentador termine el evento/);
});

/** @scenarios un-evento-con-contrasena-solo-deja-entrar-a-quien-la-sabe */
test('si el evento tiene contraseña, la web la pide y la manda al entrar; si no, no la pide', async () => {
  const api = apiFalsa({ est: { ...estado(), con_clave: true } });
  const control = controlDelEvento({ api, almacen: almacenFalso(), reloj: () => T0 + MIN, generarToken: () => 'tk-1' });
  await control.refrescar();
  assert.match(vista(control), /name="clave" type="password"/);

  await control.entrar('Ana', '');
  assert.match(control.estado.aviso, /contraseña/);
  assert.ok(!api.llamadas.some(([n]) => n === 'unirse'), 'sin contraseña no se llama');

  await control.entrar('Ana', 'cl4ve');
  assert.deepEqual(api.llamadas.find(([n]) => n === 'unirse'), ['unirse', 'Ana', 'tk-1', 'cl4ve']);

  const sin = controlDelEvento({ api: apiFalsa(), almacen: almacenFalso(), reloj: () => T0 + MIN });
  await sin.refrescar();
  assert.doesNotMatch(vista(sin), /name="clave"/);
});

/** @scenarios se-explica-como-se-juega */
test('la explicación sale en la espera y con el botón, también a mitad de frase', async () => {
  const espera = await dentro(apiFalsa({ est: estado({ inicio: null }) }));
  assert.match(vista(espera), /Cómo se juega[\s\S]*5 letras[\s\S]*5 palabras/);

  const control = await jugando(apiFalsa());
  assert.doesNotMatch(vista(control), /class="ev-ayuda"/);
  control.ayuda();
  const html = vista(control);

  assert.match(html, /class="ev-ayuda"/);
  assert.match(html, /data-accion="ayuda" aria-expanded="true">Cerrar/);
  assert.match(html, /ev-tablero/, 'el juego sigue debajo');
  control.ayuda();
  assert.doesNotMatch(vista(control), /class="ev-ayuda"/);
});

/** @scenarios se-explica-como-se-juega */
test('la explicación cuenta los colores, cómo se gana y el tiempo, con un ejemplo inventado', () => {
  const html = comoSeJuega();

  assert.match(html, /ev-celda verde">S<\/span><span>está en la frase: se destapa <strong>en todos sus sitios/);
  assert.match(html, /ev-celda amarilla">S<\/span><span>está, pero ya la tenías destapada/);
  assert.match(html, /ev-celda gris">C<\/span><span>no está en la frase/);
  assert.match(html, /Ganas al destapar todas las letras/);
  assert.match(html, /no se para aunque cierres la web/);
  assert.match(html, /SOL Y MAR[\s\S]*ev-celda llena verde">S[\s\S]*destapada">S/);
  assert.equal(html.match(/class="ev-fila"/g).length, 1, 'el ejemplo enseña solo la palabra jugada');
});
