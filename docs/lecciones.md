# Lecciones → Reglas (bucle error→regla)

> **Principio (§11 slice-system.md):** la lección NO es el artefacto — **la regla codificada lo es**.
> Todo fallo de proceso (gate en rojo con causa raíz, error del agente, hallazgo humano) produce una
> regla permanente en el punto ejecutable más fuerte posible, en esta cascada:
>
> **1. gate/CI** (mecánico) > **2. protocolo** (slice-system) > **3. skill** (fase) > **4. CLAUDE.md** (agente)
>
> Una lección con `estado: pendiente` es DEUDA — `/slice-audit` la reporta. Se registra con `/leccion`.

## Formato de entrada

```markdown
### AAAA-MM-DD — <síntoma en una frase>
- **Qué pasó:** ...
- **Causa raíz:** ...
- **Regla:** ...
- **Codificada en:** <archivo/gate/regla concreta> · **estado:** codificada | pendiente
```

---

### 2026-08-04 — Una migración de identidad se dio por hecha sin verificarla contra los datos
- **Qué pasó:** el commit que cambiaba la identidad de jugador a `slack_user_id` dejó el código con
  la apariencia de estar migrado (diccionario de IDs, `on_conflict` por ID), pero el extractor seguía
  emitiendo nombres mostrados. Resultado: 1234 de 1532 filas guardan un nombre en la columna de ID,
  el diccionario de identidades quedó inerte y hay jugadores duplicados por renombre en Slack.
- **Causa raíz:** el cambio se validó leyendo el código, no consultando el estado de los datos que
  produce. Nada obligaba a demostrar el comportamiento observable end-to-end.
- **Regla:** un cambio de comportamiento se demuestra con un test de escenario que observe el efecto
  (la fila resultante), no con la lectura del código que lo intenta. Y antes de tocar identidad,
  ranking o deduplicación, se comprueba el estado real de la columna en Supabase.
- **Codificada en:** `openspec/slice-system.md` §6 Fase 2 (TDD rojo obligatorio antes de implementar)
  y Gate 4c (mutación: un test que no cae al mutar el código no protege nada) ·
  **estado:** codificada

### 2026-08-04 — El método no se aplicaba porque no existía
- **Qué pasó:** el proyecto creció a base de commits directos a `main` sin especificación ni tests;
  las decisiones (ancla de fechas, umbrales del ranking, unificación de nombres) viven solo en el
  código y en scripts one-shot ya ejecutados.
- **Causa raíz:** no había método ni artefactos donde registrar el comportamiento esperado.
- **Regla:** todo comportamiento observable nuevo pasa por slice + change pack + TDD antes de
  implementarse; los cambios sin comportamiento observable van como change pack `Slice: N/A`.
- **Codificada en:** `openspec/slice-system.md` (constitución completa), `.claude/skills/*` y
  `CLAUDE.md` · **estado:** codificada

### 2026-08-04 — El bytecode cacheado falseó el resultado de una prueba de mutación
- **Qué pasó:** durante el Gate 4c del pack de adopción, tras restaurar el segundo mutante
  (`DOCSTRING_LOOKAHEAD = 0` → `3`) los tests seguían en rojo con el archivo ya correcto. El
  diagnóstico mostró que el `.pyc` del mutante y el `.py` restaurado tenían **el mismo tamaño y el
  mismo mtime al segundo** (1785840201), así que Python reutilizó el bytecode del mutante.
- **Causa raíz:** la invalidación de bytecode de CPython compara mtime con resolución de segundo.
  Mutar y restaurar dentro del mismo segundo, cambiando un solo carácter, cae justo en el hueco.
  Podía haber fallado en la dirección contraria y peor: un mutante ejecutándose como código sano
  habría dado el gate por bueno.
- **Regla:** todo comando de test del protocolo se ejecuta con `python3 -B` (no escribe bytecode).
  Si ya hay `__pycache__` sospechoso, purgarlo antes de creerse un veredicto.
- **Codificada en:** `openspec/slice-system.md` §6 Fase 4.1 y Gate 4c · `.claude/skills/slice-implement/SKILL.md`
  (paso 5.c y "trampas del procedimiento") · `CLAUDE.md` (Commands) · `README.md` ·
  **estado:** codificada

### 2026-08-04 — Un `git restore` se llevó por delante un arreglo hecho durante el gate
- **Qué pasó:** al reforzar `tools/wslice/gates.py` en medio del Gate 4c, el arreglo se hizo después
  del `git add -A` inicial. El `git restore` de la mutación siguiente restauró el index — que no
  tenía el arreglo — y lo borró sin aviso.
- **Causa raíz:** el procedimiento describe el index como red de seguridad para deshacer mutaciones,
  pero no dice que hay que actualizarlo cuando aparece un cambio legítimo a mitad del gate.
- **Regla:** durante el Gate 4c, todo arreglo real (test reforzado o código corregido) se stagea
  inmediatamente antes de aplicar la siguiente mutación.
- **Codificada en:** `openspec/slice-system.md` §6 Gate 4c (viñeta "el index es la única red") +
  `.claude/skills/slice-implement/SKILL.md` ("trampas del procedimiento") · **estado:** pendiente
