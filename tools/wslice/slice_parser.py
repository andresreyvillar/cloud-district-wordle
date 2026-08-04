"""Parseo de un archivo de slice: frontmatter + escenarios + wikilinks."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .slice_schema import (
    ParsedSlice,
    SliceScenario,
    SliceSchemaError,
    Wikilink,
    parse_frontmatter,
)

OBSERVABLE_HEADING = "## Comportamiento observable"
#: `### <slug>` o `### <slug> — <título>` (título opcional)
SCENARIO_RE = re.compile(r"^###\s+([a-z0-9]+(?:-[a-z0-9]+)*)(?:\s+—\s+(.+?))?\s*$")
WIKILINK_RE = re.compile(r"\[\[([a-z0-9]+(?:-[a-z0-9]+)*)\]\]")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", re.DOTALL)


class SliceParseError(Exception):
    def __init__(self, file_path: str, message: str) -> None:
        super().__init__(f"{file_path}: {message}")
        self.file_path = file_path


def split_frontmatter(raw: str) -> tuple[object, str]:
    """Separa el frontmatter YAML del cuerpo Markdown (equivalente a gray-matter)."""
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return {}, raw
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def extract_scenarios(body: str) -> list[SliceScenario]:
    """Extrae escenarios SOLO de la sección `## Comportamiento observable`:
    heading exacto, acumula hasta el siguiente `##`."""
    scenarios: list[SliceScenario] = []
    in_section = False
    current: SliceScenario | None = None

    def flush() -> None:
        nonlocal current
        if current is not None:
            current.body = current.body.strip()
            scenarios.append(current)
            current = None

    for line in body.splitlines():
        if line.startswith("## ") and not line.startswith("###"):
            flush()
            in_section = line.strip() == OBSERVABLE_HEADING
            continue
        if not in_section:
            continue
        match = SCENARIO_RE.match(line)
        if match:
            flush()
            title = match.group(2)
            current = SliceScenario(slug=match.group(1), title=title.strip() if title else None)
            continue
        if current is not None:
            current.body += line + "\n"

    flush()
    return scenarios


def extract_wikilinks(body: str) -> list[Wikilink]:
    """Wikilinks `[[slug]]` del body, con flag de si la línea los marca (TBD)."""
    out: list[Wikilink] = []
    seen: set[str] = set()
    for line in body.splitlines():
        tbd = "(tbd)" in line.lower()
        for match in WIKILINK_RE.finditer(line):
            slug = match.group(1)
            if slug in seen:
                continue
            seen.add(slug)
            out.append(Wikilink(slug=slug, tbd=tbd))
    return out


def parse_slice_file(path: Path | str) -> ParsedSlice:
    file_path = Path(path)
    raw = file_path.read_text(encoding="utf-8")
    try:
        data, content = split_frontmatter(raw)
    except yaml.YAMLError as exc:
        raise SliceParseError(str(file_path), f"YAML del frontmatter ilegible — {exc}") from exc
    try:
        frontmatter = parse_frontmatter(data)
    except SliceSchemaError as exc:
        raise SliceParseError(str(file_path), str(exc)) from exc
    return ParsedSlice(
        frontmatter=frontmatter,
        body_markdown=content,
        scenarios=tuple(extract_scenarios(content)),
        wikilinks=tuple(extract_wikilinks(content)),
    )
