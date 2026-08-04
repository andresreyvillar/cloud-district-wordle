"""Descubrimiento de slices en el workspace."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .slice_parser import SliceParseError, parse_slice_file
from .slice_schema import ParsedSlice
from .workspace import Workspace


@dataclass(frozen=True)
class DiscoveredSlice:
    file_path: str  # relativo a la raíz del workspace
    parsed: ParsedSlice

    @property
    def name(self) -> str:
        return self.parsed.frontmatter.slice


@dataclass(frozen=True)
class DiscoveryResult:
    slices: tuple[DiscoveredSlice, ...]
    errors: tuple[tuple[str, str], ...]  # (file_path, mensaje)


def _walk_slice_files(directory: Path) -> list[Path]:
    """Archivos .md del árbol, saltando plantillas (`_*.md`) y directorios `*.pending`."""
    if not directory.is_dir():
        return []
    found: list[Path] = []
    for entry in sorted(directory.iterdir()):
        if entry.is_dir():
            if entry.name.endswith(".pending"):
                continue
            found.extend(_walk_slice_files(entry))
        elif entry.is_file() and entry.suffix == ".md" and not entry.name.startswith("_"):
            found.append(entry)
    return found


def discover_slices(ws: Workspace) -> DiscoveryResult:
    slices: list[DiscoveredSlice] = []
    errors: list[tuple[str, str]] = []
    for file in _walk_slice_files(ws.abs(ws.config.slices)):
        rel = ws.rel(file)
        try:
            slices.append(DiscoveredSlice(file_path=rel, parsed=parse_slice_file(file)))
        except SliceParseError as exc:
            errors.append((rel, str(exc).split(": ", 1)[-1]))
        except OSError as exc:
            errors.append((rel, f"no se puede leer — {exc}"))
    return DiscoveryResult(slices=tuple(slices), errors=tuple(errors))


def find_slice_by_name(ws: Workspace, name: str) -> DiscoveredSlice | None:
    for candidate in discover_slices(ws).slices:
        if candidate.name == name:
            return candidate
    return None
