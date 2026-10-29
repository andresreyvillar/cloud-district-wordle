# Deltas de `dashboard` — fix-enlace-de-la-pestana-del-juego

## ADDED Requirements

### Requirement: Cada pestaña de la navegación lleva a su propia vista

El enlace de cada pestaña se construye con `rutaDe`, la inversa de `resolver`, y lleva a la vista de esa
pestaña, con la web montada en `/` o en `/2/`. La pestaña SuperWordleBros lleva a `/juego`.

Se escapó a producción: `resolver` conocía `/juego` pero `rutaDe` no tenía su caso, caía al `default` y el
enlace apuntaba a la portada. Escribir la URL funcionaba y pulsar la pestaña no. Por eso la verificación
recorre **todas** las pestañas: una nueva que se olvide de su ruta da rojo aquí.

#### Scenario: la pestaña del juego lleva al juego
- GIVEN la navegación pintada desde cualquier sección, con base `/` o `/2/`
- WHEN se lee el enlace de SuperWordleBros
- THEN apunta a `<base>juego` y `resolver` lo lleva a la vista del juego

#### Scenario: ninguna pestaña cae a la portada por defecto
- GIVEN todas las pestañas de la navegación
- WHEN se resuelven sus enlaces
- THEN cada una lleva a una vista distinta

```yaml
checks:
  - type: regex
    file: v2/js/router.js
    pattern: "case VISTAS\\.JUEGO:\\s+return '/juego';"
    describe: la ruta canónica del juego existe para construir el enlace de la pestaña
```

verified-by:
  - tests/slices/juego-de-la-jornada/navegacion.test.js
