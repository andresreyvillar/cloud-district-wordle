/**
 * Lo que el juego del evento calcula en el navegador. **Puro**: el reloj y los datos entran por parámetro (§10).
 *
 * Los colores y lo destapado no se calculan aquí: los pone el servidor, que es el único que conoce la frase.
 */

/** Cuántas palabras tiene cada frase, y cuántas letras cada palabra («La frase del día»). */
export const INTENTOS = 5;
export const LETRAS = 5;

/**
 * La frase visible en palabras y casillas. El servidor manda `_` en cada letra tapada; una letra es una casilla
 * destapada, y cualquier otro carácter, un signo fijo. `«s__ _ _a_»` → tres palabras.
 */
export function celdasDeLaFrase(visible) {
  return String(visible ?? '')
    .split(' ')
    .filter((palabra) => palabra.length > 0)
    .map((palabra) => [...palabra].map((c) => {
      if (c === '_') return { tipo: 'tapada' };
      if (/\p{L}/u.test(c)) return { tipo: 'letra', texto: c };
      return { tipo: 'signo', texto: c };
    }));
}

/** La letra de una tecla, en minúscula y sin tilde; la ñ es otra letra. Cualquier otra cosa, `null`. */
export function letraDeTecla(tecla) {
  if (typeof tecla !== 'string' || [...tecla].length !== 1) return null;
  const letra = tecla.toLowerCase();
  if (letra === 'ñ') return 'ñ';
  const sinTilde = letra.normalize('NFD').replace(/[̀-ͯ]/g, '');
  return /^[a-z]$/.test(sinTilde) ? sinTilde : null;
}

/** Una palabra como la escribiría el servidor: minúsculas, sin tildes, con ñ. */
export function normaliza(palabra) {
  return [...String(palabra ?? '')].map((c) => letraDeTecla(c) ?? '').join('');
}

/**
 * El color de cada tecla: verde si la letra está en la frase (salió verde o amarilla), gris si no está. Una letra
 * que salió verde no vuelve a gris.
 */
export function coloresDelTeclado(intentos) {
  const colores = new Map();
  for (const { palabra, colores: c } of intentos ?? []) {
    [...palabra].forEach((letra, i) => {
      if (c[i] === 'G' || c[i] === 'Y') colores.set(letra, 'G');
      else if (!colores.has(letra)) colores.set(letra, '.');
    });
  }
  return colores;
}

/** «2:41», o «1:02:03» si pasa de la hora. */
export function formatoTiempo(ms) {
  const total = Math.max(0, Math.floor(Number(ms) / 1000));
  const horas = Math.floor(total / 3600);
  const minutos = Math.floor((total % 3600) / 60);
  const segundos = String(total % 60).padStart(2, '0');
  return horas > 0 ? `${horas}:${String(minutos).padStart(2, '0')}:${segundos}` : `${minutos}:${segundos}`;
}

/** Una cuenta atrás. Redondea hacia arriba: «0:00» es que ya llegó. */
export function cuentaAtras(ms) {
  return formatoTiempo(Math.ceil(Math.max(0, Number(ms)) / 1000) * 1000);
}

/** Lo que va el reloj del móvil por detrás del servidor, en milisegundos. */
export function desfase(ahoraDelServidor, relojLocal) {
  const servidor = Date.parse(ahoraDelServidor);
  return Number.isFinite(servidor) ? servidor - relojLocal : 0;
}

/**
 * En qué momento está el evento, con la hora ya corregida al servidor:
 * - `sin-empezar`: el presentador aún no lo ha arrancado.
 * - `en-curso`: `liberadas` son las frases que ya se pueden jugar; `siguiente`, la próxima, que sale en `faltaMs`.
 * - `terminado`: el presentador lo ha terminado.
 */
export function momentoDelEvento(estado, ahora) {
  const frases = estado?.frases ?? [];
  if (estado?.terminado) return { tipo: 'terminado', total: frases.length };
  if (!estado?.empieza_en || frases.length === 0) return { tipo: 'sin-empezar', total: frases.length };
  const liberadas = frases.filter((f) => Date.parse(f.abre_en) <= ahora);
  const siguiente = frases.find((f) => Date.parse(f.abre_en) > ahora) ?? null;
  return {
    tipo: 'en-curso',
    total: frases.length,
    liberadas,
    siguiente,
    faltaMs: siguiente ? Date.parse(siguiente.abre_en) - ahora : null,
  };
}

/** Un token aleatorio con forma de UUID v4. `crypto.randomUUID` solo existe en https, y en local se prueba por http. */
export function tokenAleatorio(aleatorio = (bytes) => crypto.getRandomValues(bytes)) {
  const b = aleatorio(new Uint8Array(16));
  b[6] = (b[6] & 0x0f) | 0x40;
  b[8] = (b[8] & 0x3f) | 0x80;
  const h = [...b].map((x) => x.toString(16).padStart(2, '0')).join('');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}
