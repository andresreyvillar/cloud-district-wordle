# Context snapshot — 2026-08-08 19:10

## 1 · Session Goal

Cerrar la Fase 5 completa (ranking de figuras) y la 6.2 (medallas de figuras) del roadmap de la v2.0,
mergear la rama `wordle_2` a `main` para detener la corrupción diaria de identidades, y dejar el resumen
diario de Slack rediseñado y listo para que el grupo empiece a usar la v2 el lunes 10 de agosto.

El detonante urgente apareció a mitad de sesión: **diez jugadores estaban partidos en dos identidades**
desde el 2026-08-03 porque el cron de `main` escribía el nombre mostrado en la columna del identificador
de Slack, y cada día que pasaba se desviaban 4-5 partidas más por persona.

## 2 · Current Status

**Todo desplegado y verificado en producción. `main` en sync con `origin`. Nada pendiente de commitear**
(salvo `.DS_Store`, que está en `.gitignore` pero fue commiteado en el commit inicial y siempre aparece
como modificado — ignorar).

### Commits de la sesión, en orden

```
b48a8b2  fix(hosting): two production-only bugs in the /2/ routing
09336aa  feat(figuras): the season snapshot publishes the figure album          ← 5.3
80eddcd  feat(figuras): the album, on screen                                    ← 5.4
b68ec4a  feat(figuras): five medals that look at the drawing                    ← 6.2
98c8148  feat(publicacion): the daily message tells the day…                    ← 5.5
5178fdc  feat(publicacion): the summary jokes about the day                     ← 5.6 (determinista)
2b6d447  feat(publicacion): the composed summary ships switched off
a825332  merge: the v2 pipeline, with the channel message unchanged             ← MERGE a main
73fe05d  feat(figuras): /hoy shows what each player drew today
d949ed8  style(v2): player names read as buttons, not as hyperlinks
98acd2a  style(v2): one design for header and body, and a wider page
86bd467  feat(publicacion): the daily summary, redesigned around ties and timing
621849c  feat(publicacion): the daily image is the headline, not the whole page
145b25f  chore(publicacion): the workflow can turn the composed summary on
```

### Ficheros creados

- `/Users/andres/Projects/Personal/wordle-stats/tools/album.py` — álbum de figuras por temporada, y
  `ultima_jornada` (figuras del día para `/hoy`)
- `/Users/andres/Projects/Personal/wordle-stats/tools/resumen.py` — texto del resumen diario
- `/Users/andres/Projects/Personal/wordle-stats/tools/comentarios.py` — detectores de hechos de la jornada
- `/Users/andres/Projects/Personal/wordle-stats/v2/js/data/album.js` — proyección del álbum para la web
- Slices: `openspec/slices/ranking/clasificacion-de-figuras.md`,
  `openspec/slices/dashboard/album-de-figuras.md`,
  `openspec/slices/estadisticas/medallas-de-figuras.md`,
  `openspec/slices/publicacion/resumen-diario-compuesto.md`,
  `openspec/slices/publicacion/comentarios-de-la-jornada.md`,
  `openspec/slices/estadisticas/figuras-de-la-jornada.md`,
  `openspec/slices/ranking/empates-comparten-puesto.md`
- Change packs en `openspec/changes/`: `feat-clasificacion-de-figuras`, `feat-album-de-figuras`,
  `feat-medallas-de-figuras`, `feat-resumen-diario-compuesto`, `feat-comentarios-de-la-jornada`,
  `feat-figuras-de-la-jornada`, `feat-empates-comparten-puesto`, `feat-comentarios-por-la-hora`,
  `feat-captura-del-titular`, `chore-nombres-como-botones`, `chore-cabecera-unificada`

### Ficheros modificados de peso

- `tools/badges.py` — catálogo de 7 → 12 medallas; umbrales de figuras **remedidos**; los recuentos salen
  del álbum, no de un segundo recuento
