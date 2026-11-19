-- El admin pasa a ser un dashboard sin PIN: el evento empieza y termina a su hora, el tablero se ve sin contraseña, los
-- diez primeros suman puntos F1 a su grupo, y las palabras se cambian hasta que empieza.
--
-- Slice: admin-del-evento (openspec/slices/dashboard/). Cambio: feat-admin-dashboard.
--
-- Decisiones del dueño, el día antes del evento:
--   · **Sin contraseña** para ver el panel, echar a alguien o cambiar las palabras. Se le avisó de que, sin ella,
--     cualquiera con el enlace ve las soluciones antes de empezar; lo aceptó. Durante el juego el tablero no las da.
--   · **Horario fijo**: `empieza_en` y `terminado_en` se cargan de antemano y el evento empieza y termina solo. Antes de
--     su hora no está en juego aunque `empieza_en` esté puesto (hasta ahora bastaba con que no fuera nulo).
--   · **F1 por grupos**, además de la media de la lista: los diez primeros de la clasificación individual (con puntos)
--     suman 25, 18, 15, 12, 10, 8, 6, 4, 2 y 1 a su grupo; los empatados se reparten los puntos de los puestos que
--     ocupan.
--   · Las palabras se ven y se cambian **hasta que empieza**; después, ya no.
--
-- Las funciones con PIN (`panel_del_evento`, `empezar_evento`, `terminar_evento`, `liberar_nombre`) se quedan: sirven
-- para operar a mano. La web ya no las usa.
--
-- **Aditiva** (ADR 0005): funciones nuevas y reemplazadas; ninguna tabla cambia.

-- En juego: llegada su hora y sin terminar.
create or replace function public.evento_en_juego(e public.event_editions) returns boolean
language sql
stable
set search_path = ''
as $$
  select e.empieza_en is not null and now() >= e.empieza_en and (e.terminado_en is null or now() < e.terminado_en);
$$;

-- Antes de su hora, lo público sigue sin decir nada más que eso.
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
  if e.empieza_en is null or now() < e.empieza_en then
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
    'puntos_por_acierto', e.puntos_por_acierto,
    'puntos_por_rapidez', e.puntos_por_rapidez,
    'soluciones', case when terminado then coalesce((
      select jsonb_agg(jsonb_build_object('orden', t.orden, 'palabra', t.palabra) order by t.orden)
        from public.event_targets t where t.evento = p_evento), '[]'::jsonb) end
  );
end;
$$;

-- Los puntos F1 de cada participante: los diez primeros con puntos se llevan 25, 18, 15, 12, 10, 8, 6, 4, 2 y 1; los
-- empatados, la media de los puntos de los puestos que ocupan juntos (dos primeros: (25 + 18) / 2 = 21,5).
create function public.evento_f1(p_evento text)
returns table (jugador bigint, nombre text, grupo text, puntos numeric, puesto bigint, f1 numeric)
language sql
stable
set search_path = ''
as $$
  with x as (select * from public.evento_puntos(p_evento)),
  puestos as (
    select x.jugador, rank() over (order by x.puntos desc) as desde, count(*) over (partition by x.puntos) as empatados
      from x where x.puntos > 0
  ),
  f as (
    select puestos.jugador,
           round((select avg(coalesce(('{25,18,15,12,10,8,6,4,2,1}'::integer[])[i], 0))
                    from generate_series(puestos.desde::integer, (puestos.desde + puestos.empatados - 1)::integer) i), 2)
             as f1
      from puestos
  )
  select x.jugador, x.nombre, x.grupo, x.puntos, rank() over (order by x.puntos desc), coalesce(f.f1, 0)
    from x left join f on f.jugador = x.jugador;
$$;

revoke all on function public.evento_f1(text) from public, anon, authenticated;

