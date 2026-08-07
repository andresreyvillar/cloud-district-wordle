/**
 * La ficha de un jugador dentro de una temporada.
 *
 * Slice: `ficha-de-jugador` (openspec/slices/estadisticas/ficha-de-jugador.md).
 *
 * No calcula: pinta lo que `js/data/ficha.js` proyecta de la instantánea (ADR 0008). La pieza que justifica
 * la vista es **el coste de faltar**: el marcador dice que tu media es 4,12 y no dice que parte de ella son
 * jornadas que no jugaste. Aquí sí.
 */

import { alturaEnEscala, escalaDeDistribucion } from '../data/escala.js';
import { ficha } from '../data/ficha.js';
import { escapar } from './shell.js';

const COLOR = { bueno: '#3DE07A', medio: '#FFD23F', malo: '#8B5CFF', fallo: '#FF4D6D' };
const FALLO = 7;

/** Por encima de estas jornadas la tira satura la línea: la temporada 0 tiene 181. */
const MAXIMO_PARA_LA_TIRA = 40;

const LOGROS = {
  suertudo: 'Suertud@',
  'dia-imposible': 'El día imposible',
  superviviente: 'Superviviente',
  metronomo: 'Metrónom@',
  verdugo: 'Verdugo',
  impecable: 'Impecable',
  fondista: 'Fondista',
};

const MESES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
];

function cifra(valor, decimales = 2) {
  return typeof valor === 'number'
    ? valor.toLocaleString('es-ES', { minimumFractionDigits: decimales, maximumFractionDigits: decimales })
    : String(valor ?? '—');
}

function color(intentos, imputado) {
  if (imputado) return null;
  if (intentos >= FALLO) return COLOR.fallo;
  if (intentos >= 6) return COLOR.malo;
  if (intentos >= 4) return COLOR.medio;
  return COLOR.bueno;
}

function tira(porDia) {
  return porDia
    .map((dia) => {
      const fondo = color(dia.intentos, dia.imputado);
      const estilo = fondo
        ? `background:${fondo}`
        : 'background:transparent;border:2px solid rgba(43,39,51,.20)';
      const titulo = `Jornada ${dia.jornada} · ${dia.fecha} · ${dia.imputado ? 'imputada' : 'jugada'} ${cifra(dia.intentos, 1)}`;
      return `<i class="casilla" style="${estilo};height:22px" title="${escapar(titulo)}"></i>`;
    })
    .join('');
}

function hud(f) {
  const kpis = [
    ['Media temporada', cifra(f.media_temporada)],
    ['Media jugada', cifra(f.media_jugada)],
    ['Jornadas', `${f.jugados}/${f.dias}`],
    ['Mejor', f.mejor === undefined ? '—' : `${f.mejor}`],
    ['Peor', f.peor >= FALLO ? 'fallo' : `${f.peor}`],
  ];
  return kpis
    .map(([k, v]) => `<div class="kpi"><span>${escapar(k)}</span><b>${escapar(v)}</b></div>`)
    .join('');
}

/** El bloque que hace comprobable la regla de imputación sobre un jugador concreto. */
function costeDeFaltar(f) {
  if (!f.imputa) {
    return `
      <section class="bloque">
        <header class="bloque-cab"><h2>AUSENCIAS</h2><span>Esta temporada no imputa</span></header>
        <p class="nota">La temporada 0 se rige por las reglas con las que se jugó: la media es la de las
          partidas jugadas y faltar no tenía nota. Por eso aquí no hay coste que enseñar.</p>
      </section>`;
  }
  if (f.imputadas === 0) {
    return `
      <section class="bloque">
        <header class="bloque-cab"><h2>AUSENCIAS</h2><span>Ninguna</span></header>
        <p class="nota">Ha jugado las ${f.dias} jornadas de la temporada, así que su media de temporada es
          exactamente la de sus partidas.</p>
      </section>`;
  }
  const signo = f.coste_de_faltar >= 0 ? '+' : '−';
  return `
    <section class="bloque">
      <header class="bloque-cab"><h2>LO QUE COSTÓ FALTAR</h2>
        <span>${f.imputadas} ${f.imputadas === 1 ? 'jornada imputada' : 'jornadas imputadas'}</span></header>
      <div class="coste">
        <div><span>Media de lo jugado</span><b>${escapar(cifra(f.media_jugada))}</b></div>
        <div class="flecha">→</div>
        <div><span>Media de temporada</span><b>${escapar(cifra(f.media_temporada))}</b></div>
        <div class="delta">${signo}${escapar(cifra(Math.abs(f.coste_de_faltar)))}</div>
      </div>
      <p class="nota">A cada jornada no jugada se le pone min( max( dificultad del día , tu media ) + 0,5 ; 7 ).
        Esa es la diferencia entre las dos cifras, y es la única parte de su media que no jugó.</p>
    </section>`;
}

