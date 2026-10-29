# El resumen dice de qué iba el hilo, no solo cuánto midió

> Slice: `voz-de-la-jornada` (modificación significativa: el slice ya lee el canal; esto cambia hasta dónde).

## Por qué

El mensaje sabía decir que alguien había armado el hilo del día, pero no de qué iba. Medido sobre la jornada
1709:

| Señal | Quien abrió el hilo | El resto del día |
|---|---|---|
| Respuestas | 26 | 0 |
| Reacciones | **0** | 46 repartidas entre cinco |

Las dos señales apuntaban en direcciones opuestas y la mención solo miraba una, así que el resumen publicó
**«arrasa: la mejor nota (en 1) y el hilo del día»** el día en que el grupo lo estaba acusando de hacer
trampas. Seis de las veinte respuestas ajenas traían marcas de duda, de cinco personas distintas, y la palabra
«trampa» salió tres veces.

**El grupo lo notó antes que el código.** En ese mismo hilo alguien escribió «el bot hoy: ovación en el canal
para X», y otra persona «bot esto es para ti: que sepas que estamos llamando tramposo a X». No es una mejora
estética: el mensaje quedó en ridículo delante de todo el canal.

Un contador no distingue una ovación de un juicio. Hace falta leer la conversación.

## Qué cambia

1. **El hilo del día se lee entero**, en el borde, y se anonimiza: cada persona pasa a ser un rol y ningún
   nombre ni identificador de Slack viaja con el texto.
2. **Un modelo lo clasifica** y devuelve un objeto cerrado —tono dominante, si hubo acusación, defensa o
   propuesta de norma, la temperatura y cuántas personas dudan—. **Sin proveedor cableado**: la URL, la clave
   y el modelo entran por entorno, en formato OpenAI-compatible.

   El plan era GitHub Models con el `GITHUB_TOKEN` del propio workflow y sin secreto nuevo. Al comprobarlo
   contra la API antes de escribir el borde resultó estar **retirado desde el 30 de julio de 2026** —devuelve
   `410 github_models_retirement_brownout`—. De ahí que el proveedor no se cablee: atar el repositorio a otro
   concreto repetiría el mismo error dentro de un año. Sirve cualquiera con plan gratuito y endpoint
   compatible; se gasta **una petición al día**.

   Consecuencia: **hace falta un secreto nuevo**, y hasta que exista el slice está apagado. Eso no es un
   inconveniente sino el orden correcto — mandar la conversación del canal a un tercero es una decisión que
   se toma a mano, no un efecto secundario de mergear.
3. **La clasificación entra al compositor por parámetro**, exactamente como ya entra `palabra`: la red se
   queda en el borde y el texto del mensaje sigue comprobándose entero en un test (§10).
4. **La frase sale del refranero del repositorio**, elegida por la clasificación y el número de jornada.
5. **La mención del hilo deja de coronar** a quien abrió una conversación que era una acusación.

### El modelo clasifica; el repositorio habla

Es la decisión de diseño que sostiene todo lo demás, y la razón es concreta: **en este canal la gente ya le
escribe al bot**. Si la prosa del modelo se publicara tal cual, cualquiera podría dictarle al bot lo que dice
sobre un compañero identificable delante de todo el grupo, escribiéndolo en un hilo. Con la frase saliendo del
registro, una instrucción colada en la conversación como mucho cambia una casilla del esquema — y la casilla
no redacta. Del objeto devuelto solo se leen los campos declarados; lo demás se ignora.

## Fuera de alcance

- **Publicar prosa escrita por el modelo.** Es lo que haría el mensaje más rico y también lo que abre la
  puerta anterior. Si algún día se quiere, es otra decisión y otro change pack.
- **Citar a nadie**, literal o parafraseado.
- **Persistir nada.** La clasificación vive lo que dura el cron, como las señales.
- **Penalizar a nadie.** Este cambio cuenta lo que pasó; no toca puntos, ni reglas, ni clasificación.
- **Un clasificador propio por léxico.** Se probó sobre el hilo real y funciona —6 de 20 respuestas, 5
  personas—, pero mantener un diccionario de insultos en un repositorio público es peor que no tenerlo, y no
  distingue la ironía. Queda como posible respaldo futuro, no entra aquí.

## Impact

| Qué | Detalle |
|---|---|
| Slices | `voz-de-la-jornada` (+10 escenarios, 24 → 34) |
| Capabilities | `publicacion` (4 Requirements), `ingesta` (2), `estadisticas` (1 MODIFIED) |
| Archivos nuevos | `tools/tono.py`, `tests/slices/voz-de-la-jornada/test_tono.py` |
| Archivos tocados | `tools/post_ranking.py` (borde), `tools/resumen.py` (compositor), `tools/refranero.py` (registro), `.github/workflows/post_ranking.yml` (entorno) |
| Esquema | **Ninguno.** Nada se persiste |
| Secretos | `IA_API_URL` + `IA_API_KEY` (secrets) y `IA_MODELO` (variable). **Sin las tres, la clasificación no se llama y el mensaje es el de hoy** |
| Compatibilidad | El resumen se publica igual sin clasificación: el camino sin modelo es el de hoy |
| Riesgo | Que un tercero lea conversación del canal (anonimizada, solo el hilo del día) e inyección desde el canal (acotada por el esquema cerrado) |

## Validation Gates

```bash
python3 -m tools.wslice slice validate voz-de-la-jornada
python3 -m tools.wslice slice coverage voz-de-la-jornada
python3 -m tools.wslice verify slice voz-de-la-jornada --strict
python3 -m tools.wslice verify gates --slice voz-de-la-jornada --change-id feat-tono-del-hilo
.venv/bin/python3 -B -m pytest tests/slices/voz-de-la-jornada -q
.venv/bin/python3 -B -m pytest -q
```

## Capabilities

| Capability | Requirements | Qué aporta |
|---|---|---|
| `publicacion` | 4 ADDED | Que el mensaje diga de qué iba el hilo, con frase propia y sin publicar nada sin comprobar |
| `ingesta` | 2 ADDED | Leer el hilo del día y sacarlo del borde sin nombres |
| `estadisticas` | 1 MODIFIED | Que el recuento de respuestas deje de leerse como aplauso |
