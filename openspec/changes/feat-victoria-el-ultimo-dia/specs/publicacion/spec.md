# Deltas de `publicacion` — feat-victoria-el-ultimo-dia

## ADDED Requirements

### Requirement: La noche del último día laborable se publica la victoria en lugar del resumen

Cuando la jornada que resume el bot es la del **último día laborable del mes** (calendario, no reloj: el mismo
día que la recta final anuncia como «última jornada»), el job del resumen diario no publica el resumen: publica
el **mensaje de la victoria** del mes —el que hasta ahora salía el día 1 a las 11:00— con el título del podio del
mes («Podio del mes 🏆 · AAAA-MM»). Debajo del podio y de la felicitación va, en corto, la última jornada: la
palabra, el mejor del día y la obra del día.

El cron del día 1 sigue como red: busca ese título en el canal y, si ya está, no repite; si esa noche no se
publicó, lo publica él. Y las reintentonas del resumen esa misma noche también buscan el título del podio, así
que la victoria no sale dos veces.

Se calcula con lo que hay esa noche: una cuadrícula del último día que llegue después de que se publique no
entra en el podio (medido en 60 días: 2 de 490 llegaron después de medianoche).

#### Scenario: el último laborable sale la victoria
- GIVEN la jornada del último día laborable del mes
- WHEN corre el job del resumen
- THEN publica un mensaje con el título del podio del mes, el podio, la felicitación y la última jornada, y no el
  resumen diario

#### Scenario: no se repite
- GIVEN la victoria del mes ya publicada en el canal
- WHEN vuelve a correr el job del resumen esa noche, o el cron del día 1
- THEN no publican nada

#### Scenario: un día cualquiera sigue saliendo el resumen
- GIVEN una jornada que no es el último día laborable del mes
- WHEN corre el job del resumen
- THEN publica el resumen diario de siempre

```yaml
checks:
  - type: regex
    file: tools/post_ranking.py
    pattern: 'if temporada != TEMPORADA_CERO and es_ultimo_laborable_del_mes\(fecha\):'
    describe: "el último laborable el job del resumen publica la victoria"
  - type: regex
    file: tools/post_ranking.py
    pattern: 'if ya_celebrado\(leer_mensajes\(paginas=PAGINAS_DE_HISTORIA\), temporada\):'
    describe: "la victoria no se repite"
```

verified-by:
  - tests/slices/podio-de-cierre-de-mes/test_victoria.py


### Requirement: Desde octubre la victoria corona a los tres campeones

Si la temporada que cierra es de octubre de 2026 en adelante, el mensaje de la victoria corona, además del
marcador, al campeón del SuperWordleBros (por puntos) y al de figuras (por puntos por partida). Los empates se
comparten en una frase en plural; una competición sin nadie clasificado no corona a nadie. Antes de octubre, el
mensaje no cambia.

#### Scenario: octubre corona a los tres
- GIVEN una temporada 2026-10 cerrada con campeón en las tres competiciones
- WHEN se compone la victoria
- THEN hay una línea para el campeón del SuperWordleBros y otra para el de figuras, además del podio del marcador

#### Scenario: septiembre corona solo el marcador
- GIVEN la temporada 2026-09 con juego y figuras
- WHEN se compone la victoria
- THEN no hay líneas del SuperWordleBros ni de figuras

```yaml
checks:
  - type: regex
    file: tools/podio.py
    pattern: 'DESDE_TRES_COMPETICIONES = "2026-10"'
    describe: "los tres campeones desde octubre"
```

verified-by:
  - tests/slices/podio-de-cierre-de-mes/test_victoria.py
