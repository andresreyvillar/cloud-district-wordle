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
