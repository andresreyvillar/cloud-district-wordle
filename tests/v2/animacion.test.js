/**
 * El movimiento de la web.
 *
 *     node --test tests/v2/
 *
 * Lo que se prueba aquí no es que "se vea bien" —eso no se puede afirmar sin mirar— sino las dos cosas que
 * una animación SÍ puede romper y que no se ven mirando dos segundos: que una cifra acabe distinta de la
 * que pintó la vista, y que el movimiento siga activo para quien ha pedido que no lo esté.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { animar, cifraDe, movimientoReducido, textoDeCifra } from '../../v2/js/ui/animacion.js';

/** Una ventana de mentira con lo justo: la preferencia, el reloj y el planificador de fotogramas. */
function ventana({ reducido = false } = {}) {
  const pendientes = [];
  return {
    matchMedia: () => ({ matches: reducido }),
    performance: { now: () => 0 },
    requestAnimationFrame(fn) { pendientes.push(fn); },
    correrFotogramas(hasta = 1000) { while (pendientes.length) pendientes.shift()(hasta); },
    creados: [],
    IntersectionObserver: undefined,
  };
}

/** Se define aparte para que el doble pueda registrarse en la ventana que lo crea. */
function conObservadorEn(v) {
  v.IntersectionObserver = class {
    constructor(fn) {
      this.fn = fn;
      this.observados = [];
      this.desconectado = false;
      v.creados.push(this);
    }
    observe(e) { this.observados.push(e); }
    unobserve() {}
    disconnect() { this.desconectado = true; }
  };
  return v;
}

/** Un elemento de mentira, con lo que el módulo toca de verdad. */
function elemento(texto = '', clase = '') {
  const clases = new Set(clase.split(' ').filter(Boolean));
  return {
    textContent: texto,
    style: { propiedades: {}, setProperty(k, v) { this.propiedades[k] = v; } },
    classList: {
      add: (...c) => c.forEach((x) => clases.add(x)),
      toggle: (c, on) => (on ? clases.add(c) : clases.delete(c)),
      contains: (c) => clases.has(c),
      lista: clases,
    },
  };
}

function raizCon(mapa) {
  return { querySelectorAll: (selector) => mapa[selector] ?? [] };
}

test('una cifra se descompone respetando la coma decimal española', () => {
  assert.deepEqual(
    { ...cifraDe('3,20'), original: undefined },
    { original: undefined, numero: 3.2, decimales: 2, prefijo: '', sufijo: '' },
  );
  // «1.502» son mil quinientos dos, no uno con quinientos dos. Leerlo al revés convertía la media del
  // grupo en 320.
  assert.equal(cifraDe('1.502').numero, 1502);
  assert.equal(cifraDe('80 %').numero, 80);
  assert.equal(cifraDe('80 %').sufijo, ' %');
});

test('lo que no es un número se deja quieto', () => {
  assert.equal(cifraDe('—'), null);
  assert.equal(cifraDe('sin ganar'), null);
  assert.equal(cifraDe(''), null);
  assert.equal(cifraDe(null), null);
});

test('al terminar, el texto es EXACTAMENTE el que pintó la vista', () => {
  // La regla que no se puede romper: el número que se queda en pantalla es el de la vista, no uno
  // reconstruido. Se comprueba sobre formatos que se reformatean distinto si se pasa por `toLocaleString`.
  for (const original of ['3,20', '1.502', '80 %', '4,31', '0,57', '181', '1,00']) {
    const cifra = cifraDe(original);
    assert.equal(textoDeCifra(cifra, 1), original, `se alteró ${original}`);
    assert.equal(textoDeCifra(cifra, 1.5), original, 'pasarse de 1 tampoco puede alterarlo');
  }
});

test('durante el recorrido la cifra es menor, y conserva prefijo y sufijo', () => {
  const cifra = cifraDe('80 %');

  assert.equal(textoDeCifra(cifra, 0), '0 %');
  assert.ok(textoDeCifra(cifra, 0.5).endsWith(' %'));
  assert.notEqual(textoDeCifra(cifra, 0.5), '80 %');
});

test('el contador acaba en el valor de la vista tras correr los fotogramas', () => {
  const v = conObservadorEn(ventana());
  const kpi = elemento('4,31');
  animar(raizCon({ '.kpi b': [kpi] }), v);
  v.correrFotogramas();

  assert.equal(kpi.textContent, '4,31');
});

test('con movimiento reducido no se anima nada y todo queda en su estado final', () => {
  const v = ventana({ reducido: true });
  const kpi = elemento('4,31');
  const bloque = elemento('', 'revelar');

  animar(raizCon({ '.kpi b': [kpi], '.revelar': [bloque] }), v);

  assert.equal(kpi.textContent, '4,31', 'la cifra no se toca');
  assert.ok(bloque.classList.contains('visible'), 'lo marcado como revelable se muestra igual');
});

test('movimientoReducido lee la preferencia del sistema', () => {
  assert.equal(movimientoReducido(ventana({ reducido: true })), true);
  assert.equal(movimientoReducido(ventana({ reducido: false })), false);
  assert.equal(movimientoReducido({}), false, 'sin matchMedia no se asume nada');
});

test('sin IntersectionObserver la web se ve entera, sin animar', () => {
  const v = ventana();  // sin IntersectionObserver
  const bloque = elemento('', 'revelar');

  animar(raizCon({ '.revelar': [bloque] }), v);

  assert.ok(bloque.classList.contains('visible'));
});

test('el observador de la vista anterior se desconecta al pintar la siguiente', () => {
  // `innerHTML` tira los elementos observados pero no el observador: navegar veinte veces dejaba veinte
  // observadores vivos, cada uno trabajando en cada scroll.
  const v = conObservadorEn(ventana());
  animar(raizCon({ '.bloque': [elemento()] }), v);
  animar(raizCon({ '.bloque': [elemento()] }), v);

  assert.equal(v.creados.length, 2, 'cada render crea el suyo');
  assert.equal(v.creados[0].desconectado, true, 'el de la vista anterior sigue vivo');
  assert.equal(v.creados[1].desconectado, false, 'el actual no debe desconectarse');
});

test('el revelado escalona con tope, para que nada empiece ocho segundos tarde', () => {
  const v = conObservadorEn(ventana());
  const muchos = Array.from({ length: 60 }, () => elemento());

  animar(raizCon({ '.bloque': muchos }), v);

  const retrasos = muchos.map((e) => Number.parseInt(e.style.propiedades['--retraso'], 10));
  assert.equal(retrasos[0], 0);
  assert.ok(retrasos[1] > retrasos[0], 'escalona');
  assert.ok(Math.max(...retrasos) <= 420, `el tope no se respeta: ${Math.max(...retrasos)}`);
});
