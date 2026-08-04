"""Gate 4a — pipeline de verify de un slice.

1. validate (los errores bloquean)
2. Requirements de cada capability de specs[]:
   - checks:      → v1 sin probes implementados → `indeterminate`
   - verified-by: → los archivos referenciados DEBEN existir → `pass`
   - política indeterminate (§4): sin verified-by, el Requirement NO pasa
3. cobertura escenario↔test: uncovered = FAIL · pending (skip/fixme) = WARN
   (el verde real lo exige la ejecución de la suite, no este harness)
"""

from __future__ import annotations

from dataclasses import dataclass

from .coverage import ScenarioCoverage, report_slice_coverage
from .discover import find_slice_by_name
from .spec_parser import parse_spec_file
from .validate import validate_all_slices
from .workspace import Workspace


@dataclass(frozen=True)
class RequirementResult:
    capability: str
    requirement: str
    status: str  # 'pass' | 'fail' | 'indeterminate' | 'skipped'
    reason: str


@dataclass(frozen=True)
class VerifySliceReport:
    slice: str
    status: str  # 'pass' | 'fail' | 'indeterminate'
    validation_errors: int
    validation_warnings: int
    validation_messages: tuple[str, ...]
    requirements: tuple[RequirementResult, ...]
    coverage: tuple[ScenarioCoverage, ...]
    warnings: tuple[str, ...]


def verify_slice(ws: Workspace, name: str, strict: bool = False) -> VerifySliceReport:
    found = find_slice_by_name(ws, name)
    if found is None:
        return VerifySliceReport(
            slice=name,
            status="fail",
            validation_errors=1,
            validation_warnings=0,
            validation_messages=(f'slice "{name}" no encontrado',),
            requirements=(),
            coverage=(),
            warnings=(),
        )

    # 1. validate
    validation = validate_all_slices(ws, name)
    messages = [f"[error] {message}" for _, message in validation.parse_errors]
    messages += [
        f"[{'error' if issue.level == 'error' else 'warn'}] {issue.message}"
        for issue in validation.issues
    ]
    validation_errors = len(validation.errors) + len(validation.parse_errors)

    # 2. Requirements por capability
    requirements: list[RequirementResult] = []
    warnings: list[str] = []
    for capability in found.parsed.frontmatter.specs:
        spec_path = ws.abs(f"{ws.config.specs}/{capability}/spec.md")
        if not spec_path.is_file():
            requirements.append(
                RequirementResult(
                    capability=capability,
                    requirement="(sin spec consolidada)",
                    status="indeterminate",
                    reason=(
                        f"no existe {ws.config.specs}/{capability}/spec.md todavía "
                        "(se consolida en el archive)"
                    ),
                )
            )
            continue
        spec = parse_spec_file(spec_path)
        if not spec.requirements:
            requirements.append(
                RequirementResult(
                    capability=capability,
                    requirement="(spec vacía)",
                    status="indeterminate",
                    reason="la spec no declara Requirements",
                )
            )
            continue
        for requirement in spec.requirements:
            existing = [ref for ref in requirement.verified_by if ws.abs(ref.split("#")[0]).exists()]
            missing = [ref for ref in requirement.verified_by if not ws.abs(ref.split("#")[0]).exists()]
            if missing:
                requirements.append(
                    RequirementResult(
                        capability, requirement.title, "fail", f"verified-by roto: {', '.join(missing)}"
                    )
                )
            elif existing:
                requirements.append(
                    RequirementResult(
                        capability, requirement.title, "pass", f"verified-by: {', '.join(existing)}"
                    )
                )
            elif requirement.checks:
                kinds = ", ".join(str(check.get("type", "?")) for check in requirement.checks)
                requirements.append(
                    RequirementResult(
                        capability,
                        requirement.title,
                        "indeterminate",
                        f"checks ({kinds}) sin probe implementado y sin verified-by — añade verified-by (§4)",
                    )
                )
            else:
                requirements.append(
                    RequirementResult(
                        capability,
                        requirement.title,
                        "fail",
                        "sin checks ni verified-by (§4: al menos uno es obligatorio)",
                    )
                )

    # 3. cobertura
    coverage = report_slice_coverage(ws, found)
    warnings.extend(coverage.warnings)
    if coverage.pending:
        pending_slugs = ", ".join(s.slug for s in coverage.pending)
        warnings.append(
            f"{len(coverage.pending)} escenario(s) con cobertura pendiente (skip/fixme) — válido en "
            f"Fase 2 (TDD rojo); la Fase 4 exige verde: {pending_slugs}"
        )

    requirement_fails = [r for r in requirements if r.status == "fail"]
    requirement_indeterminate = [r for r in requirements if r.status == "indeterminate"]
    failed = (
        validation_errors > 0
        or bool(requirement_fails)
        or bool(coverage.uncovered)
        or (strict and (bool(coverage.pending) or bool(requirement_indeterminate)))
    )

    if failed:
        status = "fail"
    elif requirement_indeterminate or coverage.pending:
        status = "indeterminate"
    else:
        status = "pass"

    return VerifySliceReport(
        slice=name,
        status=status,
        validation_errors=validation_errors,
        validation_warnings=len(validation.warnings),
        validation_messages=tuple(messages),
        requirements=tuple(requirements),
        coverage=coverage.scenarios,
        warnings=tuple(warnings),
    )
