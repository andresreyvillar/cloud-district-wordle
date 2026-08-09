/**
 * El movimiento de la web: revelado al hacer scroll, cifras que suben y barras que crecen.
 *
 * Pack: `chore-animaciones` (Slice: N/A — es presentación: los mismos datos, moviéndose).
 *
 * **Nada de esto puede cambiar lo que la web dice.** Una animación que altere una cifra, aunque sea durante
 * 600 ms, convierte el marcador en algo en lo que no se puede confiar. Por eso el contador guarda el texto
 * original y **lo restaura tal cual** al terminar: el valor final es byte a byte el que pintó la vista, no
 * uno reconstruido a partir de un número.
 *
 * **`prefers-reduced-motion` manda.** No es un detalle de accesibilidad opcional: el movimiento de
 * paralaje y las apariciones desplazadas provocan mareo y náusea a quien tiene un trastorno vestibular. Con
 * la preferencia activada esto no se degrada, **se apaga**: los elementos aparecen en su estado final y no
 * se registra ni un observador.
 *
 * Solo se animan `transform` y `opacity`, que el navegador resuelve en el compositor sin recalcular
 * posiciones. Animar `height` o `top` en 181 columnas de dificultad haría trabajar al hilo principal en
 * cada fotograma.
 */

/** Cuánto se retrasa cada elemento de un grupo respecto al anterior, en milisegundos. */
const ESCALON = 45;

/** Tope del retraso acumulado. Sin él, la columna 181 de la temporada 0 empezaría ocho segundos tarde. */
const RETRASO_MAXIMO = 420;

/** Lo que dura la subida de una cifra. Bastante para que se lea como un marcador; poco para no estorbar. */
const DURACION_CIFRA = 900;

/** Qué se revela al entrar en pantalla, y en qué orden dentro de su grupo. */
const REVELABLES = [
  '.bloque',
  '.podio-card',
  '.logro',
  '.temporada-card',
  '.resultado',
  '.hero-texto',
  '.regla',
];

/** Qué cifras suben. Son pocas y visibles: las del HUD, el podio y los totales de la ficha. */
const CIFRAS = ['.kpi b', '.podio-alto .avg', '.album-cifra b', '.ficha .hud b', '.temporada-card .num'];

/**
 * Si la persona ha pedido menos movimiento.
 *
 * Se consulta **en cada render** y no una vez al arrancar: la preferencia del sistema se puede cambiar con
 * la página abierta, y quien la activa a media sesión suele estar haciéndolo porque algo le ha sentado mal.
 */
export function movimientoReducido(ventana = globalThis) {
  return Boolean(ventana.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches);
}

/**
 * El número que hay dentro de un texto, con lo que lo rodea.
 *
 * Se conserva el texto original entero porque es lo que se restaura al final. Devuelve `null` cuando no hay
 * un número que animar —«—», «X/6», «sin ganar»— y entonces ese elemento se deja quieto.
 */
export function cifraDe(texto) {
  const original = String(texto ?? '');
  const encontrado = original.match(/-?\d[\d.,]*/);
  if (!encontrado) return null;

  const crudo = encontrado[0];
  // En español el separador decimal es la coma y el de miles el punto: «1.502» son mil quinientos dos y
  // «3,20» son tres con veinte. Interpretarlo al revés convertía la media del grupo en 320.
  const decimales = crudo.includes(',') ? crudo.split(',')[1].length : 0;
  const numero = Number(crudo.replace(/\./g, '').replace(',', '.'));
  if (!Number.isFinite(numero)) return null;

  return {
    original,
    numero,
    decimales,
    prefijo: original.slice(0, encontrado.index),
    sufijo: original.slice(encontrado.index + crudo.length),
  };
}

/**
 * El texto intermedio de una cifra en una fracción del recorrido.
 *
 * **En la fracción 1 devuelve el original exacto**, sin volver a formatear: cualquier reconstrucción puede
 * diferir en un separador o en un decimal, y el número que se queda en pantalla es el que la gente lee.
 */
