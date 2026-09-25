/**
 * La pestaña SuperWordleBros: el nivel de la última jornada cerrada, jugable.
 *
 * Slice: `juego-de-la-jornada` (openspec/slices/dashboard/juego-de-la-jornada.md).
 *
 * El motor es de **Joel** (`juego/motor.js`) y sus PR lo sustituyen. Esta vista hace lo que el motor no debe
 * hacer: calcular el nivel a partir de la tabla, decir de quién es el juego, cargar el motor solo cuando hace
 * falta, y escribir el texto para compartir. El contrato entre las dos piezas está en `docs/juego-contrato.md`.
 */

import { NIVEL_CONGELADO, RANKING_DEL_JUEGO } from '../data/results.js';
import {
  clasificacionDelNivel, cuandoFue, jugadoresDelGrupo, textoParaCompartir, tiempoPreciso,
} from '../domain/superbros.js';
import { recurso } from '../router.js';

/** Escapa lo que venga de datos antes de meterlo en el DOM. Nombres de jugador incluidos. */
function escapar(texto) {
  return String(texto ?? '').replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
  );
}

/**
 * El aviso que el motor dispara al terminar el nivel, sobre el contenedor:
 *
 *     lienzo.dispatchEvent(new CustomEvent(EVENTO_FIN, { detail: { segundos, estrellas } }));
 *
 * Es **todo** lo que el juego tiene que saber de compartir. Qué se escribe y cómo llega al canal es cosa de
 * la página, así que el formato no depende de que el motor lo repita bien.
 */
export const EVENTO_FIN = 'superbros:fin';

/** El aviso del motor justo antes del primer muro que el salto normal no sube. */
export const EVENTO_PISTA = 'superbros:pista-pisoton';

/**
 * Dónde se recuerda que el tutorial ya se vio. **Una vez por navegador**, no por partida: si saliera todos
 * los días, al tercero dejaría de ser una ayuda. Para volver a verlo está el enlace de la guía.
 */
export const CLAVE_TUTORIAL = 'superbros:tutorial-pisoton-visto';

/** El GIF: grabado del propio motor, así que enseña la física de verdad y no una aproximación. */
export const GIF_DEL_PISOTON = 'assets/juego/pisoton.gif';

/** Si el tutorial ya se vio. Un almacén que falla —navegación privada, cookies bloqueadas— cuenta como «no». */
export function tutorialVisto(almacen) {
  try {
    return almacen?.getItem(CLAVE_TUTORIAL) === 'si';
  } catch {
    return false;
  }
}

/** Apunta que se vio. Si el almacén falla, no pasa nada: como mucho vuelve a salir otro día. */
export function marcarTutorialVisto(almacen) {
  try {
    almacen?.setItem(CLAVE_TUTORIAL, 'si');
  } catch {
    // sin almacén no se recuerda; no es motivo para romper el juego
  }
}

/** El panel del tutorial. Exportado para poder verificarlo sin navegador. */
export function panelDeTutorial(rutaDelGif = recurso(GIF_DEL_PISOTON)) {
  return `
    <div class="tutorial-pisoton" role="dialog" aria-modal="true" aria-labelledby="tutorial-titulo">
      <div class="tutorial-caja">
        <h3 id="tutorial-titulo">¡Muro a la vista! Toca pisotón</h3>
        <img src="${escapar(rutaDelGif)}" width="360" height="240"
             alt="El pisotón: con Shift pulsado, saltar, pulsar la flecha abajo en el aire y Espacio al tocar el suelo para rebotar por encima del muro">
        <ol>
          <li>Ve <strong>corriendo con <kbd>Shift</kbd></strong>.</li>
          <li><kbd>Espacio</kbd> para saltar y, en el aire, <kbd>↓</kbd>.</li>
          <li>Justo al tocar el suelo, <kbd>Espacio</kbd> otra vez: rebotas 5 casillas hacia delante.</li>
        </ol>
        <button type="button" class="tutorial-vale">¡Entendido!</button>
        <p class="etiqueta">El juego está en pausa mientras lo lees: no cuenta en tu tiempo.</p>
      </div>
    </div>`;
}

