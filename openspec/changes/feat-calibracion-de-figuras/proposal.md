# Proposal — feat-calibracion-de-figuras

> **Slice:** N/A — es el paso 5.0 del roadmap: calibrar antes de especificar. Una función pura sin
> trigger no es comportamiento observable, y hasta que el clasificador acierte lo suficiente no se
> puede escribir el slice del álbum ([roadmap](../../../docs/roadmap-v2.md), Fase 5).

## Why

El eje de figuras entero —`clasificacion-de-figuras`, `album-de-figuras`, `resumen-diario-compuesto` y
las cinco medallas de figuras— depende de una pregunta sin responder: **¿puede una función determinista
reconocer la figura de una cuadrícula tan bien como el humano que las etiquetó?**

Hay 30 cuadrículas etiquetadas a mano ([conjunto dorado](../../../docs/context/sources/2026-08-05-etiquetado-de-patrones.md))
y la heurística del brief fallaba: **69% de abstractos frente al 33% del humano**. Sin medir, ajustar
pesos es adivinar, y el brief lo dice: si el clasificador determinista no llega, la alternativa es un
modelo mirando el dibujo, y eso es un ADR (deja de ser gratis y no se cubre con golden tests).

Este pack responde la pregunta con números y deja el clasificador escrito, o la responde con un no.

## What Changes

Todo es nuevo. **No toca el pipeline ni la web**: nadie llama todavía al clasificador.

```
tools/figures.py                       el clasificador: patrón → figura. PURO
tools/calibrate_figures.py             el informe de calibración (solo lectura)
tests/figuras/test_clasificador.py     el examen: las 30 etiquetas humanas
```

El conjunto dorado **no se copia**: el test lo parsea del propio source, así que la verdad tiene una
sola definición y editar una etiqueta mueve el examen.

## Dos criterios, no uno

El primer candidato sacó **83% de acuerdo con las 30 y 55% de flores sobre los 1521 patrones reales**
(el humano etiqueta 37%). Acertaba el examen y no generalizaba: la regla que usaba —«hay una fila verde
ancha y algún amarillo»— se cumple cada vez más según crece la cuadrícula, así que la flor se comía las
partidas largas.

De ahí que la calibración se mida contra **dos criterios independientes**:

| Criterio | Qué mide | Datos |
|---|---|---|
| **Acuerdo** | ¿acierta la etiqueta que puso el humano? | las 30 fichas |
| **Reparto** | ¿alguna categoría se come el resto? | los 1521 patrones de producción |

El segundo es el que tumbó al primer candidato, y por eso el informe publica los dos.

## Lo calibrado

Cuatro reglas en cascada, cada una con su rasgo y su motivo. Los dos rasgos que decidieron la
calibración salen de mirar qué distingue de verdad las etiquetas humanas:

- **el amarillo del loro es el pico: toca el cuerpo.** Un amarillo flotando en negro es un pétalo, no un
  pico. Con esto el loro dejó de comerse dos flores.
- **la flor necesita pétalos libres**: una fila de amarillos sin verde, o tres amarillos flotando. Es lo
  que el humano ve —el suelo verde y los pétalos encima— y no crece con el tamaño de la cuadrícula.

| Regla | Dispara cuando | Motivo |
|---|---|---|
| abstracto | no hay banda verde final, o no hay dibujo | sin suelo no hay flor: las 3 cuadrículas falladas del conjunto son abstracto |
| loro | línea verde vertical aislada + 1-2 amarillos pegados al cuerpo + verde entre 4 y 12 | la definición del vocabulario: columna, segundo elemento y pico |
| geometrico | poca tinta y a lo sumo un amarillo | «pocas celdas y forma limpia»: un tallo, una pirámide |
| flores | dos amarillos con una fila de pétalos, o tres pétalos libres | el suelo verde con amarillos encima |
| abstracto | lo demás | no existe la categoría «ambiguo» (decisión del brief) |

## Impact

- **Nada en producción.** El clasificador no se llama desde ningún sitio; la columna `pattern` solo se lee.
- Desbloquea 5.1-5.7 y las cinco medallas de figuras de 6.2, o las cancela si el número no llega.
- El acuerdo queda **como gate y no como promesa**: un test lo comprueba en cada ejecución de la suite.
