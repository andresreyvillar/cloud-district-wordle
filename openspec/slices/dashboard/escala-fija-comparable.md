---
slice: escala-fija-comparable
status: proposed
kind: action
actor: grupo
trigger:
  type: ui
  surface: web
  detail: "todas las vistas con gráfico — la altura de una barra significa lo mismo en todas partes"
events:
  emits: []
  consumes: []
specs:
  - dashboard
tests_root: tests/slices/escala-fija-comparable/
blocked: null
---

# Dos gráficos del mismo tipo se pueden comparar mirándolos

**Actor:** cualquiera del grupo
**Trigger:** abrir cualquier vista con gráfico

## Contexto

Lo pidió el grupo en el canal, y es un defecto real de las dos gráficas que hay:

- **La dificultad por jornada** se escala al máximo del propio mes. Un mes cuya jornada más dura fue un 4,2
  se ve **exactamente igual de dramático** que uno que llegó a 6,0. La forma es idéntica y el significado no.
- **La distribución de intentos** de un jugador se escala a su propio máximo. Quien jugó 100 partidas y quien
  jugó 10 producen la misma silueta.

Un gráfico autoescalado no miente en sus números, pero **miente en lo que la vista sugiere**, que es lo que
la gente lee de un vistazo. Y es previo a cualquier animación entre meses: sin escala común, animar dos
meses seguidos es un baile sin información.

## La escala de cada cosa

| Gráfico | Escala | Por qué esa |
|---|---|---|
| Dificultad por jornada | **1 a 7 intentos**, fija | Es el rango real de una puntuación: 1 es lo mejor posible y 7 es el fallo. La v1 ya la usaba en su gráfica de evolución (`range: [0.5, 7.5]`) |
| Distribución de intentos | **el mayor recuento de la temporada**, común a todos los jugadores | Es el eje compartido de un conjunto de gráficos pequeños: el mejor lleno toca el techo y el resto se mide contra él |

## Comportamiento observable

### la-dificultad-va-en-la-escala-de-intentos
**WHEN** se pinta la dificultad de una jornada
**THEN** su altura sale de la escala fija de intentos, no del máximo del mes.

### dos-temporadas-se-pueden-comparar
**WHEN** la misma dificultad aparece en dos temporadas distintas
**THEN** se pinta con la misma altura en las dos.

### la-distribucion-comparte-escala-entre-jugadores
**WHEN** se pinta la distribución de dos jugadores de la misma temporada
**THEN** el mismo recuento da la misma altura, y quien jugó poco **se ve pequeño**, que es justo la
información que el autoescalado borraba.

### la-escala-se-declara
**WHEN** se muestra un gráfico con escala fija
**THEN** dice cuál es. Una escala fija que no se anuncia es indistinguible de una automática, así que no
arregla la lectura de un vistazo.

### un-valor-fuera-de-escala-no-se-sale-del-gráfico
**WHEN** un valor supera el máximo de la escala
**THEN** se recorta al máximo en lugar de desbordar el marco.

### sin-datos-no-se-divide-por-cero
**WHEN** una temporada no tiene ningún recuento
**THEN** la escala sigue siendo utilizable y no produce alturas inválidas.

## Estado después

Ninguno: solo pinta.

## Edge cases

- **Una dificultad por debajo de 1** no existe —el mínimo de una partida es un intento— pero el recorte
  cubre los dos extremos por si un dato viniera mal.
- **Una barra de valor mínimo** conserva una altura visible: una barra de cero píxeles se lee como ausencia
  de dato, no como valor bajo.

## Fuera de alcance, y por qué

- **La gráfica de evolución** de la ficha, que todavía no existe: nace ya con esta escala.
- **Animar la transición entre meses**: era el motivo de pedir la escala, pero es otra cosa y va después.

## Slices compañeros

- [[clasificacion-de-temporada]] · [[ficha-de-jugador]] — las dos vistas con gráfico que esto corrige.
