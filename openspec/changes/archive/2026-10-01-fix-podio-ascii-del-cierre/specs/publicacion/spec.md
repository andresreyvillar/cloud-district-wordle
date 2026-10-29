# Deltas de `publicacion` — fix-podio-ascii-del-cierre

## ADDED Requirements

### Requirement: El podio de cierre se dibuja como el del resumen diario

El mensaje de cierre de mes dibuja el podio con el **mismo podio ASCII de bloques macizos** que el resumen
diario (`tools/podios.py::podio_de_texto`), dentro de un bloque de código y bajo «🏆 *Así queda el podio ·
Temporada N*». Los puestos son los de la clasificación: con el primer puesto compartido, **todos los campeones
van juntos en el escalón central, el más alto**. Sustituye a la lista con medallas, que ponía al segundo
campeón debajo con un «·», como si fuera menos.

#### Scenario: dos campeones, juntos arriba
- GIVEN un mes cerrado con dos jugadores empatados en el primer puesto
- WHEN se compone el podio de cierre
- THEN los dos van en la columna central, encima del escalón más alto, y no hay lista de medallas

```yaml
checks:
  - type: regex
    file: tools/podio.py
    pattern: 'podio_de_texto\(\s*f"🏆 \*Así queda el podio · Temporada'
    describe: "el podio de cierre usa el podio ASCII del resumen"
```

verified-by:
  - tests/slices/podio-de-cierre-de-mes/test_podio.py
