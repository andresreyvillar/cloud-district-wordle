---
adr: 0003
titulo: Modelo de ramas — el merge a `main` es el despliegue
estado: aceptado
fecha: 2026-08-04
decide: Andrés Rey
afecta: [todas]
---

## Contexto

En `pga-cms` el flujo es `feat/… → develop → main`, con `main` protegida y el despliegue por pipeline
aprobado. Aquí la situación es distinta y hay que decirla con precisión:

> **CORRECCIÓN del 2026-08-07.** La premisa «Cloudflare publica al push a `main`» **es falsa**, y se
> escribió sin comprobarla. Verificado contra Cloudflare: no hay Workers Builds, ningún workflow
> despliega, y los diez despliegues del Worker son `wrangler deploy` lanzados a mano. Lo que sí corre
> desde `main` son los dos cron de GitHub Actions. Es decir: **mergear cambia lo que el pipeline ejecuta
> —y eso escribe en producción— pero no publica la web.** El resto del ADR (una rama por change, merge
> `--no-ff`, nunca trabajar en `main`) se mantiene: sus motivos no dependen de esta premisa. Detalle y
> pruebas en el [ADR 0005](0005-hosting-y-convivencia-v1-v2.md).

- **Cloudflare publica al push a `main`** ~~(falso, ver corrección arriba)~~: los assets estáticos de la raíz se despliegan sin
  intervención (`wrangler.jsonc` + `.assetsignore`).
- **Los workflows programados corren desde `main`**: `update_stats.yml` (cada hora) y
  `post_ranking.yml` (17:00 UTC) ejecutan la versión de `main`, con los secrets del repo. Es decir,
  un cambio en `tools/` mergeado a `main` toca la base de datos de producción en la siguiente hora.
- Hay un desarrollador. No hay revisores que necesiten una rama de integración compartida.
- El repo es **público** y los datos son de compañeros identificables.

Consecuencia que ya se ha observado: un cambio en `tools/post_ranking.py` (viewport de la captura)
lleva semanas sin commitear, así que la captura que se publica en Slack sigue usando el valor viejo.
Lo que no está en `main` no existe para el sistema.

## Opciones

**A. Replicar `feat/… → develop → main`.**
*Pro:* `main` solo avanza en despliegues deliberados; `develop` acumula trabajo integrado.
*Contra:* con un solo desarrollador, `develop` es un salto ceremonial sin revisor; y como los cron
corren desde `main`, el trabajo en `develop` no se ejercita nunca de verdad hasta el merge final.

**B. `feat/<change-id>` → `main` por PR, merge `--no-ff`.**
*Pro:* una sola integración; cada merge es un punto de revert (`git revert -m 1`); el PR es el lugar
donde el humano aprueba. *Contra:* `main` es a la vez integración y producción: un merge desplegado a
medias no tiene red.

**C. Trunk-based, commits directos a `main`.**
*Pro:* lo más rápido. *Contra:* es lo que hay hoy, y no deja punto de revert atómico ni sitio donde
aprobar.

## Decisión

**Opción B.**

```
feat/<change-id> · chore/openspec-slice-<slug>  ──PR──▶  main  ──▶  despliegue automático
        trabajo                                       producción
```

Reglas que se derivan:

1. **Nunca se trabaja en `main`.** Toda autoría e implementación va en su rama.
2. **El merge es `--no-ff`**, para que un cambio entero se deshaga con `git revert -m 1 <merge>`.
3. **Solo el humano mergea.** El agente deja los archivos staged; ni commit ni push automáticos.
4. **Mergear es desplegar.** Antes de mergear algo que toque `tools/`, hay que asumir que el próximo
   cron escribirá en Supabase con ese código. Si el cambio es de riesgo, se ejecuta primero a mano
   con datos de prueba.
5. Un slice pasa a **`shipped` en el archive posterior al merge** a `main`.

## Consecuencias

**Se vuelve fácil:** revertir (un merge = un revert); revisar (un PR por change pack); entender qué
está vivo (lo que está en `main`).

**Se vuelve difícil:** experimentar en producción sin querer. Es deliberado: el punto 4 obliga a
pensar antes de mergear código del pipeline.

**Riesgo asumido y vigilado:** no hay entorno de staging. La mitigación real son los tests con
fixtures locales (Fase 2) y la prohibición de escrituras exploratorias contra la tabla de producción
(§7). Si algún día hace falta staging, será un proyecto Supabase aparte y un ADR nuevo.

**Nota operativa:** GitHub deshabilita los workflows programados de un repo público tras un periodo
prolongado sin actividad de commits. Con el ritmo actual (último commit en mayo, cron aún vivo en
agosto) conviene vigilarlo: si las estadísticas dejan de actualizarse sin causa aparente, comprobar
primero si Actions desactivó el schedule.
