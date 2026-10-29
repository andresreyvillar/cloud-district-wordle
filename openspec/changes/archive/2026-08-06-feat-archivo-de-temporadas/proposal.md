# Proposal — feat-archivo-de-temporadas

> **Slice:** `archivo-de-temporadas` (openspec/slices/ranking/archivo-de-temporadas.md)

## Why

Es la vista que da sentido a reiniciar el marcador cada mes: **sin archivo, ganar agosto no deja rastro en
septiembre**. Con temporadas mensuales el histórico pasa de ser una lista de partidas a un palmarés
colectivo.

## What Changes

```
v2/js/data/archivo.js     PURO: instantáneas → entradas del archivo y medallero acumulado
v2/js/ui/temporadas.js    la vista
v2/js/app.js              /temporadas deja de estar pendiente
v2/css/styles.css         tarjetas de temporada y tabla del medallero
```

## Dos filas, y está bien

Hoy el archivo tiene **dos entradas**: la temporada 0 —un bloque con todo el histórico anterior a agosto— y
agosto. El roadmap hablaba de «las 9 cerradas» porque se escribió antes de la decisión de la temporada 0.
Crecerá una fila al mes.

La temporada 0 se marca como **bloque histórico jugado con otras reglas**. Sin esa marca, la vista invitaría
a comparar una media de 181 jornadas sin imputar con la de un mes de 20 imputada, que no es la misma cosa
medida dos veces.

## Lo que este slice encontró

Al pintar el medallero salió que **la temporada 0 no tenía medallas de temporada**: el filtro por prefijo de
fecha no encontraba nada para el identificador `0`. Se arregló aparte, en `fix-medallas-temporada-cero`, y el
medallero real pasó de 6 filas a 17.

## Impact

- Solo lee. Sin efectos en datos.
- Cierra el punto 2.3 de la Fase 2. De la Fase 2 queda `/datos` (2.7).
- El medallero suma **por nombre**, porque así se publican las medallas. Declarado como defecto conocido.
