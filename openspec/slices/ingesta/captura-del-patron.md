---
slice: captura-del-patron
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 * * * * — workflow update_stats.yml: extract_slack.py | add_results.py"
events:
  emits: []
  consumes: []
specs:
  - ingesta
  - resultados
tests_root: tests/slices/captura-del-patron/
blocked: null
---

# El sistema conserva el dibujo de cada resultado

**Actor:** sistema (workflow horario)
**Trigger:** la ejecución programada que lee el canal y escribe en la tabla

## Contexto

Cada resultado que un jugador publica en el canal trae dos cosas: la línea con el número de puzzle y
los intentos, y **la cuadrícula de emojis** que muestra el camino hasta la solución. Hoy la ingesta se
queda solo con la primera: la fila persiste `raw_text = "La palabra del día #1671 5/6"` y la cuadrícula
se descarta.

Esa cuadrícula es el material del ranking de figuras
([brief](../../../docs/context/briefs/ranking-de-figuras.md)): sin ella no hay nada que clasificar. Este
slice no clasifica nada — solo deja de tirar el dato.

Se guarda el **patrón crudo**, no una categoría ya calculada: el clasificador va a recalibrarse, y
guardar solo el veredicto haría irrecuperable el histórico en cada ajuste.

## Trigger técnico

El workflow `update_stats.yml` ejecuta `tools/extract_slack.py | tools/add_results.py` cada hora.

El extractor emite una línea `USER_START|<nombre>|<hora>|<texto>` por mensaje, y el texto de un
resultado **contiene saltos de línea**: la primera línea acompaña al encabezado y las filas de la
cuadrícula llegan después como líneas sueltas. El parser actual las ignora porque no coinciden con la
expresión del resultado.

Formato de las celdas en el canal (verificado): `:large_green_square:` acierto en posición,
`:large_yellow_square:` letra presente, y `:black_large_square:` o `:white_large_square:` letra ausente
— las dos últimas según el tema claro u oscuro de quien publica.

## Comportamiento observable

### patron-se-persiste
**WHEN** un mensaje de resultado incluye su cuadrícula de emojis
**THEN** la fila del resultado queda con el patrón de la cuadrícula almacenado, una fila por intento y
en el mismo orden en que aparece en el mensaje.

### ausentes-se-normalizan
**WHEN** la cuadrícula usa el cuadrado blanco para las letras ausentes y otra usa el negro
**THEN** las dos quedan almacenadas con el mismo símbolo, de modo que dos caminos idénticos producen
patrones idénticos.

### sin-cuadricula-el-resultado-se-registra
**WHEN** un mensaje de resultado no trae cuadrícula
**THEN** el resultado se registra igual y la fila queda sin patrón.

### filas-de-otro-mensaje-no-contaminan
**WHEN** dos resultados llegan seguidos, cada uno con su cuadrícula
**THEN** cada patrón queda asociado al resultado que lo precede, sin mezclar filas entre ellos.

### linea-que-no-es-fila-se-ignora
**WHEN** entre las filas aparece una línea que no son exactamente cinco celdas de cuadrado
**THEN** esa línea no forma parte del patrón.

### reejecucion-mantiene-un-solo-patron
**WHEN** la ejecución programada vuelve a procesar un mensaje ya registrado
**THEN** la fila conserva un único patrón, sin duplicar filas ni concatenar la cuadrícula consigo misma.

### patron-de-fallo-se-guarda
**WHEN** el resultado es un fallo (`X/6`) y por tanto su cuadrícula no termina en una fila de aciertos
**THEN** el patrón se almacena igual, con todas las filas que trae el mensaje.

## Estado después

Las filas nuevas de `wordle_results` llevan el patrón; las anteriores siguen sin él hasta que se ejecute
[[backfill-de-patrones]]. El resto de columnas no cambia: `player_name`, `wordle_id`, `score` y `date`
mantienen exactamente el mismo comportamiento, que es lo que exige la invariante aditiva del
[ADR 0005](../../decisions/0005-hosting-y-convivencia-v1-v2.md).

Ningún consumidor lee todavía la columna nueva: la web v1 no la conoce y el clasificador no existe.

## Edge cases

- **Mensaje editado en Slack**: si alguien corrige su mensaje, la reejecución del cron sobrescribe el
  patrón con el del texto actual. Es el mismo comportamiento que ya tiene el resultado.
- **Cuadrícula con más de seis filas**: no debería ocurrir (el juego permite seis intentos), pero el
  patrón se almacena tal cual llega; el slice no valida la coherencia entre filas y puntuación.
- **Emojis de cuadrado dentro de un mensaje de conversación**: no hay resultado al que asociarlos, así
  que no producen patrón.

## Slices compañeros

- [[backfill-de-patrones]] — recupera los patrones del histórico ya registrado.
- [[clasificacion-de-figuras]] (TBD) — consume el patrón para asignarle una categoría.
