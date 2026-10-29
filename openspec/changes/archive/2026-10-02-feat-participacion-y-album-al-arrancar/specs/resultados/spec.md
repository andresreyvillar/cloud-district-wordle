# Deltas de `resultados` — feat-participacion-y-album-al-arrancar

## MODIFIED Requirements

### Requirement: La instantánea publica el mínimo del álbum que se aplicó

El campo `minimo` del álbum en la instantánea es el mínimo **efectivo** de la temporada —las jornadas que
lleva, con tope—, no la constante: la web lo enseña para explicar por qué una fila no tiene puesto, y tiene
que ser el que decidió.

#### Scenario: el mínimo publicado es el que decidió
- GIVEN una temporada mensual con una jornada
- WHEN se materializa el álbum
- THEN `minimo` vale 1

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py
