# Deltas de `dashboard` — feat-tres-campeones

## ADDED Requirements

### Requirement: La tarjeta de la temporada enseña los tres campeones desde octubre

Desde octubre de 2026, la tarjeta de cada temporada en `/temporadas` tiene un hueco por competición —MARCADOR,
SUPERWORDLEBROS, FIGURAS—, cada uno con su corona («CAMPEÓN», «CAMPEONES», «VA GANANDO» o «EMPATE EN
CABEZA»), sus nombres enlazados y su cifra: la media, los puntos del juego y los puntos por partida de las
figuras. Una competición sin nadie clasificado dice «sin campeón». Antes de octubre la tarjeta no cambia.

El medallero desglosa la columna de temporadas ganadas por competición, nombrando solo las que tienen algún
título.

#### Scenario: la tarjeta de octubre enseña las tres
- GIVEN una temporada 2026-10 cerrada con un campeón en cada competición
- WHEN se pinta su tarjeta
- THEN aparecen MARCADOR, SUPERWORDLEBROS y FIGURAS, cada una con su campeón y su cifra

#### Scenario: una competición vacía dice sin campeón
- GIVEN una temporada 2026-10 sin clasificación del juego
- WHEN se pinta su tarjeta
- THEN el hueco del SUPERWORDLEBROS dice «sin campeón» y los otros dos salen con su campeón

```yaml
checks:
  - type: regex
    file: v2/js/ui/temporadas.js
    pattern: 'const huecos = competiciones.map\(\(c\) => hueco\(t, c, varias\)\)'
    describe: "un hueco por competición"
```

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js
