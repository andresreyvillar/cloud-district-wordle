# Deltas de `ranking` — feat-juego-en-la-temporada

## ADDED Requirements

### Requirement: El SuperWordleBros se clasifica en el mes por puntos por puesto en cada nivel

La temporada tiene una clasificación del juego además de la general y la de figuras. Los tiempos de niveles
distintos no se suman —cada nivel tiene otro largo—, así que se puntúa **por puesto en cada nivel**: 10 al
primero, 8 al segundo, 6, 5, 4, 3, 2, y 1 del octavo en adelante, en el orden del ranking del nivel: **más
estrellas primero** y, con las mismas estrellas, menos tiempo. Las mismas estrellas y el mismo tiempo en
centésimas comparten puesto y puntos (1, 1, 3). El mes suma los puntos de cada jugador; a igualdad de puntos se comparte puesto, y las
victorias y el nombre solo ordenan la lista.

Solo puntúan los niveles de jornadas que cuentan para la temporada (laborables con al menos cinco jugadores),
y cada nivel cuenta en el mes de **su jornada**, no en el de la partida.

La calcula el pipeline con una función pura —resultados, niveles y marcas entran por parámetro— y la guarda en
la instantánea como la clave `juego`: `{ escala, niveles, clasificacion: [{ posicion, jugador, nombre,
puntos, niveles, victorias }] }`. Los nombres son los de la fila más reciente de cada jugador.

#### Scenario: cada nivel reparte puntos por puesto
- GIVEN un nivel de la temporada con marcas de nueve jugadores, todas distintas
- WHEN se calcula la clasificación del juego
- THEN los puntos del nivel son 10, 8, 6, 5, 4, 3, 2, 1 y 1, de menor a mayor tiempo

#### Scenario: las estrellas pesan más que el tiempo
- GIVEN en un nivel, una marca de 9 estrellas en 12 s y otra de 13 estrellas en 13 s
- WHEN se calcula
- THEN la de 13 estrellas recibe 10 y la de 9 recibe 8

#### Scenario: un empate en un nivel comparte puntos
- GIVEN dos marcas con el mismo tiempo en centésimas en el primer puesto
- WHEN se calcula
- THEN las dos reciben 10 y la siguiente recibe 6

#### Scenario: el mes suma y comparte puesto a igualdad de puntos
- GIVEN dos jugadores que acaban el mes con los mismos puntos
- WHEN se compone la clasificación
- THEN comparten puesto, y la lista pone delante al de más victorias

#### Scenario: los niveles de días que no cuentan no puntúan
- GIVEN un nivel de un sábado y otro de un laborable con cuatro jugadores
- WHEN se calcula la clasificación del mes
- THEN ninguno de los dos da puntos

#### Scenario: el nivel del último día cuenta en su mes
- GIVEN el nivel de la última jornada de septiembre, con marcas registradas el 1 de octubre
- WHEN se calculan septiembre y octubre
- THEN sus puntos están en septiembre y no en octubre

#### Scenario: sin marcas la clasificación está vacía
- GIVEN una temporada sin ninguna marca del juego
- WHEN se materializa
- THEN `juego.clasificacion` es una lista vacía y el resto de la instantánea es el mismo

#### Scenario: la misma entrada da la misma clasificación
- GIVEN los mismos resultados, niveles y marcas en otro orden
- WHEN se calcula dos veces
- THEN las dos clasificaciones son idénticas

```yaml
checks:
  - type: regex
    file: tools/juego.py
    pattern: 'ESCALA = \(10, 8, 6, 5, 4, 3, 2\)'
    describe: la escala que decidió el dueño
  - type: regex
    file: tools/juego.py
    pattern: 'return \(-int\(marca.get\("estrellas"\) or 0\), _centesimas\(marca\["segundos"\]\)\)'
    describe: las estrellas ordenan antes que el tiempo
  - type: regex
    file: tools/seasons.py
    pattern: '"juego": clasificacion_del_juego\('
    describe: la clasificación del juego entra en la instantánea
```

verified-by:
  - tests/slices/clasificacion-del-juego/test_clasificacion_del_juego.py


### Requirement: La temporada enseña la clasificación del juego debajo del álbum de figuras

La vista de temporada pinta, justo después del álbum de figuras y antes de las estadísticas, un bloque
SUPERWORDLEBROS con la clasificación de `carga.juego`: puesto —escrito solo cuando cambia—, nombre escapado,
puntos, niveles jugados y victorias, y una línea que explica la escala y cuántos niveles lleva el mes. Sin
clasificación, o con una instantánea sin la clave `juego`, el bloque no se pinta.

#### Scenario: el bloque va entre el álbum y las estadísticas
- GIVEN una instantánea con clasificación del juego
- WHEN se pinta la temporada
- THEN el bloque SUPERWORDLEBROS aparece después de ÁLBUM DE FIGURAS y antes de ESTADÍSTICAS

#### Scenario: sin clasificación no hay bloque
- GIVEN una instantánea con `juego.clasificacion` vacía, u otra sin la clave `juego`
- WHEN se pinta la temporada
- THEN no aparece el bloque SUPERWORDLEBROS

```yaml
checks:
  - type: regex
    file: v2/js/ui/temporada.js
    pattern: '\$\{bloqueDeAlbum\(carga\)\}\s+\$\{bloqueDelJuego\(carga\)\}\s+\$\{estadisticas\(carga\)\}'
    describe: el bloque va entre el álbum y las estadísticas
```

verified-by:
  - tests/slices/marcador-del-juego/marcador.test.js
