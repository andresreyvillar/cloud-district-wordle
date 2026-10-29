# Un espejo de dos filas ya es geométrico, pero sigue sin ser gesta

## El caso

La jornada #1701, dibujo de Raquel:

```
⬛🟨⬛🟨⬛     .Y.Y.
🟩⬛🟨⬛🟩     G.Y.G
🟩🟩🟩🟩🟩     GGGGG
```

Palíndromo perfecto en las dos filas, y se etiquetaba **«flores»**: `.Y.Y.` es una fila limpia de amarillos
sobre suelo verde, que es la definición literal de la regla de la flor, y el espejo exigía tres filas de cuerpo.

## Qué cambia, medido

El umbral de la **categoría** baja de 3 a 2. Sobre las 1.758 cuadrículas del histórico:

```
cambia 1 de 1758
   #1701  Raquel  .Y.Y./G.Y.G  flores → geometrico
```

**Una sola.** Se avisó de que cuatro flores legítimas del histórico se verían afectadas —`.YYY./YY.YY` de
Claire y de Gabi entre ellas— y **el aviso era erróneo**: todas son anteriores al corte de
`PRIMERA_JORNADA_DEL_ORDEN_NUEVO`, así que el «no retroactivo» ya las protege. El aviso valía para un cambio
retroactivo, y este no lo es.

## Los dos umbrales divergen ahora, y a propósito

```
figures.CUERPO_MINIMO_DEL_ESPEJO = 2    ← clasificar: «esto es un espejo»
badges.CUERPO_MINIMO_DEL_LOGRO   = 3    ← premiar:    «esto casi no pasa nunca»
```

Estuvieron compartidos, y con razón: sin corte de reglas, un umbral bajo en la categoría robaba la figura a
flores del histórico. Con el corte esa objeción desaparece. Reconocer un dibujo y considerarlo una gesta son
decisiones distintas: con umbral 2 el logro lo tendrían nueve de veintitrés jugadores y dejaría de distinguir a
nadie — el error ya cometido con una medalla que tenían quince de dieciséis.

**Que divergan está fijado por un test**, para que nadie los vuelva a unir creyendo que la duplicidad es un
descuido.

## Fixtures que resultaron medir otra cosa

`FLOR = "Y...Y/..Y../GGGGG"`, usado en cuatro ficheros de test como «una flor», **es palíndromo en sus dos
filas**. Al bajar el umbral dejó de ser flor, y esos tests empezaron a medir la regla del espejo sin querer.
Sustituido por `Y..../..Y../GGGGG`, que es flor y no tiene simetría.

Y el test de «patrón no ambiguo» usaba ese mismo fixture, así que su premisa era falsa. Ahora **comprueba** que
el fixture cumple una sola de las cuatro reglas, en lugar de suponerlo.

## Qué no hace

- No reclasifica el histórico: cero cambios antes del corte.
- No toca el logro del espejo perfecto, que sigue en tres filas.
