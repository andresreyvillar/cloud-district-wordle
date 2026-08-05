/**
 * La vista de temporada, con la dirección visual de la liga arcade.
 *
 * Diseño: docs/context/sources/2026-08-05-diseno-liga-arcade.md
 *
 * No calcula nada. La clasificación, la dificultad por jornada y los totales llegan dentro de la instantánea
 * de la temporada (ADR 0008), así que lo que se pinta aquí es exactamente lo que publica el bot.
 *
 * De la maqueta se toma la paleta de puntuación, la tipografía, el HUD, el titular, el podio, el MARCADOR y
 * las columnas de dificultad. **No** se toman los motes, los dorsales ni el Δ de posición: son reglas de
 * juego sin decidir, dos de ellas bloqueadas por el grupo.
 */

import { escapar } from './shell.js';

/** La paleta de la maqueta: el color dice el resultado de un vistazo. */
const COLOR = { bueno: '#3DE07A', medio: '#FFD23F', malo: '#8B5CFF', fallo: '#FF4D6D' };

const FALLO = 7;

/** Los siete logros implementados, con el símbolo del sprite y cómo se leen sus datos. */
const LOGROS = [
  { id: 'suertudo', nombre: 'Suertud@', regla: 'Resolver en un solo intento' },
  { id: 'dia-imposible', nombre: 'El día imposible', regla: 'Resolver en ≤4 un día de media ≥5,5' },
  { id: 'superviviente', nombre: 'Superviviente', regla: 'Resolver en ≤4 tres días de media ≥4,5' },
  { id: 'metronomo', nombre: 'Metrónom@', regla: 'No faltar ni un día laborable del mes' },
  { id: 'verdugo', nombre: 'Verdugo', regla: 'Ser el mejor del día cinco veces' },
  { id: 'impecable', nombre: 'Impecable', regla: 'Un mes sin fallos, con 10 partidas mínimo' },
  { id: 'fondista', nombre: 'Fondista', regla: 'Quince partidas o más en el mes' },
];

function color(intentos, imputado) {
  if (imputado) return null; // se pinta en contorno: no jugada
  if (intentos >= FALLO) return COLOR.fallo;
  if (intentos >= 6) return COLOR.malo;
  if (intentos >= 4) return COLOR.medio;
  return COLOR.bueno;
}

function cifra(valor, decimales = 2) {
  return typeof valor === 'number'
    ? valor.toLocaleString('es-ES', { minimumFractionDigits: decimales, maximumFractionDigits: decimales })
    : String(valor ?? '—');
}

/** La tira de casillas de un jugador, una por jornada. Las no jugadas van en contorno. */
function tira(porDia, alto = 18) {
  return porDia
    .map((dia) => {
      const fondo = color(dia.intentos, dia.imputado);
      const estilo = fondo
        ? `background:${fondo}`
        : 'background:transparent;border:2px solid rgba(43,39,51,.20)';
      const titulo = `Jornada ${dia.jornada} · ${dia.imputado ? 'imputada' : 'jugada'} ${cifra(dia.intentos, 1)}`;
      return `<i class="casilla" style="${estilo};height:${alto}px" title="${escapar(titulo)}"></i>`;
    })
    .join('');
}

function leyenda() {
  const items = [
    [COLOR.bueno, '1-3'],
    [COLOR.medio, '4-5'],
    [COLOR.malo, '6'],
    [COLOR.fallo, 'fallo'],
    [null, 'no jugada · imputada'],
  ];
  return `<div class="leyenda">${items
    .map(([c, texto]) => {
      const estilo = c ? `background:${c}` : 'background:transparent;border:2px solid rgba(43,39,51,.20)';
      return `<span><i class="casilla" style="${estilo};height:13px"></i>${escapar(texto)}</span>`;
    })
    .join('')}</div>`;
}

function hud(carga) {
  const kpis = [
    ['Jugadores', carga.jugadores?.length ?? 0],
    ['Días válidos', carga.dias?.length ?? 0],
    ['Resultados', carga.resultados ?? 0],
    ['Media grupo', cifra(carga.media_grupo)],
  ];
  return kpis
    .map(([k, v]) => `<div class="kpi"><span>${escapar(k)}</span><b>${escapar(v)}</b></div>`)
    .join('');
}

