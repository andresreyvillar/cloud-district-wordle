/**
 * El Worker que sirve las dos webs desde un solo host.
 *
 *     /            → la v1 (assets de la raíz del repo), como hasta ahora
 *     /2/…         → la v2 (assets de v2/), con su fallback de SPA
 *
 * **Este script solo se ejecuta en las rutas que NO encajan con ningún asset.** Es una propiedad de Workers
 * Static Assets, y es lo que hace que este cambio sea seguro para la v1: `/`, `/index.html`, `/js/script.js`
 * y todo lo demás de la v1 se siguen sirviendo sin pasar por aquí. Un fallo en este código no puede tirar la
 * web que el grupo usa a diario; como mucho rompe `/2/`.
 *
 * El mapeo `/2/… → /v2/…` existe porque el directorio de assets es la raíz del repositorio, así que la URL
 * de un asset es su ruta en el repo. Renombrar `v2/` a `2/` daría la URL directa, pero `v2/` está escrito en
 * decenas de specs, slices y documentos: se prefiere una reescritura de tres líneas a un renombrado masivo.
 *
 * Consecuencia declarada: la v2 queda también accesible en `/v2/…`, porque esas rutas encajan con un asset y
 * este script no llega a verlas. Es una URL duplicada, no un agujero: los mismos ficheros públicos.
 */

/** El prefijo público de la v2, con barra final. Coincide con el `<base href>` de `v2/index.html`. */
const PREFIJO = '/2/';

/** Dónde viven de verdad esos ficheros en el repositorio. */
const INTERNO = '/v2/';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // `/2` sin barra: se redirige en lugar de servir, para que las rutas relativas del `<base>` resuelvan
    // contra `/2/` y no contra la raíz.
    if (url.pathname === PREFIJO.slice(0, -1)) {
      return Response.redirect(`${url.origin}${PREFIJO}`, 301);
    }

    if (url.pathname.startsWith(PREFIJO)) {
      const interna = new URL(`${INTERNO}${url.pathname.slice(PREFIJO.length)}`, url);
      const respuesta = await env.ASSETS.fetch(new Request(interna, request));
      if (respuesta.status !== 404) return respuesta;

      // Fallback de SPA, y **solo para la v2**: cualquier ruta de la v2 que no sea un fichero devuelve su
      // index para que el router la resuelva en el cliente. Antes esto era
      // `not_found_handling: single-page-application`, que aplicaba al Worker entero y habría hecho que una
      // ruta inexistente de la v1 devolviera una página con 200.
      return env.ASSETS.fetch(new Request(new URL(`${INTERNO}index.html`, url), request));
    }

    // La v1: se delega tal cual, incluido su 404.
    return env.ASSETS.fetch(request);
  },
};
