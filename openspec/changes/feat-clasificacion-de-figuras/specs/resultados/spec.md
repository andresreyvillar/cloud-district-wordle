# Deltas de `resultados` — feat-clasificacion-de-figuras

## ADDED Requirements

### Requirement: La categoría se deriva del patrón, no se almacena

La figura de una partida se calcula a partir del patrón crudo **cada vez que se materializa la temporada**.
No existe una columna de categoría, y ningún proceso escribe el veredicto.

El precio está declarado: recalibrar un umbral cambia el álbum de todo el mundo en la siguiente
materialización. La contrapartida es que lo hace **sin migración** y sobre el histórico completo, que es lo
que permite que el clasificador siga mejorando.

Una partida **sin patrón no tiene categoría**. No se le asigna abstracto: abstracto es un veredicto sobre
un dibujo, y aquí no hay dibujo que mirar. Queda fuera del cálculo y la instantánea publica cuántas son.

El álbum usa **los mismos días que la temporada**. No tiene su propia definición de qué jornada cuenta.

#### Scenario: la figura sale del patrón crudo
- GIVEN un resultado con su cuadrícula almacenada
- WHEN se materializa la temporada
- THEN su categoría aparece en el recuento del jugador sin haberse escrito en ninguna columna

#### Scenario: sin patrón no se inventa categoría
- GIVEN un resultado que cuenta en la temporada pero no tiene patrón
- WHEN se calcula el álbum
- THEN no cuenta como figura ni como abstracto, y la instantánea dice cuántas partidas quedaron así

#### Scenario: el álbum hereda los días de la temporada
- GIVEN un resultado con patrón cuya jornada no cuenta en la temporada
- WHEN se calcula el álbum
- THEN su patrón tampoco entra

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py
