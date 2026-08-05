# Deltas de `publicacion` — chore-nombres-de-logros

## MODIFIED Requirements

### Requirement: El nombre que se publica sale del catálogo, y renombrar reescribe el pasado

El texto del resumen usa **el nombre del catálogo**, no una cadena escrita en el mensaje. Renombrar una
medalla cambia por tanto lo que lee el canal, sin tocar la composición del mensaje.

Y tiene una consecuencia que conviene decir: como el palmarés **se calcula y no se guarda**, renombrar
reescribe el pasado. Quien ganó `Pleno` en febrero, ahora ganó `Metrónom@`. Aquí no hay daño —la rama no está
mergeada, así que nunca se publicó— pero la propiedad es permanente: **cada renombrado futuro reescribe todo
el histórico de esa medalla**. Es el precio de no almacenarlas, y se paga en cada bautizo.

#### Scenario: el nombre anunciado es el del catálogo
- GIVEN una medalla ganada en la jornada que se publica
- WHEN se compone el texto del resumen
- THEN el nombre que aparece es el que declara el catálogo

#### Scenario: dos medallas nunca comparten nombre
- GIVEN el catálogo de medallas
- WHEN se listan sus nombres
- THEN no hay dos iguales, porque el canal no podría distinguirlas

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py
