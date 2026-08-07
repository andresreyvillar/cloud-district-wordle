# Proposal — fix-reglas-ratificadas

> **Slice:** `reglas-explicadas` (modificación: dos tests reescritos, sin escenarios nuevos)

## Why

El grupo ha ratificado **las trece reglas aplicadas** (2026-08-07). El catálogo las tenía como no votadas.

Y al aplicarlo saltó un test que llevaba dos días diciendo una mentira: `imputacion-por-dificultad` constaba
como **acordada sin aplicar** cuando `standings.imputar()` se usa en la clasificación **desde el 5 de
agosto**. Lo mismo con `sin-minimo-para-clasificar`. La página decía que la tabla no imputaba mientras
imputaba, que es exactamente el fallo que esa página existe para no cometer.

## What Changes

- Las 13 reglas aplicadas pasan a `votada=True`.
- `imputacion-por-dificultad` y `sin-minimo-para-clasificar` pasan a `estado=APLICADA` —lo están— y **siguen
  sin votar**: son las dos del modelo de participación y el grupo no las ha ratificado.
- **`rules.MARGEN_DE_IMPUTACION` desaparece.** El margen se lee de `standings.MARGEN`, que es la constante
  que el cálculo usa. Era la copia que el propio módulo se había comprometido a borrar «cuando el modelo se
  implemente», y llevaba dos días duplicada.

Resultado: **15 aplicadas, 13 votadas**, y las dos sin votar son justo las que cambian quién gana el mes.

## Dos tests reescritos, y por qué no es debilitarlos

- `el-modelo-de-imputacion-consta-como-acordado-sin-aplicar` afirmaba una cadena. Ahora **demuestra el
  estado contra el cálculo**: monta una temporada con una ausencia y comprueba que la tabla trae una jornada
  imputada. Un estado que solo se afirma es lo que permitió el desfase de dos días.
- `hay-reglas-aplicadas-que-el-grupo-no-ha-votado` seguía siendo cierto, pero por otras reglas. Ahora fija el
  conjunto exacto y **es un cable trampa a propósito**: si el grupo vota esas dos, se pone rojo y alguien
  tiene que actualizar lo que la página afirma.

## Impact

- La página de reglas pasa a mostrar 13 ratificadas y 2 aplicadas pendientes de voto.
- Instantáneas rematerializadas: las reglas viajan dentro de la carga útil.
- **Queda una pregunta para el dueño**: si el grupo también ratificó el modelo de imputación, son 15 y no 13.
  Se ha asumido que no, porque es la regla que cambia quién gana y merece votarse aparte.
