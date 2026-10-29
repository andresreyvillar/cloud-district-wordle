# Proposal — feat-captura-apunta-a-la-v2

> **Slice:** `captura-apunta-a-la-v2` (openspec/slices/publicacion/captura-apunta-a-la-v2.md)

## Why

Es **el corte real**: el día que la captura apunte a la v2, el grupo deja de ver la v1 aunque siga publicada.

El roadmap decía «una línea en `post_ranking.py`». No lo es: la captura **espera `.summary-cards` y
fotografía `.container`**, que son marcado de la v1. La v2 no tiene ninguno de los dos. Cambiar solo la URL
deja el workflow esperando quince segundos un elemento que no existe y **el resumen sin publicar**.

## What Changes

- `Objetivo(nombre, url, espera, captura)` y `OBJETIVOS = {v1, v2}`, elegido con `CAPTURA_OBJETIVO`.
  El estado roto —URL de una web con selectores de la otra— deja de ser expresable.
- Un objetivo desconocido **aborta**: caer en el por defecto dejaría una errata publicando la web vieja para
  siempre sin que nadie se entere.
- `comentario(medallas, objetivo)`: el enlace es el del objetivo capturado.
- `publicar()` devuelve **código de salida**, y `main` lo propaga.

## Dos fallos silenciosos que salieron al tirar del hilo

1. **Cualquier fallo terminaba en éxito.** El `except Exception` de `main` imprimía y devolvía sin más: si
   la captura reventaba, el grupo se quedaba sin resumen y en Actions estaba todo verde. Ahora sale en rojo.
2. **El workflow no le pasa las credenciales de Supabase al paso que publica.** Sin ellas
   `leer_resultados()` devuelve vacío, así que **el mensaje diario nunca ha llevado medallas**: están
   implementadas desde el 2026-08-05 y no han salido ni un solo día. Se añaden al `env` del paso.

## Cómo se acciona el corte

`CAPTURA_OBJETIVO=v2` como variable del repositorio. El workflow ya la lee con `v1` por defecto, así que
**hasta que alguien la ponga no cambia nada**, y ponerla no requiere tocar código.

## Impact

- Nada cambia hoy: el objetivo por defecto sigue siendo la v1, que es lo desplegado.
- El mensaje diario pasará a llevar medallas en cuanto esto llegue a `main`.
- Requiere que la v2 esté desplegada (Fase 0.2) antes de accionar el interruptor.
