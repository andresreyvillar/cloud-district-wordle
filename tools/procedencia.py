"""De qué versión del repositorio viene un cálculo. **Es el borde: aquí sí se lee git.**

Slices: `temporada-mensual` y `clasificacion-de-temporada` (la instantánea que ambos materializan).

Existe por un incidente concreto. El 2026-08-13 la instantánea de agosto apareció con el álbum calculado con
una regla que se había cambiado el día anterior: alguien ejecutó `local_stack.py` desde una copia del
repositorio por detrás de `main` y **le revirtió el cálculo al grupo en silencio**. Los tres cron de esa
mañana habían corrido con el código correcto; averiguar quién había escrito ese payload costó media docena
de consultas y comparar a mano los SHA de los workflows.

Dos funciones, para las dos mitades del problema:

- `version()` — el commit con el que se calcula, para guardarlo **dentro** de la instantánea. Así la
  procedencia viaja con el dato en lugar de haber que deducirla.
- `por_detras_de_origen()` — si la copia local se ha quedado atrás, para avisar **antes** de escribir.

Nada de esto aborta nada por su cuenta: informar es el trabajo de este módulo, decidir es de quien lo llama.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

#: Segundos que se le dan a git. Corto a propósito: esto es una comprobación de cortesía y no puede colgar el
#: arranque de una herramienta de desarrollo si el remoto no responde.
ESPERA = 5


def _git(*argumentos: str, espera: int = ESPERA) -> str | None:
    """La salida de un git, o `None` si falla por cualquier motivo.

    Devolver `None` en lugar de propagar es deliberado: esto se ejecuta también en CI, donde el checkout es
    superficial y puede no haber remoto configurado. Un fallo aquí no puede impedir materializar.
    """
    try:
        hecho = subprocess.run(
            ("git", "-C", str(RAIZ), *argumentos),
            capture_output=True,
            text=True,
            timeout=espera,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return hecho.stdout.strip() if hecho.returncode == 0 else None


def version() -> str:
    """El commit con el que se está calculando, con un sufijo si el árbol tiene cambios sin commitear.

    El sufijo importa tanto como el SHA: `88cc1b7+sucio` avisa de que el payload no corresponde a ningún
    commit del repositorio, que es exactamente el caso de quien está probando algo a medias.
    """
    sha = _git("rev-parse", "--short", "HEAD")
    if not sha:
        return ""
    return f"{sha}+sucio" if _git("status", "--porcelain") else sha


def por_detras_de_origen(rama: str = "origin/main") -> tuple[bool, str]:
    """Si la copia local **no contiene** lo que hay en `rama`, y cuántos commits le faltan.

    Se hace `fetch` para no medir contra una referencia rancia: sin él, una copia que lleva días sin traer
    nada se declararía al día. Si el fetch no se puede hacer —sin red, sin remoto— se mide con lo que haya y
    se dice, porque un aviso aproximado sigue siendo mejor que ninguno.
    """
    fresco = _git("fetch", "--quiet", "origin", espera=15) is not None

    detras = _git("rev-list", "--count", f"HEAD..{rama}")
    if detras is None:
        return False, "no se ha podido comparar con el remoto"
    cuantos = int(detras or 0)
    if not cuantos:
        return False, "al día con " + rama if fresco else "al día con la copia local de " + rama
    aviso = f"faltan {cuantos} commit{'s' if cuantos > 1 else ''} de {rama}"
    return True, aviso if fresco else f"{aviso} (sin poder comprobar el remoto)"
