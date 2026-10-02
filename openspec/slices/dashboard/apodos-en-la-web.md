---
slice: apodos-en-la-web
status: proposed
kind: action
actor: grupo
trigger:
  type: ui
  surface: web
  detail: "cualquier vista de la v2 que nombre a un jugador con apodo declarado: temporada, hoy, ficha, archivo, datos, juego"
events:
  emits: []
  consumes: []
specs:
  - dashboard
tests_root: tests/slices/apodos-en-la-web/
blocked: null
---

# La web puede nombrar a un jugador con un apodo, sin cambiar quién es

**Actor:** el grupo
**Trigger:** abrir cualquier vista que nombre a un jugador con apodo

## Contexto

El grupo bromea en el canal, y el dueño quiere que la web lo recoja: Carrillo está jugando estos días con
ayuda de ChatGPT, y la web le llama «C̶a̶r̶r̶i̶l̶l̶o̶ ChatGPT», con su nombre tachado.

Un apodo es **presentación, no identidad**. En la web, a un jugador lo identifica su id de Slack —las rutas
de la ficha, el selector del juego, sus marcas—, y el nombre es solo el texto que se pinta. Renombrarlo en la
tabla partiría su historial en dos (la identidad real, de facto, cruza nombres en medallas y en el archivo),
y además está prohibido: la tabla de producción no se toca para esto.

## Comportamiento observable

### el-apodo-sustituye-al-nombre-en-cada-vista
**WHEN** una vista de la web nombra a un jugador con apodo declarado —podio, marcador, titular, álbum,
juego de la temporada, logros, hoy, ficha, archivo, medallero, tabla de datos, selector y ranking del
SuperWordleBros—
**THEN** pinta el apodo en lugar del nombre.

### la-identidad-no-cambia
**WHEN** se pinta a un jugador con apodo
**THEN** su enlace a la ficha, el valor del selector del juego y lo que se envía al guardar una marca siguen
siendo su id de Slack, como antes.

### quien-no-tiene-apodo-sale-igual
**WHEN** se pinta a un jugador sin apodo declarado
**THEN** sale su nombre, exactamente como antes de este slice.

### el-nivel-del-juego-pinta-el-apodo
**WHEN** se monta un nivel del SuperWordleBros en el que juega alguien con apodo
**THEN** la etiqueta de su tramo lleva el apodo, también en los niveles congelados antes de declararlo; el
nivel guardado no cambia.

### el-apodo-va-escapado
**WHEN** se pinta un apodo
**THEN** pasa por el mismo escape que un nombre: un apodo es texto, no marcado.

### slack-no-lleva-apodos
**WHEN** el bot publica en el canal
**THEN** nombra a todos por su nombre de Slack: los apodos son solo de la web (decisión del dueño).

## Estado después

Ninguno: solo pinta. Nada se escribe en Supabase.

## Edge cases

- **El tachado es Unicode** (U+0336 tras cada letra, decisión del dueño), no HTML: así es texto plano y vale
  igual en el HTML, en un `<option>` y en el lienzo del juego.
- **Un renombre en Slack** pierde el apodo, porque el apodo se declara por nombre: el jugador renombrado sale
  con su nombre nuevo, que es lo neutro.
- **Quitar el apodo** es borrar su línea de la tabla: no deja rastro.

## Fuera de alcance, y por qué

- **Slack**: decisión del dueño, solo la web.
- **Apodos que caducan solos**: el dueño lo quita cuando acabe la broma.
- **Unificar el pintado de nombres en un componente**: hoy hay diecisiete puntos con el mismo patrón copiado;
  este slice los envuelve sin refactorizarlos.

## Slices compañeros

- [[ficha-de-jugador]] — la ruta por id que no cambia.
- [[ranking-del-juego]] — el selector y el ranking del SuperWordleBros.
