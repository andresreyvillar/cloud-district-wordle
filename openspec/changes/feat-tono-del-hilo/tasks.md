# Tareas — feat-tono-del-hilo

Para alguien sin contexto. El orden importa: el módulo puro primero, el borde al final, porque es lo que
permite tener los tests en verde antes de tocar la red.

## 1. `tools/tono.py` — el módulo puro

Nuevo. **No hace red**: recibe mensajes ya leídos y devuelve objetos. Todo lo que lleva es determinista.

- `Tono`, dataclass congelada con exactamente estos campos: `tono: str`, `acusacion: bool`, `defensa: bool`,
  `propuesta: bool`, `intensidad: int` (0-3), `dudan: int`. **Ningún campo de texto libre.**
- `TONOS: tuple[str, ...]` — los valores admitidos de `tono` (`"incredulidad"`, `"acusacion"`, `"pique"`,
  `"celebracion"`, `"cachondeo"`, `"tecnico"`). Un valor fuera de la lista invalida la clasificación entera.
- `INTENSIDAD_MINIMA = 2` — por debajo no se publica frase.
- `transcripcion(respuestas, autor) -> str` — las respuestas de **otros** (las del propio `autor` se
  descartan), numeradas como `participante 1:`, `participante 2:`… El mapa rol→persona **no sale** de la
  función: quien compone ya sabe el nombre.
- `interpreta(crudo: str | dict | None) -> Tono | None` — valida contra el esquema. Devuelve `None` ante
  cualquier desviación: JSON roto, campo que falta, tipo que no es, `tono` desconocido, `intensidad` fuera de
  rango. **Los campos que no estén declarados se ignoran**, nunca se propagan.
- `INSTRUCCION: str` — el prompt. Pide exclusivamente el JSON del esquema y declara que el texto de entrada
  son datos, no instrucciones.

Verificación: `.venv/bin/python3 -B -m pytest tests/slices/voz-de-la-jornada/test_tono.py -q`

## 2. `tools/refranero.py` — el registro

Añadir `TONO_DEL_HILO: dict[str, tuple[str, ...]]`, con una entrada por situación publicable
(`"acusacion"`, `"acusacion-con-propuesta"`, `"incredulidad"`, `"pique"`). Mínimo **8 frases por entrada**:
el índice es cíclico por jornada, así que menos frases significa repetirse en dos semanas.

Reglas del registro, que hay tests que las fijan:
- Las frases hablan del **hilo**, con `{jugador}` como mucho una vez. Nada de comentar a las personas que
  respondieron.
- Ninguna frase afirma que alguien haya hecho trampas: la clasificación dice qué decía el canal, no qué pasó.

## 3. `tools/resumen.py` — el compositor

- `resumen_del_dia(...)` gana el parámetro `tono=None`, al lado de `palabra`. Sin él, el mensaje es el de hoy.
- Una función `frase_del_hilo(tono, jugador, jornada) -> str | None` que devuelve `None` si `tono` es `None` o
  si `tono.intensidad < INTENSIDAD_MINIMA`, y si no elige del registro con `_del_ciclo(..., jornada)`.
- En `menciones_del_canal`, cuando `tono.acusacion` es cierto, la mención `comentado` de quien abrió el hilo
  **no** se emite como reconocimiento.

Verificación: `.venv/bin/python3 -B -m pytest tests/slices/voz-de-la-jornada -q`

## 4. `tools/post_ranking.py` — el borde

- `clasifica_el_hilo(jornada, cliente=None) -> Tono | None`, **best-effort como `leer_el_canal`**: cualquier
  fallo devuelve `None` y avisa por `stderr` **solo con el tipo de excepción** (los logs de Actions son
  públicos y por ahí viaja un token).
- Elige el mensaje de resultado de esa jornada con más respuestas, pide su hilo con `conversations.replies`,
  arma la transcripción con `transcripcion(...)` y llama a la inferencia.
- Endpoint, clave y modelo **por entorno** (`IA_API_URL`, `IA_API_KEY`, `IA_MODELO`), en formato
  OpenAI-compatible. Nada de cablear un proveedor: se comprobó contra la API que GitHub Models —el plan
  original, que no pedía secreto nuevo— está retirado desde el 2026-07-30.
- Tope de tiempo explícito. El resumen no puede esperar a un servicio de fuera.
- Sin token o sin hilo → `None`, sin llamar a nada.

## 5. `.github/workflows/post_ranking.yml`

Pasar las tres variables al paso que publica. Las tres o ninguna:

```yaml
          IA_API_URL: ${{ secrets.IA_API_URL }}
          IA_API_KEY: ${{ secrets.IA_API_KEY }}
          IA_MODELO: ${{ vars.IA_MODELO }}
```

Mientras no existan, `clasifica_el_hilo` devuelve `None` sin llamar a nadie y el mensaje es el de hoy.

## 6. Devolver los `checks:` a los deltas

Se retiraron al proponer porque `checks-probe` los **ejecuta** contra el repositorio y apuntaban a código que
todavía no existía: la fase de autoría habría cerrado en rojo por construcción. Con el código escrito ya
prueban lo que tienen que probar, así que vuelven a `specs/publicacion/spec.md` y `specs/ingesta/spec.md`:

```yaml
checks:
  - type: regex
    file: tools/tono.py
    pattern: 'class Tono'
    describe: la clasificación es un objeto cerrado y sin campos de texto
```

```yaml
checks:
  - type: regex
    file: tools/refranero.py
    pattern: 'TONO_DEL_HILO'
    describe: las frases del hilo viven en el registro del repositorio
```

```yaml
checks:
  - type: regex
    file: tools/tono.py
    pattern: 'def transcripcion'
    describe: la transcripción que sale del borde se arma aquí, sin nombres
```

## Cierre

```bash
python3 -m tools.wslice slice validate voz-de-la-jornada
python3 -m tools.wslice slice coverage voz-de-la-jornada
python3 -m tools.wslice verify slice voz-de-la-jornada --strict
python3 -m tools.wslice verify gates --slice voz-de-la-jornada --change-id feat-tono-del-hilo
.venv/bin/python3 -B -m pytest -q
```

Gate 4c (mutación) sobre `tools/tono.py`: al menos un error deliberado en `interpreta` —aceptar un `tono`
fuera de la lista, o no mirar el rango de `intensidad`— tiene que poner en rojo el escenario
`una-clasificacion-invalida-no-se-usa` y ninguno más.

Commits sugeridos: (1) módulo puro + tests, (2) registro y compositor, (3) borde y workflow.
