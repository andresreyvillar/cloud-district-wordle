-- La votación anti-spoilers pregunta por la consecuencia, no por la norma.
--
-- Slice: debate-de-reglas. Dar pistas ya está prohibido; lo que el grupo decide es qué pasa cuando alguien lo
-- hace. La opción «solo prevención» era, en la práctica, no hacer nada (observación del dueño, 2026-10-14), y se
-- sustituye por la consecuencia que faltaba: sancionar solo a quien da la pista.
--
-- Se aplicó sin votos emitidos. Aun así, un voto a una opción que desaparece se borraría: no puede quedar
-- contando para algo que ya no está en la papeleta.

update public.rule_polls
   set titulo = 'Cuando alguien da una pista de la palabra, ¿qué hacemos?',
       descripcion = 'Dar pistas ya está prohibido; la duda es la consecuencia. El 14 de octubre, tras un '
         || 'comentario con una pista evidente, la jornada se resolvió bastante mejor a partir de las 10:00. Medido '
         || 'sobre 211 jornadas, publicar tarde no da ventaja por sí solo: la ventaja aparece el día de la pista.',
       opciones = '[
         {"id": "anular", "texto": "Anular la jornada: ese día no cuenta para nadie, y quien dio la pista se lleva un X/6"},
         {"id": "sancionar", "texto": "Sancionar solo a quien da la pista: su resultado del día cuenta como X/6 y el resto cuenta normal"},
         {"id": "cortar", "texto": "Anular lo publicado después: los resultados publicados tras la pista no cuentan, y quien la dio se lleva un X/6"},
         {"id": "nada", "texto": "No hacer nada: se le afea en el canal y ya está"}
       ]'::jsonb
 where id = 'anti-spoilers';

delete from public.rule_votes
 where votacion = 'anti-spoilers' and opcion not in ('anular', 'sancionar', 'cortar', 'nada');