- **REINCIDENCIA (misma fecha, slice de medallas):** la regla ya estaba escrita en el protocolo Y en la
  skill, y aun así se incumplió **dos veces más** en la misma sesión, perdiendo un arreglo cada vez. Según
  la cascada del §11, una regla que no se aplica pese a estar codificada indica que **el punto de
  codificación es demasiado débil**: dos niveles de documentación no bastan para un paso manual que se
  repite. Sube a nivel mecánico. *Destino: un comando `wslice mutate <archivo> --expr <a> <b>` que haga el
  ciclo completo —stage, mutar, ejecutar, restaurar, verificar verde— sin que el operador pueda saltarse
  el stage.*

### 2026-08-04 — El gate `federated-untouched` no veía una capability nueva completa
- **Qué pasó:** el mutante que quitaba el filtro `.md` del gate sobrevivió: ningún test lo cubría. Al
  escribir los tests que faltaban, uno de ellos falló contra el código sano y destapó un agujero real
  heredado del port: `git status --porcelain` colapsa un directorio enteramente sin trackear en una
  sola línea (`?? openspec/`), así que crear `openspec/specs/<nueva>/spec.md` en una capability nueva
  esquivaba el gate por completo.
- **Causa raíz:** el gate se portó de `slspec` literalmente, incluida esa suposición sobre la salida
  de git, y no había test que la ejercitase porque depende del repo real y no de un fixture.
- **Regla:** el gate usa `git status --porcelain --untracked-files=all`. Y ningún gate se considera
  cubierto sin al menos un test que monte el estado del que depende (aquí: un repo git temporal).
- **Codificada en:** `tools/wslice/gates.py` (`--untracked-files=all` + comentario del por qué) y
  `tests/harness/test_gates.py` (5 tests nuevos: pass, fail, staged, no-markdown, sin-repo) ·
  **estado:** codificada — *el mismo agujero existe en `slspec` de pga-cms; conviene avisar allí*

### 2026-08-04 — Una cifra medida sobre una página se propagó como hecho a cinco documentos
- **Qué pasó:** el análisis inicial de la tabla midió "1312 de 1530 filas guardan un nombre en la columna
  de ID" sobre un volcado que solo traía **la primera página de 1000 filas** de PostgREST. La cifra real,
  consultada por SQL, es **1234 de 1532**. El número equivocado llegó a dos proposals, el registro de
  lecciones y el roadmap, y se citó varias veces como argumento.
- **Causa raíz:** PostgREST pagina a 1000 filas por defecto y devuelve un `Content-Range` que lo dice. El
  primer análisis paginó para el conteo total pero no para esa métrica concreta, y nadie volvió a
  comprobarla porque ya estaba escrita en un documento.
- **Regla:** toda cifra que entre en un proposal, un ADR o una lección se mide con una consulta que
  devuelva el agregado completo —`count(*)` en SQL, o paginación explícita comprobada contra
  `Content-Range`—, nunca contando filas de un volcado parcial. Y una cifra ya escrita no se hereda: se
  vuelve a medir cuando el documento que la cita se revisa.
- **Codificada en:** este registro y la corrección de los cuatro documentos afectados ·
  **estado:** pendiente — *destino: probe `row-count` en `tools/wslice` que verifique las cifras
  declaradas en los `checks:` de un delta contra la base de datos*

### 2026-08-04 — Un test pendiente contaba como cubierto y verde
- **Qué pasó:** el primer slice escribió sus siete tests en rojo usando `pytestmark = pytest.mark.skip`
  a nivel de módulo. `wslice slice coverage` los marcó `covered` en lugar de `pending`, así que el Gate 2
  no distinguía TDD rojo de implementación terminada.
- **Causa raíz:** el escáner detecta lo pendiente por decorador inmediatamente anterior al `def` o por
  `pytest.skip()` en el cuerpo, y `pytestmark` de módulo es una tercera forma idiomática que no contempla.
- **Regla:** en los tests de escenario, el estado pendiente se declara **por test** con
  `@pytest.mark.skip`, nunca con `pytestmark` de módulo, hasta que el escáner entienda las dos formas.
- **Codificada en:** `.claude/skills/slice-propose/SKILL.md` (ejemplo de la Fase 2, ya usaba el decorador
  por test) y este registro · **estado:** pendiente — *destino: que `tools/wslice/coverage.py` reconozca
  `pytestmark` y `pytest.mark.skipif` a nivel de módulo, con su test en `tests/harness/test_coverage.py`*

### 2026-08-04 — El gate de `test-commands` se satisface con una expresión regular
- **Qué pasó:** al portar el harness se replicó el gate que busca comandos de test en `tasks.md`
  mediante regex. Que pase no demuestra que los comandos existan, sean correctos ni se ejecuten.
- **Causa raíz:** el gate mide la presencia de una cadena, no la ejecución.
- **Regla:** el `ok` de `verify gates` no sustituye a la ejecución real de la suite; los Validation
  Gates de cada proposal listan los comandos que hay que ejecutar y el reporte de la Fase 4 debe
  incluir su salida.
- **Codificada en:** `openspec/slice-system.md` §7 (comandos deterministas) + nota de honestidad en
  el proposal del pack de adopción · **estado:** pendiente — *destino: probe en `tools/wslice` que
  ejecute los comandos declarados en lugar de buscarlos*
