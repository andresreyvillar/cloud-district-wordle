-- El juego del evento pasa de frases a palabras: el Wordle de siempre, cinco palabras seguidas, con una lista de
-- participantes cargada de antemano y repartida en grupos.
--
-- Slices: palabras-del-evento y admin-del-evento (openspec/slices/dashboard/).
--
-- Reglas (Wordle): palabras válidas de cinco letras, seis como mucho. Cada letra en su sitio sale verde; si está en la
-- palabra pero en otro sitio, amarilla; si no está (o ya no quedan más como ella), gris. Se gana con cinco verdes.
--
-- Puntos: en cada palabra, la marca es el tiempo más `segundos_por_intento` por cada intento (30 s); menos es mejor.
-- Quien la resuelve se lleva un punto más uno por cada resolvedor con peor marca (la misma marca, los mismos puntos);
-- quien falla o no la juega, cero. El grupo puntúa la **media** de su lista entera: quien no juega cuenta como cero.
--
-- **Aditiva** (ADR 0005): tablas nuevas y columnas nuevas, sin `drop`. Las funciones del juego de frases dejan de ser
-- públicas (se les quita el `execute`), pero sus tablas se quedan.
--
-- **La clave pública no lee ni escribe ninguna tabla del evento.** Todo pasa por funciones `SECURITY DEFINER`.
--
-- **Esta migración no trae ni palabras, ni participantes, ni PIN**: el repositorio es público. El evento se carga
-- por SQL:
--   insert into public.event_editions (id, titulo, pin_hash)
--     values ('<id>', '<título>', encode(sha256(convert_to('<PIN>', 'UTF8')), 'hex'));
--   insert into public.event_targets (evento, orden, palabra) values ('<id>', 1, '<palabra>'), …;
--   insert into public.event_roster (evento, nombre, grupo) values ('<id>', '<nombre>', '<grupo>'), …;
-- El PIN puede ser corto: cada cinco fallos seguidos lo bloquean, y cada bloqueo dura el doble (ver `evento_pin`).

alter table public.event_editions
  -- Lo que vale un intento en segundos, para la marca de cada palabra. Se recalibra aquí, sin desplegar.
  add column segundos_por_intento integer not null default 30 check (segundos_por_intento between 0 and 600),
  -- Fallos seguidos del PIN y hasta cuándo está bloqueado.
  add column pin_fallos integer not null default 0 check (pin_fallos >= 0),
  add column pin_bloqueado_hasta timestamptz;

-- Las palabras que hay que adivinar, en orden. Ya normalizadas: minúsculas, sin tildes, con ñ.
create table public.event_targets (
  evento text not null references public.event_editions (id) on delete cascade,
  orden integer not null check (orden >= 1),
  palabra text not null check (palabra ~ '^[a-zñ]{5}$'),
  primary key (evento, orden)
);

-- La lista de quienes pueden jugar, con su grupo. Cada nombre lo elige un solo móvil (su token).
create table public.event_roster (
  id bigint generated always as identity primary key,
  evento text not null references public.event_editions (id) on delete cascade,
  nombre text not null check (char_length(nombre) between 1 and 60 and nombre = btrim(nombre)
                              and nombre !~ '[[:cntrl:]]'),
  -- El nombre sin mayúsculas ni tildes: «ANA» y «Ána» son el mismo.
  clave text generated always as (public.evento_normaliza(nombre)) stored,
  grupo text not null check (char_length(grupo) between 1 and 40 and grupo !~ '[[:cntrl:]]'),
  token uuid,
  elegido_en timestamptz,
  unique (evento, clave),
  unique (evento, token)
);

-- Una palabra jugada por un participante: su cronómetro y su resultado.
create table public.event_rounds (
  jugador bigint not null references public.event_roster (id) on delete cascade,
  orden integer not null,
  empezada_en timestamptz not null,
  terminada_en timestamptz,
  resuelta boolean not null default false,
  intentos integer not null default 0 check (intentos between 0 and 6),
  primary key (jugador, orden)
);

create table public.event_tries (
  jugador bigint not null,
  orden integer not null,
  n integer not null check (n between 1 and 6),
  palabra text not null check (palabra ~ '^[a-zñ]{5}$'),
  -- G verde, Y amarilla, . gris.
  colores text not null check (colores ~ '^[GY.]{5}$'),
  primary key (jugador, orden, n),
  foreign key (jugador, orden) references public.event_rounds (jugador, orden) on delete cascade
);

