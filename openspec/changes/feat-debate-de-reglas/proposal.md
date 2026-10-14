# Debate de reglas en Info: votaciones y propuestas

> Slice: `debate-de-reglas` (nuevo).

## Why

Las reglas se deciden en el canal y la conversación se pierde entre resultados. El dueño quiere un sitio fijo en
Info para debatirlas: normas en votación con su recuento y una zona de sugerencias firmadas. La primera votación
es la norma anti-spoilers (jornada #1742, 2026-10-14), con la opción de no hacer nada.

## What Changes

- `supabase/migrations/20261014120000_create_rule_debate.sql`: `rule_polls`, `rule_votes`, `rule_proposals`
  (RLS de lectura; las propuestas, solo las aprobadas), `votar_regla` y `proponer_regla` (security definer,
  validan) y la votación `anti-spoilers` sembrada.
- `v2/js/data/results.js`: `leerDebate` y la API `DEBATE`.
- `v2/js/domain/debate.js`: `recuento`.
- `v2/js/ui/debate.js`: el apartado, con el selector «¿Quién eres?» del juego.
- `v2/js/ui/info.js` y `v2/js/app.js`: el apartado después de las reglas vigentes.
- `v2/css/styles.css`: estilos del apartado.

## Decisiones del dueño

- Quién eres se elige, sin cuentas. Los votos se enseñan con su nombre para que una suplantación se vea.
- Las propuestas quedan pendientes hasta que el dueño las aprueba.
- Un voto por persona, cambiable mientras la votación esté abierta; la cierra el dueño.
- Opciones de la votación: anular la jornada con sanción, cortar en el spoiler, solo prevención, no hacer nada.

## Out of Scope

- Aplicar el resultado de la votación: la norma elegida será su propio slice.
- Moderar desde la web: aprobar y cerrar se hace en Supabase.

## Impact

- Esquema: tres tablas y dos funciones nuevas, aditivas. **La migración se aplica en producción aparte**, con
  confirmación del dueño; sin ella el apartado dice que no se ha podido cargar y el resto de Info sigue igual.

## Validation Gates

```bash
python3 -m tools.wslice slice validate debate-de-reglas
python3 -m tools.wslice slice coverage debate-de-reglas
python3 -m tools.wslice verify gates --slice debate-de-reglas --change-id feat-debate-de-reglas
.venv/bin/python3 -B -m pytest tests/slices/debate-de-reglas
node --test tests/slices/debate-de-reglas/
```

## Capabilities

| Capability | Requirements |
|---|---|
| `dashboard` | Info tiene un apartado de debate con votaciones y propuestas |
| `resultados` | el debate vive en tablas aditivas que solo escriben sus funciones |
