"""Gate 1a — validación de slices.

Las 10 reglas del validate.ts de pga-cms, con las surfaces de este workspace.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .discover import DiscoveredSlice, discover_slices
from .workspace import Workspace


@dataclass(frozen=True)
class ValidationIssue:
    slice: str
    level: str  # 'error' | 'warning'
    message: str


@dataclass(frozen=True)
class ValidationReport:
    slices_checked: int
    parse_errors: tuple[tuple[str, str], ...]
    issues: tuple[ValidationIssue, ...]

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self.issues if i.level == "error")

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self.issues if i.level == "warning")

    @property
    def ok(self) -> bool:
        return not self.errors and not self.parse_errors


def validate_all_slices(ws: Workspace, only: str | None = None) -> ValidationReport:
    """Reglas:
     1. filename ↔ frontmatter.slice            (error)
     2. slugs de slice duplicados               (error)
     3. slugs de escenario duplicados           (error)
     4. sin escenarios                          (warning)
     5. tests_root inexistente                  (warning)
     6. specs[] sin carpeta de capability       (error)
     7. trigger ui/http fuera de las surfaces de entrada (error, §3)
     8. consumes sin emisor en el workspace     (warning)
     9. wikilinks sin resolver y sin (TBD)      (warning)
    10. emite y consume el MISMO evento         (error, §3)
    """
    discovery = discover_slices(ws)
    issues: list[ValidationIssue] = []

    by_slug: dict[str, list[DiscoveredSlice]] = {}
    for found in discovery.slices:
        by_slug.setdefault(found.name, []).append(found)
    all_slugs = set(by_slug)
    all_emits = [ref for found in discovery.slices for ref in found.parsed.frontmatter.emits]

    targets = [s for s in discovery.slices if only is None or s.name == only]

    for found in targets:
        fm = found.parsed.frontmatter
        name = fm.slice

        def push(level: str, message: str, _name: str = name) -> None:
            issues.append(ValidationIssue(slice=_name, level=level, message=message))

        # 1. filename ↔ slug
        basename = Path(found.file_path).name
        if basename != f"{name}.md":
            push("error", f'el slug del frontmatter "{name}" no coincide con el nombre de archivo "{basename}"')

        # 2. slugs duplicados
        if len(by_slug.get(name, [])) > 1:
            push("error", f'slug de slice duplicado "{name}"')

        # 3. escenarios duplicados
        seen: set[str] = set()
        for scenario in found.parsed.scenarios:
            if scenario.slug in seen:
                push("error", f'slug de escenario duplicado "{scenario.slug}"')
            seen.add(scenario.slug)

        # 4. sin escenarios
        if not found.parsed.scenarios:
            push("warning", 'no declara escenarios bajo "## Comportamiento observable"')

        # 5. tests_root
        if not ws.abs(fm.tests_root).exists():
            push("warning", f'tests_root "{fm.tests_root}" no existe todavía')

        # 6. specs[] → carpeta de capability
        for capability in fm.specs:
            if not ws.abs(f"{ws.config.specs}/{capability}").is_dir():
                push(
                    "error",
                    f'specs[] referencia la capability desconocida "{capability}" '
                    f"(no existe {ws.config.specs}/{capability}/)",
                )
        if not fm.specs:
            push("error", "specs[] está vacío — todo slice cruza al menos una capability")

        # 7. trigger §3
        if fm.trigger.type in ("ui", "http") and ws.config.apps:
            if fm.trigger.surface not in ws.config.apps:
                push(
                    "error",
                    f'trigger {fm.trigger.type} sobre surface "{fm.trigger.surface}" — solo surfaces '
                    f"de entrada ({', '.join(ws.config.apps)}); los módulos internos nunca son entry points (§3)",
                )

        # 8. consumes sin emisor
        for consumed in fm.consumes:
            if not any(consumed.matches_emitter(emitted) for emitted in all_emits):
                push(
                    "warning",
                    f'consume "{consumed.signature()}" pero ningún slice del workspace emite una firma compatible',
                )

        # 9. wikilinks
        for link in found.parsed.wikilinks:
            if link.slug not in all_slugs and not link.tbd:
                push("warning", f"wikilink [[{link.slug}]] sin resolver (no existe y no está marcado (TBD))")

        # 10. mismo evento en emits y consumes
        for emitted in fm.emits:
            for consumed in fm.consumes:
                if emitted.event == consumed.event:
                    push(
                        "error",
                        f'emite y consume el mismo evento "{emitted.event}" — el evento es un boundary: '
                        "partir en action + reaction (§3)",
                    )

    parse_errors = (
        discovery.errors
        if only is None
        else tuple(e for e in discovery.errors if only in e[0])
    )
    return ValidationReport(
        slices_checked=len(targets),
        parse_errors=parse_errors,
        issues=tuple(issues),
    )
