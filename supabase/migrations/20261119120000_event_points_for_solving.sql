-- Los puntos del evento premian sobre todo acertar, y después la rapidez.
--
-- Slices: admin-del-evento y palabras-del-evento (openspec/slices/dashboard/). Cambio: feat-evento-puntos-por-acierto.
--
-- Antes, quien resolvía una palabra se llevaba 1 punto más uno por cada resolvedor más lento: el resolvedor más lento
-- sacaba 1, casi lo mismo que quien la fallaba, y la rapidez mandaba sobre acertar (en la simulación, quien acertaba
-- más palabras quedaba delante solo en el 78 % de los casos). Ahora (decisión del dueño, medida con eventos simulados):
--
--   puntos de una palabra resuelta = puntos_por_acierto (10) + puntos_por_rapidez (5) × (1 − M / (R − 1))
--
-- con R resolvedores de esa palabra y M de ellos con mejor marca (tiempo + segundos_por_intento por intento). El mejor
-- se lleva el extra entero, el peor nada, quien la resuelve solo el extra entero, y la misma marca da los mismos puntos:
-- empatar no quita extra. Fallada, a medias o sin jugar, 0. Se redondea a dos decimales. Quien acierta más palabras
-- queda delante en el 99 % de los casos.
--
-- **Aditiva** (ADR 0005): dos columnas nuevas con valor por defecto; `evento_puntos` cambia el tipo de sus puntos
-- (de enteros a decimales), así que se borra y se crea de nuevo, sin acceso público, como antes.

alter table public.event_editions
  -- Lo que vale acertar una palabra y el extra máximo por rapidez. Se recalibran aquí, sin desplegar.
  add column puntos_por_acierto integer not null default 10 check (puntos_por_acierto between 0 and 1000),
  add column puntos_por_rapidez integer not null default 5 check (puntos_por_rapidez between 0 and 1000);

drop function public.evento_puntos(text);

-- Los puntos de cada participante de la lista, con el detalle de cada palabra. Quien no jugó sale con cero.
create function public.evento_puntos(p_evento text)
returns table (jugador bigint, nombre text, grupo text, puntos numeric, palabras jsonb)
language sql
stable
set search_path = ''
as $$
  with e as (
    select segundos_por_intento, puntos_por_acierto, puntos_por_rapidez
      from public.event_editions where id = p_evento
  ),
  rondas as (
    select r.jugador, r.orden, r.resuelta, r.intentos,
           case when r.terminada_en is null then null
                else floor(extract(epoch from r.terminada_en - r.empezada_en) * 1000)::bigint end as tiempo_ms
      from public.event_rounds r
      join public.event_roster p on p.id = r.jugador
     where p.evento = p_evento
  ),
  marcas as (
    select rondas.*,
           case when rondas.resuelta
                then rondas.tiempo_ms + 1000::bigint * rondas.intentos * (select e.segundos_por_intento from e) end
             as marca_ms
      from rondas
  ),
  -- Entre los resolvedores de cada palabra: cuántos tienen mejor marca (M) y cuántos son (R).
  puestos as (
    select marcas.*,
           rank() over (partition by marcas.orden, marcas.resuelta order by marcas.marca_ms) - 1 as mejores,
           count(*) over (partition by marcas.orden, marcas.resuelta) as resolvedores
      from marcas
  ),
  puntuadas as (
    select puestos.*,
           case when puestos.resuelta then round(
                  (select e.puntos_por_acierto from e)
                  + (select e.puntos_por_rapidez from e)
                    * case when puestos.resolvedores <= 1 then 1
                           else 1 - puestos.mejores::numeric / (puestos.resolvedores - 1) end, 2)
                else 0 end as puntos
      from puestos
  )
  select p.id, p.nombre, p.grupo, coalesce(sum(u.puntos), 0)::numeric,
         coalesce(jsonb_agg(jsonb_build_object('orden', u.orden, 'resuelta', u.resuelta, 'intentos', u.intentos,
                                               'tiempo_ms', u.tiempo_ms, 'marca_ms', u.marca_ms, 'puntos', u.puntos)
                            order by u.orden) filter (where u.orden is not null), '[]'::jsonb)
    from public.event_roster p
    left join puntuadas u on u.jugador = p.id
   where p.evento = p_evento
   group by p.id, p.nombre, p.grupo;
