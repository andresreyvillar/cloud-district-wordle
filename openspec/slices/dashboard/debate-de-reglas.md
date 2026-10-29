---
slice: debate-de-reglas
status: shipped
kind: action
actor: jugador
trigger:
  type: ui
  surface: web
  detail: "pestaña Debate — /debate: votar una norma abierta o proponer una nueva, eligiendo quién eres"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - resultados
tests_root: tests/slices/debate-de-reglas/
blocked: null
---

# En la pestaña Debate se votan las normas abiertas y se proponen nuevas

**Actor:** quien juega
**Trigger:** votar o enviar una propuesta en la pestaña Debate

## Contexto

Las reglas se deciden conversando en el canal, y la conversación se pierde entre resultados. El dueño quiere un
sitio fijo para debatirlas: las normas en votación, con su recuento, y una zona de sugerencias donde cada uno
proponga y diga quién es.

La primera votación es la **norma anti-spoilers**: el 14 de octubre de 2026 un comentario con una pista evidente
(«el juego no me dejaba poner la Ñ») hizo que la jornada #1742 se resolviera mejor a partir de las 10:00. Medido
sobre 211 jornadas, publicar tarde no da ventaja por sí solo: la ventaja aparece el día del spoiler. El grupo
decide qué hacer, incluida la opción de no hacer nada.

**Quién eres se elige**, como en el SuperWordleBros (decisión del dueño): sin cuentas ni contraseñas. Por eso
**los votos se ven con su nombre**: si alguien vota en nombre de otro, el otro lo ve y lo cambia.

**Las propuestas se publican al enviarlas y se votan** (decisión del dueño, 2026-10-15). Al principio quedaban
pendientes hasta que el dueño las aprobaba; el primer día llegaron tres y el dueño prefirió verlas todas y que el
grupo las vote a favor o en contra. El dueño conserva una salida: una propuesta marcada `rechazada` deja de verse,
porque la web es pública y el texto va firmado con el nombre de un compañero identificable.

La web **no escribe en las tablas**: llama a dos funciones de la base de datos que deciden qué entra, igual que
`registrar_tiempo`. El dueño aprueba propuestas y cierra votaciones desde Supabase.

## Comportamiento observable

### el-debate-tiene-su-pestana
**WHEN** se abre `/debate` o se pulsa la pestaña Debate del menú
**THEN** se ve el debate sin tener que bajar por la página: nació como apartado al final de Info y en móvil
quedaba a unos 11.000 px del principio. Info conserva un párrafo que lleva a la pestaña.

### el-enlace-viejo-lleva-al-debate
**WHEN** alguien abre `/info#debate-de-reglas`, el primer enlace que se compartió
**THEN** llega a la pestaña Debate y la barra dice `/debate`

### la-votacion-abierta-se-ve-con-su-recuento
**WHEN** se abre el debate y hay una votación abierta
**THEN** se ve su pregunta, cada opción con cuántos votos lleva y quién la ha votado

### se-vota-eligiendo-tu-nombre
**WHEN** alguien elige su nombre y vota una opción de una votación abierta
**THEN** su voto queda guardado y el recuento se actualiza

### sin-nombre-no-se-vota
**WHEN** alguien pulsa votar sin haber elegido su nombre
**THEN** no se envía nada y se le pide que elija quién es

### el-voto-se-puede-cambiar
**WHEN** alguien que ya votó elige otra opción mientras la votación está abierta
**THEN** cuenta solo su último voto: una persona, un voto

### una-votacion-cerrada-no-admite-votos
**WHEN** el dueño cierra una votación
**THEN** se ve su resultado sin botones de votar, y la base de datos rechaza cualquier voto que llegue

### una-propuesta-se-publica-al-momento
**WHEN** alguien envía una propuesta con su nombre, un título y una explicación
**THEN** se guarda, se le dice que ya está publicada y aparece en el debate con su autor

### las-propuestas-rechazadas-no-se-ven
**WHEN** el dueño marca una propuesta como rechazada
**THEN** deja de verse en la web y no es legible con la clave pública; las demás, pendientes o aprobadas, sí

### las-propuestas-se-votan
**WHEN** alguien elige su nombre y vota una propuesta a favor o en contra
**THEN** su voto se guarda —uno por persona y propuesta, cambiable— y la propuesta enseña cuántos y quiénes están
a favor y en contra; una propuesta rechazada no admite votos

### la-base-de-datos-valida-lo-que-entra
**WHEN** llega un voto o una propuesta de alguien que no ha jugado nunca, a una opción o propuesta que no existe,
con un sentido de voto que no es a favor ni en contra, con un texto vacío o demasiado largo, o de quien ya tiene
tres propuestas pendientes
**THEN** se rechaza y no se guarda nada

### la-web-no-escribe-en-las-tablas
**WHEN** se intenta insertar, cambiar o borrar directamente en las tablas del debate con la clave pública
**THEN** se rechaza: solo las funciones escriben

### el-texto-de-los-jugadores-se-escapa
**WHEN** una propuesta o un nombre contiene HTML
**THEN** se pinta como texto, no como marcado

### si-el-debate-no-carga-info-sigue
**WHEN** la base de datos no responde
**THEN** la pestaña enseña su cabecera y dice que no se ha podido cargar; el resto de la web no se entera

## Estado después

`rule_polls`, `rule_votes`, `rule_proposals` y `rule_proposal_votes` en Supabase, escritas solo por `votar_regla`,
`proponer_regla` y `votar_propuesta`. La
votación `anti-spoilers` existe y está abierta. No se toca `wordle_results` ni `season_snapshots`.

## Edge cases

- **Suplantación**: elegir el nombre de otro es posible por diseño; los votos con nombre lo hacen visible y el
  afectado lo corrige votando de nuevo.
- **Ocultar, aprobar y cerrar**: el dueño, desde Supabase, con
  `update public.rule_proposals set estado = 'rechazada' where id = …` (u `'aprobada'`, que la marca como tal) y
  `update public.rule_polls set abierta = false where id = …`.
- **Una norma votada no se aplica sola**: el resultado lo convierte en regla el dueño, con su slice.

## Slices compañeros

- [[reglas-explicadas]] — la pestaña Info, que lleva al debate.
- [[ranking-del-juego]] — de donde salen el selector «¿Quién eres?» y el patrón de escritura por función.
