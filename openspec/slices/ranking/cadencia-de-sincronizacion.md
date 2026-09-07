---
slice: cadencia-de-sincronizacion
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0,20,40 * * * * — workflow update_stats.yml, con latido de 7 vueltas"
events:
  emits: []
  consumes: []
specs:
  - ranking
  - resultados
tests_root: tests/slices/cadencia-de-sincronizacion/
blocked: null
---

# La sincronización ocurre bastantes veces al día, y sin silencios largos

**Actor:** sistema (el cron de datos)
**Trigger:** las ventanas programadas del workflow de ingesta

## Contexto

El planificador de GitHub **no cumple lo que se le declara**. Medido en este repositorio con una ventana por
hora: **4-9 ejecuciones al día** de 24, con huecos de hasta **8,6 h**. La web enseñaba datos de horas antes sin
que nada estuviera roto.

Se probaron tres cosas antes de llegar aquí, y las tres constan:

| Intento | Resultado |
|---|---|
| Mover el cron fuera del minuto en punto (lo que GitHub recomienda) | **empeoró**: de 21-23 diarias a 2-6. Revertido |
| Cron del Worker de Cloudflare | **cero disparos** en cuatro días. Descartado escuchando sus logs: 23 invocaciones `fetch`, 0 de cron |
| cron-job.org | **cero disparos**. Sin diagnóstico: su historial vive en su panel |

## La decisión que cambia el problema

No se pide puntualidad, se pide **cadencia**, y con un número:

```
al menos 12 ejecuciones al día
ningún hueco de más de 2 horas
```

Eso convierte un deseo en un requisito que se puede auditar, en lugar de confiar en que el planificador
funcione.

## Cómo se consigue: dos piezas que se complementan

**Tres ventanas por hora** (72 al día). No para ser puntual, sino para que la probabilidad de un silencio
largo baje. Con una sola ventana por hora salían 4-9 ejecuciones.

**Un latido de 5,5 h.** Cada ejecución sincroniza cada 55 minutos durante casi seis horas, así que un disparo
suelto ya cubre un silencio largo.

**Y el sistema se adapta solo**, que es lo que lo hace robusto sin ser complicado:

- cuando el planificador va bien, cada ventana cancela el latido y sincroniza: la cadencia la dan las
  ventanas y el bucle nunca pasa de su primera vuelta;
- cuando el planificador calla, el latido que quedó vivo sigue sincronizando y cubre el silencio.

## Trigger técnico

`update_stats.yml`, con `concurrency` de cancelación para que solo haya un latido vivo. Cancelar a media
sincronización es seguro: la ingesta no reescribe resultados ya guardados y la materialización hace `upsert`.

## Comportamiento observable

### la-cadencia-es-un-requisito-medible
**WHEN** se juzga si la sincronización va bien
**THEN** se comprueba contra dos números —ejecuciones mínimas por día y hueco máximo— en lugar de contra una
impresión; y el veredicto no depende de cuándo se mire.

### un-dia-flojo-se-nombra
**WHEN** algún día no alcanza el mínimo de ejecuciones
**THEN** se dice **cuál**, porque saber qué día falló vale más que un sí o un no.

### el-hueco-se-mide-entre-ejecuciones-consecutivas
**WHEN** hay un silencio largo entre dos ejecuciones
**THEN** se detecta aunque el recuento diario sea suficiente: doce ejecuciones agrupadas en dos horas cumplen
el mínimo y **no** cumplen la cadencia.

### sin-ejecuciones-no-se-inventa-un-veredicto
**WHEN** no hay ejecuciones que juzgar
**THEN** no se afirma que la cadencia se cumpla ni que falle por un hueco que no existe.

## Estado después

Nada cambia en los datos: esto es el criterio y el mecanismo que lo persigue. No se escribe en Supabase.

## Edge cases

- **Una sola ejecución**: no hay huecos que medir, pero sí falta al mínimo diario.
- **Ejecuciones de días distintos**: el hueco entre el último de un día y el primero del siguiente cuenta,
  porque un silencio nocturno de seis horas es un silencio igual.

## Slices compañeros

- [[temporada-mensual]] — la materialización que este cron ejecuta.
- [[resultado-del-dia]] — los datos cuya frescura depende de esta cadencia.
