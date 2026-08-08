/**
 * La jornada en curso: quién ha jugado, quién falta y si el día cuenta todavía.
 *
 * Slice: `resultado-del-dia` (openspec/slices/estadisticas/resultado-del-dia.md).
 *
 * Función **pura**: entran las filas y la instantánea, sale un objeto. No lee el reloj —la jornada se deriva
 * de los datos— así que la vista es reproducible y no queda vacía a las 00:05 (§10 del protocolo).
 *
 * **Es la excepción declarada al [ADR 0008](../../../openspec/decisions/0008-donde-vive-el-calculo.md).** La
 * jornada abierta no está materializada: el cron corre cada hora y una hora de retraso en la vista de "hoy"
 * es justo donde más se nota. Así que la media del día se calcula aquí, sobre las filas crudas.
 *
 * Lo que **no** se duplica son los umbrales: la muestra mínima se lee de las reglas que viajan dentro de la
 * instantánea, y esas salen de la constante que usa el cálculo. Escribir un `5` en este archivo sería la
 * divergencia que la página de reglas existe para evitar.
 */

const FALLO = 7;

/** El identificador de la regla que fija la muestra mínima, en el catálogo de `tools/rules.py`. */
const REGLA_DE_LA_MUESTRA = 'dia-con-muestra-minima';

/** Sábado y domingo en `Date.prototype.getUTCDay()`. Una fecha `AAAA-MM-DD` se parsea como UTC. */
const FIN_DE_SEMANA = new Set([0, 6]);

function redondear(valor, decimales = 2) {
  const factor = 10 ** decimales;
  return Math.round(valor * factor) / factor;
}

/**
 * La muestra mínima **según las reglas publicadas**, o `null` si la instantánea no las trae.
 *
 * Devolver `null` en lugar de un valor por defecto es deliberado: un número inventado aquí afirmaría que la
 * jornada cuenta (o que no) con un umbral que el cálculo no usa.
 */
/**
 * Las figuras de una jornada: `jugador → emoji`, tal y como las publica la instantánea.
 *
 * **La web no clasifica.** `results.js` trae la cuadrícula cruda y la tentación es interpretarla aquí, pero
 * serían 120 líneas de reglas calibradas contra 30 fichas etiquetadas: una copia que divergiría del álbum y
 * del bot en la primera recalibración.
 *
 * Devuelve un mapa vacío si la instantánea no las trae —el estado de cualquier instantánea anterior a este
 * slice— o si las que trae **son de otra jornada**: publicar la de ayer sobre la de hoy sería peor que no
 * publicar nada.
 */
export function figurasDeLaJornada(carga, jornada) {
  const ultima = carga?.album?.ultima_jornada;
  if (!ultima || ultima.jornada !== jornada) return new Map();

  const emojiDe = new Map(
    (carga.album.categorias ?? []).map((c) => [c.clave, c.emoji ?? c.clave]),
  );
  return new Map(
    Object.entries(ultima.figuras ?? {}).map(([jugador, categoria]) => [
      jugador,
      emojiDe.get(categoria) ?? categoria,
    ]),
  );
}

export function minimoDeLaMuestra(reglas) {
  const regla = (reglas ?? []).find((r) => r.id === REGLA_DE_LA_MUESTRA);
  const parametro = (regla?.parametros ?? []).find((p) => typeof p.valor === 'number');
  return parametro ? parametro.valor : null;
}

/** Si esa fecha es laborable. Es la misma regla que `tools/calendario.py`, aplicada a una sola fecha. */
export function esLaborable(fecha) {
  const dia = new Date(`${fecha}T00:00:00Z`).getUTCDay();
  return !FIN_DE_SEMANA.has(dia);
}

/**
 * La jornada en curso.
 *
 * `nombres` es un mapa opcional `jugador → nombre` para poder nombrar a quien falta: quien no ha jugado hoy
 * no aparece en las filas de hoy, así que su nombre tiene que venir de otro sitio.
 */
export function diaEnCurso(resultados, carga, nombres = new Map()) {
  const jornada = resultados.reduce((alta, fila) => Math.max(alta, fila.jornada), 0);
  if (!jornada) {
    return { existe: false, jornada: null, fecha: null, jugaron: [], faltan: [], cuantos_faltan: 0 };
  }

  const deHoy = resultados.filter((fila) => fila.jornada === jornada);
  const fecha = deHoy[0].fecha;
  const laborable = esLaborable(fecha);
  const minimo = minimoDeLaMuestra(carga?.reglas);

  const jugaron = [...deHoy]
    .sort((a, b) => a.intentos - b.intentos || a.nombre.localeCompare(b.nombre))
    .map((fila) => ({
      jugador: fila.jugador,
      nombre: fila.nombre,
      intentos: fila.intentos,
      fallo: fila.intentos >= FALLO,
      patron: fila.patron,
    }));

  const presentes = new Set(deHoy.map((fila) => fila.jugador));
  const faltan = (carga?.jugadores ?? [])
    .filter((jugador) => !presentes.has(jugador))
    .map((jugador) => ({ jugador, nombre: nombres.get(jugador) ?? jugador }))
    .sort((a, b) => a.nombre.localeCompare(b.nombre));

  const media = redondear(jugaron.reduce((suma, j) => suma + j.intentos, 0) / jugaron.length);
  const mediaTemporada = typeof carga?.media_grupo === 'number' ? carga.media_grupo : null;
  const diferencia = mediaTemporada === null ? null : redondear(media - mediaTemporada);

  // Los dos filtros son independientes y hacen falta los dos: el fin de semana no cuenta por regla, y la
  // muestra absorbe los laborables en que el grupo tampoco jugó. Sin umbral publicado no se afirma ninguno.
  let cuenta = null;
  let motivo = null;
  if (!laborable) {
    cuenta = false;
    motivo = 'fin de semana';
  } else if (minimo !== null) {
    cuenta = jugaron.length >= minimo;
    motivo = cuenta ? null : 'muestra';
  }

  return {
    existe: true,
    jornada,
    fecha,
    laborable,
    minimo,
    cuenta,
    motivo,
    faltan_para_contar: minimo === null ? null : Math.max(0, minimo - jugaron.length),
    jugaron,
    faltan,
    cuantos_faltan: faltan.length,
    media,
    mejor: Math.min(...jugaron.map((j) => j.intentos)),
    peor: Math.max(...jugaron.map((j) => j.intentos)),
    media_temporada: mediaTemporada,
    diferencia,
    veredicto: diferencia === null || diferencia === 0 ? 'igual' : diferencia > 0 ? 'más dura' : 'más fácil',
    temporada: carga?.temporada ?? null,
    etiqueta: carga?.etiqueta ?? null,
  };
}