alter table public.event_targets enable row level security;
alter table public.event_roster enable row level security;
alter table public.event_rounds enable row level security;
alter table public.event_tries enable row level security;

revoke all on public.event_targets, public.event_roster, public.event_rounds, public.event_tries
  from anon, authenticated;
revoke all on sequence public.event_roster_id_seq from anon, authenticated;

-- ── Ayudantes (sin acceso público) ────────────────────────────────────────────────────────────────────────

-- Los colores de una palabra contra la solución, como el Wordle: primero los verdes (letra en su sitio); después,
-- de izquierda a derecha, amarilla mientras queden letras así en la solución sin verde ni amarilla, y gris el resto.
-- `sacos` contra `casas` → `YGY.G`: la segunda s sale verde y la primera amarilla, y una letra repetida solo sale
-- amarilla tantas veces como quede en la solución.
create function public.evento_wordle(solucion text, palabra text) returns text
language plpgsql
immutable
set search_path = ''
as $$
declare
  s text[] := regexp_split_to_array(solucion, '');
  p text[] := regexp_split_to_array(palabra, '');
  colores text[] := array['.', '.', '.', '.', '.'];
  -- Las letras de la solución que no han salido verdes, para repartir amarillas.
  quedan text[] := array[]::text[];
  i integer;
  j integer;
begin
  for i in 1..5 loop
    if p[i] = s[i] then
      colores[i] := 'G';
    else
      quedan := quedan || s[i];
    end if;
  end loop;
  for i in 1..5 loop
    if colores[i] <> 'G' then
      j := array_position(quedan, p[i]);
      if j is not null then
        colores[i] := 'Y';
        quedan := quedan[1:j - 1] || quedan[j + 1:];
      end if;
    end if;
  end loop;
  return array_to_string(colores, '');
end;
$$;

-- El participante de un token, o error.
create function public.evento_jugador(p_evento text, p_token uuid) returns public.event_roster
language plpgsql
stable
set search_path = ''
as $$
declare
  p public.event_roster;
begin
  select * into p from public.event_roster where evento = p_evento and token = p_token;
  if not found or p_token is null then
    raise exception 'no has elegido nombre' using errcode = '22023';
  end if;
  return p;
end;
$$;

