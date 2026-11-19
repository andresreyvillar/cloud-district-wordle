## ADDED Requirements

### Requirement: El reparto visual conserva los premios F1 del tablero

Los grupos parten de cero y reciben los premios del último puesto individual premiado al primero. Las personas empatadas se revelan juntas con los puntos del servidor. Los grupos se ordenan por lo acumulado y comparten puesto si empatan. Retroceder o reiniciar nunca duplica puntos; no hay premios inventados cuando el tablero no los tiene.

#### Scenario: conserva puntos y empates
- WHEN se completa el revelado
- THEN cada grupo suma exactamente las contribuciones F1 del tablero y los empates comparten puesto

verified-by:
  - tests/slices/resultados-del-evento/results.test.js
  - tests/slices/resultados-del-evento/test_browser.py
