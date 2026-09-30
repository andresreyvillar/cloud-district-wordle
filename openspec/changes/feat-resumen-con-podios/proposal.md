# El resumen diario enseña los rankings como podios y sabe en qué momento del mes está

> Slice: `resumen-diario-compuesto` (modificación). Depende de `feat-juego-en-la-temporada`, que trae la
> clasificación del juego.

## Why

El dueño quiere que el resumen del canal enseñe **los tres rankings como un podio ASCII** con los tres
primeros —primero el general, luego el SuperWordleBros y luego el de figuras— y que el resumen sea
**consciente del momento del mes**: al final del mes el desempate importa más y la tensión es máxima.

Decisiones del dueño:
- **Podio de bloques macizos** (`█`), con el 1º en el centro y más alto, el 2º a la izquierda y el 3º a la
  derecha, en un bloque de código.
- **Arranque, mitad y recta final**: las tres primeras jornadas llevan una línea de arranque; las últimas cinco
  jornadas laborables, un bloque de recta final; la última, se anuncia como tal.

## What Changes

1. `tools/podios.py` (nuevo): `podio_de_texto(titulo, puestos)`, que pinta un podio de hasta tres puestos en
   32 columnas, con empates en el mismo escalón y «y N más».
2. `tools/resumen.py`:
   - `bloque_top` y `bloque_album` pasan a podio; `bloque_juego` (nuevo) con la línea del ganador del nivel del
     día y el podio del mes.
   - `bloque_momento_del_mes(resultados, temporada, jornada, niveles, marcas)` (nuevo).
   - `resumen_del_dia(..., niveles=None, marcas=None)`: momento del mes y los tres podios, en su orden.
3. `tools/refranero.py`: las frases del arranque, la recta final y la última jornada, con el tono del
   resumen.
4. `tools/post_ranking.py`: lee `game_levels` y `game_times` y se los pasa al resumen.

## Out of Scope

- **Se pierde el emoji del dibujo del día en el marcador**: el podio va en un bloque de código de ancho fijo,
  donde un emoji ocupa dos columnas y descuadra los escalones. El dibujo del día sigue en la obra del día.
- Se pasa del top 5 al podio de tres: el cuarto y el quinto ya no salen en el resumen (sí en la web).
- La **alcanzabilidad del marcador general** no se calcula: con la media imputada y la penalización por
  ausencia, «todavía puede alcanzarle» exige simular las jornadas que quedan y no es exacto. Se da la
  distancia y la regla del empate. En el juego sí se calcula, porque es exacta: 10 por nivel.
- Los festivos no se conocen: cuentan como laborables.
- El podio de cierre de mes (`podio-de-cierre-de-mes`) no cambia.

## Impact

| Pieza | Efecto |
|---|---|
| Mensaje del canal | tres podios en lugar del top 5 y la lista del álbum; bloque del momento del mes |
| `post_ranking.py` | dos lecturas más (niveles y marcas), con la clave que ya usa |
| Tests existentes | `test_el_top_cinco_*` y `test_la_cabeza_del_album_*` describen lo que se sustituye: se reescriben como tests de podio |

## Validation Gates

```bash
python3 -m tools.wslice slice validate resumen-diario-compuesto
python3 -m tools.wslice slice coverage resumen-diario-compuesto
python3 -m tools.wslice verify gates --slice resumen-diario-compuesto --change-id feat-resumen-con-podios
```

Antes de mergear, **imprimir el mensaje real** del día con los datos de producción y leerlo: el resumen se ha
equivocado otras veces en cosas que ningún test buscaba (concordancia, repeticiones). **Nunca publicarlo en
el canal para probar**: el mensaje de prueba se imprime.

## Capabilities

| Capability | Requirements |
|---|---|
| `publicacion` | el resumen cuenta la jornada en texto (MODIFIED: podios y juego) · el resumen sabe en qué momento del mes está (ADDED) |
