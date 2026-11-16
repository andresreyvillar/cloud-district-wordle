/**
 * El juego del evento en el móvil de cada participante: `/evento`.
 *
 * Slice: `frase-del-evento`. Reglas de «La frase del día»: la frase está tapada y se destapa con palabras válidas de
 * cinco letras, cinco como mucho; se gana al destapar todas sus letras. Tres piezas:
 * - `controlDelEvento` guarda el estado y habla con la API. Sin DOM: se prueba con una API falsa.
 * - `vistaDelEvento` pinta ese estado. Pura: el reloj entra por parámetro.
 * - `montarEvento` es el borde: eventos del DOM, el cronómetro que avanza y el sondeo del estado.
 *
 * La frase entera no está nunca aquí hasta que termina el evento: el servidor manda solo lo destapado. Tampoco la
 * posición: durante el evento nadie ve su puesto (decisión del dueño).
 */

import { escapar } from '../ui/shell.js';
import {
  INTENTOS, LETRAS, celdasDeLaFrase, coloresDelTeclado, cuentaAtras, desfase, formatoTiempo, letraDeTecla,
  momentoDelEvento, tokenAleatorio,
} from './dominio.js';

const CLAVE_DEL_TOKEN = 'evento:token';

const MENSAJE_SIN_RED = 'No se ha podido conectar. Revisa la conexión y prueba otra vez.';

/**
 * El estado del participante y lo que puede hacer. `almacen` es `{leer, guardar}`; `reloj`, los ms locales;
 * `palabras`, el conjunto de palabras válidas si se ha podido cargar (si no, decide solo el servidor).
 */
