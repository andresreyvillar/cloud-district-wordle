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

import { recurso } from '../router.js';
import { albumDeTemporada } from '../data/album.js';
import { alturaDeIntentos } from '../data/escala.js';
import { rutaDeFicha } from '../data/ficha.js';
import { escapar } from './shell.js';

/** La paleta de la maqueta: el color dice el resultado de un vistazo. */
const COLOR = { bueno: '#3DE07A', medio: '#FFD23F', malo: '#8B5CFF', fallo: '#FF4D6D' };

const FALLO = 7;

/**
 * Los doce logros implementados, con el símbolo del sprite y cómo se leen sus datos.
 *
 * Los umbrales de las de figura están **remedidos con el clasificador calibrado** (`tools/badges.py`): los
 * del brief se habían fijado con el que luego se desmintió.
 */
export const LOGROS = [
  { id: 'suertudo', nombre: 'Suertud@', regla: 'Resolver en un solo intento' },
  { id: 'dia-imposible', nombre: 'El día imposible', regla: 'Resolver en ≤4 un día de media ≥5,5' },
  { id: 'espejo-perfecto', nombre: 'Espejo perfecto', regla: 'Una cuadrícula simétrica fila a fila, de tres filas o más' },
  { id: 'superviviente', nombre: 'Superviviente', regla: 'Resolver en ≤4 tres días de media ≥4,5' },
  { id: 'ornitologo', nombre: 'Ornitólog@', regla: 'Cinco loros 🦜 en la temporada' },
  { id: 'arquitecto', nombre: 'Arquitect@', regla: 'Cuatro geométricos 📐 en la temporada' },
  { id: 'metronomo', nombre: 'Metrónom@', regla: 'No faltar ni un día laborable del mes' },
  { id: 'florista', nombre: 'Florista', regla: 'Once flores 🌷 en la temporada' },
  { id: 'verdugo', nombre: 'Verdugo', regla: 'Ser el mejor del día cinco veces' },
  { id: 'impecable', nombre: 'Impecable', regla: 'Un mes sin fallos, con 10 partidas mínimo' },
  { id: 'fondista', nombre: 'Fondista', regla: 'Quince partidas o más en el mes' },
  { id: 'coleccionista', nombre: 'Coleccionista', regla: 'Las cuatro figuras en la misma temporada' },
  { id: 'abstracto', nombre: 'Abstract@', regla: 'Siete abstractos 🌀 en la temporada' },
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

function podio(tabla, temporada) {
  const colores = [COLOR.bueno, COLOR.medio, COLOR.malo];
  return tabla
    .filter((fila) => fila.clasificado !== false)
    .slice(0, 3)
    .map(
      (fila, i) => `
      <div class="podio-card" style="border-left-color:${colores[i]}">
        <div class="podio-alto">
          <span class="pos">${fila.posicion}º</span>
          <span class="avg">${escapar(cifra(fila.media_temporada))}</span>
        </div>
        <a class="nombre" href="${escapar(rutaDeFicha(temporada, fila.jugador))}">${escapar(fila.nombre)}</a>
        ${fila.por_dia.length <= 40 ? `<div class="tiras">${tira(fila.por_dia, 20)}</div>` : ''}
        <span class="detalle">${fila.jugados} de ${fila.dias} jornadas · media jugada ${escapar(cifra(fila.media_jugada))}</span>
      </div>`,
    )
    .join('');
}

/**
 * Cómo se escribe el puesto de una fila.
 *
 * **Repetir el número en dos filas seguidas se lee como una errata**, no como un empate: quien mira una
 * tabla que va 1º, 1º, 3º, 3º, 5º, 6º, 6º, 6º concluye que falta el segundo puesto y que algo está roto.
 * Así que el número se escribe **una vez** y las filas empatadas llevan un signo de igual con su puesto en
 * el `title`, para que quien use lector de pantalla sepa en qué posición está.
 *
 * Los empates aquí no son un defecto del cálculo: en una temporada de cinco jornadas en la que todo el
 * mundo ha jugado las cinco, la puntuación solo puede tomar seis valores. Los empatados de agosto tienen
 * además colecciones idénticas —las mismas figuras, en el mismo número—, así que separarlos sería
 * inventarse una diferencia que no está en los datos. Con más jornadas desaparecen solos: la temporada 0,
 * con 72 a 149 partidas por persona, no tiene ni uno.
 */
/**
 * Cuánta ventaja deja de ser una ventaja y pasa a ser una pelea, en media de intentos por día.
 *
 * Con las siete jornadas de una temporada corta, 0,15 de diferencia es **un solo intento** en todo el mes:
 * quien va segundo lo remonta con una jornada buena. Llamar «liderar» a eso es contar mal la historia.
 */
const VENTAJA_MINIMA = 0.15;

/**
 * El titular de la temporada, según lo apretado que esté el primer puesto.
 *
 * **Mira `posicion`, no el orden de la lista**, y ahí estaba el error que esto viene a arreglar: el titular
 * tomaba el segundo elemento del array como «el segundo» y contaba la diferencia, así que con un empate en
 * cabeza publicaba «Claire le sigue a 0,00» — que es exactamente lo contrario de lo que pasaba. Los empates
 * comparten puesto desde [[empates-comparten-puesto]] y el dato ya venía en la instantánea; solo faltaba
 * leerlo.
 */
export function titular(clasificados) {
  const filas = (clasificados ?? []).filter((fila) => fila.clasificado !== false);
  if (!filas.length) return 'Todavía no hay clasificación.';

  const lider = filas[0];
  const nota = cifra(lider.media_temporada);
  const empatados = filas.filter((fila) => fila.posicion === lider.posicion);

  if (empatados.length === 2) {
    return `${escapar(empatados[0].nombre)} y ${escapar(empatados[1].nombre)} van empatados a
      ${escapar(nota)} de media: la temporada se decide entre los dos.`;
  }
  if (empatados.length > 2) {
    return `${escapar(String(empatados.length))} empatados en cabeza a ${escapar(nota)} de media.
      Nadie manda todavía.`;
  }

  const siguiente = filas.find((fila) => fila.posicion !== lider.posicion);
  if (!siguiente) {
    return `${escapar(lider.nombre)} lidera con ${escapar(nota)} de media por día.`;
  }

  const ventaja = siguiente.media_temporada - lider.media_temporada;
  if (ventaja <= VENTAJA_MINIMA) {
    return `${escapar(lider.nombre)} lidera con ${escapar(nota)}, pero ${escapar(siguiente.nombre)} le
      respira en el cuello a ${escapar(cifra(ventaja))}.`;
  }
  return `${escapar(lider.nombre)} lidera con ${escapar(nota)} de media por día y
    ${escapar(siguiente.nombre)} le sigue a ${escapar(cifra(ventaja))}.`;
}

export function marcaDePuesto(posicion, anterior) {
  if (posicion === null || posicion === undefined) return '<span class="pos">—</span>';
  if (posicion !== anterior) return `<span class="pos">${posicion}º</span>`;
  return `<span class="pos empate" title="Empatado en el puesto ${posicion}"
    aria-label="Empatado en el puesto ${posicion}">=</span>`;
}

/**
 * Una fila del marcador. **El nombre enlaza a la ficha de esa misma temporada.**
 *
 * Está exportada porque es comportamiento observable del slice `ficha-de-jugador` —el marcador es la puerta
 * de entrada a la ficha— y así el enlace se verifica sin navegador.
 */
export function filaDeMarcador(fila, temporada, anterior = null) {
  const sinClasificar = fila.clasificado === false;
  const acento = sinClasificar
    ? 'transparent'
    : fila.posicion <= 3
      ? COLOR.bueno
      : 'rgba(43,39,51,.12)';
  return `
      <div class="fila${sinClasificar ? ' sin-clasificar' : ''}">
        <i class="acento" style="background:${acento}"></i>
        ${marcaDePuesto(sinClasificar ? null : fila.posicion, anterior)}
        <a class="nom" href="${escapar(rutaDeFicha(temporada, fila.jugador))}">${escapar(fila.nombre)}</a>
        <span class="tiras">${fila.por_dia.length <= 40 ? tira(fila.por_dia, 14) : ''}</span>
        <span class="num fuerte">${escapar(cifra(fila.media_temporada))}</span>
        <span class="num suave">${escapar(cifra(fila.media_jugada))}</span>
        <span class="num suave">${fila.jugados}/${fila.dias}</span>
      </div>`;
}

function marcador(tabla, imputada, temporada) {
  const filas = tabla
    .map((fila, i) => filaDeMarcador(fila, temporada, i > 0 ? tabla[i - 1].posicion : null))
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
      ${
        tabla.some((f) => f.clasificado === false)
          ? `<p class="nota aviso">Las filas sin puesto no llegan al mínimo de partidas para clasificar.
             Aparecen porque su resultado cuenta y se puede ver, pero no ocupan posición: sin ese mínimo, y
             sin imputación, la temporada la lideraría quien apenas jugó.</p>`
          : ''
      }
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
          <svg class="icono" width="30" height="30" aria-hidden="true"><use href="${recurso(`assets/icons/logros.svg#${logro.id}`)}"></use></svg>
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

/** Cómo se lee la puntuación: `📐3 · 🦜2 · 🌷1`. Sale del catálogo publicado, no de una tabla propia. */
function escalaDeFiguras(categorias) {
  return (categorias ?? [])
    .filter((c) => c.puntos > 0)
    .sort((a, b) => b.puntos - a.puntos)
    .map((c) => `${c.emoji}${c.puntos}`)
    .join(' · ');
}

/** La tira agrupada, en HTML. `🦜8 🌷60 📐3 🌀15` con el ruido en gris para que no compita con las figuras. */
export function tiraDeFiguras(entradas) {
  return (entradas ?? [])
    .map((entrada) => {
      const clase = entrada.categoria === 'abstracto' ? ' ruido' : '';
      return `<span class="figura${clase}" title="${escapar(entrada.categoria)}">${escapar(entrada.emoji)}<b>${entrada.partidas}</b></span>`;
    })
    .join('');
}

/** La puntuación del álbum: puntos por partida, con coma decimal. */
function puntosPorPartida(media) {
  return (media ?? 0).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/**
 * El bloque del ranking de belleza. Devuelve `''` cuando la instantánea no trae álbum, que es el estado de
 * producción hasta que el pipeline nuevo llegue a `main`.
 *
 * Está exportado porque es el comportamiento observable del slice, y así se verifica sin navegador.
 */
export function bloqueDeAlbum(carga) {
  const album = albumDeTemporada(carga);
  if (!album) return '';

  const filas = album.jugadores
    .map((fila, i) => {
      const sinPuesto = !fila.clasificado;
      const anterior = i > 0 ? album.jugadores[i - 1].posicion : null;
      return `
      <div class="fila album-fila${sinPuesto ? ' sin-clasificar' : ''}">
        <i class="acento" style="background:${sinPuesto ? 'transparent' : fila.posicion <= 3 ? COLOR.bueno : 'rgba(43,39,51,.12)'}"></i>
        ${marcaDePuesto(sinPuesto ? null : fila.posicion, anterior)}
        <a class="nom" href="${escapar(rutaDeFicha(carga.temporada, fila.jugador))}">${escapar(fila.nombre)}</a>
        <span class="tiras figuras">${tiraDeFiguras(fila.tira)}</span>
        <span class="num fuerte">${escapar(puntosPorPartida(fila.media))}</span>
        <span class="num suave">${fila.figuras}/${fila.partidas}</span>
      </div>`;
    })
    .join('');

  // Sin nadie por encima del mínimo no hay ranking que enseñar, y la causa está en la cobertura: se dice, en
  // lugar de una tabla con todo el mundo a raya.
  const aviso = album.clasificados
    ? ''
    : `<p class="nota aviso">Todavía no hay ranking de belleza: hacen falta ${album.minimo} partidas con
       dibujo y nadie llega. De las partidas de esta temporada, ${album.sin_patron} no tienen cuadrícula
       guardada, así que hay poco que clasificar.</p>`;

  return `
    <section class="bloque">
      <header class="bloque-cab verde"><h2>ÁLBUM DE FIGURAS</h2>
        <span>${escapar(escalaDeFiguras(album.categorias))} · por partida</span></header>
      <div class="cabeza album-cabeza">
        <i></i><span>Pos</span><span>Jugador</span><span>Álbum</span>
        <span class="der">Pts/partida</span><span class="der">Figuras</span>
      </div>
      ${filas}
      ${aviso}
      <p class="nota">Calculado sobre ${album.clasificadas} partidas con cuadrícula guardada;
        ${album.sin_patron} de esta temporada no la tienen y quedan fuera del cálculo. El álbum
        <b>no influye en el marcador</b>: es el otro premio, y premia a otra gente.</p>
    </section>`;
}

function estadisticas(carga) {
  const dificultad = carga.dificultad ?? {};
  const jornadas = Object.keys(dificultad)
    .map(Number)
    .sort((a, b) => a - b);
  if (jornadas.length === 0) return '';

  // Escala FIJA de 1 a 7, no el máximo del mes: escalada al propio mes, una temporada cuya jornada más
  // dura fue un 4,2 se veía igual de dramática que otra que llegó a 6,0 (slice `escala-fija-comparable`).
  const columnas = jornadas
    .map((j, indice) => {
      const valor = dificultad[j];
      const alto = alturaDeIntentos(valor);
      const tono = valor >= 4.5 ? COLOR.fallo : valor >= 4 ? COLOR.medio : COLOR.bueno;
      return `<i style="height:${alto}%;background:${tono};--indice:${indice}" title="Jornada ${j} · ${escapar(cifra(valor))}"></i>`;
    })
    .join('');

  return `
    <section class="bloque">
      <header class="bloque-cab morado"><h2>ESTADÍSTICAS</h2>
        <span>Dificultad por jornada · ${escapar(alturaDeIntentos.leyenda)}</span></header>
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

  const clasificados = tabla.filter((fila) => fila.clasificado !== false);
  const lider = clasificados[0] ?? tabla[0];

  contenedor.innerHTML = `
    <div class="liga">
      <!-- Sin marca: la identidad la lleva la cabecera. Repetirla aquí era la misma palabra dos veces
           seguidas en pantalla. Esta barra es lo que siempre fue: la tira de cifras de la temporada. -->
      <div class="barra">
        <div class="hud">${hud(carga)}</div>
      </div>

      <div class="hero">
        <div class="hero-texto">
          <div class="hero-meta">
            <span class="chip">${escapar(carga.etiqueta ?? temporada ?? '')}</span>
            <span class="mono">${escapar(carga.estado ?? '')}${carga.updated_at ? ` · ${escapar(antiguedad(carga.updated_at))}` : ''}</span>
          </div>
          <h1>${titular(clasificados)}</h1>
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
          ${podio(tabla, temporada)}
        </div>
      </div>

      ${marcador(tabla, carga.imputada !== false, temporada)}
      ${logros(carga)}
      ${bloqueDeAlbum(carga)}
      ${estadisticas(carga)}
    </div>`;
}
