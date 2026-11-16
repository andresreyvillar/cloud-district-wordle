# feat-frase-del-evento

## Why

La empresa organiza un evento de una mañana y quiere un juego para todos con las reglas de «La frase del día» de
lapalabradeldia.com: cada frase está tapada y se destapa con palabras de cinco letras, desde el móvil y sin cuenta,
contra el reloj. Las frases se liberan a la vez para todos, para que no se filtren, y al final hay un ranking.

## What Changes

- **Base de datos (aditiva):** `event_editions`, `event_phrases`, `event_players`, `event_plays`, `event_guesses` y
  `event_words` (el diccionario), que la clave pública no lee ni escribe. Todo pasa por funciones `SECURITY
  DEFINER`: `unirse_al_evento`, `estado_del_evento`, `mi_partida_del_evento`, `empezar_frase`, `intentar_palabra`,
  `empezar_evento`, `terminar_evento` y `ranking_del_evento`.
- **Diccionario:** `tools/diccionario_evento.py` saca las palabras de cinco letras del diccionario ortográfico de
  LibreOffice (RLA-ES, norma de la RAE, triple licencia GPL/LGPL/MPL) y genera la migración y la lista de la web.
- **Web:** dos rutas fuera de la navegación, `/evento` (el participante) y `/evento/pantalla` (el proyector),
  con su propia hoja de estilos (marca de Cloud District, preparada para el tema del evento).
- **Local:** `tools/evento_local.py` levanta un Postgres desechable con el evento de prueba y emula `/rest/v1/rpc`,
  servido en la red local para probar desde el móvil sin tocar Supabase.

## Decisiones

| Decisión | Por qué |
|---|---|
| Reglas de «La frase del día»: 5 palabras de 5 letras, verde destapa en toda la frase, se gana al destaparla (dueño) | Es el juego que el dueño pidió; la primera versión, que escribía la frase entera, no lo era. |
| Diccionario propio desde RLA-ES (dueño: «a partir de la RAE») | La lista de la RAE no tiene licencia para copiarla y el repo es público; RLA-ES sigue su norma y es libre. |
| La frase nunca sale entera del servidor hasta terminar el evento | La web es estática y el repositorio público: lo que viaja al navegador se ve. |
| Cronómetro desde cero al pulsar Empezar, sin pausa y sin máximo (dueño) | Pausar al cerrar dejaría pensar o preguntar con el reloj parado. |
| Frases liberadas cada intervalo, jugables hasta que el presentador termina (dueño: sin tiempo máximo) | Todos juegan la misma a la vez; el final lo decide la sala. |
| Ranking: más frases resueltas y, a igualdad, menos tiempo total (dueño) | Sin puntos: con 100-120 personas, los tiempos en ms no empatan. |
| Una perdida suma tiempo y una a medias no (dueño, con el incentivo a la vista) | Así se acordó; a quien va a perder le conviene no gastar la quinta palabra. |
| Palabras idempotentes por número de intento | Con la red de una sala llena, se pierden respuestas; reenviar no puede gastar otra palabra. |
| Nombre único + token por móvil, sin login; tope de 500 | Sin cuentas no se puede blindar más; un duplicado de incógnito se ve en el ranking. |
| Apariencia en una hoja propia con variables | El tema del evento está por decidir. |

## Out of Scope

- Código QR en la pantalla (se genera fuera; la pantalla enseña la dirección).
- Reiniciar o retrasar el evento desde la web: se hace desde Supabase.
- Ranking en vivo para el presentador.
- Las frases reales y el PIN real: se cargan por SQL fuera del repositorio.

## Impact

Tablas nuevas, sin tocar `wordle_results` ni las instantáneas. Mergear publica las rutas `/evento` en la web;
sin un evento cargado en la base de datos, enseñan que no hay evento. Toca RLS y funciones con escritura
pública: la Fase 4 incluye revisión de seguridad.
