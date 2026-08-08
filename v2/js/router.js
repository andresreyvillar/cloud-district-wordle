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
 *     /reglas                   las reglas de la temporada en curso
 *     /t/<AAAA-MM>/reglas       las reglas con las que se calculó esa temporada
 *
 * Función **pura**: entra una cadena, sale un objeto. No toca el DOM, no lee `location` y no consulta la
 * red, y por eso se verifica con `node --test` sin navegador.
 *
 * El identificador de jugador es el **identificador de Slack**, no su nombre: un nombre cambia y rompería
 * los enlaces que la gente comparte en el canal (ADR 0006, actualización del 2026-08-05).
 */

/**
 * El prefijo bajo el que se sirve la web, con barra final. `/2/` en producción, y **también `/2/` en local**:
 * si difirieran, los recursos de una ruta profunda (`/2/t/2026-08`) se resolverían contra el sitio
 * equivocado y la parity local-producción se perdería justo donde más duele.
 *
 * Vive en estado de módulo y lo fija el borde (`app.js`, desde `document.baseURI`) en lugar de viajar como
 * parámetro por seis módulos: es un detalle de despliegue, no un dato del dominio, y enhebrarlo por todas
 * las firmas ensuciaría el código del juego para hablar de dónde está montado.
 */
let base = "/";

/** Fija el prefijo. Lo llama el borde una vez, y los tests cuando quieren comprobar el otro caso. */
export function configurarBase(valor) {
  base = valor.endsWith("/") ? valor : `${valor}/`;
}

/** El prefijo actual, con barra final. */
export function baseActual() {
  return base;
}

/** Quita el prefijo de una ruta del navegador. `/2/hoy` → `/hoy`. */
export function sinBase(ruta) {
  const limpia = String(ruta || "/");
  if (base !== "/" && (limpia === base.slice(0, -1) || limpia.startsWith(base))) {
    return `/${limpia.slice(base.length)}`;
  }
  return limpia;
}

/** La ruta de un recurso estático, bajo el prefijo. `assets/icons/x.svg` → `/2/assets/icons/x.svg`. */
export function recurso(relativa) {
  return `${base}${String(relativa).replace(/^\//, "")}`;
}

/** Una temporada es `AAAA-MM` con mes real, o `0` — la temporada histórica. `2026-13` no es una temporada. */
export const TEMPORADA_RE = /^(0|\d{4}-(0[1-9]|1[0-2]))$/;

/** Un identificador de Slack: `U` y mayúsculas, dígitos o guiones bajos. */
export const IDENTIFICADOR_RE = /^U[A-Z0-9_]+$/;

export const VISTAS = Object.freeze({
  TEMPORADA: 'temporada',
  TEMPORADAS: 'temporadas',
  HOY: 'hoy',
  DATOS: 'datos',
  REGLAS: 'reglas',
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
  const segmentos = sinBase(ruta)
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
  if (primero === 'reglas' && resto.length === 0) {
    return { vista: VISTAS.REGLAS, temporada: null };
  }

  if (primero === 't' && TEMPORADA_RE.test(resto[0] || '')) {
    const temporada = resto[0];
    if (resto.length === 1) {
      return { vista: VISTAS.TEMPORADA, temporada };
    }
    if (resto.length === 3 && resto[1] === 'j' && IDENTIFICADOR_RE.test(resto[2])) {
      return { vista: VISTAS.JUGADOR, temporada, jugador: resto[2] };
    }
    // Las reglas viven dentro del eje de la temporada: una cerrada conserva las que se le aplicaron, y sin
    // la temporada en la ruta ese escenario es inalcanzable.
    if (resto.length === 2 && resto[1] === 'reglas') {
      return { vista: VISTAS.REGLAS, temporada };
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
  return conBase(_rutaInterna(destino));
}

/** La ruta con el prefijo puesto. `/hoy` → `/2/hoy`, y `/` → `/2/`. */
export function conBase(interna) {
  const limpia = String(interna).replace(/^\//, "");
  return `${base}${limpia}`;
}

function _rutaInterna(destino) {
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
    case VISTAS.REGLAS:
      return destino.temporada ? `/t/${destino.temporada}/reglas` : '/reglas';
    default:
      return '/';
  }
}
