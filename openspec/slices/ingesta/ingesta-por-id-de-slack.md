---
slice: ingesta-por-id-de-slack
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
  - identidad
  - resultados
tests_root: tests/slices/ingesta-por-id-de-slack/
blocked: null
---

# Un resultado nuevo se guarda bajo el identificador de quien lo publicó

**Actor:** sistema (cron horario)
**Trigger:** la ingesta que lee el canal cada hora

## Contexto

La migración de [[identidad-canonica-de-jugador]] dejó las 1524 filas del histórico con el identificador
de Slack en la columna de identidad. **El extractor sigue emitiendo el nombre mostrado**, así que cada
ejecución horaria vuelve a crear identidades de nombre junto a las canónicas: el jugador se parte en dos
otra vez y el ranking mensual lo cuenta mal.

Este slice cierra el círculo. Va **después** de la migración y no antes: al revés, las filas de la ventana
de reprocesado se habrían duplicado — 32 de las 40 últimas, medido.

## Trigger técnico

`extract_slack.py` lee los últimos 50 mensajes y los pasa por tubería a `add_results.py`. Hoy la línea que
los une lleva el nombre mostrado; pasa a llevar **el identificador y el nombre**, porque el extractor ya
consulta el directorio del workspace y tiene los dos a mano.

## Comportamiento observable

### resultado-guarda-el-identificador
**WHEN** se procesa un mensaje de resultado
**THEN** la fila guarda el identificador de Slack de quien lo publicó como identidad, no su nombre.

### nombre-mostrado-se-guarda-legible
**WHEN** se guarda una fila
**THEN** el nombre del jugador sigue siendo legible, porque es lo que muestra la web publicada: nunca el
identificador crudo.

### etiqueta-acordada-gana-al-handle
**WHEN** el nombre que una persona muestra en Slack es un handle (`carlos.h`) y el grupo tiene una etiqueta
acordada para ella
**THEN** se guarda la etiqueta, no el handle.

### renombre-no-crea-jugador-nuevo
**WHEN** un jugador cambia su nombre en Slack y publica un resultado nuevo
**THEN** el resultado va al mismo jugador que sus resultados anteriores.

### reprocesar-la-ventana-no-duplica
**WHEN** el mismo mensaje se procesa dos veces, como ocurre cada hora con la ventana de 50
**THEN** sigue habiendo una sola fila para ese jugador y ese puzzle.

### la-ventana-se-mide-en-dias-no-en-mensajes
**WHEN** se decide qué mensajes leer del canal
**THEN** el corte es **una fecha**, no un número de mensajes: se leen todos los del canal desde hace N días.

Medido sobre el histórico: el canal tiene una mediana de 10 mensajes al día y un máximo de 27, así que una
ventana de 50 mensajes cubre cinco días **de media** y **no cubre tres** en la peor racha, que son 52
mensajes. Contar mensajes hace que la cobertura dependa de lo hablador que esté el grupo, que es justo lo
contrario de lo que se quiere de una ventana de seguridad.

### la-ventana-pagina-hasta-cubrir-los-dias
**WHEN** los mensajes de la ventana no caben en una página de la API
**THEN** se piden las páginas necesarias hasta llegar al corte, en lugar de quedarse con la primera.

### la-fecha-de-corte-entra-por-parametro
**WHEN** se calcula el corte de la ventana
**THEN** la fecha actual entra por parámetro y no se lee del reloj dentro del cálculo, de modo que el corte
es verificable con una fecha fija (§10).

### un-fallo-a-mitad-de-la-paginacion-no-emite-un-lote-a-medias
**WHEN** la API falla al pedir una página que no es la primera
**THEN** la ejecución falla en lugar de emitir los mensajes que sí llegaron: un lote incompleto se ingiere
sin ruido y deja huecos que nadie ve, mientras que un fallo lo reporta el workflow.

### mensaje-sin-autor-no-inventa-identidad
**WHEN** un mensaje de resultado no trae autor
**THEN** no se guarda con una identidad inventada; se descarta y se declara en el recuento.

### patron-se-sigue-capturando
**WHEN** el mensaje trae la cuadrícula de emojis
**THEN** el patrón se guarda igual que antes de este cambio, aunque el formato de la línea haya cambiado.

## Estado después

Las filas nuevas son indistinguibles de las canonizadas: identificador en la identidad, nombre legible en
el nombre. La migración de identidad se vuelve innecesaria a partir de aquí — sigue siendo idempotente, y
ejecutarla no encontraría nada que arreglar.

## Edge cases

- **Alguien fuera del directorio**: `users.list` devuelve también a los desactivados, así que el caso real
  es un usuario que la API no devuelva. Sin nombre legible se guarda el identificador como nombre: es feo
  pero no pierde el resultado, y el jugador sigue siendo el correcto.
- **El nombre cambia entre dos ejecuciones**: las filas viejas conservan el nombre viejo y las nuevas
  llevan el nuevo. La identidad no se mueve, que es lo que importa para contar. Que la web muestre un solo
  nombre por jugador es cosa de la v2.0, que lo resolverá del identificador al pintar.
- **Un mensaje editado** cambia su texto pero no su autor: el upsert por identificador y puzzle lo
  actualiza en lugar de duplicarlo.

## Fuera de alcance, y por qué

**No se reescribe el `player_name` del histórico.** 18 de los 21 jugadores ya lo tienen igual a su nombre
de Slack, y los otros tres son etiquetas acordadas. Uniformarlo cambiaría lo que muestra la v1 sin
necesidad ([ADR 0005](../../decisions/0005-hosting-y-convivencia-v1-v2.md)).

**No se capturan los resultados publicados en hilos** (Fase 4.1 del roadmap) ni se amplía la ventana de 50
mensajes (Fase 4.2). Son fallos reales de la ingesta, con su propio slice cada uno.

## Slices compañeros

- [[identidad-canonica-de-jugador]] — la migración del histórico. **Va antes que este slice.**
- [[captura-del-patron]] — el patrón se sigue capturando; el escenario `patron-se-sigue-capturando`
  protege esa regresión al cambiar el formato de la línea.
