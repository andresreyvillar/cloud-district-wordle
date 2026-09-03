/**
 * El reloj de repuesto del pipeline, probado sin red.
 *
 * `fetch` se sustituye por un doble, así que se comprueba **qué petición se manda** y no que GitHub responda.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import worker from '../../../worker/index.js';

/** Un contexto de Workers que ejecuta la promesa en lugar de dejarla en el aire. */
function contexto() {
  const pendientes = [];
  return { waitUntil: (p) => pendientes.push(p), esperar: () => Promise.all(pendientes) };
}

/** @scenarios el-pipeline-tiene-un-reloj-de-repuesto */
test('el cron despierta el workflow de datos', async () => {
  const llamadas = [];
  const original = globalThis.fetch;
  globalThis.fetch = async (url, opciones) => {
    llamadas.push({ url, opciones });
    return new Response(null, { status: 204 });
  };
  try {
    const ctx = contexto();
    await worker.scheduled({}, { GITHUB_TOKEN: 'x' }, ctx);
    await ctx.esperar();
  } finally {
    globalThis.fetch = original;
  }

  assert.equal(llamadas.length, 1, 'una petición y no más');
  const { url, opciones } = llamadas[0];
  assert.match(url, /\/actions\/workflows\/update_stats\.yml\/dispatches$/, url);
  assert.equal(opciones.method, 'POST');
  assert.equal(JSON.parse(opciones.body).ref, 'main');
  // GitHub responde 403 sin User-Agent: no es opcional.
  assert.ok(opciones.headers['User-Agent'], 'lleva User-Agent');
  assert.match(opciones.headers.Authorization, /^Bearer /);
});

/** @scenarios el-pipeline-tiene-un-reloj-de-repuesto */
test('sin token configurado el disparador no hace nada', async () => {
  const original = globalThis.fetch;
  let llamado = false;
  globalThis.fetch = async () => {
    llamado = true;
    return new Response(null, { status: 204 });
  };
  try {
    const ctx = contexto();
    await worker.scheduled({}, {}, ctx);
    await ctx.esperar();
  } finally {
    globalThis.fetch = original;
  }
  assert.equal(llamado, false, 'apagado por defecto: sin token no se llama a nada');
});

/** @scenarios el-pipeline-tiene-un-reloj-de-repuesto */
test('un fallo del disparador no revienta', async () => {
  const original = globalThis.fetch;
  globalThis.fetch = async () => {
    throw new Error('red caída');
  };
  try {
    const ctx = contexto();
    await worker.scheduled({}, { GITHUB_TOKEN: 'x' }, ctx);
    // Si `despierta` no capturase el error, este await rechazaría.
    await ctx.esperar();
  } finally {
    globalThis.fetch = original;
  }
});

/** @scenarios el-pipeline-tiene-un-reloj-de-repuesto */
test('una respuesta que no es 204 se registra y no revienta', async () => {
  const original = globalThis.fetch;
  globalThis.fetch = async () => new Response('Bad credentials', { status: 401 });
  try {
    const ctx = contexto();
    await worker.scheduled({}, { GITHUB_TOKEN: 'x' }, ctx);
    await ctx.esperar();
  } finally {
    globalThis.fetch = original;
  }
});
