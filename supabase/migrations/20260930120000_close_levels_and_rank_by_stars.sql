-- SuperWordleBros: un nivel se cierra al congelarse el siguiente, y las estrellas pesan más que el tiempo.
--
-- Slices: ranking-del-juego (un-nivel-se-cierra-al-congelar-el-siguiente, solo-se-sobrescribe-si-mejora) ·
-- clasificacion-del-juego.
--
-- Reemplaza `registrar_tiempo` con la misma firma y los mismos permisos: todo igual que en
-- 20260925140000_create_game_levels.sql, más dos cambios. La jornada tiene que ser la última congelada. Y una
-- marca mejora con **más estrellas, o con las mismas en menos tiempo** (decisión del dueño): antes mejoraba
-- solo con menos tiempo, y 9 estrellas rápidas pisaban 13 lentas.

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
  sus_estrellas integer;
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

  -- **Un nivel se cierra al congelarse el siguiente.** Solo admite marcas el último congelado: así su ranking
  -- deja de cambiar, y la clasificación del mes del juego no se reescribe hacia atrás. El del viernes sigue
  -- siendo el último todo el fin de semana, porque un fin de semana no crea nivel.
  if p_jornada <> (select max(l.jornada) from public.game_levels l) then
    raise exception 'ese nivel ya está cerrado' using errcode = '22023';
  end if;

  if p_estrellas < 0 or p_estrellas > coleccionables then
    raise exception 'estrellas imposibles' using errcode = '22023';
  end if;

  minimo := tramos * casillas_por_tramo * pixeles_por_casilla / velocidad_maxima;
  if p_segundos < minimo or p_segundos >= 3600 then
    raise exception 'tiempo imposible' using errcode = '22023';
  end if;

  -- **Solo si mejora**: más estrellas, o las mismas en menos tiempo. Lo demás no pisa la marca: el `where` del
  -- `do update` lo descarta y `found` queda en falso.
  insert into public.game_times as actual (jornada, jugador, segundos, estrellas)
  values (p_jornada, p_jugador, round(p_segundos, 2), p_estrellas)
  on conflict (jornada, jugador) do update
     set segundos = excluded.segundos, estrellas = excluded.estrellas, updated_at = now()
   where excluded.estrellas > actual.estrellas
      or (excluded.estrellas = actual.estrellas and excluded.segundos < actual.segundos);
  mejora := found;

  select t.segundos, t.estrellas into marca, sus_estrellas
    from public.game_times t where t.jornada = p_jornada and t.jugador = p_jugador;
  return jsonb_build_object('mejora', mejora, 'segundos', marca, 'estrellas', sus_estrellas);
end;
$$;

revoke all on function public.registrar_tiempo(integer, text, numeric, integer) from public, anon, authenticated;
grant execute on function public.registrar_tiempo(integer, text, numeric, integer) to anon, authenticated;
