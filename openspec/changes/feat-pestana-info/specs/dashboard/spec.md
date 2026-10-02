# Deltas de `dashboard` — feat-pestana-info

## ADDED Requirements

### Requirement: La pestaña Info explica cómo se juega y enseña las reglas vigentes

La pestaña **Info** (`/info`) sustituye a Reglas. Tiene cuatro apartados, en este orden:

1. **Cómo se juega**: se juega la palabra de https://lapalabradeldia.com, se pega el resultado en el canal
   #wordle-line y el bot hace el resto.
2. **Las competiciones**: el marcador, el SuperWordleBros, el álbum de figuras y las medallas, un párrafo cada
   una.
3. **Lo que publica el bot**: el resumen de cada noche y la victoria la noche del último día laborable.
4. **Reglas vigentes**: las reglas del catálogo de la temporada en curso con estado «aplicada» y que no son
   históricas (la temporada 0), agrupadas por eje, sin marcas de estado ni de votación.

La explicación **no escribe cifras a mano**: los números solo aparecen en las reglas, que los leen de las
constantes del cálculo, así que la explicación no puede contradecirlas. `/reglas` y `/t/<AAAA-MM>/reglas`
llevan a `/info`: ningún enlace viejo da error.

#### Scenario: Info explica cómo se juega, las competiciones y el bot
- GIVEN la instantánea de la temporada en curso
- WHEN se abre /info
- THEN hay cuatro apartados en orden, con el enlace a lapalabradeldia.com y el nombre del canal

#### Scenario: la explicación no lleva números
- GIVEN la pestaña Info pintada
- WHEN se mira el texto de los tres primeros apartados
- THEN no hay ninguna cifra

#### Scenario: solo salen las reglas vigentes
- GIVEN un catálogo con reglas aplicadas, propuestas sin decidir y reglas históricas
- WHEN se pintan las reglas de Info
- THEN solo salen las aplicadas no históricas, y no hay marcas de «sin decidir» ni de votación

#### Scenario: los enlaces viejos llevan a Info
- GIVEN las rutas /reglas y /t/2026-09/reglas
- WHEN se resuelven
- THEN llevan a la vista Info, y la pestaña de la navegación dice «Info»

verified-by:
  - tests/slices/reglas-explicadas/info.test.js
