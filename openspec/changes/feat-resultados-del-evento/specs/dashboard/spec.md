## ADDED Requirements

### Requirement: Los resultados del evento se presentan sin adelantar premios

La ruta independiente `/2/evento/resultados` muestra una espera hasta que el evento termina. Solo usa la lectura pública del tablero y nunca escribe datos. Un fallo de conexión permite reintentar. La presentación usa el diseño y los textos aprobados, controles manuales y animaciones de podio compatibles con movimiento reducido.

#### Scenario: espera al cierre
- WHEN se abre el evento activo
- THEN no aparece ningún punto ni persona premiada y se vuelve a consultar el estado

#### Scenario: presenta y anima el podio
- WHEN se revelan los tres primeros premios
- THEN los puntos parpadean y el primero añade fuegos artificiales, salvo movimiento reducido

verified-by:
  - tests/slices/resultados-del-evento/results.test.js
  - tests/slices/resultados-del-evento/test_browser.py
