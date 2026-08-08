# Proposal — feat-clasificacion-de-figuras

> **Slice:** `clasificacion-de-figuras` (openspec/slices/ranking/clasificacion-de-figuras.md)

## Why

Las tres piezas del ranking de figuras están hechas y **ninguna se toca con las otras**: el patrón se
guarda (5.1), el histórico se recuperó (5.2) y el clasificador está calibrado (5.0, 24/30). Nadie deriva la
categoría, así que hoy el álbum no existe para ningún consumidor.

Este es el paso que las une, y solo por el lado de los datos: la instantánea de temporada pasa a publicar
el álbum. La vista es 5.4.

## Qué se decidió, y con qué medida

**Puntuación = tasa de figuras por partida clasificada.** Se midieron cuatro criterios sobre los 18
jugadores con 10+ partidas de la temporada 0:

| Criterio | Gana | Por qué se descarta |
|---|---|---|
| Recuento absoluto de figuras | quien más juega | es un ranking de asistencia con otro nombre |
| Puntos por rareza (el loro vale más) | **el segundo de la tabla de puntuación** | anula el propósito del segundo eje: premiar a otra gente |
| Solo la pieza rara (loros) | quien tuvo suerte | una categoría de 205 partidas no sostiene un ranking |
| **Tasa de figuras por partida** | **otra persona** | ninguno |

**Mínimo de 5 partidas clasificadas.** También medido, no elegido por redondo:

| Mínimo | Elegibles (temporada 0) | Líder |
|---|---|---|
| 3 | 19 | Sandra, **100% de tres partidas** |
| **5** | **18** | Juan (Kokuma), 83% de 86 |
| 8 | 18 | Juan (Kokuma) |
| 10 | 17 | Juan (Kokuma) |

Es el umbral más bajo que mata la anomalía; de ahí en adelante nada cambia. Coincide con el
`MINIMO_PARA_CLASIFICAR` de la tabla de puntuación, que a su vez venía del legacy.

**Una partida sin patrón no cuenta como abstracta.** Contarla castigaría a quien jugó cuando el pipeline
aún no guardaba cuadrículas: un fallo del sistema cobrado al jugador. Sale del denominador y la cobertura
se publica aparte.

## What Changes

```
tools/album.py               NUEVO · puro: album(resultados, temporada) -> dict
tools/seasons.py             la instantánea gana la clave `album`
tools/materialize_seasons.py lee también la columna `pattern`
```

Aditivo: ninguna clave de la carga útil cambia, así que la web actual sigue funcionando sin tocarla.

## Lo que se publica, con datos reales

| Temporada | Cuentan | Con patrón | Álbum |
|---|---|---|---|
| 0 · el histórico | 1502 | 1502 (100%) | 21 jugadores, 18 con puesto |
| 1 · agosto 2026 | 80 | 19 (24%) | 11 jugadores, **ninguno con puesto** |

Reparto de la temporada 0: 🌷 46,5% · 🌀 32,4% · 🦜 13,6% · 📐 7,4%. Y la cabeza del álbum:

| | Jugador | Tasa | Tira |
|---|---|---|---|
| 1 | Juan (Kokuma) | 83% (71/86) | 🦜8 🌷60 📐3 🌀15 |
| 2 | Raquel | 79% (86/109) | 🦜12 🌷66 📐8 🌀23 |
| 3 | Gabi | 76% (55/72) | 🦜15 🌷34 📐6 🌀17 |

Los dos podios de la temporada 0 **no comparten a nadie**: el de puntuación es Claire, Andrés R. y Flavia
Venturi; el de belleza, Juan (Kokuma), Raquel y Gabi. Es exactamente para lo que existe este eje.

**Agosto está vacío porque `captura-del-patron` no está en `main`.** El cron diario corre con el código
anterior y sigue descartando la cuadrícula: 61 de las 80 filas del mes no tienen patrón. El álbum de la
temporada en curso se llena cuando la rama se mergee, no antes.

## Impact

- Desbloquea 5.4 (`album-de-figuras`, la vista) y 6.2 (`medallas-de-figuras`).
- Corrige el brief: las rarezas citadas (🦜 8%, 📐 11%, 🌷 12%) eran del clasificador **desmentido**. Las
  reales son 🌷 46,5% · 🌀 32,4% · 🦜 13,6% · 📐 7,4%, y la pieza rara no es el loro sino el geométrico.
- Cierra la pregunta abierta «recuento o ponderado» del brief, con la medida que la decide.
