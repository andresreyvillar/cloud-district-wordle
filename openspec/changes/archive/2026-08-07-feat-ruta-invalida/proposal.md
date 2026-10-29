# Proposal — feat-ruta-invalida

> **Slice:** `ruta-invalida` (openspec/slices/dashboard/ruta-invalida.md)

## Why

**El comportamiento ya existe** desde el esqueleto, que es un pack `Slice: N/A`. Lo que no existía es nada
que lo protegiera: un refactor del router podía llevarse por delante la única vista que avisa de que el
enlace está roto, y ningún test se habría enterado.

Y el caso llega solo, porque los enlaces de esta web se pegan en el canal: una temporada que no existe, un
identificador copiado a medias, una ruta antigua después de un cambio. Con el fallback SPA **ninguna de esas
falla**: devuelven 200 y una página vacía.

## What Changes

Solo tests y spec: **ni una línea de producción**. Es el objetivo — este pack no añade comportamiento, lo
fija.

```
openspec/slices/dashboard/ruta-invalida.md
tests/slices/ruta-invalida/ruta.test.js
```

## Un pack sin rojo previo, y por qué se acepta

El protocolo pide TDD rojo. Aquí los siete tests pasan desde el primer momento, porque describen algo que ya
funciona. Lo que demuestra que sirven de algo no es el rojo inicial sino **el Gate 4c**: cuatro mutantes en
el router y en el armazón, y los cuatro caen. Sin esos mutantes este pack sería decorativo.

## Impact

- Cierra el punto 2.6 y, con `tabla-de-datos`, **la Fase 2 entera**.
- Fija de paso la distinción que más se va a confundir: **«no existe esa ruta» no es «ese jugador no jugó esa
  temporada»**. Lo segundo tiene ficha ([[ficha-de-jugador]]); lo primero, no.
