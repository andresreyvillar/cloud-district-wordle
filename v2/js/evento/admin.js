/**
 * La pantalla del admin del evento: `/evento/admin`.
 *
 * Slice: `admin-del-evento`. Con el PIN, el admin activa el evento cuando quiere y lo sigue **en directo**: contadores
 * por palabra, una fila por cada participante que ha entrado (en qué palabra va, su tiempo, sus puntos y un botón para
 * echarlo) y el ranking provisional de participantes y grupos. Lo termina, y entonces ve las soluciones, exporta los
 * puntos (JSON y CSV) y comparte los resultados en texto por WhatsApp o email.
 *
 * El PIN vive solo en memoria: al recargar se vuelve a pedir.
 */

import { escapar } from '../ui/shell.js';
import { formatoTiempo } from './dominio.js';

export function controlDelAdmin({ api }) {
  const s = { pin: null, panel: null, aviso: null, sinConexion: false, ocupado: false };

  async function refrescar() {
    if (!s.pin) return;
    try {
      s.panel = await api.panel(s.pin);
      s.sinConexion = false;
    } catch (error) {
      if (error.tipo === 'red') s.sinConexion = true;
      else s.aviso = error.message;
    }
  }

  /** Prueba el PIN: si vale, se queda en memoria y se ve el panel. */
  async function entrar(pin) {
    if (!String(pin ?? '')) {
      s.aviso = 'Escribe el PIN.';
      return;
    }
    try {
      s.panel = await api.panel(pin);
      s.pin = pin;
      s.aviso = null;
    } catch (error) {
      s.aviso = error.tipo === 'rechazo' ? error.message : 'No se ha podido conectar. Prueba otra vez.';
    }
  }

  async function conPin(accion) {
    if (!s.pin || s.ocupado) return;
    s.ocupado = true;
    try {
      await accion();
      s.aviso = null;
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
    entrar,
    activar: () => conPin(() => api.activar(s.pin)),
    terminar: () => conPin(() => api.terminar(s.pin)),
    liberar: (nombre) => conPin(() => api.liberar(s.pin, nombre)),
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
      puesto: g.puesto, grupo: g.grupo, puntos: Number(g.puntos), puntos_totales: g.puntos_totales,
      miembros: g.miembros, jugaron: g.jugaron,
    })),
    participantes: (panel.jugadores ?? []).map((j) => ({
      puesto: j.puesto, nombre: j.nombre, grupo: j.grupo, puntos: j.puntos, palabras: j.palabras,
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

/** Los grupos en CSV: puesto, grupo, puntos (la media), puntos totales, miembros y cuántos jugaron. */
export function csvDeGrupos(datos) {
  return [filaCsv(['puesto', 'grupo', 'puntos', 'puntos_totales', 'miembros', 'jugaron']),
    ...datos.grupos.map((g) => filaCsv([g.puesto, g.grupo, g.puntos, g.puntos_totales, g.miembros, g.jugaron]))]
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
    return filaCsv([p.puesto, p.nombre, p.grupo, p.puntos, ...porPalabra]);
  });
  return [filaCsv(['puesto', 'nombre', 'grupo', 'puntos', ...columnas]), ...filas].join('\n') + '\n';
}

// ── Compartir ──────────────────────────────────────────────────────────────────────────────────────────

const MEDALLAS = { 1: '🥇', 2: '🥈', 3: '🥉' };

/** Los puntos en español: «0,5», «12,25». */
function formatoPuntos(n) {
  const valor = Number(n) || 0;
  const texto = valor.toLocaleString('es-ES', { maximumFractionDigits: 2 });
  return `${texto} ${valor === 1 ? 'punto' : 'puntos'}`;
}

const conMedalla = (puesto) => MEDALLAS[Number(puesto)] ?? `${Number(puesto)}.`;

/** Los resultados en texto, para pegar en WhatsApp o en un email: todos los grupos por puesto y el podio. */
export function textoParaCompartir(panel) {
  const grupos = (panel?.grupos ?? []).map((g) => `${conMedalla(g.puesto)} ${g.grupo} · ${formatoPuntos(g.puntos)}`);
  const podio = (panel?.jugadores ?? []).filter((j) => Number(j.puesto) <= 3 && Number(j.puntos) > 0)
    .map((j) => `${conMedalla(j.puesto)} ${j.nombre} (${j.grupo}) · ${formatoPuntos(j.puntos)}`);
  return [`🏆 ${panel?.titulo ?? ''} — resultados`, '', 'GRUPOS', ...grupos,
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

function aviso(s) {
  const texto = s.aviso ?? (s.sinConexion ? 'Sin conexión: reintentando…' : null);
  return texto ? `<p class="ev-aviso" role="alert">${escapar(texto)}</p>` : '';
}

function contadores(palabras) {
  const filas = (palabras ?? []).map((p) => `<tr><th>Palabra ${Number(p.orden)}</th>
    <td><strong>${Number(p.jugando) || 0}</strong> jugando</td>
    <td><strong>${Number(p.resueltas) || 0}</strong> resuelta</td>
    <td><strong>${Number(p.falladas) || 0}</strong> fallada</td></tr>`).join('');
  return `<table class="pa-contadores"><tbody>${filas}</tbody></table>`;
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

/** Una fila por cada participante que ha entrado, por puesto, con su tiempo, en qué va y el botón para echarlo. */
function participantesEnDirecto(p) {
  const n = (p.palabras ?? []).length;
  const entrados = (p.jugadores ?? []).filter((j) => j.elegido);
  if (!entrados.length) return '';
  const filas = entrados.map((j) => `<tr><td class="pa-puesto">${Number(j.puesto)}</td><td class="pa-nombre">${
    escapar(j.nombre)}</td><td>${escapar(j.grupo)}</td><td class="pa-total">${Number(j.puntos)}</td><td>${
    Number(j.resueltas)}/${n}</td><td>${formatoTiempo(Number(j.tiempo_ms) || 0)}</td><td>${enQueVa(j, n, p.ahora)}</td>
    <td><button type="button" class="ev-boton pequeno" data-liberar="${escapar(j.nombre)}">Echar</button></td></tr>`).join('');
  return `<section class="pa-ranking"><h2>Participantes</h2><table><thead><tr><th>#</th><th>Nombre</th><th>Grupo</th>
    <th>Puntos</th><th>Resueltas</th><th>Tiempo</th><th>Ahora</th><th></th></tr></thead><tbody>${filas}</tbody></table>
    </section>`;
}

function rankingDeGrupos(grupos) {
  const filas = (grupos ?? []).map((g) => `<tr>
    <td class="pa-puesto">${Number(g.puesto)}</td><td class="pa-nombre">${escapar(g.grupo)}</td>
    <td class="pa-total">${escapar(String(g.puntos))}</td><td>${Number(g.puntos_totales)}</td>
    <td>${Number(g.jugaron)}/${Number(g.miembros)}</td></tr>`).join('');
  return `<section class="pa-ranking"><h1>Grupos</h1><table><thead><tr><th>#</th><th>Grupo</th><th>Puntos (media)</th>
    <th>Total</th><th>Jugaron</th></tr></thead><tbody>${filas}</tbody></table></section>`;
}

function rankingDeParticipantes(jugadores, n) {
  const palabra = (j, i) => {
    const w = (j.palabras ?? []).find((x) => x.orden === i + 1);
    if (!w) return '<td class="pa-nada">—</td>';
    if (!w.resuelta) return '<td class="pa-nada">✕</td>';
    return `<td>${Number(w.intentos)} · ${formatoTiempo(w.tiempo_ms)} <em>${Number(w.puntos)}</em></td>`;
  };
  const filas = (jugadores ?? []).map((j) => `<tr>
    <td class="pa-puesto">${Number(j.puesto)}</td><td class="pa-nombre">${escapar(j.nombre)}</td>
    <td>${escapar(j.grupo)}</td><td class="pa-total">${Number(j.puntos)}</td>
    ${Array.from({ length: n }, (_, i) => palabra(j, i)).join('')}</tr>`).join('');
  const cabeza = Array.from({ length: n }, (_, i) => `<th>P${i + 1}</th>`).join('');
  return `<section class="pa-ranking"><h2>Participantes</h2><table><thead><tr><th>#</th><th>Nombre</th><th>Grupo</th>
    <th>Puntos</th>${cabeza}</tr></thead><tbody>${filas}</tbody></table></section>`;
}

/** La pantalla del admin para un estado. */
export function vistaDelAdmin(s) {
  if (!s.pin || !s.panel) {
    return `<div class="pa"><form class="pa-pin" data-formulario="pin">
      <input name="pin" type="password" inputmode="numeric" autocomplete="off" placeholder="PIN" aria-label="PIN">
      <button type="submit" class="ev-boton">Entrar</button></form>${aviso(s)}</div>`;
  }
  const p = s.panel;
  const titulo = `<h1 class="pa-titulo">${escapar(p.titulo ?? '')}</h1>`;
  const elegidos = `<p class="pa-apuntados"><strong>${Number(p.elegidos) || 0}</strong> de ${Number(p.participantes) || 0}
    participantes han elegido su nombre</p>`;

  if (p.terminado) {
    const n = (p.palabras ?? []).length;
    return `<div class="pa">${titulo}
      <div class="pa-exportar">
        <button type="button" class="ev-boton" data-exportar="grupos">Grupos (CSV)</button>
        <button type="button" class="ev-boton" data-exportar="participantes">Participantes (CSV)</button>
        <button type="button" class="ev-boton" data-exportar="json">Todo (JSON)</button>
      </div>
      ${compartir(p)}${rankingDeGrupos(p.grupos)}${rankingDeParticipantes(p.jugadores, n)}
      <section class="pa-soluciones"><h2>Las palabras</h2><ol>${(p.palabras ?? []).map((w) => (
    `<li value="${Number(w.orden)}">${escapar(String(w.palabra ?? '').toUpperCase())}</li>`)).join('')}</ol></section>
      ${aviso(s)}</div>`;
  }
  if (!p.activo) {
    return `<div class="pa">${titulo}<p class="pa-nota">El evento no está activo: quien entra ve «El evento se activará en
      breve».</p>${elegidos}
      <button type="button" class="ev-boton grande" data-accion="activar">Activar el evento</button>${aviso(s)}</div>`;
  }
  return `<div class="pa">${titulo}<p class="pa-nota">Evento activo</p>${elegidos}${contadores(p.palabras)}
    <button type="button" class="ev-boton grande peligro" data-accion="terminar">Terminar el evento</button>
    <p class="pa-nota">Puntos provisionales: cuentan las palabras terminadas y cambian mientras se juega. Se actualizan
      solos.</p>
    ${rankingDeGrupos(p.grupos)}${participantesEnDirecto(p)}${aviso(s)}</div>`;
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

/** Monta la pantalla. `temporizador` es `{cada(ms, fn)}`; `confirmar`, la pregunta antes de lo que no se deshace. */
export async function montarAdmin(contenedor, control, temporizador, evento, confirmar = (texto) => window.confirm(texto)) {
  const pintar = () => {
    contenedor.innerHTML = vistaDelAdmin(control.estado);
    document.title = control.estado.panel?.titulo ? `Admin · ${control.estado.panel.titulo}` : 'Admin';
  };

  contenedor.addEventListener('submit', async (e) => {
    e.preventDefault();
    await control.entrar(new FormData(e.target).get('pin'));
    pintar();
  });

  contenedor.addEventListener('click', async (e) => {
    const accion = e.target.closest('[data-accion]')?.dataset.accion;
    const liberar = e.target.closest('[data-liberar]')?.dataset.liberar;
    const exportar = e.target.closest('[data-exportar]')?.dataset.exportar;
    const compartirlo = e.target.closest('[data-compartir]')?.dataset.compartir;
    if (accion === 'activar' && confirmar('¿Activar el evento? Todo el mundo podrá empezar a jugar.')) await control.activar();
    else if (accion === 'terminar' && confirmar('¿Terminar el evento? No se admitirán más intentos.')) await control.terminar();
    else if (liberar && confirmar(`¿Echar a «${liberar}»? Su nombre queda libre y se borra lo que ha jugado.`)) await control.liberar(liberar);
    else if (compartirlo === 'copiar') {
      await copiar(textoParaCompartir(control.estado.panel), contenedor.querySelector('.pa-compartir textarea'));
      return;
    }
    else if (exportar) {
      const datos = exportacion(control.estado.panel, evento);
      if (exportar === 'grupos') descargar(`${evento}-grupos.csv`, csvDeGrupos(datos), 'text/csv;charset=utf-8');
      else if (exportar === 'participantes') descargar(`${evento}-participantes.csv`, csvDeParticipantes(datos), 'text/csv;charset=utf-8');
      else descargar(`${evento}.json`, `${JSON.stringify(datos, null, 2)}\n`, 'application/json');
      return;
    } else return;
    pintar();
  });

  // Los contadores cambian solos: se repinta cada pocos segundos, salvo con la lista de nombres abierta.
  temporizador.cada(3000, async () => {
    if (!control.estado.pin || control.estado.panel?.terminado || contenedor.querySelector('details[open]')) return;
    await control.refrescar();
    pintar();
  });

  pintar();
}
