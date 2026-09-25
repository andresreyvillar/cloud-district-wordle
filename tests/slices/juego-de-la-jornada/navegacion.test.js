/**
 * La pestaña lleva al juego, de `juego-de-la-jornada`.
 *
 *     node --test tests/slices/juego-de-la-jornada/
 *
 * Se escapó a producción: `resolver` conocía `/juego` pero `rutaDe` no, así que escribir la URL funcionaba y
 * **pulsar la pestaña llevaba a la portada**. Ninguna prueba pulsaba la pestaña. Este test recorre todas las
 * pestañas: una nueva que se olvide de su ruta cae aquí y no en producción.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { configurarBase, resolver, rutaDe, VISTAS } from '../../../v2/js/router.js';
import { navegacion } from '../../../v2/js/ui/shell.js';

/** Los enlaces de la navegación: `[etiqueta, href]`. */
function enlaces(destino) {
  return [...navegacion(destino).matchAll(/<a href="([^"]*)"[^>]*>([^<]*)/g)].map(([, href, etiqueta]) => [etiqueta, href]);
}

/** @scenarios la-pestana-lleva-al-juego */
test('la pestaña SuperWordleBros enlaza a /juego, también con la web montada en /2/', () => {
  for (const base of ['/', '/2/']) {
    configurarBase(base);
    const [, href] = enlaces({ vista: VISTAS.TEMPORADA }).find(([etiqueta]) => etiqueta === 'SuperWordleBros');

    assert.equal(href, `${base}juego`);
    assert.equal(resolver(href).vista, VISTAS.JUEGO);
  }
  configurarBase('/');
});

/** @scenarios la-pestana-lleva-al-juego */
test('cada pestaña lleva a su propia vista, ninguna a la portada por defecto', () => {
  configurarBase('/2/');
  const vistas = enlaces({ vista: VISTAS.HOY, temporada: '2026-09' }).map(([, href]) => resolver(href).vista);
  configurarBase('/');

  assert.equal(new Set(vistas).size, vistas.length, `dos pestañas llevan a la misma vista: ${vistas.join(', ')}`);
});

/** @scenarios la-pestana-lleva-al-juego */
test('la ruta del juego hace ida y vuelta', () => {
  assert.equal(resolver(rutaDe({ vista: VISTAS.JUEGO })).vista, VISTAS.JUEGO);
});
