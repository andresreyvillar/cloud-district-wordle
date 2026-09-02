---
slice: temporada-mensual
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 * * * 1-5 — workflow update_stats.yml: materializa la temporada en curso tras ingerir"
events:
  emits: []
  consumes: []
specs:
  - ranking
  - resultados
tests_root: tests/slices/temporada-mensual/
blocked: null
---

# El marcador se reinicia el día 1 de cada mes

**Actor:** sistema (cron horario)
**Trigger:** la ingesta, que tras escribir los resultados recalcula la temporada en curso

## Contexto

Es una de las **dos reglas que el grupo cerró por votación**: 6 a favor y 0 en contra
([fuente](../../../docs/context/sources/2026-08-04-hilo-reglas-temporadas.md)). La otra es que solo cuenten
los días laborables. Todo lo demás del hilo son ideas sin decidir.

Hoy no existe el concepto: el ranking agrega todo el histórico desde el wordle #1419 y no hay forma de mirar
un mes concreto.

**Las temporadas están numeradas desde un límite** (decisión del 2026-08-05): todo lo jugado antes del
`2026-08` es **la temporada 0**, un solo bloque con el histórico, y desde agosto cada mes es una temporada
numerada. Consecuencia aceptada y declarada: el archivo pierde el "quién ganó en marzo" y los seis ganadores
distintos que habría habido tratando cada mes del pasado como temporada propia.

Este slice define **qué es una temporada** y la deja materializada. La clasificación de dentro es
[[clasificacion-de-temporada]] (TBD): aquí no se ordena a nadie.

## Trigger técnico

El cálculo vive en Python y se materializa en una tabla, según el
[ADR 0008](../../decisions/0008-donde-vive-el-calculo.md): el bot y la web tienen que decir lo mismo por
construcción y no por disciplina. El cron horario, después de ingerir, recalcula la instantánea de la
temporada en curso. Las cerradas solo se recalculan con un comando explícito, porque recalibrar el pasado
es una decisión y no un efecto secundario.

## Comportamiento observable

### temporada-es-el-mes-de-la-fecha
**WHEN** un resultado posterior al límite se asigna a una temporada
**THEN** es la del mes de su fecha, así que un resultado del día 1 pertenece ya a la temporada nueva.

### antes-del-limite-todo-es-la-temporada-cero
**WHEN** un resultado es anterior al límite de temporadas
**THEN** pertenece a la temporada 0, sea de qué mes sea, y la temporada 0 aparece como **un solo bloque** y
no como una temporada por mes.

### el-numero-de-orden-se-deriva-del-limite
**WHEN** se pide el número de orden de una temporada
**THEN** el mes del límite es la 1, el siguiente la 2, y la histórica la 0 — derivado del límite, no
almacenado.

### la-temporada-cero-no-imputa
**WHEN** se calcula la clasificación de la temporada 0
**THEN** cada jugador sale con la media de lo que jugó de verdad, sin ausencias imputadas, y la instantánea
declara que no está imputada.

### la-temporada-cero-usa-las-reglas-del-legacy
**WHEN** se calcula la temporada 0
**THEN** cuentan **todas** las jornadas con algún resultado —fines de semana incluidos y sin mínimo de
jugadores por día—, la media es la de las partidas jugadas sin imputar, y hacen falta **cinco** partidas para
clasificar: quien no llega aparece en la tabla pero sin puesto.

Son las reglas que la v1 tenía en vigor cuando se jugó ese periodo, incluido el mínimo de cinco
(`js/script.js`, `MIN_GAMES_FOR_BEST_AVG`). La única desviación es que se agrupa por **identidad** y no por
nombre mostrado: el legacy agrupaba por nombre y eso partía en dos a quien se hubiera renombrado, lo que
habría coronado a la mitad de una identidad.

### solo-los-dias-laborables-forman-la-temporada
**WHEN** se determinan los días que forman una temporada
**THEN** solo entran los de lunes a viernes.

### dia-sin-muestra-no-forma-parte
**WHEN** un día laborable lo juegan menos de cinco personas
**THEN** ese día no forma parte de la temporada, porque su dificultad no calibra nada y penalizaría una
ausencia en un día en que el grupo tampoco jugó.

### temporada-en-curso-se-deriva-de-los-datos
**WHEN** se listan las temporadas
**THEN** la más reciente con resultados consta como en curso y las anteriores como cerradas, sin consultar
el reloj.

### instantanea-queda-materializada
**WHEN** el pipeline materializa una temporada
**THEN** queda una fila con su carga útil y la marca de tiempo del cálculo.

### al-cerrar-un-mes-su-instantanea-se-actualiza
**WHEN** una temporada deja de estar en curso porque empieza la siguiente
**THEN** se rematerializa también ella, no solo la nueva, porque su estado vive dentro de la instantánea y si
nadie la reescribe la web sigue anunciándola como abierta después de cerrar.

### recalcular-actualiza-en-lugar-de-duplicar
**WHEN** se materializa dos veces la misma temporada
**THEN** sigue habiendo una sola fila para ella y su marca de tiempo se actualiza.

### calculo-determinista
**WHEN** se calcula el modelo dos veces sobre los mismos resultados
**THEN** el resultado es idéntico, sin depender del reloj ni del orden de las filas.

## Estado después

Existe una fila por temporada en `season_snapshots` —una para la temporada 0 y una por cada mes desde el
límite— con sus días, sus jornadas y su estado. `wordle_results`
**no se toca**: la instantánea es derivada, y borrarla y recalcularla no pierde nada.

## Edge cases

- **Un mes sin ningún día con muestra suficiente** (agosto, un puente largo) es una temporada **vacía**, no
  una temporada inexistente: se materializa con cero días. Lo contrario haría desaparecer un mes del
  archivo.
- **Un resultado publicado con retraso** se asigna por la fecha del puzzle, no por la del mensaje, así que
  cae en su temporada aunque se publique en la siguiente. Es la propiedad que ya da el ancla de fechas.
- **La instantánea puede quedar rancia** si el cron falla. Este slice registra `updated_at`; avisar al
  lector es cosa de la web ([ADR 0008](../../decisions/0008-donde-vive-el-calculo.md), mitigación
  declarada).

## Fuera de alcance, y por qué

- **La clasificación y el modelo de imputación**: [[clasificacion-de-temporada]] (TBD). Aquí no se ordena a
  nadie ni se imputa nada.
- **Las medallas en la instantánea**: ya están calculadas en Python pero sin materializar. Van con el
  medallero, no aquí.
- **Que la web lea la instantánea**: es el consumidor, y llega con la vista.

## Slices compañeros

- [[clasificacion-de-temporada]] (TBD) — ordena a los jugadores dentro de la temporada que este slice define.
- [[medallas-en-el-resumen-diario]] — comparte el criterio de día laborable y de muestra mínima; los dos
  usan `tools/calendario.py` para no tener dos definiciones.
