# Indicadores de juego en la ficha: eficiencia, apertura, suerte y acierto más milagroso

> Slice: `indicadores-de-juego` (nuevo).

## Why

La media no dice por qué alguien necesita los intentos que necesita. El dueño pidió que cada jugador vea en su
ficha su eficiencia, lo bien que abre, su suerte y su acierto más afortunado. Pidió también un medidor de trampas y,
tras ver el análisis, lo descartó: con una cuarentena de jugadores siempre hay rachas del 1–2 % por puro azar, y
una etiqueta así junto a un nombre en una web pública sería una acusación hecha por un número.

## What Changes

- `tools/indicadores.py` (nuevo, puro): coloreado del juego (sin tildes, con Ñ), candidatas estimadas antes de
  cada intento, y los cuatro indicadores por jugador y del grupo.
- `tools/seasons.py`: `instantanea` añade `indicadores` cuando recibe la lista de soluciones.
- `tools/materialize_seasons.py` y `tools/local_stack.py`: descargan la lista en el borde y la pasan; si falla, se
  materializa sin el bloque.
- `v2/js/ui/jugador.js` (y `v2/css/styles.css`): el bloque «Cómo juegas» en la ficha.

## Out of Scope

- Cualquier medidor, etiqueta o ranking de sospecha de trampas.
- Indicadores en el resumen de Slack o en el marcador.
- Saber qué palabras probó cada uno: solo se conocen los colores.

## Impact

- El cron horario descarga la lista de soluciones (un fichero) en cada materialización.
- La instantánea crece con un bloque por jugador. Sin cambios de esquema.
- **Datos de personas reales en una web pública**: el bloque enseña la suerte de cada uno, en tono de juego y
  sin juicios.

## Validation Gates

```bash
python3 -m tools.wslice slice validate indicadores-de-juego
python3 -m tools.wslice slice coverage indicadores-de-juego
python3 -m tools.wslice verify gates --slice indicadores-de-juego --change-id feat-indicadores-de-juego
.venv/bin/python3 -B -m pytest tests/slices/indicadores-de-juego
node --test tests/slices/indicadores-de-juego/
```

## Capabilities

| Capability | Requirements |
|---|---|
| `estadisticas` | los indicadores de juego se calculan de las cuadrículas, de forma determinista y sin publicar palabras |
| `dashboard` | la ficha pinta el bloque «Cómo juegas» |
