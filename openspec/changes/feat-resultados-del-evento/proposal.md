# Presentación de resultados del barrio

## Why
El presentador necesita repartir los premios F1 paso a paso ante el grupo, con el diseño de la maqueta aprobada.

## What Changes
Ruta independiente `/2/evento/resultados`, lectura del evento cerrado, revelado inverso de los premios F1 con sus personas, clasificación acumulada y efectos del podio. El empate individual se revela como un bloque y los puntos proceden siempre del servidor.

## Out of Scope
Cambios de reglas, puntuación, esquema, autenticación, cron, Slack, resultados de producción o edición de equipos. La instantánea del ensayo no se incluye en los assets ni en los tests.

## Impact
Solo router, arranque y nuevos módulos/estilos de la web. API existente de solo lectura. Se preservan los ficheros ajenos ya presentes en el workspace.

## Validation Gates
Tests unitarios y de navegador con fixtures inventados, suite completa Python y JavaScript, sintaxis, validate/coverage/verify/gates del slice, mutaciones contra revelado prematuro y puntos duplicados, revisión adversarial y comprobación del build publicado.

| Capability | Requirement |
|---|---|
| dashboard | Presentación independiente, cierre, errores y animaciones accesibles |
| ranking | Premios inversos, acumulación, empates, límites y datos vacíos |
