-- Los niveles de SuperWordleBros, congelados: uno por jornada, escrito una vez y nunca cambiado.
--
-- Slice: nivel-congelado (openspec/slices/dashboard/nivel-congelado.md).
--
-- **Aditiva** (ADR 0005). Lo escribe el cron (`tools/congelar_nivel.mjs`, clave de servicio); la clave
-- pública solo lo lee. Y `registrar_tiempo` pasa a medir contra el nivel congelado.

create table public.game_levels (
  jornada integer primary key,
  fecha date not null,
  nivel jsonb not null,
  frozen_at timestamptz not null default now(),
  -- Lo mínimo que `registrar_tiempo` lee del nivel. Se comprueba al congelar porque después ya no se puede
  -- corregir: un nivel mal formado dejaría esa jornada sin ranking para siempre.
  constraint nivel_con_forma check (
    -- `coalesce` porque sin la clave `jsonb_typeof` da NULL, y un check que da NULL pasa.
    coalesce(jsonb_typeof(nivel -> 'labels'), '') = 'array'
    and coalesce(jsonb_typeof(nivel -> 'collectibles'), '') = 'array'
  )
);

alter table public.game_levels enable row level security;

create policy "lectura publica" on public.game_levels for select using (true);

revoke insert, update, delete, truncate on public.game_levels from anon, authenticated;

-- **Congelado quiere decir congelado.** Un nivel con marcas en el ranking no se cambia sin querer: ni el cron
-- con un fallo ni la clave de servicio. Arreglar uno a mano exige quitar el trigger a propósito.
create function public.game_levels_inmutable() returns trigger
language plpgsql
set search_path = ''
as $$
begin
  raise exception 'un nivel congelado no se cambia' using errcode = '42501';
end;
$$;

revoke all on function public.game_levels_inmutable() from public, anon, authenticated;

create trigger no_se_cambia
  before update or delete on public.game_levels
  for each row execute function public.game_levels_inmutable();

create trigger no_se_vacia
  before truncate on public.game_levels
  for each statement execute function public.game_levels_inmutable();

-- El ranking se mide contra el nivel congelado: la jornada tiene que estarlo, el mínimo sale de sus tramos y
-- el máximo de estrellas de sus coleccionables. Misma firma y mismos permisos que la versión anterior.
create or replace function public.registrar_tiempo(
  p_jornada integer,
  p_jugador text,
  p_segundos numeric,
  p_estrellas integer
) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  -- Lo que el motor recorre como mucho, en px/s: `RUN_SPEED`, que es también la velocidad del impulso del
  -- pisotón. El margen es para que un cambio de física de Joel no rechace tiempos honrados.
  velocidad_maxima constant numeric := 300 * 1.5;
  casillas_por_tramo constant integer := 8;
  pixeles_por_casilla constant integer := 32;
  nivel jsonb;
  tramos integer;
  coleccionables integer;
  minimo numeric;
  mejora boolean;
  marca numeric;
begin
  if p_jornada is null or p_jugador is null or p_segundos is null or p_estrellas is null then
    raise exception 'faltan datos de la marca' using errcode = '22023';
  end if;

  if not exists (select 1 from public.wordle_results where slack_user_id = p_jugador) then
    raise exception 'jugador desconocido' using errcode = '22023';
  end if;

  -- Un tramo por etiqueta: `nivelDe` pone una por jugador con cuadrícula.
  select l.nivel into nivel from public.game_levels l where l.jornada = p_jornada;
  tramos := coalesce(jsonb_array_length(nivel -> 'labels'), 0);
  if tramos = 0 then
    raise exception 'esa jornada no tiene nivel' using errcode = '22023';
  end if;
  coleccionables := coalesce(jsonb_array_length(nivel -> 'collectibles'), 0);

  if p_estrellas < 0 or p_estrellas > coleccionables then
    raise exception 'estrellas imposibles' using errcode = '22023';
  end if;

  minimo := tramos * casillas_por_tramo * pixeles_por_casilla / velocidad_maxima;
  if p_segundos < minimo or p_segundos >= 3600 then
    raise exception 'tiempo imposible' using errcode = '22023';
  end if;

  -- **Solo si mejora.** Un tiempo igual o peor no pisa la marca: el `where` del `do update` lo descarta y
  -- `found` queda en falso.
  insert into public.game_times as actual (jornada, jugador, segundos, estrellas)
  values (p_jornada, p_jugador, round(p_segundos, 2), p_estrellas)
  on conflict (jornada, jugador) do update
     set segundos = excluded.segundos, estrellas = excluded.estrellas, updated_at = now()
   where excluded.segundos < actual.segundos;
  mejora := found;

  select segundos into marca from public.game_times where jornada = p_jornada and jugador = p_jugador;
  return jsonb_build_object('mejora', mejora, 'segundos', marca);
end;
$$;

revoke all on function public.registrar_tiempo(integer, text, numeric, integer) from public, anon, authenticated;
grant execute on function public.registrar_tiempo(integer, text, numeric, integer) to anon, authenticated;
