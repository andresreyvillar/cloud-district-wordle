"""Gates mecánicos de autoría (Fase 1b / 4 del protocolo).

1. federated-untouched — las specs consolidadas no se tocan fuera del archive.
2. specs-coverage      — cada capability de specs[] tiene delta con >= 1 Requirement.
3. test-commands       — tasks.md declara comandos de test explícitos.
4. checks-probe        — los `checks:` de los deltas se EJECUTAN contra el repositorio.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from .discover import find_slice_by_name
from .probes import ejecutar as ejecutar_probe
from .spec_parser import parse_spec_file
from .workspace import Workspace

#: comandos de test aceptados como "explícitos" en tasks.md (§7)
TEST_COMMAND_RE = re.compile(r"(pytest|playwright\s+test|python3?\s+-m\s+pytest|node\s+--test)")
REQUIREMENT_RE = re.compile(r"^### Requirement:", re.MULTILINE)


@dataclass(frozen=True)
class GateResult:
    name: str
    status: str  # 'pass' | 'fail' | 'skip'
    details: tuple[str, ...]


@dataclass(frozen=True)
class GatesReport:
    gates: tuple[GateResult, ...]

    @property
    def ok(self) -> bool:
        return all(gate.status != "fail" for gate in self.gates)


def _gate_federated_untouched(ws: Workspace) -> GateResult:
    # --untracked-files=all es obligatorio: sin él git colapsa un directorio entero
    # sin trackear en una sola línea ("?? openspec/") y una capability nueva completa
    # esquivaría el gate.
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=ws.root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return GateResult(
            name="federated-untouched",
            status="skip",
            details=("no es un repo git o git no está disponible",),
        )

    prefix = f"{ws.config.specs}/"
    touched = [
        line[3:].strip()
        for line in completed.stdout.splitlines()
        if line[3:].strip().startswith(prefix) and line.strip().endswith(".md")
    ]
    if touched:
        return GateResult(
            name="federated-untouched",
            status="fail",
            details=tuple(
                f"spec consolidada tocada fuera de archive: {path} (§5 federated-untouched)"
                for path in touched
            ),
        )
    return GateResult(
        name="federated-untouched",
        status="pass",
        details=("ninguna spec consolidada tocada",),
    )


def _gate_specs_coverage(ws: Workspace, slice_name: str, change_id: str) -> GateResult:
    found = find_slice_by_name(ws, slice_name)
    if found is None:
        return GateResult("specs-coverage", "fail", (f'slice "{slice_name}" no encontrado',))
    capabilities = found.parsed.frontmatter.specs
    if not capabilities:
        return GateResult("specs-coverage", "fail", ("el slice no declara specs[]",))

    details: list[str] = []
    status = "pass"
    for capability in capabilities:
        delta = ws.abs(f"{ws.config.changes}/{change_id}/specs/{capability}/spec.md")
        if not delta.is_file():
            status = "fail"
            details.append(f'falta el delta de "{capability}": {ws.rel(delta)}')
            continue
        count = len(REQUIREMENT_RE.findall(delta.read_text(encoding="utf-8")))
        if count < 1:
            status = "fail"
            details.append(f'el delta de "{capability}" no declara ningún "### Requirement:"')
        else:
            details.append(f'"{capability}": {count} Requirement(s)')
    return GateResult("specs-coverage", status, tuple(details))


def _gate_test_commands(ws: Workspace, change_id: str) -> GateResult:
    tasks = ws.abs(f"{ws.config.changes}/{change_id}/tasks.md")
    if not tasks.is_file():
        return GateResult("test-commands", "skip", ("sin tasks.md (no hay change pack)",))
    if not TEST_COMMAND_RE.search(tasks.read_text(encoding="utf-8")):
        return GateResult(
            "test-commands",
            "fail",
            ("tasks.md no declara ningún comando de test explícito (§7: comandos deterministas)",),
        )
    return GateResult("test-commands", "pass", ("tasks.md declara comandos de test",))


def _gate_checks_probe(ws: Workspace, slice_name: str, change_id: str) -> GateResult:
    """Ejecuta los `checks:` declarados en los deltas del pack.

    Es el gate que las lecciones del 2026-08-04 pedían: hasta ahora un `checks:` se leía y se daba por
    `indeterminate`, así que declarar una invariante mecánica no comprobaba nada. Los tipos que necesitan la
    base de datos siguen siendo indeterminados **y lo dicen**; los que se deciden con el repositorio ya
    fallan cuando la invariante es falsa.
    """
    found = find_slice_by_name(ws, slice_name)
    if found is None:
        return GateResult("checks-probe", "fail", (f'slice "{slice_name}" no encontrado',))

    detalles: list[str] = []
    rotos = 0
    total = 0
    for capability in found.parsed.frontmatter.specs:
        delta = ws.abs(f"{ws.config.changes}/{change_id}/specs/{capability}/spec.md")
        if not delta.is_file():
            continue
        for requirement in parse_spec_file(delta).requirements:
            for check in requirement.checks:
                total += 1
                veredicto = ejecutar_probe(ws, check, {"tests_root": found.parsed.frontmatter.tests_root})
                if veredicto.estado == "fail":
                    rotos += 1
                    detalles.append(f"✗ [{capability}] {veredicto.tipo}: {veredicto.detalle}")
                elif veredicto.estado == "pass":
                    detalles.append(f"✓ [{capability}] {veredicto.tipo}: {veredicto.detalle}")
                else:
                    detalles.append(f"◐ [{capability}] {veredicto.tipo}: {veredicto.detalle}")

    if not total:
        return GateResult("checks-probe", "skip", ("los deltas no declaran ningún checks:",))
    if rotos:
        return GateResult("checks-probe", "fail", tuple(detalles))
    return GateResult("checks-probe", "pass", tuple(detalles))


def run_gates(ws: Workspace, slice_name: str | None = None, change_id: str | None = None) -> GatesReport:
    gates = [_gate_federated_untouched(ws)]

    if slice_name and change_id:
        gates.append(_gate_specs_coverage(ws, slice_name, change_id))
    else:
        gates.append(GateResult("specs-coverage", "skip", ("sin --slice/--change-id",)))

    if change_id:
        gates.append(_gate_test_commands(ws, change_id))
    else:
        gates.append(GateResult("test-commands", "skip", ("sin --change-id",)))

    if slice_name and change_id:
        gates.append(_gate_checks_probe(ws, slice_name, change_id))
    else:
        gates.append(GateResult("checks-probe", "skip", ("sin --slice/--change-id",)))

    return GatesReport(gates=tuple(gates))
