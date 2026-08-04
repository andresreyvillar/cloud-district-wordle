---
stepsCompleted: [1, 2, 3, 4, 5, 7, 8, 9]
inputDocuments: ['js/script.js']
workflowType: 'code-review'
targetCode: 'js/script.js'
outputPath: './code-review-report-2026-05-26.md'
date: '2026-05-26'
status: 'complete'
---

# Code Review Report

**Date**: 2026-05-26
**Target**: `js/script.js` (234 líneas, JS vanilla)
**Status**: in-progress

---

## Step 1: Context

**Code Under Review**: `js/script.js` — frontend del dashboard Wordle Analytics.

**Purpose**: Carga resultados desde Supabase, calcula estadísticas por usuario (media, distribución, %éxito, participación) y renderiza 4 pestañas (Ranking, Estadísticas, Evolución temporal, Datos crudos) usando Plotly y HTML tables.

**Scope**: Un solo archivo, JS vanilla, ~259 líneas, sin tests, sin build step. Cambios recientes: añadida paginación con `.range()` y helper `escapeHtml` contra XSS.

---

## Step 2: Function Quality

Referencia: `references/functions/rules.md` (Rule 1: 2-5 líneas ideal, máx 20 · Rule 2: hacer una sola cosa · Rule 4: máx 3 args · Rule 9: extraer try/catch).

| Función | Líneas | Args | Veredicto |
|---------|-------:|-----:|-----------|
| `fetchAllResults` | 17 | 0 | ✅ Tamaño justo, una responsabilidad. |
| `DOMContentLoaded` cb | 22 | — | ⚠️ Mezcla fetch + mapeo + init + manejo de error. Rule 9: el try contiene varias acciones que podrían extraerse. |
| `escapeHtml` | 10 | 1 | ✅ Buena. |
| `openTab` | 17 | 1 | ⚠️ Rule 2: hace tres cosas (reset tabs, reset botones por parsing del `onclick`, dispatch resize). |
| `initDashboard` | 33 | 1 | ❌ Rule 1 (>20). Mezcla cómputo de stats con orquestación de 5 renders → Rule 3 (un solo nivel de abstracción). |
| `renderSummary` | 26 | 1 | ⚠️ Borderline. |
| `renderEvolutionChart` | 25 | 2 | ⚠️ Borderline. |
| `renderBubbleChart` | 46 | 1 | ❌ Rule 1. Además **muta el DOM** (crea y appendea `#bubble-chart` cada llamada). Side effect oculto → Rule 6. |
| `renderStatsTable` | 35 | 1 | ❌ Rule 1. La construcción del HTML de la distribución se merece su propia función. |
| `renderDataTable` | 10 | 1 | ✅ |

**Findings clave**:
- F-2.1 `initDashboard` viola tamaño y nivel de abstracción. **Extraer** `computeUserStats(rawData, totalDays)`.
- F-2.2 `renderBubbleChart` viola tamaño y tiene side effect implícito (crea div). Debería recibir el contenedor o tener su propio nodo declarado en HTML.
- F-2.3 `openTab` mezcla varias responsabilidades; el matching por `getAttribute('onclick').includes(tabId)` es frágil — depende del HTML inline.
- F-2.4 Acoplamiento temporal oculto entre `renderSummary` (que sobreescribe `#ranking.innerHTML`) y `renderBubbleChart` (que appendea sobre `#ranking`). G31 (Hidden Temporal Coupling).

---

## Step 3: Naming

Referencia: `references/naming/rules.md`.

**Problemas encontrados**:
- N-3.1 `_supabase` (línea 6) — encoding con guión bajo para evitar colisión con global `supabase`. Rule 6 (No encodings). Mejor: `supabaseClient` o `db`.
- N-3.2 `num` (líneas 23, 37, 39, 82) — nombre cripico. Es el número del puzzle Wordle. Rule 1 (Intention-revealing). Mejor: `wordleNumber` o `puzzleId`.
- N-3.3 `user` como nombre del campo (líneas 21, 35-39, etc.) — es un display name, no un objeto User. Mejor: `playerName` (coincide con `player_name` de DB → Rule 9: una palabra por concepto).
- N-3.4 `all` (línea 11) — genérico. Mejor: `allResults` o `rows`.
- N-3.5 `from` (línea 12) — sombra `Array.from`. Mejor: `offset`.
- N-3.6 `mappedData` (línea 35) — "Data" es noise word per Rule 3. Mejor: `playerResults`.
- N-3.7 `dist` (línea 94) — abreviatura. Mejor: `distribution`.

