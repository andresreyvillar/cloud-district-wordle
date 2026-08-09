/**
 * La vista de reglas: explica al grupo todo lo que se le aplica.
 *
 * No calcula nada. Las reglas llegan dentro de la instantánea de la temporada, materializadas por el
 * pipeline (ADR 0008), así que lo que se lee aquí es exactamente lo que el cálculo usa — incluidos los
 * umbrales, que vienen de las constantes y no de una copia escrita a mano.
 */

import { escapar } from './shell.js';

/** Los números se escriben como los escribe el grupo: con coma decimal. */
function cifra(valor) {
  return typeof valor === 'number' ? valor.toLocaleString('es-ES') : String(valor);
}

const EJES = {
  temporada: { titulo: 'La temporada', entradilla: 'Qué días cuentan y cuándo empieza de cero.' },
  clasificacion: { titulo: 'La clasificación', entradilla: 'Cómo se ordena la tabla y qué pasa si faltas.' },
  medallas: { titulo: 'Las medallas', entradilla: 'El eje que reconoce lo que la media no ve.' },
  figuras: { titulo: 'El álbum de figuras', entradilla: 'El dibujo que deja tu cuadrícula de emojis.' },
  datos: { titulo: 'Los datos', entradilla: 'Cómo se guarda lo que juegas.' },
};

const ESTADOS = {
  aplicada: { etiqueta: 'Se aplica', clase: 'aplicada' },
  'acordada-sin-aplicar': { etiqueta: 'Acordada, aún no activa', clase: 'acordada' },
  'sin-decidir': { etiqueta: 'Sin decidir', clase: 'abierta' },
};

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
  const estado = ESTADOS[regla.estado] ?? ESTADOS['sin-decidir'];
  // El marcador de votación es independiente del estado a propósito: hoy hay reglas que se aplican y que
  // el grupo no ha votado, y esconderlo sería el peor uso posible de esta página.
  const voto = regla.votada
    ? '<span class="voto si">Votada en el canal</span>'
    : '<span class="voto no">No votada</span>';
  const falta = regla.falta_decidir
    ? `<p class="falta"><strong>Falta decidir:</strong> ${escapar(regla.falta_decidir)}</p>`
    : '';

  return `
    <article class="regla ${estado.clase}${regla.votada ? '' : ' sin-votar'}">
      <header>
        <div class="marcadores">
          <span class="estado">${escapar(estado.etiqueta)}</span>
          ${voto}
        </div>
        <h3>${escapar(regla.titulo)}</h3>
      </header>
      <p class="que">${escapar(regla.que_hace)}</p>
      <p class="porque"><span>Por qué</span> ${escapar(regla.por_que)}</p>
      ${pintarParametros(regla.parametros)}
      ${falta}
    </article>`;
}

/** Agrupa por eje respetando el orden declarado, e ignora los ejes sin reglas. */
function agrupar(reglas) {
  return Object.keys(EJES)
    .map((eje) => [eje, reglas.filter((r) => r.eje === eje)])
    .filter(([, delEje]) => delEje.length > 0);
}

export function pintarReglas(contenedor, reglas, temporada) {
  if (!reglas || reglas.length === 0) {
    contenedor.innerHTML = `
      <section class="pendiente">
        <p class="etiqueta">reglas no disponibles</p>
        <p class="nota">Las reglas viajan con la instantánea de la temporada y todavía no hay ninguna
        calculada. En cuanto el pipeline la materialice, aparecen aquí.</p>
      </section>`;
    return;
  }

  const aplicadas = reglas.filter((r) => r.estado === 'aplicada').length;
  const sinVotar = reglas.filter((r) => r.estado === 'aplicada' && !r.votada).length;
  const votadas = reglas.filter((r) => r.votada).length;
  const sinDecidir = reglas.filter((r) => r.estado === 'sin-decidir').length;

  const porEje = agrupar(reglas);

  // Índice de ejes. Con veintiuna reglas la página mide casi seis mil píxeles: sin un salto directo, la
  // única forma de llegar a «Las medallas» es rodar la rueda hasta encontrarla.
  const indice = porEje
    .map(
      ([eje, delEje]) =>
        `<a href="#eje-${eje}">${escapar(EJES[eje].titulo)}<b>${delEje.length}</b></a>`,
    )
    .join('');

  const grupos = porEje
    .map(
      ([eje, delEje]) => `
      <section class="eje" id="eje-${eje}">
        <header class="eje-cab">
          <h2>${escapar(EJES[eje].titulo)}</h2>
          <p class="entradilla">${escapar(EJES[eje].entradilla)}</p>
        </header>
        <div class="rejilla-reglas">${delEje.map(pintarRegla).join('')}</div>
      </section>`,
    )
    .join('');

  contenedor.innerHTML = `
    <div class="reglas">
      <header class="reglas-cabecera">
        <div class="reglas-titular">
          <p class="etiqueta">reglas del juego${temporada ? ` · ${escapar(temporada)}` : ''}</p>
          <h1>Todo lo que se aplica, y por qué</h1>
          <p class="resumen">
            ${sinVotar > 0
              ? `<strong>${sinVotar} reglas en vigor no se han votado en el canal</strong>: se acordaron
                 en conversación de diseño. Si alguna no os cuadra, este es el momento de decirlo.`
              : 'Todas las reglas en vigor están votadas en el canal.'}
          </p>
        </div>
        <div class="hud">
          <div class="kpi"><span>En vigor</span><b>${aplicadas}</b></div>
          <div class="kpi"><span>Votadas</span><b>${votadas}</b></div>
          <div class="kpi"><span>Sin decidir</span><b>${sinDecidir}</b></div>
        </div>
      </header>
      <nav class="indice-reglas" aria-label="Ejes de reglas">${indice}</nav>
      ${grupos}
    </div>`;
}
