"""Parseo de capability specs (consolidadas y deltas): Requirements, checks y verified-by."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

#: `### Requirement: <Título>` (deltas) o `## Requirement: <Título>` (consolidadas)
REQ_RE = re.compile(r"^#{2,3}\s+Requirement:\s+(.+?)\s*$")
YAML_FENCE_RE = re.compile(r"```ya?ml\r?\n(.*?)```", re.DOTALL)
VERIFIED_BY_HEADER_RE = re.compile(r"^\s*verified-by:\s*$")
VERIFIED_BY_INLINE_RE = re.compile(r"^\s*verified-by:\s+(.+?)\s*$")
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.+?)\s*$")


@dataclass(frozen=True)
class SpecRequirement:
    title: str
    checks: tuple[dict, ...] = ()
    verified_by: tuple[str, ...] = ()
    body: str = ""


@dataclass(frozen=True)
class ParsedSpec:
    file_path: str
    requirements: tuple[SpecRequirement, ...] = field(default=())


def _extract_checks(body: str) -> list[dict]:
    checks: list[dict] = []
    for match in YAML_FENCE_RE.finditer(body):
        try:
            document = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            continue  # el YAML inválido se reporta como fail del Requirement en verify
        if isinstance(document, dict) and isinstance(document.get("checks"), list):
            checks.extend(item for item in document["checks"] if isinstance(item, dict))
    return checks


def _extract_verified_by(body: str) -> list[str]:
    out: list[str] = []
    in_list = False
    for line in body.splitlines():
        if VERIFIED_BY_HEADER_RE.match(line):
            in_list = True
            continue
        if in_list:
            item = LIST_ITEM_RE.match(line)
            if item:
                out.append(item.group(1).strip("`"))
                continue
            if not line.strip():
                continue
            in_list = False
        inline = VERIFIED_BY_INLINE_RE.match(line)
        if inline:
            out.append(inline.group(1).strip("`"))
    return out


def parse_spec_file(path: Path | str) -> ParsedSpec:
    file_path = Path(path)
    lines = file_path.read_text(encoding="utf-8").splitlines()
    requirements: list[SpecRequirement] = []
    title: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal title, buffer
        if title is None:
            return
        body = "\n".join(buffer)
        requirements.append(
            SpecRequirement(
                title=title,
                checks=tuple(_extract_checks(body)),
                verified_by=tuple(_extract_verified_by(body)),
                body=body.strip(),
            )
        )
        title = None
        buffer = []

    for line in lines:
        match = REQ_RE.match(line)
        if match:
            flush()
            title = match.group(1)
            continue
        # un heading de nivel <= al del Requirement corta el bloque
        if (
            title is not None
            and re.match(r"^#{1,2}\s", line)
            and not REQ_RE.match(line)
            and not line.startswith("####")
        ):
            flush()
            continue
        if title is not None:
            buffer.append(line)

    flush()
    return ParsedSpec(file_path=str(file_path), requirements=tuple(requirements))
