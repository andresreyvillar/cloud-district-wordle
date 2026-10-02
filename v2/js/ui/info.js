/**
 * La pestaña Info: cómo se juega, qué competiciones hay, qué publica el bot y las reglas vigentes.
 *
 * Slice: `reglas-explicadas` (pack `feat-pestana-info`). Sustituye a la pestaña Reglas.
 *
 * **La explicación no lleva cifras.** Los números —días, jugadores, puntos, horas— solo aparecen en las
 * reglas, que los leen de las constantes del cálculo. Un número escrito aquí a mano se quedaría viejo en cuanto
 * alguien recalibrara un umbral, y la página contradiría a sus propias reglas. Un test lo comprueba.
 */

import { reglasVigentes } from './reglas.js';

const PALABRA_DEL_DIA = 'https://lapalabradeldia.com';

const COMO_SE_JUEGA = `
  <section class="info-bloque">
    <h2>Cómo se juega</h2>
    <p>Cada día se juega la palabra de <a href="${PALABRA_DEL_DIA}" target="_blank" rel="noopener">lapalabradeldia.com</a>
      y se pega el resultado, tal cual lo comparte el juego, en el canal <strong>#wordle-line</strong> de Slack.</p>
    <p>Con eso basta. El bot recoge los resultados del canal, calcula las clasificaciones y las publica aquí y en
      el propio canal. Tu resultado cuenta el día del puzzle, no el día que lo pegas, y eres tu cuenta de Slack:
      cambiarte el nombre no te parte en dos.</p>
  </section>`;

const COMPETICIONES = `
  <section class="info-bloque">
    <h2>Las competiciones</h2>
    <div class="info-rejilla">
      <article>
        <h3>📊 El marcador</h3>
        <p>La competición principal. Cada mes es una temporada y el marcador empieza de cero. Gana la mejor media
          de intentos; un fallo cuenta como el peor resultado posible, y faltar un día no sale gratis: tiene nota,
          según lo dura que fuera la palabra. Solo cuentan los laborables en los que juega bastante gente.</p>
      </article>
      <article>
        <h3>🎮 El SuperWordleBros</h3>
        <p>El juego de Joel: las cuadrículas de la jornada anterior se convierten en un nivel de plataformas.
          Eliges tu nombre, juegas cuantas veces quieras y tu mejor marca entra en el ranking del nivel. Gana
          quien saca más estrellas y, a igualdad de estrellas, el más rápido. Cada nivel reparte puntos por
          puesto, y el mes los suma.</p>
      </article>
      <article>
        <h3>🎨 El álbum de figuras</h3>
        <p>La cuadrícula de emojis de cada partida dibuja algo: un loro, una flor, una figura geométrica… Cada
          figura puntúa según lo difícil que es sacarla, y el álbum tiene su propia clasificación. No toca el
          marcador: es el otro premio, y premia a otra gente.</p>
      </article>
      <article>
        <h3>🏅 Las medallas</h3>
        <p>Reconocen lo que la media no ve: jugar todos los días, resolver cuando el grupo se atasca, coleccionar
          figuras… Se ganan en cada temporada y se acumulan en el medallero, sin cambiar la clasificación.</p>
      </article>
    </div>
  </section>`;

const LO_QUE_PUBLICA_EL_BOT = `
  <section class="info-bloque">
    <h2>Lo que publica el bot</h2>
    <p><strong>Cada noche de laborable</strong>, el resumen de la jornada en el canal: la palabra y su significado, el mejor del
      día, la obra del día —el dibujo más curioso— y los podios del marcador, del SuperWordleBros y de las
      figuras. En los últimos días del mes cuenta además cómo está la pelea y qué queda en juego.</p>
    <p><strong>La noche del último día laborable del mes</strong>, en lugar del resumen, la victoria: los podios
      finales y los campeones de cada competición.</p>
  </section>`;

/** Pinta la pestaña Info. `reglas` son las de la instantánea de la temporada en curso, o nada. */
export function pintarInfo(contenedor, reglas) {
  const vigentes = reglasVigentes(reglas);
  const reglasHtml = vigentes
    ? `<p class="nota">Solo las que están en vigor. Los números salen del propio cálculo, así que son los que
        de verdad se usan.</p>${vigentes}`
    : `<p class="nota">Las reglas no están disponibles todavía: viajan con la instantánea de la temporada, y en
        cuanto el pipeline la calcule aparecen aquí.</p>`;

  contenedor.innerHTML = `
    <div class="info reglas">
      <header class="reglas-cabecera">
        <div class="reglas-titular">
          <p class="etiqueta">info</p>
          <h1>Cómo funciona Cloud District Wordle</h1>
        </div>
      </header>
      ${COMO_SE_JUEGA}
      ${COMPETICIONES}
      ${LO_QUE_PUBLICA_EL_BOT}
      <section class="info-bloque">
        <h2>Reglas vigentes</h2>
        ${reglasHtml}
      </section>
    </div>`;
}
