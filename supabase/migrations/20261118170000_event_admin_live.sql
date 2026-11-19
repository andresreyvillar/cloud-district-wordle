-- El admin sigue el evento en directo: quién ha entrado, en qué palabra va, su tiempo y el ranking provisional.
--
-- Slice: admin-del-evento (openspec/slices/dashboard/). Cambio: feat-admin-en-directo.
--
-- `panel_del_evento` entrega ahora los puntos de participantes y grupos **también durante el evento** (decisión del
-- dueño): son provisionales, porque cuentan las palabras terminadas hasta ese momento. Cada participante trae además si
-- ha entrado (`elegido`), cuántas palabras ha empezado, terminado y resuelto, el tiempo de las terminadas y desde
-- cuándo juega la que tiene a medias. Las soluciones siguen saliendo solo con el evento terminado, y el móvil de los
-- participantes no ve nada de esto: la función pide el PIN.
--
-- **Aditiva** (ADR 0005): solo reemplaza una función; ninguna tabla cambia.

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
                             sum(x.puntos)::bigint as total,
                             sum(x.puntos)::numeric / count(*) as media_exacta,
                             round(sum(x.puntos)::numeric / count(*), 2) as media
                        from public.evento_puntos(p_evento) x group by x.grupo) g) gr
    ), '[]'::jsonb)
  );
end;
$$;
