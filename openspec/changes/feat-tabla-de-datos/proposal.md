# Proposal — feat-tabla-de-datos

> **Slice:** `tabla-de-datos` (openspec/slices/dashboard/tabla-de-datos.md)

## Why

Es la vista que se mira **cuando no te fías de una cifra**, y lo que permite retirar la v1 sin perder la
única forma de comprobar que el ranking no se ha inventado nada.

## What Changes

```
v2/js/data/tabla.js       PURO: filas crudas + instantáneas → la tabla
v2/js/data/temporada.js   PURO: a qué temporada pertenece una fecha. UNA definición para toda la web
v2/js/data/results.js     el borde llama `mes` al mes, no `temporada`
v2/js/ui/datos.js         la vista
v2/js/app.js · styles.css
```

## El fallo que encontró el navegador, y que ya había cometido antes

La primera versión de la tabla decía **«1543 resultados · 70 cuentan para su temporada»**. Setenta de mil
quinientos.

La causa: buscaba la instantánea con `instantaneas.get(fila.temporada)`, donde `temporada` era el mes de la
fecha. Para las 1502 filas anteriores a agosto ese mes es `2026-05`, `2026-06`… y **ninguna existe como
temporada**: todas son la temporada 0. La tabla no fallaba, simplemente no afirmaba nada.

**Es el mismo error que `fix-medallas-temporada-cero` arregló el día anterior en `tools/badges.py`**, donde
el síntoma fue «cero medallas de temporada en 181 jornadas». Dos veces, en dos lenguajes, la misma causa:
derivar la temporada de una fecha por su cuenta en lugar de preguntárselo al modelo.

Por eso el arreglo no es una línea sino tres decisiones:

1. `v2/js/data/temporada.js` es **la única** definición en la web, y **lee el límite de las reglas
   publicadas** en lugar de escribirlo: sería la tercera copia de `seasons.INICIO_TEMPORADAS`.
2. Sin límite publicado, **no se adivina**: la fila no afirma a qué temporada pertenece.
3. El borde de datos deja de llamar `temporada` al mes. Se llama `mes`, porque eso es lo que es.

## Impact

- Cierra el punto 2.7 y, con `ruta-invalida`, la Fase 2 entera.
- Verificado en el navegador: 1572 filas, todas con su columna resuelta.
