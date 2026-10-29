# Deltas de `resultados` — feat-figuras-simetricas

## ADDED Requirements

### Requirement: La simetría es un rasgo del patrón, y no se almacena

La simetría en espejo se **deriva de la columna `pattern`** cada vez que se clasifica, igual que el resto de
los rasgos del dibujo. No se añade ninguna columna, ningún índice y ningún campo a la instantánea: lo que
viaja es la categoría resultante, no cómo se llegó a ella.

Es la misma propiedad que sostiene todo el álbum: recalibrar reclasifica el histórico solo, sin migración.
Persistir «este patrón es simétrico» crearía un dato que hay que mantener a mano en cuanto la definición del
rasgo cambie, y dejaría el histórico irrecuperable en cada ajuste.

El rasgo se mide sobre el **cuerpo** de la cuadrícula, nunca sobre la cuadrícula entera. La banda verde final
—la fila de la palabra acertada— es simétrica en toda partida resuelta, así que incluirla convertiría el
rasgo en «¿ha resuelto?», que ya se sabe por otro camino.

```yaml
checks:
  - type: cli-command
    command: python3 tools/calibrate_figures.py --sin-red
    expect: el acuerdo con el conjunto dorado no baja de 24 fichas
  - type: column
    table: wordle_results
    column: pattern
    note: el rasgo se deriva de esta columna; no se crea ninguna otra
```

#### Scenario: la simetría no añade columnas
- GIVEN el esquema de `wordle_results`
- WHEN se clasifica una cuadrícula simétrica
- THEN la categoría se deriva de `pattern` y no se escribe en ninguna columna nueva

#### Scenario: el mismo patrón da el mismo veredicto sin estado
- GIVEN una cuadrícula cualquiera
- WHEN se clasifica dos veces
- THEN el veredicto es el mismo, sin depender de una clasificación anterior

verified-by:
  - tests/slices/clasificacion-de-figuras/test_simetria.py
