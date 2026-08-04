"""Gate 2 / 4a — cobertura declarativa escenario ↔ test.

Escáner multi-lenguaje de anotaciones. Convención por lenguaje:

Python — comentario justo antes del test, o docstring del test:

    # @scenarios sin-fechas-no-filtra, duracion-valida-filtra
    def test_filtra_por_duracion(): ...

    def test_filtra_por_duracion():
        \"\"\"@scenarios duracion-valida-filtra\"\"\"

JavaScript / TypeScript — bloque JSDoc justo antes de la llamada al test:

    /** @scenarios puebla-selector */
    test('puebla el selector', ...)

`@slice <nombre>` es opcional: si no está, el slice se infiere de la ruta
(`<e2e_tests>/<slug>/...`). Un test sin `@scenarios` no aporta cobertura.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .discover import DiscoveredSlice
from .workspace import Workspace

PY_SUFFIXES = (".py",)
JS_SUFFIXES = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")

ANNOTATION_RE = re.compile(r"@(slice|scenarios)\s+([^\r\n*]*)")
JS_DOC_BLOCK_RE = re.compile(r"/\*\*(.*?)\*/", re.DOTALL)
JS_TEST_CALL_RE = re.compile(r"^\s*(?:test|it)(?:\.(fixme|skip|only|todo|each|concurrent))?\s*(?:\(|\.each)")
PY_TEST_DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+(test_\w+)\s*\(")
PY_DOCSTRING_ANNOTATION_RE = re.compile(r"@(?:slice|scenarios)\s")
PY_PENDING_MARK_RE = re.compile(r"@pytest\.mark\.(skip|skipif|xfail|todo)\b")
PY_PENDING_CALL_RE = re.compile(r"\bpytest\.(skip|xfail)\s*\(")

#: distancia máxima (en líneas) entre un `def test_` y su docstring de anotación
DOCSTRING_LOOKAHEAD = 3
#: líneas del cuerpo que se inspeccionan buscando un skip explícito
PENDING_BODY_LOOKAHEAD = 5


@dataclass(frozen=True)
class TestRef:
    file_path: str  # relativo a la raíz del workspace
    slice: str | None
    scenarios: tuple[str, ...]
    pending: bool  # TDD rojo declarado (fixme/skip/xfail)
    inferred_slice_from_path: bool


@dataclass(frozen=True)
class ScenarioCoverage:
    slug: str
    title: str | None
    covered_by: tuple[TestRef, ...]
    status: str  # 'covered' | 'pending' | 'uncovered'


@dataclass(frozen=True)
class SliceCoverageReport:
    slice: str
    scenarios: tuple[ScenarioCoverage, ...]
    warnings: tuple[str, ...]

    @property
    def uncovered(self) -> tuple[ScenarioCoverage, ...]:
        return tuple(s for s in self.scenarios if s.status == "uncovered")

    @property
    def pending(self) -> tuple[ScenarioCoverage, ...]:
        return tuple(s for s in self.scenarios if s.status == "pending")


def _parse_annotations(text: str) -> tuple[str | None, list[str]]:
    explicit_slice: str | None = None
    scenarios: list[str] = []
    for match in ANNOTATION_RE.finditer(text):
        if match.group(1) == "slice":
            explicit_slice = match.group(2).strip() or None
        else:
            scenarios.extend(part.strip() for part in match.group(2).split(",") if part.strip())
    return explicit_slice, scenarios


def _infer_slice_from_path(ws: Workspace, rel_path: str) -> str | None:
    root = ws.config.e2e_tests.rstrip("/") + "/"
    if not rel_path.startswith(root):
        return None
    remainder = rel_path[len(root) :].split("/")
    return remainder[0] if remainder and remainder[0] else None


def _scan_python(lines: list[str]) -> list[tuple[str | None, list[str], bool]]:
    """Devuelve (slice, scenarios, pending) por cada test anotado del archivo."""
    tests: list[tuple[int, bool]] = []  # (índice de línea del def, pending)
    for index, line in enumerate(lines):
        if not PY_TEST_DEF_RE.match(line):
            continue
        decorators: list[str] = []
        cursor = index - 1
        while cursor >= 0 and (lines[cursor].strip().startswith("@") or not lines[cursor].strip()):
            if lines[cursor].strip().startswith("@"):
                decorators.append(lines[cursor])
            cursor -= 1
        body = lines[index + 1 : index + 1 + PENDING_BODY_LOOKAHEAD]
        pending = any(PY_PENDING_MARK_RE.search(d) for d in decorators) or any(
            PY_PENDING_CALL_RE.search(b) for b in body
        )
        tests.append((index, pending))

    if not tests:
        return []

    found: list[tuple[str | None, list[str], bool]] = []
    for annotation_line, text in _python_annotation_blocks(lines):
        owner = _owner_test(annotation_line, tests)
        if owner is None:
            continue
        explicit_slice, scenarios = _parse_annotations(text)
        if not scenarios and explicit_slice is None:
            continue
        found.append((explicit_slice, scenarios, owner[1]))
    return found


def _python_annotation_blocks(lines: list[str]) -> list[tuple[int, str]]:
    """Bloques de texto que contienen anotaciones: comentarios `#` contiguos y
    docstrings triple-quote. Devuelve (línea inicial, texto del bloque)."""
    blocks: list[tuple[int, str]] = []
    comment_start: int | None = None
    comment_buffer: list[str] = []
    in_docstring = False
    docstring_delimiter = ""
    docstring_start = 0
    docstring_buffer: list[str] = []

    for index, line in enumerate(lines):
        stripped = line.strip()

        if in_docstring:
            docstring_buffer.append(line)
            if docstring_delimiter in stripped:
                blocks.append((docstring_start, "\n".join(docstring_buffer)))
                in_docstring = False
                docstring_buffer = []
            continue

        for delimiter in ('"""', "'''"):
            if stripped.startswith(delimiter) or stripped.startswith(f"r{delimiter}"):
                content = stripped.split(delimiter, 1)[1]
                if delimiter in content:  # docstring de una sola línea
                    blocks.append((index, content.split(delimiter)[0]))
                else:
                    in_docstring = True
                    docstring_delimiter = delimiter
                    docstring_start = index
                    docstring_buffer = [content]
                break
        else:
            if stripped.startswith("#"):
                if comment_start is None:
                    comment_start = index
                comment_buffer.append(stripped.lstrip("#"))
                continue
            if comment_buffer and comment_start is not None:
                blocks.append((comment_start, "\n".join(comment_buffer)))
            comment_start = None
            comment_buffer = []

    if comment_buffer and comment_start is not None:
        blocks.append((comment_start, "\n".join(comment_buffer)))
    return blocks