export function controlDelEvento({ api, almacen, reloj, palabras = null, generarToken = tokenAleatorio }) {
  const clave = `${CLAVE_DEL_TOKEN}:${api.evento}`;
  const s = {
    token: almacen.leer(clave),
    nombre: null,
    // Hay token pero no se ha podido leer su partida (sin red al recargar): se reintenta, sin pedir el nombre.
    recuperando: false,
    estado: null,
    desfase: 0,
    partidas: new Map(),
    // La frase que se está mirando; `null` es la lista de frases.
    seleccionada: null,
    escrito: [],
    aviso: null,
    ranking: null,
    enviando: false,
    empezando: false,
    entrando: false,
    sinConexion: false,
    // La explicación de cómo se juega, abierta desde la cabecera.
    ayuda: false,
    // La contraseña de acceso, si el evento la pide. Solo en memoria: una vez dentro, basta el token.
    clave: null,
  };

  const ahora = () => reloj() + s.desfase;
  const momento = () => momentoDelEvento(s.estado, ahora());
  const liberada = (orden) => {
    const m = momento();
    return m.tipo === 'en-curso' && m.liberadas.some((f) => f.orden === orden);
  };

  async function refrescar() {
    const pedido = reloj();
    try {
      const estado = await api.estado(s.token, s.clave);
      // La hora del servidor es la de mitad del viaje: sin descontar la latencia, el móvil iba adelantado lo que
      // tarda la petición.
      s.desfase = desfase(estado.ahora, (pedido + reloj()) / 2);
      s.estado = estado;
      s.sinConexion = false;
      if (estado.terminado && !s.ranking) s.ranking = await api.ranking(s.token, s.clave);
    } catch (error) {
      if (error.tipo === 'red') s.sinConexion = true;
      else s.aviso = error.message;
    }
  }

  /** Rehace lo del participante desde el servidor: su nombre y sus partidas. */
  async function sincronizar() {
    if (!s.token) return;
    try {
      const mia = await api.miPartida(s.token);
      s.nombre = mia.nombre;
      for (const partida of mia.partidas ?? []) s.partidas.set(partida.orden, partida);
      s.recuperando = false;
    } catch (error) {
      // Solo un token que el evento no conoce (otro evento, una base reiniciada) se tira: se vuelve a entrar. Ante
      // cualquier otro fallo se conserva y se reintenta en el siguiente sondeo, o el participante se quedaría
      // fuera con su propio nombre ocupado.
      if (error.tipo === 'rechazo' && /no estás apuntado|evento desconocido/.test(error.message)) {
        s.token = null;
        s.recuperando = false;
      } else {
        s.recuperando = true;
        s.sinConexion = error.tipo === 'red';
      }
    }
  }

  async function arrancar() {
    await sincronizar();
    await refrescar();
  }

  /**
   * Prueba la contraseña de acceso: si es la buena, el servidor entrega el estado y la web pasa a pedir el nombre.
   * Antes de eso no se enseña nada del evento.
   */
  async function desbloquear(clave) {
    if (!String(clave ?? '')) {
      s.aviso = 'Escribe la contraseña.';
      return;
    }
    s.clave = clave;
    await refrescar();
    if (s.estado?.bloqueado) {
      s.clave = null;
      s.aviso = 'Contraseña incorrecta.';
    } else {
      s.aviso = null;
    }
  }

  /** Entra con un nombre y, si el evento la pide, la contraseña (la que ya abrió el evento). */
  async function entrar(nombre, contrasena = s.clave) {
    if (!String(nombre ?? '').trim()) {
      s.aviso = 'Escribe tu nombre para entrar.';
      return;
    }
    if (s.estado?.con_clave && !String(contrasena ?? '')) {
      s.aviso = 'Escribe la contraseña del evento.';
      return;
    }
    if (s.entrando) return;
    s.entrando = true;
    // El token se fija antes de llamar: un doble toque en Entrar manda el mismo, y el servidor devuelve el mismo
    // nombre en vez de decir que está ocupado.
    s.token ??= generarToken();
    const token = s.token;
    try {
      const respuesta = await api.unirse(nombre, token, contrasena || null);
      almacen.guardar(clave, token);
      s.nombre = respuesta.nombre;
      s.aviso = null;
    } catch (error) {
      s.aviso = error.tipo === 'rechazo' ? error.message : MENSAJE_SIN_RED;
    } finally {
      s.entrando = false;
    }
  }

  /** Mira una frase de la lista (o vuelve a la lista con `null`). */
  function elegir(orden) {
    s.seleccionada = orden;
    s.escrito = [];
    s.aviso = null;
  }

  async function empezar() {
    const orden = s.seleccionada;
    if (orden === null || !liberada(orden) || s.empezando) return;
    s.empezando = true;
    try {
      const yaEmpezada = s.partidas.has(orden);
      s.partidas.set(orden, await api.empezar(s.token, orden));
      // Un segundo toque en Empezar no borra lo que ya se ha escrito.
      if (!yaEmpezada) s.escrito = [];
      s.aviso = null;
    } catch (error) {
      s.aviso = error.tipo === 'rechazo' ? error.message : MENSAJE_SIN_RED;
      if (error.tipo === 'rechazo') await refrescar();
    } finally {
      s.empezando = false;
    }
  }

  function enJuego() {
    const partida = s.partidas.get(s.seleccionada);
    return partida && !partida.terminada_en && liberada(partida.orden) ? partida : null;
  }

  function teclear(letra) {
    if (!enJuego() || s.enviando) return;
    if (s.escrito.length < LETRAS) s.escrito.push(letra);
    s.aviso = null;
  }

  function borrar() {
    if (!enJuego() || s.enviando) return;
    s.escrito.pop();
    s.aviso = null;
  }

  /**
   * Envía la palabra escrita. Si falta alguna letra, o la palabra no está en la lista, no se envía nada y el intento
   * no se gasta.
   */
  async function enviar() {
    const partida = enJuego();
    if (!partida || s.enviando) return;
    const faltan = LETRAS - s.escrito.length;
    if (faltan > 0) {
      s.aviso = faltan === 1 ? 'Falta 1 letra.' : `Faltan ${faltan} letras.`;
      return;
    }
    const palabra = s.escrito.join('');
    if (palabras && !palabras.has(palabra)) {
      s.aviso = 'La palabra no está en la lista.';
      return;
    }
    s.enviando = true;
    try {
      // El número del intento hace seguro reenviar: si el primero llegó y se perdió la respuesta, el servidor lo
      // reconoce y no gasta otro.
      const numero = (partida.intentos?.length ?? 0) + 1;
      s.partidas.set(partida.orden, await api.intentar(s.token, partida.orden, palabra, numero));
      s.escrito = [];
      s.aviso = null;
    } catch (error) {
      // Sin red, lo escrito se queda: la palabra no ha llegado y no cuenta.
      s.aviso = error.tipo === 'red' ? 'No se ha podido enviar. Tu palabra sigue escrita: prueba otra vez.' : error.message;
      // Un rechazo puede ser que la palabra no vale (y se queda escrita para corregirla) o que el servidor va por
      // delante (otra pestaña, el evento terminó): se rehace todo.
      if (error.tipo === 'rechazo') {
        await sincronizar();
        await refrescar();
      }
    } finally {
      s.enviando = false;
    }
  }

  /** Abre o cierra la explicación. */
  function ayuda() {
    s.ayuda = !s.ayuda;
  }

  return {
    estado: s, ahora, momento, arrancar, sincronizar, refrescar, desbloquear, entrar, elegir, empezar, teclear, borrar,
    enviar, ayuda,
  };
}

