/**
 * El nivel del juego: las cuadrículas de una jornada convertidas en escenario.
 *
 * Slice: `juego-de-la-jornada` (openspec/slices/dashboard/juego-de-la-jornada.md).
 *
 * El juego lo desarrolla Joel; esto solo le prepara el terreno. La forma del nivel **no se inventó aquí**:
 * se dedujo de sus dos prototipos y se verificó contra la tabla reconstruyendo el `pattern` desde los
 * bloques, que salió idéntico en los seis jugadores comprobados.
 *
 * **Esto vive en la web y no en el pipeline porque es un render, no una regla.** No clasifica ni decide nada
 * que la tabla no diga ya: dibuja una cuadrícula que existe. Reimplementar en JavaScript un clasificador sí
 * sería una segunda verdad; repintar un dato no lo es.
 *
 * **Función pura** (§10): entran los resultados, sale la estructura. Sin reloj, sin azar y sin red — que es
 * lo que permite que la misma jornada dé siempre el mismo nivel, y lo que hace comprobable el escenario.
 */

/** Cada jugador ocupa ocho columnas: cinco de cuadrícula y tres de respiro para poder saltar entre tramos. */
export const COLUMNAS_POR_JUGADOR = 8;

/** La cola del nivel, donde va la meta. */
export const COLUMNAS_DE_META = 5;

/** Dentro del tramo, la cuadrícula empieza en la cuarta columna. */
export const PRIMERA_COLUMNA_DE_REJILLA = 3;

/** Cuántas filas por encima de la cuadrícula va la etiqueta con el nombre. */
export const FILAS_HASTA_LA_ETIQUETA = 2;

/** Aire por encima de la cuadrícula más alta, para que la cámara no la recorte. */
export const AIRE = 3;

const VERDE = 'green';
const AMARILLO = 'orange';
const SUELO = 'ground';

/** Cómo se lee cada celda del patrón guardado. Lo que no está aquí es hueco. */
const BLOQUE_DE_CELDA = { G: VERDE, Y: AMARILLO };

/** Un fallo se guarda como 7 y en el canal se escribe `X/6`. La etiqueta usa lo que el grupo reconoce. */
const FALLO = 7;

/**
 * La jornada que se juega: **la última fechada antes de hoy**. `hoy` es `AAAA-MM-DD`.
 *
 * La de hoy está abierta —quien no haya jugado todavía no tiene cuadrícula— así que un nivel construido con
 * ella cambiaría bajo los pies de quien lo está jugando.
 *
 * **Se decide por fecha y no por posición.** La primera versión cogía «la penúltima jornada de la tabla», y
 * eso falla cada mañana: hasta que juega el primero, la penúltima es la de **anteayer**. Medido en vivo a las
 * 00:18 del 25 de septiembre: la tabla acababa en la 1722, que era la de ayer, y la pestaña enseñaba la
 * 1721. Sin `hoy` no se puede saber qué está cerrado, así que se devuelve `null` en lugar de adivinar.
 */
export function jornadaDelNivel(resultados, hoy) {
  if (!hoy) return null;
  const cerradas = (resultados ?? [])
    .filter((fila) => Number.isInteger(fila?.jornada) && typeof fila.fecha === 'string' && fila.fecha < hoy)
    .map((fila) => fila.jornada);
  return cerradas.length ? Math.max(...cerradas) : null;
}

/**
 * Desde qué hora de Madrid se congela el nivel de la jornada de ayer. Medido en 60 días: 2 de 490 cuadrículas
 * llegaron a la tabla después de medianoche, la más tardía a las 02:57.
 */
export const HORA_DE_CONGELAR = '04:00';

/** El día anterior a `AAAA-MM-DD`. En UTC a propósito: así el cambio de hora no descuadra un día. */
function diaAnterior(fecha) {
  const [a, m, d] = fecha.split('-').map(Number);
  return new Date(Date.UTC(a, m - 1, d - 1)).toISOString().slice(0, 10);
}

/**
 * La jornada que el cron congela: la última **asentada**. `hoy` es `AAAA-MM-DD` y `hora` `HH:MM`, las dos de
 * Madrid, y entran por parámetro (§10).
 *
 * Desde las 04:00, la de ayer; antes, la de anteayer —que el cron ya habrá congelado, salvo que estuviera
 * caído—. La de hoy, nunca: sigue abierta.
 */
export function jornadaACongelar(resultados, hoy, hora) {
  if (!hoy || !hora) return null;
  return jornadaDelNivel(resultados, hora >= HORA_DE_CONGELAR ? hoy : diaAnterior(hoy));
}

/** La fecha de una jornada, `AAAA-MM-DD`, o `null` si no hay filas suyas. */
export function fechaDe(resultados, jornada) {
  return (resultados ?? []).find((fila) => fila?.jornada === jornada)?.fecha ?? null;
}

const MESES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
];

