# Deltas de `publicacion` — feat-captura-del-titular

## MODIFIED Requirements

### Requirement: La imagen del resumen es el titular, no la página entera

La captura que acompaña al mensaje diario es **el titular de la temporada y el podio**: quién lidera, por
cuánta diferencia, y las tiras de los tres primeros.

Antes se fotografiaba la vista completa —marcador, logros, álbum y estadísticas—. Con el resumen en texto
eso **dice dos veces lo mismo**, y además llega a Slack como una tira larguísima que se ve en miniatura.

El objetivo **espera al mismo selector que fotografía**. Esperar a uno y capturar otro deja la puerta
abierta a fotografiar algo a medio pintar.

Y si el elemento no está, el fallo **dice cuál y en qué URL**: antes daba un error de objeto nulo que no
identificaba ni el selector ni la página.

#### Scenario: se fotografía el titular y el podio
- GIVEN el objetivo de la v2
- WHEN se prepara la captura
- THEN el elemento que se fotografía es el titular, no el contenedor de toda la vista

#### Scenario: se espera a lo que se va a fotografiar
- GIVEN el objetivo de la v2
- WHEN se compara lo que espera con lo que captura
- THEN son el mismo elemento

#### Scenario: un selector que no encaja se declara
- GIVEN un objetivo cuyo elemento no existe en la página
- WHEN se intenta capturar
- THEN el error nombra el selector y la URL

verified-by:
  - tests/slices/captura-apunta-a-la-v2/test_captura.py
