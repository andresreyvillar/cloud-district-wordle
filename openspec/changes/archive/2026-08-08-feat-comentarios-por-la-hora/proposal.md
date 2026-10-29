# Proposal — feat-comentarios-por-la-hora

> **Slice:** `comentarios-de-la-jornada` (modificación: tres hechos nuevos, no una regla distinta)

## Why

Lo pidió el dueño al definir cómo tiene que ser el resumen diario: además de las notas, quería los chistes
de **trampas, suerte sospechosa, el que se raja y el que sube el resultado a última hora**. Los tres
primeros ya existían; el cuarto necesitaba un dato que no se estaba usando.

## ¿Hay hora de publicación? Sí, con letra pequeña

`created_at` es cuando el cron escribió la fila, no cuando la persona publicó. Medido antes de usarlo:

- **60 minutos distintos de 60** y un reparto por horas con forma humana —pico de 07 a 11 UTC, cola hasta la
  noche—, no la forma de un proceso que corre en punto;
- el margen es de **hasta una hora**, lo que tarda el cron. Suficiente para distinguir «por la mañana» de «a
  media tarde», que es lo único que estos chistes necesitan;
- **268 filas del backfill** se insertaron todas el 2026-02-02. Ahí el margen no es de una hora sino de
  meses, así que la hora **solo se usa si cae el mismo día que el puzzle**. Se excluyen solas.

## Los tres hechos nuevos, por rareza

| Hecho | Disparador | Frecuencia |
|---|---|---|
| **acertar a la primera** | 1 intento | 0,01 |
| **llegar el último y clavarla** | último, 4h+ de hueco, tras las 14h, y 1 punto mejor que la media | 0,06 |
| **llegar el último** | último, 4h+ de hueco, tras las 14h | 0,24 |

Llegar tarde y llegar tarde **habiendo clavado** son dos chistes distintos, y se separan porque su
frecuencia lo es: uno sale un día de cada cuatro y el otro uno de cada dieciséis. Mezclarlos habría gastado
el bueno.

## Impact

- El resumen cubre los cuatro tipos de comentario que pidió el dueño.
- **Limitación declarada**: el mensaje sale a las 17:00 UTC, así que quien publique después no aparece —ni
  en el comentario ni en el marcador— hasta el día siguiente.
