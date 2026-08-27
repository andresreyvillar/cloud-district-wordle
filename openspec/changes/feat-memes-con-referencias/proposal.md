# El meme del día cita algo, y los ausentes salen por clasificación

## Por qué

Dos avisos del dueño leyendo el mensaje.

**«El meme del día es muy malo.»** Y con razón: había 79 plantillas y **ni una sola referencia reconocible**.
Se llamaba «meme» y no citaba nada — eran juegos de palabras genéricos. Un meme que no remite a nada no es un
meme, es una frase.

**«Los ausentes deberían ir por orden de puntuación.»** Salían por orden alfabético: `sorted()` sobre los
nombres. Hoy eso nombraba a *Carlos, Carlos H. y Carmen* —que van 13º, 13º y 15º— y escondía en «y otros 3» a
**Claire, segunda de la tabla**. La ausencia de quien va segundo es más noticia que la de quien va decimoquinto.

## Qué cambia

| | antes | ahora |
|---|---|---|
| plantillas de meme | 79 | **264** |
| con referencia reconocible | 0 | **166 (62%)** |
| orden de los ausentes | alfabético | **por clasificación** |

Las referencias se **buscaron antes de escribirlas**, para no tirar de memoria: *Aquí no hay quien viva* y sus
frases que entraron en el lenguaje popular, El Risitas y la paellera —señalado como el meme más famoso de
España—, Chiquito, el «Sayonara, baby» del doblaje español de Terminator 2, y el «wololo» del Age of Empires.
Van **adaptadas al juego** en lugar de citadas: «unos se han llevado el bote y otros la silla azul», «YOU DIED», «rayo azul para {jugador}»,
«no hay errores, solo accidentes felices», «unos en el mundo normal y otros en el del Revés».

## Intercaladas, no apiladas al final

Añadidas al final del registro, las referencias no se veían: `_del_ciclo` elige por `jornada % len`, así que
los índices bajos seguían siendo los genéricos y la jornada de hoy caía justo en el último de los viejos.

Ahora se **alternan** referencia y genérica, empezando por referencia. Con eso la jornada #1694 pasa de «hoy
hemos vivido dos jornadas distintas: la del 2 y la del 7» a «unos se han llevado el bote (2) y otros la silla
azul (7)».

## Qué no hace

- **Sigue sin azar.** El orden es cíclico por número de jornada (§10), porque `random` rompería los golden
  tests del mensaje. Lo que se ha ampliado es el material.
- No publica imágenes: el meme es una plantilla de texto, por derechos y porque el bot tiene `files:write`.
- No cambia cuántos ausentes se nombran, solo **cuáles**: siguen siendo tres más la coleta, para que el
  mensaje no crezca con el grupo.