// ── Vista ─────────────────────────────────────────────────────────────────────────────────────────────────

const CLASE = { G: 'verde', Y: 'amarilla', '.': 'gris' };

/** La frase con lo destapado: casillas tapadas, letras destapadas y signos en su sitio. */
export function panelDeLaFrase(visible) {
  const palabras = celdasDeLaFrase(visible);
  // La palabra más larga fija el ancho de las casillas: «transformación» tiene que caber en 320 px.
  const ancho = Math.max(1, ...palabras.map((palabra) => palabra.length));
  return `<div class="ev-frase" style="--ev-ancho: ${ancho}" aria-label="La frase">${palabras.map((palabra) => (
    `<span class="ev-palabra">${palabra.map((celda) => {
      if (celda.tipo === 'tapada') return '<span class="ev-casilla"></span>';
      if (celda.tipo === 'letra') return `<span class="ev-casilla destapada">${escapar(celda.texto.toUpperCase())}</span>`;
      return `<span class="ev-signo">${escapar(celda.texto)}</span>`;
    }).join('')}</span>`)).join('')}</div>`;
}

/** El tablero de cinco palabras: las enviadas con sus colores, la que se escribe y las que quedan. */
export function tablero(partida, escrito = []) {
  const filas = [];
  const celdas = (letras, colores) => Array.from({ length: LETRAS }, (_, i) => {
    const letra = letras[i] ?? '';
    const color = colores ? ` ${CLASE[colores[i]] ?? ''}` : '';
    return `<span class="ev-celda${letra ? ' llena' : ''}${color}">${escapar(letra.toUpperCase())}</span>`;
  }).join('');
  for (const { palabra, colores } of partida.intentos ?? []) filas.push(`<div class="ev-fila">${celdas([...palabra], colores)}</div>`);
  if (!partida.terminada_en && filas.length < INTENTOS) filas.push(`<div class="ev-fila ev-actual">${celdas(escrito, null)}</div>`);
  while (filas.length < INTENTOS) filas.push(`<div class="ev-fila">${celdas([], null)}</div>`);
  return `<div class="ev-tablero" aria-label="Tablero">${filas.join('')}</div>`;
}

const FILAS_DEL_TECLADO = ['qwertyuiop', 'asdfghjklñ', 'zxcvbnm'];

