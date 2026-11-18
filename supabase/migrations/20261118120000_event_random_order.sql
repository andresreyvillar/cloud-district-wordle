-- Cada participante juega las palabras del evento en su propio orden, y el móvil dice cuánto suma cada intento.
--
-- Slices: palabras-del-evento (openspec/slices/dashboard/). Cambio: feat-evento-orden-aleatorio.
--
-- **El número que ve el participante no es el de la palabra.** La web numera las palabras de 1 a N; detrás de cada
-- número, el servidor pone una palabra del evento distinta según quién juegue, para que nadie pueda soplar «la primera
-- es…». Las rondas se siguen guardando con la palabra del evento (`event_rounds.orden` = `event_targets.orden`), así
-- que los puntos, los contadores del admin y liberar un nombre no cambian: comparan a quienes jugaron la misma palabra,
-- sea cual sea el número que les tocó. Lo único que traduce es lo que habla con el móvil.
--
-- El orden sale de un hash del participante y de cada palabra: fijo para cada uno (recargar o cambiar de móvil no lo
-- mueve), sin columnas nuevas, y válido aunque se carguen las palabras después de que alguien haya elegido nombre.
-- **Lleva dentro la huella del PIN**, que solo está en el servidor: el repositorio es público y los ids de la lista son
-- correlativos, así que sin un secreto quien adivinara los ids podría calcular el orden de los demás. Consecuencias
-- declaradas: cambiar el PIN o las palabras con el evento en marcha cambia el orden de todos; se hace antes de activar.
--
-- **Aditiva** (ADR 0005): solo funciones; ninguna tabla cambia.

-- Qué palabra del evento hay detrás de cada número del participante: el elemento k es el `orden` de su palabra k.
create function public.evento_orden_de(p_jugador bigint) returns integer[]
language sql
stable
set search_path = ''
as $$
  select coalesce(array_agg(t.orden order by md5(e.pin_hash || '/' || p.id::text || '/' || t.orden::text), t.orden), '{}')
    from public.event_roster p
    join public.event_editions e on e.id = p.evento
    join public.event_targets t on t.evento = p.evento
   where p.id = p_jugador;
$$;

-- Una palabra tal como la ve quien la juega. `p_orden` es la palabra del evento; lo que viaja es **el número del
-- participante**, nunca la palabra del evento que hay detrás.
create or replace function public.evento_ronda(p_jugador bigint, p_orden integer) returns jsonb
language sql
stable
set search_path = ''
as $$
  select jsonb_build_object(
    'orden', array_position(public.evento_orden_de(r.jugador), r.orden),
    'empezada_en', r.empezada_en,
    'terminada_en', r.terminada_en,
    'resuelta', r.resuelta,
    'tiempo_ms', case when r.terminada_en is null then null
                      else floor(extract(epoch from r.terminada_en - r.empezada_en) * 1000)::bigint end,
    'intentos', coalesce((select jsonb_agg(jsonb_build_object('palabra', t.palabra, 'colores', t.colores) order by t.n)
                            from public.event_tries t where t.jugador = r.jugador and t.orden = r.orden), '[]'::jsonb)
  )
  from public.event_rounds r
  where r.jugador = p_jugador and r.orden = p_orden;
$$;

