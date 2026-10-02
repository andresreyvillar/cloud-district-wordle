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
import { nombreVisible } from '../domain/apodos.js';

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

/** «Ana», «Ana y Bea», «Ana, Bea y Cris». */
function juntos(partes) {
  return partes.length > 1 ? `${partes.slice(0, -1).join(', ')} y ${partes.at(-1)}` : (partes[0] ?? '');
}

/** La cifra de cada competición: la media del marcador, los puntos del juego, los puntos por partida del álbum. */
const CIFRA = {
  marcador: (fila) => cifra(fila.media_temporada),
  juego: (fila) => `${fila.puntos} pts`,
  figuras: (fila) => `${cifra(fila.media)} pts`,
};

/**
 * El hueco de una competición: corona, nombres y cifra. **Un empate en cabeza se presenta como empate**: todos
 * los del primer puesto, con «empate en cabeza» en curso y «campeones» cerrada. Con varias competiciones cada
 * hueco lleva además el nombre de la suya.
 */
function hueco(t, competicion, conTitulo) {
  const quienes = competicion.campeones.length ? competicion.campeones : competicion.lideres;
  const varios = quienes.length > 1;
  // Sin nadie no hay corona: «va ganando · sin campeón» en un mes ya cerrado decía que seguía abierto.
  let corona = quienes.length ? '<span class="pixel">VA GANANDO</span>' : '';
  if (competicion.campeones.length) {
    corona = `<span class="pixel resalte">${varios ? 'CAMPEONES' : 'CAMPEÓN'}</span>`;
  } else if (varios) {
    corona = '<span class="pixel">EMPATE EN CABEZA</span>';
  }

  const enlaces = quienes.map(
    (quien) => `<a class="ganador" href="${escapar(rutaDeFicha(t.temporada, quien.jugador))}">${escapar(nombreVisible(quien.nombre))}</a>`,
  );
  // La cifra es una: si comparten puesto, es que comparten cifra.
  const nombre = quienes.length
    ? `${juntos(enlaces)} <span class="media">${escapar(CIFRA[competicion.clave](quienes[0]))}</span>`
    : '<span class="ganador vacia">sin campeón</span>';
  // Debajo de los nombres y no a su lado: la fila de nombres es flexible y ahí se quedaba sin sitio.
  const compartido = competicion.campeones.length && varios ? '<p class="nota compartido">comparten el primer puesto</p>' : '';
  const titulo = conTitulo ? `<span class="competicion">${escapar(competicion.titulo)}</span>` : '';

  return `<div class="campeon${conTitulo ? ' de-competicion' : ''}">${titulo}${corona}<div class="quien">${nombre}</div>${compartido}</div>`;
}

/**
 * La tarjeta de una temporada: un hueco por competición. Antes de octubre de 2026 solo hay una, el marcador, y
 * la tarjeta es la de siempre; desde octubre, las tres. Exportada para poder verificarla sin navegador.
 */
export function tarjeta(t) {
  const competiciones = t.competiciones ?? [{ clave: 'marcador', titulo: 'MARCADOR', lideres: t.lideres ?? [], campeones: t.campeones ?? [] }];
  const varias = competiciones.length > 1;
  const huecos = competiciones.map((c) => hueco(t, c, varias)).join('');

  return `
    <article class="temporada-card${t.cerrada ? '' : ' abierta'}${t.historica ? ' historica' : ''}">
      <header>
        <a class="etiqueta" href="${escapar(t.ruta)}">${escapar(t.etiqueta)}</a>
        <span class="estado">${escapar(t.estado ?? '')}</span>
      </header>
      ${t.historica ? '<p class="marca-historica">Bloque histórico · se jugó con otras reglas, sin imputar ausencias</p>' : ''}
      ${huecos}
      <dl class="totales">
        <div><dt>Jornadas</dt><dd>${t.jornadas}</dd></div>
        <div><dt>Jugadores</dt><dd>${t.jugadores}</dd></div>
        <div><dt>Resultados</dt><dd>${t.resultados}</dd></div>
        <div><dt>Media grupo</dt><dd>${escapar(cifra(t.media_grupo))}</dd></div>
      </dl>
      ${t.jornadas === 0 ? '<p class="nota">Ningún día llegó a la muestra mínima. La temporada existe y está vacía.</p>' : ''}
    </article>`;
}

/** Los títulos de un jugador por competición, solo los que tiene: «🏆 2 🎮 1». Sin ninguno, «—». */
function titulos(f) {
  const t = f.titulos ?? { marcador: f.temporadas_ganadas ?? 0, juego: 0, figuras: 0 };
  const partes = [['🏆', t.marcador], ['🎮', t.juego], ['🎨', t.figuras]].filter(([, n]) => n > 0);
  return partes.length ? partes.map(([icono, n]) => `${icono} ${n}`).join(' ') : '—';
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
          ? `<a class="nom" href="${escapar(rutaDeFicha(f.temporada, f.jugador))}">${escapar(nombreVisible(f.nombre))}</a>`
          : `<span class="nom sin-ficha">${escapar(nombreVisible(f.nombre))}</span>`}
        <span class="detalle">${Object.entries(f.por_clave)
          .map(([clave, n]) => `${escapar(LOGROS[clave] ?? clave)}${n > 1 ? ` ×${n}` : ''}`)
          .join(' · ')}</span>
        <span class="num suave">${escapar(titulos(f))}</span>
        <span class="num fuerte">${f.medallas}</span>
      </div>`,
    )
    .join('');
  return `
    <section class="bloque">
      <header class="bloque-cab"><h2>MEDALLERO</h2>
        <span>acumulado de todas las temporadas</span></header>
      <div class="cabeza cuatro-med">
        <span>Jugador</span><span>Medallas</span><span class="der">Títulos</span><span class="der">Total</span>
      </div>
      ${filas}
      <p class="nota">Las medallas se recalculan a partir de los resultados, así que recalibrar un umbral
        ajusta este medallero solo. «Títulos» cuenta las temporadas cerradas que ganó, por competición: 🏆 el
        marcador, 🎮 el SuperWordleBros y 🎨 las figuras, estas dos desde octubre de 2026.</p>
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