**Aceptables** (per "Exceptions" — single-letter loop vars):
- `a, b` en comparadores de sort y reduce.
- `d, e, s, ch, tr` en lambdas y bucles cortos.

---

## Step 4: Module Design

No hay clases. A nivel de módulo:

- M-4.1 Todo en scope global. No hay IIFE ni ESM. Riesgo de colisión (de hecho ya hay una con `supabase` → ver N-3.1).
- M-4.2 Un mismo archivo tiene **3 capas mezcladas**: data-access (Supabase), lógica de dominio (cálculo de stats), presentación (HTML + Plotly). SRP a nivel de módulo violado. Para un proyecto personal pequeño es aceptable; para escalar habría que separar en módulos.
- M-4.3 Credenciales hardcodeadas en líneas 3-4. No es un problema de Clean Code per se (la `anon key` es publicable), pero acoplan el código al entorno. Inyectables vía `window.__CONFIG__` o variables de Pages.

---

## Step 5: Error Handling

- E-5.1 `fetchAllResults` propaga errores correctamente (`throw error`). ✅
- E-5.2 Único `try/catch` en el listener `DOMContentLoaded`. Captura todo el pipeline (fetch + render). ✅
- E-5.3 G3 (Incorrect Behavior at the Boundaries) — varios edge cases sin manejar:
  - `renderSummary` líneas 115-116: si `stats` está vacío, `mostConsistent.user` lanza `TypeError`.
  - `renderBubbleChart` línea 187: si `filteredStats` está vacío, `Math.max(...[])` = `-Infinity` → `sizeref` NaN.
  - `row.wordle_id.toString()` línea 37: si `wordle_id` es null, crash.
- E-5.4 Mensaje al usuario es genérico ("Revisa la consola"). Para una web pública preferible un mensaje accionable, pero el alcance del proyecto lo justifica.

---

## Step 6: Tests — N/A

No hay tests en el repo. Smell **E2** (build/test requiere más de un paso) no aplica porque no hay test suite. Si quisieras añadir, los candidatos obvios son:
- `computeUserStats` (función pura, fácil de testear).
- `escapeHtml` (función pura).
- `fetchAllResults` (mock del cliente Supabase).

---

## Step 7: Comments

Referencia: `references/smells/rules.md` (C1-C5).

| Líneas | Comentario | Veredicto |
|--------|------------|-----------|
| 1-2 | "Configuración de Supabase / REEMPLAZA ESTOS VALORES..." | **C2 Obsolete** — los valores ya están. Eliminar. |
| 32-34 | "Mapear datos de DB (snake_case) a formato interno..." | ⚠️ Útil pero **prematuro**: si renombras los campos JS a `playerName/wordleNumber`, este comentario sobra. |
| 37 | "El código original espera string a veces" | **C2 Obsolete** — referencia a "código original" que ya no existe. Eliminar o reescribir. |
| 46 | "Fallback opcional o mensaje de error en UI" | **C3 Redundant** — el código siguiente es exactamente eso. Eliminar. |
| 74 | "Redimensionar gráficos de Plotly para que ocupen todo el ancho" | ⚠️ Marginal. El truco del `resize` event no es obvio; **mantener pero acortar** o mejor extraer a `resizeAllPlots()`. |
| 84 | "1. Calcular estadísticas extendidas" | **C3 Redundant** — número de sección en lugar de extraer función. |
| 106 | "Renderizar componentes en sus pestañas" | **C3 Redundant** — los nombres de las funciones ya lo dicen. |
| 175 | "Filtrar usuarios con al menos 3 partidas" | **C3 Redundant** — la línea `.filter(s => s.total >= 3)` lo dice. |
| 218 | "Ordenar por media por defecto" | **C3 Redundant**. |

---

## Step 8: Code Smells (catálogo)

Referencia: `references/smells/rules.md`.

### General

