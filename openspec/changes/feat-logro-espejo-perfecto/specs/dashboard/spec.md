# dashboard — delta

## MODIFIED Requirements

### Requirement: El bloque de logros muestra el catálogo completo

La pestaña de temporada lista **todas** las medallas del catálogo, cada una con su nombre, su regla y su
icono. El número no se escribe en la especificación: cada logro nuevo lo dejaba desfasado.

Los dos catálogos —el del pipeline y el de la web— tienen que coincidir. Al añadir el espejo perfecto se vio
que nada lo impedía: cada lado tiene su lista y sus tests, así que el resumen diario podía anunciar un logro
que la pestaña de temporada no sabe explicar.

#### Scenario: el catálogo completo aparece en la temporada
- **WHEN** se pinta el bloque de logros de una temporada
- **THEN** aparecen todas las del catálogo con nombre, regla e icono
- **AND** el catálogo del pipeline y el de la web tienen las mismas claves
