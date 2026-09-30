# Deltas de `publicacion` — feat-resumen-con-podios

## MODIFIED Requirements

### Requirement: El resumen diario cuenta la jornada en texto

El mensaje que el bot publica cada tarde incluye, además de las medallas y el enlace, estas secciones
derivadas de los datos del día y de la temporada:

1. **Jugador del día** — la mejor puntuación de la jornada, con todos los empatados.
2. **Obra del día** — la figura **más rara de la temporada** entre las dibujadas ese día.
3. **Tres podios**, en este orden: el **marcador general**, el **SuperWordleBros** y las **figuras**.

Cada podio es un **podio ASCII de bloques macizos** (`█`) dentro de un bloque de código, con su título
encima: el 1º en el centro y más alto, el 2º a la izquierda y el 3º a la derecha; encima de cada escalón, su
puesto, su nombre y su cifra (la media en el marcador, los puntos en el juego, la puntuación media en las
figuras). Los puestos son los de la clasificación —un empate comparte escalón—; en un escalón con más de tres
nombres se nombran tres y se dice cuántos más hay. **Ninguna línea de un podio pasa de 32 caracteres**, y un
nombre de más de 10 se acorta, para que se lea en el móvil sin desplazarse.

Antes del podio del juego va una línea con el ganador del nivel que se jugó ese día —el último nivel
congelado anterior a la jornada del resumen—, su tiempo con centésimas y cuántos lo terminaron. El podio del
juego es el de la clasificación del juego del mes de la jornada del resumen.

Son **dos premios y no uno** por evidencia: exigir mejor puntuación *y* figura reconocible deja el premio
vacío el 94% de las jornadas, porque la figura sale de las partidas que salen mal.

Ninguna sección se inventa: un ranking sin nadie no pinta podio, y los demás salen igual. Y el texto **no
recalcula nada**: el marcador, el álbum y el juego salen de las mismas funciones que la instantánea que
publica la web.

#### Scenario: el marcador sale como podio
- GIVEN una temporada con al menos tres clasificados
- WHEN se compone el resumen
- THEN hay un bloque de código con bloques `█`, el 1º en la columna central y con el escalón más alto, y sus
  tres nombres con su media

#### Scenario: los podios van en su orden
- GIVEN datos para el marcador, el juego y las figuras
- WHEN se compone el resumen
- THEN el podio del marcador va antes que el del juego, y el del juego antes que el de figuras

#### Scenario: el juego lleva el ganador del día
- GIVEN un nivel congelado anterior a la jornada, con marcas
- WHEN se compone el resumen
- THEN antes del podio del juego hay una línea con el número del nivel, el ganador, su tiempo con centésimas y
  cuántos lo terminaron

#### Scenario: el empate comparte escalón
- GIVEN dos jugadores empatados en el 1º y cinco empatados en el 3º
- WHEN se pinta el podio
- THEN los dos primeros van en el escalón central, y en el 3º se nombran tres y se dice «y 2 más»

#### Scenario: el podio cabe en el móvil
- GIVEN nombres de más de 10 caracteres
- WHEN se pinta el podio
- THEN ninguna línea pasa de 32 caracteres

#### Scenario: un ranking vacío no pinta podio
- GIVEN una temporada sin marcas del juego
- WHEN se compone el resumen
- THEN no hay podio del juego, y el del marcador y el de figuras salen en su orden

```yaml
checks:
  - type: regex
    file: tools/resumen.py
    pattern: 'bloque_top\(resultados, temporada, jornada\),[\s\S]*?bloque_juego\(resultados, temporada, jornada, niveles or \(\), marcas or \(\)\),\s+bloque_album\(resultados, temporada\),'
    describe: "los podios en orden — marcador, juego, figuras"
  - type: regex
    file: tools/post_ranking.py
    pattern: 'niveles, marcas = leer_juego\(\) if resumen_activo\(\) else'
    describe: el publicador lee el juego para el resumen
```

verified-by:
  - tests/slices/resumen-diario-compuesto/test_podios.py

## ADDED Requirements

### Requirement: El resumen sabe en qué momento del mes está

El resumen se sitúa en el mes con **la fecha de la jornada y el calendario**, sin leer el reloj (§10):

- **Arranque** — la jornada es una de las tres primeras que cuentan en la temporada: justo antes de los podios
  va una línea de arranque de mes, sin hablar de ventajas.
- **Mitad** — ni arranque ni recta final: no hay bloque de tensión; el resumen es el de siempre.
- **Recta final** — quedan cuatro días laborables o menos en el mes después de la jornada: justo antes de los
  podios va el bloque de recta final, con cuántas jornadas quedan, quién manda y a qué distancia —en media
  publicada— está el segundo, y que un empate a final de mes **comparte el primer puesto**. Si hay
  clasificación del juego, dice cuántos puntos quedan en juego —10 por cada nivel del mes que queda por
  cerrar: el que está abierto, si es del mes, y uno por cada laborable desde la jornada del resumen— y si el
  segundo todavía puede alcanzar al primero.
- **Última jornada** — el último día laborable del mes: el bloque de recta final lo anuncia como la última
  jornada.

Los festivos no se conocen: cuentan como laborables, así que en un mes con festivo al final la recta final
puede anunciar una jornada de más.

#### Scenario: el mes arranca
- GIVEN la segunda jornada que cuenta en la temporada
- WHEN se compone el resumen
- THEN antes de los podios hay una línea de arranque de mes y no hay bloque de recta final

#### Scenario: la recta final cuenta lo que queda
- GIVEN una jornada con tres días laborables por delante en el mes y los dos primeros a 0,05 de media
- WHEN se compone el resumen
- THEN el bloque de recta final dice que quedan 3 jornadas, nombra al primero y al segundo, dice la distancia
  y que un empate comparte el primer puesto

#### Scenario: la recta final dice si el juego sigue abierto
- GIVEN el primero del juego con 12 puntos más que el segundo y dos niveles por cerrar en el mes
- WHEN sale el bloque de recta final
- THEN dice que quedan 20 puntos en juego y que el segundo todavía puede alcanzarle

#### Scenario: con el juego decidido se dice
- GIVEN el primero del juego con 32 puntos más que el segundo y dos niveles por cerrar en el mes
- WHEN sale el bloque de recta final
- THEN dice que el segundo ya no puede alcanzarle

#### Scenario: la última jornada se anuncia
- GIVEN la jornada del último laborable del mes
- WHEN se compone el resumen
- THEN el bloque lo anuncia como la última jornada, sin «quedan 0»

#### Scenario: a mitad de mes no hay tensión
- GIVEN una jornada que no está entre las tres primeras ni en la recta final
- WHEN se compone el resumen
- THEN no hay línea de arranque ni bloque de recta final

#### Scenario: el momento del mes no depende del reloj
- GIVEN la misma jornada compuesta con el reloj del sistema en dos fechas distintas
- WHEN se compone el resumen
- THEN el bloque del momento del mes es el mismo

```yaml
checks:
  - type: regex
    file: tools/resumen.py
    pattern: 'bloque_momento_del_mes\(resultados, temporada, jornada, niveles or \(\), marcas or \(\)\),\s+bloque_top\('
    describe: el momento del mes va justo antes de los podios
```

verified-by:
  - tests/slices/resumen-diario-compuesto/test_momento_del_mes.py
