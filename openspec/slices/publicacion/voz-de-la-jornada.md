---
slice: voz-de-la-jornada
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 17 * * 1-5 — workflow post_ranking.yml: lee el canal del día y le pone voz al resumen"
events:
  emits: []
  consumes: []
specs:
  - publicacion
  - estadisticas
  - ingesta
tests_root: tests/slices/voz-de-la-jornada/
blocked: null
---

# El resumen lee el canal del día y cuenta lo que pasó, no solo lo que se puntuó

**Actor:** sistema (el cron de la tarde)
**Trigger:** la composición del mensaje que acompaña a la captura

## Contexto

El resumen ya sabe decir lo notable, pero **la mayoría de los días no dice nada**. Medido sobre la jornada en
que se propone este slice: nueve jugadores, dificultad 3,89, **cero hechos detectados**. El mensaje sale
correcto y sin una línea con gracia.

La causa no es que los detectores estén mal, es que **miran la tabla, y la tabla no sabe lo que pasó**. Tiene
nueve columnas: quién, qué puzzle, cuántos intentos, la cuadrícula. No tiene la hora a la que cada uno
publicó, ni las reacciones, ni quién contestó a quién. Todo eso está en el canal, y el canal no se lee al
publicar.

Este slice lo lee. A las 17:00, antes de componer el mensaje, se piden los mensajes del día y se derivan
**señales**: a qué hora publicó cada uno de verdad, cuántas reacciones recibió, cuánta conversación levantó y
quién no apareció. Con eso el resumen puede nombrar al que madrugó, al que lo dejó para el final, al más
aplaudido y al que armó el hilo — y cerrar con una frase de un diccionario cuando no haya nada mejor que
decir.

**Solo salen del canal señales, nunca texto.** Ni el mensaje de nadie, ni el contenido de un hilo, ni una
cita: números y horas. El repositorio es público y la restricción de no volcar conversaciones no se cumple a
medias.

## Trigger técnico

`post_ranking.py`, antes de componer el cuerpo del mensaje, que el workflow `post_ranking.yml` ejecuta a las
17:00 UTC de lunes a viernes. Se llama a `conversations.history` con la ventana del día —el mismo método y el
mismo token que ya usa `extract_slack.py`, sin permisos nuevos— y se derivan las señales. El cálculo del
texto recibe esas señales **por parámetro**: la red se queda en el borde (§10).

## Comportamiento observable

### la-hora-real-sale-del-canal
**WHEN** se compone el resumen de una jornada
**THEN** la hora que se usa para hablar de quién publicó antes o después es la del mensaje en el canal, no la
que quedó registrada al escribir la fila.

### el-que-madruga-se-nombra
**WHEN** alguien publicó su resultado claramente antes que el resto
**THEN** el mensaje lo menciona.

### el-que-lo-deja-para-el-final-se-nombra
**WHEN** alguien publicó su resultado mucho después que el resto
**THEN** el mensaje lo menciona.

### el-que-cierra-tarde-y-clava-la-nota-se-insinua
**WHEN** quien publica el último lo hace mucho después y además con una nota muy por encima del grupo
**THEN** la mención lo dice de otra manera que un simple retraso, porque el chiste es otro: había visto lo que
hacían los demás.

### el-mas-aplaudido-se-nombra
**WHEN** un resultado del día recibió más reacciones que los demás
**THEN** el mensaje nombra a su autor.

### el-que-mas-conversacion-levanta-se-nombra
**WHEN** un mensaje del día abrió un hilo con respuestas
**THEN** el mensaje nombra a quien lo abrió.

### sin-reacciones-no-hay-premio
**WHEN** ningún resultado del día recibió reacciones
**THEN** no se nombra a nadie como más aplaudido, en lugar de coronar a alguien con cero.

### quien-falto-sale-del-canal-no-de-la-tabla
**WHEN** alguien que juega habitualmente no publicó nada ese día
**THEN** el mensaje puede mencionarlo, y esa ausencia se deriva de que no hay mensaje suyo en el canal.

### siempre-hay-una-frase
**WHEN** se compone el resumen de una jornada con resultados
**THEN** el mensaje lleva una frase que resume el día, **aunque no haya ninguna señal ni ningún hecho
notable**.

### el-registro-sale-de-la-dificultad
**WHEN** la jornada fue dura para el grupo
**THEN** la frase es de las del registro duro, y no una de día fácil.

### la-frase-no-se-repite-al-dia-siguiente
**WHEN** dos jornadas consecutivas caen en el mismo registro
**THEN** cada una recibe una frase distinta del diccionario.

### la-misma-jornada-da-la-misma-frase
**WHEN** el mensaje de una jornada se compone dos veces
**THEN** la frase es la misma, sin reloj ni azar de por medio.

### el-lider-del-marcador-tiene-su-pulla
**WHEN** hay alguien en cabeza del marcador
**THEN** el mensaje lleva una frase que lo nombra.

