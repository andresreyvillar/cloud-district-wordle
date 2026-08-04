# Capa de contexto — wordle-stats

Pipeline de ingesta: **`inbox/`** (entrada cruda) → **`sources/`** (fichas de fuentes) →
**`briefs/`** (síntesis citables) → **canónico** (`openspec/`).

Ingesta SIEMPRE vía `/context-add`. La fábrica (y cualquier slice) consume solo canónico + briefs
citados; `sources/` es para humanos.

## Jerarquía de verdad

**specs + slices** > **ADRs / glosario** > **briefs** > **sources** > conversación suelta

Si un brief contradice una spec, la spec gana y el brief se marca `superseded`. Si una fuente nueva
contradice un brief, se actualiza el brief y se anota en `docs/diario-desarrollo.md`.

## Fuente principal de requisitos

El **canal de Slack del grupo**. Las reglas del juego (qué cuenta, qué penaliza, cuándo empieza una
temporada) se deciden conversando allí, no en un documento. Por eso `/context-add` acepta hilos como
entrada de primera clase: una decisión del grupo es material canonizable; una opinión no.

**Privacidad:** el repositorio es público y los datos son de compañeros identificables. En fichas y
briefs se registra la decisión, no la conversación. Sin citas literales innecesarias, sin capturas
del canal, sin datos personales más allá del nombre mostrado que ya usa la web.

## Fuentes

| Fecha | Fuente | Tipo | Autoridad | Capabilities | Estado |
|---|---|---|---|---|---|
| — | *(vacío)* | | | | |

## Briefs

| Brief | Tema | Capabilities | Estado |
|---|---|---|---|
| — | *(vacío)* | | |
