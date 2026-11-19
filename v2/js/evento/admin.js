/**
 * El dashboard del evento: `/evento/admin`.
 *
 * Slice: `admin-del-evento`. **Sin contraseña** (decisión del dueño). El evento empieza y termina a su hora; aquí se
 * ve cuánto falta, las palabras (que se cambian hasta la hora de empezar), y en directo los participantes, el ranking
 * individual, el campeonato F1 de grupos y la media de cada lista. Terminado, se ven las soluciones, se exportan los
 * puntos (JSON y CSV) y se comparten en texto por WhatsApp o email. Con el estilo del cartel del evento.
 */

import { escapar } from '../ui/shell.js';
import { formatoTiempo } from './dominio.js';

export function controlDelAdmin({ api }) {
  const s = { panel: null, aviso: null, sinConexion: false, ocupado: false };

  async function refrescar() {
    try {
      s.panel = await api.tablero();
      s.sinConexion = false;
    } catch (error) {
      if (error.tipo === 'red') s.sinConexion = true;
      else s.aviso = error.message;
    }
  }

  /** Una acción del admin: si el servidor dice que no, se dice por qué; después se rehace el tablero. */
  async function accion(fn, exito = null) {
    if (s.ocupado) return;
    s.ocupado = true;
    try {
      await fn();
      s.aviso = exito;
    } catch (error) {
      s.aviso = error.tipo === 'rechazo' ? error.message : 'No se ha podido conectar. Prueba otra vez.';
    } finally {
      s.ocupado = false;
    }
    await refrescar();
  }

  return {
    estado: s,
    refrescar,
    echar: (nombre) => accion(() => api.echar(nombre)),
    cambiarPalabra: (orden, palabra) => accion(() => api.cambiarPalabra(orden, palabra), `Palabra ${Number(orden)} guardada.`),
  };
}

// ── Exportación ──────────────────────────────────────────────────────────────────────────────────────────

/**
 * Los puntos tal como salen del evento, para enviarlos a quien lleva la cuenta de los grupos. El formato de su API
 * está por llegar: esto es lo que hay, completo, y de aquí se adapta.
 */
export function exportacion(panel, evento) {
  return {
    evento,
    terminado_en: panel.terminado_en,
    segundos_por_intento: panel.segundos_por_intento,
    grupos: (panel.grupos ?? []).map((g) => ({
      puesto: g.puesto, grupo: g.grupo, puntos: Number(g.puntos), puntos_totales: Number(g.puntos_totales),
      miembros: g.miembros, jugaron: g.jugaron,
      puntos_f1: Number((panel.grupos_f1 ?? []).find((f) => f.grupo === g.grupo)?.puntos ?? 0),
    })),
    grupos_f1: (panel.grupos_f1 ?? []).map((g) => ({
      puesto: g.puesto, grupo: g.grupo, puntos: Number(g.puntos),
      personas: (g.personas ?? []).map((p) => ({ nombre: p.nombre, puesto: p.puesto, puntos: Number(p.puntos) })),
    })),
    participantes: (panel.jugadores ?? []).map((j) => ({
      puesto: j.puesto, nombre: j.nombre, grupo: j.grupo, puntos: Number(j.puntos), f1: Number(j.f1 ?? 0),
      palabras: j.palabras,
    })),
  };
}

/** Un campo de CSV: entre comillas si lleva separador, comillas o salto; y nunca empezando por `=+-@`, tabulador ni
 * retorno (fórmulas). */
