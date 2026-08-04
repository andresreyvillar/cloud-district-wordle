"""§11 — Observabilidad: agrega los runs.yaml de los change packs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import yaml

from .workspace import Workspace

FASES = ("propose", "tdd", "implement", "verify")
ACTORES = ("humano", "fabrica")
GATE_STATUSES = ("pass", "fail", "skip")


@dataclass(frozen=True)
class RunEntry:
    run: str
    fase: str
    actor: str
    gates: dict[str, str] = field(default_factory=dict)
    rondas_correccion: int = 0
    modelo: str | None = None
    slice: str | None = None
    mutantes: int = 0
    mutantes_supervivientes: int = 0
    adversarial_intentos: int = 0
    refutaciones_sostenidas: int = 0
    tokens: int = 0
    duracion_min: float | None = None
    notas: str | None = None

    @property
    def first_pass(self) -> bool:
        return self.rondas_correccion == 0 and "fail" not in self.gates.values()


@dataclass(frozen=True)
class ChangeRuns:
    change_id: str
    archived: bool
    file_path: str
    runs: tuple[RunEntry, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True)
class MetricsReport:
    changes: tuple[ChangeRuns, ...]
    parse_errors: int

    @property
    def all_runs(self) -> list[RunEntry]:
        return [run for change in self.changes for run in change.runs]

    @property
    def totals(self) -> dict:
        runs = self.all_runs
        fails: dict[str, int] = {}
        por_actor: dict[str, int] = {}
        for run in runs:
            por_actor[run.actor] = por_actor.get(run.actor, 0) + 1
            for gate, status in run.gates.items():
                if status == "fail":
                    fails[gate] = fails.get(gate, 0) + 1
        return {
            "runs": len(runs),
            "first_pass": sum(1 for run in runs if run.first_pass),
            "avg_rondas": (sum(run.rondas_correccion for run in runs) / len(runs)) if runs else 0.0,
            "fails_por_gate": fails,
            "mutantes": sum(run.mutantes for run in runs),
            "mutantes_supervivientes": sum(run.mutantes_supervivientes for run in runs),
            "refutaciones_sostenidas": sum(run.refutaciones_sostenidas for run in runs),
            "tokens": sum(run.tokens for run in runs),
            "por_actor": por_actor,
        }


def _parse_entry(raw: object, index: int) -> tuple[RunEntry | None, str | None]:
    if not isinstance(raw, dict):
        return None, f"entrada [{index}]: debe ser un mapa"

    errors: list[str] = []
    run = raw.get("run")
    # YAML parsea los timestamps sin comillas como datetime: se normalizan a string
    if isinstance(run, (datetime, date)):
        run = run.isoformat()
    if not isinstance(run, str) or not run.strip():
        errors.append("'run' es obligatorio (timestamp ISO, preferiblemente entrecomillado)")

    fase = raw.get("fase")
    if fase not in FASES:
        errors.append(f"'fase' debe ser una de {', '.join(FASES)}")
    actor = raw.get("actor")
    if actor not in ACTORES:
        errors.append(f"'actor' debe ser uno de {', '.join(ACTORES)}")

    gates = raw.get("gates") or {}
    if not isinstance(gates, dict):
        errors.append("'gates' debe ser un mapa gate→pass|fail|skip")
        gates = {}
    else:
        invalid = {k: v for k, v in gates.items() if v not in GATE_STATUSES}
        if invalid:
            errors.append(f"gates con valor inválido: {', '.join(sorted(invalid))}")

    rondas = raw.get("rondas_correccion", 0)
    if not isinstance(rondas, int) or isinstance(rondas, bool) or rondas < 0:
        errors.append("'rondas_correccion' debe ser un entero >= 0")
        rondas = 0

    mutacion = raw.get("mutacion") or {}
    adversarial = raw.get("adversarial") or {}
    if not isinstance(mutacion, dict) or not isinstance(adversarial, dict):
        errors.append("'mutacion' y 'adversarial' deben ser mapas")
        mutacion, adversarial = {}, {}

    if errors:
        return None, f"entrada [{index}]: " + "; ".join(errors)

    return (
        RunEntry(
            run=str(run),
            fase=str(fase),
            actor=str(actor),
            gates={str(k): str(v) for k, v in gates.items()},
            rondas_correccion=rondas,
            modelo=raw.get("modelo"),
            slice=raw.get("slice"),
            mutantes=int(mutacion.get("mutantes", 0) or 0),
            mutantes_supervivientes=int(mutacion.get("supervivientes", 0) or 0),
            adversarial_intentos=int(adversarial.get("intentos", 0) or 0),
            refutaciones_sostenidas=int(adversarial.get("refutaciones_sostenidas", 0) or 0),
            tokens=int(raw.get("tokens", 0) or 0),
            duracion_min=raw.get("duracion_min"),
            notas=raw.get("notas"),
        ),
        None,
    )


def _read_runs_file(path: Path) -> tuple[list[RunEntry], list[str]]:
    runs: list[RunEntry] = []
    errors: list[str] = []
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [], [f"{path.name}: ilegible — {exc}"]
    if raw is None:
        return [], []
    if not isinstance(raw, list):
        return [], [f"{path.name}: runs.yaml debe ser una lista de entradas"]
    for index, item in enumerate(raw):
        entry, error = _parse_entry(item, index)
        if entry is not None:
            runs.append(entry)
        if error is not None:
            errors.append(f"{path.name}: {error}")
    return runs, errors


def collect_runs(ws: Workspace) -> list[ChangeRuns]:
    changes_dir = ws.abs(ws.config.changes)
    collected: list[ChangeRuns] = []
    if not changes_dir.is_dir():
        return collected

    candidates: list[tuple[Path, bool]] = []
    for entry in sorted(changes_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name == "archive":
            candidates.extend((sub, True) for sub in sorted(entry.iterdir()) if sub.is_dir())
        else:
            candidates.append((entry, False))

    for directory, archived in candidates:
        runs_file = directory / "runs.yaml"
        if not runs_file.is_file():
            continue
        runs, errors = _read_runs_file(runs_file)
        collected.append(
            ChangeRuns(
                change_id=directory.name,
                archived=archived,
                file_path=ws.rel(runs_file),
                runs=tuple(runs),
                errors=tuple(errors),
            )
        )
    return collected


def build_report(changes: list[ChangeRuns]) -> MetricsReport:
    return MetricsReport(
        changes=tuple(changes),
        parse_errors=sum(len(change.errors) for change in changes),
    )
