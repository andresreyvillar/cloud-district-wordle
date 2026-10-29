# Proposal — feat-ficha-de-jugador

> **Slice:** `ficha-de-jugador` (openspec/slices/estadisticas/ficha-de-jugador.md)

## Why

El marcador publica que tu media de temporada es 4,12 y no dice de dónde sale. Con el modelo de imputación
eso dejó de ser un detalle: **parte de esa media son jornadas que no jugaste**. Una regla que penaliza y no
se puede mirar dentro es una regla que el grupo no va a aceptar, y con razón.

Y hay un agujero más simple: la clasificación lista 21 jugadores y **ninguna fila lleva a ningún sitio**.

## What Changes

```
v2/js/data/ficha.js        PURO: instantáneas → ficha y palmarés
v2/js/ui/jugador.js        la vista
v2/js/ui/temporada.js      el marcador y el podio enlazan a la ficha (fila extraída y exportada)
v2/js/app.js               la ruta /t/<AAAA-MM>/j/<U…> deja de estar pendiente
v2/css/styles.css          los bloques de la ficha
```

**No toca Python, ni el esquema, ni el pipeline.** Todo lo que la ficha muestra está ya en la instantánea
([ADR 0008](../../decisions/0008-donde-vive-el-calculo.md)): la media, el desglose jornada a jornada, la
distribución y las medallas. Lo único que se arma es el palmarés, cruzando instantáneas ya cargadas.

## La pieza que justifica la vista

**El coste de faltar.** La ficha pone las dos medias una al lado de la otra y publica la diferencia con su
signo:

```
MEDIA DE LO JUGADO  3,50   →   MEDIA DE TEMPORADA  3,87        +0,37
```

Esa cifra es la regla de imputación aplicada a una persona concreta, y es lo que convierte una fórmula en
algo comprobable. Cuando la temporada no imputa —la 0— la ficha **lo dice** en lugar de publicar un cero:
un cero se lee como «faltar no te costó nada», cuando lo cierto es que en esa temporada faltar no se medía.

## Decisiones de la implementación

- **El identificador de la ruta es el de Slack.** Un renombre no puede romper un enlace pegado en el canal,
  y el palmarés cruza por identidad y no por nombre: es el mismo fallo que ya se arregló en los resultados.
- **La fila del marcador se extrajo a `filaDeMarcador(fila, temporada)` y se exporta.** El enlace es
  comportamiento observable del slice, así que se verifica sin navegador en lugar de con una captura.
- **Con más de 40 jornadas el desglose se agrupa por meses.** La temporada 0 tiene 181: la tira de casillas
  no cabe en la línea y una lista de 181 entradas no se lee.
- **La ficha no falla nunca.** Con el fallback SPA del Worker cualquier ruta responde 200, así que un
  identificador inexistente es un estado de la vista, no un error del router.

## Impact

- Sin efectos en datos: la vista solo lee. No escribe en Supabase ni guarda nada en el navegador.
- Cierra el punto 2.5 de la Fase 2 del roadmap.
- Deja declarado un defecto que **no** arregla: `tools/badges.py` agrupa medallas por `player_name` y no por
  identidad. Hoy la relación es 1:1 y la ficha cruza por nombre; arreglarlo es un slice de identidad.
