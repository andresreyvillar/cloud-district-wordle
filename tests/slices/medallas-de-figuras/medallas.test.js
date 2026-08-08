/**
 * Escenarios de vista de `medallas-de-figuras`.
 *
 *     node --test tests/slices/medallas-de-figuras/
 *
 * El icono se comprueba **contra el sprite real**, leyéndolo del disco: un test que solo mirase la lista de
 * la vista pasaría con un símbolo que no existe, y en el navegador se vería un hueco.
 */

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

import { LOGROS } from '../../../v2/js/ui/temporada.js';

const SPRITE = fileURLToPath(new URL('../../../v2/assets/icons/logros.svg', import.meta.url));

const DE_FIGURA = ['ornitologo', 'arquitecto', 'florista', 'coleccionista', 'abstracto'];

/** @scenarios las-doce-medallas-aparecen-en-la-temporada */
test('la vista lista las doce medallas, con las cinco de figuras', () => {
  assert.equal(LOGROS.length, 12);

  const ids = LOGROS.map((l) => l.id);
  for (const clave of DE_FIGURA) {
    assert.ok(ids.includes(clave), `falta ${clave}`);
  }
  for (const logro of LOGROS) {
    assert.ok(logro.nombre && logro.regla, `${logro.id} sin nombre o sin regla`);
  }
});

/**
 * Los símbolos que el sprite define **de verdad**: se quitan los comentarios antes de mirar.
 *
 * La primera versión de este test buscaba la cadena `id="…"` en el fichero entero, y pasó en verde con el
 * sprite roto: el símbolo nuevo se había insertado **dentro del comentario de la cabecera**, porque ahí hay
 * un `</svg>` de ejemplo. El navegador enseñó doce tarjetas sin icono; el test decía que todo bien.
 */
function simbolosDelSprite() {
  const sinComentarios = readFileSync(SPRITE, 'utf8').replace(/<!--[\s\S]*?-->/g, '');
  return [...sinComentarios.matchAll(/<symbol id="([^"]+)"/g)].map((m) => m[1]);
}

/** @scenarios cada-medalla-de-figura-tiene-su-icono */
test('cada medalla referencia un símbolo que el sprite define de verdad', () => {
  const simbolos = simbolosDelSprite();

  for (const logro of LOGROS) {
    assert.ok(simbolos.includes(logro.id), `el sprite no define el símbolo ${logro.id}`);
  }
});

/** @scenarios cada-medalla-de-figura-tiene-su-icono */
test('el sprite sigue cerrando bien: un símbolo dentro de un comentario no cuenta', () => {
  const sprite = readFileSync(SPRITE, 'utf8');
  const abren = (sprite.match(/<symbol /g) ?? []).length;
  const cierran = (sprite.match(/<\/symbol>/g) ?? []).length;

  assert.equal(abren, cierran, 'símbolos sin cerrar');
  assert.equal(simbolosDelSprite().length, abren, 'algún símbolo quedó dentro de un comentario');
  assert.ok(sprite.trimEnd().endsWith('</svg>'), 'el sprite no termina donde debe');
});

/** @scenarios cada-medalla-de-figura-tiene-su-icono */
test('el símbolo del fontanero se renombró: la categoría ya no se llama caca', () => {
  const simbolos = simbolosDelSprite();

  assert.ok(!simbolos.includes('fontanero'), 'quedaba la última copia del vocabulario viejo');
  assert.ok(simbolos.includes('abstracto'));
});
