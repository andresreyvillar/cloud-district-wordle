/**
 * Lo que el juego del evento calcula en el navegador. **Puro**: el reloj y los datos entran por parámetro (§10).
 *
 * Los colores no se calculan aquí: los pone el servidor, que es el único que conoce la palabra.
 */

/** Intentos por palabra y letras por intento: el Wordle de siempre. */
export const INTENTOS = 6;
export const LETRAS = 5;

/** La letra de una tecla, en minúscula y sin tilde; la ñ es otra letra. Cualquier otra cosa, `null`. */
export function letraDeTecla(tecla) {
  if (typeof tecla !== 'string' || [...tecla].length !== 1) return null;
  const letra = tecla.toLowerCase();
  if (letra === 'ñ') return 'ñ';
  const sinTilde = letra.normalize('NFD').replace(/[̀-ͯ]/g, '');
  return /^[a-z]$/.test(sinTilde) ? sinTilde : null;
}

/** Un texto como lo compara el servidor: minúsculas, sin tildes, con ñ y sin espacios de sobra. */
export function normaliza(texto) {
  return String(texto ?? '').trim().toLowerCase().normalize('NFD').replace(/ñ/g, 'ñ')
    .replace(/[̀-ͯ]/g, '').replace(/\s+/g, ' ');
}

/**
 * El color de cada tecla, como en el Wordle: verde si alguna vez salió verde, amarilla si salió amarilla y nunca
 * verde, gris si solo salió gris. Una letra no baja de color.
 */
export function coloresDelTeclado(intentos) {
  const rango = { G: 3, Y: 2, '.': 1 };
  const colores = new Map();
  for (const { palabra, colores: c } of intentos ?? []) {
    [...palabra].forEach((letra, i) => {
      if ((rango[c[i]] ?? 0) > (rango[colores.get(letra)] ?? 0)) colores.set(letra, c[i]);
    });
  }
  return colores;
}

/**
 * Los nombres de la lista que encajan con lo escrito, sin mayúsculas ni tildes, y con los libres primero. Sin nada
 * escrito, todos: es el desplegable. Al buscar, la ñ también vale como n: quien escribe «inigo» busca a Íñigo.
 */
export function buscarNombres(nombres, texto) {
  const pliega = (x) => normaliza(x).replace(/ñ/g, 'n');
  const busca = pliega(texto);
  return (nombres ?? [])
    .filter((n) => pliega(n.nombre).includes(busca))
    .sort((a, b) => Number(b.libre) - Number(a.libre));
}

/** «2:41», o «1:02:03» si pasa de la hora. */
export function formatoTiempo(ms) {
  const total = Math.max(0, Math.floor(Number(ms) / 1000));
  const horas = Math.floor(total / 3600);
  const minutos = Math.floor((total % 3600) / 60);
  const segundos = String(total % 60).padStart(2, '0');
  return horas > 0 ? `${horas}:${String(minutos).padStart(2, '0')}:${segundos}` : `${minutos}:${segundos}`;
}

/** Lo que va el reloj del móvil por detrás del servidor, en milisegundos. */
export function desfase(ahoraDelServidor, relojLocal) {
  const servidor = Date.parse(ahoraDelServidor);
  return Number.isFinite(servidor) ? servidor - relojLocal : 0;
}

/**
 * Por dónde va un participante, a partir de sus rondas (`orden` → ronda) y del total de palabras:
 * - `empezar`: aún no ha empezado ninguna; toca la 1.
 * - `jugando`: tiene la ronda `orden` empezada y sin terminar.
 * - `entre`: terminó la `orden` y la siguiente (`orden + 1`) está por empezar.
 * - `fin`: terminó todas.
 */
export function puntoDelJuego(rondas, total) {
  const empezadas = [...(rondas?.values?.() ?? [])].sort((a, b) => a.orden - b.orden);
  const ultima = empezadas.at(-1);
  if (!ultima) return { tipo: 'empezar', orden: 1 };
  if (!ultima.terminada_en) return { tipo: 'jugando', orden: ultima.orden };
  if (ultima.orden >= total) return { tipo: 'fin', orden: ultima.orden };
  return { tipo: 'entre', orden: ultima.orden };
}

/** Un token aleatorio con forma de UUID v4. `crypto.randomUUID` solo existe en https, y en local se prueba por http. */
export function tokenAleatorio(aleatorio = (bytes) => crypto.getRandomValues(bytes)) {
  const b = aleatorio(new Uint8Array(16));
  b[6] = (b[6] & 0x0f) | 0x40;
  b[8] = (b[8] & 0x3f) | 0x80;
  const h = [...b].map((x) => x.toString(16).padStart(2, '0')).join('');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}
