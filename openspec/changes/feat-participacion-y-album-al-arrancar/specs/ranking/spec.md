# Deltas de `ranking` — feat-participacion-y-album-al-arrancar

## MODIFIED Requirements

### Requirement: El mínimo de partidas del álbum crece con el mes

En una temporada mensual, para tener puesto en el ranking de belleza hacen falta tantas partidas como
jornadas lleva la temporada, con tope en `MINIMO_PARA_EL_ALBUM`. En la temporada 0 el mínimo es fijo. La
media sigue siendo sobre las jornadas de la temporada, así que faltar no mejora la de nadie.

```yaml
checks:
  - type: regex
    file: tools/album.py
    pattern: '^    return max\(1, min\(MINIMO_PARA_EL_ALBUM, jornadas\)\)$'
    describe: el mínimo de una temporada mensual son las jornadas que lleva, con tope en el de siempre
```

#### Scenario: el segundo día basta con haber jugado los dos
- GIVEN una temporada mensual con dos jornadas
- WHEN se calcula el álbum
- THEN clasifica quien jugó las dos, y no quien jugó una

#### Scenario: la temporada 0 conserva el mínimo fijo
- GIVEN la temporada 0
- WHEN se calcula el álbum
- THEN el mínimo es `MINIMO_PARA_EL_ALBUM`

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py
