/**
 * Escenarios de `ruta-invalida` (Fase 2 — TDD rojo).
 *
 *     node --test tests/slices/ruta-invalida/
 *
 * `pintarDesconocida` solo asigna `innerHTML`, así que se prueba con un contenedor falso y sin navegador. Lo
 * que se comprueba es el marcado que llega al DOM, que es el comportamiento observable.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { resolver, seccionDe, VISTAS } from '../../../v2/js/router.js';
import { pintarDesconocida } from '../../../v2/js/ui/shell.js';

/** Un contenedor de mentira: `pintarDesconocida` no toca nada más que `innerHTML`. */
function contenedor() {
  return { innerHTML: '' };
}

function pintar(ruta) {
  const c = contenedor();
  pintarDesconocida(c, resolver(ruta));
  return c.innerHTML;
}

/** @scenarios una-ruta-desconocida-se-declara */
test('una ruta que el router no reconoce se declara, con la ruta pedida', () => {
  const destino = resolver('/ruta/que/no/existe');

  assert.equal(destino.vista, VISTAS.DESCONOCIDA);
  assert.equal(destino.ruta, '/ruta/que/no/existe');

  const html = pintar('/ruta/que/no/existe');
  assert.match(html, /ruta no reconocida/i);
  assert.ok(html.includes('/ruta/que/no/existe'), 'tiene que decir qué ruta se pidió');
});

/** @scenarios una-temporada-imposible-no-es-una-temporada */
test('un mes que no existe es ruta desconocida, no una temporada vacía', () => {
  for (const ruta of ['/t/2026-13', '/t/2026-00', '/t/26-01', '/t/abril']) {
    assert.equal(resolver(ruta).vista, VISTAS.DESCONOCIDA, `${ruta} no es una temporada`);
  }
  // y los meses reales sí lo son, incluida la temporada 0
  for (const ruta of ['/t/2026-01', '/t/2026-12', '/t/0']) {
    assert.equal(resolver(ruta).vista, VISTAS.TEMPORADA, `${ruta} sí es una temporada`);
  }
});

/** @scenarios un-identificador-que-no-es-de-slack-no-abre-ficha */
test('una ruta de jugador mal formada es desconocida', () => {
  for (const ruta of ['/t/2026-08/j/pepito', '/t/2026-08/j/', '/t/2026-08/j/U1/extra', '/j/U08U27DFDL2']) {
    assert.equal(resolver(ruta).vista, VISTAS.DESCONOCIDA, `${ruta} no abre ficha`);
  }
  const buena = resolver('/t/2026-08/j/U08U27DFDL2');
  assert.equal(buena.vista, VISTAS.JUGADOR);
  assert.equal(buena.jugador, 'U08U27DFDL2');
});

/** @scenarios una-ruta-desconocida-ofrece-la-salida */
test('la vista ofrece volver a la temporada en curso', () => {
  const html = pintar('/no/existe');

  assert.match(html, /href="\/"/, 'el enlace roto no puede ser el final del camino');
});

/** @scenarios una-ruta-desconocida-no-marca-ninguna-seccion */
test('una ruta desconocida no pertenece a ninguna sección de la navegación', () => {
  assert.equal(seccionDe(VISTAS.DESCONOCIDA), null);
  // las válidas sí pertenecen a una, y la ficha pertenece a Temporada
  assert.equal(seccionDe(VISTAS.JUGADOR), VISTAS.TEMPORADA);
  assert.equal(seccionDe(VISTAS.DATOS), VISTAS.DATOS);
});

/** @scenarios la-ruta-que-se-muestra-va-escapada */
test('la ruta pedida se muestra como texto, no se interpreta', () => {
  const html = pintar('/<img src=x onerror=alert(1)>');

  assert.ok(!html.includes('<img'), 'la ruta la escribe quien manda el enlace: es entrada ajena');
  assert.match(html, /&lt;img/);
});

/** @scenarios una-ruta-desconocida-se-declara */
test('las rutas válidas no caen aquí, ni con barra final ni con parámetros', () => {
  for (const ruta of ['/', '/hoy', '/hoy/', '/datos?x=1', '/reglas#eje', '/temporadas']) {
    assert.notEqual(resolver(ruta).vista, VISTAS.DESCONOCIDA, `${ruta} es válida`);
  }
});
