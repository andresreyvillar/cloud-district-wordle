# Proposal — feat-ventana-de-ingesta

> **Slice:** `ingesta-por-id-de-slack` (modificación: cuatro escenarios nuevos)
>
> **Por qué no es un slice nuevo.** El roadmap lo llamaba `ventana-de-ingesta-robusta`, pero su trigger
> sería exactamente el de `ingesta-por-id-de-slack` —el mismo cron horario, el mismo comando— y el protocolo
> prefiere modificar antes que duplicar por colisión de trigger (§3).

## Why

La ventana era de **50 mensajes**. Medido sobre 1200 mensajes reales del canal:

| Medida | Valor |
|---|---|
| Mensajes por día | mediana **10**, media 8,5, **máximo 27** |
| Lo que cubre la ventana de 50 | **5 días** naturales |
| Peor racha de 3 días | **52 mensajes** → no cabe |
| Peor racha de 7 días | **79 mensajes** → no cabe |

Contar mensajes hace que la cobertura dependa de lo hablador que esté el grupo. Un puente largo con Actions
caído, o un día de charla, y los resultados anteriores se salen de la ventana **sin que nada avise**.

## What Changes

- `VENTANA = 50` → `VENTANA_EN_DIAS = 14`, con el motivo y la medida en el propio comentario.
- `mensajes_de_la_ventana(cli, canal, ahora)`: pagina con cursor hasta el corte y devuelve en orden
  cronológico. **Si una página falla, propaga**: un lote incompleto se ingiere sin ruido y deja huecos.
- `corte_de_la_ventana(ahora, dias)`: puro, con la fecha por parámetro (§10).
- `fetch_messages(ahora=None)` resuelve el reloj **en el borde** y de ahí para dentro viaja por parámetro.

Catorce días cubren la peor racha de siete del histórico con margen. Es barato porque **reingerir no
duplica**: el upsert va por `(slack_user_id, wordle_id)`, y eso ya está cubierto por el escenario
`reprocesar-la-ventana-no-duplica` de este mismo slice.

## Impact

- La ejecución real pasa de leer 50 mensajes a leer **123 en dos páginas**, con 81 resultados de 11 jornadas
  (#1660–#1674) en lugar de los ~5 días de antes.
- Una llamada más a la API por ejecución. El coste es despreciable frente a perder un día de resultados.
