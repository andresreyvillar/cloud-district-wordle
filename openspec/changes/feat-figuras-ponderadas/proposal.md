# Proposal — feat-figuras-ponderadas

> **Slice:** `clasificacion-de-figuras` (modificación del criterio de puntuación)

## Why

Decisión del dueño: **geométrico > loro > flores**. Hasta ahora las tres figuras valían lo mismo.

El orden coincide con la rareza medida, y no por casualidad: geométrico sale en el 7,4% de las partidas,
loro en el 13,6% y flores en el 46,5%.

## Lo que cuesta, medido antes de hacerlo

Cuando se eligió el criterio se midieron cuatro alternativas, y el ponderado por rareza se descartó por
esto: **corona al segundo de la tabla de puntuación**, que es justo lo que el segundo eje existe para
evitar. Remedido ahora, con los datos ya reparados:

| Criterio | Podio de belleza | ¿Comparte con el de puntuación? |
|---|---|---|
| Actual (todas valen 1) | Juan (Kokuma) · Raquel · Gabi | **nadie** |
| **3/2/1** | Gabi · Andrés R. · Raquel | Andrés R., 2º en puntuación |
| 5/3/1 | Gabi · Andrés R. · Iria Dorado | Andrés R. |

Se hace igualmente porque lo decide el dueño, y queda escrito para que dentro de un mes se sepa qué se
cambió y a cambio de qué.

## Por qué 3/2/1 y no 6/3/1

La rareza da una proporción de unos 6:3:1. Con 5/3/1 el podio es **exactamente el mismo** que con 3/2/1, así
que la escala corta se explica igual de bien y se recuerda mejor: «un geométrico vale tres flores».

## What Changes

```
tools/album.py          PUNTOS · `puntos` y `media` por jugador · el catálogo publica lo que vale cada figura
v2/js/ui/temporada.js   la columna pasa de «Tasa %» a «Pts/partida», y la cabecera anuncia la escala
v2/js/ui/jugador.js     la ficha muestra puntos por partida
tools/resumen.py        el mensaje de Slack, igual
```

**La escala se anuncia** en la cabecera del bloque: `📐3 · 🦜2 · 🌷1 · por partida`. Un «1,14» sin saber
contra qué se mide no dice nada. Y sale del catálogo publicado, no de una tabla escrita en la web.

## Impact

- Con los datos de hoy, el líder del álbum de la temporada 0 pasa de Juan (Kokuma) a **Gabi**.
- La proporción de partidas con figura (`tasa`) **se sigue publicando**: deja de ser el criterio, no el dato.
