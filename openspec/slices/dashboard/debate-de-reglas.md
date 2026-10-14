---
slice: debate-de-reglas
status: proposed
kind: action
actor: jugador
trigger:
  type: ui
  surface: web
  detail: "pestaña Info — /info, apartado «Debate de reglas»: votar una norma abierta o proponer una nueva, eligiendo quién eres"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - resultados
tests_root: tests/slices/debate-de-reglas/
blocked: null
---

# En Info se votan las normas abiertas y se proponen nuevas

**Actor:** quien juega
**Trigger:** votar o enviar una propuesta en el apartado «Debate de reglas» de Info

## Contexto

Las reglas se deciden conversando en el canal, y la conversación se pierde entre resultados. El dueño quiere un
sitio fijo para debatirlas: las normas en votación, con su recuento, y una zona de sugerencias donde cada uno
proponga y diga quién es.

La primera votación es la **norma anti-spoilers**: el 14 de octubre de 2026 un comentario con una pista evidente
(«el juego no me dejaba poner la Ñ») hizo que la jornada #1742 se resolviera mejor a partir de las 10:00. Medido
sobre 211 jornadas, publicar tarde no da ventaja por sí solo: la ventaja aparece el día del spoiler. El grupo
decide qué hacer, incluida la opción de no hacer nada.

**Quién eres se elige**, como en el SuperWordleBros (decisión del dueño): sin cuentas ni contraseñas. Por eso
**los votos se ven con su nombre**: si alguien vota en nombre de otro, el otro lo ve y lo cambia. Y por eso las
**propuestas no se publican solas**: quedan pendientes hasta que el dueño las aprueba, porque la web es pública
y el texto va firmado con el nombre de un compañero identificable.

La web **no escribe en las tablas**: llama a dos funciones de la base de datos que deciden qué entra, igual que
`registrar_tiempo`. El dueño aprueba propuestas y cierra votaciones desde Supabase.

## Comportamiento observable

### la-votacion-abierta-se-ve-con-su-recuento
**WHEN** se abre Info y hay una votación abierta
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

### una-propuesta-queda-pendiente
**WHEN** alguien envía una propuesta con su nombre, un título y una explicación
**THEN** se guarda como pendiente, se le dice que aparecerá cuando se apruebe y no se ve todavía en la web

### solo-se-ven-las-propuestas-aprobadas
**WHEN** se abre Info
**THEN** se ven las propuestas aprobadas con su autor, y ni las pendientes ni las rechazadas son legibles con la
clave pública

### la-base-de-datos-valida-lo-que-entra
**WHEN** llega un voto o una propuesta de alguien que no ha jugado nunca, a una opción que no existe, con un
texto vacío o demasiado largo, o de quien ya tiene tres propuestas pendientes
**THEN** se rechaza y no se guarda nada

### la-web-no-escribe-en-las-tablas
**WHEN** se intenta insertar, cambiar o borrar directamente en las tablas del debate con la clave pública
**THEN** se rechaza: solo las funciones escriben

### el-texto-de-los-jugadores-se-escapa
**WHEN** una propuesta aprobada o un nombre contiene HTML
**THEN** se pinta como texto, no como marcado

### si-el-debate-no-carga-info-sigue
**WHEN** la base de datos no responde
**THEN** el resto de Info se ve igual y el apartado dice que no se ha podido cargar

## Estado después

`rule_polls`, `rule_votes` y `rule_proposals` en Supabase, escritas solo por `votar_regla` y `proponer_regla`. La
votación `anti-spoilers` existe y está abierta. No se toca `wordle_results` ni `season_snapshots`.

## Edge cases

- **Suplantación**: elegir el nombre de otro es posible por diseño; los votos con nombre lo hacen visible y el
  afectado lo corrige votando de nuevo.
- **Aprobar y cerrar**: el dueño, desde Supabase, con
  `update public.rule_proposals set estado = 'aprobada' where id = …` y
  `update public.rule_polls set abierta = false where id = …`.
- **Una norma votada no se aplica sola**: el resultado lo convierte en regla el dueño, con su slice.

## Slices compañeros

- [[reglas-explicadas]] — la pestaña Info donde vive el apartado.
- [[ranking-del-juego]] — de donde salen el selector «¿Quién eres?» y el patrón de escritura por función.