def _owner_test(annotation_line: int, tests: list[tuple[int, bool]]) -> tuple[int, bool] | None:
    """La anotación pertenece al `def test_` inmediatamente anterior si está dentro de
    su docstring (a menos de DOCSTRING_LOOKAHEAD líneas); si no, al siguiente."""
    previous = [t for t in tests if t[0] < annotation_line]
    if previous:
        candidate = previous[-1]
        if annotation_line - candidate[0] <= DOCSTRING_LOOKAHEAD:
            return candidate
    following = [t for t in tests if t[0] > annotation_line]
    return following[0] if following else None


def _scan_javascript(content: str) -> list[tuple[str | None, list[str], bool]]:
    found: list[tuple[str | None, list[str], bool]] = []
    for match in JS_DOC_BLOCK_RE.finditer(content):
        after = content[match.end() :]
        next_line = next((line for line in after.splitlines() if line.strip()), "")
        call = JS_TEST_CALL_RE.match(next_line)
        if not call:
            continue
        explicit_slice, scenarios = _parse_annotations(match.group(1))
        if not scenarios and explicit_slice is None:
            continue
        found.append((explicit_slice, scenarios, call.group(1) in ("fixme", "skip", "todo")))
    return found


def scan_test_file(ws: Workspace, path: Path) -> list[TestRef]:
    rel = ws.rel(path)
    content = path.read_text(encoding="utf-8")
    path_slice = _infer_slice_from_path(ws, rel)

    if path.suffix in PY_SUFFIXES:
        raw = _scan_python(content.splitlines())
    elif path.suffix in JS_SUFFIXES:
        raw = _scan_javascript(content)
    else:
        return []

    refs: list[TestRef] = []
    for explicit_slice, scenarios, pending in raw:
        slice_name = explicit_slice or path_slice
        if slice_name is None:
            continue
        refs.append(
            TestRef(
                file_path=rel,
                slice=slice_name,
                scenarios=tuple(scenarios),
                pending=pending,
                inferred_slice_from_path=explicit_slice is None,
            )
        )
    return refs


def _is_test_file(path: Path) -> bool:
    if path.suffix in PY_SUFFIXES:
        return path.name.startswith("test_") or path.name.endswith("_test.py")
    if path.suffix in JS_SUFFIXES:
        return bool(re.search(r"\.(spec|test)\.[jt]sx?$", path.name))
    return False


def _walk_test_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    found: list[Path] = []
    for entry in sorted(directory.iterdir()):
        if entry.is_dir():
            if entry.name in ("__pycache__", "node_modules", ".pytest_cache"):
                continue
            found.extend(_walk_test_files(entry))
        elif entry.is_file() and _is_test_file(entry):
            found.append(entry)
    return found


def scan_all_tests(ws: Workspace) -> list[TestRef]:
    roots = [ws.abs(ws.config.e2e_tests), *[ws.abs(r) for r in ws.config.test_roots]]
    files: dict[str, Path] = {}
    for root in roots:
        for file in _walk_test_files(root):
            files[str(file)] = file
    refs: list[TestRef] = []
    for file in files.values():
        refs.extend(scan_test_file(ws, file))
    return refs


def report_slice_coverage(ws: Workspace, slice_: DiscoveredSlice) -> SliceCoverageReport:
    name = slice_.name
    refs = [ref for ref in scan_all_tests(ws) if ref.slice == name]
    warnings: list[str] = []

    for ref in refs:
        if not ref.scenarios:
            warnings.append(
                f"{ref.file_path}: test asociado al slice pero sin @scenarios — no aporta cobertura"
            )

    scenarios: list[ScenarioCoverage] = []
    for scenario in slice_.parsed.scenarios:
        covered_by = tuple(ref for ref in refs if scenario.slug in ref.scenarios)
        if not covered_by:
            status = "uncovered"
        elif all(ref.pending for ref in covered_by):
            status = "pending"
        else:
            status = "covered"
        scenarios.append(
            ScenarioCoverage(
                slug=scenario.slug,
                title=scenario.title,
                covered_by=covered_by,
                status=status,
            )
        )

    valid = {s.slug for s in slice_.parsed.scenarios}
    for ref in refs:
        for declared in ref.scenarios:
            if declared not in valid:
                warnings.append(
                    f'{ref.file_path}: @scenarios "{declared}" no existe en el slice "{name}"'
                )

    return SliceCoverageReport(slice=name, scenarios=tuple(scenarios), warnings=tuple(warnings))