- `tools/standings.py` — **empates comparten puesto** (afecta a la web y al mensaje)
- `tools/post_ranking.py` — `temporada_del_resumen()`, `COLUMNAS` con `pattern` y `created_at`,
  `resumen_activo()`, objetivo v2 fotografía `.hero`, guarda de selector inexistente
- `tools/seasons.py` — la instantánea publica `album`
- `tools/materialize_seasons.py` — lee la columna `pattern`
- `tools/local_stack.py` — arreglada una llamada rota a `comentario()`
- `v2/css/styles.css` — cabecera unificada, nombres como botones, ancho 84rem, responsive
- `v2/index.html` — cabecera nueva (marca + nav de píldoras + selector)
- `v2/js/ui/temporada.js` — bloque ÁLBUM DE FIGURAS, `LOGROS` con 12, sin marca duplicada
- `v2/js/ui/jugador.js` / `v2/js/data/dia.js` / `v2/js/ui/hoy.js` — álbum en la ficha, figuras en `/hoy`
- `v2/assets/icons/logros.svg` — `fontanero` → `abstracto`, símbolo nuevo `coleccionista`
- `.github/workflows/post_ranking.yml` — pasa `RESUMEN_COMPUESTO`

### Estado de verificación

- **Suite Python:** 388 tests en verde (`.venv/bin/python3 -B -m pytest`)
- **Suite JS:** 97 tests en verde (`node --test tests/`)
- **Harness:** `python3 -m tools.wslice slice validate` sale 0; todos los packs con `verify gates` OK
- **Producción:** las 8 rutas de `/2/` sin errores de consola ni peticiones ≥400, en 390/768/1440 px y en
  claro y oscuro

### Estado de los datos en producción

- **1553 filas** (eran 1590 antes de reparar). Cuadra: 1502 de la temporada 0 + 51 de agosto.
- **0 filas con nombre en la columna de identidad** — reparación ejecutada con
  `tools/canonical_identity.py`: 8 reescrituras + 29 fusiones, 0 conflictos, ninguna cuadrícula perdida.
- Copia de seguridad previa en
  `/private/tmp/claude-501/-Users-andres-Projects-Personal-wordle-stats/79daadfd-c456-4889-8991-553de30d7da1/scratchpad/backup_previo_a_reparar.json`
  (**se pierde al reiniciar el equipo**; si hace falta conservarla, moverla fuera de `/private/tmp`).

### Variables de repositorio ACTIVAS (`gh variable list`)

```
CAPTURA_OBJETIVO    v2      ← la captura y el enlace apuntan a /2/
RESUMEN_COMPUESTO   1       ← el mensaje lleva marcador, figuras y comentarios
```

## 3 · Pending Tasks

1. **Anunciar la v2 al equipo el lunes 10 por la mañana**, antes de las 19:00, con el enlace completo
   `https://cloud-district-wordle.clouddistrict.workers.dev/2/`. Si se anuncia después, el mensaje del bot
   llega antes que la explicación.
2. **Corregir los ADR que afirman que mergear no publica la web.** Quedó demostrado hoy que **Workers
   Builds SÍ está conectado**: el CSS nuevo estaba en producción al minuto del push, sin `wrangler deploy`.
   Afecta a `openspec/decisions/0003-modelo-de-ramas-y-despliegue.md`,
   `openspec/decisions/0005-hosting-y-convivencia-v1-v2.md` y a `CLAUDE.md` (sección «Modelo de ramas» y
   «Constraints clave»). Es una premisa sobre la que se decidió más de una cosa esta semana.
3. **Decidir si la v2 sustituye a la v1 en la raíz**, y cómo. Hoy `/` sirve la v1 y `/2/` la v2. Dos
   opciones planteadas: redirigir `/` a `/2/` (tres líneas, reversible) o servir la v2 en la raíz y mover
   la v1 a `/1/` (más limpio, rompe enlaces guardados a rutas de la v1). El 1 de septiembre —arranque de
   la temporada 2— es un momento natural.
