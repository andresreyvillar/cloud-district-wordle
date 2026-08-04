"""CLI del harness de slices.

    python3 -m tools.wslice slice list [--json]
    python3 -m tools.wslice slice validate [slug] [--json]
    python3 -m tools.wslice slice coverage <slug> [--json]
    python3 -m tools.wslice verify slice <slug> [--strict] [--json]
    python3 -m tools.wslice verify gates [--slice <slug>] [--change-id <id>] [--json]
    python3 -m tools.wslice metrics [--json]

Exit code 0 = gate en verde; 1 = gate en rojo.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from typing import Any

from .coverage import report_slice_coverage
from .discover import discover_slices, find_slice_by_name
from .gates import run_gates
from .metrics import build_report, collect_runs
from .validate import validate_all_slices
from .verify import verify_slice
from .workspace import Workspace, WorkspaceError, load_workspace

ICON = {
    "pass": "✓",
    "fail": "✗",
    "skip": "○",
    "indeterminate": "◐",
    "covered": "✓",
    "pending": "◐",
    "uncovered": "✗",
}


def _dump(payload: Any) -> None:
    def default(value: Any) -> Any:
        if dataclasses.is_dataclass(value):
            return dataclasses.asdict(value)
        return str(value)

    print(json.dumps(payload, indent=2, ensure_ascii=False, default=default))


def cmd_slice_list(ws: Workspace, args: argparse.Namespace) -> int:
    discovery = discover_slices(ws)
    if args.json:
        _dump(
            {
                "slices": [
                    {
                        **dataclasses.asdict(found.parsed.frontmatter),
                        "file": found.file_path,
                        "scenarios": len(found.parsed.scenarios),
                    }
                    for found in discovery.slices
                ],
                "errors": [{"file": path, "message": message} for path, message in discovery.errors],
            }
        )
        return 1 if discovery.errors else 0

    for found in discovery.slices:
        fm = found.parsed.frontmatter
        print(
            f"• {fm.slice}  [{fm.status}] kind:{fm.kind} "
            f"trigger:{fm.trigger.type}@{fm.trigger.surface} "
            f"specs:[{','.join(fm.specs)}] escenarios:{len(found.parsed.scenarios)}"
        )
    for path, message in discovery.errors:
        print(f"✗ {path}: {message}", file=sys.stderr)
    if not discovery.slices and not discovery.errors:
        print("○ no hay slices todavía (openspec/slices/)")
    return 1 if discovery.errors else 0


def cmd_slice_validate(ws: Workspace, args: argparse.Namespace) -> int:
    report = validate_all_slices(ws, args.name)
    if args.json:
        _dump(dataclasses.asdict(report) | {"ok": report.ok})
        return 0 if report.ok else 1

    for path, message in report.parse_errors:
        print(f"✗ [parse] {path}: {message}", file=sys.stderr)
    for issue in report.issues:
        print(f"{'✗' if issue.level == 'error' else '⚠'} [{issue.slice}] {issue.message}")
    total_errors = len(report.errors) + len(report.parse_errors)
    print(
        f"{'✓' if report.ok else '✗'} {report.slices_checked} slice(s) validados — "
        f"{total_errors} error(es), {len(report.warnings)} warning(s)"
    )
    return 0 if report.ok else 1


def cmd_slice_coverage(ws: Workspace, args: argparse.Namespace) -> int:
    found = find_slice_by_name(ws, args.name)
    if found is None:
        print(f'✗ slice "{args.name}" no encontrado', file=sys.stderr)
        return 1
    report = report_slice_coverage(ws, found)
    if args.json:
        _dump(dataclasses.asdict(report))
        return 1 if report.uncovered else 0

    for scenario in report.scenarios:
        covered_by = (
            ", ".join(
                f"{ref.file_path}{' (pendiente)' if ref.pending else ''}" for ref in scenario.covered_by
            )
            or "—"
        )
        print(f"{ICON[scenario.status]} {scenario.slug} → {covered_by}")
    for warning in report.warnings:
        print(f"⚠ {warning}")
    total = len(report.scenarios)
    covered = total - len(report.uncovered)
    print(f"{'✓' if not report.uncovered else '✗'} {covered}/{total} escenarios con test declarado")
    return 1 if report.uncovered else 0


def cmd_verify_slice(ws: Workspace, args: argparse.Namespace) -> int:
    report = verify_slice(ws, args.name, strict=args.strict)
    if args.json:
        _dump(dataclasses.asdict(report))
        return 1 if report.status == "fail" else 0

    print(f"— validate: {report.validation_errors} error(es), {report.validation_warnings} warning(s)")
    for message in report.validation_messages:
        print(f"  {message}")
    print("— requirements:")
    for requirement in report.requirements:
        print(
            f"  {ICON[requirement.status]} [{requirement.capability}] "
            f"{requirement.requirement} — {requirement.reason}"
        )
    if not report.requirements:
        print("  ○ ninguna capability con spec consolidada todavía")
    print("— cobertura:")
    for scenario in report.coverage:
        print(f"  {ICON[scenario.status]} {scenario.slug}")
    for warning in report.warnings:
        print(f"⚠ {warning}")
    print(f"{ICON[report.status]} verify {report.slice}: {report.status}")
    return 1 if report.status == "fail" else 0


def cmd_verify_gates(ws: Workspace, args: argparse.Namespace) -> int:
    report = run_gates(ws, slice_name=args.slice, change_id=args.change_id)
    if args.json:
        _dump(dataclasses.asdict(report) | {"ok": report.ok})
        return 0 if report.ok else 1

    for gate in report.gates:
        print(f"{ICON[gate.status]} {gate.name}")
        for detail in gate.details:
            print(f"    {detail}")
    print("✓ gates OK" if report.ok else "✗ gates FAIL")
    return 0 if report.ok else 1


def cmd_metrics(ws: Workspace, args: argparse.Namespace) -> int:
    report = build_report(collect_runs(ws))
    if args.json:
        _dump({"changes": report.changes, "totals": report.totals, "parse_errors": report.parse_errors})
        return 1 if report.parse_errors else 0

    if not report.changes:
        print("○ sin runs registrados todavía (openspec/changes/*/runs.yaml)")
        return 0

    totals = report.totals
    actores = "  ".join(f"{actor}:{count}" for actor, count in sorted(totals["por_actor"].items()))
    print(f"runs: {totals['runs']}  ({actores})")
    if totals["runs"]:
        pct = round(totals["first_pass"] / totals["runs"] * 100)
        print(f"first-pass (0 fails, 0 rondas): {totals['first_pass']}/{totals['runs']} ({pct}%)")
    print(f"media rondas de corrección: {totals['avg_rondas']:.2f}")
    fails = sorted(totals["fails_por_gate"].items(), key=lambda item: -item[1])
    print(f"fails por gate: {'  '.join(f'{g}:{n}' for g, n in fails) if fails else '—'}")
    survivors = totals["mutantes_supervivientes"]
    print(
        f"mutación: {totals['mutantes']} mutantes, {survivors} supervivientes"
        f"{'  ⚠' if survivors else ''}"
    )
    print(f"adversarial: {totals['refutaciones_sostenidas']} refutaciones sostenidas")
    if totals["tokens"]:
        print(f"tokens (fábrica): {totals['tokens']}")
    print("— por change:")
    for change in report.changes:
        print(f"  {'📦' if change.archived else '·'} {change.change_id}: {len(change.runs)} run(s)")
        for error in change.errors:
            print(f"    ✗ {error}")
    return 1 if report.parse_errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wslice",
        description="Harness de slices de wordle-stats (protocolo openspec/slice-system.md)",
    )
    parser.add_argument("--version", action="version", version="wslice 0.1.0")
    subparsers = parser.add_subparsers(dest="group", required=True)

    slice_group = subparsers.add_parser("slice", help="operaciones sobre slices")
    slice_sub = slice_group.add_subparsers(dest="command", required=True)

    listing = slice_sub.add_parser("list", help="lista los slices del workspace")
    listing.set_defaults(handler=cmd_slice_list)

    validate = slice_sub.add_parser("validate", help="valida frontmatter, triggers y refs (Gate 1a)")
    validate.add_argument("name", nargs="?", help="slug del slice (por defecto, todos)")
    validate.set_defaults(handler=cmd_slice_validate)

    coverage = slice_sub.add_parser("coverage", help="cobertura escenario↔test vía @scenarios (Gate 2)")
    coverage.add_argument("name")
    coverage.set_defaults(handler=cmd_slice_coverage)

    verify_group = subparsers.add_parser("verify", help="verificación (Fase 4)")
    verify_sub = verify_group.add_subparsers(dest="command", required=True)

    verify_slice_cmd = verify_sub.add_parser("slice", help="validate + Requirements + cobertura (Gate 4a)")
    verify_slice_cmd.add_argument("name")
    verify_slice_cmd.add_argument(
        "--strict", action="store_true", help="pendientes e indeterminates también fallan"
    )
    verify_slice_cmd.set_defaults(handler=cmd_verify_slice)

    gates = verify_sub.add_parser("gates", help="gates mecánicos (Gate 1b)")
    gates.add_argument("--slice", dest="slice", help="slice a comprobar")
    gates.add_argument("--change-id", dest="change_id", help="change pack a comprobar")
    gates.set_defaults(handler=cmd_verify_gates)

    metrics = subparsers.add_parser("metrics", help="agrega los runs.yaml de los change packs (§11)")
    metrics.set_defaults(handler=cmd_metrics)

    for sub in (listing, validate, coverage, verify_slice_cmd, gates, metrics):
        sub.add_argument("--json", action="store_true", help="salida JSON")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        ws = load_workspace()
    except WorkspaceError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1
    return int(args.handler(ws, args))


if __name__ == "__main__":
    raise SystemExit(main())
