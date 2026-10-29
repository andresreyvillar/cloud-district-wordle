# Deltas de `ranking` — feat-tres-campeones

## ADDED Requirements

### Requirement: Desde octubre, cada temporada tiene tres campeones

Desde la temporada de octubre de 2026, una temporada tiene **tres competiciones**: el marcador general, el
SuperWordleBros (`carga.juego.clasificacion`) y las figuras (`carga.album.jugadores`, solo los clasificados).
El archivo trae `competiciones`: una entrada por competición con `clave` (`marcador`, `juego`, `figuras`),
`lideres` —todos los de su primer puesto— y `campeones` —los mismos, si la temporada está cerrada—. Antes de
octubre, `competiciones` trae solo el marcador. `campeones`/`lideres` de nivel superior siguen siendo los del
marcador.

El medallero cuenta los títulos de temporadas cerradas **por competición**, en `titulos: { marcador, juego,
figuras }`; el juego y las figuras solo desde octubre. `temporadas_ganadas` sigue contando los del marcador.

#### Scenario: una temporada de octubre trae las tres
- GIVEN una temporada 2026-10 con marcador, juego y figuras
- WHEN se construye el archivo
- THEN trae tres competiciones con sus líderes, y un empate en cualquiera de ellas trae a todos los empatados

#### Scenario: septiembre trae solo el marcador
- GIVEN una temporada 2026-09 con juego y figuras en la instantánea
- WHEN se construye el archivo
- THEN trae solo la competición del marcador

#### Scenario: el medallero separa los títulos
- GIVEN una temporada 2026-10 cerrada en la que una persona gana el marcador y otra el juego y las figuras
- WHEN se construye el medallero
- THEN la primera tiene un título del marcador y la segunda uno del juego y uno de figuras

```yaml
checks:
  - type: regex
    file: v2/js/data/archivo.js
    pattern: 'export const DESDE_TRES_COMPETICIONES = .2026-10.;'
    describe: "las tres competiciones cuentan desde octubre"
  - type: regex
    file: v2/js/data/archivo.js
    pattern: 'cuenta.get\(nombre\).titulos\[clave\] \+= 1;'
    describe: "los títulos se cuentan por competición"
```

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js
