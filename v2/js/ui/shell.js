/**
 * El armazón: cabecera, navegación, selector de temporada y contenedor de vista.
 *
 * Toca el DOM, así que aquí no hay cálculo. Cada vista real llegará con su slice y se limitará a rellenar
 * el contenedor que este módulo prepara.
 */

import { VISTAS, conBase, rutaDe, seccionDe } from '../router.js';

const SECCIONES = [
  { vista: VISTAS.TEMPORADA, etiqueta: 'Temporada' },
  { vista: VISTAS.TEMPORADAS, etiqueta: 'Temporadas' },
  { vista: VISTAS.HOY, etiqueta: 'Hoy' },
  { vista: VISTAS.DATOS, etiqueta: 'Datos' },
  { vista: VISTAS.REGLAS, etiqueta: 'Reglas' },
];

/** Escapa lo que venga de datos antes de meterlo en el DOM. Nombres de jugador incluidos. */
export function escapar(valor) {
  return String(valor ?? '').replace(/[&<>"']/g, (caracter) => {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[caracter];
  });
}

/** Pinta la navegación y marca la sección que contiene la vista actual. */
export function pintarNavegacion(contenedor, destino) {
  const activa_ = seccionDe(destino.vista);
  contenedor.innerHTML = SECCIONES.map((seccion) => {
    const activa = seccion.vista === activa_ ? ' aria-current="page"' : '';
    // `destino.temporada` es la efectiva, así que los enlaces conservan la temporada que se está mirando.
    const ruta = rutaDe({ vista: seccion.vista, temporada: destino.temporada });
    return `<a href="${ruta}"${activa}>${seccion.etiqueta}</a>`;
  }).join('');
}

/**
 * Pinta el selector de temporada. `temporadas` viene ordenada de más reciente a más antigua, y cada entrada
 * trae su identificador y su etiqueta ("Temporada 1 · agosto 2026").
 *
 * La opción vacía es "la en curso", que es lo que representa la ruta `/`.
 */
export function pintarSelector(selector, temporadas, actual) {
  selector.innerHTML =
    `<option value=""${actual ? '' : ' selected'}>En curso</option>` +
    temporadas
      .map(({ id, etiqueta }) => {
        const marca = id === actual ? ' selected' : '';
        return `<option value="${escapar(id)}"${marca}>${escapar(etiqueta)}</option>`;
      })
      .join('');
}

/**
 * Marcador de posición de una vista todavía sin implementar.
 *
 * Existe para que el esqueleto sea comprobable: al abrir una ruta se ve **qué vista se resolvió y con qué
 * parámetros**, que es justo lo que este pack tiene que demostrar. Cada slice lo sustituye por lo suyo.
 */
export function pintarPendiente(contenedor, destino, slice) {
  const parametros = Object.entries(destino)
    .filter(([clave]) => clave !== 'vista')
    .map(([clave, valor]) => `<code>${escapar(clave)}: ${escapar(valor ?? '—')}</code>`)
    .join(' · ');

  contenedor.innerHTML = `
    <section class="pendiente">
      <p class="etiqueta">vista resuelta</p>
      <h2>${escapar(destino.vista)}</h2>
      ${parametros ? `<p class="parametros">${parametros}</p>` : ''}
      <p class="nota">Esta vista llega con el slice <strong>${escapar(slice)}</strong>.</p>
    </section>`;
}

/** La vista de una ruta que no existe. La definitiva llega con el slice `ruta-invalida`. */
export function pintarDesconocida(contenedor, destino) {
  contenedor.innerHTML = `
    <section class="pendiente">
      <p class="etiqueta">ruta no reconocida</p>
      <h2>${escapar(destino.ruta ?? '')}</h2>
      <p class="nota">Con el fallback SPA no hay 404, así que esto lo detecta el cliente.
      <a href="${conBase('/')}">Volver a la temporada en curso</a>.</p>
    </section>`;
}

/** El estado de carga y el de error, que son del armazón porque los comparten todas las vistas. */
export function pintarCargando(contenedor) {
  contenedor.innerHTML = '<section class="pendiente"><p class="nota">Cargando resultados…</p></section>';
}

export function pintarError(contenedor, mensaje) {
  contenedor.innerHTML = `
    <section class="pendiente error">
      <p class="etiqueta">no se han podido cargar los datos</p>
      <p class="nota">${escapar(mensaje)}</p>
    </section>`;
}