export function teclado(intentos) {
  const colores = coloresDelTeclado(intentos);
  const tecla = (letra) => {
    const color = colores.get(letra);
    return `<button type="button" class="ev-tecla${color ? ` ${CLASE[color]}` : ''}" data-tecla="${letra}">${letra.toUpperCase()}</button>`;
  };
  const [primera, segunda, tercera] = FILAS_DEL_TECLADO;
  return `<div class="ev-teclado">
    <div>${[...primera].map(tecla).join('')}</div>
    <div>${[...segunda].map(tecla).join('')}</div>
    <div><button type="button" class="ev-tecla ancha" data-accion="enviar">Enviar</button>${[...tercera].map(tecla).join('')}<button type="button" class="ev-tecla ancha" data-accion="borrar" aria-label="Borrar">⌫</button></div>
  </div>`;
}

/**
 * Cómo se juega, con un ejemplo: casi nadie conoce este modo, y sin él la primera palabra se gasta sin entender por
 * qué una letra sale amarilla. El ejemplo es una frase inventada, no una del evento.
 */
export function comoSeJuega() {
  const ejemplo = tablero({ intentos: [{ palabra: 'sacas', colores: 'GG.GG' }], terminada_en: 'ejemplo' })
    .replace(/<div class="ev-fila"><span class="ev-celda"><\/span>(<span class="ev-celda"><\/span>){4}<\/div>/g, '');
  return `<section class="ev-ayuda" aria-label="Cómo se juega">
    <h2>Cómo se juega</h2>
    <ol>
      <li>La frase está <strong>tapada</strong>. Destápala escribiendo <strong>palabras de 5 letras</strong>: tienes
        <strong>5 palabras</strong> por frase.</li>
      <li>Cada letra de tu palabra se colorea:
        <ul class="ev-leyenda">
          <li><span class="ev-celda verde">S</span><span>está en la frase: se destapa <strong>en todos sus sitios</strong>.</span></li>
          <li><span class="ev-celda amarilla">S</span><span>está, pero ya la tenías destapada: no suma nada.</span></li>
          <li><span class="ev-celda gris">C</span><span>no está en la frase.</span></li>
        </ul>
      </li>
      <li><strong>Ganas al destapar todas las letras.</strong> No hace falta escribir la frase.</li>
    </ol>
    <p class="ev-nota">Ejemplo: con la frase «SOL Y MAR», la palabra SACAS destapa la S y la A.</p>
    ${ejemplo}${panelDeLaFrase('s__ _ _a_')}
    <p class="ev-truco"><strong>Truco:</strong> empieza con palabras de letras distintas y frecuentes (vocales, S, R,
      N, L, T). Cuando intuyas la frase, busca palabras con las letras que te faltan.</p>
    <p class="ev-nota">El tiempo corre desde que pulsas Empezar y no se para aunque cierres la web. Gana quien resuelve
      más frases y, a igualdad, quien tarda menos.</p>
  </section>`;
}

function soluciones(estado) {
  const con = (estado?.frases ?? []).filter((f) => f.solucion);
  if (!con.length) return '';
  return `<section class="ev-soluciones"><h2>Las frases</h2><ol>${con.map((f) => (
    `<li value="${Number(f.orden)}">${escapar(f.solucion)}</li>`
  )).join('')}</ol></section>`;
}

const frases = (n) => `${n} ${n === 1 ? 'frase' : 'frases'}`;

export function vistaRanking(filas, miNombre) {
  return `<section class="ev-ranking"><h2>Ranking final</h2><ol>${(filas ?? []).map((f) => `
    <li class="${f.nombre === miNombre ? 'mia' : ''}">
      <span class="ev-puesto">${Number(f.puesto)}</span>
      <span class="ev-nombre">${escapar(f.nombre)}</span>
      <span class="ev-marca-final">${frases(Number(f.resueltas))} · ${formatoTiempo(f.tiempo_ms)}</span>
    </li>`).join('')}</ol></section>`;
}

