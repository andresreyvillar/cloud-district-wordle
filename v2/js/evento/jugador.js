/**
 * El juego del evento en el móvil de cada participante: `/evento`.
 *
 * Slice: `palabras-del-evento`. El Wordle de siempre, varias palabras seguidas: seis intentos para cada palabra de
 * cinco letras, cada una con su cronómetro, que empieza al pulsar «Empezar» o «Siguiente palabra». Tres piezas:
 * - `controlDelEvento` guarda el estado y habla con la API. Sin DOM: se prueba con una API falsa.
 * - `vistaDelEvento` pinta ese estado. Pura: el reloj entra por parámetro.
 * - `montarEvento` es el borde: eventos del DOM, el cronómetro que avanza y el sondeo del estado.
 *
 * La solución no está nunca aquí hasta que termina el evento: el servidor manda solo los colores. Ni los puntos ni el
 * grupo: los ve el admin al terminar (decisión del dueño).
 */

import { escapar } from '../ui/shell.js';
import {
  INTENTOS, LETRAS, buscarNombres, coloresDelTeclado, desfase, formatoTiempo, letraDeTecla, normaliza, puntoDelJuego,
  tokenAleatorio,
} from './dominio.js';

const CLAVE_DEL_TOKEN = 'evento:token';

const MENSAJE_SIN_RED = 'No se ha podido conectar. Revisa la conexión y prueba otra vez.';

/** El servidor no reconoce el token: el nombre se liberó, o es de otro evento. */
const sinNombre = (error) => error?.tipo === 'rechazo' && /no has elegido nombre|evento desconocido/.test(error.message);

/**
 * El estado del participante y lo que puede hacer. `almacen` es `{leer, guardar}`; `reloj`, los ms locales.
 *
 * Si una palabra vale lo decide el servidor: vale una del diccionario o la solución de esa misma palabra, que la
 * empresa puede haber elegido fuera de él y que el móvil no puede conocer.
 */