-- Lo público: además, con el evento activado, cuántos segundos suma cada intento (la web lo dice al empezar).
create or replace function public.estado_del_juego(p_evento text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions;
  terminado boolean;
begin
  select * into e from public.event_editions where id = p_evento;
  if not found then
    raise exception 'evento desconocido' using errcode = '22023';
  end if;
  if e.empieza_en is null then
    return jsonb_build_object('ahora', now(), 'activo', false, 'terminado', false);
  end if;
  terminado := public.evento_terminado(e);
  return jsonb_build_object(
    'ahora', now(),
    'activo', not terminado,
    'terminado', terminado,
    'titulo', e.titulo,
    'total', (select count(*) from public.event_targets where evento = p_evento),
    'segundos_por_intento', e.segundos_por_intento,
    'soluciones', case when terminado then coalesce((
      select jsonb_agg(jsonb_build_object('orden', t.orden, 'palabra', t.palabra) order by t.orden)
        from public.event_targets t where t.evento = p_evento), '[]'::jsonb) end
  );
end;
$$;

-- Lo del participante, en su orden. Terminado el evento, también sus palabras en ese orden (`palabras`).
create or replace function public.mi_juego(p_evento text, p_token uuid) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.event_roster := public.evento_jugador(p_evento, p_token);
  e public.event_editions;
  suyo integer[] := public.evento_orden_de(p.id);
  datos jsonb;
begin
  datos := jsonb_build_object(
    'nombre', p.nombre,
    'rondas', coalesce((select jsonb_agg(public.evento_ronda(p.id, r.orden) order by array_position(suyo, r.orden))
                          from public.event_rounds r where r.jugador = p.id), '[]'::jsonb)
  );
  select * into e from public.event_editions where id = p_evento;
  if public.evento_terminado(e) then
    datos := datos || jsonb_build_object('palabras', coalesce((
      select jsonb_agg(t.palabra order by array_position(suyo, t.orden))
        from public.event_targets t where t.evento = p_evento), '[]'::jsonb));
  end if;
  return datos;
end;
$$;

-- Empieza la palabra que el participante ve con el número `p_orden`. Van una tras otra: la siguiente solo con la
-- anterior **de su orden** terminada.
create or replace function public.empezar_palabra(p_evento text, p_token uuid, p_orden integer) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.event_roster := public.evento_jugador(p_evento, p_token);
  e public.event_editions;
  suyo integer[] := public.evento_orden_de(p.id);
  orden_ integer := suyo[p_orden];
begin
  if orden_ is not null and exists (select 1 from public.event_rounds where jugador = p.id and orden = orden_) then
    return public.evento_ronda(p.id, orden_);
  end if;
  select * into e from public.event_editions where id = p_evento;
  if not public.evento_en_juego(e) then
    raise exception 'el evento no está activo' using errcode = '22023';
  end if;
  if orden_ is null then
    raise exception 'esa palabra no existe' using errcode = '22023';
  end if;
  if p_orden > 1 and not exists (select 1 from public.event_rounds
                                  where jugador = p.id and orden = suyo[p_orden - 1] and terminada_en is not null) then
    raise exception 'termina antes la palabra anterior' using errcode = '22023';
  end if;

  insert into public.event_rounds (jugador, orden, empezada_en) values (p.id, orden_, now())
  on conflict (jugador, orden) do nothing;
  return public.evento_ronda(p.id, orden_);
end;
$$;

-- Un intento en la palabra que el participante ve con el número `p_orden`. Con cinco verdes o con el sexto, termina.
-- `p_numero` lo hace idempotente, como antes.
create or replace function public.probar_palabra(p_evento text, p_token uuid, p_orden integer, p_palabra text,
                                                 p_numero integer)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.event_roster := public.evento_jugador(p_evento, p_token);
  orden_ integer := (public.evento_orden_de(p.id))[p_orden];
  e public.event_editions;
  r public.event_rounds;
  palabra_ text := public.evento_normaliza(coalesce(p_palabra, ''));
  colores_ text;
  n_ integer;
  resuelta_ boolean;
begin
  select * into r from public.event_rounds where jugador = p.id and orden = orden_ for update;
  if not found then
    raise exception 'esa palabra no está empezada' using errcode = '22023';
  end if;

  if p_numero between 1 and r.intentos then
    if exists (select 1 from public.event_tries t
                where t.jugador = p.id and t.orden = orden_ and t.n = p_numero and t.palabra = palabra_) then
      return public.evento_ronda(p.id, orden_);
    end if;
    raise exception 'ese intento ya está enviado' using errcode = '22023';
  end if;

  select * into e from public.event_editions where id = p_evento;
  if not public.evento_en_juego(e) then
    raise exception 'el evento ha terminado' using errcode = '22023';
  end if;
  if r.terminada_en is not null then
    raise exception 'esa palabra ya ha terminado' using errcode = '22023';
  end if;
  if p_numero is distinct from r.intentos + 1 then
    raise exception 'intento fuera de orden' using errcode = '22023';
  end if;
  if palabra_ !~ '^[a-zñ]{5}$' then
    raise exception 'la palabra tiene que tener cinco letras' using errcode = '22023';
  end if;
  -- Vale una palabra del diccionario o la solución de **esta** palabra. La de otra no: delataría una solución.
  if not exists (select 1 from public.event_words w where w.palabra = palabra_)
     and not exists (select 1 from public.event_targets t
                      where t.evento = p_evento and t.orden = orden_ and t.palabra = palabra_) then
    raise exception 'la palabra no está en la lista' using errcode = '22023';
  end if;

  select public.evento_wordle(t.palabra, palabra_) into colores_
    from public.event_targets t where t.evento = p_evento and t.orden = orden_;
  n_ := r.intentos + 1;
  resuelta_ := colores_ = 'GGGGG';

  insert into public.event_tries (jugador, orden, n, palabra, colores) values (p.id, orden_, n_, palabra_, colores_);
  update public.event_rounds
     set intentos = n_,
         resuelta = resuelta_,
         terminada_en = case when resuelta_ or n_ = 6 then now() end
   where jugador = p.id and orden = orden_;

  return public.evento_ronda(p.id, orden_);
end;
$$;

-- El ayudante nuevo no es público: diría qué palabra del evento hay detrás de cada número.
revoke all on function public.evento_orden_de(bigint) from public, anon, authenticated;
