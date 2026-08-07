---
slice: captura-apunta-a-la-v2
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 17 * * 1-5 — workflow post_ranking.yml: de qué web se saca la captura y a cuál enlaza"
events:
  emits: []
  consumes: []
specs:
  - publicacion
tests_root: tests/slices/captura-apunta-a-la-v2/
blocked: null
---

# La captura diaria puede apuntar a la v2 cambiando una variable

**Actor:** sistema (cron diario)
**Trigger:** el workflow que publica el resumen en el canal

> **Comparte cron con [[medallas-en-el-resumen-diario]] y aun así es un slice aparte.** Aquel decide **qué
> dice** el mensaje; este, **de dónde sale la imagen y a dónde lleva el enlace**. No se solapan, viven en
> módulos distintos y uno puede cambiar sin tocar al otro. Se declara aquí porque el protocolo prefiere
> modificar antes que duplicar cuando el trigger coincide (§3), y esta es la excepción razonada.

## Contexto

Es **el corte real**: el día que esto apunte a la v2, el grupo deja de ver la v1 aunque siga publicada.

Hoy la URL está escrita a mano en `tools/post_ranking.py`. Cambiarla parece una línea, y no lo es: la
captura **espera el selector `.summary-cards` y fotografía `.container`**, que son marcado de la v1. La v2
no tiene ninguno de los dos. Cambiar solo la URL deja el workflow esperando quince segundos a un elemento
que no existe, y el resumen **no se publica**.

Por eso lo configurable no es la URL sino **el objetivo entero**: dónde mirar, qué esperar y qué fotografiar.
Un objetivo mal formado —la URL de la v2 con los selectores de la v1— deja de ser expresable.

## Comportamiento observable

### el-objetivo-de-la-captura-es-configurable
**WHEN** se decide de qué web sacar la captura
**THEN** sale de la configuración del entorno y no de una constante escrita en el código.

### cada-objetivo-trae-sus-selectores
**WHEN** se elige un objetivo
**THEN** vienen con él **su URL, el selector que hay que esperar y el que se fotografía**, porque son tres
datos de la misma decisión: los de la v1 no sirven para la v2.

### el-enlace-del-mensaje-apunta-a-donde-la-captura
**WHEN** se compone el texto que acompaña a la imagen
**THEN** el enlace es el del mismo objetivo del que se sacó la captura, para que nadie reciba una foto de una
web y un enlace a otra.

### un-objetivo-desconocido-falla-en-lugar-de-usar-el-viejo
**WHEN** la configuración pide un objetivo que no existe
**THEN** la ejecución falla. Caer en el objetivo por defecto dejaría una errata publicando la web vieja
indefinidamente sin que nadie se entere.

### el-objetivo-por-defecto-es-el-que-esta-publicado
**WHEN** no hay configuración
**THEN** se usa la v1, que es lo que hay desplegado. El corte lo decide una variable de entorno, no un
despliegue de código.

### una-publicacion-fallida-no-termina-en-exito
**WHEN** la captura o la subida fallan
**THEN** la ejecución termina con error, para que el workflow lo marque en rojo. Hoy imprime el fallo y
termina bien, así que el grupo deja de recibir el resumen y en Actions está todo verde.

## Estado después

Ninguno en datos. Cambia **dónde mira** el bot, no lo que guarda.

## Edge cases

- **La v2 sin desplegar** es el estado actual: el objetivo por defecto sigue siendo la v1 y nada cambia
  hasta que alguien ponga la variable.
- **Un objetivo con URL alcanzable pero sin el selector** falla por timeout, y ahora eso **es un error**,
  no un final silencioso.

## Fuera de alcance, y por qué

- **Desplegar la v2** (Fase 0.2). Este slice deja el interruptor puesto; accionarlo es otra cosa.
- **Sustituir la captura por texto**: es [[resumen-diario-compuesto]] (TBD), y elimina el navegador entero.
- **Elegir qué se fotografía de la v2** más allá de un selector: la composición del resumen nuevo es del
  slice de arriba.

## Slices compañeros

- [[medallas-en-el-resumen-diario]] — el mismo mensaje, la otra mitad: lo que dice.
- [[resumen-diario-compuesto]] (TBD) — el que hará que esta captura deje de existir.