/** Días entre dos fechas `AAAA-MM-DD`. En UTC a propósito: así el cambio de hora no descuadra un día. */
function diasEntre(desde, hasta) {
  const utc = (f) => { const [a, m, d] = f.split('-').map(Number); return Date.UTC(a, m - 1, d); };
  return Math.round((utc(hasta) - utc(desde)) / 86400000);
}

/**
 * Cómo se nombra la jornada en la cabecera: `jornada de ayer · 24 de septiembre` cuando lo fue, y
 * `jornada del 22 de septiembre` cuando no — un lunes, o un día que nadie jugó, «ayer» sería mentira.
 */
export function cuandoFue(fecha, hoy) {
  if (!fecha) return '';
  const [, mes, dia] = fecha.split('-').map(Number);
  const cuando = `${dia} de ${MESES[mes - 1]}`;
  return hoy && diasEntre(fecha, hoy) === 1 ? `jornada de ayer · ${cuando}` : `jornada del ${cuando}`;
}

/**
 * Los jugadores de esa jornada que tienen algo que dibujar, en orden estable.
 *
 * **Las filas llegan normalizadas** (`data/results.js::normalizar`): `jornada`, `nombre`, `intentos`,
 * `patron`. La primera versión leía los nombres crudos de la tabla —`wordle_id`, `player_name`— y con datos
 * reales todo le llegaba `undefined`, así que la pestaña decía que no había jornada que jugar. Los tests no
 * lo vieron porque sus fixtures tenían la forma de la tabla, no la de la web: lo destapó abrir la página.
 */
function tramosDe(resultados, jornada) {
  return (resultados ?? [])
    .filter((fila) => fila?.jornada === jornada && typeof fila.patron === 'string' && fila.patron)
    // **Por nombre y no por el orden que llegue.** Las filas vienen de una consulta, y un orden que dependa
    // de la base de datos haría que el mismo día diera niveles distintos.
    .sort((a, b) => String(a.nombre ?? '').localeCompare(String(b.nombre ?? ''), 'es'));
}

/** Cómo se escribe la nota en la etiqueta. */
function nota(score) {
  return score >= FALLO ? 'X' : String(score);
}

/**
 * El nivel de una jornada, o `null` si esa jornada no tiene a nadie con cuadrícula.
 *
 * Devolver `null` en lugar de un nivel vacío es deliberado: un escenario sin tramos es un pasillo de suelo
 * sin nada que hacer, y la vista puede decir que no hay partida en lugar de aparentar que sí.
 */
export function nivelDe(resultados, jornada) {
  const tramos = tramosDe(resultados, jornada);
  if (!tramos.length) return null;

  const widthTiles = tramos.length * COLUMNAS_POR_JUGADOR + COLUMNAS_DE_META;
  const blocks = [];
  const labels = [];
  const collectibles = [];
  let masAlto = 0;

  // **El suelo primero y entero.** Un hueco en el suelo es una caída que se pierde sin haber fallado, así
  // que cubre hasta la última columna y no solo hasta el último tramo.
  for (let col = 0; col < widthTiles; col += 1) {
    blocks.push({ col, row: 0, type: SUELO });
  }

  tramos.forEach((fila, indice) => {
    const base = indice * COLUMNAS_POR_JUGADOR;
    const intentos = String(fila.patron).split('/');
    masAlto = Math.max(masAlto, intentos.length);

    const delTramo = [];
    intentos.forEach((intento, orden) => {
      // **De abajo arriba.** La fila 1 es el último intento —el que resolvió— así que el escenario se lee
      // como se leyó la partida: cuanto más arriba, más lejos estaba de acertar.
      const row = intentos.length - orden;
      [...intento].forEach((celda, columna) => {
        const type = BLOQUE_DE_CELDA[celda];
        if (type) {
          delTramo.push({ col: base + PRIMERA_COLUMNA_DE_REJILLA + columna, row, type });
        }
      });
    });
    blocks.push(...delTramo);

    labels.push({
      col: base + PRIMERA_COLUMNA_DE_REJILLA,
      row: intentos.length + FILAS_HASTA_LA_ETIQUETA,
      text: `${fila.nombre}  ${nota(fila.intentos)}/6`,
    });

    // **El coleccionable se apoya, no flota.** Va sobre la plataforma más alta del tramo —la más a la
    // izquierda si empatan—, así que premia subir y siempre tiene suelo debajo. El prototipo lo colocaba al
    // azar, y aquí la misma jornada tiene que dar siempre el mismo nivel.
    if (delTramo.length) {
      const cima = Math.max(...delTramo.map((b) => b.row));
      const columna = Math.min(...delTramo.filter((b) => b.row === cima).map((b) => b.col));
      collectibles.push({ col: columna, row: cima + 1 });
    }
  });

  return {
    widthTiles,
    heightTiles: masAlto + AIRE,
    blocks,
    labels,
    collectibles,
    finish: { col: widthTiles - 3, row: 1 },
  };
}

