/**
 * El apartado «Debate de reglas» de Info: las votaciones abiertas y las propuestas del grupo.
 *
 * Slice: `debate-de-reglas`. Quién eres se elige con el mismo selector del SuperWordleBros, y se recuerda con la
 * misma clave: quien ya se eligió para jugar no tiene que volver a hacerlo aquí. **Los votos se enseñan con su
 * nombre** porque nadie inicia sesión: si alguien vota por otro, el otro lo ve y lo cambia.
 */

import { DEBATE } from '../data/results.js';
import { nombreVisible } from '../domain/apodos.js';
import { recuento } from '../domain/debate.js';
import { jugadoresDelGrupo } from '../domain/superbros.js';
import { jugadorRecordado, recordarJugador, selectorDeJugador } from './juego.js';
import { escapar } from './shell.js';

const votos = (n) => `${n} ${n === 1 ? 'voto' : 'votos'}`;

/** El nombre de Slack de un id, sin apodo: el apodo se pone al pintar. Quien no está en la lista es «alguien». */
function nombrePor(jugadores) {
  const nombres = new Map((jugadores ?? []).map(({ jugador, nombre }) => [jugador, nombre]));
  return (id) => nombres.get(id) ?? 'alguien';
}

function vistaVotacion(votacion, todos, nombre, elegido) {
  const opciones = recuento(votacion, todos);
  const miVoto = opciones.find((o) => o.votantes.includes(elegido))?.id ?? null;
  const filas = opciones.map((o) => {
    const quienes = o.votantes.map((id) => nombreVisible(nombre(id))).sort((a, b) => a.localeCompare(b, 'es')).join(', ');
    const boton = votacion.abierta
      ? `<button type="button" class="votar" data-votacion="${escapar(votacion.id)}" data-opcion="${escapar(o.id)}"`
        + ` aria-pressed="${o.id === miVoto}">${o.id === miVoto ? 'Tu voto' : 'Votar'}</button>`
      : '';
    return `
        <li class="opcion${o.id === miVoto ? ' mia' : ''}">
          <div class="opcion-texto">
            <strong>${escapar(o.texto)}</strong>
            <span class="opcion-votos">${votos(o.total)}${quienes ? ` · ${escapar(quienes)}` : ''}</span>
          </div>
          ${boton}
        </li>`;
  }).join('');
  return `
      <article class="votacion${votacion.abierta ? '' : ' cerrada'}">
        <h3>${escapar(votacion.titulo)} <span class="etiqueta">${votacion.abierta ? 'en votación' : 'votación cerrada'}</span></h3>
        ${votacion.descripcion ? `<p>${escapar(votacion.descripcion)}</p>` : ''}
        <ul class="opciones">${filas}</ul>
      </article>`;
}

function vistaPropuestas(propuestas, nombre) {
  if (!propuestas?.length) return '<p class="nota">Todavía no hay propuestas aprobadas. ¡Estrena tú la primera!</p>';
  return `<ul class="propuestas">${propuestas.map((p) => `
      <li>
        <strong>${escapar(p.titulo)}</strong>
        <p>${escapar(p.texto)}</p>
        <span class="nota">Propuesta de ${escapar(nombreVisible(nombre(p.autor)))}</span>
      </li>`).join('')}</ul>`;
}

/** El apartado entero. Exportado para poder verificarlo sin navegador. */
export function vistaDebate(datos, jugadores, elegido) {
  const nombre = nombrePor(jugadores);
  const votaciones = (datos?.votaciones ?? []).map((v) => vistaVotacion(v, datos?.votos, nombre, elegido)).join('');
  return `
    ${selectorDeJugador(jugadores, elegido)}
    <p class="estado-debate" role="status"></p>
    ${votaciones || '<p class="nota">Todavía no hay votaciones.</p>'}
    <h3 class="eje-titulo">Propuestas del grupo</h3>
    ${vistaPropuestas(datos?.propuestas, nombre)}
    <form class="propuesta-nueva">
      <h3 class="eje-titulo">Propón una regla</h3>
      <label>Título <input name="titulo" maxlength="120" required></label>
      <label>Explícala <textarea name="texto" rows="4" maxlength="2000" required></textarea></label>
      <button type="submit">Enviar propuesta</button>
      <p class="nota">Va firmada con tu nombre y se publica aquí cuando se aprueba.</p>
      <p class="estado-propuesta" role="status"></p>
    </form>`;
}

