-- El ranking de SuperWordleBros: la mejor marca de cada jugador en cada nivel (= jornada).
--
-- Slice: ranking-del-juego (openspec/slices/dashboard/ranking-del-juego.md).
--
-- **Aditiva** (ADR 0005): no toca `wordle_results` ni `season_snapshots`, solo las lee.
--
-- La clave pública **no escribe en la tabla**: solo la lee y ejecuta `registrar_tiempo`, que es quien decide
-- qué entra. Así un intento peor no pisa una marca, y nadie puede borrar ni editar la de otro.

create table public.game_times (
  jornada integer not null,
  jugador text not null,
  segundos numeric(7, 2) not null check (segundos > 0 and segundos < 3600),
  estrellas integer not null check (estrellas >= 0),
  updated_at timestamptz not null default now(),
  primary key (jornada, jugador)
);

alter table public.game_times enable row level security;

create policy "lectura publica" on public.game_times for select using (true);

-- Supabase da por defecto todos los privilegios de las tablas nuevas a `anon` y `authenticated`. Sin política
-- de escritura la RLS ya lo bloquea; quitar el privilegio lo bloquea también si algún día alguien añade una.
revoke insert, update, delete, truncate on public.game_times from anon, authenticated;

create function public.registrar_tiempo(
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
  tramos integer;
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

  -- Los tramos del nivel son los jugadores de la jornada con cuadrícula (`nivelDe` en la web).
  select count(distinct slack_user_id) into tramos
    from public.wordle_results
   where wordle_id = p_jornada and pattern is not null and pattern <> '';
  if tramos = 0 then
    raise exception 'esa jornada no tiene nivel' using errcode = '22023';
  end if;

  if p_estrellas < 0 or p_estrellas > tramos then
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
