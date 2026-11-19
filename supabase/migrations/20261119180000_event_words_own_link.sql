-- Las palabras se revisan en su propio enlace: el dashboard ya no las enseña antes de empezar.
--
-- Slice: admin-del-evento (openspec/slices/dashboard/). Cambio: feat-palabras-en-su-enlace.
--
-- Decisión del dueño: él tiene el dashboard abierto y quiere jugar sin conocer las palabras, así que quien las revisa
-- (Nouha) lo hace en `/evento/palabras`. `tablero_del_evento` solo las da al terminar; `palabras_del_evento` las da
-- antes de empezar y nada más. Sin PIN, como el resto del dashboard (decisión del dueño): lo que las separa es el enlace.
--
-- **Aditiva** (ADR 0005): una función nueva y otra reemplazada; ninguna tabla cambia.

-- El tablero ya no da las palabras antes de empezar: solo al terminar.
create or replace function public.tablero_del_evento(p_evento text) returns jsonb
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
             || case when terminado then jsonb_build_object('palabra', t.palabra) else '{}'::jsonb end
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

-- Las palabras, para revisarlas y cambiarlas, solo antes de la hora de empezar.
create function public.palabras_del_evento(p_evento text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions;
begin
  select * into e from public.event_editions where id = p_evento;
  if not found then
    raise exception 'evento desconocido' using errcode = '22023';
  end if;
  if not (e.empieza_en is null or now() < e.empieza_en) then
    raise exception 'El evento ya ha empezado: las palabras ya no se ven aquí.' using errcode = '22023';
  end if;
  return jsonb_build_object(
    'ahora', now(),
    'titulo', e.titulo,
    'empieza_en', e.empieza_en,
    'palabras', coalesce((select jsonb_agg(jsonb_build_object('orden', t.orden, 'palabra', t.palabra) order by t.orden)
                            from public.event_targets t where t.evento = p_evento), '[]'::jsonb)
  );
end;
$$;

revoke all on function public.palabras_del_evento(text) from public, anon, authenticated;
grant execute on function public.palabras_del_evento(text) to anon, authenticated;
