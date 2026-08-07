---
slice: ruta-invalida
status: proposed
kind: action
actor: grupo
trigger:
  type: ui
  surface: web
  detail: "cualquier ruta que no exista — con el fallback SPA no hay 404 que avise"
events:
  emits: []
  consumes: []
specs:
  - dashboard
tests_root: tests/slices/ruta-invalida/
blocked: null
---

# Una ruta que no existe lo dice, en lugar de dejar la página en blanco

**Actor:** cualquiera que llegue con un enlace roto
**Trigger:** abrir una ruta que el router no reconoce

## Contexto

El Worker sirve la v2 con `not_found_handling: single-page-application`, así que **cualquier ruta devuelve
el documento con 200**. Eso es lo que hace que `/t/2026-07` funcione sin servidor de rutas, y es también lo
que elimina la red de seguridad: sin 404, una ruta mal escrita **no falla**, simplemente no pinta nada.

Y el caso llega solo. Los enlaces de esta web se pegan en el canal: una temporada que no existe (`/t/2026-13`),
un identificador copiado a medias, una ruta antigua después de un cambio.

El comportamiento existe desde el esqueleto, que es un pack `Slice: N/A`. Este slice lo convierte en
comportamiento **fijado por escenarios**: hasta ahora nada impedía que un refactor del router se llevara por
delante la única vista que avisa de que el enlace está roto.

## Comportamiento observable

### una-ruta-desconocida-se-declara
**WHEN** se abre una ruta que el router no reconoce
**THEN** la vista lo declara y muestra **qué ruta** se pidió, en lugar de una página en blanco.

### una-temporada-imposible-no-es-una-temporada
**WHEN** la ruta lleva un mes que no existe, como `2026-13` o `2026-00`
**THEN** se trata como ruta desconocida y no como una temporada vacía: una temporada vacía es un mes real
sin jornadas válidas, que es otra cosa y se muestra de otra manera.

### un-identificador-que-no-es-de-slack-no-abre-ficha
**WHEN** la ruta de jugador lleva algo que no tiene forma de identificador de Slack
**THEN** es ruta desconocida. Un jugador que no jugó esa temporada **sí** tiene ficha
([[ficha-de-jugador]]); lo que no la tiene es una ruta mal formada.

### una-ruta-desconocida-ofrece-la-salida
**WHEN** se muestra la vista de ruta desconocida
**THEN** ofrece volver a la temporada en curso, para que el enlace roto no sea el final del camino.

### una-ruta-desconocida-no-marca-ninguna-seccion
**WHEN** se pinta la navegación en una ruta desconocida
**THEN** no hay ninguna sección marcada como actual, porque la ruta no pertenece a ninguna.

### la-ruta-que-se-muestra-va-escapada
**WHEN** la ruta pedida contiene marcado
**THEN** se muestra como texto y no se interpreta: la ruta la escribe quien envía el enlace, así que es
entrada ajena.

## Estado después

Ninguno: solo pinta.

## Edge cases

- **La raíz y las rutas con barra final** son válidas, no desconocidas: `/`, `/hoy/` y `/hoy` son la misma.
- **Los parámetros y el fragmento** (`?x=1`, `#algo`) no hacen desconocida una ruta válida.
- **Una ruta desconocida sigue devolviendo 200** al servidor. No hay forma de que sea un 404 sin renunciar
  al fallback SPA, y renunciar rompería todas las rutas de temporada.

## Fuera de alcance, y por qué

- **Adivinar qué quiso escribir** («¿querías decir `/t/2026-01`?»): sin una medida de qué se falla de verdad,
  sugerir es inventar.
- **Registrar los enlaces rotos** en algún sitio: no hay telemetría en la v2 y añadirla es una decisión
  aparte, con datos de personas de por medio.

## Slices compañeros

- [[ficha-de-jugador]] — la diferencia entre «no existe esa ruta» y «ese jugador no jugó esa temporada».
- [[tabla-de-datos]] · [[archivo-de-temporadas]] — las rutas válidas a las que se puede volver.
