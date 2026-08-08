---
slice: <slug-kebab-unico>
status: proposed          # proposed | shipped | deprecated | blocked
kind: action              # action | reaction | scheduled | maintenance | failure
actor: <jugador|grupo|sistema>
trigger:
  type: <ui|cron|command>
  surface: <web|pipeline>
  detail: "<pantalla / comando / schedule que dispara el comportamiento>"
events:
  emits: []               # eventos que emite
  consumes: []            # eventos que consume
specs:                    # TODOS los dominios (capabilities) que cruza end-to-end
  - <capability>
tests_root: tests/slices/<slug>/
blocked: null             # { reason, since, by } si está pausado
---

# <Título del comportamiento observable>

**Actor:** <quién lo dispara>
**Trigger:** <qué lo dispara>

## Contexto

<Qué intenta conseguir el actor y por qué. 2-3 párrafos máximo.>

## Trigger técnico

<Pantalla, comando o schedule exacto. Datos de entrada relevantes.>

## Comportamiento observable

### <slug-escenario-1>
**WHEN** <condición precisa>
**THEN** <efecto observable y verificable>

### <slug-escenario-2>
**WHEN** ...
**THEN** ...

## Estado después

<Filas de la tabla, mensajes publicados, efectos externos, estado de la UI.>

## Edge cases

<Idempotencia, reejecución, días sin datos, entradas malformadas.>

## Slices compañeros
- [[<slug-relacionado>]] — <relación>
