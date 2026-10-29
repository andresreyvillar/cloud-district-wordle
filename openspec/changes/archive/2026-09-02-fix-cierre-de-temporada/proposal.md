# La temporada cerrada seguía anunciándose como abierta

## Qué pasó

El 2 de septiembre, con agosto cerrado desde el día 1, la web seguía diciendo que agosto estaba **en curso**.

Lo vio el dueño. Y el cálculo no tenía la culpa:

```
temporadas() dice:  2026-09 → en curso · 2026-08 → cerrada   ✔ correcto
la instantánea:     2026-08 → estado: 'en curso'             ✘ congelada
                    fechada el 2026-09-01 a las 01:42
```

## Por qué

El estado vive **dentro de la instantánea**, y el cron rematerializaba solo la temporada en curso:

```python
objetivo = [... for entrada in lista if entrada["estado"] == EN_CURSO]
```

Cuando agosto dejó de estar en curso salió de ese filtro, así que nadie la volvió a escribir y se quedó con el
`estado: en curso` del último día que lo estuvo. No es solo la etiqueta: agosto también se quedó sin su última
rematerialización, con lo que la clasificación de la jornada final podía no estar reflejada.

## Qué cambia

Se rematerializa además **la última cerrada**. Con una basta: solo ella puede tener el estado obsoleto, porque
las anteriores ya se escribieron estando cerradas. Recalcular todas cada hora significaría rehacer el
histórico entero —181 jornadas— para arreglar una etiqueta.

```
antes:  2026-09
ahora:  2026-09, 2026-08          (el histórico sigue fuera)
```

## Qué no hace

- **No recalcula el histórico**: sigue necesitando `--todas`, que es lo que evita rehacer 181 jornadas cada
  hora.
- No cambia el cálculo del estado, que ya era correcto: lo que fallaba era **cuándo se escribía**.