/**
 * Abre el tutorial **con la partida en pausa**, y la reanuda al cerrarlo.
 *
 * Pausar no es cortesía: el tutorial sale justo delante de un muro, con el cronómetro corriendo, y leer cómo
 * se salta costaría segundos en el ranking. Recibe la partida por parámetro para poder probarlo con un doble.
 */
export function abrirTutorial(contenedor, partida, almacen) {
  if (contenedor.querySelector('.tutorial-pisoton')) return;
  partida?.scene?.pause?.('main');
  contenedor.insertAdjacentHTML('beforeend', panelDeTutorial());
  const panel = contenedor.querySelector('.tutorial-pisoton');
  const cerrar = () => {
    panel.remove();
    marcarTutorialVisto(almacen);
    partida?.scene?.resume?.('main');
    contenedor.querySelector(`#${ID_DEL_CONTENEDOR}`)?.focus({ preventScroll: true });
  };
  const boton = panel.querySelector('.tutorial-vale');
  boton.addEventListener('click', cerrar);
  // El motor captura Espacio para saltar, así que un botón no se pulsa con él: se cierra con Intro o Escape.
  panel.addEventListener('keydown', (evento) => {
    if (evento.key === 'Enter' || evento.key === 'Escape') {
      evento.preventDefault();
      cerrar();
    }
  });
  boton.focus();
}

