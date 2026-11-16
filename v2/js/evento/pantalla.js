/**
 * La pantalla del proyector del evento: `/evento/pantalla`.
 *
 * Slice: `pantalla-del-evento`. El presentador empieza el evento con el PIN; desde ahí la pantalla enseña cuántas
 * frases van liberadas y cuánto falta para la siguiente, los contadores de cada frase **sin nombres ni tiempos** y,
 * con todas fuera, el botón de terminar. Terminado, el ranking y las frases. No lleva reloj propio: se reconstruye
 * del estado del servidor.
 */

import { escapar } from '../ui/shell.js';
import { cuentaAtras, desfase, formatoTiempo, momentoDelEvento } from './dominio.js';

export function controlDeLaPantalla({ api, reloj }) {
  // `clave`: la contraseña de acceso, si el evento la pide; solo en memoria (al recargar se vuelve a pedir).
  const s = { estado: null, desfase: 0, ranking: null, aviso: null, sinConexion: false, clave: null };

  const ahora = () => reloj() + s.desfase;

  async function refrescar() {
    const pedido = reloj();
    try {
      const estado = await api.estado(null, s.clave);
      s.desfase = desfase(estado.ahora, (pedido + reloj()) / 2);
      s.estado = estado;
      s.sinConexion = false;
      if (estado.terminado && !s.ranking) s.ranking = await api.ranking(null, s.clave);
    } catch (error) {
      if (error.tipo === 'red') s.sinConexion = true;
      else s.aviso = error.message;
    }
  }

  async function conPin(accion, pin) {
    try {
      await accion(pin);
      s.aviso = null;
    } catch (error) {
      s.aviso = error.tipo === 'rechazo' && /PIN/.test(error.message) ? 'El PIN no es correcto.'
        : error.tipo === 'rechazo' ? error.message : 'No se ha podido conectar. Prueba otra vez.';
    }
    await refrescar();
  }

  async function desbloquear(clave) {
    s.clave = clave || null;
    await refrescar();
    if (s.estado?.bloqueado) {
      s.clave = null;
      s.aviso = 'Contraseña incorrecta.';
    } else {
      s.aviso = null;
    }
  }

  return {
    estado: s,
    ahora,
    refrescar,
    desbloquear,
    empezar: (pin) => conPin(api.empezarEvento, pin),
    terminar: (pin) => conPin(api.terminarEvento, pin),
  };
}

function formularioDelPin(accion, texto) {
  return `<form class="pa-pin" data-formulario="${accion}">
    <input name="pin" type="password" autocomplete="off" placeholder="PIN" aria-label="PIN">
    <button type="submit" class="ev-boton">${texto}</button>
  </form>`;
}

function contadores(liberadas) {
  const filas = liberadas.map((f) => `<tr><th>Frase ${Number(f.orden)}</th>
    <td><strong>${Number(f.jugando) || 0}</strong> jugando</td>
    <td><strong>${Number(f.resueltas) || 0}</strong> la han resuelto</td>
    <td><strong>${Number(f.sin_resolver) || 0}</strong> sin palabras</td></tr>`).join('');
  return `<table class="pa-contadores"><tbody>${filas}</tbody></table>`;
}

function soluciones(estado) {
  const con = (estado?.frases ?? []).filter((f) => f.solucion);
  if (!con.length) return '';
  return `<section class="pa-soluciones"><h2>Las frases</h2><ol>${con.map((f) => (
    `<li value="${Number(f.orden)}">${escapar(f.solucion)}</li>`
  )).join('')}</ol></section>`;
}

const frases = (n) => `${n} ${n === 1 ? 'frase' : 'frases'}`;

export function vistaDelRankingFinal(filas) {
  const podio = (filas ?? []).filter((f) => f.puesto <= 3).map((f) => (
    `<li class="pa-podio-${Number(f.puesto)}"><span>${Number(f.puesto)}º</span><strong>${escapar(f.nombre)}</strong>`
    + `<em>${frases(Number(f.resueltas))} · ${formatoTiempo(f.tiempo_ms)}</em></li>`)).join('');
  const cuerpo = (filas ?? []).map((f) => `<tr>
      <td class="pa-puesto">${Number(f.puesto)}</td>
      <td class="pa-nombre">${escapar(f.nombre)}</td>
      <td>${Number(f.resueltas)}</td>
      <td class="pa-total">${formatoTiempo(f.tiempo_ms)}</td>
    </tr>`).join('');
  return `<section class="pa-ranking"><h1>Ranking final</h1>${podio ? `<ol class="pa-podio">${podio}</ol>` : ''}
    <table><thead><tr><th>#</th><th>Nombre</th><th>Frases</th><th>Tiempo</th></tr></thead><tbody>${cuerpo}</tbody></table>
  </section>`;
}

