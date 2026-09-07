# Cada disparo cubre cinco horas y media, en vez de una

## Por qué: los tres relojes probados y lo que dio cada uno

```
                        resultado
GitHub Actions          6-8 de 24 al día, a minutos arbitrarios (27, 34, 07, 54…)
Cloudflare Worker cron  cero disparos en cuatro días
cron-job.org            cero disparos desde que se configuró
```

**Cloudflare está descartado con prueba directa.** Se escucharon sus logs durante la ventana de las 09:10 y se
capturaron **23 invocaciones `fetch` y cero de cron**: el tail estaba vivo y recibiendo, pero su planificador no
invoca el Worker. Coincide con los informes de su comunidad. De cron-job.org no hay diagnóstico: su historial
de ejecuciones vive en su panel.

Y de la propia experiencia: mover el cron de minuto se probó, **empeoró**, y se revirtió.

## El cambio de enfoque

En lugar de pelear por más disparos, **cada disparo cubre más tiempo**. El job sincroniza cada 55 minutos
durante cinco horas y media, todo dentro de la misma ejecución.

```
antes:  un disparo = una sincronización     → 6-8 al día
ahora:  un disparo = 7 sincronizaciones     → cobertura continua
```

Con el hueco máximo medido en el planificador de GitHub —**5,6 h**, mediana 3,6— una cobertura de 5,5 h por
disparo cierra todos los huecos reales salvo el peor, y a ese le faltarían seis minutos.

## Los números, y de dónde salen

```
espera entre vueltas   55 min   ciclo de 56 min con los ~35 s que tarda la sincronización,
                                así que ningún hueco pasa de una hora
vueltas                7        334 min de job, bajo el techo de 350; ocho no caben (390)
timeout-minutes        350      el límite duro de GitHub son 360 y mata el job
cobertura por disparo  5,5 h
```

El repositorio es **público**, así que los minutos de Actions son ilimitados y gratis: cinco horas y media de
runner al día no cuestan nada.

## Detalles que condicionan el diseño

**No se auto-despierta.** El `GITHUB_TOKEN` automático **no puede** lanzar `workflow_dispatch` —GitHub lo
bloquea para evitar bucles— y montar un PAT solo para esto añadiría una credencial que mantener. No hace
falta: los 6-8 disparos diarios de GitHub bastan para relanzar el latido.

**Una sola ejecución viva** (`concurrency` con `cancel-in-progress`). Cada disparo cancela el latido en curso y
arranca uno nuevo, así que la ventana se reinicia en cada disparo en lugar de acumular latidos solapados.
Cancelar a media sincronización es seguro: la ingesta no reescribe resultados ya guardados y la materialización
hace `upsert`.

**Un fallo de una vuelta no aborta el latido.** Se registra como aviso y se sigue: perder una hora es mejor que
perder las cinco siguientes. La suma de fallos sí se propaga al final, para que la ejecución salga en rojo.

**El disparo manual sigue siendo de una vuelta** (`vueltas` por defecto a 1 en `workflow_dispatch`), para que
lanzarlo a mano no ocupe el runner cinco horas.

## Qué no hace

- **No garantiza al 100%** la cadencia horaria: si GitHub no dispara en más de 5,5 h, hay hueco. Lo que hace
  es convertir el problema de «6-8 disparos al día» en «cobertura continua salvo huecos excepcionales».
- No toca el pipeline: los dos comandos son los de siempre.
- El cron de Cloudflare se deja puesto, documentado como no funcional, por si su planificador se recupera.
