# Proposal — feat-medallas-de-figuras

> **Slice:** `medallas-de-figuras` (openspec/slices/estadisticas/medallas-de-figuras.md)

## Why

Había siete medallas y **ninguna miraba el dibujo**. El eje de figuras tenía ranking pero no logros, así que
premiaba solo a quien encabeza y no a quien consigue algo concreto.

## Los umbrales del brief no valían, y el propio brief lo decía

Estaban medidos con el clasificador que luego se desmintió, con esta nota: «hay que rehacerlos junto a la
calibración, no por separado». Rehechos sobre **122 pares jugador-mes** con el clasificador calibrado:

| Medalla | Umbral del brief | Lo lograba… en realidad | Umbral nuevo | Lo logra | Nivel |
|---|---|---|---|---|---|
| Ornitólog@ | 4 loros | 11,5% (quería 3%) | **5 loros** | 3,3% | legendario |
| Arquitect@ | 4 geométricos | 1,6% (quería 2%) | **4** (sin cambio) | 1,6% | legendario |
| Florista | 5 flores | **63,1%** (quería 8%) | **11 flores** | 11,5% | raro |
| Abstract@ | 12 abstractos | **0,8%** (quería 24%) | **7 abstractos** | 23,0% | común |
| Coleccionista | las cuatro | 41,0% (quería 32%) | las cuatro | 41,0% | común |

Los dos que más se movieron son los dos que dependen del reparto: con el clasificador bueno, `flores` pasó a
ser el 46,5% de todo y `abstracto` bajó al 32,4%.

Cada umbral queda justo por debajo del máximo que alguien ha llegado a hacer —loro 8, geométrico 4, flores
18, abstracto 14—, que es donde un logro es difícil sin ser imposible. Excluir agosto de 2026, el mes casi
sin patrones, movía cada cifra **menos de dos puntos**, así que no se excluye: un umbral que dependa de qué
meses se miren no es un umbral.

## What Changes

```
tools/badges.py             catálogo de 7 → 12 · umbrales · `_de_figura` sobre el recuento del álbum
tools/post_ranking.py       `temporada_del_resumen` + `COLUMNAS` con `pattern`
v2/js/ui/temporada.js       las doce tarjetas, con su regla
v2/js/ui/jugador.js         los cinco nombres nuevos en el palmarés
v2/assets/icons/logros.svg  `fontanero` → `abstracto` · símbolo nuevo `coleccionista`
```

**El recuento sale del álbum, no de un segundo recuento.** Si la tira dice `🦜5` y `Ornitólog@` no salta, el
logro parece roto. Es el mismo principio que ya se aplicó al álbum, y por la misma razón: en este
repositorio, dos definiciones de lo mismo han divergido tres veces.

## Un fallo latente, de la tercera vez que aparece la misma causa raíz

`post_ranking.seccion_de_medallas` derivaba la temporada con `str(fecha)[:7]` — el prefijo del mes. Hoy
funciona **por casualidad**, porque agosto de 2026 es a la vez el mes y el identificador de temporada; para
cualquier fecha anterior devolvía un identificador que no existe y las medallas del día salían de una
temporada vacía.

Es la tercera aparición: ya mordió en `badges._de_la_temporada` (181 jornadas sin una sola medalla) y en la
web (`/datos` decía que contaban 70 de 1543 filas). Ahora usa `seasons.temporada_de`, como todo lo demás.

Y el resumen **no leía la columna del patrón**, así que ninguna medalla de figura habría podido anunciarse
nunca. El fallo habría sido silencioso: medallas que simplemente no salen.

## Un test que pasó en verde con el sprite roto

El símbolo nuevo se insertó **dentro del comentario de la cabecera** del sprite, porque ahí hay un `</svg>`
de ejemplo y el script cortó por el primero. Resultado: SVG mal formado, **las doce tarjetas sin icono** —
también las siete que funcionaban— y el test en verde, porque buscaba la cadena `id="coleccionista"` en el
fichero entero y ahí estaba, comentada.

Lo cazó el navegador. El test ahora **quita los comentarios antes de mirar**, cuenta que los `<symbol>`
abiertos y cerrados cuadren, y comprueba que el fichero termine donde debe.

## Impact

- Cierra el punto 6.2 y deja el eje de figuras completo: clasificación, álbum y medallas.
- La temporada 0 sale distorsionada —13 de 21 jugadores son «Ornitólog@ legendario»— porque son 181
  jornadas con umbrales pensados para un mes. Es la misma distorsión que ya tienen Fondista y Verdugo allí,
  y se acepta igual: darle a las figuras una regla propia de temporada sería una segunda definición.
