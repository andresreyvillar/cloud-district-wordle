-- El evento de prueba: cinco palabras inventadas, una lista de participantes inventados en grupos y un PIN de prueba.
--
-- **No es una migración**: no se aplica sola en ningún sitio. La carga `tools/evento_local.py` en su Postgres
-- desechable (que puede añadir a la lista los nombres de quienes juegan al Wordle, leídos de Supabase al arrancar,
-- sin que pasen por el repositorio). Las palabras, la lista y el PIN del evento real no van al repositorio.
--
-- PIN de prueba: 0000

insert into public.event_editions (id, titulo, pin_hash)
values ('prueba', 'Evento de prueba', encode(sha256(convert_to('0000', 'UTF8')), 'hex'));

insert into public.event_targets (evento, orden, palabra) values
  ('prueba', 1, 'nubes'),
  ('prueba', 2, 'piano'),
  ('prueba', 3, 'campo'),
  ('prueba', 4, 'lunes'),
  ('prueba', 5, 'flora');

insert into public.event_roster (evento, nombre, grupo) values
  ('prueba', 'Participante Uno', 'Grupo 1'),
  ('prueba', 'Participante Dos', 'Grupo 1'),
  ('prueba', 'Participante Tres', 'Grupo 2'),
  ('prueba', 'Participante Cuatro', 'Grupo 2'),
  ('prueba', 'Participante Cinco', 'Grupo 3');
