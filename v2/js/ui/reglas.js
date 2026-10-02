/**
 * Las reglas vigentes, para la pestaña Info (slice `reglas-explicadas`).
 *
 * No calcula nada. Las reglas llegan dentro de la instantánea de la temporada, materializadas por el
 * pipeline (ADR 0008), así que lo que se lee aquí es exactamente lo que el cálculo usa — incluidos los
 * umbrales, que vienen de las constantes y no de una copia escrita a mano.
 *
 * **Solo las vigentes**: las aplicadas que no son históricas. Las propuestas y las de la temporada 0 siguen en
 * el catálogo, pero aquí liarían a quien solo quiere saber cómo se juega hoy (decisión del dueño). Por lo
 * mismo, sin marcas de estado ni de votación.
 */

import { escapar } from './shell.js';

/** Los números se escriben como los escribe el grupo: con coma decimal. Una lista, separada por puntos. */
function cifra(valor) {
  if (Array.isArray(valor)) return valor.map(cifra).join(' · ');
  return typeof valor === 'number' ? valor.toLocaleString('es-ES') : String(valor);
}

const EJES = {
  temporada: { titulo: 'La temporada', entradilla: 'Qué días cuentan y cuándo empieza de cero.' },
  clasificacion: { titulo: 'El marcador', entradilla: 'Cómo se ordena la tabla y qué pasa si faltas.' },
  medallas: { titulo: 'Las medallas', entradilla: 'Lo que reconoce lo que la media no ve.' },
  figuras: { titulo: 'El álbum de figuras', entradilla: 'El dibujo que deja tu cuadrícula de emojis.' },
  juego: { titulo: 'El SuperWordleBros', entradilla: 'Cómo puntúa el juego de cada día.' },
  datos: { titulo: 'Los datos', entradilla: 'Cómo se guarda lo que juegas.' },
};

/** Si una regla se enseña: aplicada y no histórica. */
export function esVigente(regla) {
  return regla?.estado === 'aplicada' && !regla.historica;
}

function pintarParametros(parametros) {
  if (!parametros || parametros.length === 0) return '';
  const filas = parametros
    .map(
      (p) => `<li><span class="pnombre">${escapar(p.nombre)}</span>
        <span class="pvalor">${escapar(cifra(p.valor))}${p.unidad ? ` ${escapar(p.unidad)}` : ''}</span></li>`,
    )
    .join('');
  return `<ul class="parametros">${filas}</ul>`;
}

function pintarRegla(regla) {
  return `
    <article class="regla aplicada">
      <header><h3>${escapar(regla.titulo)}</h3></header>
      <p class="que">${escapar(regla.que_hace)}</p>
      <p class="porque"><span>Por qué</span> ${escapar(regla.por_que)}</p>
      ${pintarParametros(regla.parametros)}
    </article>`;
}

/** Agrupa por eje respetando el orden declarado, e ignora los ejes sin reglas. */
function agrupar(reglas) {
  return Object.keys(EJES)
    .map((eje) => [eje, reglas.filter((r) => r.eje === eje)])
    .filter(([, delEje]) => delEje.length > 0);
}

/** Las reglas vigentes por eje, en HTML, con un índice de ejes. Vacío si no hay ninguna. */
export function reglasVigentes(reglas) {
  const porEje = agrupar((reglas ?? []).filter(esVigente));
  if (!porEje.length) return '';
  // Índice de ejes: sin un salto directo, la única forma de llegar al último es rodar la rueda.
  const indice = porEje
    .map(([eje, delEje]) => `<a href="#eje-${eje}">${escapar(EJES[eje].titulo)}<b>${delEje.length}</b></a>`)
    .join('');
  const grupos = porEje
    .map(
      ([eje, delEje]) => `
      <section class="eje" id="eje-${eje}">
        <header class="eje-cab">
          <h3 class="eje-titulo">${escapar(EJES[eje].titulo)}</h3>
          <p class="entradilla">${escapar(EJES[eje].entradilla)}</p>
        </header>
        <div class="rejilla-reglas">${delEje.map(pintarRegla).join('')}</div>
      </section>`,
    )
    .join('');
  return `<nav class="indice-reglas">${indice}</nav>${grupos}`;
}