function aviso(s) {
  if (s.enviando) return '<p class="ev-aviso enviando" role="status">Enviando…</p>';
  const texto = s.aviso ?? (s.sinConexion ? 'Sin conexión: reintentando…' : null);
  return texto ? `<p class="ev-aviso" role="alert">${escapar(texto)}</p>` : '';
}

function estadoDeLaPartida(partida, ahora) {
  if (!partida) return 'Por jugar';
  if (partida.resuelta) return `Resuelta en ${formatoTiempo(partida.tiempo_ms)}`;
  if (partida.terminada_en) return 'Sin resolver';
  return `Jugando · ${formatoTiempo(ahora - Date.parse(partida.empezada_en))}`;
}

function lista(s, m, ahora) {
  const tarjetas = m.liberadas.map((f) => {
    const partida = s.partidas.get(f.orden);
    const clase = partida?.resuelta ? ' resuelta' : partida?.terminada_en ? ' perdida' : partida ? ' jugando' : '';
    return `<li><button type="button" class="ev-tarjeta${clase}" data-elegir="${Number(f.orden)}">
      <strong>Frase ${Number(f.orden)}</strong><span>${estadoDeLaPartida(partida, ahora)}</span></button></li>`;
  }).join('');
  const siguiente = m.siguiente
    ? `<p class="ev-nota">La frase ${Number(m.siguiente.orden)} sale en <strong class="ev-reloj" data-cuenta-atras="${Date.parse(m.siguiente.abre_en)}">${cuentaAtras(m.faltaMs)}</strong></p>`
    : '<p class="ev-nota">Ya están todas las frases. El ranking sale cuando el presentador termine el evento.</p>';
  return `<section class="ev-lista"><h1>Frases</h1><ol class="ev-tarjetas">${tarjetas}</ol>${siguiente}${aviso(s)}</section>`;
}

/**
 * Tras terminar una frase, el paso a la siguiente: un botón si ya está liberada; si no, el mismo botón apagado con
 * lo que falta para que salga, que se enciende solo al llegar a cero (la cuenta atrás pide el estado y se repinta).
 */
function aLaSiguiente(s, orden, m, ahora) {
  const siguiente = (s.estado?.frases ?? []).find((f) => f.orden === orden + 1);
  if (!siguiente) {
    return '<p class="ev-nota">Era la última frase. El ranking sale cuando el presentador termine el evento.</p>';
  }
  const n = Number(siguiente.orden);
  if (m.liberadas.some((f) => f.orden === n)) {
    return `<button type="button" class="ev-boton grande" data-elegir="${n}">Ir a la frase ${n}</button>`;
  }
  const abre = Date.parse(siguiente.abre_en);
  return `<button type="button" class="ev-boton grande" disabled>La frase ${n} sale en `
    + `<strong class="ev-reloj" data-cuenta-atras="${abre}">${cuentaAtras(abre - ahora)}</strong></button>`;
}

function frase(s, orden, m, ahora) {
  const volver = '<button type="button" class="ev-volver" data-accion="volver">← Frases</button>';
  const partida = s.partidas.get(orden);
  if (!partida) {
    return `<section class="ev-empezar">${volver}<h1>Frase ${orden}</h1>
      <p>Destápala con palabras de cinco letras: cada letra que esté en la frase se destapa en todos sus sitios.
      Tienes cinco palabras. El tiempo corre desde que pulsas Empezar y no se para aunque cierres la web.</p>
      <button type="button" class="ev-boton grande" data-accion="empezar">Empezar</button>${aviso(s)}</section>`;
  }
  const inicio = Date.parse(partida.empezada_en);
  const reloj = partida.terminada_en
    ? `<strong class="ev-reloj">${formatoTiempo(partida.tiempo_ms)}</strong>`
    : `<strong class="ev-reloj" data-cronometro="${inicio}">${formatoTiempo(ahora - inicio)}</strong>`;
  const resultado = !partida.terminada_en ? ''
    : (partida.resuelta
      ? `<p class="ev-resultado bien">¡Resuelta en ${formatoTiempo(partida.tiempo_ms)}!</p>`
      : '<p class="ev-resultado">Esta vez no ha podido ser.</p>') + aLaSiguiente(s, orden, m, ahora);
  return `<section class="ev-juego">
    <div class="ev-barra">${volver}<span class="ev-cronometro">Frase ${orden} · ${reloj}</span></div>
    ${resultado}${panelDeLaFrase(partida.visible)}${tablero(partida, s.escrito)}${aviso(s)}
    ${partida.terminada_en ? '<p class="ev-nota">La frase entera se enseña al terminar el evento.</p>' : teclado(partida.intentos)}
  </section>`;
}

