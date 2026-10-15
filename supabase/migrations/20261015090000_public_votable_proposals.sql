-- Las propuestas se publican al enviarlas y se votan a favor o en contra.
--
-- Slice: debate-de-reglas. Decisión del dueño (2026-10-15): el primer día llegaron tres propuestas y prefirió
-- verlas todas y que el grupo las vote, en lugar de aprobarlas una a una. Le queda una salida: una propuesta
-- marcada `rechazada` deja de verse y de admitir votos.
--
-- **Aditiva** (ADR 0005): cambia una política de lectura y añade una tabla y una función.

-- `alter` y no `drop` + `create`: el resultado es el mismo, y un `drop` hacía que el conector de Supabase pidiera
-- una confirmación que nunca llegaba («Invalid or expired requestState», tres veces).
alter policy "lectura de las aprobadas" on public.rule_proposals using (estado <> 'rechazada');
alter policy "lectura de las aprobadas" on public.rule_proposals rename to "lectura de las no rechazadas";

create table public.rule_proposal_votes (
  propuesta bigint not null references public.rule_proposals (id) on delete cascade,
  votante text not null,
  voto text not null check (voto in ('a_favor', 'en_contra')),
  updated_at timestamptz not null default now(),
  -- Una persona, un voto por propuesta: votar otra vez lo cambia.
  primary key (propuesta, votante)
);

alter table public.rule_proposal_votes enable row level security;
create policy "lectura publica" on public.rule_proposal_votes for select using (true);
revoke insert, update, delete, truncate on public.rule_proposal_votes from anon, authenticated;

create function public.votar_propuesta(p_propuesta bigint, p_votante text, p_voto text) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
begin
  if p_propuesta is null or p_votante is null or p_voto is null then
    raise exception 'faltan datos del voto' using errcode = '22023';
  end if;

  -- Una rechazada no existe para la web: el mismo error que una que nunca existió.
  if not exists (select 1 from public.rule_proposals where id = p_propuesta and estado <> 'rechazada') then
    raise exception 'propuesta desconocida' using errcode = '22023';
  end if;

  if p_voto not in ('a_favor', 'en_contra') then
    raise exception 'voto desconocido' using errcode = '22023';
  end if;

  if not exists (select 1 from public.wordle_results where slack_user_id = p_votante) then
    raise exception 'jugador desconocido' using errcode = '22023';
  end if;

  insert into public.rule_proposal_votes (propuesta, votante, voto)
  values (p_propuesta, p_votante, p_voto)
  on conflict (propuesta, votante) do update set voto = excluded.voto, updated_at = now();

  return jsonb_build_object('voto', p_voto);
end;
$$;

revoke all on function public.votar_propuesta(bigint, text, text) from public, anon, authenticated;
grant execute on function public.votar_propuesta(bigint, text, text) to anon, authenticated;
