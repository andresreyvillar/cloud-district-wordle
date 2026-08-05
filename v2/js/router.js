/**
 * Router de la v2.0: ruta → vista y parámetros.
 *
 * Mapa de rutas del ADR 0006:
 *
 *     /                         temporada en curso
 *     /t/<AAAA-MM>              temporada concreta
 *     /t/<AAAA-MM>/j/<U…>       jugador dentro de esa temporada
 *     /temporadas               archivo + medallero
 *     /hoy                      el día en curso
 *     /datos                    tabla cruda
 *
 * Función **pura**: entra una cadena, sale un objeto. No toca el DOM, no lee `location` y no consulta la
 * red, y por eso se verifica con `node --test` sin navegador.
 *
 * El identificador de jugador es el **identificador de Slack**, no su nombre: un nombre cambia y rompería
 * los enlaces que la gente comparte en el canal (ADR 0006, actualización del 2026-08-05).
 */

/** Una temporada es `AAAA-MM` con mes real: `2026-13` no es una temporada. */
export const TEMPORADA_RE = /^\d{4}-(0[1-9]|1[0-2])$/;

/** Un identificador de Slack: `U` y mayúsculas, dígitos o guiones bajos. */
export const IDENTIFICADOR_RE = /^U[A-Z0-9_]+$/;

export const VISTAS = Object.freeze({
  TEMPORADA: 'temporada',
  TEMPORADAS: 'temporadas',
  HOY: 'hoy',
  DATOS: 'datos',
  JUGADOR: 'jugador',
  DESCONOCIDA: 'desconocida',
});

/**
 * Resuelve una ruta.
 *
 * `temporada: null` en la vista de temporada significa **la en curso**, y se resuelve en el borde con los
 * datos: el router no sabe qué día es hoy, a propósito (§10 del protocolo).
 *
 * Una ruta que no encaja devuelve `DESCONOCIDA` en lugar de lanzar. Con el fallback SPA del Worker el 404
 * desaparece —cualquier ruta devuelve el documento con 200— así que detectarla es cosa del cliente.
 */
export function resolver(ruta) {
  const segmentos = String(ruta || '/')
    .split('?')[0]
    .split('#')[0]
    .split('/')
    .filter((segmento) => segmento.length > 0);

  if (segmentos.length === 0) {
    return { vista: VISTAS.TEMPORADA, temporada: null };
  }

  const [primero, ...resto] = segmentos;

  if (primero === 'temporadas' && resto.length === 0) {
    return { vista: VISTAS.TEMPORADAS };
  }
  if (primero === 'hoy' && resto.length === 0) {
    return { vista: VISTAS.HOY };
  }
  if (primero === 'datos' && resto.length === 0) {
    return { vista: VISTAS.DATOS };
  }

  if (primero === 't' && TEMPORADA_RE.test(resto[0] || '')) {
    const temporada = resto[0];
    if (resto.length === 1) {
      return { vista: VISTAS.TEMPORADA, temporada };
    }
    if (resto.length === 3 && resto[1] === 'j' && IDENTIFICADOR_RE.test(resto[2])) {
      return { vista: VISTAS.JUGADOR, temporada, jugador: resto[2] };
    }
  }

  return { vista: VISTAS.DESCONOCIDA, ruta: `/${segmentos.join('/')}` };
}

/**
 * La sección de navegación que **contiene** una vista.
 *
 * El jugador vive dentro de una temporada (`/t/<AAAA-MM>/j/<U…>`), así que la sección activa mientras se
 * mira una ficha es Temporada. Sin esto, la ficha de jugador no marcaba ninguna sección y la navegación
 * parecía apagada — lo cazó el navegador, no un unitario.
 *
 * Una ruta desconocida no pertenece a ninguna sección, y devuelve `null` a propósito.
 */
export function seccionDe(vista) {
  if (vista === VISTAS.JUGADOR) return VISTAS.TEMPORADA;
  if (vista === VISTAS.DESCONOCIDA) return null;
  return vista;
}

/** La ruta canónica de una vista. Es la inversa de `resolver`, y sirve para construir enlaces. */
export function rutaDe(destino) {
  switch (destino.vista) {
    case VISTAS.TEMPORADA:
      return destino.temporada ? `/t/${destino.temporada}` : '/';
    case VISTAS.JUGADOR:
      return `/t/${destino.temporada}/j/${destino.jugador}`;
    case VISTAS.TEMPORADAS:
      return '/temporadas';
    case VISTAS.HOY:
      return '/hoy';
    case VISTAS.DATOS:
      return '/datos';
    default:
      return '/';
  }
}
