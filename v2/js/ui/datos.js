/**
 * La tabla cruda.
 *
 * Slice: `tabla-de-datos` (openspec/slices/dashboard/tabla-de-datos.md).
 *
 * Se porta de la v1 tal cual —fecha, jugador, jornada, intentos, de la más reciente a la más antigua— con
 * una columna que allí no cabía: si esa fila cuenta para su temporada. Es la vista que permite comprobar
 * que el ranking no se ha inventado nada, así que vuelca **todas** las filas.
 */

import { filasDeDatos } from '../data/tabla.js';
import { escapar } from './shell.js';

const MOTIVOS = {
  muestra: 'ese día no llegó al mínimo de jugadores',
  'fin de semana': 'fin de semana',
};

export function pintarDatos(contenedor, resultados, instantaneas) {
  const filas = filasDeDatos(resultados, instantaneas);

  if (!filas.length) {
    contenedor.innerHTML = `
      <section class="vacio">
        <h1>Sin datos</h1>
        <p class="serif">No hay ningún resultado guardado todavía.</p>
      </section>`;
    return;
  }

  const cuentan = filas.filter((f) => f.cuenta === true).length;
  const fuera = filas.filter((f) => f.cuenta === false).length;

  const cuerpo = filas
    .map((f) => {
      const marca = f.cuenta === null
        ? '<span class="sin-dato" title="La temporada de esta fila no está materializada">—</span>'
        : f.cuenta
          ? '<span class="si">cuenta</span>'
          : `<span class="no" title="${escapar(MOTIVOS[f.motivo] ?? '')}">no · ${escapar(f.motivo ?? '')}</span>`;
      return `
        <tr${f.cuenta === false ? ' class="descartada"' : ''}>
          <td class="mono">${escapar(f.fecha)}</td>
          <td>${escapar(f.nombre)}</td>
          <td class="mono">#${f.jornada}</td>
          <td class="mono der${f.fallo ? ' fallo' : ''}">${escapar(f.marca)}</td>
          <td>${marca}</td>
        </tr>`;
    })
    .join('');

  contenedor.innerHTML = `
    <section class="datos">
      <header class="titular">
        <div>
          <h1>Datos</h1>
          <p class="serif">${filas.length} resultados guardados · ${cuentan} cuentan para su temporada ·
            ${fuera} no</p>
        </div>
      </header>

      <p class="nota">Es la tabla en bruto, sin cálculo de por medio: sirve para comprobar que el marcador no
        se ha inventado nada. Una fila que no cuenta se guarda igual y se puede mirar; lo que no hace es
        puntuar.</p>

      <div class="tabla-cruda">
        <table>
          <thead>
            <tr><th>Fecha</th><th>Jugador</th><th>Jornada</th><th class="der">Intentos</th><th>¿Cuenta?</th></tr>
          </thead>
          <tbody>${cuerpo}</tbody>
        </table>
      </div>
    </section>`;
}
