-- El evento de prueba: frases inventadas, ventanas de 10 minutos y un PIN de prueba.
--
-- **No es una migración**: no se aplica sola en ningún sitio. La carga `tools/evento_local.py` en su Postgres
-- desechable. Las frases y el PIN del evento real no van al repositorio: se cargan por SQL en Supabase.
--
-- PIN de prueba: prueba-local

insert into public.event_editions (id, titulo, intervalo_minutos, pin_hash)
values ('prueba', 'Evento de prueba', 10, encode(sha256(convert_to('prueba-local', 'UTF8')), 'hex'));

insert into public.event_phrases (evento, orden, frase) values
  ('prueba', 1, 'Más vale tarde que nunca'),
  ('prueba', 2, '¿Quién dijo miedo?'),
  ('prueba', 3, 'El año que viene, más'),
  ('prueba', 4, 'Poco a poco se llega lejos'),
  ('prueba', 5, 'Hoy por ti, mañana por mí');
