# Deltas de `estadisticas` — feat-comentarios-de-la-jornada

## ADDED Requirements

### Requirement: Los hechos notables de una jornada se detectan, no se narran

Una jornada produce **hechos**: quién resolvió muy rápido un día duro, quién quedó muy por encima o por
debajo de la media del grupo, y quién no apareció el día difícil.

Un hecho es un dato —qué clase, quién y con qué cifra—, **no una frase**. Esa separación es lo que permite
verificar la detección con tests y cambiar después quién redacta sin tocarla.

Los umbrales están **calibrados por frecuencia** sobre el histórico: un hecho que ocurre a diario no es
notable. Y el de día difícil se **reutiliza** del catálogo de medallas: no puede significar dos cosas.

Una jornada **sin muestra suficiente** no produce hechos: con pocos jugadores la media del día no dice nada
del día sino de quién apareció.

Las ausencias se miden contra **quien juega esa temporada**, no contra quien jugó alguna vez.

#### Scenario: los hechos son datos, no frases
- GIVEN una jornada con resultados notables
- WHEN se detectan los hechos
- THEN cada hecho identifica su clase, su protagonista y su cifra, sin texto redactado

#### Scenario: sin muestra no hay hechos
- GIVEN una jornada con menos jugadores de los que hacen falta para calibrar la media
- WHEN se detectan los hechos
- THEN no se detecta ninguno

#### Scenario: una persona produce un solo hecho
- GIVEN alguien que cumple más de una condición el mismo día
- WHEN se detectan los hechos
- THEN se queda con el más notable

#### Scenario: las ausencias son de la temporada en curso
- GIVEN alguien que jugó en una temporada anterior y no en esta
- WHEN se detectan las ausencias de un día difícil
- THEN no se le cuenta como ausente

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py