-- Una palabra tal como la ve quien la juega: sus intentos con colores, si terminó y en cuánto. Nunca la solución.
create function public.evento_ronda(p_jugador bigint, p_orden integer) returns jsonb
language sql
stable
set search_path = ''
as $$
  select jsonb_build_object(
    'orden', r.orden,
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

-- Si el evento está en juego: activado y sin terminar.
create function public.evento_en_juego(e public.event_editions) returns boolean
language sql
stable
set search_path = ''
as $$
  select e.empieza_en is not null and (e.terminado_en is null or now() < e.terminado_en);
$$;

create function public.evento_terminado(e public.event_editions) returns boolean
language sql
stable
set search_path = ''
as $$
  select e.terminado_en is not null and now() >= e.terminado_en;
$$;

-- Comprueba el PIN y lleva la cuenta de fallos: `ok`, `incorrecto` o `bloqueado`. Cada cinco fallos seguidos bloquean
-- el PIN, también para el bueno, y cada bloqueo dura el doble que el anterior: 1, 2, 4… minutos, hasta una hora. Con
-- 10.000 PIN de cuatro cifras, probarlos todos lleva meses. Quien sepa el id del evento puede tener al admin
-- bloqueado; el plan B es desbloquearlo por SQL (`pin_fallos = 0, pin_bloqueado_hasta = null`). Un acierto pone la
-- cuenta a cero. **No lanza error**: un error desharía la cuenta.
create function public.evento_pin(p_evento text, p_pin text) returns text
language plpgsql
set search_path = ''
as $$
declare
  e public.event_editions;
begin
  select * into e from public.event_editions where id = p_evento for update;
  if not found then
    return 'incorrecto';
  end if;
  if e.pin_bloqueado_hasta is not null and now() < e.pin_bloqueado_hasta then
    return 'bloqueado';
  end if;
  if e.pin_hash = encode(sha256(convert_to(coalesce(p_pin, ''), 'UTF8')), 'hex') then
    update public.event_editions set pin_fallos = 0, pin_bloqueado_hasta = null where id = p_evento;
    return 'ok';
  end if;
  update public.event_editions
     set pin_fallos = e.pin_fallos + 1,
         pin_bloqueado_hasta = case when (e.pin_fallos + 1) % 5 = 0
                                    then now() + make_interval(mins => least(60, 2 ^ ((e.pin_fallos + 1) / 5 - 1))::integer)
                               end
   where id = p_evento;
  return 'incorrecto';
end;
$$;

-- La respuesta de un PIN que no vale, para devolverla tal cual.
create function public.evento_pin_rechazado(resultado text) returns jsonb
language sql
immutable
set search_path = ''
as $$
  select jsonb_build_object('error', case when resultado = 'bloqueado'
                                          then 'Demasiados intentos: espera unos minutos.' else 'PIN incorrecto' end);
$$;

-- Los puntos de cada participante de la lista, con el detalle de cada palabra. Quien no jugó sale con cero.
create function public.evento_puntos(p_evento text)
returns table (jugador bigint, nombre text, grupo text, puntos bigint, palabras jsonb)
language sql
stable
set search_path = ''
as $$
  with rondas as (
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
                then rondas.tiempo_ms + 1000::bigint * rondas.intentos
                     * (select e.segundos_por_intento from public.event_editions e where e.id = p_evento) end as marca_ms
      from rondas
  ),
  -- Ordenadas de peor a mejor marca, el puesto es 1 más los que tienen peor marca: lo que puntúa.
  puntuadas as (
    select marcas.*,
           case when marcas.resuelta then rank() over (partition by marcas.orden, marcas.resuelta
                                                       order by marcas.marca_ms desc) else 0 end as puntos
      from marcas
  )
  select p.id, p.nombre, p.grupo, coalesce(sum(u.puntos), 0)::bigint,
         coalesce(jsonb_agg(jsonb_build_object('orden', u.orden, 'resuelta', u.resuelta, 'intentos', u.intentos,
                                               'tiempo_ms', u.tiempo_ms, 'marca_ms', u.marca_ms, 'puntos', u.puntos)
                            order by u.orden) filter (where u.orden is not null), '[]'::jsonb)
    from public.event_roster p
    left join puntuadas u on u.jugador = p.id
   where p.evento = p_evento
   group by p.id, p.nombre, p.grupo;
$$;

revoke all on function public.evento_wordle(text, text), public.evento_jugador(text, uuid),
  public.evento_ronda(bigint, integer), public.evento_en_juego(public.event_editions),
  public.evento_terminado(public.event_editions), public.evento_pin(text, text), public.evento_pin_rechazado(text),
  public.evento_puntos(text)
  from public, anon, authenticated;

-- ── Lo que llama el móvil ─────────────────────────────────────────────────────────────────────────────────

-- Lo público: la hora del servidor y si el evento está en juego. **Antes de activarlo, nada más**: ni título, ni
-- cuántas palabras hay. Terminado, las soluciones.
create function public.estado_del_juego(p_evento text) returns jsonb
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
    'soluciones', case when terminado then coalesce((
      select jsonb_agg(jsonb_build_object('orden', t.orden, 'palabra', t.palabra) order by t.orden)
        from public.event_targets t where t.evento = p_evento), '[]'::jsonb) end
  );
end;
$$;

