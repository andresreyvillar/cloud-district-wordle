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

Es **lo único que el grupo cerró por votación**: 6 a favor y 0 en contra
([fuente](../../../docs/context/sources/2026-08-04-hilo-reglas-temporadas.md)). Todo lo demás del hilo son
ideas sin decidir.

Hoy no existe el concepto: el ranking agrega todo el histórico desde el wordle #1419 y la pregunta "¿quién
ganó en marzo?" no tiene dónde vivir. Aplicando temporadas mensuales al histórico existente hay **9
temporadas cerradas**, así que el archivo no es una promesa: es contenido desde el primer día.

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
**WHEN** un resultado se asigna a una temporada
**THEN** es la del mes de su fecha, así que un resultado del día 1 pertenece ya a la temporada nueva.

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

### recalcular-actualiza-en-lugar-de-duplicar
**WHEN** se materializa dos veces la misma temporada
**THEN** sigue habiendo una sola fila para ella y su marca de tiempo se actualiza.

### calculo-determinista
**WHEN** se calcula el modelo dos veces sobre los mismos resultados
**THEN** el resultado es idéntico, sin depender del reloj ni del orden de las filas.

## Estado después

Existe una fila por temporada en `season_snapshots` con sus días, sus jornadas y su estado. `wordle_results`
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