export function textoDeCifra(cifra, fraccion) {
  if (fraccion >= 1) return cifra.original;
  const valor = cifra.numero * fraccion;
  const formateado = valor.toLocaleString('es-ES', {
    minimumFractionDigits: cifra.decimales,
    maximumFractionDigits: cifra.decimales,
  });
  return `${cifra.prefijo}${formateado}${cifra.sufijo}`;
}

/** Suavizado de salida: rápido al principio y frenando al final, como un marcador que se para. */
function frenada(t) {
  return 1 - (1 - t) ** 3;
}

function animarCifras(raiz, ventana) {
  for (const selector of CIFRAS) {
    for (const elemento of raiz.querySelectorAll(selector)) {
      const cifra = cifraDe(elemento.textContent);
      if (!cifra || cifra.numero === 0) continue;

      const arranque = ventana.performance?.now?.() ?? 0;
      elemento.textContent = textoDeCifra(cifra, 0);
      const paso = (ahora) => {
        const fraccion = Math.min(1, (ahora - arranque) / DURACION_CIFRA);
        elemento.textContent = textoDeCifra(cifra, frenada(fraccion));
        if (fraccion < 1) ventana.requestAnimationFrame(paso);
      };
      ventana.requestAnimationFrame(paso);
    }
  }
}

function prepararRevelado(raiz, ventana) {
  const observador = new ventana.IntersectionObserver(
    (entradas) => {
      for (const entrada of entradas) {
        if (!entrada.isIntersecting) continue;
        entrada.target.classList.add('visible');
        // Se deja de observar en cuanto aparece: el revelado ocurre una vez, y mantener el observador vivo
        // para cientos de elementos cuesta trabajo en cada scroll sin cambiar nada de lo que se ve.
        observador.unobserve(entrada.target);
      }
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.05 },
  );

  for (const selector of REVELABLES) {
    [...raiz.querySelectorAll(selector)].forEach((elemento, indice) => {
      elemento.classList.add('revelar');
      elemento.style.setProperty('--retraso', `${Math.min(indice * ESCALON, RETRASO_MAXIMO)}ms`);
      observador.observe(elemento);
    });
  }
  return observador;
}

/** El observador de la vista anterior, para desconectarlo antes de pintar la siguiente. */
let observadorActual = null;

/**
 * Pone en marcha el movimiento de una vista recién pintada.
 *
 * Se llama **después de cada render**, y lo primero que hace es desconectar el observador de la vista
 * anterior: `innerHTML` tira los elementos observados, pero no el observador, y navegar veinte veces
 * dejaba veinte observadores vivos.
 */
export function animar(raiz, ventana = globalThis) {
  observadorActual?.disconnect();
  observadorActual = null;
  if (!raiz) return;

  if (movimientoReducido(ventana) || !ventana.IntersectionObserver) {
    // Sin movimiento: todo en su estado final desde el primer fotograma. No se marca nada como `revelar`,
    // así que ni siquiera hay una clase que pudiera dejar algo invisible si algo fallara después.
    for (const elemento of raiz.querySelectorAll('.revelar')) {
      elemento.classList.add('visible');
    }
    return;
  }

  observadorActual = prepararRevelado(raiz, ventana);
  animarCifras(raiz, ventana);
}

/**
 * Marca la cabecera cuando la página no está arriba del todo.
 *
 * Se registra una sola vez, en el arranque, y usa un evento pasivo: un listener de scroll que no puede
 * cancelar el gesto deja que el navegador siga desplazando sin esperar a este código.
 */
export function seguirScroll(documento = globalThis.document, ventana = globalThis) {
  const cabecera = documento.querySelector('.cabecera');
  if (!cabecera) return;
  const mirar = () => cabecera.classList.toggle('desplazada', ventana.scrollY > 8);
  ventana.addEventListener('scroll', mirar, { passive: true });
  mirar();
}
