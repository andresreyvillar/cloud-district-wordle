# Tareas — fix-enlace-de-la-pestana-del-juego

1. `v2/js/router.js`: la ruta canónica del juego en `_rutaInterna`.
2. `tests/slices/juego-de-la-jornada/navegacion.test.js`: todas las pestañas llevan a su vista.
3. Probar en el navegador pulsando la pestaña desde otras secciones.

```bash
python3 -m tools.wslice slice validate juego-de-la-jornada
python3 -m tools.wslice slice coverage juego-de-la-jornada
python3 -m tools.wslice verify gates --slice juego-de-la-jornada --change-id fix-enlace-de-la-pestana-del-juego
node --test tests/
```
