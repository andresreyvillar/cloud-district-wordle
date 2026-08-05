# Deltas de `dashboard` — feat-reglas-explicadas

## ADDED Requirements

### Requirement: Las reglas que se aplican son legibles desde la web

Existe una vista en `/reglas` que explica **todas** las reglas del juego, agrupadas por eje. Cada regla dice
qué hace, **por qué existe** y en qué estado está.

Una regla sin motivo se lee como arbitrariedad, así que el motivo no es adorno: es parte del requisito.

#### Scenario: las reglas se agrupan por eje
- GIVEN el catálogo de reglas
- WHEN el grupo abre la página
- THEN las ve agrupadas por eje y no como una lista plana

#### Scenario: cada regla explica por qué existe
- GIVEN cualquier regla del catálogo
- WHEN se muestra
- THEN incluye su motivo, no solo su enunciado

#### Scenario: sin instantánea la página lo explica
- GIVEN que no hay instantánea de la que leer
- WHEN se abre la página
- THEN se explica el motivo en lugar de mostrar una página vacía

verified-by:
  - tests/slices/reglas-explicadas/test_reglas.py

### Requirement: El estado de una regla se muestra, y se distingue de si el grupo la votó

Cada regla lleva **dos marcadores independientes**:

- **estado**: `aplicada` · `acordada-sin-aplicar` · `sin-decidir`;
- **votada**: si el grupo la aprobó en el canal.

Son independientes a propósito, porque hoy hay reglas **aplicadas y no votadas** —la de días laborables y el
modelo de imputación— y esconderlo sería el peor uso posible de esta página.

Una regla `sin-decidir` dice además **qué falta decidir**.

#### Scenario: una regla acordada sin implementar no se presenta como vigente
- GIVEN una regla decidida pero sin implementar
- WHEN se muestra
- THEN su estado dice que todavía no se aplica

#### Scenario: una regla aplicada y no votada lo declara
- GIVEN una regla que el cálculo usa y que el grupo no votó
- WHEN se muestra
- THEN aparece como aplicada y como no votada

#### Scenario: una regla sin decidir dice qué falta
- GIVEN una regla en discusión
- WHEN se muestra
- THEN incluye qué queda por decidir

verified-by:
  - tests/slices/reglas-explicadas/test_reglas.py
