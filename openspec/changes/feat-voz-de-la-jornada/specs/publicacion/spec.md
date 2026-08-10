# Deltas de `publicacion` — feat-voz-de-la-jornada

## ADDED Requirements

### Requirement: El resumen diario siempre tiene algo que decir

El mensaje de la tarde lleva **siempre** una frase que resume la jornada, aunque no haya ninguna señal del
canal ni ningún hecho notable. Es lo que separa un marcador de un informe: medido sobre la jornada en que se
propone esto —nueve jugadores, dificultad 3,89— los detectores encontraron **cero** hechos y el mensaje salió
sin una sola línea con tono.

El **registro** de la frase sale de la dificultad de la jornada, que ya se calcula: día fácil, día normal, día
duro. Así el tono lo elige el dato y no una decisión escrita a mano.

Además de la frase del día, el mensaje lleva **una pulla para quien manda en el marcador y otra para quien
manda en el álbum**, cuando hay líder. Sin líder de álbum —nadie llega al mínimo de partidas— esa frase no
sale: no se nombra a quien no tiene puesto.

Las frases salen de un **diccionario de refranes tradicionales y pullas escritas para el grupo**, con **quince
por registro**. Menos de diez y el grupo se las sabe en dos semanas; quince dan más de un mes sin repetir. No
se copia ninguna compilación ajena: el refrán tradicional es de dominio público, pero la selección y las
fichas de un refranero editado tienen dueño y el repositorio es público.

La frase se elige **derivándola del número de jornada**, no del reloj ni del azar. El proyecto es determinista
por contrato (§10), y es lo que permite comprobar el mensaje entero en un test y que dos ejecuciones del mismo
cron publiquen lo mismo. El precio declarado: el orden es cíclico y por tanto predecible si alguien se pone a
mirar.

Las frases de un mismo mensaje **no se repiten entre sí**, y las menciones del canal van **encima** de la
frase, no en su lugar: el día raro conserva su titular y el día corriente tiene voz.

```yaml
checks:
  - type: cli-command
    command: python3 tools/preview_resumen.py
    note: compone el mensaje de una jornada sin publicarlo, para revisarlo antes de que lo lea el grupo
```

#### Scenario: el día sin nada que contar tiene frase
- GIVEN una jornada sin hechos notables y sin señales del canal
- WHEN se compone el resumen
- THEN el mensaje lleva una frase que resume el día

#### Scenario: el registro lo elige la dificultad
- GIVEN una jornada que el grupo resolvió con muchos intentos
- WHEN se compone el resumen
- THEN la frase es de las del registro duro

#### Scenario: dos jornadas seguidas no repiten frase
- GIVEN dos jornadas consecutivas del mismo registro
- WHEN se componen sus resúmenes
- THEN las frases son distintas

#### Scenario: la misma jornada da el mismo mensaje
- GIVEN una jornada
- WHEN se compone su resumen dos veces
- THEN el texto es idéntico

#### Scenario: quien manda se lleva su pulla
- GIVEN una temporada con líder de marcador y líder de álbum
- WHEN se compone el resumen
- THEN el mensaje nombra a los dos, con frases distintas

#### Scenario: sin líder de álbum no se inventa la pulla
- GIVEN una temporada en que nadie llega al mínimo de partidas del álbum
- WHEN se compone el resumen
- THEN no sale frase de álbum

### Requirement: El mensaje no crece sin límite

El mensaje publica **como mucho tres añadidos** sobre los bloques que ya tenía. Sin tope, una jornada movida
encadenaría doce bloques —jugador del día, obra, marcador, figuras, tres comentarios, cinco menciones, frase,
dos pullas y meme— y eso es un muro de texto que **nadie lee en un canal de Slack**. El efecto sería el
contrario del que persigue este slice.

La prioridad, de más peso a menos:

1. **el meme del día**, si la jornada tiene una forma reconocible — es lo que describe lo que pasó;
2. **las menciones con más evidencia** — más reacciones, más respuestas, más distancia en la hora;
3. **la frase del día**, que cede el sitio cuando hay algo mejor.

Que la frase sea la última no la contradice: existe para el día que **no tiene nada que contar**, y ese día es
la única que hay, así que sale siempre que hace falta. Tope decidido por el dueño al implementar, después de
ver que lo especificado sin límite empeoraba el mensaje.

#### Scenario: la jornada con mucho material no encadena todo
- GIVEN una jornada con meme, cinco menciones y frase disponible
- WHEN se compone el resumen
- THEN se publican como mucho tres añadidos

#### Scenario: la frase cede el sitio cuando hay algo mejor
- GIVEN una jornada con meme y menciones suficientes para llenar el tope
- WHEN se compone el resumen
- THEN la frase del día no sale

#### Scenario: el día sin nada conserva su frase
- GIVEN una jornada sin meme y sin menciones
- WHEN se compone el resumen
- THEN la frase del día sale

### Requirement: El meme del día describe la jornada, y si no la describe no sale

El mensaje puede llevar un **meme del día**: una plantilla de texto que nombra una forma reconocible de
jornada y se rellena con sus datos. Las formas son de la jornada, no del jugador: uno solo resuelve, todos
fallan, todos empatan en el mismo número, el líder de la temporada se hunde, el último de la tabla clava,
nadie dibuja nada.

**Es texto, nunca una imagen.** Subir una imagen ajena al canal desde un bot que tiene `files:write` sería un
problema de derechos y de permisos a la vez, y la plantilla en texto consigue el mismo chiste sin ninguno de
los dos. Por la misma razón las plantillas son **escritas para este canal** y no citas de guiones de
televisión ni de posts de foros: el refrán tradicional es de dominio público, un guion no.

Las condiciones se evalúan **en orden** y se usa la primera que se cumple, de modo que la forma más llamativa
gana sobre la genérica. Si no se cumple ninguna, **no hay meme**: forzar uno que no describe lo que pasó es
peor que no ponerlo, porque un chiste que no encaja delata que lo pone una máquina.

#### Scenario: la jornada con forma reconocible tiene meme
- GIVEN una jornada en que solo una persona resolvió la palabra
- WHEN se compone el resumen
- THEN el mensaje lleva el meme correspondiente a esa forma, con su nombre

#### Scenario: la jornada corriente no tiene meme
- GIVEN una jornada que no encaja en ninguna forma reconocida
- WHEN se compone el resumen
- THEN no sale ningún meme

#### Scenario: el meme no sube imágenes
- GIVEN una jornada con meme
- WHEN se publica el mensaje
- THEN el meme viaja como texto y no se adjunta ninguna imagen

#### Scenario: los comentarios no los sustituye la frase
- GIVEN una jornada con hechos notables
- WHEN se compone el resumen
- THEN los comentarios se publican y la frase también

verified-by:
  - tests/slices/voz-de-la-jornada/test_voz.py
