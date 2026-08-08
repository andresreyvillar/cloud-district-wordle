/**
 * El Worker que reparte las dos webs por ruta.
 *
 *     node --test tests/v2/
 *
 * Se prueba con un doble de `env.ASSETS` que solo conoce unos pocos ficheros, porque lo que hay que verificar
 * es **el reparto**, no que Cloudflare sepa servir un fichero.
 *
 * El doble imita la restricción que importa: `ASSETS.fetch` devuelve 404 cuando el fichero no existe. Un
 * doble que devolviera siempre 200 haría pasar el fallback de SPA sin ejercitarlo.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import worker from '../../worker/index.js';

/** Los ficheros que existen como asset. Todo lo demás es 404, como en producción. */
const FICHEROS = new Set([
  '/index.html',
  '/js/script.js',
  '/v2/index.html',
  '/v2/css/styles.css',
  '/v2/assets/icons/logros.svg',
]);

function entorno() {
  const pedidos = [];
  return {
    pedidos,
    ASSETS: {
      async fetch(request) {
        const ruta = new URL(request.url).pathname;
        pedidos.push(ruta);
        const normalizada = ruta.endsWith('/') ? `${ruta}index.html` : ruta;
        if (FICHEROS.has(normalizada)) {
          return new Response(`contenido de ${normalizada}`, { status: 200 });
        }
        return new Response('no encontrado', { status: 404 });
      },
    },
  };
}

async function pedir(ruta) {
  const env = entorno();
  const respuesta = await worker.fetch(new Request(`https://ejemplo.workers.dev${ruta}`), env);
  return { respuesta, pedidos: env.pedidos };
}

test('la raíz y los ficheros de la v1 se delegan tal cual', async () => {
  const raiz = await pedir('/');
  assert.equal(raiz.respuesta.status, 200);
  assert.deepEqual(raiz.pedidos, ['/'], 'la v1 no se reescribe');

  const script = await pedir('/js/script.js');
  assert.equal(script.respuesta.status, 200);
  assert.deepEqual(script.pedidos, ['/js/script.js']);
});

test('una ruta inexistente de la v1 sigue siendo 404, no una página con 200', async () => {
  const { respuesta } = await pedir('/lo-que-sea');

  assert.equal(respuesta.status, 404, 'el fallback de SPA es solo de la v2');
});

test('/2 sin barra redirige a /2/, para que el `base` resuelva bien', async () => {
  const { respuesta } = await pedir('/2');

  assert.equal(respuesta.status, 301);
  assert.equal(respuesta.headers.get('location'), 'https://ejemplo.workers.dev/2/');
});

test('/2/ sirve el index de la v2', async () => {
  const { respuesta, pedidos } = await pedir('/2/');

  assert.equal(respuesta.status, 200);
  assert.equal(await respuesta.text(), 'contenido de /v2/index.html');
  assert.ok(pedidos[0].startsWith('/v2/'), `la ruta se reescribió a ${pedidos[0]}`);
});

test('los recursos de la v2 se reescriben a v2/', async () => {
  const css = await pedir('/2/css/styles.css');
  assert.equal(css.respuesta.status, 200);
  assert.deepEqual(css.pedidos, ['/v2/css/styles.css']);

  const sprite = await pedir('/2/assets/icons/logros.svg');
  assert.equal(sprite.respuesta.status, 200);
  assert.deepEqual(sprite.pedidos, ['/v2/assets/icons/logros.svg']);
});

test('una ruta profunda de la v2 cae en su index, no en el de la v1', async () => {
  const { respuesta, pedidos } = await pedir('/2/t/2026-08/j/U08U27DFDL2');

  assert.equal(respuesta.status, 200);
  assert.equal(await respuesta.text(), 'contenido de /v2/index.html');
  assert.deepEqual(
    pedidos,
    ['/v2/t/2026-08/j/U08U27DFDL2', '/v2/'],
    'primero intenta el fichero y luego cae al index de la v2',
  );
});

test('el fallback de la v2 no se lleva por delante a la v1', async () => {
  const v1 = await pedir('/ruta/inventada');
  const v2 = await pedir('/2/ruta/inventada');

  assert.equal(v1.respuesta.status, 404);
  assert.equal(v2.respuesta.status, 200);
  assert.ok(!v1.pedidos.some((ruta) => ruta.includes('index.html')), 'la v1 no recibe fallback');
});

test('un prefijo parecido pero distinto no se confunde con el de la v2', async () => {
  // `/2abc` empieza por "/2" pero no por "/2/": es de la v1.
  const { respuesta, pedidos } = await pedir('/2abc');

  assert.equal(respuesta.status, 404);
  assert.deepEqual(pedidos, ['/2abc'], 'no se reescribió');
});


test('una redirección de la capa de assets no se devuelve al navegador', async () => {
  // El fallo real de producción: `/2/t/0` devolvía un 307 a `/v2/`, así que el navegador acababa en la ruta
  // interna y perdía la de la v2. Solo un 200 cuenta como fichero.
  const env = {
    pedidos: [],
    ASSETS: {
      async fetch(request) {
        const ruta = new URL(request.url).pathname;
        env.pedidos.push(ruta);
        if (ruta === '/v2/') return new Response('index de la v2', { status: 200 });
        return new Response(null, { status: 307, headers: { location: '/v2/' } });
      },
    },
  };

  const respuesta = await worker.fetch(
    new Request('https://ejemplo.workers.dev/2/t/0'),
    env,
  );

  assert.equal(respuesta.status, 200, 'una 3xx de los assets no puede llegar al navegador');
  assert.equal(await respuesta.text(), 'index de la v2');
  assert.deepEqual(env.pedidos, ['/v2/t/0', '/v2/']);
});


test('un 304 de los assets se devuelve, no se confunde con "no existe"', async () => {
  // El segundo fallo real: en la SEGUNDA visita el navegador pide condicionalmente los módulos que ya tiene
  // en caché, los assets responden 304, y tratarlo como "no existe" devolvía el index con MIME text/html.
  // El doble nunca había devuelto un 304, así que ningún test podía verlo.
  const env = {
    ASSETS: {
      async fetch(request) {
        if (new URL(request.url).pathname === '/v2/js/app.js') {
          return new Response(null, { status: 304 });
        }
        return new Response('index de la v2', { status: 200 });
      },
    },
  };

  const respuesta = await worker.fetch(
    new Request('https://ejemplo.workers.dev/2/js/app.js', {
      headers: { 'if-none-match': 'W/"abc"' },
    }),
    env,
  );

  assert.equal(respuesta.status, 304, 'un 304 tiene que llegar al navegador para que use su caché');
});
