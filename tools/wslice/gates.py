"""Gates mecánicos de autoría (Fase 1b / 4 del protocolo), sobre las specs vivas (ADR 0009).

1. specs-coverage — cada capability de specs[] tiene su spec viva con >= 1 Requirement.
2. checks-probe   — los `checks:` de esas specs se EJECUTAN contra el repositorio.
3. test-commands  — si el cambio trae un change pack (opcional), su tasks.md declara comandos de test.

Antes existía `federated-untouched`, que prohibía tocar `openspec/specs/` fuera del archive. Con specs vivas
editarlas en la rama es lo normal, así que el gate desapareció con los deltas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .discover import find_slice_by_name
from .probes import ejecutar as ejecutar_probe
from .spec_parser import parse_spec_file
from .workspace import Workspace

#: comandos de test aceptados como "explícitos" en tasks.md (§7)
TEST_COMMAND_RE = re.compile(r"(pytest|playwright\s+test|python3?\s+-m\s+pytest|node\s+--test)")


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


def _spec_viva(ws: Workspace, capability: str):
    return ws.abs(f"{ws.config.specs}/{capability}/spec.md")


def _gate_specs_coverage(ws: Workspace, slice_name: str) -> GateResult:
    found = find_slice_by_name(ws, slice_name)
    if found is None:
        return GateResult("specs-coverage", "fail", (f'slice "{slice_name}" no encontrado',))
    capabilities = found.parsed.frontmatter.specs
    if not capabilities:
        return GateResult("specs-coverage", "fail", ("el slice no declara specs[]",))

    details: list[str] = []
    status = "pass"
    for capability in capabilities:
        spec = _spec_viva(ws, capability)
        if not spec.is_file():
            status = "fail"
            details.append(f'"{capability}" no tiene spec viva: {ws.rel(spec)}')
            continue
        count = len(parse_spec_file(spec).requirements)
        if count == 0:
            status = "fail"
            details.append(f'la spec de "{capability}" no declara ningún "## Requirement:"')
            continue
        details.append(f'"{capability}": {count} Requirement(s)')
    return GateResult("specs-coverage", status, tuple(details))


def _gate_test_commands(ws: Workspace, change_id: str) -> GateResult:
    tasks = ws.abs(f"{ws.config.changes}/{change_id}/tasks.md")
    if not tasks.is_file():
        return GateResult("test-commands", "skip", ("sin tasks.md (el change pack es opcional)",))
    if not TEST_COMMAND_RE.search(tasks.read_text(encoding="utf-8")):
        return GateResult(
            "test-commands",
            "fail",
            ("tasks.md no declara ningún comando de test explícito (§7: comandos deterministas)",),
        )
    return GateResult("test-commands", "pass", ("tasks.md declara comandos de test",))


def _gate_checks_probe(ws: Workspace, slice_name: str) -> GateResult:
    """Ejecuta los `checks:` declarados en las specs vivas de las capabilities del slice.

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
        spec = _spec_viva(ws, capability)
        if not spec.is_file():
            continue
        for requirement in parse_spec_file(spec).requirements:
            for check in requirement.checks:
                total += 1
                # Lo que depende de los tests (el doble de un índice) se mira en los que demuestran ESTE
                # Requirement: la spec viva es compartida, y los tests de otro slice que cruce el dominio no
                # tienen por qué escribir en la tabla.
                raiz = (
                    str(Path(requirement.verified_by[0].split("#")[0]).parent) + "/"
                    if requirement.verified_by
                    else found.parsed.frontmatter.tests_root
                )
                veredicto = ejecutar_probe(ws, check, {"tests_root": raiz})
                if veredicto.estado == "fail":
                    rotos += 1
                    detalles.append(f"✗ [{capability}] {veredicto.tipo}: {veredicto.detalle}")
                elif veredicto.estado == "pass":
                    detalles.append(f"✓ [{capability}] {veredicto.tipo}: {veredicto.detalle}")
                else:
                    detalles.append(f"◐ [{capability}] {veredicto.tipo}: {veredicto.detalle}")

    if not total:
        return GateResult("checks-probe", "skip", ("las specs del slice no declaran ningún checks:",))
    if rotos:
        return GateResult("checks-probe", "fail", tuple(detalles))
    return GateResult("checks-probe", "pass", tuple(detalles))


def run_gates(ws: Workspace, slice_name: str | None = None, change_id: str | None = None) -> GatesReport:
    gates: list[GateResult] = []

    if slice_name:
        gates.append(_gate_specs_coverage(ws, slice_name))
        gates.append(_gate_checks_probe(ws, slice_name))
    else:
        gates.append(GateResult("specs-coverage", "skip", ("sin --slice",)))
        gates.append(GateResult("checks-probe", "skip", ("sin --slice",)))

    if change_id:
        gates.append(_gate_test_commands(ws, change_id))
    else:
        gates.append(GateResult("test-commands", "skip", ("sin change pack (opcional desde ADR 0009)",)))

    return GatesReport(gates=tuple(gates))