- **G3 Incorrect Behavior at the Boundaries**: edge cases en `renderSummary` y `renderBubbleChart` (ver E-5.3).
- **G6 Wrong Level of Abstraction**: `initDashboard` mezcla cómputo de stats (bajo nivel) con orquestación (alto nivel).
- **G9 Dead Code**:
  - Variable `fails` (línea 90, exportada en línea 103) → nunca consumida por ningún renderer. **Borrar.**
  - Comentarios obsoletos (ver Step 7).
- **G14 Feature Envy**: `openTab` línea 69 parsea el atributo `onclick` de los botones — depende del HTML inline. Mejor: data-attribute (`data-tab="ranking"`) y leer eso.
- **G16 Obscured Intent**: `sizeref: 2.0 * Math.max(...filteredStats.map(s => s.successRate)) / (40**2)` — fórmula sin nombre.
- **G19 Use Explanatory Variables**: la línea anterior; varios `.reduce/.map` encadenados sin variables intermedias.
- **G21 Algorithm by Accident**: `openTab` línea 69 — funciona solo por la convención del `onclick` inline en el HTML.
- **G25 Magic Numbers**:
  - `7` (L90): umbral de fallo. → `FAIL_THRESHOLD` o `MAX_ATTEMPTS = 6`.
  - `6` (L97, L223): intentos máximos. → `MAX_ATTEMPTS`.
  - `5` (L116): mínimo para "Mejor Media". → `MIN_GAMES_FOR_BEST_AVG`.
  - `3` (L176): mínimo para bubble chart. → `MIN_GAMES_FOR_BUBBLE`.
  - `10` (L185): tamaño mínimo de bubble. → `MIN_BUBBLE_SIZE`.
  - `40` (L187): bubble max diameter. → `MAX_BUBBLE_DIAMETER`.
  - `50` (L76): timeout de resize. → `RESIZE_DEBOUNCE_MS`.
- **G30 Functions Should Do One Thing**: `initDashboard`, `renderBubbleChart`, `renderStatsTable`, `openTab` (ya listadas en Step 2).
- **G31 Hidden Temporal Coupling**: `renderSummary` → `renderBubbleChart` (mismo contenedor `#ranking`).

### Functions

- **F2 Output Arguments**: ninguna.
- **F3 Flag Arguments**: ninguna.

### Names

- **N1 Choose Descriptive Names**: ver N-3.1, N-3.2, N-3.3, N-3.4.
- **N6 Avoid Encodings**: `_supabase` (N-3.1).

### Environment

- **E1/E2**: no aplica (proyecto estático, sin build).

---

## Step 9: Resumen y Priorización

### Alta prioridad (corrección de bugs o riesgo claro)
1. **G3 Boundaries** — Añadir guards en `renderSummary` y `renderBubbleChart` para arrays vacíos. Hoy mismo no rompe porque siempre hay datos, pero si filtras por usuario o periodo en el futuro, sí.
2. **G14 / G21 `openTab`** — Cambiar el parsing de `onclick` por `data-tab` attributes en HTML. Frágil ante refactor.
3. **G31 Acoplamiento temporal** — `renderBubbleChart` debe tener su propio contenedor declarado en `index.html` (`<div id="bubble-chart">`) en lugar de inyectarlo en runtime sobre `#ranking`.

### Media prioridad (legibilidad y mantenibilidad)
4. **Rule 1 + G30** — Extraer `computeUserStats(rawData, totalDays)` fuera de `initDashboard`. Función pura, fácil de testear.
5. **G25 Magic Numbers** — Convertir `7, 6, 5, 3, 10, 40, 50` en constantes nombradas en la cabecera.
6. **N6 / N-3.1** — Renombrar `_supabase` → `supabaseClient`.
7. **N-3.2 / N-3.3** — Renombrar `num` → `wordleNumber`, `user` → `playerName`. Elimina el mapping snake_case → legacy.
8. **C2 / C3** — Limpiar los 5 comentarios obsoletos/redundantes (L1-2, L37, L46, L84, L106, L175, L218).

### Baja prioridad (mejoras opcionales)
9. **Dead code G9** — Borrar `fails` si nadie lo consume.
10. **G19 explanatory variables** — Romper el `sizeref` en variables nombradas.
11. **M-4.2** — Considerar separar capas (data / stats / render) cuando el archivo supere ~400 líneas.