-- Los nombres de la lista y si están libres, para elegir el propio. Solo con el evento en juego (ni antes ni después:
-- son nombres reales); nunca el grupo.
create function public.nombres_del_evento(p_evento text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions;
begin
  select * into e from public.event_editions where id = p_evento;
  if not found or not public.evento_en_juego(e) then
    raise exception 'el evento no está activo' using errcode = '22023';
  end if;
  return coalesce((select jsonb_agg(jsonb_build_object('nombre', nombre, 'libre', token is null) order by clave)
                     from public.event_roster where evento = p_evento), '[]'::jsonb);
end;
$$;

-- Un móvil elige su nombre de la lista. Un móvil que ya tiene nombre lo conserva; un nombre de otro móvil, no se da.
create function public.elegir_nombre(p_evento text, p_nombre text, p_token uuid) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions;
  p public.event_roster;
begin
  select * into e from public.event_editions where id = p_evento;
  if not found or p_token is null then
    raise exception 'evento desconocido' using errcode = '22023';
  end if;
  select * into p from public.event_roster where evento = p_evento and token = p_token;
  if found then
    return jsonb_build_object('nombre', p.nombre);
  end if;
  if not public.evento_en_juego(e) then
    raise exception 'el evento no está activo' using errcode = '22023';
  end if;

  select * into p from public.event_roster
   where evento = p_evento and clave = public.evento_normaliza(btrim(coalesce(p_nombre, '')))
   for update;
  if not found then
    raise exception 'ese nombre no está en la lista' using errcode = '22023';
  end if;
  if p.token is not null then
    raise exception 'ese nombre ya está elegido: si eres tú, avisa a la organización' using errcode = '22023';
  end if;
  update public.event_roster set token = p_token, elegido_en = now() where id = p.id;
  return jsonb_build_object('nombre', p.nombre);
end;
$$;

-- Lo de un participante, para rehacer la pantalla al recargar: su nombre, cuántas palabras hay y lo jugado.
create function public.mi_juego(p_evento text, p_token uuid) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.event_roster := public.evento_jugador(p_evento, p_token);
begin
  return jsonb_build_object(
    'nombre', p.nombre,
    'rondas', coalesce((select jsonb_agg(public.evento_ronda(p.id, r.orden) order by r.orden)
                          from public.event_rounds r where r.jugador = p.id), '[]'::jsonb)
  );
end;
$$;

-- Empieza una palabra: su cronómetro arranca con la hora del servidor la primera vez y no se mueve si se repite. Las
-- palabras van en orden: la siguiente solo con la anterior terminada.
create function public.empezar_palabra(p_evento text, p_token uuid, p_orden integer) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.event_roster := public.evento_jugador(p_evento, p_token);
  e public.event_editions;
begin
  if exists (select 1 from public.event_rounds where jugador = p.id and orden = p_orden) then
    return public.evento_ronda(p.id, p_orden);
  end if;
  select * into e from public.event_editions where id = p_evento;
  if not public.evento_en_juego(e) then
    raise exception 'el evento no está activo' using errcode = '22023';
  end if;
  if not exists (select 1 from public.event_targets where evento = p_evento and orden = p_orden) then
    raise exception 'esa palabra no existe' using errcode = '22023';
  end if;
  if p_orden > 1 and not exists (select 1 from public.event_rounds
                                  where jugador = p.id and orden = p_orden - 1 and terminada_en is not null) then
    raise exception 'termina antes la palabra anterior' using errcode = '22023';
  end if;

  insert into public.event_rounds (jugador, orden, empezada_en) values (p.id, p_orden, now())
  on conflict (jugador, orden) do nothing;
  return public.evento_ronda(p.id, p_orden);
end;
$$;

-- Un intento. Con cinco verdes o con el sexto, la palabra termina con la hora del servidor.
--
-- `p_numero` es el número de intento que el móvil cree que envía (1 a 6). Lo hace **idempotente**: el reenvío de un
-- intento que llegó pero cuya respuesta se perdió devuelve la ronda tal cual, sin gastar otro.
create function public.probar_palabra(p_evento text, p_token uuid, p_orden integer, p_palabra text, p_numero integer)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.event_roster := public.evento_jugador(p_evento, p_token);
  e public.event_editions;
  r public.event_rounds;
  palabra_ text := public.evento_normaliza(coalesce(p_palabra, ''));
  colores_ text;
  n_ integer;
  resuelta_ boolean;
begin
  select * into r from public.event_rounds where jugador = p.id and orden = p_orden for update;
  if not found then
    raise exception 'esa palabra no está empezada' using errcode = '22023';
  end if;

  if p_numero between 1 and r.intentos then
    if exists (select 1 from public.event_tries t
                where t.jugador = p.id and t.orden = p_orden and t.n = p_numero and t.palabra = palabra_) then
      return public.evento_ronda(p.id, p_orden);
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
  -- Vale una palabra del diccionario o la solución de **esta** palabra (por si la empresa elige una que no está en él).
  -- La de otra ronda no: un intento aceptado fuera del diccionario delataría una solución futura.
  if not exists (select 1 from public.event_words w where w.palabra = palabra_)
     and not exists (select 1 from public.event_targets t
                      where t.evento = p_evento and t.orden = p_orden and t.palabra = palabra_) then
    raise exception 'la palabra no está en la lista' using errcode = '22023';
  end if;

  select public.evento_wordle(t.palabra, palabra_) into colores_
    from public.event_targets t where t.evento = p_evento and t.orden = p_orden;
  n_ := r.intentos + 1;
  resuelta_ := colores_ = 'GGGGG';

  insert into public.event_tries (jugador, orden, n, palabra, colores) values (p.id, p_orden, n_, palabra_, colores_);
  update public.event_rounds
     set intentos = n_,
         resuelta = resuelta_,
         terminada_en = case when resuelta_ or n_ = 6 then now() end
   where jugador = p.id and orden = p_orden;

  return public.evento_ronda(p.id, p_orden);
end;
$$;

-- ── Lo que llama el admin (con PIN) ───────────────────────────────────────────────────────────────────────

-- Activa el evento. Activado, no se mueve. Un PIN que no vale vuelve como `{error}`, sin lanzar: así cuenta el fallo.
create or replace function public.empezar_evento(p_evento text, p_pin text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  pin text := public.evento_pin(p_evento, p_pin);
  e public.event_editions;
begin
  if pin <> 'ok' then
    return public.evento_pin_rechazado(pin);
  end if;
  update public.event_editions set empieza_en = coalesce(empieza_en, now()) where id = p_evento returning * into e;
  return jsonb_build_object('empieza_en', e.empieza_en);
end;
$$;

-- Termina el evento: no se admiten más intentos y salen los puntos y las soluciones. Terminado, no se mueve.
create or replace function public.terminar_evento(p_evento text, p_pin text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  pin text := public.evento_pin(p_evento, p_pin);
  e public.event_editions;
begin
  if pin <> 'ok' then
    return public.evento_pin_rechazado(pin);
  end if;
  select * into e from public.event_editions where id = p_evento;
  if e.empieza_en is null then
    return jsonb_build_object('error', 'El evento no está activado.');
  end if;
  update public.event_editions set terminado_en = coalesce(terminado_en, now()) where id = p_evento returning * into e;
  return jsonb_build_object('terminado_en', e.terminado_en);
end;
$$;

-- Deja libre un nombre elegido por error y borra lo que se jugó con él. Con el evento terminado no: cambiaría los puntos.
create function public.liberar_nombre(p_evento text, p_pin text, p_nombre text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  pin text := public.evento_pin(p_evento, p_pin);
  p public.event_roster;
begin
  if pin <> 'ok' then
    return public.evento_pin_rechazado(pin);
  end if;
  if exists (select 1 from public.event_editions e where e.id = p_evento and public.evento_terminado(e)) then
    return jsonb_build_object('error', 'El evento ha terminado: los nombres ya no se liberan.');
  end if;
  select * into p from public.event_roster
   where evento = p_evento and clave = public.evento_normaliza(btrim(coalesce(p_nombre, '')));
  if not found then
    return jsonb_build_object('error', 'Ese nombre no está en la lista.');
  end if;
  delete from public.event_rounds where jugador = p.id;
  update public.event_roster set token = null, elegido_en = null where id = p.id;
  return jsonb_build_object('nombre', p.nombre);
end;
$$;

-- Todo lo del admin. Durante el evento, contadores sin nombres ni tiempos y la lista para liberar nombres; terminado,
-- además los puntos de cada participante y de cada grupo, y las soluciones.
create function public.panel_del_evento(p_evento text, p_pin text) returns jsonb
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
  ) || case when not terminado then '{}'::jsonb else jsonb_build_object(
    'jugadores', coalesce((
      select jsonb_agg(jsonb_build_object('puesto', puesto, 'nombre', nombre, 'grupo', grupo, 'puntos', puntos,
                                          'palabras', palabras) order by puesto, nombre)
        from (select x.*, rank() over (order by x.puntos desc) as puesto from public.evento_puntos(p_evento) x) j
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
  ) end;
end;
$$;

-- ── Permisos ──────────────────────────────────────────────────────────────────────────────────────────────

revoke all on function public.estado_del_juego(text), public.nombres_del_evento(text),
  public.elegir_nombre(text, text, uuid), public.mi_juego(text, uuid), public.empezar_palabra(text, uuid, integer),
  public.probar_palabra(text, uuid, integer, text, integer), public.liberar_nombre(text, text, text),
  public.panel_del_evento(text, text)
  from public, anon, authenticated;
grant execute on function public.estado_del_juego(text), public.nombres_del_evento(text),
  public.elegir_nombre(text, text, uuid), public.mi_juego(text, uuid), public.empezar_palabra(text, uuid, integer),
  public.probar_palabra(text, uuid, integer, text, integer), public.liberar_nombre(text, text, text),
  public.panel_del_evento(text, text), public.empezar_evento(text, text), public.terminar_evento(text, text)
  to anon, authenticated;

-- El juego de frases deja de ser público: sus funciones siguen ahí, pero la web ya no puede llamarlas.
revoke execute on function public.unirse_al_evento(text, text, uuid, text), public.estado_del_evento(text),
  public.estado_del_evento(text, uuid, text), public.mi_partida_del_evento(text, uuid),
  public.empezar_frase(text, uuid, integer), public.intentar_palabra(text, uuid, integer, text, integer),
  public.ranking_del_evento(text), public.ranking_del_evento(text, uuid, text)
  from public, anon, authenticated;
