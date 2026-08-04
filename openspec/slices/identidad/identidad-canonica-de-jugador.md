---
slice: identidad-canonica-de-jugador
status: proposed
kind: maintenance
actor: sistema
trigger:
  type: command
  surface: pipeline
  detail: "python3 tools/canonical_identity.py — ejecución manual puntual, previa al cambio del extractor"
events:
  emits: []
  consumes: []
specs:
  - identidad
  - resultados
tests_root: tests/slices/identidad-canonica-de-jugador/
blocked: null
---

# Cada jugador pasa a tener un identificador que no cambia

**Actor:** sistema (ejecución manual)
**Trigger:** comando puntual sobre el pipeline

## Contexto

Hoy la identidad de un jugador es **el nombre que muestra en Slack**: 1235 de las 1533 filas guardan un
nombre en la columna que debería llevar un identificador. Eso tiene tres consecuencias medidas:

- Un jugador que se cambia el nombre **se convierte en dos jugadores**. Ya pasó: dos identidades
  distintas que resuelven al mismo ID de Slack, con las mismas puntuaciones registradas dos veces.
- Ocho filas llevan el identificador de **otra persona**, producto de un cruce en el diccionario de
  mapeos: su nombre mostrado dice un jugador y su identificador pertenece a otro.
- Cualquier clasificación mensual con umbral de participación **cuenta mal** a quien esté partido en dos,
  porque reparte sus días entre dos jugadores.

Este slice **no cambia la ingesta**. Solo canoniza lo que ya está guardado, y ese orden no es negociable:
si el extractor empezara a emitir identificadores antes de esta migración, las filas de la ventana de
reprocesado se duplicarían — 32 de las 40 últimas, medido.

## Trigger técnico

Un comando manual, repetible sin daño. Resuelve cada nombre mostrado contra el directorio del workspace,
escribe el identificador en las filas que llevan un nombre, fusiona lo que resulte duplicado y elimina lo
que resulte de una atribución cruzada. Como toda migración de este repo, exige un ensayo previo.

## Comportamiento observable

### nombre-se-resuelve-a-id
**WHEN** una fila guarda un nombre mostrado como identidad y ese nombre corresponde a una persona del
workspace
**THEN** la fila queda con el identificador de Slack de esa persona.

### id-existente-no-se-toca
**WHEN** una fila ya guarda un identificador de Slack
**THEN** el comando no la modifica, de modo que una segunda ejecución no cambia nada.

### renombre-se-fusiona
**WHEN** dos identidades distintas resuelven al mismo identificador y tienen registrado el mismo puzzle
con la misma puntuación
**THEN** queda una sola fila para ese jugador y ese puzzle.

### atribucion-cruzada-se-elimina
**WHEN** una fila lleva el identificador de una persona distinta de la que indica su nombre mostrado
**THEN** la fila se elimina, porque es producto de un cruce de mapeo y no de una partida jugada.

### nombre-desconocido-se-declara
**WHEN** el nombre de una fila no corresponde a ninguna persona del workspace
**THEN** la fila conserva su identidad actual y el comando la cuenta como no resuelta.

### nombre-mostrado-se-conserva
**WHEN** el comando escribe el identificador de una fila
**THEN** su nombre mostrado no cambia, porque es la columna que lee la web publicada.

### ensayo-no-escribe
**WHEN** el comando se ejecuta en modo ensayo
**THEN** produce el mismo recuento que produciría la ejecución real, sin modificar ninguna fila.

## Estado después

Todas las filas resolubles guardan un identificador de Slack en lugar de un nombre. El número de partidas
por jugador cambia **solo** por las dos causas declaradas: las fusiones de un renombre (la misma partida
contada una vez en lugar de dos) y las eliminaciones por atribución cruzada. El comando informa de las
dos cantidades, y esa es la única forma legítima de que el censo se mueva.

`player_name` sigue conteniendo el nombre mostrado, así que la web publicada no nota nada
([ADR 0005](../../decisions/0005-hosting-y-convivencia-v1-v2.md)).

## Edge cases

- **Alguien que ya no está en el workspace**: su nombre no resuelve y sus filas quedan como no resueltas.
  No se borran: un jugador que se fue jugó de verdad.
- **Dos personas con el mismo nombre mostrado**: el directorio devuelve una sola, así que la resolución
  sería ambigua. No se ha observado hoy, y si apareciese el comando debe declararlo en lugar de elegir `?`.
- **Reejecución**: idempotente por `id-existente-no-se-toca`.

## Slices compañeros

- [[ingesta-por-id-de-slack]] (TBD) — el extractor emite el identificador. **Va después de este slice**,
  nunca antes.
- [[backfill-de-patrones]] — sus 305 filas no resueltas son exactamente este problema; tras esta
  migración, volver a ejecutarlo recupera el resto.
