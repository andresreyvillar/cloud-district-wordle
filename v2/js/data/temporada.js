/**
 * A qué temporada pertenece una fecha. **Una sola definición para toda la web.**
 *
 * Existe porque el mismo error se ha cometido ya dos veces: derivar la temporada comparando el prefijo de la
 * fecha. Funcionaba mientras toda temporada era un `AAAA-MM`; con la temporada 0 rompe **en silencio**, y las
 * dos veces el síntoma fue un agregado con una cifra absurda —cero medallas en 181 jornadas, y 70 filas de
 * 1543 «contando»— en lugar de una excepción.
 *
 * El límite **no se escribe aquí**: se lee de las reglas que viajan dentro de la instantánea, que salen de
 * `seasons.INICIO_TEMPORADAS`. Escribirlo en JavaScript sería la tercera copia del mismo dato.
 */

/** La regla del catálogo que publica el límite (`tools/rules.py`). */
const REGLA_DEL_LIMITE = 'temporada-cero';

/** El identificador de la temporada histórica. El mismo que `seasons.TEMPORADA_CERO`. */
export const TEMPORADA_CERO = '0';

/** El mes en que empiezan las temporadas numeradas, según las reglas publicadas, o `null` si no vienen. */
export function limiteDeTemporadas(reglas) {
  const regla = (reglas ?? []).find((r) => r.id === REGLA_DEL_LIMITE);
  const parametro = (regla?.parametros ?? []).find((p) => typeof p.valor === 'string');
  return parametro ? parametro.valor : null;
}

/** Las reglas publicadas, tomadas de cualquier instantánea: todas llevan el mismo catálogo. */
export function reglasDe(instantaneas) {
  for (const carga of instantaneas.values()) {
    if (carga?.reglas?.length) return carga.reglas;
  }
  return [];
}

/**
 * La temporada de una fecha: `0` si es anterior al límite, su `AAAA-MM` si no.
 *
 * Sin límite conocido devuelve `null`: no se puede afirmar a qué temporada pertenece algo cuando no se sabe
 * dónde está la frontera, y suponerla es lo que produjo los dos fallos silenciosos.
 */
export function temporadaDe(fecha, limite) {
  if (!limite) return null;
  const mes = String(fecha).slice(0, 7);
  return mes < limite ? TEMPORADA_CERO : mes;
}