### el-lider-del-album-tiene-la-suya
**WHEN** el álbum tiene un líder con puesto
**THEN** el mensaje lleva una frase que lo nombra, distinta de la del marcador.

### sin-lider-no-se-inventa-pulla
**WHEN** nadie llega al mínimo de partidas del álbum
**THEN** la frase del álbum no sale, en lugar de nombrar a quien no tiene puesto.

### el-mensaje-no-crece-sin-limite
**WHEN** la jornada da más material del que cabe
**THEN** el mensaje publica como mucho **tres añadidos**, eligiendo los de más peso, en lugar de encadenarlos
todos.

### la-frase-del-dia-es-el-ultimo-recurso
**WHEN** la jornada tiene meme y menciones de sobra para llenar el tope
**THEN** la frase del día cede su sitio, porque existe para el día que no tiene nada que contar.

### las-frases-no-se-pisan
**WHEN** un mensaje lleva varias frases
**THEN** son distintas entre sí, incluso si la misma persona manda en los dos rankings.

### el-meme-del-dia-necesita-que-pase-algo
**WHEN** la jornada encaja en una de las formas reconocidas —uno solo resuelve, todos fallan, todos empatan,
el líder se hunde, el último clava—
**THEN** el mensaje lleva el meme del día correspondiente, rellenado con los datos de esa jornada.

### sin-forma-reconocida-no-hay-meme
**WHEN** la jornada no encaja en ninguna forma
**THEN** no sale meme, en lugar de forzar uno que no describe lo que pasó.

### el-meme-es-texto-y-no-imagen
**WHEN** se publica el meme del día
**THEN** es una plantilla de texto rellenada con datos, y no se sube ninguna imagen al canal.

### el-canal-caido-no-tumba-el-resumen
**WHEN** la lectura del canal falla o no devuelve nada
**THEN** el resumen se publica igual con lo que sale de la tabla, sin las menciones que dependen del canal.

### del-canal-solo-salen-numeros
**WHEN** se derivan las señales de la jornada
**THEN** lo que viaja al resto del sistema son horas y recuentos, y en ningún caso el texto de un mensaje.

## Estado después

El mensaje que se publica gana las menciones que haya y una frase de cierre. Ninguna cifra del marcador
cambia: es la misma información con voz y con contexto.

Nada se persiste. Las señales viven lo que dura la ejecución del cron, y por dos razones: **no hace falta
esquema nuevo** para datos de comportamiento de personas identificables, y las **reacciones son un dato
vivo** —si se guardaran al ingerir cada hora quedarían congeladas a media mañana, mientras que leerlas a las
17:00 cuenta el día entero.

Con los datos del canal medidos al proponerlo, la señal es abundante: los buenos resultados acumulan del
orden de seis a nueve reacciones, y hay hilos de decenas de respuestas.

## Edge cases

- **Jornada sin resultados**: no hay mensaje, así que no hay frase ni menciones.
- **Reejecución del cron**: la misma jornada da la misma frase, porque el índice sale del número de jornada y
  no del reloj. Las menciones pueden cambiar entre dos ejecuciones si alguien reacciona en medio, y eso es
  correcto: la reacción es del día, no del instante.
- **Un solo jugador**: no hay madrugador ni rezagado —no hay con quién comparar— y la frase sale igual.
- **Mensajes que no son resultados**: el canal lleva charla, y contarla como resultado falsearía la hora y la
  ausencia. Solo se atribuye hora de publicación a los mensajes que llevan un resultado.
- **Mensajes del propio bot**: no cuentan para nada. El bot publica todas las tardes y sería siempre el más
  aplaudido de su propio resumen.
- **Diccionario agotado**: no se agota. El índice es cíclico, así que con quince frases por registro la
  repetición llega cada tres semanas, que es preferible a un catálogo infinito de chistes malos.
- **Ventana del día y husos**: la ventana se calcula sobre la fecha de la jornada, no sobre «las últimas 24
  horas», para que dos ejecuciones del mismo día cubran lo mismo.

## Fuera de alcance

- **Persistir las señales.** Ni columna nueva ni backfill. Si algún día la web quiere pintar horas de
  publicación, es otro slice y toca el esquema.
- **Leer hilos completos.** Se cuenta cuántas respuestas tiene un hilo, no lo que dicen. Bajar a leer el
  contenido de las respuestas sería traer conversación al sistema.
- **Elegir la frase al azar.** El proyecto es determinista por contrato (§10), y es lo que hace posible
  comprobar el mensaje entero en un test.

## Slices compañeros

- [[comentarios-de-la-jornada]] — lo notable según la tabla. Este slice le añade lo que solo sabe el canal.
- [[resumen-diario-compuesto]] — el mensaje donde todo esto se inserta.
- [[ingesta-por-id-de-slack]] — ya lee el canal cada hora, y ya extrae la hora real del mensaje: la emite en
  su línea y se descarta al escribir la fila. Este slice la usa sin pedirle nada a la tabla.
- [[medallas-en-el-resumen-diario]] — el otro bloque que se le añade al mensaje.
