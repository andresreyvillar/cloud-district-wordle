-- Un evento con contraseña no enseña nada a quien no la da: ni título, ni frases, ni horarios, ni contadores, ni
-- ranking.
--
-- Slices: frase-del-evento y pantalla-del-evento. La demo para la organización se publicó con contraseña de acceso,
-- pero `estado_del_evento` y `ranking_del_evento` eran públicos: cualquiera que abriera el enlace sabía de qué iba
-- el evento. Ahora los dos aceptan el token de un participante o la contraseña, y sin ninguno de los dos solo dicen
-- que hace falta contraseña. Un evento sin contraseña sigue igual.
--
-- La firma cambia. Sin `drop` (en producción se aplica sin confirmación destructiva): las versiones nuevas, con token
-- y contraseña **sin valores por defecto**, conviven con las de un solo parámetro, y estas pasan a llamar a las
-- nuevas sin token ni contraseña. Así ninguna de las dos queda abierta, y PostgREST no duda entre ellas: la web manda
-- siempre `p_token` y `p_clave` (aunque sean nulos), que solo encajan con la nueva.

-- Si quien pregunta puede ver el evento: no tiene contraseña, o trae la buena, o es un participante apuntado.
create function public.evento_visible_para(e public.event_editions, p_token uuid, p_clave text) returns boolean
language sql
stable
set search_path = ''
as $$
  select e.clave_hash is null
      or e.clave_hash = encode(sha256(convert_to(coalesce(p_clave, ''), 'UTF8')), 'hex')
      or exists (select 1 from public.event_players p where p.evento = e.id and p.token = p_token);
$$;

revoke all on function public.evento_visible_para(public.event_editions, uuid, text) from public, anon, authenticated;

-- Lo público del evento: la hora del servidor, cuándo sale cada frase, los contadores sin nombres y, terminado el
-- evento, las soluciones. Con contraseña, solo para quien la sabe o ya está dentro.
create function public.estado_del_evento(p_evento text, p_token uuid, p_clave text)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions;
  ahora timestamptz := now();
  terminado boolean;
begin
  select * into e from public.event_editions where id = p_evento;
  if not found then
    raise exception 'evento desconocido' using errcode = '22023';
  end if;
  if not public.evento_visible_para(e, p_token, p_clave) then
    return jsonb_build_object('ahora', ahora, 'con_clave', true, 'bloqueado', true);
  end if;
  terminado := e.terminado_en is not null and ahora >= e.terminado_en;

  return jsonb_build_object(
    'titulo', e.titulo,
    'ahora', ahora,
    'empieza_en', e.empieza_en,
    'terminado_en', e.terminado_en,
    'intervalo_minutos', e.intervalo_minutos,
    'participantes', (select count(*) from public.event_players where evento = p_evento),
    'terminado', terminado,
    -- Si para entrar hace falta contraseña (la web la pide); nunca la huella.
    'con_clave', e.clave_hash is not null,
    'bloqueado', false,
    'frases', coalesce((
      select jsonb_agg(
        jsonb_build_object(
          'orden', f.orden,
          'abre_en', e.empieza_en + make_interval(mins => e.intervalo_minutos * (f.orden - 1)),
          'estado', public.evento_ventana(e.empieza_en, e.terminado_en, e.intervalo_minutos, f.orden, ahora),
          'jugando', (select count(*) from public.event_plays pl join public.event_players p on p.id = pl.jugador
                       where p.evento = p_evento and pl.orden = f.orden and pl.terminada_en is null),
          'resueltas', (select count(*) from public.event_plays pl join public.event_players p on p.id = pl.jugador
                         where p.evento = p_evento and pl.orden = f.orden and pl.resuelta),
          'sin_resolver', (select count(*) from public.event_plays pl join public.event_players p on p.id = pl.jugador
                            where p.evento = p_evento and pl.orden = f.orden and pl.terminada_en is not null
                              and not pl.resuelta)
        )
        -- La solución, solo con el evento terminado.
        || case when terminado then jsonb_build_object('solucion', f.frase) else '{}'::jsonb end
        order by f.orden)
      from public.event_phrases f where f.evento = p_evento), '[]'::jsonb)
  );
end;
$$;

-- El ranking final: solo con el evento terminado y, con contraseña, solo para quien la sabe o ya está dentro.
-- Primero más frases resueltas; a igualdad, menos tiempo total, que suma las partidas terminadas (resueltas o
-- perdidas). Una partida a medias no cuenta; quien no terminó ninguna no sale.
create function public.ranking_del_evento(p_evento text, p_token uuid, p_clave text)
returns jsonb
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
  if not public.evento_visible_para(e, p_token, p_clave) then
    raise exception 'contraseña incorrecta' using errcode = '22023';
  end if;
  if e.terminado_en is null or now() < e.terminado_en then
    raise exception 'el ranking se publica al terminar el evento' using errcode = '22023';
  end if;

  return coalesce((
    with terminadas as (
      select p.id as jugador, p.nombre, pl.orden, pl.resuelta,
             floor(extract(epoch from pl.terminada_en - pl.empezada_en) * 1000)::bigint as tiempo_ms
        from public.event_players p
        join public.event_plays pl on pl.jugador = p.id
       where p.evento = p_evento and pl.terminada_en is not null
    ),
    totales as (
      select nombre,
             count(*) filter (where resuelta) as resueltas,
             sum(tiempo_ms)::bigint as tiempo_ms,
             jsonb_agg(jsonb_build_object('orden', orden, 'resuelta', resuelta, 'tiempo_ms', tiempo_ms)
                       order by orden) as frases
        from terminadas
       group by jugador, nombre
    )
    select jsonb_agg(jsonb_build_object('puesto', puesto, 'nombre', nombre, 'resueltas', resueltas,
                                        'tiempo_ms', tiempo_ms, 'frases', frases) order by puesto, nombre)
      from (select *, rank() over (order by resueltas desc, tiempo_ms asc) as puesto from totales) r
  ), '[]'::jsonb);
end;
$$;

-- Las de un solo parámetro, cerradas igual: son las nuevas sin token ni contraseña.
create or replace function public.estado_del_evento(p_evento text) returns jsonb
language sql
security definer
set search_path = ''
as $$
  select public.estado_del_evento(p_evento, null::uuid, null::text);
$$;

create or replace function public.ranking_del_evento(p_evento text) returns jsonb
language sql
security definer
set search_path = ''
as $$
  select public.ranking_del_evento(p_evento, null::uuid, null::text);
$$;

revoke all on function public.estado_del_evento(text, uuid, text), public.ranking_del_evento(text, uuid, text)
  from public, anon, authenticated;
grant execute on function public.estado_del_evento(text, uuid, text), public.ranking_del_evento(text, uuid, text)
  to anon, authenticated;