/** Las teclas que usa el juego y que el navegador usa para mover la página. */
const TECLAS_DEL_JUEGO = new Set([' ', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight']);

/**
 * Si una pulsación es del juego y no debe mover la página. **Con o sin modificadores.**
 *
 * Phaser ya bloquea el scroll de las teclas que usa, pero **no cuando va pulsado Shift, Ctrl, Alt o Cmd**: lo
 * hace a propósito, para no romper los atajos del navegador. Y el pisotón se hace corriendo con Shift, así
 * que justo al rebotar, Shift + Espacio —que en cualquier navegador es «subir la página»— mandaba la página
 * hacia arriba y el juego desaparecía de la vista. El resto —rueda, trackpad, barra, Re Pág— sigue libre.
 */
export function esTeclaDelJuego(evento) {
  return TECLAS_DEL_JUEGO.has(evento?.key);
}

/** Dónde se monta el motor y de dónde lee el nivel. */
export const ID_DEL_CONTENEDOR = 'juego-contenedor';

/**
 * Phaser, con la versión fijada. Se carga **solo en esta pestaña y solo una vez**: pesa lo suyo, y el resto
 * de la web no lo necesita para nada.
 */
export const PHASER = 'https://cdn.jsdelivr.net/npm/phaser@3.70.0/dist/phaser.min.js';

/**
 * Los controles, tal y como los define el motor de Joel. **Solo teclado**: el prototipo no trae controles
 * táctiles, así que en el móvil se ve pero no se juega — eso llega, si llega, con un PR suyo.
 */
export const CONTROLES = [
  { teclas: ['←', '→'], alternativa: ['A', 'D'], que: 'moverte' },
  { teclas: ['Shift'], que: 'correr' },
  // Solo Espacio: el motor lee `cursors.space` y nada más. ↑ y W NO saltan — la primera versión de esta
  // guía lo decía, y se comprobó contra el código del motor antes de publicarla.
  { teclas: ['Espacio'], que: 'saltar — cuanto más lo mantienes, más alto' },
  // El pisotón (propuesta sobre el motor de Joel): rebotar 5 casillas cuesta un combo con ventana corta.
  { teclas: ['↓'], alternativa: ['S'], que: 'en el aire: pisotón — pulsa Espacio justo al caer y rebotas 5 casillas hacia delante (corre con Shift para llegar lejos)' },
  { teclas: ['R'], que: 'volver a empezar' },
];

/**
 * La cabecera. **La autoría va aquí y es parte del comportamiento**, no un adorno: el juego es de Joel y
 * quien lo abra tiene que saberlo sin preguntar.
 */
export function cabecera(jornada, cuando = '') {
  const detalle = Number.isInteger(jornada)
    ? ` · ${escapar(cuando || 'jornada')} · #${escapar(jornada)}`
    : '';
  return `
    <header class="bloque-cab amarillo">
      <h2>SUPER WORDLE BROS.</h2>
      <span>un juego de Joel${detalle}</span>
    </header>`;
}

/** Las teclas de una fila de la guía. */
function teclas(lista) {
  return lista.map((t) => `<kbd>${escapar(t)}</kbd>`).join(' ');
}

/** La guía de controles. Exportada para poder verificarla sin navegador. */
export function guiaDeControles() {
  const filas = CONTROLES.map(({ teclas: principales, alternativa, que }) => `
      <li>
        <span class="teclas">${teclas(principales)}${alternativa ? ` <span class="o">o</span> ${teclas(alternativa)}` : ''}</span>
        <span class="que">${escapar(que)}</span>
      </li>`).join('');
  return `
    <section class="guia-controles" aria-label="Controles del juego">
      <h3>Cómo se juega</h3>
      <ul>${filas}</ul>
      <p class="etiqueta">Llega a la bandera en el menor tiempo, recogiendo las estrellas por el camino. Se
        juega con teclado. <button type="button" class="ver-tutorial">¿Cómo se hace el pisotón?</button></p>
    </section>`;
}

/**
 * Dónde se recuerda quién eres. Por navegador, como el tutorial: quien juega desde su portátil no tiene que
 * volver a elegirse cada día.
 */
export const CLAVE_JUGADOR = 'superbros:jugador';

/** El jugador recordado, si sigue en la lista. Un almacén que falla o un nombre que ya no está cuentan como nadie. */
export function jugadorRecordado(almacen, jugadores) {
  let guardado = null;
  try {
    guardado = almacen?.getItem(CLAVE_JUGADOR) ?? null;
  } catch {
    return null;
  }
  return (jugadores ?? []).some((j) => j.jugador === guardado) ? guardado : null;
}

/** Apunta quién eres. Si el almacén falla, no pasa nada: se vuelve a elegir otro día. */
export function recordarJugador(almacen, jugador) {
  try {
    almacen?.setItem(CLAVE_JUGADOR, jugador);
  } catch {
    // sin almacén no se recuerda; el ranking funciona igual
  }
}

/** El desplegable «¿Quién eres?». Exportado para poder verificarlo sin navegador. */
export function selectorDeJugador(jugadores, elegido) {
  const opciones = (jugadores ?? []).map(({ jugador, nombre }) =>
    `<option value="${escapar(jugador)}"${jugador === elegido ? ' selected' : ''}>${escapar(nombre)}</option>`,
  ).join('');
  return `
    <label class="quien-eres">
      <span>¿Quién eres?</span>
      <select class="quien-eres-lista">
        <option value=""${elegido ? '' : ' selected'}>— elige tu nombre —</option>${opciones}
      </select>
    </label>`;
}

/** La tabla del ranking de un nivel. Exportada para poder verificarla sin navegador. */
export function rankingDelNivel(clasificacion, elegido) {
  if (!clasificacion?.length) {
    return '<p class="etiqueta">Nadie ha terminado este nivel todavía. ¡Estrénalo!</p>';
  }
  const filas = clasificacion.map((f) => `
        <tr${f.jugador === elegido ? ' class="es-tuya"' : ''}>
          <td>${escapar(f.puesto)}</td>
          <td>${escapar(f.nombre)}</td>
          <td>${escapar(tiempoPreciso(f.segundos))}</td>
          <td>⭐ ${escapar(f.estrellas)}</td>
        </tr>`).join('');
  return `
    <table class="tabla-ranking-juego">
      <thead><tr><th>#</th><th>Jugador</th><th>Tiempo</th><th>Estrellas</th></tr></thead>
      <tbody>${filas}
      </tbody>
    </table>`;
}

/**
 * Lo que pasa con cada partida terminada, sin DOM: quién eres, qué partida espera a que lo digas, y qué se
 * le cuenta a quien juega. Recibe la API del ranking por parámetro para poder probarlo sin red.
 *
 * - **Sin nombre, la partida espera.** Al elegirlo se guarda esa misma, sin repetir el nivel.
 * - **Cada llegada a la meta se manda**: reintentar no tiene límite, y la base de datos decide si mejora.
 * - Un fallo se cuenta y no se arrastra: la siguiente partida vuelve a intentarlo.
 */
export function controlDelRanking({ api, jornada, total }) {
  let jugador = null;
  let pendiente = null;

  async function guardar(partida) {
    const conseguidas = Math.min(Math.max(0, Math.floor(Number(partida.estrellas) || 0)), total);
    const marca = {
      jornada,
      jugador,
      segundos: Math.round((Number(partida.segundos) || 0) * 100) / 100,
      estrellas: conseguidas,
    };
    try {
      const { mejora, segundos } = await api.registrar(marca);
      return mejora
        ? { estado: 'mejora', texto: `¡Nueva marca! ${tiempoPreciso(segundos)} guardado en el ranking.` }
        : { estado: 'sin-mejora', texto: `Tu mejor marca sigue siendo ${tiempoPreciso(segundos)}. ¡Otra vez!` };
    } catch {
      return { estado: 'error', texto: 'El tiempo no se ha podido guardar. Puedes seguir jugando y compartirlo igual.' };
    }
  }

  return {
    async elegir(quien) {
      jugador = quien || null;
      if (!jugador || !pendiente) return null;
      const partida = pendiente;
      pendiente = null;
      return guardar(partida);
    },
    async terminar(partida) {
      if (!jugador) {
        pendiente = partida;
        return { estado: 'sin-jugador', texto: 'Elige quién eres para guardar este tiempo en el ranking.' };
      }
      return guardar(partida);
    },
  };
}

/** La vista completa, en HTML. Exportada para poder verificarla sin navegador. */
export function vista(nivel, jornada, cuando = '', jugadores = [], elegido = null) {
  if (!nivel) {
    return `
      <section class="bloque">
        ${cabecera(null)}
        <p class="etiqueta">todavía no hay ningún nivel listo: el de cada jornada se congela a las 04:00 del día siguiente</p>
      </section>`;
  }
  return `
    <section class="bloque">
      ${cabecera(jornada, cuando)}
      <p class="etiqueta">${nivel.labels.length} tramos · las cuadrículas de ese día son el escenario</p>
      <div id="${ID_DEL_CONTENEDOR}" class="juego-lienzo" tabindex="0"></div>
      <section class="ranking-juego" aria-label="Ranking del nivel">
        <h3>Ranking del nivel</h3>
        ${selectorDeJugador(jugadores, elegido)}
        <p class="estado-marca etiqueta" role="status"></p>
        <div class="ranking-juego-tabla"><p class="etiqueta">cargando el ranking…</p></div>
      </section>
      ${guiaDeControles()}
    </section>`;
}

/**
 * El panel para compartir: el texto a la vista y un botón que lo copia.
 *
 * **Copiar, no publicar.** La persona lo pega en el canal como pega su Wordle, y así el mensaje lo firma
 * ella. La web no tiene —ni debe tener— forma de escribir en Slack: el token del bot vive en el workflow, y
 * lleva permiso para leer el historial entero del canal.
 */
export function panelDeCompartir(texto) {
  return `
    <div class="compartir">
      <p class="etiqueta">¡Nivel completado! Cópialo y pégalo en el canal:</p>
      <pre class="compartir-texto">${escapar(texto)}</pre>
      <button type="button" class="compartir-boton">Copiar para el canal</button>
    </div>`;
}

/** Copia al portapapeles, con el camino antiguo por si el navegador no deja usar el moderno. */
async function copiar(texto, documento) {
  try {
    await navigator.clipboard.writeText(texto);
    return true;
  } catch {
    const area = documento.createElement('textarea');
    area.value = texto;
    documento.body.appendChild(area);
    area.select();
    const hecho = documento.execCommand?.('copy') ?? false;
    area.remove();
    return hecho;
  }
}

let cargandoPhaser = null;

/** Phaser una sola vez por página. Si la carga falla, se puede volver a intentar al volver a la pestaña. */
function cargarPhaser(documento) {
  const ventana = documento.defaultView;
  if (ventana?.Phaser) return Promise.resolve(ventana.Phaser);
  cargandoPhaser ??= new Promise((resolver, rechazar) => {
    const script = documento.createElement('script');
    script.src = PHASER;
    script.onload = () => resolver(ventana.Phaser);
    script.onerror = () => {
      cargandoPhaser = null;
      rechazar(new Error('no se pudo cargar Phaser'));
    };
    documento.head.appendChild(script);
  });
  return cargandoPhaser;
}

let partida = null;
let turno = 0;

/**
 * Para la partida en curso. **La app lo llama antes de pintar cualquier vista.**
 *
 * Sin esto, al cambiar de pestaña el juego seguía vivo: el lienzo desaparecía del DOM pero Phaser seguía
 * corriendo su bucle y **capturando las flechas y el espacio en toda la web**, que dejaba de poder hacer
 * scroll con el teclado en las demás pestañas.
 */
export function desmontarJuego() {
  turno += 1;
  partida?.destroy(true);
  partida = null;
}

/**
 * `localStorage`, o `null`. Pedirlo ya puede lanzar —navegación privada, cookies bloqueadas— y sin almacén se
 * juega igual: solo se olvidan el tutorial visto y quién eres.
 */
function almacenDe(documento) {
  try {
    return documento?.defaultView?.localStorage ?? null;
  } catch {
    return null;
  }
}

/**
 * La partida que se juega: el último nivel congelado, `{ jornada, fecha, nivel }`, o `null` si no hay ninguno
 * o no se puede leer. **Un fallo de lectura no rompe la pestaña**: dice que no hay nivel, como sin datos.
 */
export async function nivelParaJugar(fuente) {
  try {
    const partida = await fuente.ultimo();
    return partida?.nivel ? partida : null;
  } catch {
    return null;
  }
}

/**
 * Pinta la pestaña: lee el nivel congelado, lo deja en el contenedor y monta el motor. `hoy` es `AAAA-MM-DD`
 * y solo sirve para decir «jornada de ayer». `ranking` y `niveles` son las APIs reales por defecto.
 */
export async function pintarJuego(contenedor, resultados, hoy, ranking = RANKING_DEL_JUEGO, niveles = NIVEL_CONGELADO) {
  desmontarJuego();
  const miTurno = turno;
  contenedor.innerHTML = `
    <section class="bloque">
      ${cabecera(null)}
      <p class="etiqueta">cargando el nivel…</p>
    </section>`;
  // `congelado` y no `partida`: ese nombre es el de la partida de Phaser, a nivel de módulo, y taparlo aquí
  // convertía `partida = montar(...)` en una asignación a una constante —el juego no arrancaba—.
  const congelado = await nivelParaJugar(niveles);
  // Si mientras se leía se cambió de pestaña, no se pinta: sería escribir sobre otra vista.
  if (miTurno !== turno) return null;
  const jornada = congelado?.jornada ?? null;
  const nivel = congelado?.nivel ?? null;

  const documento = contenedor.ownerDocument;
  const almacen = almacenDe(documento);
  const jugadores = jugadoresDelGrupo(resultados);
  let elegido = jugadorRecordado(almacen, jugadores);
  contenedor.innerHTML = vista(nivel, jornada, cuandoFue(congelado?.fecha ?? null, hoy), jugadores, elegido);

  const lienzo = contenedor.querySelector(`#${ID_DEL_CONTENEDOR}`);
  if (!lienzo || !nivel) return nivel;
  lienzo.dataset.nivel = JSON.stringify(nivel);

  // El ranking del nivel. Todo lo que llega tarde —una lectura, una marca guardada— se descarta si mientras
  // tanto se cambió de pestaña: escribiría sobre una vista que ya no está.
  const control = controlDelRanking({ api: ranking, jornada, total: nivel.collectibles.length });
  const estado = contenedor.querySelector('.estado-marca');
  const tabla = contenedor.querySelector('.ranking-juego-tabla');
  const selector = contenedor.querySelector('.quien-eres-lista');
  const contar = (resultado) => {
    if (!resultado || miTurno !== turno) return;
    estado.textContent = resultado.texto;
    selector.closest('.quien-eres')?.classList.toggle('pide-nombre', resultado.estado === 'sin-jugador');
  };
  const refrescar = () => ranking.leer(jornada)
    .then((marcas) => {
      if (miTurno === turno) tabla.innerHTML = rankingDelNivel(clasificacionDelNivel(marcas, jugadores), elegido);
    })
    .catch(() => {
      if (miTurno === turno) tabla.innerHTML = '<p class="etiqueta">No se ha podido cargar el ranking.</p>';
    });
  control.elegir(elegido);
  refrescar();
  selector.addEventListener('change', async () => {
    elegido = selector.value || null;
    recordarJugador(almacen, elegido ?? '');
    contar(await control.elegir(elegido));
    refrescar();
  });

  // Mientras el juego tiene el foco, sus teclas no mueven la página. Con el foco en otra parte, las flechas
  // vuelven a hacer scroll como siempre.
  //
  // **Va en el padre, no en el lienzo, y no es un detalle.** Phaser descarta cualquier tecla que ya llegue
  // bloqueada (`if (event.defaultPrevented) return`), y un bloqueo en el propio lienzo se ejecutaba antes que
  // él: le quitaba al juego las flechas y el espacio y lo dejaba injugable. En el padre, la tecla ya ha pasado
  // por Phaser cuando se bloquea; y bloquearla a esa altura sigue impidiendo el scroll, porque el navegador
  // lo decide al final del recorrido.
  lienzo.parentElement.addEventListener('keydown', (evento) => {
    if (lienzo.contains(evento.target) && esTeclaDelJuego(evento)) evento.preventDefault();
  });
  // Si el foco se va con una tecla pulsada, su «soltar» llega a otro sitio y el personaje seguiría corriendo
  // solo. Al perder el foco se sueltan todas.
  lienzo.addEventListener('blur', () => partida?.scene?.getScene?.('main')?.input?.keyboard?.resetKeys?.());
  // Un clic en el juego le devuelve el foco. El navegador lo haría solo, pero Phaser anula la pulsación del
  // ratón sobre el lienzo y con ella el cambio de foco: sin esto, quien sacaba el foco no podía volver.
  lienzo.addEventListener('pointerdown', () => lienzo.focus({ preventScroll: true }));

  // **El total lo pone la página, no el motor.** Es el número de coleccionables que ella misma generó: si el
  // motor contara mal, el canal no leería un `11/10`.
  //
  // **En cada partida, no solo en la primera**: tras `R` se vuelve a terminar, y cada llegada a la meta
  // cambia el texto para compartir y va al ranking.
  const alTerminar = async (evento) => {
    const { segundos, estrellas } = evento.detail ?? {};
    const texto = textoParaCompartir({ jornada, segundos, estrellas, total: nivel.collectibles.length });
    contenedor.querySelector('.compartir')?.remove();
    lienzo.insertAdjacentHTML('afterend', panelDeCompartir(texto));
    const boton = contenedor.querySelector('.compartir-boton');
    boton?.addEventListener('click', async () => {
      boton.textContent = (await copiar(texto, documento))
        ? '¡Copiado! Ahora pégalo en el canal'
        : 'No se pudo copiar: selecciona el texto a mano';
    });
    const resultado = await control.terminar({ segundos, estrellas });
    contar(resultado);
    if (resultado.estado === 'mejora' || resultado.estado === 'sin-mejora') refrescar();
  };
  lienzo.addEventListener(EVENTO_FIN, alTerminar);

  Promise.all([cargarPhaser(documento), import('../juego/motor.js')])
    .then(([Phaser, { montar }]) => {
      // Si mientras cargaba se cambió de pestaña, no se monta: sería un juego fantasma sobre un lienzo que
      // ya no está en la página.
      if (miTurno !== turno || !lienzo.isConnected) return;
      partida = montar(lienzo, nivel, Phaser);
      lienzo.addEventListener(EVENTO_PISTA, () => {
        if (!tutorialVisto(almacen)) abrirTutorial(contenedor, partida, almacen);
      });
      contenedor.querySelector('.ver-tutorial')
        ?.addEventListener('click', () => abrirTutorial(contenedor, partida, almacen));
      // **El hueco toma la proporción del juego**, leída del propio motor y no copiando sus fórmulas: así
      // el lienzo se llena sin franjas negras, y si Joel cambia la resolución en un PR sigue encajando.
      lienzo.style.aspectRatio = `${partida.config.width} / ${partida.config.height}`;
      partida.scale?.refresh?.();
      lienzo.focus({ preventScroll: true });
    })
    .catch(() => {
      if (miTurno !== turno) return;
      lienzo.innerHTML = '<p class="etiqueta">No se ha podido cargar el juego. Recarga la página para reintentarlo.</p>';
    });
  return nivel;
}