function campoCsv(valor) {
  let texto = String(valor ?? '');
  if (/^[=+\-@\t\r]/.test(texto)) texto = `'${texto}`;
  return /[",;\n\r]/.test(texto) ? `"${texto.replace(/"/g, '""')}"` : texto;
}

const filaCsv = (campos) => campos.map(campoCsv).join(',');

/** Los grupos en CSV: puesto, grupo, puntos (la media), puntos totales, miembros, cuántos jugaron y puntos F1. */
export function csvDeGrupos(datos) {
  return [filaCsv(['puesto', 'grupo', 'puntos', 'puntos_totales', 'miembros', 'jugaron', 'puntos_f1']),
    ...datos.grupos.map((g) => filaCsv([g.puesto, g.grupo, g.puntos, g.puntos_totales, g.miembros, g.jugaron,
      g.puntos_f1 ?? 0]))]
    .join('\n') + '\n';
}

/** Los participantes en CSV: puesto, nombre, grupo, puntos y, por palabra, intentos, segundos y puntos. */
export function csvDeParticipantes(datos) {
  const n = Math.max(0, ...datos.participantes.flatMap((p) => (p.palabras ?? []).map((w) => w.orden)));
  const columnas = Array.from({ length: n }, (_, i) => [`p${i + 1}_intentos`, `p${i + 1}_segundos`, `p${i + 1}_puntos`]).flat();
  const filas = datos.participantes.map((p) => {
    const porPalabra = Array.from({ length: n }, (_, i) => {
      const w = (p.palabras ?? []).find((x) => x.orden === i + 1);
      if (!w) return ['', '', 0];
      return [w.resuelta ? w.intentos : 'X', w.tiempo_ms === null ? '' : (w.tiempo_ms / 1000).toFixed(1), w.puntos];
    }).flat();
    return filaCsv([p.puesto, p.nombre, p.grupo, p.puntos, p.f1 ?? 0, ...porPalabra]);
  });
  return [filaCsv(['puesto', 'nombre', 'grupo', 'puntos', 'f1', ...columnas]), ...filas].join('\n') + '\n';
}

// ── Compartir ──────────────────────────────────────────────────────────────────────────────────────────

const MEDALLAS = { 1: '🥇', 2: '🥈', 3: '🥉' };

/** Un número de puntos en español: «0,5», «12,25». */
const cifra = (n) => (Number(n) || 0).toLocaleString('es-ES', { maximumFractionDigits: 2 });

/** Los puntos en español, con su palabra: «1 punto», «12,25 puntos». */
function formatoPuntos(n) {
  return `${cifra(n)} ${Number(n) === 1 ? 'punto' : 'puntos'}`;
}

const conMedalla = (puesto) => MEDALLAS[Number(puesto)] ?? `${Number(puesto)}.`;

/** Los resultados en texto, para pegar en WhatsApp o en un email: el campeonato F1 de grupos con quién sumó, todos
 * los grupos por su media y el podio. */
export function textoParaCompartir(panel) {
  const f1 = (panel?.grupos_f1 ?? []).map((g) => {
    const quien = (g.personas ?? []).map((p) => `${p.nombre} ${cifra(p.puntos)}`).join(', ');
    return `${conMedalla(g.puesto)} ${g.grupo} · ${formatoPuntos(g.puntos)}${quien ? ` (${quien})` : ''}`;
  });
  const grupos = (panel?.grupos ?? []).map((g) => `${conMedalla(g.puesto)} ${g.grupo} · ${formatoPuntos(g.puntos)}`);
  const podio = (panel?.jugadores ?? []).filter((j) => Number(j.puesto) <= 3 && Number(j.puntos) > 0)
    .map((j) => `${conMedalla(j.puesto)} ${j.nombre} (${j.grupo}) · ${formatoPuntos(j.puntos)}`);
  return [`🏆 ${panel?.titulo ?? ''} — resultados`,
    ...(f1.length ? ['', 'GRUPOS · F1', ...f1] : []),
    '', 'GRUPOS · MEDIA DE LA LISTA', ...grupos,
    ...(podio.length ? ['', 'PODIO', ...podio] : [])].join('\n');
}

function compartir(p) {
  const texto = textoParaCompartir(p);
  const asunto = `${p.titulo ?? ''} — resultados`;
  const whatsapp = `https://wa.me/?text=${encodeURIComponent(texto)}`;
  const email = `mailto:?subject=${encodeURIComponent(asunto)}&body=${encodeURIComponent(texto)}`;
  return `<section class="pa-compartir"><h2>Compartir los resultados</h2>
    <textarea readonly rows="${texto.split('\n').length}" aria-label="Resultados en texto">${escapar(texto)}</textarea>
    <div class="pa-exportar">
      <button type="button" class="ev-boton" data-compartir="copiar">Copiar</button>
      <a class="ev-boton" href="${escapar(whatsapp)}" target="_blank" rel="noopener">WhatsApp</a>
      <a class="ev-boton" href="${escapar(email)}">Email</a>
    </div></section>`;
}

// ── Vista ─────────────────────────────────────────────────────────────────────────────────────────────────

/** Los avisos flotan, como en el juego: no mueven el dashboard. */
function aviso(s) {
  if (s.aviso) return `<p class="ev-aviso ev-flotante se-desvanece" role="alert">${escapar(s.aviso)}</p>`;
  return s.sinConexion ? '<p class="ev-aviso ev-flotante" role="alert">Sin conexión: reintentando…</p>' : '';
}

const MADRID = 'Europe/Madrid';
const hora = (iso) => new Intl.DateTimeFormat('es-ES', { timeZone: MADRID, hour: '2-digit', minute: '2-digit' })
  .format(new Date(iso));

/** Lo que falta, para la cuenta atrás: «2 h 13 min», «13 min», «45 s». */
export function cuantoFalta(ms) {
  const s = Math.max(0, Math.floor(ms / 1000));
  if (s < 60) return `${s} s`;
  const min = Math.floor(s / 60);
  return min < 60 ? `${min} min` : `${Math.floor(min / 60)} h ${min % 60} min`;
}

/** La fecha como en el cartel: «2026/ nov/ 20», en la hora de Madrid. */
function fechaDelCartel(iso) {
  if (!iso) return '';
  const partes = Object.fromEntries(new Intl.DateTimeFormat('es-ES', {
    timeZone: MADRID, year: 'numeric', month: 'short', day: 'numeric',
  }).formatToParts(new Date(iso)).map((x) => [x.type, x.value]));
  return `${partes.year}/<br>${String(partes.month).replace('.', '')}/<br>${partes.day}`;
}

/** En qué punto está el evento: cuánto falta para empezar, cuánto para terminar, o terminado. */
function estadoDelEvento(p) {
  const ahora = Date.parse(p.ahora);
  const franja = p.empieza_en && p.terminado_en ? ` · de ${hora(p.empieza_en)} a ${hora(p.terminado_en)}` : '';
  if (p.terminado) return 'Terminado';
  if (p.antes) return p.empieza_en ? `Empieza en ${cuantoFalta(Date.parse(p.empieza_en) - ahora)}${franja}` : 'Sin hora de empezar';
  return p.terminado_en ? `En juego · termina en ${cuantoFalta(Date.parse(p.terminado_en) - ahora)}${franja}` : 'En juego';
}

function cabecera(p) {
  const titulo = String(p.titulo ?? '').trim().toLowerCase().replace(/\.?$/, '.');
  return `<header class="pa-cabecera">
    <p class="pa-fecha">${fechaDelCartel(p.empieza_en)}</p>
    <h1 class="pa-titulo">${escapar(titulo)}</h1>
    <p class="pa-estado">${escapar(estadoDelEvento(p))}</p>
  </header>`;
}

/** Cuántos han entrado y, en juego o terminado, cómo va cada palabra (antes de empezar solo habría ceros). */
function contadores(p) {
  const palabras = (p.palabras ?? []).map((w) => `<tr><th>Palabra ${Number(w.orden)}</th>
    <td><strong>${Number(w.jugando) || 0}</strong> jugando</td>
    <td><strong>${Number(w.resueltas) || 0}</strong> resuelta</td>
    <td><strong>${Number(w.falladas) || 0}</strong> fallada</td></tr>`).join('');
  return `<section class="pa-cifras">
    <p class="pa-apuntados"><strong>${Number(p.elegidos) || 0}</strong> de ${Number(p.participantes) || 0}
      participantes han entrado</p>
    ${p.antes ? '' : `<table class="pa-contadores"><tbody>${palabras}</tbody></table>`}</section>`;
}

/** Las palabras, una por fila, para revisarlas y cambiarlas. Solo en su propio enlace (`/evento/palabras`). */
function editorDePalabras(p) {
  const limite = p.empieza_en ? ` hasta las ${hora(p.empieza_en)}` : '';
  const filas = (p.palabras ?? []).map((w) => `<form class="pa-palabra" data-formulario="palabra" data-orden="${
    Number(w.orden)}"><span class="pa-num">${Number(w.orden)}</span>
      <input name="palabra" value="${escapar(String(w.palabra ?? '').toUpperCase())}" maxlength="5" autocomplete="off"
        autocapitalize="characters" spellcheck="false" aria-label="Palabra ${Number(w.orden)}">
      <button type="submit" class="ev-boton pequeno">Guardar</button></form>`).join('');
  return `<section class="pa-palabras"><h2>Las palabras</h2>
    <p class="pa-nota">Se pueden cambiar${limite}: cinco letras, del diccionario del juego y sin repetir. Después ya no
      se ven ni se cambian hasta que termine.</p>${filas}</section>`;
}

/** Antes de empezar, el dashboard no enseña las palabras: quien lo mira también puede jugar. */
function sinPalabras() {
  return `<section class="pa-palabras"><h2>Las palabras</h2>
    <p class="pa-nota">Se revisan en su propio enlace, para que el dashboard se pueda mirar sin conocerlas.</p></section>`;
}

/** En qué va cada uno: la palabra que juega con su reloj (con la hora del servidor), si ha terminado o si no ha empezado. */
function enQueVa(j, n, ahora) {
  if (j.jugando_desde) {
    const reloj = formatoTiempo(Math.max(0, Date.parse(ahora) - Date.parse(j.jugando_desde)));
    return `Jugando la ${Number(j.empezadas)}/${n} · ${reloj}`;
  }
  if (Number(j.terminadas) >= n && n > 0) return 'Ha terminado';
  return Number(j.empezadas) ? 'Entre palabras' : 'Sin empezar';
}

/** El campeonato F1 de grupos: los diez primeros suman 25, 18, 15… a su grupo. Quién los sumó, al lado. */
function campeonatoF1(grupos) {
  const filas = (grupos ?? []).map((g) => `<tr><td class="pa-puesto">${Number(g.puesto)}</td><td class="pa-nombre">${
    escapar(g.grupo)}</td><td class="pa-total">${cifra(g.puntos)}</td><td class="pa-quien">${(g.personas ?? [])
    .map((x) => `<span>${escapar(x.nombre)} <em>${cifra(x.puntos)}</em></span>`).join('')}</td></tr>`).join('');
  return `<section class="pa-ranking pa-f1"><h2>Grupos · F1</h2>
    <p class="pa-nota">Los diez primeros suman a su grupo 25, 18, 15, 12, 10, 8, 6, 4, 2 y 1.</p>
    <table><thead><tr><th>#</th><th>Grupo</th><th>Puntos</th><th class="pa-quien">Quién los suma</th></tr></thead>
    <tbody>${filas}</tbody></table></section>`;
}

/** Una fila por cada participante que ha entrado, por puesto, con su tiempo, en qué va y, en juego, el botón para echarlo. */
function participantesEnDirecto(p) {
  const n = (p.palabras ?? []).length;
  const entrados = (p.jugadores ?? []).filter((j) => j.elegido);
  if (!entrados.length) return '<section class="pa-ranking"><h2>Participantes</h2><p class="pa-nota">Aún no ha entrado nadie.</p></section>';
  const echar = (j) => (p.activo
    ? `<td><button type="button" class="ev-boton pequeno" data-liberar="${escapar(j.nombre)}">Echar</button></td>` : '');
  const filas = entrados.map((j) => `<tr><td class="pa-puesto">${Number(j.puesto)}</td><td class="pa-nombre">${
    escapar(j.nombre)}</td><td>${escapar(j.grupo)}</td><td class="pa-total">${cifra(j.puntos)}</td><td>${
    cifra(j.f1)}</td><td>${Number(j.resueltas)}/${n}</td><td>${formatoTiempo(Number(j.tiempo_ms) || 0)}</td><td>${
    enQueVa(j, n, p.ahora)}</td>${echar(j)}</tr>`).join('');
  return `<section class="pa-ranking"><h2>Participantes</h2><table><thead><tr><th>#</th><th>Nombre</th><th>Grupo</th>
    <th>Puntos</th><th>F1</th><th>Resueltas</th><th>Tiempo</th><th>Ahora</th>${p.activo ? '<th></th>' : ''}</tr></thead>
    <tbody>${filas}</tbody></table></section>`;
}

function rankingDeGrupos(grupos) {
  const filas = (grupos ?? []).map((g) => `<tr>
    <td class="pa-puesto">${Number(g.puesto)}</td><td class="pa-nombre">${escapar(g.grupo)}</td>
    <td class="pa-total">${cifra(g.puntos)}</td><td>${cifra(g.puntos_totales)}</td>
    <td>${Number(g.jugaron)}/${Number(g.miembros)}</td></tr>`).join('');
  return `<section class="pa-ranking"><h2>Grupos · media de la lista</h2><table><thead><tr><th>#</th><th>Grupo</th>
    <th>Puntos (media)</th><th>Total</th><th>Jugaron</th></tr></thead><tbody>${filas}</tbody></table></section>`;
}

function rankingDeParticipantes(jugadores, n) {
  const palabra = (j, i) => {
    const w = (j.palabras ?? []).find((x) => x.orden === i + 1);
    if (!w) return '<td class="pa-nada">—</td>';
    if (!w.resuelta) return '<td class="pa-nada">✕</td>';
    return `<td>${Number(w.intentos)} · ${formatoTiempo(w.tiempo_ms)} <em>${cifra(w.puntos)}</em></td>`;
  };
  const filas = (jugadores ?? []).map((j) => `<tr>
    <td class="pa-puesto">${Number(j.puesto)}</td><td class="pa-nombre">${escapar(j.nombre)}</td>
    <td>${escapar(j.grupo)}</td><td class="pa-total">${cifra(j.puntos)}</td>
    ${Array.from({ length: n }, (_, i) => palabra(j, i)).join('')}</tr>`).join('');
  const cabeza = Array.from({ length: n }, (_, i) => `<th>P${i + 1}</th>`).join('');
  return `<section class="pa-ranking"><h2>Cada palabra</h2><table><thead><tr><th>#</th><th>Nombre</th><th>Grupo</th>
    <th>Puntos</th>${cabeza}</tr></thead><tbody>${filas}</tbody></table></section>`;
}

/** El dashboard para un estado. Sin contraseña. */
export function vistaDelAdmin(s) {
  if (!s.panel) {
    return `<div class="pa pa-cartel"><p class="pa-estado">${s.sinConexion ? 'Sin conexión: reintentando…' : 'Cargando…'}</p>
      ${aviso(s)}</div>`;
  }
  const p = s.panel;
  if (p.antes) {
    return `<div class="pa pa-cartel">${cabecera(p)}${contadores(p)}${sinPalabras()}${aviso(s)}</div>`;
  }
  // Los dos rankings de grupos, uno al lado del otro; los participantes, a todo el ancho (son muchos y con muchas columnas).
  const rankings = `<div class="pa-columnas"><div>${campeonatoF1(p.grupos_f1)}</div><div>${rankingDeGrupos(p.grupos)}</div></div>
    ${participantesEnDirecto(p)}`;
  if (p.terminado) {
    const n = (p.palabras ?? []).length;
    return `<div class="pa pa-cartel">${cabecera(p)}
      <div class="pa-exportar">
        <button type="button" class="ev-boton" data-exportar="grupos">Grupos (CSV)</button>
        <button type="button" class="ev-boton" data-exportar="participantes">Participantes (CSV)</button>
        <button type="button" class="ev-boton" data-exportar="json">Todo (JSON)</button>
      </div>
      ${compartir(p)}${rankings}${rankingDeParticipantes(p.jugadores, n)}
      <section class="pa-soluciones"><h2>Las palabras</h2><ol>${(p.palabras ?? []).map((w) => (
    `<li value="${Number(w.orden)}">${escapar(String(w.palabra ?? '').toUpperCase())}</li>`)).join('')}</ol></section>
      ${aviso(s)}</div>`;
  }
  return `<div class="pa pa-cartel">${cabecera(p)}${contadores(p)}
    <p class="pa-nota">Puntos provisionales: cuentan las palabras terminadas y cambian mientras se juega. Se actualizan
      solos.</p>${rankings}${aviso(s)}</div>`;
}

// ── Borde ─────────────────────────────────────────────────────────────────────────────────────────────────

function descargar(nombre, contenido, tipo) {
  const url = URL.createObjectURL(new Blob([contenido], { type: tipo }));
  const enlace = Object.assign(document.createElement('a'), { href: url, download: nombre });
  document.body.append(enlace);
  enlace.click();
  enlace.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Copia el texto; sin permiso para el portapapeles, lo deja seleccionado para copiarlo a mano. */
async function copiar(texto, area) {
  try {
    await navigator.clipboard.writeText(texto);
  } catch {
    area?.select();
    document.execCommand?.('copy');
  }
}

/** Monta el dashboard. `temporizador` es `{cada(ms, fn)}`; `confirmar`, la pregunta antes de lo que no se deshace. */
export async function montarAdmin(contenedor, control, temporizador, evento, confirmar = (texto) => window.confirm(texto)) {
  const pintar = () => {
    contenedor.innerHTML = vistaDelAdmin(control.estado);
    document.title = control.estado.panel?.titulo ? `Admin · ${control.estado.panel.titulo}` : 'Admin';
  };

  contenedor.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formulario = e.target.closest('[data-formulario="palabra"]');
    if (!formulario) return;
    await control.cambiarPalabra(Number(formulario.dataset.orden), new FormData(formulario).get('palabra'));
    pintar();
  });

  contenedor.addEventListener('click', async (e) => {
    const liberar = e.target.closest('[data-liberar]')?.dataset.liberar;
    const exportar = e.target.closest('[data-exportar]')?.dataset.exportar;
    const compartirlo = e.target.closest('[data-compartir]')?.dataset.compartir;
    if (liberar && confirmar(`¿Echar a «${liberar}»? Su nombre queda libre y se borra lo que ha jugado.`)) await control.echar(liberar);
    else if (compartirlo === 'copiar') {
      await copiar(textoParaCompartir(control.estado.panel), contenedor.querySelector('.pa-compartir textarea'));
      return;
    } else if (exportar) {
      const datos = exportacion(control.estado.panel, evento);
      if (exportar === 'grupos') descargar(`${evento}-grupos.csv`, csvDeGrupos(datos), 'text/csv;charset=utf-8');
      else if (exportar === 'participantes') descargar(`${evento}-participantes.csv`, csvDeParticipantes(datos), 'text/csv;charset=utf-8');
      else descargar(`${evento}.json`, `${JSON.stringify(datos, null, 2)}\n`, 'application/json');
      return;
    } else return;
    pintar();
  });

  // Todo cambia solo: se repinta cada pocos segundos, salvo mientras se escribe una palabra (no se pierde lo escrito)
  // y con el evento terminado, que ya no se mueve.
  temporizador.cada(3000, async () => {
    if (control.estado.panel?.terminado || contenedor.contains(document.activeElement?.closest?.('input') ?? null)) return;
    await control.refrescar();
    pintar();
  });

  await control.refrescar();
  pintar();
}

// ── Las palabras, en su propio enlace ─────────────────────────────────────────────────────────────────────

/** El control de `/evento/palabras`: leer las palabras y cambiar una, solo antes de empezar. */
export function controlDePalabras({ api }) {
  const s = { datos: null, cerrado: null, aviso: null, sinConexion: false, ocupado: false };

  async function refrescar() {
    try {
      s.datos = await api.palabras();
      s.cerrado = null;
      s.sinConexion = false;
    } catch (error) {
      if (error.tipo === 'red') s.sinConexion = true;
      else s.cerrado = error.message;
    }
  }

  async function cambiarPalabra(orden, palabra) {
    if (s.ocupado) return;
    s.ocupado = true;
    try {
      await api.cambiarPalabra(orden, palabra);
      s.aviso = `Palabra ${Number(orden)} guardada.`;
    } catch (error) {
      s.aviso = error.tipo === 'rechazo' ? error.message : 'No se ha podido conectar. Prueba otra vez.';
    } finally {
      s.ocupado = false;
    }
    await refrescar();
  }

  return { estado: s, refrescar, cambiarPalabra };
}

/** La página de las palabras: con el estilo del cartel; empezado el evento, solo dice que ya no se ven aquí. */
export function vistaDePalabras(s) {
  if (s.cerrado) {
    return `<div class="pa pa-cartel"><p class="pa-estado">${escapar(s.cerrado)}</p></div>`;
  }
  if (!s.datos) {
    return `<div class="pa pa-cartel"><p class="pa-estado">${s.sinConexion ? 'Sin conexión: reintentando…' : 'Cargando…'}</p>
      ${aviso(s)}</div>`;
  }
  const p = { ...s.datos, antes: true };
  return `<div class="pa pa-cartel">${cabecera(p)}${editorDePalabras(p)}${aviso(s)}</div>`;
}

export async function montarPalabras(contenedor, control) {
  const pintar = () => {
    contenedor.innerHTML = vistaDePalabras(control.estado);
    document.title = 'Las palabras';
  };
  contenedor.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formulario = e.target.closest('[data-formulario="palabra"]');
    if (!formulario) return;
    await control.cambiarPalabra(Number(formulario.dataset.orden), new FormData(formulario).get('palabra'));
    pintar();
  });
  await control.refrescar();
  pintar();
}
