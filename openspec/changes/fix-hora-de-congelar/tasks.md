# Tareas — fix-hora-de-congelar

1. `HORA_DE_CONGELAR` a `'02:00'` y los textos que la citan (aviso de la pestaña, workflow, contrato, slice).
2. Tests de `nivel-congelado` a la hora nueva, con los escenarios renombrados.

```bash
python3 -m tools.wslice slice validate nivel-congelado
python3 -m tools.wslice slice coverage nivel-congelado
python3 -m tools.wslice verify gates --slice nivel-congelado --change-id fix-hora-de-congelar
node --test tests/slices/nivel-congelado/
```
