# Proposal — chore-esqueleto-v2

> **Slice:** N/A — plantilla sin comportamiento observable.

## Why

La v2.0 tiene cinco secciones y una ruta por vista ([ADR 0006](../../decisions/0006-estructura-de-informacion-v2.md)),
y ninguna de ellas existe: `index.html` sigue siendo el de la v1. Antes de escribir la primera vista hace
falta el armazón —módulos, router, borde de datos y **arranque local**—, porque sin él no se puede ver nada
en un navegador y cada slice tendría que traerse su propia infraestructura.

Va en su propio pack **a propósito**: el Gate 4c tiene que poder distinguir plantilla de comportamiento. Si
el esqueleto entrase con el primer slice, mutar el router pondría en rojo un test de ranking y nadie sabría
qué protege qué.

## What Changes

Nada de lo existente. **Todo es nuevo y vive en `v2/`**, que no toca la v1
([ADR 0005](../../decisions/0005-hosting-y-convivencia-v1-v2.md)):

```
v2/index.html            el único documento; el resto son módulos ES
v2/css/styles.css        armazón visual, con modo claro y oscuro
v2/js/router.js          PURO: ruta → vista + parámetros
v2/js/data/results.js    el borde de datos: lee Supabase paginando
v2/js/ui/shell.js        el armazón: cabecera, selector de temporada, contenedor de vista
v2/js/app.js             el borde: arranca, carga, resuelve la ruta, pinta
v2/js/domain/            vacío por ahora: cada regla del juego llega con su slice
tools/serve_v2.py        servidor local con el mismo fallback SPA que el Worker
wrangler.v2.jsonc        configuración del Worker nuevo, con not_found_handling
tests/v2/router.test.js  unitarios del router con node --test
```

- **`.assetsignore` gana `v2/`.** Sin eso el Worker de la v1 publicaría la v2 a medio hacer en
  `/v2/index.html`, porque su `assets.directory` es la raíz del repo.
- **El arranque local reproduce el fallback SPA.** `python3 -m http.server` devuelve 404 en `/t/2026-07`, así
  que probar el router en local sería imposible con él: `tools/serve_v2.py` sirve `index.html` con 200 para
  cualquier ruta que no sea un archivo, que es exactamente lo que hará Cloudflare.

## Out of Scope

| Fuera | Disparador que lo traería |
|---|---|
| El contenido de cualquier vista | Su slice. El esqueleto pinta un marcador de posición que dice qué vista resolvió |
| El cálculo de temporadas | `temporada-mensual` (Fase 2.1). `js/domain/` nace vacío a propósito |
| La ruta inválida con sentido | `ruta-invalida` (Fase 2.6). El esqueleto la detecta y lo dice, pero no es la vista final |
| Crear el Worker en Cloudflare | Fase 0.2, y el despliegue es lo último por decisión explícita |
| Retirar la v1 | ADR propio cuando llegue |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Ninguno. `Slice: N/A` |
| **Capabilities** | Ninguna: sin comportamiento observable, sin Requirements |
| **Archivos nuevos** | los nueve de arriba |
| **Archivos modificados** | `.assetsignore` |
| **Compatibilidad** | La v1 no cambia. Nada de `v2/` se publica hasta que exista el Worker |
| **Riesgo** | Bajo. No toca el pipeline, no escribe en la base de datos y no se despliega |

## Validation Gates

```bash
# 1 · Sintaxis y unitarios del router
node --check v2/js/router.js && node --check v2/js/app.js
node --test tests/v2/

# 2 · La suite de Python sigue intacta
.venv/bin/python3 -B -m pytest -q

# 3 · Arranque local, y se comprueba a mano en el navegador
python3 tools/serve_v2.py
#   / , /t/2026-07 , /temporadas , /hoy , /datos y /ruta-mala devuelven 200 con el documento
#   y la consola no tiene errores

# 4 · El Worker de la v1 no publicaría la v2
grep -q '^v2/$' .assetsignore
```

**Gate 4c (mutación)** aplica al router, que es la única lógica del pack: mutar el patrón de temporada o el
orden de las rutas debe poner en rojo su unitario.

**Gate 4e (security review):** la clave de Supabase que va en el cliente es la **publicable**, la misma que
la v1 ya expone, con RLS de solo lectura. No entra ninguna credencial nueva.

## Notas de honestidad

- **`js/domain/` nace vacío y eso es deliberado**, no un olvido. Si el esqueleto trajera el cálculo de
  temporadas, ese cálculo llegaría sin escenarios y sin test de mutación, que es justo lo que el método
  intenta evitar.
- **El esqueleto no se puede verificar del todo sin ojos.** Los unitarios cubren el router y el servidor
  local se comprueba con `curl`, pero que el documento pinte algo con sentido en un navegador es una
  comprobación manual. Queda declarada como tal, no disimulada.
- **La clave publicable va en el código fuente**, como en la v1. Es correcto para un cliente sin backend y
  con RLS de solo lectura, pero conviene recordar que **cualquiera puede leer la tabla entera** con ella: la
  protección es que no puede escribir, no que los datos sean privados.
