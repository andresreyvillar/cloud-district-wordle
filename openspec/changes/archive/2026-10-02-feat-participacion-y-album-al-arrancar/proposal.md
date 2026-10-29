# El resumen cuenta la participación, y el álbum tiene ranking desde el primer día

> Slices: `clasificacion-de-figuras` · `resumen-diario-compuesto` (modificaciones).

## Why

El 2 de octubre juegan 18 personas, récord del canal (el anterior, 16), y debutan 7, entre ellos los
primeros usuarios externos. El resumen no lo contaba. Y no salía el podio de figuras: el álbum exigía cinco
partidas para clasificar, así que los primeros días del mes no había ranking de belleza.

Decisiones del dueño: **bajar el mínimo, escalonado** (tantas partidas como jornadas lleva el mes, hasta
cinco); el bloque de participación **solo cuando es noticia**; los debutantes **por su nombre**; una coletilla
pop que rota.

## What Changes

- `tools/album.py`: `minimo_de_la_temporada`; `minimo` y `clasificado` usan el mínimo efectivo.
- `tools/rules.py`: la regla `figuras-ponderadas` explica el mínimo que crece.
- `tools/resumen.py`: `bloque_participacion`, tras la jornada; el juego y las figuras en lista.
- `tools/podios.py`: `lista_de_texto`. El podio ASCII queda solo para el marcador (decisión del dueño).
- `tools/comentarios.py`: el plural de las cinco claves que no lo tenían (`sembrado`, `no-inspirado`,
  `clavada`, `rezagado`, `rezagado-con-suerte`); la vista previa del 2 de octubre decía «Carlos H. y Rubén
  Cogollor ha ido a lo suyo».

## Out of Scope

- La temporada 0 conserva el mínimo fijo.
- La web no cambia de código: enseña el `minimo` que trae la instantánea.
- El mensaje de la victoria del mes mantiene sus tres podios ASCII hasta que el dueño decida.

## Impact

- **El álbum de octubre cambia en la siguiente materialización**: hoy clasifica quien jugó las dos jornadas.
- El resumen de esta noche ya lleva los tres podios y el bloque de participación.

## Validation Gates

```bash
python3 -m tools.wslice slice validate clasificacion-de-figuras
python3 -m tools.wslice slice validate resumen-diario-compuesto
python3 -m tools.wslice slice coverage clasificacion-de-figuras
python3 -m tools.wslice slice coverage resumen-diario-compuesto
python3 -m tools.wslice verify gates --slice clasificacion-de-figuras --change-id feat-participacion-y-album-al-arrancar
python3 -m tools.wslice verify gates --slice resumen-diario-compuesto --change-id feat-participacion-y-album-al-arrancar
.venv/bin/python3 -B -m pytest tests/slices/clasificacion-de-figuras tests/slices/resumen-diario-compuesto
```

## Capabilities

| Capability | Requirements |
|---|---|
| `ranking` | el mínimo de partidas del álbum crece con el mes (MODIFIED) |
| `resultados` | la instantánea publica el mínimo que se aplicó (MODIFIED) |
| `publicacion` | el resumen cuenta la participación cuando es noticia · juego y figuras en lista (MODIFIED) |