function distribucion(f) {
  const total = f.distribucion.reduce((a, b) => a + b, 0) || 1;
  // La escala es la de TODA la temporada, no la del jugador: escalada a su propio máximo, quien jugó cien
  // partidas y quien jugó diez dibujaban la misma silueta (slice `escala-fija-comparable`).
  const escala = f.escala_distribucion;
  const barras = f.distribucion
    .map((cuantas, i) => {
      const intentos = i + 1;
      const fondo = color(intentos, false);
      const etiqueta = intentos >= FALLO ? 'X' : `${intentos}`;
      return `
        <div class="barra" title="${escapar(`${cuantas} de ${total}`)}">
          <b style="height:${alturaEnEscala(cuantas, escala)}%;background:${fondo}"></b>
          <span class="n">${cuantas || ''}</span>
          <span class="eje">${etiqueta}</span>
        </div>`;
    })
    .join('');
  return `
    <section class="bloque">
      <header class="bloque-cab"><h2>DISTRIBUCIÓN</h2>
        <span>${total} ${total === 1 ? 'partida jugada' : 'partidas jugadas'} · ${escapar(escalaDeDistribucion.leyenda(escala))}</span></header>
      <div class="distribucion">${barras}</div>
    </section>`;
}

/** El desglose: jornada a jornada si caben, y por meses cuando son 181. */
function desglose(f) {
  if (f.por_dia.length <= MAXIMO_PARA_LA_TIRA) {
    const entradas = f.por_dia
      .map(
        (dia) => `
        <li class="${dia.imputado ? 'imputada' : ''}">
          <span class="jor">#${dia.jornada}</span>
          <span class="fec">${escapar(dia.fecha)}</span>
          <span class="val">${escapar(cifra(dia.intentos, dia.imputado ? 2 : 0))}</span>
          <span class="tipo">${dia.imputado ? 'imputada' : 'jugada'}</span>
        </li>`,
      )
      .join('');
    return `
      <section class="bloque">
        <header class="bloque-cab"><h2>JORNADA A JORNADA</h2>
          <span>${f.imputadas} de ${f.dias} imputadas</span></header>
        <div class="tiras">${tira(f.por_dia)}</div>
        <ul class="desglose">${entradas}</ul>
      </section>`;
  }

  const porMes = new Map();
  for (const dia of f.por_dia) {
    const mes = String(dia.fecha).slice(0, 7);
    if (!porMes.has(mes)) porMes.set(mes, []);
    porMes.get(mes).push(dia);
  }
  const filas = [...porMes.entries()]
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([mes, dias]) => {
      const jugadas = dias.filter((d) => !d.imputado);
      const media = jugadas.length
        ? jugadas.reduce((suma, d) => suma + d.intentos, 0) / jugadas.length
        : null;
      const [anio, numero] = mes.split('-');
      return `
        <div class="fila">
          <span class="nom">${escapar(MESES[Number(numero) - 1])} ${escapar(anio)}</span>
          <span class="num suave">${jugadas.length}/${dias.length}</span>
          <span class="num fuerte">${escapar(cifra(media))}</span>
        </div>`;
    })
    .join('');
  return `
    <section class="bloque">
      <header class="bloque-cab"><h2>MES A MES</h2>
        <span>${f.por_dia.length} jornadas: la tira no cabe</span></header>
      <div class="cabeza tres"><span>Mes</span><span class="der">Jugadas</span><span class="der">Media</span></div>
      ${filas}
    </section>`;
}