4. **5.7 `imagen-de-la-obra-del-dia`** — sin proveedor ni credencial de ningún modelo en el entorno.
   Recomendación dada: **descartarla**; cuesta dinero por jornada, no se puede cubrir con tests y el
   resumen ya publica la obra del día con su emoji y su autor.
5. **Las medallas de la temporada 0 se ven infladas**: 13 de 21 jugadores con «Ornitólog@ · legendario» y
   12 con «Arquitect@», porque son 181 jornadas con umbrales calibrados para un mes. Documentado como
   distorsión aceptada (la misma que ya tenían Fondista y Verdugo). Si molesta al anunciar, ocultar el
   bloque de logros en la temporada 0 sería otro slice.
6. **11 lecciones en estado `pendiente`** en `docs/lecciones.md`. La mayoría esperan probes que consulten
   la base de datos (`row-count` y similares) para que el harness verifique cifras en lugar de creerse un
   texto. Es lo más rentable que queda por hacer: son las que evitan que se repita lo que ha pasado hoy
   tres veces.
7. **Tachar del roadmap dos líneas que ya no aplican**: 0.2 («crear un Worker aparte para la v2» — se
   resolvió con `/2/` en el mismo Worker) y 6.3 («anunciar la medalla recién ganada» — **ya está hecho**:
   `texto_de_medallas` solo anuncia lo ganado en la jornada).
8. **Fase 3 completa (3.2–3.7) sigue bloqueada por el grupo**: podios separados, nota ponderada, rachas,
   mayor remontada, cierre de la etapa el 31 de agosto y ausencias justificadas.

## 4 · Key Decisions & Context

### Plataforma y despliegue

- **Cloudflare Workers Static Assets**, un solo Worker `cloud-district-wordle` sirviendo las dos webs:
  `/` → v1 (assets de la raíz del repo), `/2/` → v2 (assets de `v2/`), repartido por `worker/index.js`.
- **Subdominio de cuenta: `clouddistrict`** (no `andres-rey`). Es de la cuenta, no de cada Worker.
- **Workers Builds ESTÁ conectado**: push a `main` publica la web automáticamente en ~1 minuto. Esto
  contradice la documentación del repo (ver tarea pendiente 2).
- Los dos cron son GitHub Actions y corren desde `main`:
  `update_stats.yml` cada hora en punto, `post_ranking.yml` a las **17:00 UTC de lunes a viernes**.
- Credenciales en `.env` (local) y en secrets del repo: `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`,
  `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`. **No hay credencial de ningún modelo.**

### Decisiones de producto tomadas esta sesión, todas medidas antes de fijarlas

- **Puntuación del álbum = tasa de figuras por partida clasificada, mínimo 5 partidas.** Cuatro criterios
  medidos: el recuento absoluto corona a quien más juega; el ponderado por rareza corona al segundo de la
  tabla de puntuación (anula el propósito del eje); solo-loros corona a quien tuvo suerte. Con mínimo 3
  gana alguien con 100% de tres partidas; con 5, 8 y 10 el líder es el mismo.
- **Una partida sin patrón no cuenta como abstracta.** Sale del denominador; la cobertura se publica aparte.
- **Umbrales de medallas de figuras REMEDIDOS** (los del brief eran del clasificador desmentido):
  Ornitólog@ 5 loros (3,3%), Arquitect@ 4 geométricos (1,6%), Florista 11 flores (11,5%), Abstract@ 7
  abstractos (23,0%), Coleccionista las cuatro (41,0%).
- **Empates comparten puesto** en el marcador y en el álbum. Medido: el **62%** de las jornadas que cuentan
  tiene empate en la mejor nota. Fue un **cambio de regla declarado como `MODIFIED`**: el escenario
  `empate-se-rompe-por-participacion` decía que el desempate daba mejor puesto; ahora ordena la lista.
- **Disparadores de comentarios, por frecuencia medida sobre 186 jornadas**: clavada 0,01 ·
  rezagado-con-suerte 0,06 · sospechoso 0,06 · rajado 0,18 · rezagado 0,24 · sembrado 0,24 ·
  no-inspirado 0,24. La notabilidad ordena por esa frecuencia.
