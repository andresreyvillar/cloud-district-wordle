# Garantizar una sincronización por hora: reintento y reloj de repuesto

## Las dos causas, medidas

**1. El planificador de GitHub descarta ventanas.** De 24 ejecuciones diarias esperadas salen 5 o 6, con
huecos de 3 a 6 horas seguidas. Está documentado: «algunos trabajos en cola pueden descartarse», sin reintento
ni recuperación. No es nuestro código — el disparo manual funciona siempre.

Ya se probó lo único que GitHub recomienda, mover el cron fuera del minuto en punto: **empeoró** (de 21-23
diarias a 2-6), se revirtió, y siguió igual de mal. Dentro de GitHub no quedaba nada por probar.

**2. Fallos transitorios de red.** 4 de las últimas 200 ejecuciones (2%) murieron con `httpx.ReadTimeout`
escribiendo en Supabase. Sin reintento, esa hora se perdía entera — y con las ventanas ya escasas, perder
también las que sí se disparan era el fallo más barato de arreglar que quedaba.

## Qué se hace

**Reintento en el borde.** Tres intentos con espera creciente en la lectura y la escritura de Supabase. Solo
para fallos que pueden ser transitorios: unas credenciales mal puestas fallan a la primera, porque
reintentarlas solo retrasa el diagnóstico.

**Reloj de repuesto en Cloudflare.** El Worker que ya sirve la web gana un Cron Trigger que despierta el
workflow por `workflow_dispatch`. No añade proveedor —la cuenta ya existe— y los cron de Workers sí son
fiables.

```
GitHub Actions    0 * * * *     ← sigue, por si funciona
Cloudflare Worker 10 * * * *    ← el que garantiza
```

Van a minutos distintos para no gastar dos runners cuando las dos ventanas coincidan. **Coincidir no rompe
nada**: la ingesta no reescribe resultados ya guardados y la materialización hace `upsert`.

## Lo que hay que hacer a mano

El disparador está **apagado hasta que exista el secreto**:

```bash
npx wrangler secret put GITHUB_TOKEN     # token con permiso de Actions (workflow o actions:write)
npx wrangler deploy
```

Sin `GITHUB_TOKEN` el `scheduled` no hace nada, que es el estado por defecto y lo que hace seguro desplegar
esto sin haber creado el token todavía.

## Qué no hace

- **No toca la web.** `scheduled` es un manejador aparte de `fetch`: un fallo del disparador no puede afectar
  a lo que el grupo usa a diario, y por eso captura sus propios errores.
- No recupera ventanas perdidas hacia atrás: garantiza la siguiente, no rehace la anterior.
- No mueve el pipeline fuera de GitHub Actions. Si esto tampoco basta, el siguiente paso sería reescribirlo
  en el Worker, que es mucho más trabajo.