-- El tablero del evento, **sin PIN**: lo mismo que el panel, más los puntos F1 de cada participante y de cada grupo.
-- Las palabras, solo antes de empezar (para revisarlas y cambiarlas) y al terminar; durante el juego, nunca.
create function public.tablero_del_evento(p_evento text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions;
  antes boolean;
  terminado boolean;
begin
  select * into e from public.event_editions where id = p_evento;
  if not found then
    raise exception 'evento desconocido' using errcode = '22023';
  end if;
  antes := e.empieza_en is null or now() < e.empieza_en;
  terminado := public.evento_terminado(e);

  return jsonb_build_object(
    'ahora', now(),
    'titulo', e.titulo,
    'antes', antes,
    'activo', public.evento_en_juego(e),
    'terminado', terminado,
    'empieza_en', e.empieza_en,
    'terminado_en', e.terminado_en,
    'segundos_por_intento', e.segundos_por_intento,
    'puntos_por_acierto', e.puntos_por_acierto,
    'puntos_por_rapidez', e.puntos_por_rapidez,
    'participantes', (select count(*) from public.event_roster where evento = p_evento),
    'elegidos', (select count(*) from public.event_roster where evento = p_evento and token is not null),
    'palabras', coalesce((
      select jsonb_agg(jsonb_build_object(
               'orden', t.orden,
               'jugando', (select count(*) from public.event_rounds r join public.event_roster p on p.id = r.jugador
                            where p.evento = p_evento and r.orden = t.orden and r.terminada_en is null),
               'resueltas', (select count(*) from public.event_rounds r join public.event_roster p on p.id = r.jugador
                              where p.evento = p_evento and r.orden = t.orden and r.resuelta),
               'falladas', (select count(*) from public.event_rounds r join public.event_roster p on p.id = r.jugador
                             where p.evento = p_evento and r.orden = t.orden and r.terminada_en is not null
                               and not r.resuelta))
             || case when antes or terminado then jsonb_build_object('palabra', t.palabra) else '{}'::jsonb end
             order by t.orden)
        from public.event_targets t where t.evento = p_evento), '[]'::jsonb),
    'jugadores', coalesce((
      select jsonb_agg(jsonb_build_object('puesto', j.puesto, 'nombre', j.nombre, 'grupo', j.grupo, 'puntos', j.puntos,
                                          'f1', j.f1, 'palabras', j.palabras, 'elegido', j.elegido,
                                          'empezadas', j.empezadas, 'terminadas', j.terminadas,
                                          'resueltas', j.resueltas, 'tiempo_ms', j.tiempo_ms,
                                          'jugando_desde', j.jugando_desde) order by j.puesto, j.nombre)
        from (select f.puesto, f.nombre, f.grupo, f.puntos, f.f1, x.palabras,
                     (select p.token is not null from public.event_roster p where p.id = f.jugador) as elegido,
                     (select count(*) from public.event_rounds r where r.jugador = f.jugador) as empezadas,
                     (select count(*) from public.event_rounds r where r.jugador = f.jugador
                         and r.terminada_en is not null) as terminadas,
                     (select count(*) from public.event_rounds r where r.jugador = f.jugador and r.resuelta) as resueltas,
                     (select coalesce(sum(floor(extract(epoch from r.terminada_en - r.empezada_en) * 1000)), 0)::bigint
                        from public.event_rounds r where r.jugador = f.jugador and r.terminada_en is not null)
                       as tiempo_ms,
                     (select min(r.empezada_en) from public.event_rounds r where r.jugador = f.jugador
                         and r.terminada_en is null) as jugando_desde
                from public.evento_f1(p_evento) f
                join public.evento_puntos(p_evento) x on x.jugador = f.jugador) j
    ), '[]'::jsonb),
    'grupos', coalesce((
      select jsonb_agg(jsonb_build_object('puesto', puesto, 'grupo', grupo, 'miembros', miembros, 'jugaron', jugaron,
                                          'puntos_totales', total, 'puntos', media) order by puesto, grupo)
        -- El puesto, con la media sin redondear: dos medias distintas no empatan por el redondeo.
        from (select g.*, rank() over (order by g.media_exacta desc) as puesto
                from (select x.grupo, count(*) as miembros,
                             count(*) filter (where jsonb_array_length(x.palabras) > 0) as jugaron,
                             round(sum(x.puntos), 2) as total,
                             sum(x.puntos)::numeric / count(*) as media_exacta,
                             round(sum(x.puntos)::numeric / count(*), 2) as media
                        from public.evento_puntos(p_evento) x group by x.grupo) g) gr
    ), '[]'::jsonb),
    'grupos_f1', coalesce((
      select jsonb_agg(jsonb_build_object('puesto', puesto, 'grupo', grupo, 'puntos', total, 'personas', personas)
                       order by puesto, grupo)
        from (select g.*, rank() over (order by g.total desc) as puesto
                from (select f.grupo, sum(f.f1) as total,
                             coalesce(jsonb_agg(jsonb_build_object('nombre', f.nombre, 'puesto', f.puesto,
                                                                   'puntos', f.f1) order by f.f1 desc, f.nombre)
                                        filter (where f.f1 > 0), '[]'::jsonb) as personas
                        from public.evento_f1(p_evento) f group by f.grupo) g) gf
    ), '[]'::jsonb)
  );
end;
$$;

-- Echa a un participante, **sin PIN**: su nombre queda libre y se borra lo que jugó. Con el evento terminado, no.
create function public.echar_participante(p_evento text, p_nombre text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.event_roster;
begin
  if exists (select 1 from public.event_editions e where e.id = p_evento and public.evento_terminado(e)) then
    raise exception 'El evento ha terminado: ya no se echa a nadie.' using errcode = '22023';
  end if;
  select * into p from public.event_roster
   where evento = p_evento and clave = public.evento_normaliza(btrim(coalesce(p_nombre, '')));
  if not found then
    raise exception 'Ese nombre no está en la lista.' using errcode = '22023';
  end if;
  delete from public.event_rounds where jugador = p.id;
  update public.event_roster set token = null, elegido_en = null where id = p.id;
  return jsonb_build_object('nombre', p.nombre);
end;
$$;

-- Cambia una palabra, **sin PIN**, hasta que el evento empieza. Tiene que estar en el diccionario del juego (si no, se
-- podría encontrar probando sin gastar intentos) y no repetir otra del evento.
create function public.cambiar_palabra(p_evento text, p_orden integer, p_palabra text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions;
  palabra_ text := public.evento_normaliza(btrim(coalesce(p_palabra, '')));
begin
  select * into e from public.event_editions where id = p_evento;
  if not found then
    raise exception 'evento desconocido' using errcode = '22023';
  end if;
  if not (e.empieza_en is null or now() < e.empieza_en) then
    raise exception 'El evento ya ha empezado: las palabras ya no se cambian.' using errcode = '22023';
  end if;
  if palabra_ !~ '^[a-zñ]{5}$' then
    raise exception 'La palabra tiene que tener cinco letras.' using errcode = '22023';
  end if;
  if not exists (select 1 from public.event_words w where w.palabra = palabra_) then
    raise exception 'Esa palabra no está en el diccionario del juego.' using errcode = '22023';
  end if;
  if exists (select 1 from public.event_targets t where t.evento = p_evento and t.orden <> p_orden
                                                   and t.palabra = palabra_) then
    raise exception 'Esa palabra ya está en el evento.' using errcode = '22023';
  end if;
  update public.event_targets set palabra = palabra_ where evento = p_evento and orden = p_orden;
  if not found then
    raise exception 'Esa palabra no existe.' using errcode = '22023';
  end if;
  return jsonb_build_object('orden', p_orden, 'palabra', palabra_);
end;
$$;

revoke all on function public.tablero_del_evento(text), public.echar_participante(text, text),
  public.cambiar_palabra(text, integer, text)
  from public, anon, authenticated;
grant execute on function public.tablero_del_evento(text), public.echar_participante(text, text),
  public.cambiar_palabra(text, integer, text)
  to anon, authenticated;
