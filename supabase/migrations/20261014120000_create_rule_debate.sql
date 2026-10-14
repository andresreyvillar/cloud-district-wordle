-- El debate de reglas: votaciones abiertas, sus votos y las propuestas de los jugadores.
--
-- Slice: debate-de-reglas (openspec/slices/dashboard/debate-de-reglas.md).
--
-- **Aditiva** (ADR 0005): no toca `wordle_results` ni `season_snapshots`, solo lee la primera para saber quién
-- ha jugado alguna vez.
--
-- La clave pública **no escribe en las tablas**: las lee y ejecuta `votar_regla` y `proponer_regla`, que
-- deciden qué entra. Quién eres se elige en la web, sin cuentas (decisión del dueño), así que las funciones
-- solo admiten a quien ha jugado y los votos se leen con su nombre: si alguien vota por otro, el otro lo ve.
--
-- El dueño aprueba propuestas y cierra votaciones desde Supabase:
--   update public.rule_proposals set estado = 'aprobada' where id = …;
--   update public.rule_polls set abierta = false where id = '…';

create table public.rule_polls (
  id text primary key,
  titulo text not null,
  descripcion text not null default '',
  -- [{id, texto}], en el orden en que se enseñan.
  opciones jsonb not null check (jsonb_typeof(opciones) = 'array' and jsonb_array_length(opciones) >= 2),
  abierta boolean not null default true,
  created_at timestamptz not null default now()
);

create table public.rule_votes (
  votacion text not null references public.rule_polls (id) on delete cascade,
  votante text not null,
  opcion text not null,
  updated_at timestamptz not null default now(),
  -- Una persona, un voto: votar otra vez lo cambia.
  primary key (votacion, votante)
);

create table public.rule_proposals (
  id bigint generated always as identity primary key,
  autor text not null,
  titulo text not null check (char_length(titulo) between 3 and 120),
  texto text not null check (char_length(texto) between 10 and 2000),
  -- **Pendiente hasta que el dueño la apruebe.** La web es pública y la propuesta va firmada con el nombre de
  -- un compañero identificable: no se publica sola.
  estado text not null default 'pendiente' check (estado in ('pendiente', 'aprobada', 'rechazada')),
  created_at timestamptz not null default now()
);

alter table public.rule_polls enable row level security;
alter table public.rule_votes enable row level security;
alter table public.rule_proposals enable row level security;

create policy "lectura publica" on public.rule_polls for select using (true);
create policy "lectura publica" on public.rule_votes for select using (true);
create policy "lectura de las aprobadas" on public.rule_proposals for select using (estado = 'aprobada');

-- Supabase da por defecto todos los privilegios de las tablas nuevas a `anon` y `authenticated`. Sin política
-- de escritura la RLS ya bloquea insert, update y delete, pero no `truncate`: quitar el privilegio lo cierra todo.
revoke insert, update, delete, truncate on public.rule_polls, public.rule_votes, public.rule_proposals
  from anon, authenticated;

create function public.votar_regla(p_votacion text, p_votante text, p_opcion text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  abierta_ boolean;
begin
  if p_votacion is null or p_votante is null or p_opcion is null then
    raise exception 'faltan datos del voto' using errcode = '22023';
  end if;

  select abierta into abierta_ from public.rule_polls where id = p_votacion;
  if not found then
    raise exception 'votación desconocida' using errcode = '22023';
  end if;
  if not abierta_ then
    raise exception 'votación cerrada' using errcode = '22023';
  end if;

  if not exists (
    select 1 from public.rule_polls, jsonb_array_elements(opciones) as o
     where id = p_votacion and o->>'id' = p_opcion
  ) then
    raise exception 'opción desconocida' using errcode = '22023';
  end if;

  if not exists (select 1 from public.wordle_results where slack_user_id = p_votante) then
    raise exception 'jugador desconocido' using errcode = '22023';
  end if;

  insert into public.rule_votes (votacion, votante, opcion)
  values (p_votacion, p_votante, p_opcion)
  on conflict (votacion, votante) do update set opcion = excluded.opcion, updated_at = now();

  return jsonb_build_object('opcion', p_opcion);
end;
$$;

create function public.proponer_regla(p_autor text, p_titulo text, p_texto text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  -- Tope de propuestas sin revisar por persona: frena el relleno sin cortar a quien propone de verdad.
  pendientes_maximas constant integer := 3;
  -- Sin espacios, tabuladores ni saltos de línea en los bordes: `btrim` a secas solo quita espacios, y una
  -- explicación de diez saltos de línea pasaba el mínimo.
  titulo_ text := btrim(coalesce(p_titulo, ''), E' \t\r\n');
  texto_ text := btrim(coalesce(p_texto, ''), E' \t\r\n');
begin
  if p_autor is null or not exists (select 1 from public.wordle_results where slack_user_id = p_autor) then
    raise exception 'jugador desconocido' using errcode = '22023';
  end if;

  if char_length(titulo_) < 3 or char_length(titulo_) > 120 then
    raise exception 'el título tiene que tener entre 3 y 120 caracteres' using errcode = '22023';
  end if;
  if char_length(texto_) < 10 or char_length(texto_) > 2000 then
    raise exception 'la explicación tiene que tener entre 10 y 2000 caracteres' using errcode = '22023';
  end if;

  -- Una propuesta a la vez por autor: sin el cerrojo, varias peticiones simultáneas contaban las mismas
  -- pendientes y entraban todas.
  perform pg_advisory_xact_lock(hashtext('proponer_regla:' || p_autor));
  if (select count(*) from public.rule_proposals where autor = p_autor and estado = 'pendiente')
     >= pendientes_maximas then
    raise exception 'ya tienes tres propuestas pendientes de revisar' using errcode = '22023';
  end if;

  insert into public.rule_proposals (autor, titulo, texto) values (p_autor, titulo_, texto_);
  return jsonb_build_object('estado', 'pendiente');
end;
$$;

revoke all on function public.votar_regla(text, text, text) from public, anon, authenticated;
grant execute on function public.votar_regla(text, text, text) to anon, authenticated;
revoke all on function public.proponer_regla(text, text, text) from public, anon, authenticated;
grant execute on function public.proponer_regla(text, text, text) to anon, authenticated;

-- La primera votación: qué hacer con los spoilers (2026-10-14). El grupo decide, incluido no hacer nada.
insert into public.rule_polls (id, titulo, descripcion, opciones) values (
  'anti-spoilers',
  '¿Qué hacemos con los spoilers?',
  'Una pista en un comentario ayuda a quien juega después. El 14 de octubre, tras un comentario con una pista '
  || 'evidente, la jornada se resolvió bastante mejor a partir de las 10:00. Medido sobre 211 jornadas, publicar '
  || 'tarde no da ventaja por sí solo: la ventaja aparece el día del spoiler.',
  '[
    {"id": "anular", "texto": "Anular la jornada: si el grupo marca un spoiler, ese día no cuenta para nadie y quien dio la pista recibe una sanción"},
    {"id": "cortar", "texto": "Cortar en el spoiler: los resultados publicados después del spoiler no cuentan"},
    {"id": "prevencion", "texto": "Solo prevención: nada de pistas sobre la palabra antes de las 18:00, sin sanción"},
    {"id": "nada", "texto": "No hacer nada"}
  ]'::jsonb
);