$$;

revoke all on function public.evento_puntos(text) from public, anon, authenticated;

-- Lo público: con el evento activado, también lo que vale acertar y el extra por rapidez (la web lo dice al empezar).
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
    'puntos_por_acierto', e.puntos_por_acierto,
    'puntos_por_rapidez', e.puntos_por_rapidez,
    'soluciones', case when terminado then coalesce((
      select jsonb_agg(jsonb_build_object('orden', t.orden, 'palabra', t.palabra) order by t.orden)
        from public.event_targets t where t.evento = p_evento), '[]'::jsonb) end
  );
end;
$$;

-- El panel: los totales de grupo con decimales, y lo que vale acertar y la rapidez.
create or replace function public.panel_del_evento(p_evento text, p_pin text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  pin text := public.evento_pin(p_evento, p_pin);
  e public.event_editions;
  terminado boolean;
begin
  if pin <> 'ok' then
    return public.evento_pin_rechazado(pin);
  end if;
  select * into e from public.event_editions where id = p_evento;
  terminado := public.evento_terminado(e);

  return jsonb_build_object(
    'ahora', now(),
    'titulo', e.titulo,
    'activo', public.evento_en_juego(e),
    'terminado', terminado,
    'empieza_en', e.empieza_en,
    'terminado_en', e.terminado_en,
    'segundos_por_intento', e.segundos_por_intento,
    'puntos_por_acierto', e.puntos_por_acierto,
    'puntos_por_rapidez', e.puntos_por_rapidez,
    'participantes', (select count(*) from public.event_roster where evento = p_evento),
    'elegidos', (select count(*) from public.event_roster where evento = p_evento and token is not null),
    'nombres', coalesce((select jsonb_agg(jsonb_build_object('nombre', nombre, 'elegido', token is not null)
                                          order by clave)
                           from public.event_roster where evento = p_evento), '[]'::jsonb),
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
             || case when terminado then jsonb_build_object('palabra', t.palabra) else '{}'::jsonb end
             order by t.orden)
        from public.event_targets t where t.evento = p_evento), '[]'::jsonb)
  ) || jsonb_build_object(
    'jugadores', coalesce((
      select jsonb_agg(jsonb_build_object('puesto', puesto, 'nombre', nombre, 'grupo', grupo, 'puntos', puntos,
                                          'palabras', palabras, 'elegido', elegido, 'empezadas', empezadas,
                                          'terminadas', terminadas, 'resueltas', resueltas, 'tiempo_ms', tiempo_ms,
                                          'jugando_desde', jugando_desde) order by puesto, nombre)
        from (select x.*, rank() over (order by x.puntos desc) as puesto,
                     (select p.token is not null from public.event_roster p where p.id = x.jugador) as elegido,
                     (select count(*) from public.event_rounds r where r.jugador = x.jugador) as empezadas,
                     (select count(*) from public.event_rounds r where r.jugador = x.jugador
                         and r.terminada_en is not null) as terminadas,
                     (select count(*) from public.event_rounds r where r.jugador = x.jugador and r.resuelta) as resueltas,
                     (select coalesce(sum(floor(extract(epoch from r.terminada_en - r.empezada_en) * 1000)), 0)::bigint
                        from public.event_rounds r where r.jugador = x.jugador and r.terminada_en is not null)
                       as tiempo_ms,
                     (select min(r.empezada_en) from public.event_rounds r where r.jugador = x.jugador
                         and r.terminada_en is null) as jugando_desde
                from public.evento_puntos(p_evento) x) j
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
    ), '[]'::jsonb)
  );
end;
$$;
