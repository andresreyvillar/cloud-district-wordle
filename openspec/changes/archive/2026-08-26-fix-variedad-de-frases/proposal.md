# El mensaje diario dejaba de sonar variado

## Por qué

El dueño leyó el canal y avisó de dos cosas. Las dos eran ciertas, y las dos se midieron antes de tocar nada.

**El meme repetía la misma frase.** Se elige por condición y gana la primera que se cumple; `dia-de-dos-mundos`
es el catch-all, dispara con `peor - mejor >= 4` —cualquier día en que alguien falle y alguien resuelva bien— y
**tenía una sola plantilla**. Medido sobre 199 jornadas: salía en el 19% de los días y era **el 83% de todos
los memes publicados**. En agosto se publicó la misma frase en #1684, #1688, #1691 y #1692.

Y había un segundo defecto al lado: **8 de los 13 memes escritos no tenían condición implementada**. Texto que
nunca se ejecutaba, dando la falsa impresión de que había trece formas disponibles.

**La sospecha repetía el molde, no la frase.** Aquí el aviso apuntaba a otra causa: en 50 apariciones salen 49
textos distintos, así que la rotación funciona. Lo que no cambiaba era la forma — **🤨 en las 24 frases y la
nota citada en 22 de 24**—, así que veinticuatro textos distintos se leían como un solo chiste.

## Qué cambia

| | antes | ahora |
|---|---|---|
| plantillas de meme | 13 (una por condición) | **79** en 11 condiciones |
| condiciones implementadas | 5 de 13 | **11 de 11** |
| textos de meme distintos publicados en 199 jornadas | 5 | **57** |
| peso de `dia-de-dos-mundos` sobre los memes | 83% | **24%** |
| frases de sospecha | 24 + 18 | **36 + 30** |
| sospechas con 🤨 | 100% | **66% / 60%** |
| total de frases del proyecto | 315 | **406** |

Se descartó `remontada-del-dia`: su condición se solapa con el bloque de relevo y definirla aquí duplicaría
ese criterio en dos sitios.

**Sigue sin azar.** `_del_ciclo` elige por número de jornada (§10): `random` daría variedad y rompería los
golden tests del mensaje. Lo que se ha ampliado es el material, no el mecanismo.

## Qué no hace

- No toca datos ni esquema: es texto y selección.
- No publica imágenes. El meme es una plantilla de texto, por derechos y porque el bot tiene `files:write`.
- Cuatro condiciones (`solo-uno-lo-saca`, `todos-fallan`, `todos-el-mismo-numero`, `nadie-dibuja-nada`) siguen
  sin haber salido nunca en el histórico. Ahora **están implementadas**; simplemente describen jornadas que
  todavía no han ocurrido.