export function controlDelEvento({ api, almacen, reloj, generarToken = tokenAleatorio }) {
  const clave = `${CLAVE_DEL_TOKEN}:${api.evento}`;
  const s = {
    token: almacen.leer(clave),
    nombre: null,
    // Hay token pero no se ha podido leer su juego (sin red al recargar): se reintenta, sin pedir el nombre.
    recuperando: false,
    estado: null,
    desfase: 0,
    // La lista de nombres para elegir el propio, lo escrito en el buscador y si la lista está desplegada.
    nombres: null,
    buscado: '',
    desplegado: false,
    rondas: new Map(),
    // Las soluciones del participante en su orden: solo llegan con el evento terminado.
    palabras: null,
    escrito: [],
    aviso: null,
    enviando: false,
    empezando: false,
    entrando: false,
    sinConexion: false,
    ayuda: false,
  };

  const ahora = () => reloj() + s.desfase;
  const total = () => Number(s.estado?.total) || 0;
  const punto = () => puntoDelJuego(s.rondas, total());

  async function cargarNombres() {
    try {
      s.nombres = await api.nombres();
    } catch (error) {
      if (error.tipo === 'red') s.sinConexion = true;
    }
  }

  async function refrescar() {
    const pedido = reloj();
    try {
      const estado = await api.estado();
      // La hora del servidor es la de mitad del viaje: sin descontar la latencia, el móvil iba adelantado lo que
      // tarda la petición.
      s.desfase = desfase(estado.ahora, (pedido + reloj()) / 2);
      s.estado = estado;
      s.sinConexion = false;
    } catch (error) {
      if (error.tipo === 'red') s.sinConexion = true;
      else s.aviso = error.message;
      return;
    }
    // Las palabras de cada uno, en su orden, solo las da el servidor con el evento terminado: si termina con la
    // página abierta, se piden.
    if (s.estado.terminado && s.token && !s.palabras) await sincronizar();
    if (s.estado.activo && !s.nombre && !s.recuperando && !s.nombres) await cargarNombres();
  }

  /** Rehace lo del participante desde el servidor: su nombre y sus rondas. */
  async function sincronizar() {
    if (!s.token) return;
    try {
      const mio = await api.miJuego(s.token);
      s.nombre = mio.nombre;
      s.rondas = new Map((mio.rondas ?? []).map((ronda) => [ronda.orden, ronda]));
      s.palabras = Array.isArray(mio.palabras) ? mio.palabras : null;
      s.recuperando = false;
    } catch (error) {
      // Solo un token que el evento no conoce (otro evento, un nombre liberado por el admin) se tira: se vuelve a
      // elegir. Ante cualquier otro fallo (sin red, un tiempo agotado en la base de datos) se conserva y se reintenta,
      // o el participante se quedaría fuera con su propio nombre ocupado.
      if (sinNombre(error)) {
        s.token = null;
        s.nombre = null;
        s.rondas = new Map();
        s.recuperando = false;
      } else {
        s.recuperando = true;
        s.sinConexion = true;
      }
    }
  }

  async function arrancar() {
    await sincronizar();
    await refrescar();
  }

  /** Lo escrito en el buscador de nombres: filtra la lista y la despliega. */
  function buscar(texto) {
    s.buscado = String(texto ?? '');
    s.desplegado = true;
    s.aviso = null;
  }

  /** Abre o cierra la lista entera. */
  function desplegar() {
    s.desplegado = !s.desplegado;
  }

  /** Elige un nombre de la lista desplegada: queda escrito y la lista se cierra. */
  function marcar(nombre) {
    s.buscado = String(nombre ?? '');
    s.desplegado = false;
    s.aviso = null;
  }

  /** Entra con un nombre de la lista. Uno que no está en ella no se envía. */
  async function entrar(nombre = s.buscado) {
    const escrito = String(nombre ?? '').trim();
    if (!escrito) {
      s.aviso = 'Busca tu nombre en la lista.';
      return;
    }
    const enLaLista = s.nombres?.find((n) => normaliza(n.nombre) === normaliza(escrito));
    if (s.nombres && !enLaLista) {
      s.aviso = 'Ese nombre no está en la lista: elígelo de la lista.';
      s.desplegado = true;
      return;
    }
    if (s.entrando) return;
    s.entrando = true;
    // El token se fija y se guarda antes de llamar: un doble toque manda el mismo, y si la respuesta se pierde y se
    // recarga, el móvil recupera el nombre que el servidor sí le dio.
    s.token ??= generarToken();
    almacen.guardar(clave, s.token);
    try {
      const respuesta = await api.elegir(enLaLista?.nombre ?? escrito, s.token);
      s.nombre = respuesta.nombre;
      s.aviso = null;
      s.desplegado = false;
    } catch (error) {
      s.aviso = error.tipo === 'rechazo' ? error.message : MENSAJE_SIN_RED;
      if (error.tipo === 'rechazo') await cargarNombres();
    } finally {
      s.entrando = false;
    }
  }

  /** Empieza la palabra que toca: la primera, o la siguiente a la terminada. Su cronómetro arranca ahora. */
  async function empezar() {
    const p = punto();
    if (!s.estado?.activo || s.empezando || (p.tipo !== 'empezar' && p.tipo !== 'entre')) return;
    const orden = p.tipo === 'empezar' ? 1 : p.orden + 1;
    s.empezando = true;
    try {
      s.rondas.set(orden, await api.empezar(s.token, orden));
      s.escrito = [];
      s.aviso = null;
    } catch (error) {
      s.aviso = error.tipo === 'rechazo' ? error.message : MENSAJE_SIN_RED;
      // Un rechazo puede ser que el admin liberó el nombre: se rehace lo del participante, y sin nombre vuelve a elegir.
      if (error.tipo === 'rechazo') {
        await sincronizar();
        await refrescar();
      }
    } finally {
      s.empezando = false;
    }
  }

  function enJuego() {
    const p = punto();
    return s.estado?.activo && p.tipo === 'jugando' ? s.rondas.get(p.orden) : null;
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

  /** Envía lo escrito. Si falta alguna letra no se envía; si la palabra no vale, el servidor lo dice y no gasta intento. */
  async function enviar() {
    const ronda = enJuego();
    if (!ronda || s.enviando) return;
    const faltan = LETRAS - s.escrito.length;
    if (faltan > 0) {
      s.aviso = faltan === 1 ? 'Falta 1 letra.' : `Faltan ${faltan} letras.`;
      return;
    }
    const palabra = s.escrito.join('');
    s.enviando = true;
    try {
      // El número del intento hace seguro reenviar: si el primero llegó y se perdió la respuesta, el servidor lo
      // reconoce y no gasta otro.
      const numero = (ronda.intentos?.length ?? 0) + 1;
      s.rondas.set(ronda.orden, await api.probar(s.token, ronda.orden, palabra, numero));
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
    estado: s, ahora, punto, arrancar, sincronizar, refrescar, buscar, desplegar, marcar, entrar, empezar, teclear,
    borrar, enviar, ayuda,
  };
}

// ── Vista ─────────────────────────────────────────────────────────────────────────────────────────────────

const CLASE = { G: 'verde', Y: 'amarilla', '.': 'gris' };

/** El tablero de seis intentos: los enviados con sus colores, el que se escribe y los que quedan. */
export function tablero(ronda, escrito = []) {
  const filas = [];
  const celdas = (letras, colores) => Array.from({ length: LETRAS }, (_, i) => {
    const letra = letras[i] ?? '';
    const color = colores ? ` ${CLASE[colores[i]] ?? ''}` : '';
    return `<span class="ev-celda${letra ? ' llena' : ''}${color}">${escapar(letra.toUpperCase())}</span>`;
  }).join('');
  for (const { palabra, colores } of ronda.intentos ?? []) {
    filas.push(`<div class="ev-fila">${celdas([...palabra], colores)}</div>`);
  }
  if (!ronda.terminada_en && filas.length < INTENTOS) filas.push(`<div class="ev-fila ev-actual">${celdas(escrito, null)}</div>`);
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

/** Cuánto suma cada intento, si el servidor lo ha dicho. Sin cifra no se inventa una. */
function porIntento(segundos) {
  const n = Number(segundos);
  return Number.isInteger(n) && n > 0 ? n : null;
}

/** Cómo se juega: que el tiempo cuenta, las reglas del Wordle y los tres colores, con un ejemplo inventado. */
export function comoSeJuega(segundos) {
  const n = porIntento(segundos);
  const fila = (palabra, colores) => `<div class="ev-fila">${[...palabra].map((letra, i) => (
    `<span class="ev-celda ${CLASE[colores[i]]}">${letra}</span>`)).join('')}</div>`;
  return `<section class="ev-ayuda" aria-label="Cómo se juega">
    <h2>Cómo se juega</h2>
    <ol>
      <li><strong>El tiempo cuenta</strong>: cuanto antes resuelvas cada palabra, más puntos. El cronómetro corre desde
        que pulsas y no se para aunque cierres la web${n ? `, y cada intento suma además ${n} segundos` : ''}.</li>
      <li>Adivina la <strong>palabra de 5 letras</strong> en <strong>6 intentos</strong>. Cada intento tiene que ser una
        palabra que exista.</li>
      <li>Tras cada intento, las letras cambian de color:
        <ul class="ev-leyenda">
          <li><span class="ev-celda verde">A</span><span>La letra está en la palabra y en la posición correcta.</span></li>
          <li><span class="ev-celda amarilla">A</span><span>La letra está en la palabra, pero en otra posición.</span></li>
          <li><span class="ev-celda gris">A</span><span>La letra no aparece en la palabra.</span></li>
        </ul>
      </li>
      <li>Al resolverla (o al gastar los 6 intentos) pasas a la siguiente con <strong>Siguiente palabra</strong>.</li>
    </ol>
    <p class="ev-nota">Ejemplo con la palabra NUBES: en PLUMA la U está pero en otro sitio; en NUBIA, la N, la U y la B
      están en su sitio.</p>
    <div class="ev-tablero">${fila('PLUMA', '..Y..')}${fila('NUBIA', 'GGG..')}</div>
    <p class="ev-nota">Las tildes no cuentan; la Ñ es una letra más.</p>
  </section>`;
}

function aviso(s) {
  if (s.enviando) return '<p class="ev-aviso enviando" role="status">Enviando…</p>';
  const texto = s.aviso ?? (s.sinConexion ? 'Sin conexión: reintentando…' : null);
  return texto ? `<p class="ev-aviso" role="alert">${escapar(texto)}</p>` : '';
}

const intentos = (n) => `${n} ${n === 1 ? 'intento' : 'intentos'}`;

/** Cómo le fue en cada palabra: resuelta (intentos y tiempo), sin resolver, sin terminar o sin jugar. */
function resumen(s) {
  const filas = Array.from({ length: Number(s.estado?.total) || 0 }, (_, i) => {
    const ronda = s.rondas.get(i + 1);
    const texto = !ronda ? 'Sin jugar' : !ronda.terminada_en ? 'Sin terminar'
      : ronda.resuelta ? `${intentos(ronda.intentos.length)} · ${formatoTiempo(ronda.tiempo_ms)}` : 'Sin resolver';
    const clase = ronda?.resuelta ? ' resuelta' : ronda?.terminada_en ? ' fallada' : '';
    const palabra = s.palabras?.[i];
    const cual = palabra ? ` · ${escapar(String(palabra).toUpperCase())}` : '';
    return `<li class="ev-resumen-fila${clase}"><span class="ev-etiqueta">Palabra ${i + 1}${cual}</span><span>${texto}</span></li>`;
  }).join('');
  return `<ol class="ev-resumen">${filas}</ol>`;
}

function soluciones(estado) {
  const lista = estado?.soluciones ?? [];
  if (!lista.length) return '';
  return `<section class="ev-soluciones"><h2>Las palabras</h2><ol>${lista.map((p) => (
    `<li value="${Number(p.orden)}">${escapar(String(p.palabra).toUpperCase())}</li>`)).join('')}</ol></section>`;
}

/** Lo que se ve antes de activar el evento: solo el aviso. Ni título, ni reglas, ni nombres. */
export function vistaDeLaEspera() {
  return `<section class="ev-espera">
    <p class="ev-etiqueta">En breve</p>
    <h1>El evento se activará en breve</h1>
    <p>Deja esta página abierta: empezará sola.</p>
  </section>`;
}

/** La lista de nombres que encajan con lo buscado. Se repinta sola al escribir, sin tocar el campo. */
export function listaDeNombres(s) {
  if (!s.desplegado) return '';
  const encontrados = buscarNombres(s.nombres, s.buscado);
  if (!encontrados.length) return '<p class="ev-nota ev-sin-nombres">Ningún nombre de la lista encaja.</p>';
  return `<ul class="ev-nombres" id="ev-nombres" role="listbox">${encontrados.map((n) => (
    n.libre
      ? `<li><button type="button" role="option" data-nombre="${escapar(n.nombre)}">${escapar(n.nombre)}</button></li>`
      : `<li><button type="button" role="option" disabled>${escapar(n.nombre)} <em>ya elegido</em></button></li>`
  )).join('')}</ul>`;
}

function eleccionDelNombre(s) {
  return `<section class="ev-entrada">
    <h1>¿Quién eres?</h1>
    <p>Escribe tu nombre o búscalo en la lista.</p>
    <form data-formulario="entrar" autocomplete="off">
      <label for="ev-nombre" class="ev-etiqueta">Tu nombre</label>
      <div class="ev-combo">
        <input id="ev-nombre" name="nombre" value="${escapar(s.buscado)}" autocomplete="off" role="combobox"
          aria-controls="ev-nombres" aria-expanded="${Boolean(s.desplegado)}" placeholder="Nombre y apellido">
        <button type="button" class="ev-desplegar" data-accion="desplegar" aria-label="Ver la lista de nombres">▾</button>
      </div>
      <div data-lista-de-nombres>${listaDeNombres(s)}</div>
      <button type="submit" class="ev-boton grande">Entrar</button>
    </form>${aviso(s)}</section>`;
}

/** La barra de cada palabra: cuál es de cuántas y su cronómetro (parado si terminó). */
function barra(s, ronda, ahora) {
  const inicio = Date.parse(ronda.empezada_en);
  const reloj = ronda.terminada_en
    ? `<strong class="ev-reloj">${formatoTiempo(ronda.tiempo_ms)}</strong>`
    : `<strong class="ev-reloj" data-cronometro="${inicio}">${formatoTiempo(ahora - inicio)}</strong>`;
  const cuenta = ronda.terminada_en ? '' : '<span class="ev-cuenta">⏱ El tiempo cuenta</span>';
  return `<div class="ev-barra"><span class="ev-etiqueta">Palabra ${Number(ronda.orden)}/${Number(s.estado.total)}</span>${reloj}${cuenta}</div>`;
}

function juego(s, ahora) {
  const p = puntoDelJuego(s.rondas, Number(s.estado.total));
  const n = Number(s.estado.total);
  const segundos = porIntento(s.estado.segundos_por_intento);
  if (p.tipo === 'empezar') {
    return `<section class="ev-empezar">
      <p class="ev-etiqueta">Palabra 1/${n}</p>
      <h1>${n} palabras, 6 intentos cada una</h1>
      <p class="ev-tiempo"><strong>El tiempo cuenta.</strong> El cronómetro arranca al pulsar y no se para hasta que
        la resuelves o gastas los intentos.${segundos ? ` Cada intento suma además ${segundos} segundos.` : ''}
        Cuanto antes, más puntos.</p>
      <button type="button" class="ev-boton grande" data-accion="empezar">Empezar</button>${aviso(s)}
    </section>${s.ayuda ? '' : comoSeJuega(segundos)}`;
  }
  const ronda = s.rondas.get(p.orden);
  if (p.tipo === 'jugando') {
    return `<section class="ev-juego">${barra(s, ronda, ahora)}${tablero(ronda, s.escrito)}${aviso(s)}
      ${teclado(ronda.intentos)}</section>`;
  }
  const resultado = ronda.resuelta
    ? `<p class="ev-resultado bien">¡Resuelta en ${intentos(ronda.intentos.length)} y ${formatoTiempo(ronda.tiempo_ms)}!</p>`
    : '<p class="ev-resultado">No la has adivinado.</p><p class="ev-nota">La palabra se desvela al terminar el evento.</p>';
  const siguiente = p.tipo === 'entre'
    ? `<button type="button" class="ev-boton grande" data-accion="empezar">Siguiente palabra ${p.orden + 1}/${n}</button>`
    : `<h2>¡Has terminado las ${n} palabras!</h2>${resumen(s)}
       <p class="ev-nota">Los puntos se conocen al terminar el evento.</p>`;
  return `<section class="ev-juego">${barra(s, ronda, ahora)}${resultado}${tablero(ronda)}${siguiente}${aviso(s)}</section>`;
}

/** La pantalla del participante para un estado y una hora (ya corregida al servidor). */
export function vistaDelEvento(s, ahora) {
  if (!s.estado) {
    return s.sinConexion
      ? '<section class="ev-espera"><h1>Sin conexión</h1><p>Lo reintentamos solos; no cierres esta página.</p></section>'
      : '<section class="ev-espera"><p>Cargando…</p></section>';
  }
  if (!s.estado.activo && !s.estado.terminado) return vistaDeLaEspera();

  const boton = `<button type="button" class="ev-ayuda-boton" data-accion="ayuda" aria-expanded="${Boolean(s.ayuda)}">${
    s.ayuda ? 'Cerrar' : '¿Cómo se juega?'}</button>`;
  const cabecera = `<header class="ev-cabecera"><span class="ev-marca">${escapar(s.estado.titulo ?? '')}</span>${
    s.nombre ? `<span class="ev-quien">${escapar(s.nombre)}</span>` : ''}${boton}</header>${
    s.ayuda ? comoSeJuega(s.estado.segundos_por_intento) : ''}`;

  if (s.estado.terminado) {
    const mio = s.nombre ? `<h2>Tus palabras</h2>${resumen(s)}` : '';
    return `${cabecera}<section class="ev-final"><p class="ev-etiqueta">Fin</p><h1>El evento ha terminado</h1>
      <p>Gracias por jugar. Los puntos se anuncian en el evento.</p>${mio}${s.nombre ? '' : soluciones(s.estado)}</section>`;
  }
  if (!s.nombre && s.recuperando) {
    return `${cabecera}<section class="ev-espera"><h1>Recuperando tu partida…</h1>
      <p>No hemos podido conectar. Lo reintentamos solos; no cierres esta página.</p></section>`;
  }
  if (!s.nombre) return `${cabecera}${eleccionDelNombre(s)}`;
  return `${cabecera}${juego(s, ahora)}`;
}

// ── Borde ─────────────────────────────────────────────────────────────────────────────────────────────────

/** Cada cuánto se pregunta el estado al servidor. Con 120 móviles, 5 s son 24 peticiones por segundo. */
const SONDEO_MS = 5_000;

/** Monta el juego en un contenedor. `temporizador` es `{cada(ms, fn)}`; el borde le pasa `setInterval`. */
export async function montarEvento(contenedor, control, temporizador) {
  const pintar = () => {
    contenedor.innerHTML = vistaDelEvento(control.estado, control.ahora());
    // La pestaña no dice de qué va el evento hasta que se activa.
    document.title = control.estado.estado?.titulo || 'En breve';
  };
  const arriba = () => window.scrollTo?.(0, 0);
  // Enviar pinta dos veces: al salir («Enviando…», el teclado quieto) y al volver la respuesta.
  const enviar = async () => {
    const enCurso = control.enviar();
    pintar();
    await enCurso;
    pintar();
  };

  // Solo repinta si el clic era del juego: repintar en cualquier clic quitaba el formulario antes de que llegara su
  // `submit`, y el navegador lo cancelaba.
  contenedor.addEventListener('click', async (evento) => {
    const tecla = evento.target.closest('[data-tecla]');
    const nombre = evento.target.closest('[data-nombre]');
    const accion = evento.target.closest('[data-accion]')?.dataset.accion;
    if (tecla) control.teclear(tecla.dataset.tecla);
    else if (nombre) control.marcar(nombre.dataset.nombre);
    else if (accion === 'desplegar') control.desplegar();
    else if (accion === 'ayuda') {
      control.ayuda();
      arriba();
    } else if (accion === 'empezar') {
      await control.empezar();
      arriba();
    } else if (accion === 'enviar') return enviar();
    else if (accion === 'borrar') control.borrar();
    else return;
    pintar();
  });

  // Al escribir en el buscador solo se repinta la lista: repintar el campo le quitaría el foco.
  contenedor.addEventListener('input', (evento) => {
    if (evento.target.name !== 'nombre') return;
    control.buscar(evento.target.value);
    const hueco = contenedor.querySelector('[data-lista-de-nombres]');
    if (hueco) hueco.innerHTML = listaDeNombres(control.estado);
    evento.target.setAttribute('aria-expanded', String(control.estado.desplegado));
  });

  contenedor.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    await control.entrar(new FormData(evento.target).get('nombre'));
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

  // El cronómetro avanza solo.
  temporizador.cada(1000, () => {
    for (const reloj of contenedor.querySelectorAll('[data-cronometro]')) {
      reloj.textContent = formatoTiempo(control.ahora() - Number(reloj.dataset.cronometro));
    }
  });
  // El sondeo detecta la activación y el final. Solo repinta si cambia algo de eso, para no pisar lo que se escribe.
  temporizador.cada(SONDEO_MS, async () => {
    if (control.estado.recuperando) {
      await control.arrancar();
      pintar();
      return;
    }
    const fase = () => `${control.estado.estado?.activo}|${control.estado.estado?.terminado}|${control.estado.sinConexion}`;
    const antes = fase();
    await control.refrescar();
    if (antes !== fase()) pintar();
  });

  await control.arrancar();
  pintar();
}