function podio(tabla) {
  const colores = [COLOR.bueno, COLOR.medio, COLOR.malo];
  return tabla
    .slice(0, 3)
    .map(
      (fila, i) => `
      <div class="podio-card" style="border-left-color:${colores[i]}">
        <div class="podio-alto">
          <span class="pos">${fila.posicion}º</span>
          <span class="avg">${escapar(cifra(fila.media_temporada))}</span>
        </div>
        <span class="nombre">${escapar(fila.nombre)}</span>
        ${fila.por_dia.length <= 40 ? `<div class="tiras">${tira(fila.por_dia, 20)}</div>` : ''}
        <span class="detalle">${fila.jugados} de ${fila.dias} jornadas · media jugada ${escapar(cifra(fila.media_jugada))}</span>
      </div>`,
    )
    .join('');
}

function marcador(tabla, imputada) {
  const filas = tabla
    .map((fila) => {
      const acento = fila.posicion <= 3 ? COLOR.bueno : 'rgba(43,39,51,.12)';
      return `
      <div class="fila">
        <i class="acento" style="background:${acento}"></i>
        <span class="pos">${fila.posicion}</span>
        <span class="nom">${escapar(fila.nombre)}</span>
        <span class="tiras">${fila.por_dia.length <= 40 ? tira(fila.por_dia, 14) : ''}</span>
        <span class="num fuerte">${escapar(cifra(fila.media_temporada))}</span>
        <span class="num suave">${escapar(cifra(fila.media_jugada))}</span>
        <span class="num suave">${fila.jugados}/${fila.dias}</span>
      </div>`;
    })
    .join('');

  return `
    <section class="bloque">
      <header class="bloque-cab"><h2>MARCADOR</h2>
        <span>${imputada ? 'Ordenado por media de temporada (con ausencias imputadas)' : 'Ordenado por media de las partidas jugadas'}</span></header>
      <div class="cabeza">
        <i></i><span>Pos</span><span>Jugador</span><span>Jornadas</span>
        <span class="der">Media temp.</span><span class="der">Media jugada</span><span class="der">Jorn.</span>
      </div>
      ${filas}
      <p class="nota">${
        imputada
          ? 'A las jornadas no jugadas se les imputa min( max( dificultad del día , tu media ) + 0,5 ; 7 ). El denominador es el mismo para todos, así que las medias se comparan sin más reglas.'
          : 'Sin imputar: cada media es la de las partidas que ese jugador jugó de verdad. Por eso la columna de jornadas dice cuántas jugó cada uno.'
      }</p>
    </section>`;
}

function logros(carga) {
  const ganadores = carga.logros ?? {};
  const tarjetas = LOGROS.map((logro) => {
    const quienes = ganadores[logro.id] ?? [];
    const estado = quienes.length ? `${quienes.length} lo tiene${quienes.length > 1 ? 'n' : ''}` : 'sin ganar';
    return `
      <article class="logro ${quienes.length ? 'ganado' : ''}">
        <header>
          <svg class="icono" width="30" height="30" aria-hidden="true"><use href="/assets/icons/logros.svg#${logro.id}"></use></svg>
          <span class="estado">${escapar(estado)}</span>
        </header>
        <h3>${escapar(logro.nombre)}</h3>
        <p>${escapar(logro.regla)}</p>
        <span class="quienes">${quienes.length ? escapar(quienes.join(', ')) : '—'}</span>
      </article>`;
  }).join('');

  return `
    <section class="bloque logros-bloque">
      <header class="bloque-cab amarillo"><h2>LOGROS</h2><span>Se reinician el día 1</span></header>
      <div class="logros">${tarjetas}</div>
    </section>`;
}

