# Deltas de `dashboard` — feat-juego-en-la-temporada

## ADDED Requirements

### Requirement: La pestaña dice cuándo el nivel ya está cerrado

Si alguien termina el nivel en una pestaña abierta antes de que se congelara el siguiente, `registrar_tiempo`
lo rechaza por nivel cerrado. La página no enseña entonces el aviso genérico de fallo: dice que ese nivel ya
está cerrado y que recargue para jugar el nuevo. El texto para compartir sigue apareciendo.

#### Scenario: una marca de un nivel cerrado lo dice
- GIVEN un nombre elegido y la API del ranking que rechaza la marca por nivel cerrado
- WHEN se llega a la meta
- THEN el estado dice que el nivel ya está cerrado y que se recargue

```yaml
checks:
  - type: regex
    file: v2/js/ui/juego.js
    pattern: 'nivel ya está cerrado/.test\('
    describe: la pestaña distingue el rechazo por nivel cerrado
```

verified-by:
  - tests/slices/ranking-del-juego/marcas.test.js


### Requirement: La clasificación del juego de la temporada se pinta sin recalcular

El bloque SUPERWORDLEBROS de la temporada lee `carga.juego` tal cual lo dejó el pipeline: no ordena, no
puntúa y no lee `game_times`. Así la web y el resumen del canal enseñan la misma tabla.

#### Scenario: cada fila sale con sus cifras
- GIVEN una clasificación del juego con empates
- WHEN se pinta el bloque
- THEN cada fila lleva puesto, nombre, puntos, niveles y victorias, y el puesto compartido solo se escribe una
  vez

verified-by:
  - tests/slices/marcador-del-juego/marcador.test.js


### Requirement: Solo se congelan los niveles de días que cuentan para la temporada

El cron congela únicamente jornadas **laborables con al menos cinco jugadores**, las mismas que cuentan para la
temporada y que puntúan en el juego. Una jornada de fin de semana o de un laborable con menos jugadores no crea
nivel, así que no cierra el que está en juego: **el nivel del viernes se juega el sábado, el domingo y el
lunes**, y todas esas marcas cuentan. El del lunes se congela el martes a partir de las 02:00 y cierra el del
viernes.

El mínimo de cinco jugadores es el de `tools/seasons.py::MUESTRA_MINIMA_DEL_DIA`; el script del cron, en
JavaScript, usa la misma cifra, y un test comprueba que las dos coinciden.

#### Scenario: un sábado con partidas no crea nivel
- GIVEN el nivel del viernes congelado y resultados del sábado
- WHEN corre el cron el domingo a las 02:00 o después
- THEN no se congela nada y el nivel del viernes sigue siendo el último

#### Scenario: un laborable con cuatro jugadores no crea nivel
- GIVEN una jornada laborable con cuatro jugadores
- WHEN corre el cron al día siguiente
- THEN se congela la anterior que cuenta, no esa

#### Scenario: los dos mínimos son el mismo
- GIVEN el mínimo de jugadores del pipeline y el del script
- WHEN se comparan
- THEN son iguales

```yaml
checks:
  - type: regex
    file: v2/js/domain/superbros.js
    pattern: 'return jornadaDelNivel\(deDiasQueCuentan\(resultados\)'
    describe: el cron solo congela días que cuentan
```

verified-by:
  - tests/slices/nivel-congelado/congelar.test.js


### Requirement: El ranking de cada nivel pone las estrellas por delante del tiempo

El ranking bajo el juego ordena de más a menos estrellas y, con las mismas estrellas, de menor a mayor tiempo.
Comparten puesto solo dos marcas con las mismas estrellas y el mismo tiempo. Cuando una partida no mejora la
marca, la página dice cuál es la marca que se queda, con sus estrellas y su tiempo.

#### Scenario: más estrellas va delante aunque sea más lento
- GIVEN una marca de 9 estrellas en 12,03 s y otra de 13 estrellas en 13 s
- WHEN se pinta el ranking del nivel
- THEN la de 13 estrellas va primera

#### Scenario: si no mejora, se dice la marca que se queda
- GIVEN una partida que no mejora la marca
- WHEN la base de datos responde
- THEN la página dice las estrellas y el tiempo de la marca que se queda

verified-by:
  - tests/slices/ranking-del-juego/marcas.test.js