/**
 * La puntuación para el canal. **La pega quien jugó**, como se pega el resultado del Wordle.
 *
 * La web no puede publicar en nombre de nadie —el token del bot vive solo en el workflow, y una vía de
 * escritura al canal desde la web pública es justo lo que no se quiere tener— y además no conviene: un
 * mensaje pegado por su dueño lleva autor de verdad, que es lo que un ranking necesita.
 *
 * La cabecera es **estable y legible**, con su lector al lado (`leerPuntuacion`), por si algún día el
 * ranking se saca del canal igual que hoy se sacan los resultados. Formato y lector viven juntos a propósito:
 * separados, uno cambia y el otro no se entera.
 */
export const CABECERA = 'Super Wordle Bros.';

/** Lo que reconoce una puntuación del juego dentro de un mensaje. */
export const ES_PUNTUACION = /Super Wordle Bros\.?\s*#(\d+)\s*⏱\s*(\d+):(\d{2})\s*⭐\s*(\d+)\/(\d+)/u;

/** Casilla de estrella conseguida y de estrella que faltó. Los cuadrados que el canal ya reconoce. */
const CONSEGUIDA = '🟨';
const PERDIDA = '⬛';

/** El tiempo como se lee en un cronómetro: `1:23`, `0:05`, `10:00`. */
export function tiempo(segundos) {
  const total = Math.max(0, Math.floor(Number(segundos) || 0));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
}

/**
 * El texto de una partida terminada. Función pura: la misma partida da siempre el mismo texto.
 *
 * Las estrellas se acotan al total: un contador que se pase —un coleccionable contado dos veces en el
 * motor— no puede escribir en el canal un `11/10`.
 */
export function textoParaCompartir({ jornada, segundos, estrellas, total }) {
  const de = Math.max(0, Math.floor(Number(total) || 0));
  const conseguidas = Math.min(de, Math.max(0, Math.floor(Number(estrellas) || 0)));
  const barra = CONSEGUIDA.repeat(conseguidas) + PERDIDA.repeat(de - conseguidas);
  return `${CABECERA} #${jornada} ⏱ ${tiempo(segundos)} ⭐ ${conseguidas}/${de}\n${barra}`;
}

/** Lo contrario: la partida de un texto compartido, o `null` si el texto no es una puntuación del juego. */
export function leerPuntuacion(texto) {
  const encontrado = ES_PUNTUACION.exec(String(texto ?? ''));
  if (!encontrado) return null;
  const [, jornada, minutos, segundos, estrellas, total] = encontrado.map(Number);
  return { jornada, segundos: minutos * 60 + segundos, estrellas, total };
}

/**
 * Los jugadores del grupo, para el «¿Quién eres?» del ranking: cada uno una vez, por nombre.
 *
 * **Todos los que han jugado alguna vez**, no solo los de la jornada del nivel: al juego puede jugar quien ese
 * día no hizo el Wordle. El nombre es el de su fila más reciente, que es como le conoce hoy el grupo.
 */
export function jugadoresDelGrupo(resultados) {
  const ultimo = new Map();
  for (const fila of resultados ?? []) {
    if (!fila?.jugador) continue;
    const previa = ultimo.get(fila.jugador);
    if (!previa || fila.jornada > previa.jornada) ultimo.set(fila.jugador, fila);
  }
  return [...ultimo.values()]
    .map((fila) => ({ jugador: fila.jugador, nombre: String(fila.nombre ?? fila.jugador) }))
    .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));
}

/** El tiempo del ranking, con centésimas: `0:42.37`. En un nivel corto se gana por décimas. */
export function tiempoPreciso(segundos) {
  const centesimas = Math.max(0, Math.round((Number(segundos) || 0) * 100));
  const minutos = Math.floor(centesimas / 6000);
  const resto = (centesimas % 6000) / 100;
  return `${minutos}:${resto.toFixed(2).padStart(5, '0')}`;
}

/**
 * El ranking de un nivel: de menor a mayor tiempo, y **dos tiempos iguales comparten puesto** (1, 1, 3), como
 * en el resto de clasificaciones de la web. Una marca de alguien que ya no está en la lista sale con su
 * identificador en lugar de desaparecer.
 */
export function clasificacionDelNivel(marcas, jugadores) {
  const nombres = new Map((jugadores ?? []).map((j) => [j.jugador, j.nombre]));
  const filas = (marcas ?? [])
    .map((m) => ({
      jugador: m.jugador,
      nombre: nombres.get(m.jugador) ?? String(m.jugador),
      segundos: Number(m.segundos),
      estrellas: Number(m.estrellas),
    }))
    .sort((a, b) => a.segundos - b.segundos || a.nombre.localeCompare(b.nombre, 'es'));
  return filas.map((fila, indice) => {
    let puesto = indice + 1;
    while (puesto > 1 && filas[puesto - 2].segundos === fila.segundos) puesto -= 1;
    return { puesto, ...fila };
  });
}
