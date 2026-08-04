"""Esquema del frontmatter de un slice (§2 de la constitución).

Port del schema.ts de pga-cms: mismas reglas, validadas a mano en lugar de con zod.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

KINDS = ("action", "reaction", "scheduled", "maintenance", "failure")
STATUSES = ("proposed", "shipped", "deprecated", "blocked")
TRIGGER_TYPES = ("ui", "http", "event", "cron", "command")


class SliceSchemaError(Exception):
    """Frontmatter inválido. El mensaje lista todos los problemas encontrados."""


@dataclass(frozen=True)
class SliceTrigger:
    type: str
    surface: str
    detail: str


@dataclass(frozen=True)
class EventRef:
    """Un evento: nombre y, opcionalmente, discriminador de payload."""

    event: str
    discriminator: dict[str, str | int | bool] | None = None

    def signature(self) -> str:
        """'Event{k1=v1,k2=v2}' con claves ordenadas."""
        if not self.discriminator:
            return self.event
        parts = [f"{k}={self.discriminator[k]}" for k in sorted(self.discriminator)]
        return f"{self.event}{{{','.join(parts)}}}"

    def matches_emitter(self, emitter: EventRef) -> bool:
        """Un consumidor matchea a un emisor si el evento coincide y cada (k,v) del
        discriminador del consumidor aparece en el del emisor. Sin discriminador,
        el consumidor escucha todo el evento."""
        if self.event != emitter.event:
            return False
        if not self.discriminator:
            return True
        emitted = emitter.discriminator or {}
        return all(emitted.get(k) == v for k, v in self.discriminator.items())


@dataclass(frozen=True)
class SliceBlocked:
    reason: str
    since: str
    by: str


@dataclass(frozen=True)
class SliceFrontmatter:
    slice: str
    status: str
    kind: str
    trigger: SliceTrigger
    tests_root: str
    actor: str | None = None
    emits: tuple[EventRef, ...] = ()
    consumes: tuple[EventRef, ...] = ()
    specs: tuple[str, ...] = ()
    blocked: SliceBlocked | None = None


@dataclass
class SliceScenario:
    slug: str
    title: str | None
    body: str = ""


@dataclass(frozen=True)
class Wikilink:
    slug: str
    tbd: bool


@dataclass(frozen=True)
class ParsedSlice:
    frontmatter: SliceFrontmatter
    body_markdown: str
    scenarios: tuple[SliceScenario, ...] = ()
    wikilinks: tuple[Wikilink, ...] = ()


def _parse_event_ref(raw: object, where: str, errors: list[str]) -> EventRef | None:
    if isinstance(raw, str) and raw.strip():
        return EventRef(event=raw.strip())
    if isinstance(raw, dict):
        event = raw.get("event")
        if not isinstance(event, str) or not event.strip():
            errors.append(f"{where}: 'event' es obligatorio y debe ser un string no vacío")
            return None
        discriminator = raw.get("discriminator")
        if discriminator is not None and not isinstance(discriminator, dict):
            errors.append(f"{where}: 'discriminator' debe ser un mapa")
            return None
        return EventRef(event=event.strip(), discriminator=discriminator or None)
    errors.append(f"{where}: debe ser un string o un mapa {{event, discriminator}}")
    return None


def parse_frontmatter(data: object) -> SliceFrontmatter:
    """Valida el frontmatter y devuelve el objeto tipado, o lanza SliceSchemaError
    con TODOS los problemas encontrados (no solo el primero)."""
    errors: list[str] = []
    if not isinstance(data, dict):
        raise SliceSchemaError("el frontmatter debe ser un mapa YAML")

    def require_slug(key: str) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not SLUG_RE.match(value):
            errors.append(f"{key}: debe ser kebab-case ([a-z0-9]+(-[a-z0-9]+)*)")
            return ""
        return value

    def require_enum(key: str, allowed: tuple[str, ...]) -> str:
        value = data.get(key)
        if value not in allowed:
            errors.append(f"{key}: debe ser uno de {', '.join(allowed)}")
            return ""
        return str(value)

    def require_text(key: str) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key}: es obligatorio")
            return ""
        return value.strip()

    slug = require_slug("slice")
    status = require_enum("status", STATUSES)
    kind = require_enum("kind", KINDS)
    tests_root = require_text("tests_root")

    raw_trigger = data.get("trigger")
    if not isinstance(raw_trigger, dict):
        errors.append("trigger: es obligatorio (mapa con type, surface y detail)")
        trigger = SliceTrigger(type="", surface="", detail="")
    else:
        t_type = raw_trigger.get("type")
        if t_type not in TRIGGER_TYPES:
            errors.append(f"trigger.type: debe ser uno de {', '.join(TRIGGER_TYPES)}")
            t_type = ""
        surface = raw_trigger.get("surface")
        if not isinstance(surface, str) or not surface.strip():
            errors.append("trigger.surface: es obligatorio (surface que expone el trigger)")
            surface = ""
        detail = raw_trigger.get("detail")
        if not isinstance(detail, str) or not detail.strip():
            errors.append("trigger.detail: es obligatorio (pantalla / comando / schedule)")
            detail = ""
        trigger = SliceTrigger(type=str(t_type), surface=str(surface).strip(), detail=str(detail).strip())

    raw_events = data.get("events") or {}
    if not isinstance(raw_events, dict):
        errors.append("events: debe ser un mapa con 'emits' y 'consumes'")
        raw_events = {}
    emits: list[EventRef] = []
    consumes: list[EventRef] = []
    for key, sink in (("emits", emits), ("consumes", consumes)):
        raw_list = raw_events.get(key) or []
        if not isinstance(raw_list, list):
            errors.append(f"events.{key}: debe ser una lista")
            continue
        for index, item in enumerate(raw_list):
            ref = _parse_event_ref(item, f"events.{key}[{index}]", errors)
            if ref is not None:
                sink.append(ref)

    raw_specs = data.get("specs") or []
    specs: list[str] = []
    if not isinstance(raw_specs, list):
        errors.append("specs: debe ser una lista de capabilities")
    else:
        for index, item in enumerate(raw_specs):
            if not isinstance(item, str) or not SLUG_RE.match(item):
                errors.append(f"specs[{index}]: debe ser kebab-case")
                continue
            specs.append(item)

    raw_blocked = data.get("blocked")
    blocked: SliceBlocked | None = None
    if isinstance(raw_blocked, dict):
        missing = [k for k in ("reason", "since", "by") if not str(raw_blocked.get(k, "")).strip()]
        if missing:
            errors.append(f"blocked: faltan campos {', '.join(missing)}")
        else:
            blocked = SliceBlocked(
                reason=str(raw_blocked["reason"]),
                since=str(raw_blocked["since"]),
                by=str(raw_blocked["by"]),
            )
    elif raw_blocked not in (None, False):
        errors.append("blocked: debe ser null o un mapa {reason, since, by}")

    actor = data.get("actor")
    if actor is not None and (not isinstance(actor, str) or not actor.strip()):
        errors.append("actor: si se declara, debe ser un string no vacío")
        actor = None

    if errors:
        raise SliceSchemaError("frontmatter inválido — " + "; ".join(errors))

    return SliceFrontmatter(
        slice=slug,
        status=status,
        kind=kind,
        actor=actor.strip() if isinstance(actor, str) else None,
        trigger=trigger,
        emits=tuple(emits),
        consumes=tuple(consumes),
        specs=tuple(specs),
        tests_root=tests_root,
        blocked=blocked,
    )
