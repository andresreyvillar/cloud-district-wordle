# Proposal — feat-figuras-de-la-jornada

> **Slice:** `figuras-de-la-jornada` (openspec/slices/estadisticas/figuras-de-la-jornada.md)

## Why

`/hoy` decía quién ha jugado y en cuántos intentos, pero no **qué ha dibujado cada uno** — la mitad del
juego desde que existe el álbum, y ausente justo en la única vista de la jornada abierta, que es donde la
gente mira cuando acaba de publicar.

## La decisión que manda: la web no clasifica

`results.js` ya trae la cuadrícula cruda, así que clasificar en el navegador era lo fácil. Serían **120
líneas de reglas calibradas contra 30 fichas etiquetadas**, y en la primera recalibración dirían cosas
distintas que el álbum y que el bot. En este repositorio, dos definiciones de lo mismo han divergido tres
veces esta semana.

La figura la calcula Python y viaja en la instantánea (ADR 0008).

## Y no salen del álbum

El álbum agregado cuenta **solo lo que puntúa**, y una jornada abierta no alcanza la muestra mínima a media
mañana: con `resultados_de_temporada`, hoy no tendría figuras hasta que jugara la quinta persona.

Son dos preguntas distintas —«qué puntúa» y «qué se ha dibujado hoy»— y se responden por separado. Un
mutante lo confirma: cambiar la fuente a `resultados_de_temporada` deja la jornada abierta sin dibujos.

## What Changes

```
tools/album.py        `ultima_jornada`: la jornada más reciente y la figura de cada uno
v2/js/data/dia.js     `figurasDeLaJornada`: jugador → emoji, del catálogo publicado
v2/js/ui/hoy.js       `tarjetasDeHoy`: el emoji en cada tarjeta + el aviso de desfase
v2/css/styles.css     una cuarta columna en la tarjeta, que colapsa si no hay figura
```

**Una sola jornada, no el histórico.** Publicar las figuras de las 181 jornadas de la temporada 0 añadiría
miles de entradas que nadie lee; la vista de hoy mira hoy.

## El desfase se declara

La puntuación se lee de las filas crudas y la figura de la instantánea, que se materializa cada hora: quien
publique entre dos pasadas aparece con su nota y sin dibujo. La vista lo dice en lugar de dejar un hueco que
parece un fallo.

## Verificado en navegador

`/hoy` muestra el emoji junto a los intentos, el aviso aparece cuando toca y no hay errores de consola.

Y de paso deja a la vista, sin margen de duda, **el efecto de las identidades partidas**: Claire, Juan
(Kokuma), Dani Sanchez, Raquel, Sandra, Cata, Clara C y Luis aparecen **dos veces cada uno** en la jornada,
y la mitad de sus tarjetas sin figura. Se arregla con `tools/canonical_identity.py`, que ya está verificado.

## Impact

- Cierra el eje de figuras en las tres vistas: temporada, ficha y jornada.
- El aviso de desfase no se verá casi nunca en la práctica: el cron corre cada hora y la gente publica a lo
  largo del día.
