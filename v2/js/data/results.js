/**
 * El borde de datos: lee `wordle_results` de Supabase.
 *
 * La clave que va aquí es la **publicable**, con RLS de solo lectura, igual que en la v1. Consecuencia que
 * conviene tener presente: cualquiera puede leer la tabla entera con ella. La protección es que no puede
 * escribir, no que los datos sean privados.
 *
 * Este módulo es el único sitio de la v2.0 que habla con la red, y el único que normaliza la forma de una
 * fila. Lo de dentro (`js/domain/`) recibe objetos ya normalizados y no sabe de dónde vienen.
 */

const SUPABASE_URL = 'https://oogturrjjcyrvzmiufff.supabase.co';
const SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_h92oql1czQVyp30m49uxFA_23airRWH';

/** PostgREST devuelve 1000 filas por página. Contar sobre una sola ya produjo una cifra falsa una vez. */
const PAGINA = 1000;

const COLUMNAS = 'slack_user_id,player_name,wordle_id,score,date,pattern';

/**
 * Una fila normalizada. Es el **único** punto de mapeo de la v2.0: si Supabase añade una columna o
 * devuelve un nulo inesperado, se nota aquí y no repartido por las vistas (ADR 0004, mitigación
 * declarada de no tener tipos).
 */
export function normalizar(fila) {
  return {
    jugador: fila.slack_user_id,
    nombre: fila.player_name ?? fila.slack_user_id,
    jornada: Number(fila.wordle_id),
    intentos: Number(fila.score),
    fecha: String(fila.date).slice(0, 10),
    // `mes` y no `temporada`: son cosas distintas desde que existe la temporada 0, y llamarlo
    // temporada invitaba a usarlo como tal. Quien necesite la temporada usa `data/temporada.js`.
    mes: String(fila.date).slice(0, 7),
    patron: fila.pattern ?? null,
  };
}

/**
 * Todos los resultados, paginando de forma explícita.
 *
 * Recibe el cliente por parámetro para poder sustituirlo en un test; `cargarResultados()` sin argumentos
 * crea el real.
 */
export async function leerTodo(cliente) {
  const filas = [];
  let desplazamiento = 0;

  for (;;) {
    const { data, error } = await cliente
      .from('wordle_results')
      .select(COLUMNAS)
      .order('wordle_id', { ascending: true })
      .range(desplazamiento, desplazamiento + PAGINA - 1);

    if (error) throw new Error(`Supabase: ${error.message}`);
    if (!data || data.length === 0) return filas;

    filas.push(...data.map(normalizar));
    if (data.length < PAGINA) return filas;
    desplazamiento += PAGINA;
  }
}

/** Crea el cliente real y lee. El import del SDK es dinámico para que este módulo se pueda importar en Node. */
export async function cargarResultados() {
  const { createClient } = await import(
    'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'
  );
  return leerTodo(createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY));
}


/** Las instantáneas de temporada, indexadas por temporada. Es de donde salen las reglas y el cálculo. */
export async function leerInstantaneas(cliente) {
  const { data, error } = await cliente
    .from('season_snapshots')
    .select('temporada,payload,updated_at')
    .order('temporada', { ascending: false });

  if (error) throw new Error(`Supabase: ${error.message}`);
  return new Map((data ?? []).map((fila) => [fila.temporada, { ...fila.payload, updated_at: fila.updated_at }]));
}

export async function cargarInstantaneas() {
  const { createClient } = await import(
    'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'
  );
  return leerInstantaneas(createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY));
}

/**
 * Las marcas del ranking de un nivel. Caben en una página: hay una por jugador y jornada, y el grupo no llega
 * ni de lejos a las 1000 filas de PostgREST.
 */
export async function leerMarcas(cliente, jornada) {
  const { data, error } = await cliente
    .from('game_times')
    .select('jugador,segundos,estrellas')
    .eq('jornada', jornada);

  if (error) throw new Error(`Supabase: ${error.message}`);
  return data ?? [];
}

/**
 * Registra una marca. **La única escritura de la web**, y no va a la tabla sino a la función
 * `registrar_tiempo`: es ella la que decide si la marca mejora la anterior o si es imposible. Con la clave
 * pública, la tabla solo se lee.
 */
export async function escribirMarca(cliente, { jornada, jugador, segundos, estrellas }) {
  const { data, error } = await cliente.rpc('registrar_tiempo', {
    p_jornada: jornada,
    p_jugador: jugador,
    p_segundos: segundos,
    p_estrellas: estrellas,
  });

  if (error) throw new Error(`Supabase: ${error.message}`);
  return { mejora: Boolean(data?.mejora), segundos: Number(data?.segundos) };
}

let clienteDelRanking = null;

/** El cliente real, creado una vez: el ranking lee y escribe varias veces por partida. */
async function cliente() {
  if (!clienteDelRanking) {
    const { createClient } = await import(
      'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'
    );
    clienteDelRanking = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);
  }
  return clienteDelRanking;
}

/** La API del ranking que usa la pestaña del juego. Los tests le pasan otra. */
export const RANKING_DEL_JUEGO = {
  leer: async (jornada) => leerMarcas(await cliente(), jornada),
  registrar: async (marca) => escribirMarca(await cliente(), marca),
};

/**
 * El último nivel congelado del juego, o `null` si todavía no hay ninguno. Lo congela el cron
 * (`tools/congelar_nivel.mjs`); la web **ya no lo calcula**, así que todos juegan el mismo escenario.
 */
export async function leerNivelCongelado(cliente) {
  const { data, error } = await cliente
    .from('game_levels')
    .select('jornada,fecha,nivel')
    .order('jornada', { ascending: false })
    .limit(1);

  if (error) throw new Error(`Supabase: ${error.message}`);
  const [fila] = data ?? [];
  return fila ? { jornada: Number(fila.jornada), fecha: String(fila.fecha).slice(0, 10), nivel: fila.nivel } : null;
}

/** La fuente de niveles que usa la pestaña del juego. Los tests le pasan otra. */
export const NIVEL_CONGELADO = {
  ultimo: async () => leerNivelCongelado(await cliente()),
};
