---
fuente: diseno-liga-arcade
tipo: diseno
fecha: 2026-08-05
autoridad: propuesta (dirección visual acordada; las reglas de juego que contiene, no)
capabilities: [dashboard, ranking, estadisticas, publicacion]
estado: vigente
original: proyecto de Claude Design "Wordle Temporadas" · 6aee2383-04c9-479a-9b46-92e991cc1e5a
---

## Qué es

Una maqueta completa de la vista de temporada, con el sistema de diseño de Cloud District
(`cloud-district-design-system`). Tres tableros; el implementable es **3a, "Liga arcade"**: la temporada
contada como una partida.

Lo trae el usuario con instrucción explícita de aplicar el estilo y de tener en cuenta los logros nuevos.

## Dirección visual — acordada

| Pieza | Decisión |
|---|---|
| Paleta de puntuación | 1-3 `#3DE07A` · 4-5 `#FFD23F` · 6 `#8B5CFF` · fallo `#FF4D6D` · no jugada, contorno |
| Fondo y superficies | página `#F3F3F3` · tablero `#F6F6F1` · tarjeta `#FFFFFF` |
| Tinta | `#2B2733` principal · `#57516B` secundaria · `#7C7690` terciaria |
| Tipografía | Poppins para texto · DM Mono para cifras y etiquetas · Silkscreen para la marca · Libre Baskerville itálica para la entradilla |
| Estructura | barra superior con HUD, titular grande, podio de tres, `MARCADOR`, `LOGROS`, `ESTADÍSTICAS` |
| Cuadrículas | tira de casillas por jornada, una por día, con la no jugada en contorno |
| Forma | plano, sin sombras, bordes de 2-3 px, secciones separadas por regla gruesa de color |

Nada de esto cambia una regla del juego, así que entra sin pasar por el canal.

## Reglas de juego que el diseño inventa — NO acordadas

El diseño no se limita a pintar: propone mecánicas. Se registran aquí para no perderlas, **no para
implementarlas**.

### Los ocho logros de la maqueta

| Logro | Regla en la maqueta | Estado en la maqueta |
|---|---|---|
| Suertud@ | resolver en un intento | acordada |
| Ornitólog@ | más de 10 loros en un mes | acordada |
| Florista | más de 10 flores en un mes | acordada |
| Arquitect@ | más de 10 geometrías en un mes | acordada |
| Fontaner@ | más de 10 cacas en un mes | propuesta |
| Metrónom@ | publicar todos los días de la temporada | propuesta |
| Superviviente | cerrar el mes sin un solo fallo | propuesta |
| Rajad@ | tres o más ausencias en los días duros | propuesta |

### Once estadísticas derivadas y doce motes

`francotirador` · `sospechoso` · `sembrado` · `rajado` · `noinspirado` · `sexta` · `metronomo` ·
`fantasma` · `remontador` · `irregular` · `aplicado`, y de ellas sale un **mote** por jugador
("El fantasma", "El metrónomo", "El de la sexta", "El irregular", "El discreto"…) con su razón.

Más: **dorsales de tres letras** por jugador y **Δ de posición** en la última jornada.

## Tres conflictos con lo ya medido, y cómo se resuelven

**1. Cuatro umbrales son inalcanzables.** "Más de 10" en cualquier figura no lo logra nadie: el máximo
histórico de una figura en un mes es **6**, la media 1,1, y ninguna de las 123 parejas jugador-mes llega a
10 ([brief de medallas](../briefs/medallas.md)). **Resolución (usuario, 2026-08-05): se asumen los umbrales
calibrados**, no los de la maqueta.

**2. Dos nombres chocan, y uno redefine una regla existente.**

| Nombre en la maqueta | Regla | Ya existía como |
|---|---|---|
| Superviviente | mes sin un solo fallo | **Impecable** |
| Metrónom@ | publicar todos los días | **Pleno** |

Y `Superviviente` ya está implementado con otra regla (resolver en ≤4 tres días de media ≥4,5). Resolución:
se adopta **Metrónom@** en lugar de `Pleno` —el nombre estaba declarado abierto en el brief— y se **rechaza**
llamar `Superviviente` al mes sin fallo, que sigue siendo `Impecable`. Adoptar ese nombre habría dejado dos
reglas distintas con el mismo nombre.

**3. Dos de las estadísticas están bloqueadas por el grupo.** `remontador` es la "mayor remontada" y
`irregular`/`metronomo` roza las "rachas": las dos están explícitamente sin decidir en la Fase 3 del
roadmap. Y cuatro (`sospechoso`, `sembrado`, `rajado`, `noinspirado`) ya existen en el
[brief de figuras](../briefs/ranking-de-figuras.md) como los **comentarios jocosos del resumen diario**, con
frecuencias calibradas por jornada; la maqueta las reutiliza como estadísticas de temporada, que es un uso
distinto del mismo cálculo.

## Lo que sigue abierto

| Abierto | Qué falta decidir |
|---|---|
| Los motes | Son doce etiquetas que el bot y la web colgarían a personas reales. Divertido y también señalable: conviene que el grupo vea la lista antes de que aparezca junto a su nombre |
| Dorsales de tres letras | Cómo se derivan y qué pasa con dos personas que colisionen |
| Δ de posición | Exige guardar la clasificación de la jornada anterior, que hoy no se guarda |
| `Rajad@` como logro negativo | El grupo pidió un "muro de la vergüenza"; esto lo es. Falta que lo confirme |