- **La captura del resumen es `.hero`** (titular + podio), no la página entera: el texto ya lleva el
  marcador y el álbum.

### Comportamientos NO OBVIOS descubiertos (lo más caro de reconstruir)

- **JSONB no conserva el orden de las claves.** Postgres las devuelve ordenadas por longitud y luego
  alfabéticamente. Por eso el catálogo de categorías viaja como **lista**, no como diccionario: con un
  diccionario, `abstracto` (9 letras) llegaba antes que `geometrico` (10) y la web pintaba el ruido entre
  las figuras que puntúan. **Ningún test de Python lo cazaba**: allí el dict conserva el orden de inserción.
- **`created_at` sirve como hora de publicación aproximada** (margen de hasta una hora, lo que tarda el
  cron), **salvo en 268 filas del backfill** insertadas todas el 2026-02-02. Por eso solo se usa si la
  marca cae el mismo día que el puzzle.
- **La misma causa raíz apareció TRES veces**: derivar la temporada del prefijo de la fecha en lugar de
  `seasons.temporada_de`. En `badges._de_la_temporada`, en `v2/js/data/temporada.js` y en
  `post_ranking.seccion_de_medallas`. En este último funcionaba **por casualidad** porque agosto de 2026 es
  a la vez el mes y el identificador de temporada.
- **`.distribucion .barra` heredaba el relleno de `.barra`** (la tira de cifras de la temporada) porque
  comparten nombre de clase. Ya se neutralizaban fondo y borde, pero no el relleno.
- **`main { padding: 2rem 0 }` reinicia el `padding-inline`** del contenedor. Usar `padding-block`.
- **`var(--liga-tinta)` se invierte con el tema oscuro**: sobre el verde de la liga deja el texto casi
  invisible. Para texto sobre verde va la tinta fija `#14072B`, como hace `.pixel.resalte`.
- **El primer `</svg>` del sprite está dentro de un comentario** de la cabecera. Insertar un símbolo
  cortando por él rompe el fichero y deja las doce tarjetas sin icono — con el test en verde, porque
  buscaba la cadena y estaba comentada.
- **zsh no separa en palabras las variables sin comillas**, y las comillas invertidas dentro de un string
  de Python en un `-c` las interpreta el shell. Usar heredocs `<<'PY'` con cuidado o ficheros.

### Reglas de trabajo confirmadas por el dueño

- **La v2 no es pública todavía**: los cron siguen siendo los de la v1 y la raíz sirve la v1. Dos
  interruptores gobiernan el corte, ambos ya activados: `CAPTURA_OBJETIVO=v2` y `RESUMEN_COMPUESTO=1`.
- **Las medallas NO están tras interruptor**: son comportamiento especificado de un slice aceptado.
  Intentar apagarlas rompía dos tests y se revirtió.
- Protocolo: cada comportamiento observable necesita slice + deltas + tests antes que código, gate de
  mutación con 1-3 errores deliberados, y **prohibido debilitar un test para ponerlo verde** — un test que
  falla por un cambio de regla se actualiza declarando el cambio como `MODIFIED` en el delta.

## 5 · Resume Prompt

```
Read context-snapshot-2026-08-08-1910.md in the repository root first — it has the full state of the
previous session.

Then do pending task 2: correct the ADRs that claim merging to main does not publish the web. It was
proven false today — Workers Builds is connected and the new CSS was live in production about a minute
after the push, with no `wrangler deploy` run. Update
openspec/decisions/0003-modelo-de-ramas-y-despliegue.md,
openspec/decisions/0005-hosting-y-convivencia-v1-v2.md and the "Modelo de ramas" and "Constraints clave"
sections of CLAUDE.md so they state the real mechanism, and record how it was verified. This matters
because several decisions this week rested on the wrong premise.

Do not deploy anything and do not touch the production database. Follow the repo protocol: this is a
documentation fix, so no slice is needed, but leave the change staged and let me decide about committing.
```