function medallas(f) {
  if (!f.medallas.length) {
    return `
      <section class="bloque">
        <header class="bloque-cab"><h2>MEDALLAS</h2><span>Ninguna esta temporada</span></header>
        <p class="nota">Las medallas se recalculan cada vez a partir de los resultados, así que aún puede
          ganarlas mientras la temporada siga abierta.</p>
      </section>`;
  }
  const piezas = f.medallas
    .map(
      (clave) => `
      <article class="logro ganado">
        <header>
          <svg class="icono" width="30" height="30" aria-hidden="true"><use href="/assets/icons/logros.svg#${escapar(clave)}"></use></svg>
        </header>
        <h3>${escapar(LOGROS[clave] ?? clave)}</h3>
      </article>`,
    )
    .join('');
  return `
    <section class="bloque">
      <header class="bloque-cab"><h2>MEDALLAS</h2>
        <span>${f.medallas.length} esta temporada</span></header>
      <div class="logros">${piezas}</div>
    </section>`;
}

function palmaresBloque(lista) {
  const filas = lista
    .map(
      (t) => `
      <a class="fila${t.actual ? ' actual' : ''}" href="/t/${escapar(t.temporada)}/j/${escapar(t.jugador ?? '')}">
        <span class="pos">${t.clasificado ? `${t.posicion}º` : '—'}</span>
        <span class="nom">${escapar(t.etiqueta)}</span>
        <span class="num suave">${t.jugados}/${t.dias}</span>
        <span class="num fuerte">${escapar(cifra(t.media_temporada))}</span>
      </a>`,
    )
    .join('');
  return `
    <section class="bloque">
      <header class="bloque-cab"><h2>PALMARÉS</h2>
        <span>${lista.length} ${lista.length === 1 ? 'temporada' : 'temporadas'} con resultados</span></header>
      <div class="cabeza cuatro"><span>Pos</span><span>Temporada</span><span class="der">Jorn.</span><span class="der">Media</span></div>
      ${filas}
    </section>`;
}

/** Pinta la ficha. Si el jugador no jugó esa temporada, lo dice y ofrece las que sí. */
export function pintarJugador(contenedor, instantaneas, temporada, jugador) {
  const f = ficha(instantaneas, temporada, jugador);

  if (!f.existe) {
    const otras = f.otras.length
      ? `<p>Sí tiene resultados en ${f.otras
          .map((t) => `<a href="/t/${escapar(t.temporada)}/j/${escapar(jugador)}">${escapar(t.etiqueta)}</a>`)
          .join(' · ')}.</p>`
      : '<p>No hay resultados suyos en ninguna temporada.</p>';
    contenedor.innerHTML = `
      <section class="vacio">
        <h1>${escapar(f.nombre)}</h1>
        <p class="serif">No jugó ninguna jornada de ${escapar(f.etiqueta)}.</p>
        ${otras}
        <p><a href="/t/${escapar(temporada)}">Volver al marcador</a></p>
      </section>`;
    return;
  }

  const puesto = f.clasificado
    ? `<span class="puesto">${f.posicion}º</span>`
    : '<span class="puesto sin">sin puesto</span>';
  const conJugador = f.palmares.map((t) => ({ ...t, jugador }));

  contenedor.innerHTML = `
    <section class="ficha">
      <header class="titular">
        <div>
          ${puesto}
          <h1>${escapar(f.nombre)}</h1>
          <p class="serif">${escapar(f.etiqueta)} · ${escapar(f.estado ?? '')}</p>
        </div>
        <div class="hud">${hud(f)}</div>
      </header>
      ${
        f.clasificado
          ? ''
          : `<p class="nota aviso">Aparece sin puesto porque no llega al mínimo de partidas de esta
             temporada. Su media se calcula igual y se puede ver.</p>`
      }
      ${costeDeFaltar(f)}
      ${distribucion(f)}
      ${desglose(f)}
      ${medallas(f)}
      ${palmaresBloque(conJugador)}
      <p class="volver"><a href="/t/${escapar(temporada)}">← Volver al marcador de ${escapar(f.etiqueta)}</a></p>
    </section>`;
}
