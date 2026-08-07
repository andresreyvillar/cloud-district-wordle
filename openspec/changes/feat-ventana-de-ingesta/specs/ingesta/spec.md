# Deltas de `ingesta` — feat-ventana-de-ingesta

## MODIFIED Requirements

### Requirement: La ventana de ingesta se mide en días y se pagina

La ejecución horaria lee **todos los mensajes del canal desde una fecha de corte**, paginando hasta
alcanzarla. La ventana no se expresa en número de mensajes.

Medido sobre el histórico: mediana de 10 mensajes al día, máximo 27. Una ventana de 50 mensajes cubre cinco
días **de media** y **no cubre tres** en la peor racha, que son 52 mensajes. Contar mensajes hace que la
cobertura dependa de lo hablador que esté el grupo — un día de charla desplaza los resultados de días
anteriores— que es lo contrario de lo que se le pide a una red de seguridad.

Reingerir lo ya guardado no duplica, porque el upsert va por `(slack_user_id, wordle_id)`. Ese es el hecho
que hace barata una ventana ancha: el único coste son un par de páginas más de API.

#### Scenario: la ventana es una fecha de corte
- GIVEN mensajes de hace un día, de hace casi la ventana entera y de hace un mes
- WHEN se lee el canal
- THEN entran los dos primeros y no el tercero

#### Scenario: un día hablador no desplaza a los días anteriores
- GIVEN sesenta mensajes de charla de hoy y un resultado de hace cuatro días
- WHEN se lee el canal
- THEN el resultado de hace cuatro días entra igualmente

#### Scenario: la ventana pagina hasta el corte
- GIVEN más mensajes en la ventana de los que caben en una página
- WHEN se lee el canal
- THEN se piden las páginas necesarias y llegan todos, en orden cronológico

#### Scenario: la fecha de corte entra por parámetro
- GIVEN una fecha actual concreta
- WHEN se calcula el corte
- THEN sale de esa fecha y no del reloj del sistema

#### Scenario: un fallo a mitad de la paginación aborta
- GIVEN que la segunda página falla
- WHEN se lee el canal
- THEN la ejecución falla en lugar de emitir los mensajes que sí llegaron

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py
