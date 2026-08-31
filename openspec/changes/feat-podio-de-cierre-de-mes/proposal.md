# Al empezar el mes, el canal ve el podio del que cierra

## Por qué

El marcador se reinicia cada mes y eso pasaba **sin que nadie lo dijera**: un día la tabla estaba llena y al
siguiente vacía. Ni se felicitaba al campeón ni se marcaba el arranque.

## Dos cosas que no se podían hacer como se pidieron

**«El primer día de competición de cada mes» no se puede expresar en cron.** Al restringir día del mes y día de
la semana a la vez, cron los interpreta como **O** y no como Y: `1-7 * 1-5` dispararía además todos los
laborables del mes. La condición vive en el código y **sale de los datos** (§10): la temporada en curso es la
del último resultado y se celebra la inmediatamente anterior.

**Las animaciones no caben en un mensaje de Slack.** Un mensaje no ejecuta CSS; la web anima el podio y una
captura lo congela. Se hace con **imagen estática**, que es lo que se pidió literalmente («una imagen de un
podio») y reutiliza la captura de Playwright que ya existe: cero dependencias nuevas. Un GIF exigiría capturar
fotogramas y montarlos con una dependencia más, para un segundo y medio de movimiento una vez al mes; queda
como posible mejora, decidido con el dueño.

## Cómo

```
.github/workflows/post_podium.yml   cron 0 9 1-7 * *   (11:00 Madrid, días 1 al 7)
tools/podio.py                      la lógica pura: qué mes, quién sube, qué se dice
tools/post_podium.py                el borde: guarda, captura y publicación
objetivo de captura                 /2/t/<mes cerrado> → espera .podio-card, captura .podio
refranero                           PODIO_CAMPEON (12) y NUEVA_TEMPORADA (12)
```

**Del 1 al 7 y no solo el 1** porque el mensaje es idempotente y GitHub descarta ventanas —medido aquí, hasta
un 86% en los peores días—: si el 1 no corre, se publica el 2 y el cierre no se pierde.

**A las 11:00 de Madrid** porque hace falta al menos un resultado del mes nuevo para saber que el anterior ha
cerrado, y el pico de publicación del canal está entre las 08:00 y las 10:00.

**La imagen es la de la web**, no un dibujo aparte: así el mensaje y la página no pueden decir cosas distintas.

## Así queda con los datos de agosto

```
🏆 Temporada 1 · agosto 2026 — así queda el podio

🥇 Andrés R. — 3,81
🥈 Claire — 3,92
🥉 Dani Sanchez — 4,05

👑 Andrés R. ha ganado el mes. Nadie ha aguantado tanto tan arriba.
Se lleva además 📅 🌀 🗂️ 💪 ✨ 🎯 de la temporada.

🔄 Todos a cero otra vez. Aquí no hay herencias, hay que volver a ganárselo.
```

## Qué no hace

- **No celebra la temporada 0**: no cerró un mes, es el bloque anterior a que existieran las temporadas.
- **No celebra tras un salto de meses**: el mes en curso ha de ser consecutivo al cerrado, o se estaría
  felicitando otra vez a quien ganó algo ya celebrado.
- No escribe nada en Supabase.