/** Lo que dice la base de datos al rechazar algo, sin el prefijo técnico. */
const motivo = (error) => String(error?.message ?? error).replace(/^Supabase:\s*/, '');

/**
 * Votar y proponer, sin DOM: decide si se envía y qué se le dice a quien lo intenta. Así se verifica sin navegador.
 */
export function controlDelDebate({ api = DEBATE } = {}) {
  return {
    async votar(elegido, votacion, opcion) {
      if (!elegido) return { estado: 'sin-jugador', texto: 'Elige tu nombre para votar.' };
      try {
        await api.votar({ votacion, votante: elegido, opcion });
        return { estado: 'votado', texto: 'Voto guardado. Puedes cambiarlo mientras la votación siga abierta.' };
      } catch (error) {
        return { estado: 'error', texto: `No se ha podido guardar el voto: ${motivo(error)}.` };
      }
    },
    async proponer(elegido, titulo, texto) {
      if (!elegido) return { estado: 'sin-jugador', texto: 'Elige tu nombre para proponer.' };
      const limpio = { autor: elegido, titulo: String(titulo ?? '').trim(), texto: String(texto ?? '').trim() };
      if (!limpio.titulo || !limpio.texto) return { estado: 'incompleta', texto: 'Falta el título o la explicación.' };
      try {
        await api.proponer(limpio);
        return { estado: 'pendiente', texto: '¡Recibida! Aparecerá aquí cuando se apruebe.' };
      } catch (error) {
        return { estado: 'error', texto: `No se ha podido enviar: ${motivo(error)}.` };
      }
    },
  };
}

function almacenDe(documento) {
  try {
    return documento?.defaultView?.localStorage ?? null;
  } catch {
    return null;
  }
}

/** Pinta el apartado en `contenedor` y lo deja funcionando. Si la base de datos no responde, lo dice. */
export async function pintarDebate(contenedor, resultados, api = DEBATE) {
  if (!contenedor) return;
  contenedor.innerHTML = '<p class="etiqueta">cargando el debate…</p>';
  const jugadores = jugadoresDelGrupo(resultados);
  const almacen = almacenDe(contenedor.ownerDocument);
  let elegido = jugadorRecordado(almacen, jugadores);
  const control = controlDelDebate({ api });
  let datos;

  const avisar = (resultado, donde = '.estado-debate') => {
    const estado = contenedor.querySelector(donde);
    if (estado) estado.textContent = resultado.texto;
    contenedor.querySelector('.quien-eres')?.classList.toggle('pide-nombre', resultado.estado === 'sin-jugador');
  };

  const montar = (aviso) => {
    // Votar o cambiar de nombre redibuja el apartado: lo que se estuviera escribiendo en la propuesta se conserva.
    const borrador = contenedor.querySelector?.('.propuesta-nueva');
    const escrito = borrador ? { titulo: borrador.titulo.value, texto: borrador.texto.value } : null;
    contenedor.innerHTML = vistaDebate(datos, jugadores, elegido);
    const formulario = contenedor.querySelector?.('.propuesta-nueva');
    if (escrito && formulario) {
      formulario.titulo.value = escrito.titulo;
      formulario.texto.value = escrito.texto;
    }
    if (aviso) avisar(aviso);
    if (!contenedor.querySelector) return;
    contenedor.querySelector('.quien-eres-lista')?.addEventListener('change', (evento) => {
      elegido = evento.target.value || null;
      recordarJugador(almacen, elegido ?? '');
      montar();
    });
    contenedor.querySelectorAll('button.votar').forEach((boton) => boton.addEventListener('click', async () => {
      const resultado = await control.votar(elegido, boton.dataset.votacion, boton.dataset.opcion);
      // También si falla: la votación puede haberse cerrado mientras tanto, y entonces sobran los botones.
      if (resultado.estado !== 'sin-jugador') datos = await api.leer().catch(() => datos);
      montar(resultado);
    }));
    contenedor.querySelector('.propuesta-nueva')?.addEventListener('submit', async (evento) => {
      evento.preventDefault();
      const formulario = evento.target;
      const resultado = await control.proponer(elegido, formulario.titulo.value, formulario.texto.value);
      if (resultado.estado === 'pendiente') formulario.reset();
      avisar(resultado, '.estado-propuesta');
    });
  };

  try {
    datos = await api.leer();
  } catch {
    contenedor.innerHTML = '<p class="nota">No se ha podido cargar el debate. Prueba a recargar la página.</p>';
    return;
  }
  montar();
}
