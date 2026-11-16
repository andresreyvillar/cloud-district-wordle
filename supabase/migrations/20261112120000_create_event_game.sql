-- El juego del evento: «La frase del día» de lapalabradeldia.com, con frases que se liberan cada intervalo.
--
-- Slices: frase-del-evento y pantalla-del-evento (openspec/slices/dashboard/).
--
-- Reglas: cada frase está tapada; se juega con palabras válidas de cinco letras, cinco como mucho. Cada letra de la
-- palabra que está en la frase y no se había destapado sale verde y se destapa en toda la frase; si ya estaba
-- destapada, amarilla; si no está, gris. Se gana al destapar todas las letras distintas de la frase.
--
-- **Aditiva** (ADR 0005): tablas nuevas, sin tocar `wordle_results` ni ninguna otra.
--
-- **La clave pública no lee ni escribe ninguna tabla del evento.** La solución de una frase y la huella del PIN
-- no pueden ser legibles desde el navegador, así que todo pasa por funciones `SECURITY DEFINER` que validan lo
-- que entra y devuelven solo lo que se puede ver. Las horas las pone siempre el servidor.
--
-- **Esta migración no trae ni frases ni PIN**: el repositorio es público. El evento se carga por SQL:
--   insert into public.event_editions (id, titulo, intervalo_minutos, pin_hash)
--     values ('<id>', '<título>', 30, encode(sha256(convert_to('<PIN largo>', 'UTF8')), 'hex'));
--   insert into public.event_phrases (evento, orden, frase) values ('<id>', 1, '<frase>'), …;
-- Para pedir contraseña al entrar: update public.event_editions set clave_hash = encode(sha256(convert_to('<clave>',
-- 'UTF8')), 'hex') where id = '<id>';
-- El PIN, **largo y aleatorio** (por ejemplo `openssl rand -base64 12`): cualquiera puede llamar a
-- `empezar_evento` y no hay bloqueo por intentos, así que uno corto se adivina a base de probar.
--
-- Las palabras válidas (`event_words`) llegan en la migración siguiente, generada por tools/diccionario_evento.py.

