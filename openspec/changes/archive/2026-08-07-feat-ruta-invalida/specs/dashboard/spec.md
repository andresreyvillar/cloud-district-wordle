# Deltas de `dashboard` — feat-ruta-invalida

## ADDED Requirements

### Requirement: Una ruta que no existe se declara, porque el fallback SPA no lo hará

El Worker sirve la v2 con `not_found_handling: single-page-application`, así que **cualquier ruta devuelve
200**. Eso es lo que permite que `/t/2026-07` funcione sin servidor de rutas, y a la vez elimina el 404 que
avisaría de un enlace roto: sin él, una ruta mal escrita no falla, simplemente no pinta nada.

La detección es por tanto **del cliente**, y tiene que decir qué ruta se pidió y ofrecer la salida.

#### Scenario: una ruta desconocida se declara con la ruta pedida
- GIVEN una ruta que el router no reconoce
- WHEN se abre
- THEN la vista lo declara y muestra la ruta pedida, en lugar de una página en blanco

#### Scenario: un mes imposible no es una temporada
- GIVEN una ruta con un mes que no existe, como `2026-13`
- WHEN se resuelve
- THEN es ruta desconocida, no una temporada vacía

#### Scenario: una ruta de jugador mal formada no abre ficha
- GIVEN una ruta de jugador cuyo identificador no tiene forma de identificador de Slack
- WHEN se resuelve
- THEN es ruta desconocida

#### Scenario: la vista ofrece volver
- GIVEN la vista de ruta desconocida
- WHEN se muestra
- THEN ofrece volver a la temporada en curso

#### Scenario: una ruta desconocida no pertenece a ninguna sección
- GIVEN una ruta desconocida
- WHEN se pinta la navegación
- THEN ninguna sección aparece como actual

#### Scenario: la ruta pedida se muestra escapada
- GIVEN una ruta que contiene marcado
- WHEN se muestra
- THEN aparece como texto y no se interpreta

verified-by:
  - tests/slices/ruta-invalida/ruta.test.js
