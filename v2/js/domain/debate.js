/**
 * El recuento de una votación del debate de reglas. Slice `debate-de-reglas`. **Puro**: entra lo leído, sale
 * el recuento.
 */

/**
 * Cada opción con sus votantes y su total, en el orden de la votación. Si una persona aparece dos veces, cuenta
 * su último voto: la tabla ya lo garantiza con su clave, y aquí se repite para que el recuento no dependa de ello.
 */
export function recuento(votacion, votos) {
  const ultimo = new Map();
  for (const voto of votos ?? []) {
    if (voto?.votacion === votacion?.id) ultimo.set(voto.votante, voto.opcion);
  }
  return (votacion?.opciones ?? []).map(({ id, texto }) => {
    const votantes = [...ultimo].filter(([, opcion]) => opcion === id).map(([votante]) => votante);
    return { id, texto, votantes, total: votantes.length };
  });
}

/** Quién está a favor y quién en contra de una propuesta. Como en `recuento`, cuenta el último voto de cada uno. */
export function apoyos(propuesta, votos) {
  const ultimo = new Map();
  for (const voto of votos ?? []) {
    if (voto?.propuesta === propuesta?.id) ultimo.set(voto.votante, voto.voto);
  }
  const de = (sentido) => [...ultimo].filter(([, voto]) => voto === sentido).map(([votante]) => votante);
  return { a_favor: de('a_favor'), en_contra: de('en_contra') };
}