create table public.event_editions (
  id text primary key check (id ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  titulo text not null,
  -- Cada cuánto se libera una frase. 10 en las pruebas, 30 el día del evento: se cambia aquí, sin desplegar.
  intervalo_minutos integer not null default 30 check (intervalo_minutos between 1 and 180),
  -- Vacío hasta que el presentador empieza el evento.
  empieza_en timestamptz,
  -- Vacío hasta que el presentador lo termina: entonces se publican el ranking y las soluciones.
  terminado_en timestamptz,
  pin_hash text not null check (pin_hash ~ '^[0-9a-f]{64}$'),
  -- Contraseña de acceso, opcional: con ella, solo entra quien la sabe (una demo para la organización). Se guarda su
  -- huella, como la del PIN; la contraseña no está en el repositorio.
  clave_hash text check (clave_hash ~ '^[0-9a-f]{64}$')
);

create table public.event_phrases (
  evento text not null references public.event_editions (id) on delete cascade,
  orden integer not null check (orden >= 1),
  -- Letras (con tildes y ñ), espacios y signos. Al menos una letra.
  frase text not null check (frase ~ '^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ .,;:¿?¡!''"-]+$' and frase ~ '[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]'),
  primary key (evento, orden)
);

create table public.event_players (
  id bigint generated always as identity primary key,
  evento text not null references public.event_editions (id) on delete cascade,
  -- Letras latinas (las de Latin-1: tildes, ñ, ç, ã…), cifras, espacios sueltos y . ' -, con al menos una letra o
  -- cifra: sin caracteres invisibles ni letras de otros alfabetos que se parezcan a las nuestras («\u0410na», A cirílica).
  nombre text not null check (char_length(nombre) between 1 and 30
                              and nombre ~ '^[A-Za-zÀ-ÖØ-öø-ÿ0-9.''-]+( [A-Za-zÀ-ÖØ-öø-ÿ0-9.''-]+)*$'
                              and nombre ~ '[A-Za-z0-9À-ÖØ-öø-ÿ]'),
  -- El nombre sin mayúsculas ni tildes: «ANA» y «Ána» son el mismo.
  clave text not null,
  token uuid not null,
  created_at timestamptz not null default now(),
  unique (evento, clave),
  unique (evento, token)
);

create table public.event_plays (
  jugador bigint not null references public.event_players (id) on delete cascade,
  orden integer not null,
  empezada_en timestamptz not null,
  terminada_en timestamptz,
  resuelta boolean not null default false,
  intentos integer not null default 0 check (intentos between 0 and 5),
  -- Las letras destapadas hasta ahora, sin repetir.
  descubiertas text not null default '' check (descubiertas ~ '^[a-zñ]*$'),
  primary key (jugador, orden)
);

create table public.event_guesses (
  jugador bigint not null,
  orden integer not null,
  n integer not null check (n between 1 and 5),
  palabra text not null check (palabra ~ '^[a-zñ]{5}$'),
  colores text not null check (colores ~ '^[GY.]{5}$'),
  primary key (jugador, orden, n),
  foreign key (jugador, orden) references public.event_plays (jugador, orden) on delete cascade
);

alter table public.event_editions enable row level security;
alter table public.event_phrases enable row level security;
alter table public.event_players enable row level security;
alter table public.event_plays enable row level security;
alter table public.event_guesses enable row level security;

-- Sin políticas y sin privilegios: con la clave pública, ni leer. Supabase da por defecto todos los privilegios
-- de las tablas nuevas a `anon` y `authenticated`; sin quitarlos, la RLS dejaría el `select` en cero filas pero
-- no el `truncate`.
revoke all on public.event_editions, public.event_phrases, public.event_players, public.event_plays,
  public.event_guesses from anon, authenticated;
revoke all on sequence public.event_players_id_seq from anon, authenticated;

-- Empezado el evento, el intervalo no se cambia: movería las liberaciones. Para un ensayo, se vacía antes
-- `empieza_en`.
create function public.evento_intervalo_congelado() returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if old.empieza_en is not null and new.empieza_en is not null
     and new.intervalo_minutos <> old.intervalo_minutos then
    raise exception 'el evento ya ha empezado: el intervalo no se cambia' using errcode = '22023';
  end if;
  return new;
end;
$$;

create trigger intervalo_congelado before update on public.event_editions
  for each row execute function public.evento_intervalo_congelado();

-- ── Ayudantes (sin acceso público) ────────────────────────────────────────────────────────────────────────

-- Minúsculas y sin tildes ni diéresis. La ñ se queda: es otra letra. NFC primero: una tilde escrita como carácter
-- combinable pasa a ser una sola letra y la traducción la quita. Las mayúsculas acentuadas se traducen a mano
-- porque `lower` depende de la collation de la base y con `C` no toca lo que no es ASCII.
create function public.evento_normaliza(texto text) returns text
language sql
immutable
set search_path = ''
as $$
  select lower(translate(normalize(texto, NFC), 'ÁÀÄÂÉÈËÊÍÌÏÎÓÒÖÔÚÙÜÛÑáàäâéèëêíìïîóòöôúùüû',
                                                'aaaaeeeeiiiioooouuuuñaaaaeeeeiiiioooouuuu'));
$$;

-- Las letras distintas de un texto, normalizadas y en orden alfabético: «¡Más vale!» → «aelmsv».
create function public.evento_letras(frase text) returns text
language sql
immutable
set search_path = ''
as $$
  select coalesce(string_agg(distinct letra, '' order by letra), '')
    from regexp_split_to_table(regexp_replace(public.evento_normaliza(frase), '[^a-zñ]', '', 'g'), '') as letra
   where letra <> '';
$$;

-- La frase tal como la ve quien tiene destapadas esas letras: cada letra tapada es `_`; las destapadas, los
-- espacios y los signos, en su sitio. Con todo destapado es la frase.
create function public.evento_visible(frase text, descubiertas text) returns text
language sql
immutable
set search_path = ''
as $$
  select string_agg(
           case when c ~ '[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]' and strpos(descubiertas, public.evento_normaliza(c)) = 0
                then '_' else c end, '' order by i)
    from unnest(regexp_split_to_array(frase, '')) with ordinality as t(c, i);
$$;

-- Los colores de una palabra, como «La frase del día»: contra el conjunto de letras de la frase, no por posición.
-- `G` si está y no se había destapado (repetida en la misma palabra, `G` las dos veces), `Y` si ya estaba
-- destapada, `.` si no está.
create function public.evento_colores(letras_frase text, descubiertas text, palabra text) returns text
language sql
immutable
set search_path = ''
as $$
  select string_agg(
           case when strpos(letras_frase, c) = 0 then '.'
                when strpos(descubiertas, c) > 0 then 'Y'
                else 'G' end, '' order by i)
    from unnest(regexp_split_to_array(palabra, '')) with ordinality as t(c, i);
$$;

-- El estado de una frase a una hora: pendiente hasta que se libera, abierta hasta que termina el evento, y cerrada.
create function public.evento_ventana(empieza_en timestamptz, terminado_en timestamptz, intervalo integer,
                                      orden integer, ahora timestamptz)
returns text
language sql
immutable
set search_path = ''
as $$
  select case
    when empieza_en is null or ahora < empieza_en + make_interval(mins => intervalo * (orden - 1)) then 'pendiente'
    when terminado_en is not null and ahora >= terminado_en then 'cerrada'
    else 'abierta'
  end;
$$;

-- El participante de un token, o error.
create function public.evento_participante(p_evento text, p_token uuid) returns public.event_players
language plpgsql
stable
set search_path = ''
as $$
declare
  p public.event_players;
begin
  select * into p from public.event_players where evento = p_evento and token = p_token;
  if not found then
    raise exception 'no estás apuntado al evento' using errcode = '22023';
  end if;
  return p;
end;
$$;

-- Una partida tal como la ve su dueño: la frase con lo destapado, sus palabras, si terminó y en cuánto. Nunca la
-- frase entera, salvo que la haya destapado entera.
create function public.evento_partida(p_jugador bigint, p_evento text, p_orden integer) returns jsonb
language sql
stable
set search_path = ''
as $$
  select jsonb_build_object(
    'orden', pl.orden,
    'visible', public.evento_visible(f.frase, pl.descubiertas),
    'descubiertas', pl.descubiertas,
    'empezada_en', pl.empezada_en,
    'terminada_en', pl.terminada_en,
    'resuelta', pl.resuelta,
    'tiempo_ms', case when pl.terminada_en is null then null
                      else floor(extract(epoch from pl.terminada_en - pl.empezada_en) * 1000)::bigint end,
    'intentos', coalesce((select jsonb_agg(jsonb_build_object('palabra', g.palabra, 'colores', g.colores) order by g.n)
                            from public.event_guesses g where g.jugador = pl.jugador and g.orden = pl.orden), '[]'::jsonb)
  )
  from public.event_plays pl
  join public.event_phrases f on f.evento = p_evento and f.orden = pl.orden
  where pl.jugador = p_jugador and pl.orden = p_orden;
$$;

-- Comprueba el PIN contra la huella, o error. El mismo mensaje exista o no el evento.
create function public.evento_con_pin(p_evento text, p_pin text) returns public.event_editions
language plpgsql
set search_path = ''
as $$
declare
  e public.event_editions;
begin
  select * into e from public.event_editions where id = p_evento for update;
  if not found or e.pin_hash <> encode(sha256(convert_to(coalesce(p_pin, ''), 'UTF8')), 'hex') then
    raise exception 'PIN incorrecto' using errcode = '22023';
  end if;
  return e;
end;
$$;

revoke all on function public.evento_normaliza(text), public.evento_letras(text), public.evento_visible(text, text),
  public.evento_colores(text, text, text),
  public.evento_ventana(timestamptz, timestamptz, integer, integer, timestamptz),
  public.evento_participante(text, uuid), public.evento_partida(bigint, text, integer),
  public.evento_con_pin(text, text), public.evento_intervalo_congelado()
  from public, anon, authenticated;

-- ── Lo que llama la web ───────────────────────────────────────────────────────────────────────────────────

-- Apunta a un participante. Un token ya apuntado conserva su nombre; un nombre ya apuntado con otro token se
-- rechaza.
create function public.unirse_al_evento(p_evento text, p_nombre text, p_token uuid, p_clave text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  -- Todo blanco (también el no separable y los de ancho cero) se pliega a un espacio, y luego se recorta.
  nombre_ text := btrim(regexp_replace(normalize(coalesce(p_nombre, ''), NFC),
                        '[\s\u00a0\u1680\u180e\u2000-\u200f\u2028\u2029\u202f\u205f\u2060\u3000\ufeff]+', ' ', 'g'));
  existente text;
  clave_hash_ text;
  -- Tope de altas por evento: un script no puede llenar el ranking ni ocupar los nombres de todos.
  maximo constant integer := 500;
begin
  select clave_hash into clave_hash_ from public.event_editions where id = p_evento;
  if p_token is null or not found then
    raise exception 'evento desconocido' using errcode = '22023';
  end if;

  -- Un móvil ya apuntado no vuelve a necesitar la contraseña: su token ya demuestra que la sabía.
  select nombre into existente from public.event_players where evento = p_evento and token = p_token;
  if found then
    return jsonb_build_object('nombre', existente);
  end if;

  if clave_hash_ is not null
     and clave_hash_ <> encode(sha256(convert_to(coalesce(p_clave, ''), 'UTF8')), 'hex') then
    raise exception 'contraseña incorrecta' using errcode = '22023';
  end if;

  if char_length(nombre_) < 1 or char_length(nombre_) > 30 then
    raise exception 'el nombre tiene que tener entre 1 y 30 caracteres' using errcode = '22023';
  end if;
  if nombre_ !~ '^[A-Za-zÀ-ÖØ-öø-ÿ0-9.''-]+( [A-Za-zÀ-ÖØ-öø-ÿ0-9.''-]+)*$'
     or nombre_ !~ '[A-Za-z0-9À-ÖØ-öø-ÿ]' then
    raise exception 'el nombre solo puede llevar letras, números, espacios y . '' -' using errcode = '22023';
  end if;

  perform pg_advisory_xact_lock(hashtext('unirse_al_evento:' || p_evento));
  if (select count(*) from public.event_players where evento = p_evento) >= maximo then
    raise exception 'el evento está completo' using errcode = '22023';
  end if;

  begin
    insert into public.event_players (evento, nombre, clave, token)
    values (p_evento, nombre_, public.evento_normaliza(nombre_), p_token);
  exception when unique_violation then
    raise exception 'ese nombre ya está apuntado: elige otro' using errcode = '22023';
  end;
  return jsonb_build_object('nombre', nombre_);
end;
$$;

-- Lo público del evento: la hora del servidor, cuándo sale cada frase, los contadores sin nombres y, terminado el
-- evento, las soluciones.
create function public.estado_del_evento(p_evento text) returns jsonb
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

-- Lo de un participante: su nombre y sus partidas, para rehacer la pantalla al recargar.
create function public.mi_partida_del_evento(p_evento text, p_token uuid) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.event_players := public.evento_participante(p_evento, p_token);
begin
  return jsonb_build_object(
    'nombre', p.nombre,
    'partidas', coalesce((select jsonb_agg(public.evento_partida(p.id, p_evento, pl.orden) order by pl.orden)
                            from public.event_plays pl where pl.jugador = p.id), '[]'::jsonb)
  );
end;
$$;

-- Empieza una frase: el cronómetro arranca en cero con la hora del servidor la primera vez y no se mueve si se repite.
create function public.empezar_frase(p_evento text, p_token uuid, p_orden integer) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.event_players := public.evento_participante(p_evento, p_token);
  e public.event_editions;
begin
  select * into e from public.event_editions where id = p_evento;
  if not exists (select 1 from public.event_phrases where evento = p_evento and orden = p_orden)
     or public.evento_ventana(e.empieza_en, e.terminado_en, e.intervalo_minutos, p_orden, now()) <> 'abierta' then
    raise exception 'esa frase no está abierta' using errcode = '22023';
  end if;

  insert into public.event_plays (jugador, orden, empezada_en) values (p.id, p_orden, now())
  on conflict (jugador, orden) do nothing;
  return public.evento_partida(p.id, p_evento, p_orden);
end;
$$;

-- Una palabra: vuelve la partida con sus colores y lo destapado. Al destapar la frase entera o al gastar la quinta,
-- la partida termina con la hora del servidor.
--
-- `p_numero` es el número de intento que el móvil cree que envía (1 a 5). Lo hace **idempotente**: si la palabra
-- llegó pero se perdió la respuesta, el reenvío trae el mismo número y la misma palabra, y vuelve la partida tal
-- cual sin guardar nada. Sin él, un reenvío gastaba un intento más, y el que resolvía quedaba rechazado con la
-- partida ya terminada.
create function public.intentar_palabra(p_evento text, p_token uuid, p_orden integer, p_palabra text, p_numero integer)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.event_players := public.evento_participante(p_evento, p_token);
  e public.event_editions;
  pl public.event_plays;
  letras_frase text;
  palabra_ text := public.evento_normaliza(coalesce(p_palabra, ''));
  colores_ text;
  descubiertas_ text;
  n_ integer;
  resuelta_ boolean;
begin
  -- Una palabra a la vez por partida: dos envíos simultáneos no gastan el mismo número.
  select * into pl from public.event_plays where jugador = p.id and orden = p_orden for update;
  if not found then
    raise exception 'esa frase no está empezada' using errcode = '22023';
  end if;

  -- El reenvío de una palabra que ya está guardada devuelve la partida como quedó, también si aquella la terminó.
  if p_numero between 1 and pl.intentos then
    if exists (select 1 from public.event_guesses g
                where g.jugador = p.id and g.orden = p_orden and g.n = p_numero and g.palabra = palabra_) then
      return public.evento_partida(p.id, p_evento, p_orden);
    end if;
    raise exception 'esa palabra ya está enviada' using errcode = '22023';
  end if;

  select * into e from public.event_editions where id = p_evento;
  if public.evento_ventana(e.empieza_en, e.terminado_en, e.intervalo_minutos, p_orden, now()) <> 'abierta' then
    raise exception 'esa frase no está abierta' using errcode = '22023';
  end if;
  if pl.terminada_en is not null then
    raise exception 'esa partida ya ha terminado' using errcode = '22023';
  end if;
  if p_numero is distinct from pl.intentos + 1 then
    raise exception 'intento fuera de orden' using errcode = '22023';
  end if;
  if palabra_ !~ '^[a-zñ]{5}$' then
    raise exception 'la palabra tiene que tener cinco letras' using errcode = '22023';
  end if;
  if not exists (select 1 from public.event_words w where w.palabra = palabra_) then
    raise exception 'la palabra no está en la lista' using errcode = '22023';
  end if;

  select public.evento_letras(frase) into letras_frase from public.event_phrases where evento = p_evento and orden = p_orden;
  colores_ := public.evento_colores(letras_frase, pl.descubiertas, palabra_);
  -- Lo destapado, sin repetir: lo de antes más las letras de esta palabra que están en la frase.
  descubiertas_ := public.evento_letras(pl.descubiertas || regexp_replace(palabra_, '[^' || letras_frase || ']', '', 'g'));
  n_ := pl.intentos + 1;
  resuelta_ := descubiertas_ = letras_frase;

  insert into public.event_guesses (jugador, orden, n, palabra, colores) values (p.id, p_orden, n_, palabra_, colores_);
  update public.event_plays
     set intentos = n_,
         descubiertas = descubiertas_,
         resuelta = resuelta_,
         terminada_en = case when resuelta_ or n_ = 5 then now() end
   where jugador = p.id and orden = p_orden;

  return public.evento_partida(p.id, p_evento, p_orden);
end;
$$;

-- Empieza el evento si el PIN coincide con su huella. Empezado, no se mueve.
create function public.empezar_evento(p_evento text, p_pin text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions := public.evento_con_pin(p_evento, p_pin);
begin
  if e.empieza_en is null then
    update public.event_editions set empieza_en = now() where id = p_evento returning * into e;
  end if;
  return jsonb_build_object('empieza_en', e.empieza_en);
end;
$$;

-- Termina el evento si el PIN coincide: no se admiten más palabras y se publican el ranking y las soluciones.
-- Terminado, no se mueve.
create function public.terminar_evento(p_evento text, p_pin text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions := public.evento_con_pin(p_evento, p_pin);
begin
  if e.empieza_en is null then
    raise exception 'el evento no ha empezado' using errcode = '22023';
  end if;
  if e.terminado_en is null then
    update public.event_editions set terminado_en = now() where id = p_evento returning * into e;
  end if;
  return jsonb_build_object('terminado_en', e.terminado_en);
end;
$$;

-- El ranking final: solo con el evento terminado. Primero más frases resueltas; a igualdad, menos tiempo total,
-- que suma las partidas terminadas (resueltas o perdidas). Una partida a medias no cuenta; quien no terminó
-- ninguna no sale.
create function public.ranking_del_evento(p_evento text) returns jsonb
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

revoke all on function public.unirse_al_evento(text, text, uuid, text), public.estado_del_evento(text),
  public.mi_partida_del_evento(text, uuid), public.empezar_frase(text, uuid, integer),
  public.intentar_palabra(text, uuid, integer, text, integer), public.empezar_evento(text, text),
  public.terminar_evento(text, text), public.ranking_del_evento(text)
  from public, anon, authenticated;
grant execute on function public.unirse_al_evento(text, text, uuid, text), public.estado_del_evento(text),
  public.mi_partida_del_evento(text, uuid), public.empezar_frase(text, uuid, integer),
  public.intentar_palabra(text, uuid, integer, text, integer), public.empezar_evento(text, text),
  public.terminar_evento(text, text), public.ranking_del_evento(text)
  to anon, authenticated;
