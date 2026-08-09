/**
 * El archivo de temporadas: el palmarés colectivo.
 *
 * Slice: `archivo-de-temporadas` (openspec/slices/ranking/archivo-de-temporadas.md).
 *
 * Es la vista que da sentido a reiniciar el marcador cada mes: sin archivo, ganar agosto no deja rastro en
 * septiembre. Hoy tiene dos filas y crecerá una al mes.
 */

import { archivo, medallero } from '../data/archivo.js';
import { rutaDeFicha } from '../data/ficha.js';
import { escapar } from './shell.js';

const LOGROS = {
  suertudo: 'Suertud@',
  'dia-imposible': 'El día imposible',
  superviviente: 'Superviviente',
  metronomo: 'Metrónom@',
  verdugo: 'Verdugo',
  impecable: 'Impecable',
  fondista: 'Fondista',
};

function cifra(valor, decimales = 2) {
  return typeof valor === 'number'
    ? valor.toLocaleString('es-ES', { minimumFractionDigits: decimales, maximumFractionDigits: decimales })
    : String(valor ?? '—');
}

function tarjeta(t) {
  const quien = t.campeon ?? t.lider;
  const corona = t.campeon
    ? `<span class="pixel resalte">CAMPEÓN</span>`
    : '<span class="pixel">VA GANANDO</span>';

  const nombre = quien
    ? `<a class="ganador" href="${escapar(rutaDeFicha(t.temporada, quien.jugador))}">${escapar(quien.nombre)}</a>
       <span class="media">${escapar(cifra(quien.media_temporada))}</span>`
    : '<span class="ganador vacia">sin campeón</span>';

  return `
    <article class="temporada-card${t.cerrada ? '' : ' abierta'}${t.historica ? ' historica' : ''}">
      <header>
        <a class="etiqueta" href="${escapar(t.ruta)}">${escapar(t.etiqueta)}</a>
        <span class="estado">${escapar(t.estado ?? '')}</span>
      </header>
      ${t.historica ? '<p class="marca-historica">Bloque histórico · se jugó con otras reglas, sin imputar ausencias</p>' : ''}
      <div class="campeon">${corona}<div class="quien">${nombre}</div></div>
      <dl class="totales">
        <div><dt>Jornadas</dt><dd>${t.jornadas}</dd></div>
        <div><dt>Jugadores</dt><dd>${t.jugadores}</dd></div>
        <div><dt>Resultados</dt><dd>${t.resultados}</dd></div>
        <div><dt>Media grupo</dt><dd>${escapar(cifra(t.media_grupo))}</dd></div>
      </dl>
      ${t.jornadas === 0 ? '<p class="nota">Ningún día llegó a la muestra mínima. La temporada existe y está vacía.</p>' : ''}
    </article>`;
}

function medalleroBloque(tabla) {
  if (!tabla.length) {
    return `
      <section class="bloque">
        <header class="bloque-cab"><h2>MEDALLERO</h2><span>vacío</span></header>
        <p class="nota">Todavía no hay medallas repartidas.</p>
      </section>`;
  }
  const filas = tabla
    .map(
      (f) => `
      <div class="fila">
        ${f.jugador
          ? `<a class="nom" href="${escapar(rutaDeFicha(f.temporada, f.jugador))}">${escapar(f.nombre)}</a>`
          : `<span class="nom sin-ficha">${escapar(f.nombre)}</span>`}
        <span class="detalle">${Object.entries(f.por_clave)
          .map(([clave, n]) => `${escapar(LOGROS[clave] ?? clave)}${n > 1 ? ` ×${n}` : ''}`)
          .join(' · ')}</span>
        <span class="num suave">${f.temporadas_ganadas || '—'}</span>
        <span class="num fuerte">${f.medallas}</span>
      </div>`,
    )
    .join('');
  return `
    <section class="bloque">
      <header class="bloque-cab"><h2>MEDALLERO</h2>
        <span>acumulado de todas las temporadas</span></header>
      <div class="cabeza cuatro-med">
        <span>Jugador</span><span>Medallas</span><span class="der">Temporadas</span><span class="der">Total</span>
      </div>
      ${filas}
      <p class="nota">Las medallas se recalculan a partir de los resultados, así que recalibrar un umbral
        ajusta este medallero solo. «Temporadas» cuenta las que ganó ya cerradas.</p>
    </section>`;
}

export function pintarTemporadas(contenedor, instantaneas) {
  const lista = archivo(instantaneas);

  if (!lista.length) {
    contenedor.innerHTML = `
      <section class="vacio">
        <h1>Sin temporadas</h1>
        <p class="serif">No hay ninguna instantánea materializada todavía.</p>
      </section>`;
    return;
  }

  const cerradas = lista.filter((t) => t.cerrada).length;
  contenedor.innerHTML = `
    <section class="archivo">
      <header class="titular">
        <div>
          <h1>Archivo</h1>
          <p class="serif">${lista.length} ${lista.length === 1 ? 'temporada' : 'temporadas'} ·
            ${cerradas} ${cerradas === 1 ? 'cerrada' : 'cerradas'}</p>
        </div>
      </header>
      <div class="temporadas">${lista.map(tarjeta).join('')}</div>
      ${medalleroBloque(medallero(instantaneas))}
    </section>`;
}
