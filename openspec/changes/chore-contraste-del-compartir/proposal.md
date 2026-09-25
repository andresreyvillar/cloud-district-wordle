# Proposal — chore-contraste-del-compartir

> **Slice:** N/A — presentación. El mismo texto para compartir, legible. Ningún dato ni comportamiento cambia.

## Why

En la pestaña SuperWordleBros, el texto para compartir apenas se leía en modo claro. `.compartir-texto`
usaba `var(--fondo-hundido, #1b1f2a)`, una variable que no existe, así que siempre caía al respaldo casi
negro; y el texto heredaba la tinta oscura del tema claro: oscuro sobre oscuro.

## Qué cambia

`v2/css/styles.css`: fondo `--liga-tablero` y tinta `--liga-tinta`, que se redefinen juntos en modo oscuro,
más un borde `--borde` para separarlo del fondo de la página.

## Verificación

Contraste medido en el navegador sobre los estilos calculados (fórmula WCAG): **13,4:1** en modo claro y
**14,7:1** en oscuro. Antes, en claro, tinta `#1b1b1f` sobre `#1b1f2a`: por debajo de 1,2:1.
