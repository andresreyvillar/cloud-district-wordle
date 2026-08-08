"""Carga del manifest del workspace (openspec.workspace.yaml)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

MANIFEST = "openspec.workspace.yaml"

DEFAULTS = {
    "slices": "openspec/slices",
    "specs": "openspec/specs",
    "changes": "openspec/changes",
    "e2e_tests": "tests/slices",
}


class WorkspaceError(Exception):
    """El manifest no existe o es inválido."""


@dataclass(frozen=True)
class WorkspaceConfig:
    slices: str = DEFAULTS["slices"]
    specs: str = DEFAULTS["specs"]
    changes: str = DEFAULTS["changes"]
    e2e_tests: str = DEFAULTS["e2e_tests"]
    apps: tuple[str, ...] = ()
    test_roots: tuple[str, ...] = field(default=("tests",))


@dataclass(frozen=True)
class Workspace:
    root: Path
    config: WorkspaceConfig

    def abs(self, relative: str) -> Path:
        return (self.root / relative).resolve()

    def rel(self, path: Path) -> str:
        return str(Path(path).resolve().relative_to(self.root))


def _parse_config(raw: object, manifest_path: Path) -> WorkspaceConfig:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise WorkspaceError(f"{manifest_path}: el manifest debe ser un mapa YAML")

    def as_str(key: str) -> str:
        value = raw.get(key, DEFAULTS.get(key))
        if not isinstance(value, str) or not value.strip():
            raise WorkspaceError(f"{manifest_path}: '{key}' debe ser una ruta no vacía")
        return value.strip()

    def as_str_tuple(key: str, default: tuple[str, ...]) -> tuple[str, ...]:
        value = raw.get(key)
        if value is None:
            return default
        if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
            raise WorkspaceError(f"{manifest_path}: '{key}' debe ser una lista de strings")
        return tuple(v.strip() for v in value if v.strip())

    return WorkspaceConfig(
        slices=as_str("slices"),
        specs=as_str("specs"),
        changes=as_str("changes"),
        e2e_tests=as_str("e2e_tests"),
        apps=as_str_tuple("apps", ()),
        test_roots=as_str_tuple("test_roots", ("tests",)),
    )


def load_workspace(start_dir: Path | str | None = None) -> Workspace:
    """Busca openspec.workspace.yaml subiendo desde start_dir."""
    current = Path(start_dir or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        manifest = candidate / MANIFEST
        if manifest.is_file():
            raw = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            return Workspace(root=candidate, config=_parse_config(raw, manifest))
    raise WorkspaceError(f"No se encontró {MANIFEST} subiendo desde {current}")
