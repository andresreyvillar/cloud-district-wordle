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
  mapeos: su nombre mostrado dice un jugador y su identificador pertenece a otro. **Este comando no decide
  qué son**: las declara y las deja intactas. Se intentó reatribuirlas al dueño del nombre y fue un error
  que fabricó partidas — el canal demostró que dos correspondían a días en que esa persona no publicó nada
  y una tercera era copia exacta de la cuadrícula de otra jugadora. Y borrarlas por sospecha tampoco vale:
  lo que las delata es el canal, que este cálculo no consulta.
- Cualquier clasificación mensual con umbral de participación **cuenta mal** a quien esté partido en dos,
  porque reparte sus días entre dos jugadores.

Este slice **no cambia la ingesta**. Solo canoniza lo que ya está guardado, y ese orden no es negociable:
si el extractor empezara a emitir identificadores antes de esta migración, las filas de la ventana de
reprocesado se duplicarían — 32 de las 40 últimas, medido.

## Trigger técnico

Un comando manual, repetible sin daño. Resuelve cada nombre mostrado contra el directorio del workspace,
escribe el identificador en las filas que llevan un nombre y fusiona lo que resulte duplicado. Lo que no
puede resolver —atribuciones cruzadas y claves bloqueadas— lo declara y lo deja intacto. Como toda
migración de este repo, exige un ensayo previo.

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

### atribucion-cruzada-se-declara-y-no-se-toca
**WHEN** una fila lleva el identificador de una persona distinta de la que indica su nombre mostrado
**THEN** la fila se declara en el recuento y no se modifica: ni se reatribuye ni se elimina.

### clave-ocupada-se-declara-y-no-se-fuerza
**WHEN** la identidad que hay que escribir en una fila choca con la de otra fila del mismo puzzle
**THEN** si la otra fila va a desaparecer por fusión se escribe después de borrarla, y si no se mueve la
escritura se omite: la fila conserva su identidad y el informe la declara bloqueada.

### nombre-compartido-lo-desempata-quien-juega
**WHEN** dos personas del workspace comparten una forma del nombre
**THEN** se resuelve a favor de la que ha publicado en el canal, y si las dos han publicado la forma se
declara ambigua y sus filas quedan como no resueltas.

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

Todas las filas resolubles guardan un identificador de Slack en lugar de un nombre. El censo baja **por una
sola causa declarada: las fusiones**, y una fusión exige que las dos filas coincidan en jugador, puzzle y
puntuación. Nada se elimina por otro motivo. El comando informa de cuántas resuelve, cuántas fusiona y
cuántas deja sin tocar por cruzadas o bloqueadas, y ese informe es la única forma legítima de explicar el
censo nuevo.

`player_name` sigue conteniendo el nombre mostrado, así que la web publicada no nota nada
([ADR 0005](../../decisions/0005-hosting-y-convivencia-v1-v2.md)).

## Edge cases

- **Alguien que ya no está en el workspace**: **sí resuelve**. `users.list` sigue devolviendo el nombre y el
  identificador de los usuarios desactivados, y un identificador de Slack no se reasigna nunca. Tres de los
  jugadores del histórico están en este caso, con 110 filas entre los tres: filtrarlos las dejaba todas sin
  resolver, incluido el renombre que este slice viene a arreglar.
- **Dos personas con el mismo nombre mostrado**: ocurre de verdad, en dos formas. Lo desempata quién ha
  publicado en el canal, que es la señal pertinente porque quien está en la tabla es quien juega. Sin
  desempate, la forma se declara ambigua.
- **Una etiqueta que no existe en Slack**: tres nombres de la tabla son etiquetas escritas a mano y no
  resuelven contra el workspace. Van en un mapeo curado que se aplica **como relleno, nunca por encima** de
  `users.list`: ese diccionario hereda un error de etiquetado, y aplicado como override atribuiría 111
  filas a otra persona.
- **Reejecución**: idempotente por `id-existente-no-se-toca`.

## Slices compañeros

- [[ingesta-por-id-de-slack]] (TBD) — el extractor emite el identificador. **Va después de este slice**,
  nunca antes.
- [[backfill-de-patrones]] — sus 305 filas no resueltas son exactamente este problema; tras esta
  migración, volver a ejecutarlo recupera el resto.
