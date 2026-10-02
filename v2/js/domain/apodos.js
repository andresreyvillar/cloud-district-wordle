/**
 * Los apodos de la web: cómo se pinta a un jugador, no quién es.
 *
 * Slice: `apodos-en-la-web`. **Es presentación.** La identidad sigue siendo el id de Slack —rutas de la ficha,
 * selector del juego, marcas—, así que el apodo se aplica solo al pintar, nunca al cargar los datos: los
 * cruces por nombre (medallas, archivo) seguirían viendo el nombre de verdad y se romperían.
 *
 * Solo la web: el bot de Slack nombra a todos por su nombre (decisión del dueño). Para quitar un apodo se
 * borra su línea.
 */

/** Tacha un texto con U+0336 tras cada letra: es texto plano, así que vale en HTML, en un `<option>` y en el lienzo. */
function tachar(texto) {
  return [...texto].map((letra) => `${letra}̶`).join('');
}

/** El apodo de cada jugador, por su nombre de Slack. Declarado por el dueño. */
export const APODOS = {
  // Juega estos días con ayuda de ChatGPT (2026-10-02).
  Carrillo: `${tachar('Carrillo')} ChatGPT`,
};

/** Lo que se pinta por un nombre: su apodo, si lo tiene; si no, el nombre tal cual. */
export function nombreVisible(nombre) {
  return Object.hasOwn(APODOS, nombre) ? APODOS[nombre] : nombre;
}

/**
 * La etiqueta de un tramo del nivel con el apodo. `nivelDe` la escribe como «nombre  nota/6», con dos espacios:
 * se cambia solo el nombre entero que va delante de ellos.
 */
export function etiquetaVisible(texto) {
  const corte = String(texto).lastIndexOf('  ');
  if (corte < 0) return texto;
  return nombreVisible(texto.slice(0, corte)) + texto.slice(corte);
}

/** Una copia del nivel congelado con las etiquetas apodadas, para el motor. El nivel guardado no cambia. */
export function nivelConApodos(nivel) {
  if (!nivel) return nivel;
  return { ...nivel, labels: (nivel.labels ?? []).map((l) => ({ ...l, text: etiquetaVisible(l.text) })) };
}
