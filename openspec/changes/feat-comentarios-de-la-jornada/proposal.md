# Proposal — feat-comentarios-de-la-jornada

> **Slice:** `comentarios-de-la-jornada` (openspec/slices/publicacion/comentarios-de-la-jornada.md)

## Why

El resumen ya cuenta la jornada, pero la cuenta en seco. Lo que hace que el grupo lo lea es el comentario:
que alguien resolviera en dos un día imposible, que otro se dejara la partida, que alguien no apareciera
justo el día duro.

## Alcance: los detectores, no la redacción generativa

**Fuera de alcance a propósito.** El brief contempla un modelo escribiendo el chiste; no hay proveedor
decidido ni credencial en el entorno, y llamar a un modelo por jornada cuesta dinero. La decisión es del
dueño.

La estructura queda preparada: los detectores emiten **hechos**, no texto. Cambiar quién redacta —la
plantilla de hoy, un modelo mañana— no toca la detección, que es lo único cubrible con tests.

## Frecuencias remedidas

Las del brief se midieron antes de la regla de días laborables. Rehechas sobre las **186 jornadas que
cuentan**:

| Comentario | Disparador | Brief | Real hoy |
|---|---|---|---|
| Sospechoso | ≤2 con media del día ≥4,0 | 0,06 | **0,07** |
| Sembrado | 1,5 mejor que la media | 0,35 | **0,24** |
| No inspirado | 1,5 peor que la media | 0,71 | **0,48** |
| No inspirado | **2,0** peor que la media | — | **0,24** ← el elegido |
| Rajado | ausencia en día de media ≥4,5 | — | **0,18** |

El brief ya pedía subir «no inspirado» a 2,0; con las reglas de hoy el margen viejo da 0,48 y el nuevo 0,24.

El umbral de día difícil **se reutiliza** de `badges.UMBRAL_DIA_DIFICIL` en lugar de declarar otro: «día
difícil» no puede significar dos cosas en el mismo mensaje.

## Dos fallos que enseñó el mensaje real, no un test

- **El mismo chiste tres veces.** Un día duro llenaba la sección con tres «se ha rajado» seguidos: la
  notabilidad ordena, y todos los hechos de la clase más notable se comían el hueco. Ahora sale **un
  comentario por tipo**, y las ausencias van juntas en una línea — tres líneas señalando a tres ausentes
  dejan de ser una broma y son una lista de morosos.
- **«Carlos, Edu Noeda no ha aparecido».** El castellano concuerda, y el catálogo no tenía plural.

Y uno más, del mismo vistazo: se llamaba «rajada» a **Carmen, que jugó una vez en marzo**. Las ausencias se
miden ahora contra quien juega **esta temporada**, no contra quien jugó alguna vez.

## Un mutante que sobrevivió

El que permite repetir el mismo tipo de chiste. El test usaba las **ausencias**, que van agrupadas en un
solo hecho: la línea salía una vez aunque no hubiera deduplicación por tipo, así que el test parecía
cubrirlo y no cubría nada. Rehecho con tres personas disparando «no inspirado», que es un hecho por persona.

## Impact

- Cierra el punto 5.6 en su parte determinista.
- Deja 5.7 (imagen de la obra del día) como lo único pendiente de la fase, y bloqueado por la misma
  decisión: proveedor, credencial y coste.
