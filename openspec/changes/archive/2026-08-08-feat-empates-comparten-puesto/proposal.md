# Proposal — feat-empates-comparten-puesto

> **Slice:** `empates-comparten-puesto` (openspec/slices/ranking/empates-comparten-puesto.md)

## Why

La tabla repartía puestos correlativos, así que dos jugadores con exactamente la misma media salían como 2º
y 3º. El tercero no ha hecho nada peor: la diferencia la fabricaba el desempate interno, que existe para que
el orden sea determinista.

Pasaba en el marcador de la temporada 0 ahora mismo — Andrés R. y Flavia Venturi, los dos con 3,58 — y lo
pidió el dueño al definir el resumen diario.

**Empatar no es un caso raro:** medido sobre las 186 jornadas que cuentan, el **62%** tiene empate en la
mejor nota del día.

## What Changes

```
tools/standings.py   puesto compartido en el marcador
tools/album.py       puesto compartido en el ranking de figuras, por la misma razón
tools/resumen.py     el mensaje sangra el empate en vez de repetir el número
```

Se compara sobre la media **publicada**, no sobre el flotante: si a la vista son el mismo número, separarlos
es incomprensible para quien lo lee.

## Un cambio de regla, declarado como tal

El escenario `empate-se-rompe-por-participacion` de `clasificacion-de-temporada` decía que en un empate «va
delante el que ha jugado más días», **y eso decidía el puesto**. Ahora decide **el orden de la lista** y no
el puesto: quien juega un día más no ha hecho una temporada mejor que quien empata con él, y si la
participación tiene que valer, ya lo hace la imputación desde dentro de la media.

Va como `## MODIFIED Requirements` y el slice queda actualizado. **Dos tests de ese slice cambiaron**, y no
es debilitarlos: uno afirmaba que los puestos son correlativos —ya no lo son— y el otro que el desempate da
mejor puesto —ahora ordena—. Los dos siguen comprobando el desempate, sobre lo que ahora decide.

Un tercer test, el del tamaño del mensaje, contaba los prefijos `1.` como sustituto de «cuántas filas tiene
el top». Con puestos compartidos ese proxy dejó de medir lo que decía: ahora cuenta líneas.

## Impact

- Afecta a la web y al mensaje a la vez, porque los dos leen la misma tabla: enseñan lo mismo sin tocarlas.
- Con los datos de hoy, en agosto **Cata y Dani Sanchez comparten el 4º** con 4,20, y en el ranking de
  figuras **tres jugadores comparten el 1º** con un 80%.