/**
 * La puerta de un evento con contraseña: solo el campo para escribirla. Ni título, ni reglas, ni ayuda: quien no la
 * sabe no tiene por qué saber de qué va el evento.
 */
export function vistaDeLaPuerta(s) {
  return `<section class="ev-puerta">
    <form data-formulario="clave">
      <label for="ev-clave">Contraseña</label>
      <input id="ev-clave" name="clave" type="password" autocomplete="off" required>
      <button type="submit" class="ev-boton">Entrar</button>
    </form>${aviso(s)}</section>`;
}

/** La pantalla del participante para un estado y una hora (ya corregida al servidor). */
export function vistaDelEvento(s, ahora) {
  if (!s.nombre && !s.recuperando && s.estado?.bloqueado) return vistaDeLaPuerta(s);

  const boton = `<button type="button" class="ev-ayuda-boton" data-accion="ayuda" aria-expanded="${Boolean(s.ayuda)}">${
    s.ayuda ? 'Cerrar' : '¿Cómo se juega?'}</button>`;
  const titulo = `<header class="ev-cabecera"><span class="ev-marca">${escapar(s.estado?.titulo ?? 'La frase del evento')}</span>${
    s.nombre ? `<span class="ev-quien">${escapar(s.nombre)}</span>` : ''}${boton}</header>${s.ayuda ? comoSeJuega() : ''}`;

  if (!s.nombre && s.recuperando) {
    return `${titulo}<section class="ev-espera"><h1>Recuperando tu partida…</h1>
      <p>No hemos podido conectar. Lo reintentamos solos; no cierres esta página.</p></section>`;
  }
  if (!s.nombre) {
    return `${titulo}<section class="ev-entrada">
      <h1>Destapa la frase</h1>
      <p>Cinco palabras de cinco letras para destapar cada frase. Gana quien resuelve más frases en menos tiempo.</p>
      <form data-formulario="entrar">
        <label for="ev-nombre">Tu nombre</label>
        <input id="ev-nombre" name="nombre" maxlength="30" autocomplete="name" required>
        <button type="submit" class="ev-boton">Entrar</button>
      </form>${aviso(s)}</section>`;
  }

  const m = momentoDelEvento(s.estado, ahora);
  if (m.tipo === 'terminado') {
    return `${titulo}${vistaRanking(s.ranking, s.nombre)}${soluciones(s.estado)}`;
  }
  if (m.tipo === 'sin-empezar') {
    return `${titulo}<section class="ev-espera"><h1>¡Ya estás dentro!</h1>
      <p>La primera frase sale en cuanto el presentador empiece el evento. No cierres esta página.</p>${aviso(s)}</section>
      ${s.ayuda ? '' : comoSeJuega()}`;
  }
  if (s.seleccionada !== null && m.liberadas.some((f) => f.orden === s.seleccionada)) {
    return `${titulo}${frase(s, s.seleccionada, m, ahora)}`;
  }
  return `${titulo}${lista(s, m, ahora)}`;
}

// ── Borde ─────────────────────────────────────────────────────────────────────────────────────────────────

