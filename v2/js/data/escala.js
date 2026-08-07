/**
 * Las escalas de los gráficos. **Fijas, para que dos gráficos del mismo tipo se puedan comparar.**
 *
 * Slice: `escala-fija-comparable` (openspec/slices/dashboard/escala-fija-comparable.md).
 *
 * Un gráfico autoescalado no miente en sus números, pero miente en lo que sugiere de un vistazo, que es
 * como se leen. Con la dificultad escalada al máximo del propio mes, uno cuya jornada más dura fue un 4,2 se
 * veía exactamente igual de dramático que otro que llegó a 6,0.
 */

/** El rango real de una puntuación: 1 es lo mejor posible y 7 es el fallo. La v1 ya lo usaba en su gráfica. */
export const ESCALA_DE_INTENTOS = Object.freeze({ minimo: 1, maximo: 7 });

/** Altura mínima visible, en tanto por ciento. Una barra de cero se lee como que no hay dato. */
const MINIMO_VISIBLE = 2;

function recortar(valor, minimo, maximo) {
  return Math.min(maximo, Math.max(minimo, valor));
}

/**
 * La altura de una barra de intentos, en tanto por ciento de la escala fija.
 *
 * Los valores fuera de rango se recortan: un dato malo no puede desbordar el marco del gráfico.
 */
export function alturaDeIntentos(intentos) {
  const { minimo, maximo } = ESCALA_DE_INTENTOS;
  const acotado = recortar(intentos, minimo, maximo);
  const proporcion = (acotado - minimo) / (maximo - minimo);
  return Math.max(MINIMO_VISIBLE, Math.round(proporcion * 100));
}

alturaDeIntentos.leyenda = 'escala fija de 1 a 7 intentos';

/**
 * La escala común de las distribuciones de una temporada: el mayor recuento de cualquier jugador.
 *
 * Es el eje compartido de un conjunto de gráficos pequeños. Con él, el mejor lleno toca el techo y el resto
 * se mide contra él; sin él, quien jugó diez partidas y quien jugó cien dibujan la misma silueta.
 */
export function escalaDeDistribucion(clasificacion) {
  const recuentos = (clasificacion ?? []).flatMap((fila) => fila.distribucion ?? []);
  return Math.max(1, ...recuentos);
}

escalaDeDistribucion.leyenda = (escala) => `escala común: hasta ${escala} partidas`;

/** La altura de un recuento sobre una escala dada, recortada a [0, 100]. Una escala de 0 no da infinito. */
export function alturaEnEscala(valor, escala) {
  if (!escala || escala <= 0) return 0;
  return recortar(Math.round((valor / escala) * 100), 0, 100);
}
