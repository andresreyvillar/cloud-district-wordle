# Implementación

1. Declarar y probar la ruta independiente y el controlador de lectura del evento cerrado.
2. Probar y adaptar el modelo de premios a los datos del tablero, incluidos empates y lista sin premios.
3. Integrar el diseño aprobado, controles, teclado y efectos del podio sin dependencias nuevas.
4. Ejecutar `node --test tests/slices/resultados-del-evento/`.
5. Ejecutar `.venv/bin/python3 -B -m pytest tests/slices/resultados-del-evento/`.
6. Ejecutar `.venv/bin/python3 -B -m pytest` y `node --test tests/v2/ tests/slices/`.
7. Ejecutar `python3 -B -m tools.wslice slice validate resultados-del-evento`, `python3 -B -m tools.wslice slice coverage resultados-del-evento`, `python3 -B -m tools.wslice verify slice resultados-del-evento` y `python3 -B -m tools.wslice verify gates --slice resultados-del-evento --change-id feat-resultados-del-evento`.
8. Hacer las mutaciones y la revisión adversarial; publicar y comprobar la espera sin escribir datos del evento.