/** Cada cuánto se pregunta el estado al servidor. Con 120 móviles, 10 s son 12 peticiones por segundo. */
const SONDEO_MS = 10_000;

/** Monta el juego en un contenedor. `temporizador` es `{cada(ms, fn)}`; el borde le pasa `setInterval`. */
export async function montarEvento(contenedor, control, temporizador) {
  const pintar = () => {
    contenedor.innerHTML = vistaDelEvento(control.estado, control.ahora());
    // La pestaña tampoco dice de qué va el evento hasta que se abre.
    document.title = control.estado.estado?.titulo || 'Acceso';
  };
  const arriba = () => window.scrollTo?.(0, 0);
  // Enviar pinta dos veces: al salir («Enviando…», el teclado quieto) y al volver la respuesta.
  const enviar = async () => {
    const enCurso = control.enviar();
    pintar();
    await enCurso;
    pintar();
  };

  // Solo repinta si el clic era del juego: repintar en cualquier clic quitaba el formulario de entrada antes de
  // que llegara su `submit`, y el navegador lo cancelaba.
  contenedor.addEventListener('click', async (evento) => {
    const tecla = evento.target.closest('[data-tecla]');
    const elegida = evento.target.closest('[data-elegir]');
    const accion = evento.target.closest('[data-accion]')?.dataset.accion;
    if (tecla) control.teclear(tecla.dataset.tecla);
    else if (elegida) {
      control.elegir(Number(elegida.dataset.elegir));
      arriba();
    } else if (accion === 'volver') control.elegir(null);
    else if (accion === 'ayuda') {
      control.ayuda();
      arriba();
    }
    else if (accion === 'empezar') await control.empezar();
    else if (accion === 'enviar') return enviar();
    else if (accion === 'borrar') control.borrar();
    else return;
    pintar();
  });

  contenedor.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const datos = new FormData(evento.target);
    if (evento.target.dataset.formulario === 'clave') await control.desbloquear(datos.get('clave'));
    else await control.entrar(datos.get('nombre'));
    pintar();
  });

  document.addEventListener('keydown', async (evento) => {
    if (evento.metaKey || evento.ctrlKey || evento.altKey || evento.target.closest?.('input')) return;
    if (evento.key === 'Enter') {
      evento.preventDefault();
      await enviar();
      return;
    }
    if (evento.key === 'Backspace') control.borrar();
    else {
      const letra = letraDeTecla(evento.key);
      if (!letra) return;
      control.teclear(letra);
    }
    evento.preventDefault();
    pintar();
  });

  // El cronómetro y las cuentas atrás avanzan solos; al llegar una a cero se pregunta al servidor qué toca.
  temporizador.cada(1000, async () => {
    for (const reloj of contenedor.querySelectorAll('[data-cronometro]')) {
      reloj.textContent = formatoTiempo(control.ahora() - Number(reloj.dataset.cronometro));
    }
    let llego = false;
    for (const reloj of contenedor.querySelectorAll('[data-cuenta-atras]')) {
      const falta = Number(reloj.dataset.cuentaAtras) - control.ahora();
      reloj.textContent = cuentaAtras(falta);
      if (falta <= 0) llego = true;
    }
    if (llego) {
      await control.refrescar();
      pintar();
    }
  });
  temporizador.cada(SONDEO_MS, async () => {
    if (!control.estado.nombre) {
      // Escribiendo el nombre no se repinta el formulario; si se recargó sin red, se reintenta recuperar la partida.
      if (control.estado.recuperando) {
        await control.arrancar();
        pintar();
      }
      return;
    }
    const fase = () => control.momento().tipo + (control.estado.estado?.frases ?? []).map((f) => f.estado).join();
    const antes = fase();
    await control.refrescar();
    if (antes !== fase() || control.estado.sinConexion) pintar();
  });

  await control.arrancar();
  pintar();
}
