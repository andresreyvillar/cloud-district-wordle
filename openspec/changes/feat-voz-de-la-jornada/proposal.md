# Proposal — feat-voz-de-la-jornada

> **Slice:** `voz-de-la-jornada` (nuevo)

## Why

El resumen de la tarde **no dice nada la mayoría de los días**. Medido sobre la jornada en que se propone
esto: nueve jugadores, dificultad 3,89, **cero hechos detectados** por los comentarios. El mensaje salió
correcto y sin una línea con tono.

Los detectores no están mal: **miran la tabla, y la tabla no sabe lo que pasó**. Tiene nueve columnas —quién,
qué puzzle, cuántos intentos, la cuadrícula— y no tiene la hora a la que cada uno publicó, ni las reacciones,
ni quién contestó a quién. Todo eso está en el canal, y el canal no se lee al publicar.

## Lo que se añade

**Una lectura del canal del día**, con la misma llamada y el mismo token que ya usa la ingesta horaria, de la
que salen **señales**: hora real de publicación, reacciones por mensaje, respuestas por hilo y quién no
apareció. Con eso el resumen puede nombrar al madrugador, al rezagado, al más aplaudido y al que montó el
hilo.

**Un diccionario de frases** para que el día sin nada que contar tenga voz, con el registro elegido por la
dificultad de la jornada.

**Un meme del día**, en texto, cuando la jornada tenga una forma reconocible.

## Medido antes de proponerlo

**La señal del canal existe y es rica.** Sobre los mensajes recientes: los buenos resultados acumulan del
orden de **seis a nueve reacciones** (`boom` es el aplauso del grupo), y hay hilos de **37 y 14 respuestas**.
El premio al más aplaudido no saldría desierto.

**La hora real ya está en el pipeline y se tira a la basura.** `extract_slack.py:114` la extrae del `ts` del
mensaje y la emite en su línea; `add_results.py` no la escribe. Resolución de segundos, verificada.

**Y por eso el madrugador es posible ahora y no antes.** Con `created_at` —lo único que hay en la tabla— solo
el 34% de los resultados de una jornada tienen minuto distinto, porque el cron escribe por lotes cada hora.
Ese dato no sirve. El `ts` del canal sí.

## Por qué no se persiste nada

Las señales viven lo que dura la ejecución del cron. Dos razones, y la segunda es de corrección:

- No hace falta **esquema nuevo** para datos de comportamiento de personas identificables, en un repositorio
  público y con una tabla que ya es sensible.
- **Las reacciones son un dato vivo.** Guardarlas en la ingesta horaria las congelaría a media mañana;
  leerlas a las 17:00 cuenta el día completo.

## Procedencia del diccionario, y por qué importa

| Fuente | Qué se usa | Por qué |
|---|---|---|
| Refranero tradicional español | el refrán, nunca la ficha ni la selección | anónimo y de dominio público; la compilación editada **sí** tiene dueño |
| Proverbios chinos y japoneses tradicionales | el proverbio | igual de anónimos y públicos |
| Cultura pop, memes, foros | **nada literal** — se escriben originales | un guion de televisión o un post de foro son obra de terceros, y el repositorio es público |

Lo pidió el dueño explícitamente («memes, televisión, frases de internet, foros»), y se resuelve escribiendo
ese registro en vez de copiarlo. Sale mejor además: una pulla escrita para el Wordle encaja, y una cita pegada
con cinta se nota.

## What Changes

```
tools/refranero.py     NUEVO · solo datos: 45 frases de día, 30 de líder, 40 de mención, 12 memes
tools/senales.py       NUEVO · deriva señales del canal; el texto de los mensajes no sale de aquí
tools/voz.py           NUEVO · elige frase, menciones y meme a partir de señales y jornada
tools/post_ranking.py  lee el canal antes de componer, y pasa las señales por parámetro
```

## Impact

- El mensaje de la tarde gana menciones, una frase de cierre y, cuando la jornada tenga forma, un meme.
- **Ninguna cifra cambia.** No hay puntos nuevos, el marcador no se toca y el álbum tampoco.
- Una llamada más a Slack por ejecución del cron de la tarde. Sin scopes nuevos.
- El canal caído **no tumba el resumen**: se publica con lo que sale de la tabla.

## Out of Scope

- **Persistir las señales.** Ni columna ni backfill. Si la web quiere pintar horas, es otro slice.
- **Leer el contenido de los hilos.** Se cuentan las respuestas, no se leen.
- **Publicar imágenes.** El meme es texto. El bot tiene `files:write` y eso pide prudencia, no creatividad.
- **Elegir al azar.** Determinista por contrato (§10): el índice sale del número de jornada.

## Validation Gates

- `wslice slice validate voz-de-la-jornada` · `verify slice` · `verify gates`
- **Los umbrales de madrugador y rezagado se miden antes de fijarlos**, sobre el histórico del canal. El
  criterio: que la mención salga en una **minoría clara** de las jornadas. Un umbral que nombra a alguien
  todos los días no es una mención, es una columna.
- El mensaje compuesto se **revisa a ojo** antes de mergear, con la jornada real y sin publicar. Es lo que
  cazó «resolvión» cuando los gates estaban todos verdes.
- Prueba de mutación sobre el determinismo: sustituir el índice por azar debe poner en rojo
  `la-misma-jornada-da-la-misma-frase`.

## Capabilities

| Capability | Requirements |
|---|---|
| `ingesta` | ADDED — El canal se lee al publicar, y de él solo salen números |
| `estadisticas` | ADDED — Las señales del canal producen menciones, y cada una exige evidencia |
| `publicacion` | ADDED — El resumen diario siempre tiene algo que decir · El meme del día describe la jornada |