function estadisticas(carga) {
  const dificultad = carga.dificultad ?? {};
  const jornadas = Object.keys(dificultad)
    .map(Number)
    .sort((a, b) => a - b);
  if (jornadas.length === 0) return '';

  const max = Math.max(...jornadas.map((j) => dificultad[j]));
  const columnas = jornadas
    .map((j) => {
      const valor = dificultad[j];
      const alto = Math.round((valor / max) * 100);
      const tono = valor >= 4.5 ? COLOR.fallo : valor >= 4 ? COLOR.medio : COLOR.bueno;
      return `<i style="height:${alto}%;background:${tono}" title="Jornada ${j} · ${escapar(cifra(valor))}"></i>`;
    })
    .join('');

  return `
    <section class="bloque">
      <header class="bloque-cab morado"><h2>ESTADÍSTICAS</h2><span>Dificultad por jornada</span></header>
      <div class="columnas">${columnas}</div>
      <div class="extremos">
        <div><span class="dura">Jornada más dura · ${carga.mas_dificil ?? '—'}</span>
          <b>${escapar(cifra(dificultad[carga.mas_dificil]))}</b></div>
        <div><span class="facil">Más fácil · ${carga.mas_facil ?? '—'}</span>
          <b>${escapar(cifra(dificultad[carga.mas_facil]))}</b></div>
      </div>
    </section>`;
}

function antiguedad(updatedAt) {
  if (!updatedAt) return '';
  const minutos = Math.round((Date.now() - new Date(updatedAt).getTime()) / 60000);
  if (minutos < 60) return `calculado hace ${minutos} min`;
  const horas = Math.round(minutos / 60);
  if (horas < 48) return `calculado hace ${horas} h`;
  return `calculado hace ${Math.round(horas / 24)} días`;
}

export function pintarTemporada(contenedor, carga, temporada) {
  if (!carga) {
    contenedor.innerHTML = `<section class="pendiente"><p class="etiqueta">sin instantánea</p>
      <p class="nota">Esta temporada no está calculada todavía. El cron la materializa al ingerir.</p></section>`;
    return;
  }

  const tabla = carga.clasificacion ?? [];
  if (tabla.length === 0) {
    contenedor.innerHTML = `<section class="pendiente"><p class="etiqueta">temporada sin días válidos</p>
      <h2>${escapar(temporada ?? '')}</h2>
      <p class="nota">Ningún día de esta temporada llegó a los cinco jugadores que hacen falta para que
      cuente, así que no hay clasificación. No es un error: es un mes sin partido.</p></section>`;
    return;
  }

  const lider = tabla[0];
  const segundo = tabla[1];
  const diferencia = segundo ? segundo.media_temporada - lider.media_temporada : 0;

  contenedor.innerHTML = `
    <div class="liga">
      <div class="barra">
        <div class="marca-liga"><span class="pixel">WORDLE</span><span class="pixel resalte">LIGA</span></div>
        <div class="hud">${hud(carga)}</div>
      </div>

      <div class="hero">
        <div class="hero-texto">
          <div class="hero-meta">
            <span class="chip">${escapar(carga.etiqueta ?? temporada ?? '')}</span>
            <span class="mono">${escapar(carga.estado ?? '')}${carga.updated_at ? ` · ${escapar(antiguedad(carga.updated_at))}` : ''}</span>
          </div>
          <h1>${escapar(lider.nombre)} lidera con ${escapar(cifra(lider.media_temporada))} de media por día${
            segundo ? ` y ${escapar(segundo.nombre)} le sigue a ${escapar(cifra(diferencia))}` : ''
          }.</h1>
          <p class="serif">${carga.dias?.length ?? 0} jornadas válidas, ${carga.jugadores?.length ?? 0}
            jugadores y ${carga.resultados ?? 0} resultados. ${
              carga.imputada === false
                ? 'La temporada 0 se ordena por la media de las partidas jugadas: las reglas nuevas no estaban en vigor y la gente se incorporó en meses distintos.'
                : 'La tabla se calcula sobre los días de la temporada, no sobre las partidas jugadas.'
            }</p>
          ${
            lider.por_dia.length <= 40
              ? `<div class="hero-tira">
            <span class="mono etiqueta">Partida de ${escapar(lider.nombre)}, jornada a jornada</span>
            <div class="tiras grande">${tira(lider.por_dia, 30)}</div>
            ${leyenda()}
          </div>`
              : ''
          }
        </div>
        <div class="podio">
          <span class="mono etiqueta">Podio de la temporada</span>
          ${podio(tabla)}
        </div>
      </div>

      ${marcador(tabla, carga.imputada !== false)}
      ${logros(carga)}
      ${estadisticas(carga)}
    </div>`;
}
