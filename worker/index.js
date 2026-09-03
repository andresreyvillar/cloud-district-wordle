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

      // Se cae al index **solo** si el fichero no existe (404) o si los assets responden con una
      // redirección de normalización (3xx). Todo lo demás se devuelve tal cual.
      //
      // Las dos condiciones salieron de producción, y las dos por separado:
      //
      // - devolver la 3xx tal cual mandaba al navegador a `/v2/`, filtrando la ruta interna y perdiendo la
      //   de la v2;
      // - exigir exactamente 200 rompía la **segunda** visita: el navegador manda una petición condicional
      //   con el módulo ya en caché, los assets contestan **304 Not Modified**, y eso se tomaba por "no
      //   existe", así que `/2/js/app.js` devolvía el index como si fuera JavaScript. La web solo fallaba
      //   si ya la habías abierto antes, que es el caso de todo el que la use a diario.
      // 304 está en el rango 3xx y **no es una redirección**: es "usa tu caché". Meterlo en el rango
      // reintroducía el fallo que este código acaba de arreglar.
      const REDIRECCIONES = [301, 302, 303, 307, 308];
      const esRedireccion = REDIRECCIONES.includes(respuesta.status);
      if (respuesta.status !== 404 && !esRedireccion) return respuesta;

      // Fallback de SPA, y **solo para la v2**: cualquier ruta de la v2 que no sea un fichero devuelve su
      // index para que el router la resuelva en el cliente. Se pide el directorio y no `index.html` porque
      // es la forma canónica: pedir el fichero dispara la misma normalización que causó el fallo anterior.
      return env.ASSETS.fetch(new Request(new URL(INTERNO, url), request));
    }

    // La v1: se delega tal cual, incluido su 404.
    return env.ASSETS.fetch(request);
  },

  /**
   * El **reloj de repuesto** del pipeline: cada hora despierta el workflow de datos de GitHub.
   *
   * Existe porque el planificador de GitHub no garantiza nada. Su documentación lo dice —«algunos trabajos en
   * cola pueden descartarse»— y este repositorio lo ha medido: de 24 ejecuciones diarias esperadas salían
   * entre 5 y 6, con huecos de 3 a 6 horas. Se probó lo único que GitHub recomienda, mover el cron fuera del
   * minuto en punto, y empeoró; se revirtió y siguió igual. Los cron de Workers sí son fiables, y este Worker
   * ya estaba desplegado, así que el reloj se cambia de sitio en lugar de añadir un proveedor.
   *
   * **No duplica trabajo.** `workflow_dispatch` lanza el mismo workflow que el cron de GitHub, y el pipeline
   * es idempotente: la ingesta no reescribe resultados ya guardados y la materialización hace `upsert`. Si
   * las dos ventanas coinciden, la segunda recalcula lo mismo.
   *
   * **Falla en silencio y a propósito.** Un error aquí no puede afectar a la web: es un `scheduled` aparte de
   * `fetch`, así que ni comparte camino ni puede tirar lo que el grupo usa a diario. Sin `GITHUB_TOKEN`
   * configurado no hace nada, que es el estado por defecto.
   */
  async scheduled(evento, env, contexto) {
    if (!env.GITHUB_TOKEN) {
      console.log('sin GITHUB_TOKEN: el disparador está apagado');
      return;
    }
    contexto.waitUntil(despierta(env));
  },
};

/** El workflow que se despierta y en qué rama. Van juntos: despertar otro en otra rama no es un caso de uso. */
const WORKFLOW = 'update_stats.yml';
const RAMA = 'main';
const REPO = 'andresreyvillar/cloud-district-wordle';

async function despierta(env) {
  const url = `https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`;
  try {
    const respuesta = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.GITHUB_TOKEN}`,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        // GitHub exige User-Agent y responde 403 sin él.
        'User-Agent': 'cloud-district-wordle-cron',
      },
      body: JSON.stringify({ ref: RAMA }),
    });
    // 204 es el éxito de este endpoint: acepta y no devuelve cuerpo.
    if (respuesta.status !== 204) {
      console.error(`dispatch devolvió ${respuesta.status}: ${await respuesta.text()}`);
      return;
    }
    console.log(`${WORKFLOW} despertado en ${RAMA}`);
  } catch (error) {
    console.error(`no se pudo despertar ${WORKFLOW}: ${error}`);
  }
}
