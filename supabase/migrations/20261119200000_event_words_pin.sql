-- Las palabras tienen su propio PIN: quien las revisa lo crea la primera vez y desde entonces hace falta.
--
-- Slice: admin-del-evento (openspec/slices/dashboard/). Cambio: feat-pin-de-palabras.
--
-- Decisión del dueño: en el dashboard hay un botón para quien revisa las palabras (Nouha); la primera vez crea un PIN
-- de cuatro cifras que solo sabe ella, y desde entonces ese PIN hace falta para verlas y cambiarlas, siempre antes de
-- la hora de empezar. El dueño juega sin conocerlas.
--
-- **Es un PIN aparte del del evento.** El orden de las palabras de cada participante se calcula con la huella del PIN
-- del evento (`evento_orden_de`): si el PIN de las palabras fuera ese, crearlo barajaría a todos.
--
-- Cinco fallos seguidos bloquean el PIN de las palabras cinco minutos, también el bueno. Si se olvida, se reinicia por
-- SQL (`palabras_pin_hash = null`) y el siguiente que entre crea uno nuevo. Las funciones sin PIN que había
-- (`palabras_del_evento`, `cambiar_palabra`) dejan de ser públicas: no queda atajo.
--
-- **Aditiva** (ADR 0005): tres columnas nuevas que admiten nulo o tienen valor por defecto, y funciones nuevas.

alter table public.event_editions
  add column palabras_pin_hash text check (palabras_pin_hash ~ '^[0-9a-f]{64}$'),
  add column palabras_pin_fallos integer not null default 0 check (palabras_pin_fallos >= 0),
  add column palabras_pin_bloqueado_hasta timestamptz;

revoke execute on function public.palabras_del_evento(text), public.cambiar_palabra(text, integer, text)
  from public, anon, authenticated;

-- Comprueba el PIN de las palabras y lleva la cuenta: `ok`, `incorrecto`, `bloqueado` o `sin_pin`. No lanza error:
-- un error desharía la cuenta de fallos.
create function public.evento_pin_de_palabras(p_evento text, p_pin text) returns text
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions;
begin
  select * into e from public.event_editions where id = p_evento for update;
  if not found or e.palabras_pin_hash is null then
    return 'sin_pin';
  end if;
  if e.palabras_pin_bloqueado_hasta is not null and now() < e.palabras_pin_bloqueado_hasta then
    return 'bloqueado';
  end if;
  if encode(sha256(convert_to(coalesce(p_pin, ''), 'UTF8')), 'hex') = e.palabras_pin_hash then
    update public.event_editions set palabras_pin_fallos = 0, palabras_pin_bloqueado_hasta = null where id = p_evento;
    return 'ok';
  end if;
  update public.event_editions
     set palabras_pin_fallos = palabras_pin_fallos + 1,
         palabras_pin_bloqueado_hasta = case when (palabras_pin_fallos + 1) % 5 = 0
                                             then now() + interval '5 minutes' end
   where id = p_evento;
  return 'incorrecto';
end;
$$;

revoke all on function public.evento_pin_de_palabras(text, text) from public, anon, authenticated;

-- La respuesta a un PIN de las palabras que no vale, para devolverla tal cual.
create function public.evento_pin_de_palabras_rechazado(p_resultado text) returns jsonb
language sql
immutable
set search_path = ''
as $$
  select jsonb_build_object('error', case p_resultado
    when 'bloqueado' then 'Demasiados intentos: espera unos minutos.'
    when 'sin_pin' then 'Aún no hay PIN para las palabras: créalo primero.'
    else 'PIN incorrecto' end);
$$;

revoke all on function public.evento_pin_de_palabras_rechazado(text) from public, anon, authenticated;

-- Lo que la página de las palabras necesita saber antes de pedir nada: si ya hay PIN y si aún no ha empezado.
create function public.estado_de_las_palabras(p_evento text) returns jsonb
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
  return jsonb_build_object(
    'ahora', now(),
    'titulo', e.titulo,
    'empieza_en', e.empieza_en,
    'antes', e.empieza_en is null or now() < e.empieza_en,
    'tiene_pin', e.palabras_pin_hash is not null
  );
end;
$$;

-- Crea el PIN de las palabras: cuatro cifras, solo si aún no hay uno y antes de la hora de empezar.
create function public.crear_pin_de_palabras(p_evento text, p_pin text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  e public.event_editions;
begin
  select * into e from public.event_editions where id = p_evento for update;
  if not found then
    raise exception 'evento desconocido' using errcode = '22023';
  end if;
  if not (e.empieza_en is null or now() < e.empieza_en) then
    raise exception 'El evento ya ha empezado: las palabras ya no se ven aquí.' using errcode = '22023';
  end if;
  if e.palabras_pin_hash is not null then
    raise exception 'Ya hay un PIN para las palabras.' using errcode = '22023';
  end if;
  if coalesce(p_pin, '') !~ '^[0-9]{4}$' then
    raise exception 'El PIN tiene que tener cuatro cifras.' using errcode = '22023';
  end if;
  update public.event_editions
     set palabras_pin_hash = encode(sha256(convert_to(p_pin, 'UTF8')), 'hex'), palabras_pin_fallos = 0,
         palabras_pin_bloqueado_hasta = null
   where id = p_evento;
  return jsonb_build_object('ok', true);
end;
$$;

-- Las palabras, con el PIN y antes de la hora de empezar.
create function public.ver_palabras(p_evento text, p_pin text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  pin text := public.evento_pin_de_palabras(p_evento, p_pin);
begin
  if pin <> 'ok' then
    return public.evento_pin_de_palabras_rechazado(pin);
  end if;
  return public.palabras_del_evento(p_evento);
end;
$$;

-- Cambia una palabra, con el PIN y antes de la hora de empezar (las reglas, las de `cambiar_palabra`).
create function public.guardar_palabra(p_evento text, p_pin text, p_orden integer, p_palabra text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  pin text := public.evento_pin_de_palabras(p_evento, p_pin);
begin
  if pin <> 'ok' then
    return public.evento_pin_de_palabras_rechazado(pin);
  end if;
  return public.cambiar_palabra(p_evento, p_orden, p_palabra);
end;
$$;

revoke all on function public.estado_de_las_palabras(text), public.crear_pin_de_palabras(text, text),
  public.ver_palabras(text, text), public.guardar_palabra(text, text, integer, text)
  from public, anon, authenticated;
grant execute on function public.estado_de_las_palabras(text), public.crear_pin_de_palabras(text, text),
  public.ver_palabras(text, text), public.guardar_palabra(text, text, integer, text)
  to anon, authenticated;