/** La pantalla para un estado, una hora (corregida al servidor) y la dirección por la que se entra. */
export function vistaDeLaPantalla(s, ahora, direccion) {
  const titulo = escapar(s.estado?.titulo ?? 'La frase del evento');
  const aviso = s.aviso || s.sinConexion
    ? `<p class="ev-aviso" role="alert">${escapar(s.aviso ?? 'Sin conexión: reintentando…')}</p>` : '';
  // Con contraseña, nada del evento hasta que se escribe: ni título, ni dirección, ni contadores.
  if (s.estado?.bloqueado) {
    return `<div class="pa"><form class="pa-pin" data-formulario="clave">
      <input name="clave" type="password" autocomplete="off" placeholder="Contraseña" aria-label="Contraseña">
      <button type="submit" class="ev-boton">Entrar</button></form>${aviso}</div>`;
  }
  const m = momentoDelEvento(s.estado, ahora);

  if (m.tipo === 'terminado') {
    return `<div class="pa">${vistaDelRankingFinal(s.ranking)}${soluciones(s.estado)}</div>`;
  }
  if (m.tipo === 'sin-empezar') {
    return `<div class="pa"><h1 class="pa-titulo">${titulo}</h1>
      <p class="pa-entra">Entra en <strong>${escapar(direccion)}</strong></p>
      <p class="pa-apuntados"><strong>${Number(s.estado?.participantes) || 0}</strong> participantes apuntados</p>
      <p class="pa-nota">El juego está a punto de empezar.</p>
      ${formularioDelPin('empezar', 'Empezar el evento')}${aviso}</div>`;
  }
  const cabecera = `<p class="pa-entra">${escapar(direccion)}</p>
    <h1 class="pa-titulo">${m.liberadas.length} de ${m.total} frases en juego</h1>`;
  const siguiente = m.siguiente
    ? `<p class="pa-nota">La frase ${Number(m.siguiente.orden)} sale en</p>
       <p class="pa-reloj" data-cuenta-atras="${Date.parse(m.siguiente.abre_en)}">${cuentaAtras(m.faltaMs)}</p>`
    : `<p class="pa-nota">Ya están todas. Cuando quieras, termina el evento para ver el ranking.</p>
       ${formularioDelPin('terminar', 'Terminar el evento')}`;
  return `<div class="pa">${cabecera}${siguiente}${contadores(m.liberadas)}${aviso}</div>`;
}

/** Monta la pantalla. `temporizador` es `{cada(ms, fn)}`. */
export async function montarPantalla(contenedor, control, temporizador, direccion) {
  const pintar = () => {
    contenedor.innerHTML = vistaDeLaPantalla(control.estado, control.ahora(), direccion);
    document.title = control.estado.estado?.titulo || 'Acceso';
  };

  contenedor.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const datos = new FormData(evento.target);
    const pin = datos.get('pin');
    if (evento.target.dataset.formulario === 'clave') await control.desbloquear(datos.get('clave'));
    else if (evento.target.dataset.formulario === 'terminar') await control.terminar(pin);
    else await control.empezar(pin);
    pintar();
  });

  temporizador.cada(1000, async () => {
    for (const reloj of contenedor.querySelectorAll('[data-cuenta-atras]')) {
      const falta = Number(reloj.dataset.cuentaAtras) - control.ahora();
      reloj.textContent = cuentaAtras(falta);
      if (falta <= 0) {
        await control.refrescar();
        pintar();
        return;
      }
    }
  });
  // Los contadores cambian sin que cambie la fase: el proyector se repinta en cada sondeo, salvo con el PIN a medias.
  temporizador.cada(3000, async () => {
    const pin = contenedor.querySelector('[data-formulario] input');
    // Con el PIN a medias o el cursor en el campo, repintar le quitaría el foco y lo escrito.
    if (pin && (pin.value || document.activeElement === pin)) return;
    await control.refrescar();
    pintar();
  });

  await control.refrescar();
  pintar();
}
