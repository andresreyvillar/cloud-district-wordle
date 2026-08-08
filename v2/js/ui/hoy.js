/**
 * La vista de la jornada en curso.
 *
 * Slice: `resultado-del-dia` (openspec/slices/estadisticas/resultado-del-dia.md).
 *
 * Lo que esta vista tiene que decir bien es lo incómodo: **hoy puede no contar todavía**. Un día entra en la
 * temporada si es laborable y lo juegan al menos cinco personas, así que a media mañana la jornada existe,
 * tiene resultados y aún no puntúa. Si se calla, alguien mira su nota, luego la ve cambiar y concluye que el
 * sistema miente.
 */

import { diaEnCurso } from '../data/dia.js';
import { rutaDeFicha } from '../data/ficha.js';
import { escapar } from './shell.js';

const COLOR = { bueno: '#3DE07A', medio: '#FFD23F', malo: '#8B5CFF', fallo: '#FF4D6D' };
const FALLO = 7;

function cifra(valor, decimales = 2) {
  return typeof valor === 'number'
    ? valor.toLocaleString('es-ES', { minimumFractionDigits: decimales, maximumFractionDigits: decimales })
    : String(valor ?? '—');
}

function color(intentos) {
  if (intentos >= FALLO) return COLOR.fallo;
  if (intentos >= 6) return COLOR.malo;
  if (intentos >= 4) return COLOR.medio;
  return COLOR.bueno;
}

const DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
const MESES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
];

function enPalabras(fecha) {
  const d = new Date(`${fecha}T00:00:00Z`);
  const texto = `${DIAS[d.getUTCDay()]} ${d.getUTCDate()} de ${MESES[d.getUTCMonth()]}`;
  // La mayúscula se pone aquí y no con `text-transform: capitalize`, que se la pondría también a "de".
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

/** El aviso que decide la honestidad de la vista. */
function siCuenta(dia) {
  if (dia.cuenta === null) {
    return `<p class="nota aviso">La instantánea de la temporada no trae publicado el mínimo de jugadores, así
      que esta vista no puede afirmar si la jornada cuenta. No se inventa el número.</p>`;
  }
  if (dia.cuenta) {
    return `<p class="nota">Esta jornada <strong>ya cuenta</strong> para la temporada: es laborable y la han
      jugado ${dia.jugaron.length} personas, el mínimo son ${dia.minimo}.</p>`;
  }
  if (dia.motivo === 'fin de semana') {
    return `<p class="nota aviso">Es ${escapar(DIAS[new Date(`${dia.fecha}T00:00:00Z`).getUTCDay()])}:
      <strong>esta jornada no puntúa</strong>. Los resultados se guardan y se pueden mirar, pero el fin de
      semana no forma parte de la temporada, juegue quien juegue.</p>`;
  }
  return `<p class="nota aviso"><strong>Todavía no cuenta.</strong> Han jugado ${dia.jugaron.length} y hacen
    falta ${dia.minimo}: ${dia.faltan_para_contar}
    ${dia.faltan_para_contar === 1 ? 'persona más' : 'personas más'} y la jornada entra en la temporada. Hasta
    entonces no fija dificultad ni penaliza a quien falta.</p>`;
}

function tarjetas(dia, temporada) {
  return dia.jugaron
    .map(
      (j, i) => `
      <a class="resultado" href="${escapar(rutaDeFicha(temporada, j.jugador))}"
         style="border-left-color:${color(j.intentos)}">
        <span class="orden">${i + 1}</span>
        <span class="quien">${escapar(j.nombre)}</span>
        <span class="marca">${j.fallo ? 'X' : j.intentos}<em>/6</em></span>
      </a>`,
    )
    .join('');
}

export function pintarHoy(contenedor, resultados, instantaneas, temporada) {
  const carga = instantaneas.get(temporada) ?? null;

  // Los nombres de quien falta no están en las filas de hoy: se toman de la clasificación de la temporada.
  const nombres = new Map(
    (carga?.clasificacion ?? []).map((fila) => [fila.jugador, fila.nombre]),
  );
  const dia = diaEnCurso(resultados, carga, nombres);

  if (!dia.existe) {
    contenedor.innerHTML = `
      <section class="vacio">
        <h1>Aún no hay jornada</h1>
        <p class="serif">No hay ningún resultado guardado, así que no hay día que mostrar.</p>
      </section>`;
    return;
  }

  const kpis = [
    ['Han jugado', `${dia.jugaron.length}`],
    ['Faltan', `${dia.cuantos_faltan}`],
    ['Media del día', cifra(dia.media)],
    ['Mejor', dia.mejor >= FALLO ? 'X' : `${dia.mejor}`],
  ];

  const comparacion =
    dia.diferencia === null
      ? ''
      : `<div class="veredicto ${dia.veredicto === 'más dura' ? 'dura' : dia.veredicto === 'más fácil' ? 'facil' : ''}">
           <span>La palabra ha salido</span>
           <b>${escapar(dia.veredicto)}</b>
           <span>que la media de la temporada (${escapar(cifra(dia.media_temporada))}),
             por ${escapar(cifra(Math.abs(dia.diferencia)))}</span>
         </div>`;

  const ausentes = dia.faltan.length
    ? `<div class="ausentes">${dia.faltan
        .map(
          (j) =>
            `<a href="${escapar(rutaDeFicha(temporada, j.jugador))}">${escapar(j.nombre)}</a>`,
        )
        .join('')}</div>`
    : '<p class="nota">No falta nadie: ha jugado toda la temporada.</p>';

  contenedor.innerHTML = `
    <section class="hoy">
      <header class="titular">
        <div>
          <span class="pixel resalte">#${dia.jornada}</span>
          <h1>${escapar(enPalabras(dia.fecha))}</h1>
          <p class="serif">${escapar(dia.etiqueta ?? '')}</p>
        </div>
        <div class="hud">${kpis
          .map(([k, v]) => `<div class="kpi"><span>${escapar(k)}</span><b>${escapar(v)}</b></div>`)
          .join('')}</div>
      </header>

      <section class="bloque">
        <header class="bloque-cab"><h2>CÓMO SE HA DADO</h2>
          <span>media ${escapar(cifra(dia.media))} · mejor ${dia.mejor >= FALLO ? 'X' : dia.mejor} · peor ${dia.peor >= FALLO ? 'X' : dia.peor}</span></header>
        ${comparacion}
        ${siCuenta(dia)}
      </section>

      <section class="bloque">
        <header class="bloque-cab"><h2>HAN JUGADO</h2><span>${dia.jugaron.length}</span></header>
        <div class="resultados">${tarjetas(dia, temporada)}</div>
      </section>

      <section class="bloque">
        <header class="bloque-cab"><h2>FALTAN</h2><span>${dia.cuantos_faltan}</span></header>
        ${ausentes}
        <p class="nota">La lista sale de quien ha jugado esta temporada. Faltar en un día que cuenta se paga
          con la nota imputada; en un día que no cuenta, no se paga.</p>
      </section>
    </section>`;
}
